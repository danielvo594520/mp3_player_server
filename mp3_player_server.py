#!/usr/bin/env python3
"""
MP3 Player MCP Server
Provides tools to play, stop, and list MP3 files in a specified directory.
"""

import asyncio
import os
import random
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
PLAYLIST: list[str] = []
CURRENT_INDEX: int = -1
PLAY_MODE: str = "sequential"  # sequential, shuffle, repeat_all, repeat_one
SHUFFLE_ORDER: list[int] = []
AUTO_PLAY_TASK: Optional[asyncio.Task] = None


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
    status_parts = []
    
    if IS_PLAYING and pygame.mixer.music.get_busy():
        status_parts.append(f"Playing: {CURRENT_FILE}")
    elif CURRENT_FILE:
        status_parts.append(f"Stopped (last played: {CURRENT_FILE})")
    else:
        status_parts.append("No music has been played yet")
    
    if PLAYLIST:
        status_parts.append(f"\nPlaylist: {len(PLAYLIST)} tracks")
        status_parts.append(f"Current position: {CURRENT_INDEX + 1}/{len(PLAYLIST)}")
        status_parts.append(f"Play mode: {PLAY_MODE}")
    
    return "\n".join(status_parts)


def create_playlist_from_all(shuffle: bool = False) -> str:
    """Create a playlist from all MP3 files."""
    global PLAYLIST, CURRENT_INDEX, SHUFFLE_ORDER
    
    files = get_mp3_files()
    if not files:
        return "No MP3 files found in the music folder"
    
    PLAYLIST = files
    CURRENT_INDEX = 0
    
    if shuffle:
        SHUFFLE_ORDER = list(range(len(PLAYLIST)))
        random.shuffle(SHUFFLE_ORDER)
    else:
        SHUFFLE_ORDER = []
    
    return f"Playlist created with {len(PLAYLIST)} tracks" + (" (shuffled)" if shuffle else "")


def set_play_mode(mode: str) -> str:
    """Set the play mode."""
    global PLAY_MODE, SHUFFLE_ORDER
    
    valid_modes = ["sequential", "shuffle", "repeat_all", "repeat_one"]
    if mode not in valid_modes:
        return f"Invalid mode. Valid modes: {', '.join(valid_modes)}"
    
    PLAY_MODE = mode
    
    # Create shuffle order if switching to shuffle mode
    if mode == "shuffle" and PLAYLIST and not SHUFFLE_ORDER:
        SHUFFLE_ORDER = list(range(len(PLAYLIST)))
        random.shuffle(SHUFFLE_ORDER)
    
    return f"Play mode set to: {mode}"


def get_next_index() -> Optional[int]:
    """Get the next track index based on play mode."""
    if not PLAYLIST:
        return None
    
    if PLAY_MODE == "repeat_one":
        return CURRENT_INDEX
    
    if PLAY_MODE == "shuffle":
        if not SHUFFLE_ORDER:
            SHUFFLE_ORDER.extend(range(len(PLAYLIST)))
            random.shuffle(SHUFFLE_ORDER)
        
        current_shuffle_pos = SHUFFLE_ORDER.index(CURRENT_INDEX) if CURRENT_INDEX in SHUFFLE_ORDER else -1
        next_shuffle_pos = (current_shuffle_pos + 1) % len(SHUFFLE_ORDER)
        
        if next_shuffle_pos == 0 and PLAY_MODE != "repeat_all":
            return None  # End of playlist
        
        return SHUFFLE_ORDER[next_shuffle_pos]
    
    # Sequential or repeat_all
    next_index = CURRENT_INDEX + 1
    if next_index >= len(PLAYLIST):
        if PLAY_MODE == "repeat_all":
            return 0
        return None
    
    return next_index


def get_previous_index() -> Optional[int]:
    """Get the previous track index."""
    if not PLAYLIST or CURRENT_INDEX <= 0:
        return None
    
    if PLAY_MODE == "shuffle" and SHUFFLE_ORDER:
        current_shuffle_pos = SHUFFLE_ORDER.index(CURRENT_INDEX)
        previous_shuffle_pos = (current_shuffle_pos - 1) % len(SHUFFLE_ORDER)
        return SHUFFLE_ORDER[previous_shuffle_pos]
    
    return CURRENT_INDEX - 1


def play_track_at_index(index: int) -> str:
    """Play a track at a specific index."""
    global CURRENT_INDEX
    
    if not PLAYLIST:
        return "No playlist created. Use play_all first."
    
    if index < 0 or index >= len(PLAYLIST):
        return f"Invalid index: {index}"
    
    CURRENT_INDEX = index
    filename = PLAYLIST[CURRENT_INDEX]
    return play_mp3(filename)


def next_track() -> str:
    """Skip to the next track."""
    next_index = get_next_index()
    
    if next_index is None:
        return "End of playlist reached"
    
    return play_track_at_index(next_index)


def previous_track() -> str:
    """Go back to the previous track."""
    prev_index = get_previous_index()
    
    if prev_index is None:
        return "Already at the beginning of playlist"
    
    return play_track_at_index(prev_index)


def play_all(shuffle: bool = False) -> str:
    """Play all MP3 files."""
    result = create_playlist_from_all(shuffle)
    if "No MP3 files" in result:
        return result
    
    if shuffle:
        set_play_mode("shuffle")
    
    return play_track_at_index(0)


async def auto_play_monitor():
    """Monitor playback and auto-play next track."""
    global IS_PLAYING
    
    while True:
        await asyncio.sleep(0.5)  # Check every 0.5 seconds
        
        if IS_PLAYING and not pygame.mixer.music.get_busy():
            # Current track has finished
            IS_PLAYING = False
            
            # Try to play next track
            next_index = get_next_index()
            if next_index is not None:
                play_track_at_index(next_index)


def start_auto_play_monitor():
    """Start the auto-play monitor task."""
    global AUTO_PLAY_TASK
    
    if AUTO_PLAY_TASK is None or AUTO_PLAY_TASK.done():
        loop = asyncio.get_event_loop()
        AUTO_PLAY_TASK = loop.create_task(auto_play_monitor())


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
            name="play_all",
            description="Play all MP3 files in the folder with optional shuffle. Enables auto-play for continuous playback.",
            inputSchema={
                "type": "object",
                "properties": {
                    "shuffle": {
                        "type": "boolean",
                        "description": "Whether to shuffle the playlist (default: false)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="set_play_mode",
            description="Set the playback mode: sequential, shuffle, repeat_all, or repeat_one",
            inputSchema={
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "description": "Play mode: 'sequential', 'shuffle', 'repeat_all', or 'repeat_one'",
                        "enum": ["sequential", "shuffle", "repeat_all", "repeat_one"]
                    }
                },
                "required": ["mode"]
            }
        ),
        Tool(
            name="next_track",
            description="Skip to the next track in the playlist",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="previous_track",
            description="Go back to the previous track in the playlist",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
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
            description="Get the current playback status including playlist info",
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
    
    elif name == "play_all":
        shuffle = arguments.get("shuffle", False)
        result = play_all(shuffle)
        return [TextContent(type="text", text=result)]
    
    elif name == "set_play_mode":
        mode = arguments.get("mode", "sequential")
        result = set_play_mode(mode)
        return [TextContent(type="text", text=result)]
    
    elif name == "next_track":
        result = next_track()
        return [TextContent(type="text", text=result)]
    
    elif name == "previous_track":
        result = previous_track()
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
    
    # Start auto-play monitor
    start_auto_play_monitor()
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
