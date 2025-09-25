#!/usr/bin/env python3
"""
Minecraft Server Manager - Launcher Interface

Clean 3-option launcher for the Minecraft Server Management Suite.
Provides simple interface to choose between three distinct management modes.

Options:
1. Server Manager - Full GUI interface with all features (server_gui.py)
2. Discord Bot Console - Discord bot with visible console output (bot.py) 
3. Server Console - Lightweight server-only management (server_console.py)

Each option serves a specific purpose:
- Server Manager: Complete interface for server and bot management
- Bot Console: Standalone Discord bot with monitoring output
- Server Console: Pure server management without GUI or bot overhead

Usage: python launcher.py
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

class LauncherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Server Launcher")
        self.root.geometry("500x450")  # Increased height to ensure all buttons fit
        self.root.configure(bg="#2b2b2b")
        self.root.resizable(False, False)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title_label = tk.Label(self.root, text="🎮 Minecraft Server Launcher", 
                              bg="#2b2b2b", fg="white", 
                              font=('Arial', 18, 'bold'))
        title_label.pack(pady=(30, 20))
        
        # Description
        desc_label = tk.Label(self.root, 
                             text="Choose your interface:",
                             bg="#2b2b2b", fg="#cccccc", 
                             font=('Arial', 12))
        desc_label.pack(pady=(0, 30))
        
        # Buttons frame
        buttons_frame = tk.Frame(self.root, bg="#2b2b2b")
        buttons_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        # Server Manager GUI
        gui_btn = tk.Button(buttons_frame, 
                           text="🖥️ Server Manager\n(Full GUI Interface)", 
                           command=self.launch_gui_mode,
                           bg="#4CAF50", fg="white", 
                           font=('Arial', 12, 'bold'),
                           height=3,
                           relief="flat", bd=0)
        gui_btn.pack(pady=8, fill="x")
        print("GUI button created")
        
        # Discord Bot Console
        bot_btn = tk.Button(buttons_frame, 
                           text="🤖 Discord Bot Console\n(Bot with Visible Output)", 
                           command=self.launch_bot_console,
                           bg="#2196F3", fg="white", 
                           font=('Arial', 12, 'bold'),
                           height=3,
                           relief="flat", bd=0)
        bot_btn.pack(pady=8, fill="x")
        print("Bot button created")
        
        # Server Only Console
        server_btn = tk.Button(buttons_frame, 
                              text="⚡ Server Console\n(Server Only, No Bot/GUI)", 
                              command=self.launch_server_console,
                              bg="#FF5722", fg="white", 
                              font=('Arial', 12, 'bold'),
                              height=3,
                              relief="flat", bd=0)
        server_btn.pack(pady=8, fill="x")
        print("Server button created")
        
        # Info label at bottom
        info_label = tk.Label(self.root, 
                             text="Three clean options: Full GUI • Bot Console • Server Only",
                             bg="#2b2b2b", fg="#888888", 
                             font=('Arial', 10),
                             justify="center")
        info_label.pack(side="bottom", pady=15)
        
    def launch_gui_mode(self):
        """Launch Server Manager with full GUI interface"""
        messagebox.showinfo("Launching", "Server Manager GUI will start after you click OK.\nThis launcher will then close.")
        
        try:
            subprocess.Popen([sys.executable.replace('python.exe', 'pythonw.exe'), "server_gui.py"],
                           creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
            self.root.destroy()
            sys.exit(0)
        except Exception as e:
            try:
                subprocess.Popen([sys.executable, "server_gui.py"])
                self.root.destroy()
                sys.exit(0)
            except Exception as e2:
                messagebox.showerror("Error", f"Failed to launch Server Manager: {e2}")
            
    def launch_bot_console(self):
        """Launch Discord bot with visible console output"""
        try:
            subprocess.Popen([sys.executable, "bot.py"], 
                           creationflags=0)  # Visible console window
            messagebox.showinfo("Launched", "Discord bot is starting in console mode...\nThis launcher will now close.")
            self.root.destroy()
            sys.exit(0)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Discord bot console: {e}")
            
    def launch_server_console(self):
        """Launch server-only console (no GUI, no Discord bot)"""
        try:
            subprocess.Popen([sys.executable, "server_console.py"])
            messagebox.showinfo("Launched", "Server console is starting...\nThis launcher will now close.")
            self.root.destroy()
            sys.exit(0)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch server console: {e}")

def main():
    root = tk.Tk()
    app = LauncherGUI(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()