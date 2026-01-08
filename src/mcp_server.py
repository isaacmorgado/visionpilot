"""
MCP Server for Computer Control.

Exposes computer control primitives as MCP tools for integration with
Roo Code, Claude Code, and other MCP-compatible clients.

This server provides direct access to mouse, keyboard, and screenshot
capabilities, allowing AI assistants to compose autonomous workflows
with visual feedback.

Usage:
    python -m src.mcp_server
"""

import asyncio
import logging
import sys
from typing import Any, Sequence

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from .computer import ComputerController
from .screen import ScreenCapture

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("computer-control-mcp")

# Initialize server and controller
server = Server("computer-control")
controller = ComputerController()
screen = ScreenCapture()


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available computer control tools.
    
    Each tool maps to a primitive action for mouse, keyboard, or screen control.
    """
    return [
        types.Tool(
            name="screenshot",
            description="Capture a screenshot of the current screen. Returns the image as base64-encoded PNG for visual analysis.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="mouse_move",
            description="Move the mouse cursor to specified screen coordinates without clicking.",
            inputSchema={
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X coordinate (pixels from left edge)"
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y coordinate (pixels from top edge)"
                    }
                },
                "required": ["x", "y"]
            }
        ),
        types.Tool(
            name="left_click",
            description="Perform a left mouse click. If coordinates are provided, moves to that position first.",
            inputSchema={
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X coordinate (optional - clicks at current position if not provided)"
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y coordinate (optional - clicks at current position if not provided)"
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="right_click",
            description="Perform a right mouse click (context menu). If coordinates are provided, moves to that position first.",
            inputSchema={
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X coordinate (optional)"
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y coordinate (optional)"
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="double_click",
            description="Perform a double left click. If coordinates are provided, moves to that position first.",
            inputSchema={
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X coordinate (optional)"
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y coordinate (optional)"
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="middle_click",
            description="Perform a middle mouse click. If coordinates are provided, moves to that position first.",
            inputSchema={
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X coordinate (optional)"
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y coordinate (optional)"
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="left_click_drag",
            description="Click and drag from start position to end position.",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_x": {
                        "type": "integer",
                        "description": "Starting X coordinate"
                    },
                    "start_y": {
                        "type": "integer",
                        "description": "Starting Y coordinate"
                    },
                    "end_x": {
                        "type": "integer",
                        "description": "Ending X coordinate"
                    },
                    "end_y": {
                        "type": "integer",
                        "description": "Ending Y coordinate"
                    }
                },
                "required": ["start_x", "start_y", "end_x", "end_y"]
            }
        ),
        types.Tool(
            name="scroll",
            description="Scroll the mouse wheel. Positive values scroll up, negative scroll down.",
            inputSchema={
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "integer",
                        "description": "Number of scroll clicks (positive=up, negative=down)"
                    },
                    "x": {
                        "type": "integer",
                        "description": "X coordinate to scroll at (optional)"
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y coordinate to scroll at (optional)"
                    }
                },
                "required": ["amount"]
            }
        ),
        types.Tool(
            name="type",
            description="Type text using the keyboard. Use this for entering text into fields, search boxes, etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to type"
                    }
                },
                "required": ["text"]
            }
        ),
        types.Tool(
            name="key",
            description="Press a key or key combination. Use '+' to combine keys (e.g., 'ctrl+c', 'command+shift+s').",
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Key name or combination (e.g., 'Return', 'Tab', 'ctrl+c', 'command+v')"
                    }
                },
                "required": ["key"]
            }
        ),
        types.Tool(
            name="cursor_position",
            description="Get the current cursor position on screen.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="get_screen_size",
            description="Get the screen dimensions in pixels.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> Sequence[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    
    Dispatches to the appropriate ComputerController method based on tool name.
    """
    args = arguments or {}
    
    try:
        if name == "screenshot":
            return await _handle_screenshot()
        
        elif name == "mouse_move":
            x = args.get("x")
            y = args.get("y")
            if x is None or y is None:
                return [types.TextContent(type="text", text="Error: x and y coordinates required")]
            result, _ = controller.execute("mouse_move", coordinate=[x, y])
            return [types.TextContent(type="text", text=result)]
        
        elif name == "left_click":
            coord = _get_coordinate(args)
            result, _ = controller.execute("left_click", coordinate=coord)
            return [types.TextContent(type="text", text=result)]
        
        elif name == "right_click":
            coord = _get_coordinate(args)
            result, _ = controller.execute("right_click", coordinate=coord)
            return [types.TextContent(type="text", text=result)]
        
        elif name == "double_click":
            coord = _get_coordinate(args)
            result, _ = controller.execute("double_click", coordinate=coord)
            return [types.TextContent(type="text", text=result)]
        
        elif name == "middle_click":
            coord = _get_coordinate(args)
            result, _ = controller.execute("middle_click", coordinate=coord)
            return [types.TextContent(type="text", text=result)]
        
        elif name == "left_click_drag":
            start_x = args.get("start_x")
            start_y = args.get("start_y")
            end_x = args.get("end_x")
            end_y = args.get("end_y")
            if None in (start_x, start_y, end_x, end_y):
                return [types.TextContent(type="text", text="Error: start_x, start_y, end_x, end_y all required")]
            result, _ = controller.execute(
                "left_click_drag",
                coordinate=[start_x, start_y],
                text=f"{end_x},{end_y}"
            )
            return [types.TextContent(type="text", text=result)]
        
        elif name == "scroll":
            amount = args.get("amount", 3)
            coord = _get_coordinate(args)
            result, _ = controller.execute("scroll", coordinate=coord, text=str(amount))
            return [types.TextContent(type="text", text=result)]
        
        elif name == "type":
            text = args.get("text")
            if not text:
                return [types.TextContent(type="text", text="Error: text required")]
            result, _ = controller.execute("type", text=text)
            return [types.TextContent(type="text", text=result)]
        
        elif name == "key":
            key = args.get("key")
            if not key:
                return [types.TextContent(type="text", text="Error: key required")]
            result, _ = controller.execute("key", text=key)
            return [types.TextContent(type="text", text=result)]
        
        elif name == "cursor_position":
            result, _ = controller.execute("cursor_position")
            return [types.TextContent(type="text", text=result)]
        
        elif name == "get_screen_size":
            width, height = screen.screen_size
            return [types.TextContent(type="text", text=f"Screen size: {width}x{height} pixels")]
        
        else:
            return [types.TextContent(type="text", text=f"Error: Unknown tool '{name}'")]
    
    except Exception as e:
        logger.error(f"Error executing tool '{name}': {e}", exc_info=True)
        return [types.TextContent(type="text", text=f"Error executing {name}: {str(e)}")]


async def _handle_screenshot() -> Sequence[types.TextContent | types.ImageContent]:
    """
    Capture and return a screenshot as base64 image content.
    """
    try:
        base64_data, image = screen.capture_base64(save=False)
        width, height = image.size
        
        return [
            types.TextContent(
                type="text",
                text=f"Screenshot captured ({width}x{height} pixels)"
            ),
            types.ImageContent(
                type="image",
                data=base64_data,
                mimeType="image/png"
            )
        ]
    except Exception as e:
        logger.error(f"Screenshot failed: {e}", exc_info=True)
        return [types.TextContent(type="text", text=f"Screenshot failed: {str(e)}")]


def _get_coordinate(args: dict) -> list[int] | None:
    """
    Extract x, y coordinates from arguments if both are provided.
    """
    x = args.get("x")
    y = args.get("y")
    if x is not None and y is not None:
        return [x, y]
    return None


async def main():
    """
    Run the MCP server using stdio transport.
    """
    logger.info("Starting Computer Control MCP Server...")
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="computer-control",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
