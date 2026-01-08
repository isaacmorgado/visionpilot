# VisionPilot

An AI-powered vision-based autonomous computer control system. VisionPilot uses vision-language models to see your screen and control your computer to perform complex multi-step tasks autonomously.

## Overview

This project demonstrates how to build an autonomous computer control system that can:

- **Control mouse**: Movements, clicks, scrolling, dragging
- **Execute keyboard input**: Typing, key combinations, shortcuts
- **Analyze screen**: Visual recognition via Claude's vision capabilities
- **Orchestrate workflows**: Multi-step autonomous task execution
- **Integrate with macOS**: AppleScript for native app control

### Primary Use Case: Premiere Pro Plugin Testing

The system is designed to autonomously:
1. Load Adobe Premiere Pro
2. Navigate to the extensions panel
3. Install/activate plugins
4. Run test scenarios
5. Capture results and report findings

## Requirements

- **macOS** (tested on macOS 14+)
- **Python 3.10+**
- **LLM Provider API Key** (see [LLM Provider Configuration](#llm-provider-configuration) below)
- **macOS Permissions**: Accessibility and Screen Recording

## LLM Provider Configuration

This system supports multiple LLM providers with vision and computer control capabilities. Choose based on your budget and requirements.

### Provider Comparison

| Provider | Cost | Free Tier | Vision Support | Computer Use API | Best For |
|----------|------|-----------|----------------|------------------|----------|
| **Google Gemini** | FREE / $ | ✅ Generous | ✅ Yes | Via function calling | **Cost-effective operation** |
| **Anthropic Claude** | $$$ | ❌ No | ✅ Yes | ✅ Native API | **Best accuracy for computer control** |
| **OpenAI GPT-4o** | $$ | ❌ No | ✅ Yes | Via function calling | **ChatGPT subscription users** |
| **Featherless.ai** | $ | Varies | ⚠️ Limited | Via function calling | **Open-source models** |

### Cost Analysis

**Recommended for cost-effectiveness:**

1. **🥇 Google Gemini 2.0 Flash (FREE Tier)**
   - **Cost**: Free tier with generous limits
   - **Model**: `gemini-2.0-flash-exp` or `gemini-1.5-flash`
   - **Vision**: Full support
   - **Why**: Best bang-for-buck, no credit card required
   - **Limits**: 15 RPM (requests per minute), 1M TPM (tokens per minute), 1500 RPD (requests per day)

2. **🥈 Google Gemini Flash (Paid Tier)**
   - **Cost**: ~$0.075 per 1M input tokens, ~$0.30 per 1M output tokens
   - **Model**: `gemini-2.0-flash-exp`
   - **Why**: Very cheap, higher rate limits
   - **When to use**: When free tier limits are exceeded

3. **🥉 OpenAI GPT-4o-mini**
   - **Cost**: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
   - **Model**: `gpt-4o-mini`
   - **Why**: Good balance of cost and quality
   - **When to use**: If you have ChatGPT API access

4. **Anthropic Claude 3.5 Sonnet**
   - **Cost**: ~$3 per 1M input tokens, ~$15 per 1M output tokens
   - **Model**: `claude-sonnet-4-20250514`
   - **Why**: Best accuracy for computer control (native Computer Use API)
   - **When to use**: When accuracy matters more than cost, or you have existing subscription

### Quick Start: Free Tier (Gemini)

The fastest way to get started without spending money:

#### 1. Get Google API Key (Free)

1. Visit [Google AI Studio](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

**No credit card required!** Free tier includes:
- 15 requests per minute
- 1 million tokens per minute
- 1500 requests per day

#### 2. Configure Environment

```bash
# Edit .env file
cd visionpilot
nano .env

# Add your Google API key
GOOGLE_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp

# Set provider to auto (will prefer free Gemini)
LLM_PROVIDER=auto
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Test It

```bash
# Check provider status
python -m src.cli info

# Should show Gemini as available and selected
# Run a simple task
python -m src.cli run "Take a screenshot"
```

### Provider Setup Instructions

#### Google Gemini Setup

**Free Tier (Recommended):**
```bash
# Get API key from https://aistudio.google.com/apikey
GOOGLE_API_KEY=your_gemini_api_key

# Use free tier model
GEMINI_MODEL=gemini-2.0-flash-exp

# Or alternative free model
GEMINI_MODEL=gemini-1.5-flash
```

**Paid Tier:**
```bash
# Same API key works for paid tier
# Billing automatically activated when free tier exceeded
# Set up billing at https://console.cloud.google.com/billing
```

**Models Available:**
- `gemini-2.0-flash-exp` - Experimental, fastest, free tier (recommended)
- `gemini-1.5-flash` - Stable, fast, free tier
- `gemini-2.0-flash` - Production, paid tier
- `gemini-1.5-pro` - Advanced reasoning, paid tier

#### Anthropic Claude Setup

**API Key:**
```bash
# Get API key from https://console.anthropic.com/
ANTHROPIC_API_KEY=your_anthropic_api_key

# Optionally specify model
ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

**Models Available:**
- `claude-sonnet-4-20250514` - Latest with Computer Use API (recommended)
- `claude-3-5-sonnet-20241022` - Previous generation
- `claude-3-opus-20240229` - Highest capability

**Note**: Claude has native Computer Use API support, making it the most accurate for this use case, but also the most expensive.

#### OpenAI Setup

**API Key:**
```bash
# Get API key from https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key

# Specify model
OPENAI_MODEL=gpt-4o-mini  # Cheaper
# or
OPENAI_MODEL=gpt-4o      # More capable
```

**Models Available:**
- `gpt-4o-mini` - Cost-effective, good for most tasks
- `gpt-4o` - Latest, most capable
- `gpt-4-turbo` - Previous generation

**ChatGPT Plus Users**: Your subscription doesn't include API access. You need a separate API key from [OpenAI Platform](https://platform.openai.com/).

#### Featherless.ai Setup

**API Key:**
```bash
# Get API key from https://featherless.ai/
FEATHERLESS_API_KEY=your_featherless_api_key

# Specify model
FEATHERLESS_MODEL=meta-llama/llama-3.1-70b-instruct
```

**Models Available:**
- `meta-llama/llama-3.1-70b-instruct` - Good reasoning
- `mistralai/mixtral-8x7b-instruct` - Fast inference
- Check [Featherless models](https://featherless.ai/models) for vision-capable options

**Note**: Vision support varies by model. Check model capabilities before use.

### Provider Selection

The system auto-selects providers in this order of priority:

1. **Auto Mode** (default): Gemini (free) → Claude → OpenAI → Featherless
2. **Manual Override**: Use `LLM_PROVIDER` environment variable or `--provider` CLI flag

```bash
# Auto-select (prefers free tier)
LLM_PROVIDER=auto

# Force specific provider
LLM_PROVIDER=gemini
LLM_PROVIDER=anthropic
LLM_PROVIDER=openai
LLM_PROVIDER=featherless
```

**CLI Override:**
```bash
# Use specific provider for a task
python -m src.cli run "task" --provider gemini
python -m src.cli run "task" --provider anthropic

# Use specific model
python -m src.cli run "task" --provider openai --model gpt-4o
```

### Checking Provider Status

```bash
python -m src.cli info
```

**Example Output:**
```
Provider Configuration:
┌────────────┬──────────────────────┬─────────┬────────┬──────────────┬──────┬───────────┐
│ Provider   │ Model                │ API Key │ Vision │ Computer Use │ Cost │ Free Tier │
├────────────┼──────────────────────┼─────────┼────────┼──────────────┼──────┼───────────┤
│ gemini     │ gemini-2.0-flash-exp │ ✓       │ ✓      │ ✓            │ FREE │ ✓         │
│ anthropic  │ claude-sonnet-4      │ ✓       │ ✓      │ ✓✓✓          │ $$$  │ ✗         │
│ openai     │ gpt-4o-mini          │ ✗       │ ✓      │ ✓            │ $$   │ ✗         │
│ featherless│ llama-3.1-70b        │ ✗       │ ~      │ ✓            │ $    │ ~         │
└────────────┴──────────────────────┴─────────┴────────┴──────────────┴──────┴───────────┘

Selected Provider: gemini (gemini-2.0-flash-exp)
Recommendation: ✓ Using free tier - excellent choice for cost-effective operation!
```

### Cost Optimization Tips

1. **Start with Gemini Free Tier**: No cost, generous limits
2. **Cache Screenshots**: Provider abstraction reuses screenshots when possible
3. **Reduce Iterations**: Set `--max-iterations` lower for simple tasks
4. **Use Cheaper Models**: `gpt-4o-mini` instead of `gpt-4o`, `gemini-1.5-flash` instead of `gemini-1.5-pro`
5. **Monitor Usage**: Check provider dashboards for usage:
   - Google: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/metrics
   - Anthropic: https://console.anthropic.com/settings/usage
   - OpenAI: https://platform.openai.com/usage

### Multi-Provider Architecture

The system uses a provider abstraction layer:

```python
from src.providers import ProviderFactory, ProviderType

# Auto-select based on available API keys
provider = ProviderFactory.create_provider()

# Or manually specify
provider = ProviderFactory.create_provider(ProviderType.GEMINI)

# Use in agent
from src.agent import ComputerUseAgent, AgentConfig

config = AgentConfig(provider=provider)
agent = ComputerUseAgent(config=config)
```

**Provider Files:**
- `src/providers/base.py` - Abstract base class
- `src/providers/gemini_provider.py` - Google Gemini
- `src/providers/anthropic_provider.py` - Anthropic Claude
- `src/providers/openai_provider.py` - OpenAI GPT
- `src/providers/featherless_provider.py` - Featherless.ai
- `src/providers/factory.py` - Provider selection logic

## Installation

### 1. Clone and Setup

```bash
# Navigate to the project directory
cd visionpilot

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

**Option A: Use Free Tier (Recommended for getting started)**

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your Google API key (free from https://aistudio.google.com/apikey)
nano .env
# Set: GOOGLE_API_KEY=your-google-api-key
# Set: GEMINI_MODEL=gemini-2.0-flash-exp
# Set: LLM_PROVIDER=auto
```

**Option B: Use Anthropic Claude (Best for computer control accuracy)**

```bash
# Edit .env with your Anthropic API key
nano .env
# Set: ANTHROPIC_API_KEY=your-api-key-here
# Set: LLM_PROVIDER=anthropic
```

**Option C: Use OpenAI (If you have ChatGPT API access)**

```bash
# Edit .env with your OpenAI API key
nano .env
# Set: OPENAI_API_KEY=your-api-key-here
# Set: OPENAI_MODEL=gpt-4o-mini
# Set: LLM_PROVIDER=openai
```

Or set directly via environment variables:

```bash
# For Gemini (free tier) - Recommended
export GOOGLE_API_KEY="your-google-api-key"
export GEMINI_MODEL="gemini-2.0-flash-exp"
export LLM_PROVIDER="auto"

# For Anthropic
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export LLM_PROVIDER="anthropic"

# For OpenAI
export OPENAI_API_KEY="your-openai-api-key"
export OPENAI_MODEL="gpt-4o-mini"
export LLM_PROVIDER="openai"
```

**See [LLM Provider Configuration](#llm-provider-configuration) section above for detailed setup instructions.**

### 3. Grant macOS Permissions

This system requires special macOS permissions to control your computer:

#### Accessibility Permission (Required for mouse/keyboard)

1. Open **System Preferences** → **Security & Privacy** → **Privacy**
2. Select **Accessibility** in the left sidebar
3. Click the lock icon and enter your password
4. Add your terminal application (Terminal, iTerm, VS Code, etc.)
5. Enable the checkbox next to your terminal app

#### Screen Recording Permission (Required for screenshots)

1. Open **System Preferences** → **Security & Privacy** → **Privacy**
2. Select **Screen Recording** in the left sidebar
3. Click the lock icon and enter your password
4. Add your terminal application
5. Enable the checkbox next to your terminal app

**Important**: Restart your terminal after granting permissions!

### 4. Verify Setup

```bash
# Check permissions are working
python -m src.cli test-permissions

# View system info
python -m src.cli info
```

## Usage

There are two ways to use this system:

1. **Standalone CLI** - Direct command-line interface for task execution
2. **MCP Integration** - Native tool integration with Roo Code, Claude Code, and other MCP clients

---

### Mode 1: Standalone CLI

The CLI provides direct task execution with Claude's Computer Use API as the orchestrator.

#### CLI Commands

```bash
# General task execution
python -m src.cli run "Open Safari and navigate to google.com"

# Launch an application
python -m src.cli launch "Safari"

# Take a screenshot
python -m src.cli screenshot

# System information
python -m src.cli info

# Test permissions
python -m src.cli test-permissions

# Premiere Pro specific task
python -m src.cli premiere "Open the Extensions panel"

# Dry run (show what would happen)
python -m src.cli premiere "Navigate to File menu" --dry-run
```

#### CLI Options

```bash
# Enable verbose logging
python -m src.cli -v run "task"

# Save logs to file
python -m src.cli --log-file logs/session.log run "task"

# Use different model
python -m src.cli run "task" --model claude-sonnet-4-20250514

# Set max iterations
python -m src.cli run "task" --max-iterations 30
```

---

### Mode 2: MCP Integration

MCP (Model Context Protocol) integration provides **superior autonomous control** compared to CLI-only approaches:

| Approach | How it works | Autonomy |
|----------|--------------|----------|
| **CLI** | Claude constructs command strings like `python -m src.cli run "task"` | Opaque, one-shot |
| **MCP** | Claude gets native tools (mouse_move, click, screenshot) and composes them | Full visual feedback loop |

MCP follows Anthropic's Computer Use API design philosophy - meant for tool calling, not CLI wrapping.

#### Available MCP Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `screenshot` | Capture screen as base64 PNG | None |
| `mouse_move` | Move cursor to coordinates | `x`, `y` |
| `left_click` | Left click at position | `x`, `y` (optional) |
| `right_click` | Right click at position | `x`, `y` (optional) |
| `double_click` | Double-click at position | `x`, `y` (optional) |
| `middle_click` | Middle-click at position | `x`, `y` (optional) |
| `left_click_drag` | Click and drag | `start_x`, `start_y`, `end_x`, `end_y` |
| `scroll` | Scroll wheel | `amount`, `x`, `y` (optional) |
| `type` | Type text | `text` |
| `key` | Press key combination | `key` (e.g., "ctrl+c") |
| `cursor_position` | Get current cursor position | None |
| `get_screen_size` | Get screen dimensions | None |

#### Configure Roo Code

Add to your Roo Code MCP settings (`~/.config/roo-code/mcp.json` or workspace `.roo/mcp.json`):

```json
{
  "mcpServers": {
    "computer-control": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "/path/to/autonomous-computer-control",
      "env": {
        "PYTHONPATH": "/path/to/autonomous-computer-control"
      }
    }
  }
}
```

Replace `/path/to/autonomous-computer-control` with the actual path to this project.

#### Configure Claude Code

Add to your Claude Code MCP settings (`~/.claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "computer-control": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "/path/to/autonomous-computer-control",
      "env": {
        "PYTHONPATH": "/path/to/autonomous-computer-control"
      }
    }
  }
}
```

#### Using MCP Tools

After configuration and restarting your IDE, the tools appear as native capabilities:

```
User: Take a screenshot of my desktop

Claude: [Calls screenshot tool]
        Screenshot captured (2560x1440 pixels)
        [Shows base64 image]
        
        I can see your desktop with Finder, Safari, and VS Code open...
```

```
User: Click on the Safari icon in the dock

Claude: [Calls screenshot tool to see current state]
        [Calls left_click tool with x=640, y=1400]
        Left click at (640, 1400)
        
        [Calls screenshot tool to verify]
        Safari is now active and showing the homepage...
```

#### MCP Server Testing

Test that the server runs correctly:

```bash
cd autonomous-computer-control

# Install dependencies (if not already done)
pip install -r requirements.txt

# Run the MCP server directly (should wait for stdin)
python -m src.mcp_server

# The server communicates via stdio - it's designed to be launched by MCP clients
# Press Ctrl+C to exit
```

#### Why MCP Over CLI?

1. **Visual Feedback Loop**: Claude can take screenshots between actions to verify success
2. **Composable Actions**: Claude builds multi-step workflows dynamically
3. **Error Recovery**: Claude can see and react to unexpected states
4. **Natural Interaction**: No need to construct command-line strings
5. **Better Context**: Screenshot images provide rich visual context for decision-making

### Python API

```python
from autonomous_computer_control import ComputerUseAgent, AgentConfig

# Create agent with custom config
config = AgentConfig(
    model="claude-sonnet-4-20250514",
    max_iterations=50,
    action_delay=0.5
)
agent = ComputerUseAgent(config=config)

# Run a task
result = agent.run("Open Safari and search for Python tutorials")

if result.success:
    print(f"Task completed: {result.message}")
else:
    print(f"Task failed: {result.error}")
```

### AppleScript Integration

```python
from autonomous_computer_control import AppleScriptRunner

# Launch an application
success, message = AppleScriptRunner.launch_app("Adobe Premiere Pro")

# Get frontmost app
success, app_name = AppleScriptRunner.get_frontmost_app()

# Click menu item
success, message = AppleScriptRunner.click_menu_item(
    "Adobe Premiere Pro",
    "Window",
    "Extensions"
)
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User / CLI                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Agent Loop (agent.py)                      │
│  ┌─────────────┐    ┌────────────────┐    ┌──────────────────┐ │
│  │  Send       │ -> │ Claude API     │ -> │ Parse Tool       │ │
│  │  Screenshot │    │ Computer Use   │    │ Requests         │ │
│  └─────────────┘    └────────────────┘    └──────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Control Layer (computer.py)                   │
│  ┌─────────────┐    ┌────────────────┐    ┌──────────────────┐ │
│  │  Mouse      │    │  Keyboard      │    │  AppleScript     │ │
│  │  Control    │    │  Control       │    │  Runner          │ │
│  │  (PyAutoGUI)│    │  (PyAutoGUI)   │    │  (osascript)     │ │
│  └─────────────┘    └────────────────┘    └──────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Vision Layer (screen.py)                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Screen Capture → Base64 Encode → Claude Vision API     │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
autonomous-computer-control/
├── src/
│   ├── __init__.py        # Package exports
│   ├── agent.py           # Claude Computer Use agent loop
│   ├── computer.py        # Mouse/keyboard control
│   ├── screen.py          # Screenshot capture
│   ├── cli.py             # Command-line interface
│   ├── mcp_server.py      # MCP server for tool integration
│   └── logging_config.py  # Logging setup
├── screenshots/           # Captured screenshots
├── logs/                  # Log files
├── mcp-config.json       # MCP configuration template
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

## Supported Actions

| Action | Description | Parameters |
|--------|-------------|------------|
| `screenshot` | Capture screen | None |
| `mouse_move` | Move cursor | `coordinate: [x, y]` |
| `left_click` | Left click | `coordinate: [x, y]` (optional) |
| `right_click` | Right click | `coordinate: [x, y]` (optional) |
| `double_click` | Double click | `coordinate: [x, y]` (optional) |
| `left_click_drag` | Drag | `coordinate: [x, y]`, `text: "end_x,end_y"` |
| `scroll` | Scroll | `coordinate: [x, y]`, `text: "amount"` |
| `key` | Press key(s) | `text: "key"` or `"mod+key"` |
| `type` | Type text | `text: "string to type"` |
| `cursor_position` | Get position | None |

### Key Combinations

```python
# Single keys
"Return", "Tab", "Escape", "BackSpace", "Delete"
"Up", "Down", "Left", "Right"
"F1" through "F12"

# Combinations
"ctrl+c", "ctrl+v", "ctrl+z"
"command+s", "command+shift+s"
"alt+tab"
```

## Configuration

### AgentConfig Options

| Option | Default | Description |
|--------|---------|-------------|
| `model` | `claude-sonnet-4-20250514` | Claude model to use |
| `max_tokens` | `4096` | Max response tokens |
| `max_iterations` | `50` | Max agent loop iterations |
| `max_actions_per_session` | `100` | Safety limit on actions |
| `action_delay` | `0.5` | Delay between actions (seconds) |
| `screenshot_on_tool_result` | `True` | Include screenshot with tool results |
| `system_prompt` | (default) | Custom system prompt |

## Troubleshooting

### Permissions Issues

**"Operation not permitted" errors:**
- Ensure Accessibility permission is granted
- Ensure Screen Recording permission is granted
- Restart your terminal after granting permissions

**Test with:**
```bash
python -m src.cli test-permissions
```

### API Errors

**"API key not found":**
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

**Rate limiting:**
- Increase `action_delay` in config
- Reduce `max_iterations`

### Screenshot Issues

**Black or empty screenshots:**
- Grant Screen Recording permission
- Some windows may be protected (DRM content)

### Mouse/Keyboard Not Working

**No response from inputs:**
- Grant Accessibility permission
- Check PyAutoGUI failsafe (move mouse to corner)
- Some secure input fields block automation

## Safety Features

1. **Action Limits**: Maximum actions per session prevents runaway automation
2. **Iteration Limits**: Maximum iterations stops infinite loops
3. **PyAutoGUI Failsafe**: Move mouse to screen corner to abort
4. **Action Delays**: Configurable delays prevent overwhelming the system
5. **Dry Run Mode**: Test workflows without executing actions

## Development

### Running Tests

```bash
# Run test modules
python -m src.screen
python -m src.computer
python -m src.agent "Take a screenshot"
```

### Adding New Actions

1. Add action to `Action` enum in `computer.py`
2. Implement handler method
3. Add case to `execute()` method
4. Update documentation

## API Costs & Monitoring

### Cost Overview by Provider

**Free Options:**
- **Google Gemini Free Tier**: FREE up to 1500 requests/day
  - 15 RPM, 1M TPM limits
  - Perfect for development and testing
  - No credit card required

**Paid Options (approximate costs per 1M tokens):**

| Provider | Input Cost | Output Cost | Image Cost | Total/Task Est. |
|----------|-----------|-------------|------------|-----------------|
| **Gemini Flash (Paid)** | $0.075 | $0.30 | Included | $0.01-0.05 |
| **GPT-4o-mini** | $0.15 | $0.60 | Included | $0.02-0.10 |
| **GPT-4o** | $2.50 | $10.00 | Included | $0.25-1.00 |
| **Claude Sonnet 4** | $3.00 | $15.00 | Included | $0.30-1.50 |

**Typical Task Costs:**
- Simple task (5-10 iterations): $0.01-0.10 (or FREE with Gemini)
- Complex task (20-30 iterations): $0.10-0.50 (or FREE with Gemini)
- Extended session (50+ iterations): $0.50-2.00 (or FREE with Gemini until limits)

### Cost Optimization

1. **Use Gemini Free Tier**: Start here - it's free!
2. **Limit Iterations**: Set `--max-iterations` based on task complexity
3. **Reduce Screenshot Frequency**: Set `screenshot_on_tool_result=False` if not needed
4. **Cache Results**: Provider abstraction reuses screenshots when possible
5. **Choose Cheaper Models**: Use `-mini` or `flash` variants when accuracy isn't critical

### Monitor Usage

**Google Gemini:**
- Dashboard: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/metrics
- Free tier quota visible in Google AI Studio

**Anthropic Claude:**
- Dashboard: https://console.anthropic.com/settings/usage
- Set budget alerts in console

**OpenAI GPT:**
- Dashboard: https://platform.openai.com/usage
- Set monthly budget limits

**CLI Monitoring:**
```bash
# Check current provider and estimated costs
python -m src.cli info

# Run with cost tracking
python -m src.cli run "task" -v  # Verbose shows token usage
```

## License

MIT License - See LICENSE file

## Acknowledgments

- [Anthropic Computer Use API](https://docs.anthropic.com/en/docs/computer-use)
- [anthropic-quickstarts](https://github.com/anthropics/anthropic-quickstarts)
- [PyAutoGUI](https://pyautogui.readthedocs.io/)

---

## Installation Complete ✅

If you followed the installation steps above, your system should now be configured with:

### Installed Components

| Component | Status | Location |
|-----------|--------|----------|
| Python Virtual Environment | ✅ | `./venv/` |
| Dependencies | ✅ | Installed in venv |
| Environment File | ✅ | `./.env` (needs API key) |
| MCP Configuration | ✅ | `~/.roo/mcp.json` or workspace `.roo/mcp.json` |

### MCP Server Configuration

The MCP server is configured in your Roo Code workspace at `.roo/mcp.json`:

```json
{
  "mcpServers": {
    "computer-control": {
      "command": "/Users/imorgado/Desktop/autonomous-computer-control/venv/bin/python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "/Users/imorgado/Desktop/autonomous-computer-control",
      "env": {
        "PYTHONPATH": "/Users/imorgado/Desktop/autonomous-computer-control"
      }
    }
  }
}
```

### Available MCP Tools (12 total)

After restarting Roo Code, these tools will be available:

| Tool | Description |
|------|-------------|
| `screenshot` | Capture screen as base64 PNG |
| `mouse_move` | Move cursor to coordinates |
| `left_click` | Left click at position |
| `right_click` | Right click at position |
| `double_click` | Double-click at position |
| `middle_click` | Middle-click at position |
| `left_click_drag` | Click and drag |
| `scroll` | Scroll wheel |
| `type` | Type text |
| `key` | Press key combination |
| `cursor_position` | Get current cursor position |
| `get_screen_size` | Get screen dimensions |

### Next Steps

1. **Add your LLM Provider API key**:

   **Option A: Free Tier (Recommended)**
   ```bash
   # Edit .env file
   nano autonomous-computer-control/.env
   # Add: GOOGLE_API_KEY=your_google_api_key (get from https://aistudio.google.com/apikey)
   # Add: GEMINI_MODEL=gemini-2.0-flash-exp
   # Add: LLM_PROVIDER=auto
   ```

   **Option B: Anthropic Claude**
   ```bash
   # Edit .env file
   nano autonomous-computer-control/.env
   # Add: ANTHROPIC_API_KEY=your_anthropic_api_key
   # Add: LLM_PROVIDER=anthropic
   ```

   **Option C: OpenAI**
   ```bash
   # Edit .env file
   nano autonomous-computer-control/.env
   # Add: OPENAI_API_KEY=your_openai_api_key
   # Add: OPENAI_MODEL=gpt-4o-mini
   # Add: LLM_PROVIDER=openai
   ```

2. **Grant Screen Recording permission** (required for screenshots):
   - Open **System Settings** → **Privacy & Security** → **Screen Recording**
   - Enable your terminal application (Terminal, iTerm, VS Code)
   - **Restart your terminal** after granting

3. **Restart Roo Code** to load the MCP server:
   - Close and reopen VS Code/Roo Code
   - The computer-control tools should appear in tool lists

4. **Verify provider setup**:
   ```bash
   cd autonomous-computer-control
   python -m src.cli info
   # Should show your selected provider as available
   ```

5. **Test the MCP tools** in Roo Code:
   - Ask: "Take a screenshot of my desktop"
   - Ask: "Move the mouse to the center of the screen"

---

## Extended Troubleshooting Guide

### Permission Errors

#### Screen Recording Not Working

**Symptoms:**
- `screenshot` tool returns "could not create image from display"
- Empty or black screenshots

**Solutions:**
1. Open **System Settings** → **Privacy & Security** → **Screen Recording**
2. Add your terminal application (VS Code, Terminal.app, iTerm2)
3. Toggle the permission OFF and back ON
4. **Restart your terminal application completely**
5. If using VS Code, restart VS Code

```bash
# Verify screen recording permission
python -m src.cli test-permissions
```

#### Accessibility Not Working

**Symptoms:**
- Mouse/keyboard commands have no effect
- "Operation not permitted" errors

**Solutions:**
1. Open **System Settings** → **Privacy & Security** → **Accessibility**
2. Add your terminal application
3. Restart terminal after granting

### Import Errors

#### ModuleNotFoundError: No module named 'mcp'

**Solutions:**
```bash
# Ensure you're in the virtual environment
cd autonomous-computer-control
source venv/bin/activate
pip install -r requirements.txt
```

#### ModuleNotFoundError: No module named 'src'

**Solutions:**
```bash
# Set PYTHONPATH before running
export PYTHONPATH="/Users/imorgado/Desktop/autonomous-computer-control"
python -m src.mcp_server
```

### API Key Issues

#### "API key not found" or Authentication Errors

**Solutions:**
1. Verify `.env` file exists with correct key:
   ```bash
   cat .env | grep ANTHROPIC
   ```

2. Set environment variable directly:
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```

3. Verify key is valid at [Anthropic Console](https://console.anthropic.com/)

### MCP Server Issues

#### Server Won't Start

**Symptoms:**
- MCP server doesn't appear in Roo Code
- Connection errors in logs

**Solutions:**
1. Test server manually:
   ```bash
   cd autonomous-computer-control
   source venv/bin/activate
   python -m src.mcp_server
   # Should wait for stdin (normal behavior)
   # Press Ctrl+C to exit
   ```

2. Verify MCP config path is correct in `.roo/mcp.json`

3. Check Roo Code logs for MCP connection errors

#### MCP Tools Not Appearing After Restart

**Solutions:**
1. Verify `.roo/mcp.json` exists in workspace root
2. Check JSON syntax is valid:
   ```bash
   python -m json.tool .roo/mcp.json
   ```
3. Restart VS Code completely (not just reload window)
4. Check VS Code Developer Console (Help → Toggle Developer Tools) for errors

### PyAutoGUI Failsafe

PyAutoGUI has a failsafe feature: moving mouse to screen corner aborts all operations.

**To disable (not recommended for production):**
```python
import pyautogui
pyautogui.FAILSAFE = False
```

### Performance Tips

1. **Reduce screenshot quality** for faster operations:
   ```bash
   # In .env
   SCREENSHOT_QUALITY=50
   ```

2. **Increase action delay** if operations are too fast:
   ```bash
   # In .env
   ACTION_DELAY=1.0
   ```

3. **Limit iterations** to prevent runaway automation:
   ```bash
   # In .env
   MAX_ACTIONS_PER_SESSION=50
   ```
