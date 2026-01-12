# Migration Guide: Moving to AutomationContext

**Target Audience**: Existing visionpilot users upgrading to Week 3+ implementation
**Migration Complexity**: Low-Medium (mostly API wrapper changes)
**Estimated Time**: 15-30 minutes for typical codebase

---

## Table of Contents

- [Why Migrate?](#why-migrate)
- [Breaking Changes](#breaking-changes)
- [Migration Steps](#migration-steps)
- [Before & After Examples](#before--after-examples)
- [Common Patterns](#common-patterns)
- [Troubleshooting](#troubleshooting)

---

## Why Migrate?

### Benefits of AutomationContext

1. **Isolated Resources** - Multiple contexts can run in parallel without interference
2. **Automatic Cleanup** - Context manager handles resource management
3. **Event System** - Monitor and log automation actions
4. **Better Ergonomics** - Simpler API with context manager pattern
5. **Future-Proof** - All new features will use AutomationContext

### Performance

Same 15-30x performance gain with macOS Native backend is preserved.

---

## Breaking Changes

### Import Changes

**Before (Weeks 1-2)**:
```python
from src.backends.factory import create_backend
```

**After (Week 3+)**:
```python
from src.context import AutomationContext
```

### API Changes

| Old API | New API | Notes |
|---------|---------|-------|
| `backend = create_backend("macos")` | `with AutomationContext(backend="macos") as ctx:` | Context manager pattern |
| `backend.screenshot()` | `ctx.screenshot()` | Same parameters |
| `backend.left_click(x, y)` | `ctx.click(x, y)` | Simplified method name |
| `backend.right_click(x, y)` | `ctx.click(x, y, button="right")` | Unified click method |
| `backend.middle_click(x, y)` | `ctx.click(x, y, button="middle")` | Unified click method |
| `backend.left_click_drag(...)` | `ctx.drag(...)` | Renamed for clarity |
| No context isolation | Isolated per context | New feature |
| No event system | `ctx.on("event", callback)` | New feature |

---

## Migration Steps

### Step 1: Update Imports

**Before**:
```python
from src.backends.factory import create_backend
from src.backends.abstract_backend import AbstractBackend
```

**After**:
```python
from src.context import AutomationContext
```

### Step 2: Replace Backend Creation with Context Manager

**Before**:
```python
backend = create_backend("macos", action_delay=0.5)
try:
    backend.screenshot()
    backend.left_click(100, 100)
finally:
    # Manual cleanup (none available in old API)
    pass
```

**After**:
```python
with AutomationContext(backend="macos", action_delay=0.5) as ctx:
    ctx.screenshot()
    ctx.click(100, 100)
# Automatic cleanup
```

### Step 3: Update Method Calls

Replace specific click methods with unified `click()`:

**Before**:
```python
backend.left_click(100, 100)
backend.right_click(200, 200)
backend.middle_click(300, 300)
```

**After**:
```python
ctx.click(100, 100)  # Left click by default
ctx.click(200, 200, button="right")
ctx.click(300, 300, button="middle")
```

Replace `left_click_drag()` with `drag()`:

**Before**:
```python
backend.left_click_drag(100, 100, 300, 200)
```

**After**:
```python
ctx.drag(100, 100, 300, 200)
```

### Step 4: Add Event Callbacks (Optional)

Take advantage of the new event system:

```python
def on_screenshot(image):
    print(f"Screenshot captured: {image.size}")

with AutomationContext() as ctx:
    ctx.on("screenshot", on_screenshot)
    ctx.screenshot()  # Triggers callback
```

---

## Before & After Examples

### Example 1: Simple Screenshot Script

**Before (Weeks 1-2)**:
```python
from src.backends.factory import create_backend

backend = create_backend("macos")
msg, image = backend.screenshot()
print(f"Screenshot: {image.size}")
```

**After (Week 3+)**:
```python
from src.context import AutomationContext

with AutomationContext(backend="macos") as ctx:
    msg, image = ctx.screenshot()
    print(f"Screenshot: {image.size}")
```

**Changes**: Wrapped in context manager, backend → ctx

---

### Example 2: Mouse Automation

**Before**:
```python
from src.backends.factory import create_backend

backend = create_backend("macos", action_delay=0.1)

# Move and click
backend.mouse_move(500, 300)
backend.left_click(500, 300)

# Right-click
backend.right_click(600, 400)

# Drag
backend.left_click_drag(100, 100, 300, 200)
```

**After**:
```python
from src.context import AutomationContext

with AutomationContext(backend="macos", action_delay=0.1) as ctx:
    # Move and click
    ctx.mouse_move(500, 300)
    ctx.click(500, 300)

    # Right-click
    ctx.click(600, 400, button="right")

    # Drag
    ctx.drag(100, 100, 300, 200)
```

**Changes**: Context manager, unified click(), renamed drag()

---

### Example 3: Keyboard Automation

**Before**:
```python
from src.backends.factory import create_backend

backend = create_backend("macos")
backend.key_press("command+s")
backend.type_text("Hello, World!")
```

**After**:
```python
from src.context import AutomationContext

with AutomationContext(backend="macos") as ctx:
    ctx.key_press("command+s")
    ctx.type_text("Hello, World!")
```

**Changes**: Context manager only (no API changes)

---

### Example 4: Background Automation (macOS)

**Before**:
```python
import subprocess
from src.backends.factory import create_backend

backend = create_backend("macos")

# Launch app
proc = subprocess.Popen(["/Applications/Premiere Pro.app"])
pid = proc.pid

# No background methods available in old API
# Had to activate window first (slow)
```

**After**:
```python
import subprocess
from src.context import AutomationContext

with AutomationContext(backend="macos") as ctx:
    # Launch app
    proc = subprocess.Popen(["/Applications/Premiere Pro.app"])

    # Capture without activating (15-30x faster)
    image = ctx.capture_window_by_pid(proc.pid)

    # Send keys without activating
    ctx.send_key_to_pid(proc.pid, "command+s")
```

**Changes**: New background methods available

---

### Example 5: Parallel Automation

**Before**: Not easily possible (shared resources)

**After**:
```python
from src.context import AutomationContext

# Multiple isolated contexts
with AutomationContext(backend="macos") as ctx1:
    with AutomationContext(backend="macos") as ctx2:
        # Each has isolated directories
        ctx1.screenshot()  # → /tmp/visionpilot_screenshots_abc123_/
        ctx2.screenshot()  # → /tmp/visionpilot_screenshots_def456_/
```

**Changes**: New capability

---

### Example 6: Event Monitoring

**Before**: Not available

**After**:
```python
from src.context import AutomationContext

log = []

def log_action(action_type, *args):
    log.append((action_type, args))

with AutomationContext() as ctx:
    ctx.on("screenshot", lambda img: log_action("screenshot", img.size))
    ctx.on("click", lambda x, y: log_action("click", x, y))

    ctx.screenshot()
    ctx.click(100, 100)

print(log)
# [('screenshot', ((1920, 1080),)), ('click', (100, 100))]
```

**Changes**: New capability

---

### Example 7: Long-Running Automation

**Before**:
```python
from src.backends.factory import create_backend

backend = create_backend("macos")

for i in range(100):
    backend.screenshot()
    backend.left_click(i * 10, i * 10)

# No way to track progress
```

**After**:
```python
from src.context import AutomationContext

with AutomationContext(backend="macos") as ctx:
    for i in range(100):
        ctx.screenshot()
        ctx.click(i * 10, i * 10)

    # Check progress
    stats = ctx.get_stats()
    print(f"Actions: {stats['action_count']}")
    print(f"Screenshots: {stats['screenshot_count']}")
```

**Changes**: Progress tracking with `get_stats()`

---

## Common Patterns

### Pattern 1: Reusable Automation Function

**Before**:
```python
def automate_task(backend):
    backend.screenshot()
    backend.left_click(100, 100)
    backend.key_press("enter")

# Usage
from src.backends.factory import create_backend
backend = create_backend("macos")
automate_task(backend)
```

**After**:
```python
def automate_task(ctx):
    ctx.screenshot()
    ctx.click(100, 100)
    ctx.key_press("enter")

# Usage
from src.context import AutomationContext
with AutomationContext(backend="macos") as ctx:
    automate_task(ctx)
```

### Pattern 2: Error Handling

**Before**:
```python
from src.backends.factory import create_backend

backend = create_backend("macos")
try:
    backend.screenshot()
    backend.left_click(100, 100)
except Exception as e:
    print(f"Error: {e}")
finally:
    # No cleanup available
    pass
```

**After**:
```python
from src.context import AutomationContext

try:
    with AutomationContext(backend="macos") as ctx:
        ctx.screenshot()
        ctx.click(100, 100)
except Exception as e:
    print(f"Error: {e}")
# Cleanup happens automatically even on exception
```

### Pattern 3: Custom Screenshot Directory

**Before**:
```python
from src.backends.factory import create_backend

backend = create_backend("macos", screenshot_dir="/path/to/screenshots")
backend.screenshot()
```

**After**:
```python
from src.context import AutomationContext

with AutomationContext(
    backend="macos",
    screenshot_dir="/path/to/screenshots"
) as ctx:
    ctx.screenshot()
```

### Pattern 4: Metadata Tracking

**Before**: Not available

**After**:
```python
from src.context import AutomationContext

metadata = {
    "task": "premiere_automation",
    "user": "john",
    "workflow": "video_editing"
}

with AutomationContext(backend="macos", metadata=metadata) as ctx:
    ctx.screenshot()

    # Retrieve metadata
    stats = ctx.get_stats()
    print(stats["metadata"])
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'src.context'"

**Solution**: Ensure you're using Week 3+ implementation. Check that `src/context.py` exists.

```bash
# Verify file exists
ls src/context.py

# If missing, you're on an older version
git pull  # or update your code
```

---

### Issue: "AttributeError: 'AutomationContext' object has no attribute 'left_click'"

**Solution**: Use the new unified `click()` method instead:

```python
# Old
ctx.left_click(100, 100)

# New
ctx.click(100, 100)
```

---

### Issue: "RuntimeError: Context ... is closed"

**Solution**: Ensure you're operating inside the context manager:

```python
# Wrong
ctx = AutomationContext()
ctx.close()
ctx.screenshot()  # Error!

# Right
with AutomationContext() as ctx:
    ctx.screenshot()  # OK
```

---

### Issue: Screenshots saved to different directory than expected

**Solution**: Each context has its own isolated directory. Check the directory:

```python
with AutomationContext() as ctx:
    print(f"Screenshots: {ctx.screenshot_dir}")
    ctx.screenshot()
```

To use a custom directory:

```python
with AutomationContext(screenshot_dir="/my/custom/dir") as ctx:
    ctx.screenshot()
```

---

### Issue: Need to preserve directories after context closes

**Solution**: Use `cleanup_on_close=False`:

```python
with AutomationContext(cleanup_on_close=False) as ctx:
    print(f"Screenshots: {ctx.screenshot_dir}")
    ctx.screenshot()
# Directory still exists after context closes
```

---

### Issue: Event callbacks not firing

**Solution**: Register callbacks before performing actions:

```python
# Wrong order
with AutomationContext() as ctx:
    ctx.screenshot()  # No callback yet
    ctx.on("screenshot", my_callback)  # Too late

# Right order
with AutomationContext() as ctx:
    ctx.on("screenshot", my_callback)  # Register first
    ctx.screenshot()  # Callback fires
```

---

### Issue: Background methods not available

**Solution**: Ensure you're using macOS Native backend:

```python
# Wrong - PyAutoGUI doesn't support background operations
with AutomationContext(backend="pyautogui") as ctx:
    ctx.capture_window_by_pid(pid)  # Returns None

# Right
with AutomationContext(backend="macos") as ctx:
    image = ctx.capture_window_by_pid(pid)  # Works on macOS
```

---

### Issue: Performance regression after migration

**Solution**: Ensure you're using the same backend and `action_delay`:

```python
# Before (Week 2)
backend = create_backend("macos", action_delay=0.0)

# After (Week 3) - use same settings
with AutomationContext(backend="macos", action_delay=0.0) as ctx:
    pass
```

Performance should be identical or better.

---

## Migration Checklist

Use this checklist to verify your migration:

- [ ] Updated all imports from `src.backends.factory` to `src.context`
- [ ] Replaced `create_backend()` with `AutomationContext()` context manager
- [ ] Changed `backend.left_click()` to `ctx.click()`
- [ ] Changed `backend.right_click()` to `ctx.click(button="right")`
- [ ] Changed `backend.middle_click()` to `ctx.click(button="middle")`
- [ ] Changed `backend.left_click_drag()` to `ctx.drag()`
- [ ] All backend operations now inside `with AutomationContext() as ctx:` blocks
- [ ] Removed manual cleanup code (now automatic)
- [ ] Added event callbacks where useful (optional)
- [ ] Added metadata tracking where useful (optional)
- [ ] Tested that performance is preserved
- [ ] Verified screenshots are saved to expected location
- [ ] Tested error handling

---

## Performance Comparison

The 15-30x performance gain from Week 2 (macOS Native backend) is **fully preserved** in Week 3+:

| Operation | PyAutoGUI | macOS Native (Old) | AutomationContext + macOS (New) |
|-----------|-----------|-------------------|--------------------------------|
| Screenshot | 100ms | 5ms | 5ms ✅ Same |
| Mouse move | 80ms | 4ms | 4ms ✅ Same |
| Click | 90ms | 5ms | 5ms ✅ Same |
| Background capture | N/A | 3ms | 3ms ✅ Same |

AutomationContext is a **zero-overhead wrapper** around the backend.

---

## Need Help?

If you encounter issues not covered in this guide:

1. Check [API_REFERENCE.md](API_REFERENCE.md) for complete API documentation
2. Review [WEEK_3_COMPLETE.md](WEEK_3_COMPLETE.md) for implementation details
3. Run Week 4 tests to verify your installation:
   ```bash
   python3 run_all_week4_tests.py
   ```

---

## Summary

Migration from Weeks 1-2 to Week 3+ is straightforward:

1. **Import**: `from src.context import AutomationContext`
2. **Wrap**: Use `with AutomationContext() as ctx:` context manager
3. **Replace**: `backend.left_click()` → `ctx.click()`
4. **Enjoy**: Isolated resources, event system, automatic cleanup

The migration is **backward-compatible** in performance (same 15-30x speedup) while adding new capabilities for parallel automation and event monitoring.
