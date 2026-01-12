# VisionPilot API Reference

**Version**: 1.0.0 (Week 5)
**Last Updated**: 2026-01-12

Complete API reference for VisionPilot background automation system.

---

## Table of Contents

- [AutomationContext](#automationcontext)
- [Backend Factory](#backend-factory)
- [AbstractBackend](#abstractbackend)
- [PyAutoGUIBackend](#pyautoguibackend)
- [MacOSBackend](#macosbackend)
- [Data Types](#data-types)

---

## AutomationContext

**Module**: `src.context`

Playwright-style isolated automation context for background automation.

### Class: `AutomationContext`

```python
class AutomationContext:
    """
    Isolated automation context following Playwright pattern.

    Each context maintains isolated resources and can run independently
    without interfering with other contexts.
    """
```

### Constructor

```python
def __init__(
    self,
    backend: str = "auto",
    action_delay: float = 0.5,
    screenshot_dir: Optional[str] = None,
    temp_dir: Optional[str] = None,
    cleanup_on_close: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
)
```

**Parameters**:
- `backend` (str): Backend type
  - `"auto"` - Auto-detect best backend (macOS Native on macOS, PyAutoGUI elsewhere)
  - `"pyautogui"` - Use PyAutoGUI backend (cross-platform, 1.0x baseline)
  - `"macos"` - Use macOS Native backend (15-30x faster, macOS only)
- `action_delay` (float): Delay between actions in seconds (default: 0.5)
- `screenshot_dir` (str, optional): Custom directory for screenshots (default: isolated temp dir)
- `temp_dir` (str, optional): Custom directory for temp files (default: isolated temp dir)
- `cleanup_on_close` (bool): Whether to cleanup resources on context close (default: True)
- `metadata` (dict, optional): Custom metadata to attach to this context

**Raises**:
- `ValueError`: If backend type is invalid

**Example**:
```python
# Basic usage with auto backend
with AutomationContext() as ctx:
    ctx.screenshot()
    ctx.click(100, 100)

# macOS Native backend for maximum performance
with AutomationContext(backend="macos", action_delay=0.0) as ctx:
    ctx.screenshot(save=False)

# Custom directories and metadata
with AutomationContext(
    backend="macos",
    screenshot_dir="/path/to/screenshots",
    cleanup_on_close=False,
    metadata={"task": "premiere_automation", "user": "john"}
) as ctx:
    ctx.screenshot()
```

### Context Manager

```python
def __enter__(self) -> AutomationContext
def __exit__(self, exc_type, exc_val, exc_tb) -> bool
```

Supports Python's `with` statement for automatic cleanup.

**Example**:
```python
with AutomationContext(backend="macos") as ctx:
    ctx.screenshot()
    ctx.click(100, 100)
# Resources automatically cleaned up
```

### Screen Operations

#### `screenshot()`

```python
def screenshot(self, save: bool = True) -> Tuple[str, Image.Image]
```

Capture a screenshot in this context's isolated directory.

**Parameters**:
- `save` (bool): Whether to save the screenshot to disk (default: True)

**Returns**:
- `Tuple[str, Image.Image]`: Message string and PIL Image object

**Raises**:
- `RuntimeError`: If context is closed

**Events**: Emits `screenshot` event with Image

**Example**:
```python
with AutomationContext() as ctx:
    msg, image = ctx.screenshot(save=False)
    print(f"Screenshot size: {image.size}")
```

#### `get_screen_size()`

```python
def get_screen_size(self) -> Tuple[int, int]
```

Get screen dimensions.

**Returns**:
- `Tuple[int, int]`: (width, height) in pixels

**Raises**:
- `RuntimeError`: If context is closed

**Example**:
```python
with AutomationContext() as ctx:
    width, height = ctx.get_screen_size()
    print(f"Screen: {width}x{height}")
```

### Mouse Operations

#### `cursor_position()`

```python
def cursor_position(self) -> Tuple[str, Tuple[int, int]]
```

Get current cursor position.

**Returns**:
- `Tuple[str, Tuple[int, int]]`: Message string and (x, y) coordinates

**Raises**:
- `RuntimeError`: If context is closed

**Example**:
```python
with AutomationContext() as ctx:
    msg, (x, y) = ctx.cursor_position()
    print(f"Cursor at: ({x}, {y})")
```

#### `mouse_move()`

```python
def mouse_move(self, x: int, y: int) -> str
```

Move mouse to specified position.

**Parameters**:
- `x` (int): X coordinate in pixels
- `y` (int): Y coordinate in pixels

**Returns**:
- `str`: Action message

**Raises**:
- `RuntimeError`: If context is closed

**Events**: Emits `mouse_move` event with (x, y)

**Example**:
```python
with AutomationContext() as ctx:
    ctx.mouse_move(500, 300)
```

#### `click()`

```python
def click(
    self,
    x: Optional[int] = None,
    y: Optional[int] = None,
    button: str = "left"
) -> str
```

Click at specified position.

**Parameters**:
- `x` (int, optional): X coordinate (None = current position)
- `y` (int, optional): Y coordinate (None = current position)
- `button` (str): Button to click - `"left"`, `"right"`, or `"middle"` (default: `"left"`)

**Returns**:
- `str`: Action message

**Raises**:
- `RuntimeError`: If context is closed
- `ValueError`: If button type is invalid

**Events**: Emits `click` event with (x, y)

**Example**:
```python
with AutomationContext() as ctx:
    # Click at specific position
    ctx.click(100, 100)

    # Right-click at current position
    ctx.click(button="right")

    # Click at cursor position
    ctx.click()
```

#### `double_click()`

```python
def double_click(
    self,
    x: Optional[int] = None,
    y: Optional[int] = None
) -> str
```

Double-click at specified position.

**Parameters**:
- `x` (int, optional): X coordinate (None = current position)
- `y` (int, optional): Y coordinate (None = current position)

**Returns**:
- `str`: Action message

**Raises**:
- `RuntimeError`: If context is closed

**Example**:
```python
with AutomationContext() as ctx:
    ctx.double_click(200, 150)
```

#### `drag()`

```python
def drag(
    self,
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int
) -> str
```

Drag from start to end position.

**Parameters**:
- `start_x` (int): Starting X coordinate
- `start_y` (int): Starting Y coordinate
- `end_x` (int): Ending X coordinate
- `end_y` (int): Ending Y coordinate

**Returns**:
- `str`: Action message

**Raises**:
- `RuntimeError`: If context is closed

**Example**:
```python
with AutomationContext() as ctx:
    # Drag from (100, 100) to (300, 200)
    ctx.drag(100, 100, 300, 200)
```

#### `scroll()`

```python
def scroll(
    self,
    amount: int,
    x: Optional[int] = None,
    y: Optional[int] = None
) -> str
```

Scroll at specified position.

**Parameters**:
- `amount` (int): Scroll amount (positive = up/right, negative = down/left)
- `x` (int, optional): X coordinate (None = current position)
- `y` (int, optional): Y coordinate (None = current position)

**Returns**:
- `str`: Action message

**Raises**:
- `RuntimeError`: If context is closed

**Example**:
```python
with AutomationContext() as ctx:
    # Scroll up by 3 units at current position
    ctx.scroll(3)

    # Scroll down by 5 units at (400, 300)
    ctx.scroll(-5, 400, 300)
```

### Keyboard Operations

#### `key_press()`

```python
def key_press(self, key_combo: str) -> str
```

Press a key or key combination.

**Parameters**:
- `key_combo` (str): Key or combination (e.g., `"enter"`, `"command+s"`, `"ctrl+c"`)

**Returns**:
- `str`: Action message

**Raises**:
- `RuntimeError`: If context is closed

**Events**: Emits `key_press` event with key_combo

**Supported Keys**:
- Letters: `a-z`
- Numbers: `0-9`
- Special: `enter`, `return`, `tab`, `space`, `backspace`, `delete`, `esc`
- Function: `f1-f12`
- Arrows: `up`, `down`, `left`, `right`
- Modifiers: `command`/`cmd`, `shift`, `ctrl`, `alt`/`option`

**Example**:
```python
with AutomationContext() as ctx:
    # Press Enter
    ctx.key_press("enter")

    # Command+S (Save)
    ctx.key_press("command+s")

    # Ctrl+C (Copy)
    ctx.key_press("ctrl+c")
```

#### `type_text()`

```python
def type_text(self, text: str) -> str
```

Type a string of text.

**Parameters**:
- `text` (str): Text to type

**Returns**:
- `str`: Action message

**Raises**:
- `RuntimeError`: If context is closed

**Example**:
```python
with AutomationContext() as ctx:
    ctx.type_text("Hello, World!")
```

### Background Operations (macOS-specific)

#### `capture_window_by_pid()`

```python
def capture_window_by_pid(self, pid: int) -> Optional[Image.Image]
```

Capture a window by process ID without activating it. **macOS Native backend only.**

**Parameters**:
- `pid` (int): Process ID of the application

**Returns**:
- `Image.Image | None`: PIL Image or None if not supported/failed

**Raises**:
- `RuntimeError`: If context is closed

**Events**: Emits `screenshot` event with Image if successful

**Performance**: 15-30x faster than activating window + screenshot

**Example**:
```python
import subprocess

with AutomationContext(backend="macos") as ctx:
    # Launch Premiere Pro
    proc = subprocess.Popen(["/path/to/premiere"])

    # Capture without activating
    image = ctx.capture_window_by_pid(proc.pid)
    if image:
        print(f"Captured: {image.size}")
```

#### `send_key_to_pid()`

```python
def send_key_to_pid(self, pid: int, key_combo: str) -> bool
```

Send keyboard input to a process without activating it. **macOS Native backend only.**

**Parameters**:
- `pid` (int): Process ID of the application
- `key_combo` (str): Key or combination to send

**Returns**:
- `bool`: True if successful

**Raises**:
- `RuntimeError`: If context is closed

**Events**: Emits `key_press` event with key_combo if successful

**Performance**: 15-30x faster than activating window + key press

**Example**:
```python
import subprocess

with AutomationContext(backend="macos") as ctx:
    proc = subprocess.Popen(["/path/to/premiere"])

    # Send Command+S without activating
    success = ctx.send_key_to_pid(proc.pid, "command+s")
```

### Event System

#### `on()`

```python
def on(self, event: str, callback: Callable) -> None
```

Register an event callback.

**Parameters**:
- `event` (str): Event name
- `callback` (Callable): Callback function

**Supported Events**:
- `screenshot` - Called after screenshot (callback receives `Image`)
- `click` - Called after click (callback receives `x`, `y`)
- `key_press` - Called after key press (callback receives `key_combo`)
- `mouse_move` - Called after mouse move (callback receives `x`, `y`)
- `context_close` - Called when context closes (no parameters)

**Raises**:
- `ValueError`: If event name is unknown

**Example**:
```python
def on_screenshot(image):
    print(f"Screenshot taken: {image.size}")

def on_click(x, y):
    print(f"Clicked at ({x}, {y})")

with AutomationContext() as ctx:
    ctx.on("screenshot", on_screenshot)
    ctx.on("click", on_click)

    ctx.screenshot()  # Triggers on_screenshot
    ctx.click(100, 100)  # Triggers on_click
```

### Context Management

#### `close()`

```python
def close(self) -> None
```

Close the context and cleanup resources.

Removes temporary directories if `cleanup_on_close` is True.

**Events**: Emits `context_close` event

**Example**:
```python
ctx = AutomationContext()
try:
    ctx.screenshot()
finally:
    ctx.close()

# Or use context manager (automatic):
with AutomationContext() as ctx:
    ctx.screenshot()
```

### Properties

#### `backend_name`

```python
@property
def backend_name(self) -> str
```

Get backend name.

**Returns**:
- `str`: Backend name (`"PyAutoGUI"` or `"macOS Native"`)

**Example**:
```python
with AutomationContext(backend="macos") as ctx:
    print(ctx.backend_name)  # "macOS Native"
```

#### `is_closed`

```python
@property
def is_closed(self) -> bool
```

Check if context is closed.

**Returns**:
- `bool`: True if closed

**Example**:
```python
ctx = AutomationContext()
print(ctx.is_closed)  # False
ctx.close()
print(ctx.is_closed)  # True
```

#### `action_count`

```python
@property
def action_count(self) -> int
```

Get number of actions performed.

**Returns**:
- `int`: Total action count

**Example**:
```python
with AutomationContext() as ctx:
    ctx.screenshot()
    ctx.click(100, 100)
    print(ctx.action_count)  # 2
```

#### `screenshot_count`

```python
@property
def screenshot_count(self) -> int
```

Get number of screenshots taken.

**Returns**:
- `int`: Total screenshot count

**Example**:
```python
with AutomationContext() as ctx:
    ctx.screenshot()
    ctx.screenshot()
    print(ctx.screenshot_count)  # 2
```

#### `context_id`

```python
@property
def context_id(self) -> str
```

Get unique context ID.

**Returns**:
- `str`: 8-character UUID prefix

**Example**:
```python
with AutomationContext() as ctx:
    print(ctx.context_id)  # "a3f8c1d2"
```

#### `screenshot_dir`

```python
@property
def screenshot_dir(self) -> Path
```

Get screenshot directory path.

**Returns**:
- `Path`: Screenshot directory

**Example**:
```python
with AutomationContext() as ctx:
    print(ctx.screenshot_dir)
    # /tmp/visionpilot_screenshots_a3f8c1d2_xyz/
```

#### `temp_dir`

```python
@property
def temp_dir(self) -> Path
```

Get temp directory path.

**Returns**:
- `Path`: Temp directory

**Example**:
```python
with AutomationContext() as ctx:
    print(ctx.temp_dir)
    # /tmp/visionpilot_temp_a3f8c1d2_xyz/
```

### Methods

#### `get_stats()`

```python
def get_stats(self) -> Dict[str, Any]
```

Get context statistics.

**Returns**:
- `Dict[str, Any]`: Statistics dictionary

**Dictionary Keys**:
- `context_id` (str): Unique context ID
- `backend` (str): Backend name
- `created_at` (str): ISO timestamp
- `closed` (bool): Whether context is closed
- `action_count` (int): Total actions performed
- `screenshot_count` (int): Total screenshots taken
- `screenshot_dir` (str): Screenshot directory path
- `temp_dir` (str): Temp directory path
- `metadata` (dict): Custom metadata

**Example**:
```python
with AutomationContext(metadata={"task": "test"}) as ctx:
    ctx.screenshot()
    ctx.click(100, 100)

    stats = ctx.get_stats()
    print(f"Actions: {stats['action_count']}")
    print(f"Screenshots: {stats['screenshot_count']}")
    print(f"Metadata: {stats['metadata']}")
```

---

## Backend Factory

**Module**: `src.backends.factory`

Factory for creating backend instances.

### Function: `create_backend()`

```python
def create_backend(
    backend_type: str = "auto",
    action_delay: float = 0.5,
    screenshot_dir: Optional[str] = None
) -> AbstractBackend
```

Create a backend instance.

**Parameters**:
- `backend_type` (str): Backend type - `"auto"`, `"pyautogui"`, or `"macos"`
- `action_delay` (float): Delay between actions (default: 0.5)
- `screenshot_dir` (str, optional): Screenshot directory

**Returns**:
- `AbstractBackend`: Backend instance

**Raises**:
- `ValueError`: If backend_type is invalid

**Auto-detection**:
- macOS (Darwin): macOS Native backend
- Other platforms: PyAutoGUI backend

**Example**:
```python
from src.backends.factory import create_backend

# Auto-detect
backend = create_backend("auto")

# Explicit backend
backend = create_backend("macos", action_delay=0.0)
```

---

## AbstractBackend

**Module**: `src.backends.abstract_backend`

Abstract base class defining the backend interface.

### Class: `AbstractBackend`

```python
class AbstractBackend(ABC):
    """Abstract base class for automation backends."""
```

All backends must implement these methods:
- `screenshot(save: bool) -> Tuple[str, Image.Image]`
- `get_screen_size() -> Tuple[int, int]`
- `cursor_position() -> Tuple[str, Tuple[int, int]]`
- `mouse_move(x: int, y: int) -> str`
- `left_click(x: Optional[int], y: Optional[int]) -> str`
- `right_click(x: Optional[int], y: Optional[int]) -> str`
- `middle_click(x: Optional[int], y: Optional[int]) -> str`
- `double_click(x: Optional[int], y: Optional[int]) -> str`
- `left_click_drag(start_x: int, start_y: int, end_x: int, end_y: int) -> str`
- `scroll(amount: int, x: Optional[int], y: Optional[int]) -> str`
- `key_press(key_combo: str) -> str`
- `type_text(text: str) -> str`
- `get_capabilities() -> BackendCapabilities`

---

## Data Types

### BackendCapabilities

```python
@dataclass
class BackendCapabilities:
    """Backend capability information."""

    name: str                      # Backend name
    background_capture: bool       # Can capture windows in background
    background_input: bool         # Can send input to background windows
    performance_multiplier: float  # Performance vs baseline (PyAutoGUI = 1.0)
    platform: str                  # Platform name
```

**Example**:
```python
with AutomationContext(backend="macos") as ctx:
    caps = ctx._backend.get_capabilities()
    print(f"Backend: {caps.name}")
    print(f"Background capture: {caps.background_capture}")
    print(f"Performance: {caps.performance_multiplier}x")
```

---

## Usage Examples

### Basic Screenshot

```python
from src.context import AutomationContext

with AutomationContext() as ctx:
    msg, image = ctx.screenshot()
    print(f"Saved: {msg}")
```

### Parallel Contexts

```python
from src.context import AutomationContext

# Create multiple isolated contexts
with AutomationContext(backend="macos") as ctx1:
    with AutomationContext(backend="macos") as ctx2:
        # Each has isolated directories
        ctx1.screenshot()  # Saved to ctx1's directory
        ctx2.screenshot()  # Saved to ctx2's directory
```

### Event Monitoring

```python
from src.context import AutomationContext

actions = []

def log_action(event_type, *args):
    actions.append((event_type, args))

with AutomationContext() as ctx:
    ctx.on("screenshot", lambda img: log_action("screenshot", img.size))
    ctx.on("click", lambda x, y: log_action("click", x, y))

    ctx.screenshot()
    ctx.click(100, 100)

print(actions)
# [('screenshot', ((1920, 1080),)), ('click', (100, 100))]
```

### Background Automation (macOS)

```python
import subprocess
from src.context import AutomationContext

with AutomationContext(backend="macos", action_delay=0.0) as ctx:
    # Launch app
    proc = subprocess.Popen(["/Applications/Premiere Pro.app"])

    # Wait for app to launch
    import time
    time.sleep(3)

    # Automate without activating
    image = ctx.capture_window_by_pid(proc.pid)
    ctx.send_key_to_pid(proc.pid, "command+s")
```

---

## Error Handling

### Common Exceptions

- `RuntimeError`: Operation on closed context
- `ValueError`: Invalid parameter (backend, button type, etc.)
- `Exception`: Backend-specific errors

### Example

```python
from src.context import AutomationContext

try:
    with AutomationContext(backend="macos") as ctx:
        ctx.screenshot()
        ctx.click(100, 100)
except ValueError as e:
    print(f"Invalid parameter: {e}")
except RuntimeError as e:
    print(f"Context error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Performance Tips

1. **Use macOS Native backend on macOS** for 15-30x speedup
2. **Set `action_delay=0.0`** for maximum speed
3. **Use `save=False`** for screenshots you don't need to persist
4. **Batch operations** in a single context instead of creating/destroying
5. **Use background operations** (`capture_window_by_pid`, `send_key_to_pid`) to eliminate window activation delays

---

## See Also

- [WEEK_3_COMPLETE.md](WEEK_3_COMPLETE.md) - AutomationContext implementation details
- [WEEK_4_COMPLETE.md](WEEK_4_COMPLETE.md) - Testing and benchmarking
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Migrating from direct backend usage
