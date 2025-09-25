#!/usr/bin/env python3
"""
Discord Bot for Minecraft Server Status Monitoring - Console Mode

This Discord bot provides real-time Minecraft server status monitoring and
automatic status updates in Discord channels. This is the standalone console
version launched via the "Discord Bot Console" option in launcher.py.

Features:
- Real-time server status monitoring with automatic updates every 30 seconds
- Automatic status message posting and updating in Discord channels
- External server connectivity testing (internal and external domains)  
- Force server status checks via trigger file system
- Player count and online status tracking
- Server log monitoring for player join/leave events
- Comprehensive error handling and connection management
- Persistent status message management (remembers message ID)
- Visible console output for monitoring bot activity

Functionality:
- Monitors Minecraft server via mcstatus library
- Updates Discord embed with server status, player count, and connectivity
- Tracks player join/leave events from server logs
- Handles both internal and external domain testing
- Automatic reconnection and error recovery

Author: Your Name
License: MIT
Repository: https://github.com/yourusername/minecraft-server-manager
"""

import signal
import threading
from datetime import datetime
import sys

import os
from dotenv import load_dotenv
import discord
import asyncio
from mcstatus import JavaServer

# Ensure stdout is unbuffered for real-time output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

load_dotenv()
TOKEN = os.getenv("TOKEN")  # Bot token from .env
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # Discord channel ID from .env
SERVER_IP = os.getenv("SERVER_IP")  # Minecraft server IP from .env
SERVER_PORT = 25565  # Default port, can be changed in code if needed
LOG_FILE = os.getenv("MINECRAFT_LOG_FILE")  # Log file path from .env


intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent

class StatusBot(discord.Client):
    def set_offline_status(self):
        if self.status_message and self.loop and not self.loop.is_closed():
            try:
                embed = discord.Embed(
                    title="Minecraft Server Status",
                    description="🔴 Offline",
                    color=discord.Color.red()
                )
                fut = asyncio.run_coroutine_threadsafe(self.status_message.edit(embed=embed), self.loop)
                fut.result(timeout=5)
                print("[INFO] Status marked as offline before closing.")
            except asyncio.TimeoutError:
                print("[ERROR] Timeout when marking status offline.")
            except Exception as e:
                print(f"[ERROR] Failed to mark status offline: {type(e).__name__}: {e}")
        else:
            print("[WARN] Could not mark offline - loop closed or message unavailable.")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_message = None

    async def on_ready(self):
        print(f"Connected as {self.user}")
        channel = self.get_channel(CHANNEL_ID)
        if channel is None:
            print(f"Error: Could not find channel with ID {CHANNEL_ID}. Check if the bot has access to the channel.")
            return

        message_id_path = "status_message_id.txt"
        message = None

        # Try to load the message ID from file
        if os.path.exists(message_id_path):
            with open(message_id_path, "r") as f:
                try:
                    message_id = int(f.read().strip())
                    message = await channel.fetch_message(message_id)
                    print(f"[INFO] Editing existing message: {message_id}")
                except Exception as e:
                    print(f"[WARN] Could not fetch previous message: {e}")

        # If not found, send a new message and save its ID
        if message is None:
            embed = discord.Embed(
                title="Minecraft Server Status",
                description="Checking...",
                color=discord.Color.greyple()
            )
            message = await channel.send(embed=embed)
            with open(message_id_path, "w") as f:
                f.write(str(message.id))
            print(f"[INFO] New message sent: {message.id}")

        self.status_message = message

        # Start both tasks
        self.loop.create_task(watch_logs(message))
        self.loop.create_task(poll_status(message))

    async def close(self):
        # Set status to offline before closing
        if self.status_message:
            try:
                embed = discord.Embed(
                    title="Minecraft Server Status",
                    description="🔴 Offline",
                    color=discord.Color.red()
                )
                await self.status_message.edit(embed=embed)
                print("[INFO] Status marked as offline before closing.")
            except Exception as e:
                print(f"[ERROR] Failed to mark status offline: {e}")
        await super().close()

# Shared state
server_online = False
players_online = set()
last_update_time = 0  # Track last update time to prevent rate limiting

async def update_embed(message):
    """Update the Discord embed with current status."""
    global last_update_time
    
    # Rate limiting: minimum 2 seconds between updates
    import time
    current_time = time.time()
    if current_time - last_update_time < 2:
        return  # Skip update if too soon
    
    last_update_time = current_time
    
    if server_online:
        embed = discord.Embed(
            title="Minecraft Server Status",
            description="🟢 Online",
            color=discord.Color.green()
        )
        embed.add_field(name="Players", value=f"{len(players_online)}: {', '.join(players_online) if players_online else 'None'}", inline=False)
    else:
        embed = discord.Embed(
            title="Minecraft Server Status",
            description="🔴 Offline",
            color=discord.Color.red()
        )
    await message.edit(embed=embed)

async def watch_logs(message):
    """Watch Minecraft server log for events."""
    global server_online, players_online

    import re
    # First, scan the log file to reconstruct online players
    joined = []
    left = []
    print(f"[DEBUG] Scanning log file: {LOG_FILE}")
    
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines_processed = 0
            for line in f:
                lines_processed += 1
                # Detect player join
                if "joined the game" in line:
                    match = re.search(r": ([^ ]+) joined the game", line)
                    if match:
                        name = match.group(1)
                        joined.append(name)
                        print(f"[DEBUG] Found join: {name}")
                # Detect player leave
                if "left the game" in line:
                    match = re.search(r": ([^ ]+) left the game", line)
                    if match:
                        name = match.group(1)
                        left.append(name)
                        print(f"[DEBUG] Found leave: {name}")
                # Detect server start
                if "Done (" in line and "For help" not in line:
                    server_online = True
                    # Clear player lists when server restarts
                    joined.clear()
                    left.clear()
                    print(f"[DEBUG] Server started, cleared player lists")
                # Detect server stopping
                if "Stopping server" in line:
                    server_online = False
                    joined.clear()
                    left.clear()
                    print(f"[DEBUG] Server stopped, cleared player lists")
            
            print(f"[DEBUG] Processed {lines_processed} lines from log file")
            print(f"[DEBUG] Total joins found: {joined}")
            print(f"[DEBUG] Total leaves found: {left}")
    except Exception as e:
        print(f"[ERROR] Failed to read log file: {e}")

    # Reconstruct online players - better logic
    players_online.clear()
    player_sessions = {}
    
    # Count joins and leaves for each player
    for name in joined:
        player_sessions[name] = player_sessions.get(name, 0) + 1
    for name in left:
        player_sessions[name] = player_sessions.get(name, 0) - 1
    
    # Players with positive count are online
    for name, count in player_sessions.items():
        if count > 0:
            players_online.add(name)
    
    print(f"[INIT] Online players detected: {', '.join(players_online) if players_online else 'None'}")
    print(f"[DEBUG] Player sessions: {player_sessions}")
    await update_embed(message)

    # Now tail the log file for new events
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                await asyncio.sleep(1)
                continue

            # Only log player joins, leaves, and commands, with timestamp
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if "joined the game" in line:
                match = re.search(r": ([^ ]+) joined the game", line)
                if match:
                    name = match.group(1)
                    players_online.add(name)
                    print(f"[{now}] [LOG] {name} joined the server.")
                    await update_embed(message)
            elif "left the game" in line:
                match = re.search(r": ([^ ]+) left the game", line)
                if match:
                    name = match.group(1)
                    players_online.discard(name)
                    print(f"[{now}] [LOG] {name} left the server.")
                    await update_embed(message)

            # Detect server start
            if "Done (" in line and "For help" not in line:
                server_online = True
                await update_embed(message)

            # Detect server stopping
            if "Stopping server" in line:
                server_online = False
                players_online.clear()
                await update_embed(message)

async def poll_status(message):
    """Backup verification using mcstatus, runs every 5 min if logs don't detect anything."""
    global server_online
    server = JavaServer.lookup(f"{SERVER_IP}:{SERVER_PORT}")
    
    # Also test localhost for comparison
    localhost_server = JavaServer.lookup(f"localhost:{SERVER_PORT}")

    while True:
        # Check for force check trigger file
        force_check_file = "force_server_check.trigger"
        force_check_requested = False
        
        if os.path.exists(force_check_file):
            try:
                os.remove(force_check_file)
                force_check_requested = True
                print("[INFO] Force server check triggered by GUI")
                sys.stdout.flush()
            except:
                pass
        
        external_working = False
        localhost_working = False
        
        # Test external server
        try:
            print(f"[DEBUG] Trying to connect to external server: {SERVER_IP}:{SERVER_PORT}")
            sys.stdout.flush()
            status = server.status()
            external_working = True
            server_online = True
            print(f"[DEBUG] External server online! {status.players.online} players connected")
            
            # Update player list from external server
            players_online.clear()
            if status.players.sample:
                for player in status.players.sample:
                    players_online.add(player.name)
                print(f"[DEBUG] Player names from external server: {', '.join(players_online)}")
            elif status.players.online > 0:
                # Server has players but didn't return names (server config issue)
                print(f"[DEBUG] Server has {status.players.online} players but names not available (server hide-online-players=true?)")
                players_online.add(f"Player 1" if status.players.online == 1 else f"{status.players.online} Players")
            else:
                print(f"[DEBUG] No players online")
            
            sys.stdout.flush()
        except Exception as e:
            print(f"[DEBUG] Error connecting to external server {SERVER_IP}:{SERVER_PORT}: {type(e).__name__}: {e}")
            
            # Provide specific error details
            error_str = str(e).lower()
            if "timeout" in error_str:
                print(f"[DEBUG] Timeout - server may not be externally accessible (firewall/port forwarding?)")
            elif "connection refused" in error_str:
                print(f"[DEBUG] Connection refused - server may be offline or port blocked")
            elif "getaddrinfo" in error_str or "name resolution" in error_str:
                print(f"[DEBUG] DNS error - domain {SERVER_IP} is not resolving to an IP")
                print(f"[DEBUG] Check: 1) No-IP/DynDNS configuration 2) Internet connection 3) Valid domain")
            
        # Test localhost for comparison
        try:
            localhost_status = localhost_server.status()
            localhost_working = True
            print(f"[DEBUG] Local server working: {localhost_status.players.online} players")
            if localhost_status.players.sample:
                local_players = [p.name for p in localhost_status.players.sample]
                print(f"[DEBUG] Local server players: {', '.join(local_players)}")
        except Exception as e:
            print(f"[DEBUG] Local server also failed: {e}")
            
        # Set server status based on external connectivity (what players see)
        if not external_working:
            server_online = False
            players_online.clear()
            
        # Diagnostic summary
        if localhost_working and not external_working:
            print(f"[DEBUG] DIAGNOSIS: Server runs locally but is not externally accessible")
            print(f"[DEBUG] Possible causes: 1) Port forwarding not configured 2) Firewall blocking 3) DNS not updated")
        elif not localhost_working and not external_working:
            print(f"[DEBUG] DIAGNOSIS: Server appears to be completely offline")
        elif external_working:
            print(f"[DEBUG] DIAGNOSIS: Everything working - server externally accessible!")
                
        await update_embed(message)
        
        # Sleep with frequent checks for force triggers if this wasn't a force check
        if not force_check_requested:
            # Sleep for 5 minutes, but check for force triggers every 10 seconds
            for i in range(30):  # 30 * 10 seconds = 5 minutes
                await asyncio.sleep(10)
                if os.path.exists("force_server_check.trigger"):
                    break  # Break early if force check is requested
        else:
            # If this was a force check, wait a bit before next regular check
            await asyncio.sleep(30)


def run_bot():
    global client
    client = StatusBot(intents=intents)

    def handle_exit(sig, frame):
        print(f"[INFO] Exit signal ({sig}) received. Marking status offline...")
        try:
            client.set_offline_status()
        except Exception as e:
            print(f"[ERRO] Erro durante shutdown: {type(e).__name__}: {e}")
        finally:
            print("[INFO] Shutting down bot...")
            import os
            os._exit(0)

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    client.run(TOKEN)

if not TOKEN:
    print("[ERROR] TOKEN not found in environment variables. Check your .env file.")
else:
    run_bot()
