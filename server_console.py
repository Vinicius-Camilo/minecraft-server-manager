#!/usr/bin/env python3
"""
Minecraft Server Console - Lightweight Server Management

Simple console-only interface for basic Minecraft server management without GUI or Discord bot.
This is the lightweight option launched via the "Server Console" option in launcher.py.

Features:
- Start/stop/restart server commands
- Send commands directly to server
- View server output in real-time with timestamps
- Minimal resource usage - no GUI overhead
- Direct server interaction without additional processes
- Clean console interface with basic command set

Usage:
- start     - Start the Minecraft server
- stop      - Stop the Minecraft server  
- restart   - Restart the Minecraft server
- quit      - Exit this console
- help      - Show available commands
- <any>     - Send command directly to server

Perfect for:
- Quick server management without GUI overhead
- Remote server administration
- Low-resource environments
- Direct server command access

Usage: python server_console.py
"""

import subprocess
import sys
import os
import threading
import time
from datetime import datetime

class ServerConsole:
    def __init__(self):
        self.server_process = None
        self.server_running = False
        self.server_dir = r"F:\server mine atm102\atm10 2"
        self.server_jar = "neoforge-21.1.77.jar"  # Adjust as needed
        
        print("🎮 Minecraft Server Console")
        print("=" * 50)
        print(f"Server Directory: {self.server_dir}")
        print("Commands: start, stop, restart, <any server command>, quit")
        print("=" * 50)
        
    def start_server(self):
        """Start the Minecraft server"""
        if self.server_running:
            print("❌ Server is already running!")
            return
            
        if not os.path.exists(self.server_dir):
            print(f"❌ Server directory not found: {self.server_dir}")
            return
            
        jar_path = os.path.join(self.server_dir, self.server_jar)
        if not os.path.exists(jar_path):
            print(f"❌ Server jar not found: {jar_path}")
            return
            
        try:
            print("🚀 Starting Minecraft server...")
            
            # Start server process
            self.server_process = subprocess.Popen(
                ["java", "-jar", self.server_jar, "nogui"],
                cwd=self.server_dir,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.server_running = True
            print("✅ Server starting... (type 'stop' to stop server, 'quit' to exit console)")
            
            # Start output reader thread
            threading.Thread(target=self.read_server_output, daemon=True).start()
            
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            
    def stop_server(self):
        """Stop the Minecraft server"""
        if not self.server_running or not self.server_process:
            print("❌ Server is not running!")
            return
            
        try:
            print("🛑 Stopping server...")
            self.server_process.stdin.write("stop\n")
            self.server_process.stdin.flush()
            
            # Wait for server to stop
            self.server_process.wait(timeout=30)
            self.server_running = False
            print("✅ Server stopped successfully")
            
        except subprocess.TimeoutExpired:
            print("⚠️ Server didn't stop gracefully, forcing termination...")
            self.server_process.terminate()
            self.server_running = False
            print("✅ Server terminated")
        except Exception as e:
            print(f"❌ Error stopping server: {e}")
            
    def send_command(self, command):
        """Send command to server"""
        if not self.server_running or not self.server_process:
            print("❌ Server is not running!")
            return
            
        try:
            self.server_process.stdin.write(command + "\n")
            self.server_process.stdin.flush()
            print(f"💬 Command sent: {command}")
        except Exception as e:
            print(f"❌ Error sending command: {e}")
            
    def read_server_output(self):
        """Read and display server output"""
        while self.server_running and self.server_process:
            try:
                line = self.server_process.stdout.readline()
                if not line:
                    break
                    
                # Display server output with timestamp
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] {line.rstrip()}")
                
            except Exception as e:
                print(f"❌ Error reading server output: {e}")
                break
                
        self.server_running = False
        
    def restart_server(self):
        """Restart the server"""
        print("🔄 Restarting server...")
        self.stop_server()
        time.sleep(3)
        self.start_server()
        
    def run(self):
        """Main console loop"""
        while True:
            try:
                user_input = input(">>> ").strip()
                
                if user_input.lower() == "quit":
                    if self.server_running:
                        print("Stopping server before exit...")
                        self.stop_server()
                    print("👋 Goodbye!")
                    break
                    
                elif user_input.lower() == "start":
                    self.start_server()
                    
                elif user_input.lower() == "stop":
                    self.stop_server()
                    
                elif user_input.lower() == "restart":
                    self.restart_server()
                    
                elif user_input.lower() in ["help", "?"]:
                    print("\nAvailable commands:")
                    print("  start    - Start the Minecraft server")
                    print("  stop     - Stop the Minecraft server")  
                    print("  restart  - Restart the Minecraft server")
                    print("  quit     - Exit this console")
                    print("  help     - Show this help")
                    print("  <any>    - Send command to server\n")
                    
                elif user_input:
                    # Send as server command
                    self.send_command(user_input)
                    
            except KeyboardInterrupt:
                print("\n\n🛑 Ctrl+C detected. Stopping...")
                if self.server_running:
                    self.stop_server()
                break
            except EOFError:
                break
                
def main():
    console = ServerConsole()
    console.run()
    
if __name__ == "__main__":
    main()