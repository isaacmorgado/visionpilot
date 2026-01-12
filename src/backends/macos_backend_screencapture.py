"""
macOS Backend Enhancement: screencapture CLI for Adobe Apps

Based on Gemini AI's recommendation for capturing Adobe Premiere Pro windows.

Problem: Adobe uses Metal/OpenGL hardware acceleration for window compositing,
creating "protected pixel data" that ImageIO refuses to serialize. This causes
CGImageDestinationFinalize to fail silently.

Solution: Use macOS `screencapture` CLI, which:
- Is signed by Apple with inherited permissions
- Handles window server compositing differently than CGWindowListCreateImage
- Sidesteps PyObjC memory management and ImageIO quirks

This is Gemini's "Gold Standard" approach for Adobe applications.
"""

import subprocess
import tempfile
from pathlib import Path
from typing import Optional
from PIL import Image


def capture_window_by_id_cli(
    window_id: int, output_path: Optional[str] = None
) -> Optional[Image.Image]:
    """
    Capture a window using macOS screencapture CLI.

    This bypasses CGImageDestination issues with Adobe's hardware-accelerated windows.

    Args:
        window_id: CGWindowID from CGWindowListCopyWindowInfo
        output_path: Optional output path (default: temp file)

    Returns:
        PIL Image if successful, None otherwise
    """
    try:
        # Create temp file if no output path provided
        if output_path is None:
            fd, output_path = tempfile.mkstemp(suffix=".png")
            import os

            os.close(fd)  # Close file descriptor, screencapture will write

        # Run screencapture CLI
        # -l: capture specific window ID
        # -x: no shutter sound
        # -o: no shadow (cleaner for testing)
        result = subprocess.run(
            ["screencapture", "-l", str(window_id), "-x", "-o", output_path],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode != 0:
            print(f"[screencapture CLI] Failed: {result.stderr}")
            return None

        # Load the captured image
        image = Image.open(output_path).convert("RGB")

        # Clean up temp file if we created it
        if output_path.startswith(tempfile.gettempdir()):
            Path(output_path).unlink(missing_ok=True)

        return image

    except subprocess.TimeoutExpired:
        print("[screencapture CLI] Timeout after 5 seconds")
        return None
    except Exception as e:
        print(f"[screencapture CLI] Error: {e}")
        return None


def capture_window_by_pid_cli(pid: int) -> Optional[Image.Image]:
    """
    Capture a window by PID using screencapture CLI.

    Finds the window ID for the given PID, then uses screencapture CLI
    to capture it. This is Gemini's recommended approach for Adobe apps.

    Args:
        pid: Process ID of the target application

    Returns:
        PIL Image if successful, None otherwise
    """
    try:
        from Quartz import CoreGraphics as CG

        # Get list of all windows (use kCGWindowListOptionAll for Adobe apps)
        window_list = CG.CGWindowListCopyWindowInfo(
            CG.kCGWindowListOptionAll, CG.kCGNullWindowID
        )

        if not window_list:
            print("[screencapture CLI] No windows found")
            return None

        # Find the best window for this process ID
        target_window_id = None
        matching_windows = []

        for window in window_list:
            window_pid = window.get("kCGWindowOwnerPID", 0)
            if window_pid == pid:
                bounds = window.get("kCGWindowBounds", {})
                window_id = window.get("kCGWindowNumber", 0)
                window_name = window.get("kCGWindowName", "")
                window_layer = window.get("kCGWindowLayer", 0)

                matching_windows.append(
                    {
                        "id": window_id,
                        "name": window_name,
                        "bounds": bounds,
                        "layer": window_layer,
                        "width": bounds.get("Width", 0),
                        "height": bounds.get("Height", 0),
                    }
                )

        if not matching_windows:
            print(f"[screencapture CLI] No windows found for PID {pid}")
            return None

        # Sort by size (largest first) and layer (0 = normal window)
        matching_windows.sort(
            key=lambda w: (w["layer"] == 0, w["width"] * w["height"]), reverse=True
        )

        target_window_id = matching_windows[0]["id"]

        print(
            f"[screencapture CLI] Capturing window ID {target_window_id} for PID {pid}"
        )
        print(
            f"  Window: {matching_windows[0]['name'][:40] if matching_windows[0]['name'] else 'unnamed'} "
            f"({matching_windows[0]['width']}x{matching_windows[0]['height']})"
        )

        # Use screencapture CLI to capture the window
        return capture_window_by_id_cli(target_window_id)

    except Exception as e:
        print(f"[screencapture CLI] Error: {e}")
        return None


def capture_window_raw_bytes(pid: int) -> Optional[bytes]:
    """
    Extract raw pixel data using CGDataProviderCopyData.

    This is Gemini's alternative approach: bypass CGImageDestination entirely
    and extract raw bytes. Useful for debugging or custom image reconstruction.

    Args:
        pid: Process ID of the target application

    Returns:
        Raw pixel bytes if successful, None otherwise
    """
    try:
        from Quartz import CoreGraphics as CG

        # [Same window finding logic as above]
        window_list = CG.CGWindowListCopyWindowInfo(
            CG.kCGWindowListOptionAll, CG.kCGNullWindowID
        )

        if not window_list:
            return None

        target_window_id = None
        for window in window_list:
            if window.get("kCGWindowOwnerPID", 0) == pid:
                bounds = window.get("kCGWindowBounds", {})
                if bounds.get("Width", 0) > 0 and bounds.get("Height", 0) > 0:
                    target_window_id = window.get("kCGWindowNumber", 0)
                    break

        if not target_window_id:
            return None

        # Capture window as CGImage
        cg_image = CG.CGWindowListCreateImage(
            CG.CGRectNull,
            CG.kCGWindowListOptionIncludingWindow,
            target_window_id,
            CG.kCGWindowImageBoundsIgnoreFraming | CG.kCGWindowImageDefault,
        )

        if not cg_image:
            return None

        # Extract raw bytes using CGDataProvider (Gemini's recommendation)
        provider = CG.CGImageGetDataProvider(cg_image)
        data = CG.CGDataProviderCopyData(provider)

        if data and len(data) > 0:
            print(f"[Raw Bytes] Extracted {len(data)} bytes")
            return bytes(data)
        else:
            print("[Raw Bytes] No data extracted (protected buffer)")
            return None

    except Exception as e:
        print(f"[Raw Bytes] Error: {e}")
        return None


# Test function
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python macos_backend_screencapture.py <PID>")
        sys.exit(1)

    pid = int(sys.argv[1])

    print(f"Testing screencapture CLI with PID {pid}...")
    image = capture_window_by_pid_cli(pid)

    if image:
        print(f"✅ Success! Captured {image.size} image")
        output_path = f"/tmp/test_capture_{pid}.png"
        image.save(output_path)
        print(f"Saved to: {output_path}")
    else:
        print("❌ Failed to capture window")
