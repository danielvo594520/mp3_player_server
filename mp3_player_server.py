#!/usr/bin/env python3
"""
MP3 Player MCP Server
Provides tools to play, stop, and list MP3 files in a specified directory.
"""

import asyncio
import os
from pathlib import Path
from typing import Optional
import pygame
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# Initialize pygame mixer
pygame.mixer.init()

# Global state
MUSIC_FOLDER: Optional[Path] = None
CURRENT_FILE: Optional[str] = None
IS_PLAYING: bool = False


def set_music_folder(folder_path: str) -> None:
    """Set the music folder path."""
    global MUSIC_FOLDER
    MUSIC_FOLDER = Path(folder_path).resolve()
    if not MUSIC_FOLDER.exists():
        raise ValueError(f"Folder does not exist: {MUSIC_FOLDER}")


def get_mp3_files() -> list[str]:
    """Get list of MP3 files in the music folder."""
    if not MUSIC_FOLDER:
        return []
    
    mp3_files = []
    for file in MUSIC_FOLDER.glob("*.mp3"):
        mp3_files.append(file.name)
    
    return sorted(mp3_files)


def play_mp3(filename: str) -> str:
    """Play an MP3 file."""
    global CURRENT_FILE, IS_PLAYING
    
    if not MUSIC_FOLDER:
        return "Error: Music folder not set"
    
    file_path = MUSIC_FOLDER / filename
    
    if not file_path.exists():
        return f"Error: File not found: {filename}"
    
    try:
        pygame.mixer.music.load(str(file_path))
        pygame.mixer.music.play()
        CURRENT_FILE = filename
        IS_PLAYING = True
        return f"Now playing: {filename}"
    except Exception as e:
        return f"Error playing file: {str(e)}"


def stop_playback() -> str:
    """Stop the current playback."""
    global IS_PLAYING
    
    if not IS_PLAYING:
        return "No music is currently playing"
    
    pygame.mixer.music.stop()
    IS_PLAYING = False
    return f"Stopped playback: {CURRENT_FILE}"


def get_status() -> str:
    """Get current playback status."""
    if IS_PLAYING and pygame.mixer.music.get_busy():
        return f"Playing: {CURRENT_FILE}"
    elif CURRENT_FILE:
        return f"Stopped (last played: {CURRENT_FILE})"
    else:
        return "No music has been played yet"


# Create MCP server
app = Server("mp3-player")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="list_mp3_files",
            description="List all MP3 files in the configured music folder",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="play_mp3",
            description="Play a specific MP3 file from the music folder",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the MP3 file to play (e.g., 'song.mp3')"
                    }
                },
                "required": ["filename"]
            }
        ),
        Tool(
            name="stop_playback",
            description="Stop the currently playing music",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_playback_status",
            description="Get the current playback status",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    
    if name == "list_mp3_files":
        files = get_mp3_files()
        if not files:
            result = "No MP3 files found in the music folder"
        else:
            result = "MP3 Files:\n" + "\n".join(f"- {f}" for f in files)
        
        return [TextContent(type="text", text=result)]
    
    elif name == "play_mp3":
        filename = arguments.get("filename", "")
        result = play_mp3(filename)
        return [TextContent(type="text", text=result)]
    
    elif name == "stop_playback":
        result = stop_playback()
        return [TextContent(type="text", text=result)]
    
    elif name == "get_playback_status":
        result = get_status()
        return [TextContent(type="text", text=result)]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Main entry point."""
    # Set your music folder path here
    # Example: set_music_folder("/path/to/your/music/folder")
    
    # You can also read from environment variable
    music_folder = os.environ.get("MUSIC_FOLDER", "")
    if music_folder:
        set_music_folder(music_folder)
    else:
        print("Warning: MUSIC_FOLDER environment variable not set", flush=True)
        print("Please set it or modify the code to specify your music folder", flush=True)
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
