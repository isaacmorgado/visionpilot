"""
CLI interface for the Autonomous Computer Control system.

Provides command-line access to the Computer Use agent functionality.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .agent import AgentConfig, AgentResult, ComputerUseAgent, create_agent
from .computer import AppleScriptRunner
from .logging_config import get_logger, setup_logging
from .providers import get_available_providers, create_provider
from .providers.base import ProviderNotAvailableError

console = Console()
logger = get_logger(__name__)


def print_banner():
    """Print the application banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║     Autonomous Computer Control System - POC v0.1.0           ║
║     Powered by Claude Computer Use API                        ║
╚═══════════════════════════════════════════════════════════════╝
"""
    console.print(banner, style="bold blue")


def print_result(result: AgentResult):
    """Print the agent result in a formatted way."""
    status_style = "bold green" if result.success else "bold red"
    status_text = "✓ SUCCESS" if result.success else "✗ FAILED"
    
    console.print()
    console.print(Panel(
        f"[{status_style}]{status_text}[/{status_style}]\n\n"
        f"Message: {result.message}\n"
        f"Iterations: {result.iterations}\n"
        f"Actions Taken: {result.actions_taken}"
        + (f"\nError: {result.error}" if result.error else ""),
        title="Result",
        border_style="green" if result.success else "red"
    ))


def on_action_callback(action: str, params: Dict):
    """Callback for action execution."""
    logger.info(f"Executing action: {action}", extra={"params": params})
    console.print(f"  [yellow]→[/yellow] {action}", end="")
    if "coordinate" in params and params["coordinate"]:
        console.print(f" at {params['coordinate']}", end="")
    if "text" in params and params["text"]:
        text = params["text"][:30] + "..." if len(params.get("text", "")) > 30 else params.get("text", "")
        console.print(f" '{text}'", end="")
    console.print()


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--log-file", type=click.Path(), help="Log file path")
@click.pass_context
def cli(ctx, verbose: bool, log_file: Optional[str]):
    """Autonomous Computer Control System CLI."""
    ctx.ensure_object(dict)
    
    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(level=log_level, log_file=log_file)
    
    ctx.obj["verbose"] = verbose


@cli.command()
@click.argument("task")
@click.option("--model", help="Model to use (if not set, uses provider default)")
@click.option("--provider", help="LLM provider (auto|gemini|anthropic|openai|featherless)")
@click.option("--max-iterations", default=50, help="Maximum iterations")
@click.option("--no-screenshot", is_flag=True, help="Skip initial screenshot")
@click.pass_context
def run(ctx, task: str, model: Optional[str], provider: Optional[str], max_iterations: int, no_screenshot: bool):
    """
    Run a task using the Computer Use agent.
    
    TASK is the description of what you want the agent to do.
    
    Examples:
    
        acc run "Open Safari and navigate to google.com"
        
        acc run "Click the File menu and select New"
        
        acc run "Take a screenshot" --provider gemini
        
        acc run "Open calculator" --provider anthropic --model claude-sonnet-4
    """
    print_banner()
    
    console.print(f"[bold]Task:[/bold] {task}")
    if model:
        console.print(f"[bold]Model:[/bold] {model}")
    if provider:
        console.print(f"[bold]Provider:[/bold] {provider}")
    console.print(f"[bold]Max Iterations:[/bold] {max_iterations}")
    console.print()
    
    logger.info("Starting task", extra={"task": task, "model": model, "provider": provider})
    
    # Create agent (will auto-select provider if not specified)
    try:
        agent = create_agent(
            model=model,
            provider=provider,
            max_iterations=max_iterations
        )
        agent.on_action = on_action_callback
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("\n[yellow]Tip:[/yellow] Run 'acc info' to check provider status")
        console.print("[yellow]Tip:[/yellow] Set GOOGLE_API_KEY for FREE tier (https://aistudio.google.com/apikey)")
        sys.exit(1)
    
    # Run task
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task_id = progress.add_task("Running agent...", total=None)
        
        result = agent.run(task, initial_screenshot=not no_screenshot)
        
        progress.update(task_id, completed=True)
    
    print_result(result)
    
    # Save final screenshot if available
    if result.final_screenshot:
        screenshot_dir = Path("screenshots")
        screenshot_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = screenshot_dir / f"final_{timestamp}.png"
        result.final_screenshot.save(screenshot_path)
        console.print(f"\n[dim]Final screenshot saved to: {screenshot_path}[/dim]")
    
    logger.info("Task completed", extra={
        "success": result.success,
        "iterations": result.iterations,
        "actions": result.actions_taken
    })
    
    sys.exit(0 if result.success else 1)


@cli.command()
@click.argument("app_name")
def launch(app_name: str):
    """
    Launch an application by name.
    
    APP_NAME is the name of the application to launch.
    
    Examples:
    
        acc launch "Safari"
        
        acc launch "Adobe Premiere Pro"
    """
    print_banner()
    
    console.print(f"[bold]Launching:[/bold] {app_name}")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"Launching {app_name}...", total=None)
        
        success, result = AppleScriptRunner.launch_app(app_name, wait=True)
        
        progress.update(task, completed=True)
    
    if success:
        console.print(f"[green]✓[/green] {app_name} launched successfully")
        console.print(f"[dim]Frontmost app: {result}[/dim]")
    else:
        console.print(f"[red]✗[/red] Failed to launch {app_name}")
        console.print(f"[red]Error: {result}[/red]")
        sys.exit(1)


@cli.command()
def screenshot():
    """
    Take a screenshot and save it.
    
    The screenshot will be saved to the screenshots directory.
    """
    from .screen import ScreenCapture
    
    print_banner()
    
    screen = ScreenCapture()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Capturing screenshot...", total=None)
        
        image = screen.capture(save=True)
        
        progress.update(task, completed=True)
    
    console.print(f"[green]✓[/green] Screenshot captured")
    console.print(f"[dim]Size: {image.size[0]}x{image.size[1]}[/dim]")
    console.print(f"[dim]Saved to: screenshots/[/dim]")


@cli.command()
def info():
    """
    Display system information and configuration.
    """
    import pyautogui
    
    print_banner()
    
    # Create info table
    table = Table(title="System Information")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    # Screen info
    screen_size = pyautogui.size()
    table.add_row("Screen Size", f"{screen_size[0]} x {screen_size[1]}")
    
    # Mouse position
    mouse_pos = pyautogui.position()
    table.add_row("Mouse Position", f"({mouse_pos[0]}, {mouse_pos[1]})")
    
    # Frontmost app
    success, app = AppleScriptRunner.get_frontmost_app()
    table.add_row("Frontmost App", app if success else "Unknown")
    
    # Python version
    table.add_row("Python Version", sys.version.split()[0])
    
    console.print(table)
    
    # LLM Provider status
    console.print("\n[bold]LLM Provider Status:[/bold]")
    
    provider_table = Table(title="Available Providers")
    provider_table.add_column("Provider", style="cyan")
    provider_table.add_column("Model", style="yellow")
    provider_table.add_column("API Key", style="green")
    provider_table.add_column("Vision", style="blue")
    provider_table.add_column("Computer Use", style="blue")
    provider_table.add_column("Cost", style="magenta")
    provider_table.add_column("Free Tier", style="green")
    
    # Get available providers
    available_providers = get_available_providers()
    
    # Define all providers with their env var names
    all_providers_info = [
        {
            "name": "Google Gemini",
            "env_var": "GOOGLE_API_KEY",
            "model_env": "GEMINI_MODEL",
            "default_model": "gemini-2.0-flash-exp",
            "vision": "✓",
            "computer_use": "Via Functions",
            "cost": "FREE/$ ",
            "free_tier": "✓"
        },
        {
            "name": "Anthropic Claude",
            "env_var": "ANTHROPIC_API_KEY",
            "model_env": "ANTHROPIC_MODEL",
            "default_model": "claude-sonnet-4-20250514",
            "vision": "✓",
            "computer_use": "Native API",
            "cost": "$$$",
            "free_tier": "✗"
        },
        {
            "name": "OpenAI GPT",
            "env_var": "OPENAI_API_KEY",
            "model_env": "OPENAI_MODEL",
            "default_model": "gpt-4o-mini",
            "vision": "✓",
            "computer_use": "Via Functions",
            "cost": "$$",
            "free_tier": "✗"
        },
        {
            "name": "Featherless.ai",
            "env_var": "FEATHERLESS_API_KEY",
            "model_env": "FEATHERLESS_MODEL",
            "default_model": "llama-3.1-70b",
            "vision": "Limited",
            "computer_use": "Via Functions",
            "cost": "$",
            "free_tier": "✗"
        }
    ]
    
    # Add rows for each provider
    for provider_info in all_providers_info:
        api_key = os.environ.get(provider_info["env_var"])
        key_status = "[green]✓ Set[/green]" if api_key else "[red]✗ Not Set[/red]"
        
        # Get model from env or use default
        model = os.environ.get(provider_info["model_env"], provider_info["default_model"])
        
        provider_table.add_row(
            provider_info["name"],
            model,
            key_status,
            provider_info["vision"],
            provider_info["computer_use"],
            provider_info["cost"],
            provider_info["free_tier"]
        )
    
    console.print(provider_table)
    
    # Show selected provider
    selected_provider = os.environ.get("LLM_PROVIDER", "auto")
    console.print(f"\n[bold]Selected Provider:[/bold] {selected_provider}")
    
    if available_providers:
        console.print(f"[green]✓ {len(available_providers)} provider(s) available[/green]")
        console.print("\n[bold]Recommendation:[/bold]")
        console.print("  • For FREE operation: Set GOOGLE_API_KEY (no credit card required)")
        console.print("  • For best computer use: Set ANTHROPIC_API_KEY (paid)")
    else:
        console.print("[red]✗ No providers available! Set at least one API key.[/red]")
        console.print("\n[bold]Quick Start (FREE):[/bold]")
        console.print("  1. Get FREE Gemini API key: https://aistudio.google.com/apikey")
        console.print("  2. Set in .env: GOOGLE_API_KEY=your_key_here")
        console.print("  3. Run: acc run 'your task'")
    
    # Permission check
    console.print("\n[bold]Permission Check:[/bold]")
    console.print("  Run 'acc test-permissions' to verify accessibility permissions")


@cli.command("test-permissions")
def test_permissions():
    """
    Test if the required macOS permissions are granted.
    
    This checks:
    - Accessibility permissions (for mouse/keyboard control)
    - Screen recording permissions (for screenshots)
    """
    import pyautogui
    
    print_banner()
    
    console.print("[bold]Testing Permissions...[/bold]\n")
    
    # Test screenshot permission
    console.print("1. Testing screen capture permission...")
    try:
        from .screen import ScreenCapture
        screen = ScreenCapture()
        image = screen.capture(save=False)
        if image:
            console.print("   [green]✓[/green] Screen capture: OK")
        else:
            console.print("   [red]✗[/red] Screen capture: FAILED")
    except Exception as e:
        console.print(f"   [red]✗[/red] Screen capture: FAILED ({e})")
    
    # Test mouse control permission
    console.print("2. Testing mouse control permission...")
    try:
        pos = pyautogui.position()
        # Move mouse slightly and back
        pyautogui.moveRel(1, 0, duration=0.05)
        pyautogui.moveRel(-1, 0, duration=0.05)
        console.print("   [green]✓[/green] Mouse control: OK")
    except Exception as e:
        console.print(f"   [red]✗[/red] Mouse control: FAILED ({e})")
    
    # Test keyboard control permission
    console.print("3. Testing keyboard control permission...")
    try:
        # Just verify we can call the function
        pyautogui.press("shift")  # Safe key to press
        console.print("   [green]✓[/green] Keyboard control: OK")
    except Exception as e:
        console.print(f"   [red]✗[/red] Keyboard control: FAILED ({e})")
    
    # Test AppleScript permission
    console.print("4. Testing AppleScript permission...")
    try:
        success, result = AppleScriptRunner.get_frontmost_app()
        if success:
            console.print("   [green]✓[/green] AppleScript: OK")
        else:
            console.print(f"   [yellow]![/yellow] AppleScript: Limited ({result})")
    except Exception as e:
        console.print(f"   [red]✗[/red] AppleScript: FAILED ({e})")
    
    console.print("\n[bold]Permission Setup Instructions:[/bold]")
    console.print("""
If any tests failed, you need to grant permissions:

1. Open System Preferences → Security & Privacy → Privacy
2. Click the lock icon to make changes
3. Enable the following for your terminal app:
   - Accessibility (required for mouse/keyboard)
   - Screen Recording (required for screenshots)
4. Restart your terminal after granting permissions
""")


@cli.command()
@click.argument("task")
@click.option("--dry-run", is_flag=True, help="Show what would be done without executing")
@click.option("--provider", help="LLM provider to use")
def premiere(task: str, dry_run: bool, provider: Optional[str]):
    """
    Run a Premiere Pro specific task.
    
    TASK is the task to perform in Premiere Pro.
    
    This command will:
    1. Launch Premiere Pro if not running
    2. Execute the specified task
    3. Report results
    
    Examples:
    
        acc premiere "Open the Extensions panel"
        
        acc premiere "Navigate to Window menu"
    """
    print_banner()
    
    console.print("[bold]Premiere Pro Task Runner[/bold]\n")
    console.print(f"[bold]Task:[/bold] {task}")
    
    if dry_run:
        console.print("\n[yellow]DRY RUN - No actions will be executed[/yellow]")
        console.print("\nSteps that would be taken:")
        console.print("  1. Check if Premiere Pro is running")
        console.print("  2. Launch Premiere Pro if needed")
        console.print("  3. Wait for application to be ready")
        console.print("  4. Take initial screenshot")
        console.print("  5. Execute task via LLM provider")
        console.print("  6. Report results")
        return
    
    # First, ensure Premiere Pro is running
    console.print("\n[dim]Step 1: Checking Premiere Pro...[/dim]")
    success, frontmost = AppleScriptRunner.get_frontmost_app()
    
    if "Premiere" not in frontmost:
        console.print("  Launching Adobe Premiere Pro...")
        success, result = AppleScriptRunner.launch_app("Adobe Premiere Pro", wait=True)
        if not success:
            console.print(f"[red]Failed to launch Premiere Pro: {result}[/red]")
            sys.exit(1)
        console.print("  [green]✓[/green] Premiere Pro launched")
    else:
        console.print("  [green]✓[/green] Premiere Pro already running")
    
    # Create the full task with context
    full_task = f"""You are controlling Adobe Premiere Pro on macOS.

Task: {task}

Instructions:
1. First, take a screenshot to see the current state
2. Identify the relevant UI elements
3. Execute the necessary actions step by step
4. Verify the result with a final screenshot
5. Report what was accomplished

Important:
- Premiere Pro uses standard macOS menus
- Wait after clicking for UI to respond
- Use keyboard shortcuts when appropriate (e.g., Cmd+Shift+X for Extensions)
"""
    
    console.print("\n[dim]Step 2: Executing task...[/dim]")
    
    try:
        agent = create_agent(provider=provider)
        agent.on_action = on_action_callback
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("\n[yellow]Tip:[/yellow] Run 'acc info' to check provider status")
        sys.exit(1)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task_id = progress.add_task("Running agent...", total=None)
        result = agent.run(full_task)
        progress.update(task_id, completed=True)
    
    print_result(result)
    
    sys.exit(0 if result.success else 1)


def main():
    """Entry point for the CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
