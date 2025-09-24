#!/usr/bin/env python3
"""
Minecraft Server & Discord Bot Manager

A comprehensive Python-based management interface for Minecraft servers and Discord bots 
with real-time monitoring, performance analytics, and intelligent alerting system.

Features:
- Server start/stop with intelligent process management
- Discord bot integration with automatic status updates
- Real-time performance monitoring (CPU, Memory, simulated TPS)
- Player activity tracking and management tools (kick, ban, OP)
- Interactive server console with bidirectional communication
- Server properties editor with backup system and common settings helper
- Configurable performance alerts with visual/audio notifications
- Professional dark-themed tabbed GUI interface
- Comprehensive error handling and process cleanup

Technical Architecture:
- Multi-threaded GUI application using Tkinter
- Process management via psutil and subprocess
- Discord bot integration with mcstatus server queries
- Real-time performance data collection and analysis
- JSON-based configuration and statistics persistence

Author: Your Name
License: MIT
Repository: https://github.com/yourusername/minecraft-server-manager
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import queue
import time
import os
from datetime import datetime, timedelta
import re
import json
import collections
import winsound  # For system sounds on Windows

class MinecraftServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Server & Discord Bot Manager")
        self.root.geometry("1400x900")
        self.root.configure(bg="#2b2b2b")
        
        # Server process and communication
        self.server_process = None
        self.bot_process = None
        self.log_queue = queue.Queue()
        self.bot_log_queue = queue.Queue()
        self.server_running = False
        self.bot_running = False
        
        # Server paths - update these as needed
        self.server_dir = r"F:\server mine atm102\atm10 2"
        self.log_file = r"F:\server mine atm102\atm10 2\logs\latest.log"
        self.bot_dir = r"E:\pessoal\Bot Discord"
        
        # Analytics data
        self.performance_data = {
            'cpu': collections.deque(maxlen=60),  # Last 60 data points
            'memory': collections.deque(maxlen=60),
            'timestamps': collections.deque(maxlen=60),
            'tps': collections.deque(maxlen=60)
        }
        self.player_data = {}  # {player_name: {'join_time': datetime, 'total_playtime': seconds}}
        self.analytics_update_interval = 5000  # 5 seconds
        
        # Performance alert settings
        self.memory_threshold_mb = 4096  # 4GB warning threshold
        self.cpu_threshold_percent = 85  # 85% CPU warning threshold
        self.tps_threshold = 15  # TPS warning threshold
        self.last_memory_alert = None
        self.last_cpu_alert = None
        self.last_tps_alert = None
        self.alert_cooldown = 300  # 5 minutes between same-type alerts
        self.last_alert_time = 0  # Track last alert time for cooldown
        
        self.setup_ui()
        self.setup_styles()
        
        # Start log monitoring
        self.start_log_monitoring()
        
        # Start analytics monitoring
        self.start_analytics_monitoring()
        
        # Check if bot is already running
        self.check_existing_processes()
        
        # Start periodic analytics updates
        self.schedule_analytics_update()
        
    def schedule_analytics_update(self):
        """Schedule periodic analytics display updates"""
        self.update_analytics_display()
        # Schedule next update
        self.root.after(self.analytics_update_interval, self.schedule_analytics_update)
        
    def setup_styles(self):
        """Configure the visual theme"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Dark theme colors
        bg_color = "#2b2b2b"
        text_color = "#ffffff"
        accent_color = "#4CAF50"
        
        # Configure colors
        style.configure('Title.TLabel', 
                       background=bg_color, 
                       foreground=text_color, 
                       font=('Arial', 16, 'bold'))
        
        style.configure('ServerStatus.TLabel',
                       background=bg_color,
                       foreground="#ff0000",  # Red for offline
                       font=('Arial', 12, 'bold'))
                       
        style.configure('BotStatus.TLabel',
                       background=bg_color,
                       foreground="#ff0000",  # Red for offline  
                       font=('Arial', 12, 'bold'))
        
        # Notebook styling
        style.configure('TNotebook', 
                       background=bg_color,
                       borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background="#404040",
                       foreground=text_color,
                       padding=[20, 10],
                       font=('Arial', 11, 'bold'))
        style.map('TNotebook.Tab',
                 background=[('selected', accent_color)],
                 foreground=[('selected', text_color)])
        
        # Frame styling
        style.configure('TFrame', background=bg_color)
        
        style.configure('ServerStatus.TLabel', 
                       background='#2b2b2b', 
                       foreground='#00ff00', 
                       font=('Arial', 11, 'bold'))
        
        style.configure('BotStatus.TLabel', 
                       background='#2b2b2b', 
                       foreground='#00ff00', 
                       font=('Arial', 11, 'bold'))
        
        style.configure('Server.TButton',
                       font=('Arial', 10, 'bold'))
        
    def setup_ui(self):
        """Create the user interface"""
        # Header frame
        title_frame = tk.Frame(self.root, bg="#2b2b2b", height=80)
        title_frame.pack(fill="x", padx=10, pady=5)
        title_frame.pack_propagate(False)
        
        # Title on left side
        title_label = ttk.Label(title_frame, text="🎮 Minecraft Server & Discord Bot Manager", style='Title.TLabel')
        title_label.pack(side="left", pady=20, padx=10)
        
        # Status indicators on right side
        status_frame = tk.Frame(title_frame, bg="#2b2b2b")
        status_frame.pack(side="right", pady=10, padx=20, fill="y")
        
        # Server status row
        server_status_row = tk.Frame(status_frame, bg="#2b2b2b")
        server_status_row.pack(fill="x", pady=2)
        
        tk.Label(server_status_row, text="Server:", bg="#2b2b2b", fg="white", 
                font=('Arial', 11, 'bold')).pack(side="left")
        self.server_status_label = tk.Label(server_status_row, text="● OFFLINE", 
                                          bg="#2b2b2b", fg="#ff4444", 
                                          font=('Arial', 11, 'bold'))
        self.server_status_label.pack(side="right", padx=(10, 0))
        
        # Bot status row
        bot_status_row = tk.Frame(status_frame, bg="#2b2b2b")
        bot_status_row.pack(fill="x", pady=2)
        
        tk.Label(bot_status_row, text="Bot:", bg="#2b2b2b", fg="white", 
                font=('Arial', 11, 'bold')).pack(side="left")
        self.bot_status_label = tk.Label(bot_status_row, text="● OFFLINE", 
                                        bg="#2b2b2b", fg="#ff4444", 
                                        font=('Arial', 11, 'bold'))
        self.bot_status_label.pack(side="right", padx=(10, 0))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Server Control Tab
        self.create_control_tab()
        
        # Discord Bot Tab
        self.create_bot_tab()
        
        # Server Console Tab
        self.create_console_tab()
        
        # Log Viewer Tab
        self.create_log_tab()
        
        # Players Tab
        self.create_players_tab()
        
        # Server Properties Tab
        self.create_properties_tab()
        
        # Analytics Tab
        self.create_analytics_tab()
        
    def create_bot_tab(self):
        """Create Discord bot management tab"""
        bot_frame = ttk.Frame(self.notebook)
        self.notebook.add(bot_frame, text="🤖 Discord Bot")
        
        # Bot control buttons
        bot_button_frame = tk.Frame(bot_frame, bg="#3b3b3b")
        bot_button_frame.pack(fill="x", padx=10, pady=10)
        
        self.start_bot_btn = tk.Button(bot_button_frame, text="🟢 Start Bot", 
                                      command=self.start_bot, 
                                      bg="#4CAF50", fg="white", font=('Arial', 12, 'bold'),
                                      padx=20, pady=10)
        self.start_bot_btn.pack(side="left", padx=5)
        
        self.stop_bot_btn = tk.Button(bot_button_frame, text="🔴 Stop Bot", 
                                     command=self.stop_bot, 
                                     bg="#f44336", fg="white", font=('Arial', 12, 'bold'),
                                     padx=20, pady=10, state="disabled")
        self.stop_bot_btn.pack(side="left", padx=5)
        
        self.restart_bot_btn = tk.Button(bot_button_frame, text="🔄 Restart Bot", 
                                        command=self.restart_bot, 
                                        bg="#FF9800", fg="white", font=('Arial', 12, 'bold'),
                                        padx=20, pady=10, state="disabled")
        self.restart_bot_btn.pack(side="left", padx=5)
        
        # Emergency stop button
        self.emergency_stop_btn = tk.Button(bot_button_frame, text="🚨 Kill All Bot Processes", 
                                          command=self.emergency_stop_bot, 
                                          bg="#d32f2f", fg="white", font=('Arial', 10, 'bold'),
                                          padx=15, pady=10)
        self.emergency_stop_btn.pack(side="left", padx=5)
        
        # Force server check button
        self.force_check_btn = tk.Button(bot_button_frame, text="🔍 Force Server Check", 
                                        command=self.force_server_check, 
                                        bg="#2196F3", fg="white", font=('Arial', 10, 'bold'),
                                        padx=15, pady=10)
        self.force_check_btn.pack(side="left", padx=5)
        
        # Bot info frame
        bot_info_frame = tk.LabelFrame(bot_frame, text="Bot Information", 
                                      bg="#3b3b3b", fg="white", font=('Arial', 11, 'bold'))
        bot_info_frame.pack(fill="x", padx=10, pady=10)
        
        # Bot status info
        self.bot_info_text = scrolledtext.ScrolledText(bot_info_frame, height=4, 
                                                      bg="#1e1e1e", fg="#cccccc", 
                                                      font=('Consolas', 10))
        self.bot_info_text.pack(fill="x", padx=10, pady=10)
        
        # Bot console
        bot_log_label = tk.Label(bot_frame, text="Bot Console:", 
                                bg="#2b2b2b", fg="white", font=('Arial', 11, 'bold'))
        bot_log_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        # Bot log controls
        bot_log_control_frame = tk.Frame(bot_frame, bg="#3b3b3b")
        bot_log_control_frame.pack(fill="x", padx=10, pady=5)
        
        self.bot_auto_scroll_var = tk.BooleanVar(value=True)
        bot_auto_scroll_check = tk.Checkbutton(bot_log_control_frame, text="Auto-scroll", 
                                              variable=self.bot_auto_scroll_var,
                                              bg="#3b3b3b", fg="white", 
                                              selectcolor="#3b3b3b")
        bot_auto_scroll_check.pack(side="right")
        
        clear_bot_logs_btn = tk.Button(bot_log_control_frame, text="Clear Console", 
                                      command=self.clear_bot_logs, 
                                      bg="#ff5722", fg="white", font=('Arial', 10))
        clear_bot_logs_btn.pack(side="right", padx=10)
        
        # Bot log display
        self.bot_log_display = scrolledtext.ScrolledText(bot_frame, 
                                                        height=20, 
                                                        bg="#1e1e1e", 
                                                        fg="#00bfff", 
                                                        font=('Consolas', 9))
        self.bot_log_display.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Bot console input
        bot_input_frame = tk.Frame(bot_frame, bg="#3b3b3b")
        bot_input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        tk.Label(bot_input_frame, text="Console Input:", 
                bg="#3b3b3b", fg="white", font=('Arial', 10, 'bold')).pack(side="left")
        
        self.bot_input_entry = tk.Entry(bot_input_frame, 
                                       bg="#2b2b2b", fg="white", 
                                       font=('Consolas', 10),
                                       insertbackground="white",
                                       state="disabled")
        self.bot_input_entry.pack(side="left", fill="x", expand=True, padx=10)
        self.bot_input_entry.bind('<Return>', self.send_bot_input)
        
        # Add placeholder behavior
        self.bot_input_placeholder = "Type bot commands here... (bot must be running)"
        self.setup_bot_input_placeholder()
        
        send_btn = tk.Button(bot_input_frame, text="Send", 
                           command=self.send_bot_input, 
                           bg="#4CAF50", fg="white", font=('Arial', 9, 'bold'),
                           padx=15)
        send_btn.pack(side="right")
        
    def create_control_tab(self):
        """Create server control tab"""
        control_frame = ttk.Frame(self.notebook)
        self.notebook.add(control_frame, text="🎛️ Server Control")
        
        # Server control buttons
        button_frame = tk.Frame(control_frame, bg="#3b3b3b")
        button_frame.pack(fill="x", padx=10, pady=10)
        
        self.start_btn = tk.Button(button_frame, text="🟢 Start Server", 
                                  command=self.start_server, 
                                  bg="#4CAF50", fg="white", font=('Arial', 12, 'bold'),
                                  padx=20, pady=10)
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = tk.Button(button_frame, text="🔴 Stop Server", 
                                 command=self.stop_server, 
                                 bg="#f44336", fg="white", font=('Arial', 12, 'bold'),
                                 padx=20, pady=10, state="disabled")
        self.stop_btn.pack(side="left", padx=5)
        
        self.restart_btn = tk.Button(button_frame, text="🔄 Restart Server", 
                                    command=self.restart_server, 
                                    bg="#FF9800", fg="white", font=('Arial', 12, 'bold'),
                                    padx=20, pady=10, state="disabled")
        self.restart_btn.pack(side="left", padx=5)
        
        # Check/Connect server button (smart button)
        self.check_server_btn = tk.Button(button_frame, text="� Check/Connect Server", 
                                         command=self.smart_server_check, 
                                         bg="#2196F3", fg="white", font=('Arial', 11, 'bold'),
                                         padx=15, pady=10)
        self.check_server_btn.pack(side="left", padx=5)
        
        # Server info frame
        info_frame = tk.LabelFrame(control_frame, text="Server Information", 
                                  bg="#3b3b3b", fg="white", font=('Arial', 11, 'bold'))
        info_frame.pack(fill="x", padx=10, pady=10)
        
        # Server details
        details = [
            ("Server Directory:", self.server_dir),
            ("Log File:", self.log_file),
            ("Server Type:", "NeoForged Minecraft Server"),
            ("Version:", "ATM 10")
        ]
        
        for i, (label, value) in enumerate(details):
            row_frame = tk.Frame(info_frame, bg="#3b3b3b")
            row_frame.pack(fill="x", padx=10, pady=5)
            
            tk.Label(row_frame, text=label, bg="#3b3b3b", fg="white", 
                    font=('Arial', 10, 'bold')).pack(side="left")
            tk.Label(row_frame, text=value, bg="#3b3b3b", fg="#cccccc", 
                    font=('Arial', 10)).pack(side="left", padx=(10, 0))
        
    def create_console_tab(self):
        """Create interactive console tab"""
        console_frame = ttk.Frame(self.notebook)
        self.notebook.add(console_frame, text="💻 Console")
        
        # Console controls
        control_frame = tk.Frame(console_frame, bg="#2b2b2b")
        control_frame.pack(fill="x", padx=10, pady=5)
        
        console_label = tk.Label(control_frame, text="Server Console Output:", 
                               bg="#2b2b2b", fg="white", font=('Arial', 11, 'bold'))
        console_label.pack(side="left")
        
        # Auto-scroll checkbox for console
        self.console_auto_scroll_var = tk.BooleanVar(value=True)
        auto_scroll_check = tk.Checkbutton(control_frame, text="Auto-scroll", 
                                          variable=self.console_auto_scroll_var,
                                          bg="#2b2b2b", fg="white", 
                                          selectcolor="#3b3b3b",
                                          font=('Arial', 10))
        auto_scroll_check.pack(side="right")
        
        self.console_output = scrolledtext.ScrolledText(console_frame, 
                                                       height=25, 
                                                       bg="#1e1e1e", 
                                                       fg="#00ff00", 
                                                       font=('Consolas', 10),
                                                       insertbackground="white")
        self.console_output.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Command input
        command_frame = tk.Frame(console_frame, bg="#2b2b2b")
        command_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(command_frame, text="Command:", bg="#2b2b2b", fg="white", 
                font=('Arial', 11, 'bold')).pack(side="left")
        
        self.command_entry = tk.Entry(command_frame, bg="#3b3b3b", fg="white", 
                                     font=('Consolas', 11), insertbackground="white")
        self.command_entry.pack(side="left", fill="x", expand=True, padx=10)
        self.command_entry.bind('<Return>', self.send_command)
        
        self.send_btn = tk.Button(command_frame, text="Send", 
                                 command=self.send_command, 
                                 bg="#2196F3", fg="white", font=('Arial', 10, 'bold'))
        self.send_btn.pack(side="right")
        
    def create_log_tab(self):
        """Create log viewer tab"""
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="📋 Logs")
        
        # Log controls
        control_frame = tk.Frame(log_frame, bg="#3b3b3b")
        control_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(control_frame, text="Server Logs:", bg="#3b3b3b", fg="white", 
                font=('Arial', 11, 'bold')).pack(side="left")
        
        self.auto_scroll_var = tk.BooleanVar(value=True)
        auto_scroll_check = tk.Checkbutton(control_frame, text="Auto-scroll", 
                                          variable=self.auto_scroll_var,
                                          bg="#3b3b3b", fg="white", 
                                          selectcolor="#3b3b3b")
        auto_scroll_check.pack(side="right")
        
        clear_btn = tk.Button(control_frame, text="Clear Logs", 
                             command=self.clear_logs, 
                             bg="#ff5722", fg="white", font=('Arial', 10))
        clear_btn.pack(side="right", padx=10)
        
        # Log display
        self.log_display = scrolledtext.ScrolledText(log_frame, 
                                                    height=30, 
                                                    bg="#1e1e1e", 
                                                    fg="#ffffff", 
                                                    font=('Consolas', 9))
        self.log_display.pack(fill="both", expand=True, padx=10, pady=5)
        
    def create_players_tab(self):
        """Create players management tab"""
        players_frame = ttk.Frame(self.notebook)
        self.notebook.add(players_frame, text="👥 Players")
        
        # Players list
        tk.Label(players_frame, text="Online Players:", 
                font=('Arial', 12, 'bold')).pack(anchor="w", padx=10, pady=10)
        
        self.players_listbox = tk.Listbox(players_frame, height=10, 
                                         bg="#3b3b3b", fg="white", 
                                         font=('Arial', 11))
        self.players_listbox.pack(fill="x", padx=10, pady=5)
        
        # Player actions
        action_frame = tk.Frame(players_frame, bg="#2b2b2b")
        action_frame.pack(fill="x", padx=10, pady=10)
        
        actions = [
            ("Kick Player", self.kick_player, "#ff9800"),
            ("Ban Player", self.ban_player, "#f44336"),
            ("Make OP", self.make_op, "#4caf50"),
            ("Remove OP", self.remove_op, "#ff5722")
        ]
        
        for text, command, color in actions:
            btn = tk.Button(action_frame, text=text, command=command, 
                           bg=color, fg="white", font=('Arial', 10))
            btn.pack(side="left", padx=5)
            
    def create_properties_tab(self):
        """Create server properties editor tab"""
        props_frame = ttk.Frame(self.notebook)
        self.notebook.add(props_frame, text="⚙️ Server Properties")
        
        # Title and file path info
        title_frame = tk.Frame(props_frame, bg="#2b2b2b")
        title_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(title_frame, text="Server Properties Editor", 
                font=('Arial', 14, 'bold'), bg="#2b2b2b", fg="white").pack(side="left")
                
        # Properties file path
        self.properties_file = os.path.join(self.server_dir, "server.properties")
        
        # Action buttons
        button_frame = tk.Frame(props_frame, bg="#2b2b2b")
        button_frame.pack(fill="x", padx=10, pady=5)
        
        reload_btn = tk.Button(button_frame, text="🔄 Reload", 
                              command=self.reload_properties, 
                              bg="#2196F3", fg="white", font=('Arial', 10, 'bold'),
                              padx=15, pady=5)
        reload_btn.pack(side="left", padx=5)
        
        save_btn = tk.Button(button_frame, text="💾 Save", 
                            command=self.save_properties, 
                            bg="#4CAF50", fg="white", font=('Arial', 10, 'bold'),
                            padx=15, pady=5)
        save_btn.pack(side="left", padx=5)
        
        reset_btn = tk.Button(button_frame, text="🔄 Reset", 
                             command=self.reset_properties, 
                             bg="#FF9800", fg="white", font=('Arial', 10, 'bold'),
                             padx=15, pady=5)
        reset_btn.pack(side="left", padx=5)
        
        # Template button
        template_btn = tk.Button(button_frame, text="📋 Common Settings", 
                               command=self.show_common_properties, 
                               bg="#9C27B0", fg="white", font=('Arial', 10, 'bold'),
                               padx=15, pady=5)
        template_btn.pack(side="left", padx=5)
        
        # Properties editor
        editor_frame = tk.Frame(props_frame, bg="#2b2b2b")
        editor_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollable text editor
        text_frame = tk.Frame(editor_frame)
        text_frame.pack(fill="both", expand=True)
        
        self.properties_text = tk.Text(text_frame, 
                                     bg="#3b3b3b", fg="white", 
                                     font=('Consolas', 10),
                                     wrap=tk.NONE)
        
        # Scrollbars
        v_scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=self.properties_text.yview)
        h_scrollbar = tk.Scrollbar(text_frame, orient="horizontal", command=self.properties_text.xview)
        
        self.properties_text.config(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack text editor and scrollbars
        self.properties_text.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        # Status bar
        self.properties_status = tk.Label(props_frame, text="Ready", 
                                        bg="#2b2b2b", fg="#4CAF50", 
                                        font=('Arial', 10))
        self.properties_status.pack(fill="x", padx=10, pady=5)
        
        # Load properties file on startup
        self.reload_properties()
    
    def check_existing_server_process(self):
        """Check if a Minecraft server is already running"""
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline and 'java' in cmdline[0].lower():
                        # Check if it's a Minecraft server process
                        cmdline_str = ' '.join(cmdline).lower()
                        if (('forgeserver' in cmdline_str) or 
                            ('minecraft' in cmdline_str) or 
                            ('neoforge' in cmdline_str) or
                            ('server.jar' in cmdline_str) or
                            ('spigot' in cmdline_str) or
                            ('paper' in cmdline_str) or
                            ('bukkit' in cmdline_str) or
                            ('fabric' in cmdline_str) or
                            ('-server' in cmdline_str and '.jar' in cmdline_str)):
                            return proc.info['pid']
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except ImportError:
            # psutil not available, skip check
            pass
        return None
        
    def reload_properties(self):
        """Reload server.properties file"""
        try:
            if os.path.exists(self.properties_file):
                with open(self.properties_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.properties_text.delete(1.0, tk.END)
                self.properties_text.insert(1.0, content)
                self.properties_status.config(text="Properties loaded", fg="#4CAF50")
            else:
                self.properties_text.delete(1.0, tk.END)
                self.properties_text.insert(1.0, "# server.properties file not found\n# Start the server once to generate this file")
                self.properties_status.config(text="Properties file not found", fg="#FF9800")
                
        except Exception as e:
            self.properties_status.config(text=f"Error loading: {e}", fg="#f44336")
            
    def save_properties(self):
        """Save current properties to file"""
        try:
            content = self.properties_text.get(1.0, tk.END)
            
            # Create backup
            backup_file = self.properties_file + ".backup"
            if os.path.exists(self.properties_file):
                import shutil
                shutil.copy2(self.properties_file, backup_file)
                
            # Save new content
            with open(self.properties_file, 'w', encoding='utf-8') as f:
                f.write(content.rstrip() + '\n')  # Ensure file ends with newline
                
            self.properties_status.config(text="Properties saved (backup created)", fg="#4CAF50")
            messagebox.showinfo("Saved", f"Properties saved to:\n{self.properties_file}\n\nBackup created: {backup_file}")
            
        except Exception as e:
            error_msg = f"Failed to save properties: {e}"
            self.properties_status.config(text=error_msg, fg="#f44336")
            messagebox.showerror("Save Error", error_msg)
            
    def reset_properties(self):
        """Reset properties to last saved version"""
        if messagebox.askyesno("Reset Properties", 
                              "This will discard all unsaved changes.\n\nAre you sure?"):
            self.reload_properties()
            
    def show_common_properties(self):
        """Show a dialog with common server properties"""
        common_props = {
            "Basic Settings": [
                ("server-port", "25565", "Server port (default: 25565)"),
                ("max-players", "20", "Maximum players"),
                ("motd", "A Minecraft Server", "Message of the day"),
                ("difficulty", "easy", "Difficulty: peaceful, easy, normal, hard"),
                ("gamemode", "survival", "Default gamemode: survival, creative, adventure, spectator")
            ],
            "World Settings": [
                ("level-name", "world", "World folder name"),
                ("level-seed", "", "World seed (empty for random)"),
                ("level-type", "minecraft\\:normal", "World type: normal, flat, largeBiomes, amplified"),
                ("generate-structures", "true", "Generate structures (villages, dungeons, etc.)"),
                ("spawn-protection", "16", "Spawn protection radius")
            ],
            "Performance": [
                ("view-distance", "10", "Render distance (2-32)"),
                ("simulation-distance", "10", "Simulation distance (3-32)"),
                ("max-tick-time", "60000", "Max tick time before server watchdog"),
                ("entity-broadcast-range-percentage", "100", "Entity broadcast range %")
            ],
            "Security": [
                ("online-mode", "true", "Require valid Minecraft accounts"),
                ("white-list", "false", "Enable whitelist"),
                ("enforce-whitelist", "false", "Kick non-whitelisted players"),
                ("op-permission-level", "4", "OP permission level (1-4)")
            ]
        }
        
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Common Server Properties")
        dialog.configure(bg="#2b2b2b")
        dialog.geometry("800x600")
        
        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Main frame with scrollbar
        main_frame = tk.Frame(dialog, bg="#2b2b2b")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(main_frame, bg="#2b2b2b")
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#2b2b2b")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add categories and properties
        for category, props in common_props.items():
            # Category header
            cat_frame = tk.LabelFrame(scrollable_frame, text=category, 
                                    bg="#3b3b3b", fg="white", font=('Arial', 12, 'bold'))
            cat_frame.pack(fill="x", padx=5, pady=10)
            
            for prop_name, default_value, description in props:
                prop_frame = tk.Frame(cat_frame, bg="#3b3b3b")
                prop_frame.pack(fill="x", padx=10, pady=5)
                
                # Property name and description
                tk.Label(prop_frame, text=f"{prop_name}={default_value}", 
                        bg="#3b3b3b", fg="#4CAF50", font=('Consolas', 10, 'bold')).pack(anchor="w")
                tk.Label(prop_frame, text=description, 
                        bg="#3b3b3b", fg="#cccccc", font=('Arial', 9)).pack(anchor="w")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Close button
        close_btn = tk.Button(dialog, text="Close", command=dialog.destroy,
                            bg="#4CAF50", fg="white", font=('Arial', 12, 'bold'),
                            padx=20, pady=10)
        close_btn.pack(pady=10)
        
    def create_analytics_tab(self):
        """Create analytics and performance dashboard tab"""
        analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(analytics_frame, text="📊 Analytics")
        
        # Main container
        main_container = tk.Frame(analytics_frame, bg="#2b2b2b")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Performance Dashboard Section
        perf_frame = tk.LabelFrame(main_container, text="🖥️ Server Performance", 
                                  bg="#3b3b3b", fg="white", font=('Arial', 12, 'bold'))
        perf_frame.pack(fill="x", padx=5, pady=5)
        
        # Performance stats display
        stats_frame = tk.Frame(perf_frame, bg="#3b3b3b")
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        # CPU Usage
        cpu_frame = tk.Frame(stats_frame, bg="#3b3b3b")
        cpu_frame.pack(side="left", fill="x", expand=True, padx=10)
        
        tk.Label(cpu_frame, text="CPU Usage", bg="#3b3b3b", fg="white", 
                font=('Arial', 11, 'bold')).pack()
        self.cpu_label = tk.Label(cpu_frame, text="0.0%", bg="#3b3b3b", 
                                 fg="#4CAF50", font=('Arial', 20, 'bold'))
        self.cpu_label.pack()
        
        # Memory Usage
        mem_frame = tk.Frame(stats_frame, bg="#3b3b3b")
        mem_frame.pack(side="left", fill="x", expand=True, padx=10)
        
        tk.Label(mem_frame, text="Memory Usage", bg="#3b3b3b", fg="white", 
                font=('Arial', 11, 'bold')).pack()
        self.memory_label = tk.Label(mem_frame, text="0 MB", bg="#3b3b3b", 
                                    fg="#2196F3", font=('Arial', 20, 'bold'))
        self.memory_label.pack()
        
        # Server Uptime
        uptime_frame = tk.Frame(stats_frame, bg="#3b3b3b")
        uptime_frame.pack(side="left", fill="x", expand=True, padx=10)
        
        tk.Label(uptime_frame, text="Uptime", bg="#3b3b3b", fg="white", 
                font=('Arial', 11, 'bold')).pack()
        self.uptime_label = tk.Label(uptime_frame, text="00:00:00", bg="#3b3b3b", 
                                    fg="#FF9800", font=('Arial', 20, 'bold'))
        self.uptime_label.pack()
        
        # TPS (Ticks Per Second)
        tps_frame = tk.Frame(stats_frame, bg="#3b3b3b")
        tps_frame.pack(side="left", fill="x", expand=True, padx=10)
        
        tk.Label(tps_frame, text="TPS", bg="#3b3b3b", fg="white", 
                font=('Arial', 11, 'bold')).pack()
        self.tps_label = tk.Label(tps_frame, text="20.0", bg="#3b3b3b", 
                                 fg="#9C27B0", font=('Arial', 20, 'bold'))
        self.tps_label.pack()
        
        # Performance Graph (Simple Text-based for now)
        graph_frame = tk.LabelFrame(main_container, text="📈 Performance History", 
                                   bg="#3b3b3b", fg="white", font=('Arial', 12, 'bold'))
        graph_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.performance_text = tk.Text(graph_frame, height=8, bg="#2b2b2b", fg="white", 
                                       font=('Consolas', 9), state='disabled')
        self.performance_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Performance Alert Settings
        alert_frame = tk.LabelFrame(main_container, text="⚠️ Performance Alerts", 
                                   bg="#3b3b3b", fg="white", font=('Arial', 12, 'bold'))
        alert_frame.pack(fill="x", padx=5, pady=5)
        
        alert_controls = tk.Frame(alert_frame, bg="#3b3b3b")
        alert_controls.pack(fill="x", padx=10, pady=10)
        
        # Memory threshold setting
        memory_frame = tk.Frame(alert_controls, bg="#3b3b3b")
        memory_frame.pack(side="left", padx=10)
        
        tk.Label(memory_frame, text="Memory Alert (MB):", bg="#3b3b3b", fg="white", 
                font=('Arial', 10)).pack(side="left")
        self.memory_threshold_var = tk.StringVar(value=str(self.memory_threshold_mb))
        self.alert_memory_entry = tk.Entry(memory_frame, textvariable=self.memory_threshold_var, 
                               width=8, bg="#2b2b2b", fg="white")
        self.alert_memory_entry.pack(side="left", padx=5)
        
        # CPU threshold setting  
        cpu_frame = tk.Frame(alert_controls, bg="#3b3b3b")
        cpu_frame.pack(side="left", padx=10)
        
        tk.Label(cpu_frame, text="CPU Alert (%):", bg="#3b3b3b", fg="white", 
                font=('Arial', 10)).pack(side="left")
        self.cpu_threshold_var = tk.StringVar(value=str(self.cpu_threshold_percent))
        self.alert_cpu_entry = tk.Entry(cpu_frame, textvariable=self.cpu_threshold_var, 
                            width=6, bg="#2b2b2b", fg="white")
        self.alert_cpu_entry.pack(side="left", padx=5)
        
        # Sound alerts toggle
        sound_frame = tk.Frame(alert_controls, bg="#3b3b3b")
        sound_frame.pack(side="left", padx=10)
        
        self.alert_sound_var = tk.BooleanVar(value=True)
        sound_check = tk.Checkbutton(sound_frame, text="Sound Alerts", 
                                    variable=self.alert_sound_var,
                                    bg="#3b3b3b", fg="white", selectcolor="#2b2b2b",
                                    font=('Arial', 10))
        sound_check.pack()
        
        # Apply settings button
        apply_btn = tk.Button(alert_controls, text="💾 Apply Settings", 
                             command=self.apply_alert_settings, 
                             bg="#4CAF50", fg="white", font=('Arial', 10, 'bold'),
                             padx=10, pady=5)
        apply_btn.pack(side="right", padx=10)
        
        # Test alert button (for demonstration)
        test_btn = tk.Button(alert_controls, text="⚠️ Test Alert", 
                            command=self.test_performance_alert, 
                            bg="#FF9800", fg="white", font=('Arial', 10, 'bold'),
                            padx=10, pady=5)
        test_btn.pack(side="right", padx=5)
        
        # Player Activity Section
        player_frame = tk.LabelFrame(main_container, text="👥 Player Activity", 
                                    bg="#3b3b3b", fg="white", font=('Arial', 12, 'bold'))
        player_frame.pack(fill="x", padx=5, pady=5)
        
        # Player stats controls
        player_controls = tk.Frame(player_frame, bg="#3b3b3b")
        player_controls.pack(fill="x", padx=10, pady=5)
        
        refresh_players_btn = tk.Button(player_controls, text="🔄 Refresh Players", 
                                       command=self.refresh_player_stats, 
                                       bg="#4CAF50", fg="white", font=('Arial', 10, 'bold'),
                                       padx=15, pady=5)
        refresh_players_btn.pack(side="left", padx=5)
        
        clear_stats_btn = tk.Button(player_controls, text="🗑️ Clear Stats", 
                                   command=self.clear_player_stats, 
                                   bg="#f44336", fg="white", font=('Arial', 10, 'bold'),
                                   padx=15, pady=5)
        clear_stats_btn.pack(side="left", padx=5)
        
        # Player activity display
        self.player_activity_text = scrolledtext.ScrolledText(player_frame, height=10, 
                                                             bg="#2b2b2b", fg="white", 
                                                             font=('Consolas', 10))
        self.player_activity_text.pack(fill="x", padx=10, pady=10)
        
        # Analytics status
        self.analytics_status = tk.Label(main_container, text="Analytics: Starting...", 
                                        bg="#2b2b2b", fg="#4CAF50", font=('Arial', 10))
        self.analytics_status.pack(fill="x", padx=10, pady=5)
        
        # Initialize displays
        self.update_analytics_display()
        
    def start_analytics_monitoring(self):
        """Start analytics monitoring thread"""
        self.server_start_time = None
        threading.Thread(target=self.analytics_monitor_thread, daemon=True).start()
        
    def analytics_monitor_thread(self):
        """Background thread for collecting performance data"""
        while True:
            try:
                # Check if server is running (either internally started or external)
                if self.server_running and self.server_process:
                    # Server started through GUI
                    self.collect_performance_data()
                else:
                    # Check for external Minecraft server process
                    external_pid = self.check_existing_server_process()
                    if external_pid:
                        self.collect_external_performance_data(external_pid)
                    
                # Update display on main thread
                self.root.after(0, self.update_analytics_display)
                
            except Exception as e:
                self.root.after(0, lambda: self.analytics_status.config(
                    text=f"Analytics error: {e}", fg="#f44336"))
                    
            time.sleep(5)  # Update every 5 seconds
            
    def collect_performance_data(self):
        """Collect server performance data"""
        try:
            import psutil
            
            if hasattr(self.server_process, 'pid'):  # subprocess.Popen object
                pid = self.server_process.pid
            else:  # psutil.Process object
                pid = self.server_process.pid
                
            process = psutil.Process(pid)
            
            # Collect CPU and memory data
            cpu_percent = process.cpu_percent()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024  # Convert to MB
            
            current_time = datetime.now()
            
            # Store data
            self.performance_data['cpu'].append(cpu_percent)
            self.performance_data['memory'].append(memory_mb)
            self.performance_data['timestamps'].append(current_time)
            
            # Try to extract TPS from logs (if available)
            tps = self.extract_tps_from_logs()
            self.performance_data['tps'].append(tps if tps else 20.0)
            
            # Set server start time
            if not self.server_start_time:
                self.server_start_time = current_time
                
        except Exception as e:
            # If we can't get process info, add placeholder data
            self.performance_data['cpu'].append(0)
            self.performance_data['memory'].append(0)
            self.performance_data['timestamps'].append(datetime.now())
            self.performance_data['tps'].append(20.0)
            
    def extract_tps_from_logs(self):
        """Extract TPS information from server logs"""
        # This is a simplified TPS extraction - real TPS would need server-side monitoring
        # For now, we'll simulate based on performance
        try:
            if self.performance_data['cpu']:
                cpu_avg = sum(list(self.performance_data['cpu'])[-5:]) / min(5, len(self.performance_data['cpu']))
                # Simulate TPS based on CPU usage (higher CPU = lower TPS)
                if cpu_avg > 80:
                    return max(5.0, 20.0 - (cpu_avg - 80) * 0.5)
                else:
                    return 20.0
        except:
            pass
        return 20.0
        
    def collect_external_performance_data(self, pid):
        """Collect performance data from external Minecraft server process"""
        try:
            import psutil
            process = psutil.Process(pid)
            
            # Collect CPU and memory data
            cpu_percent = process.cpu_percent()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024  # Convert to MB
            
            current_time = datetime.now()
            
            # Store data
            self.performance_data['cpu'].append(cpu_percent)
            self.performance_data['memory'].append(memory_mb)
            self.performance_data['timestamps'].append(current_time)
            
            # Try to extract TPS from logs (if available)
            tps = self.extract_tps_from_logs()
            self.performance_data['tps'].append(tps if tps else 20.0)
            
            # Set server start time if not already set
            if not self.server_start_time:
                # For external processes, estimate start time from process creation
                try:
                    process_start = datetime.fromtimestamp(process.create_time())
                    self.server_start_time = process_start
                except:
                    self.server_start_time = current_time
                    
        except (psutil.NoSuchProcess, psutil.AccessDenied, ImportError) as e:
            # If we can't get process info, add placeholder data
            self.performance_data['cpu'].append(0)
            self.performance_data['memory'].append(0)
            self.performance_data['timestamps'].append(datetime.now())
            self.performance_data['tps'].append(20.0)
        
    def update_analytics_display(self):
        """Update the analytics display with current data"""
        try:
            # Check if we have performance data (from internal or external server)
            has_server_data = (self.server_running and self.performance_data['cpu']) or \
                             (self.check_existing_server_process() and self.performance_data['cpu'])
                             
            if has_server_data:
                # Update current stats
                current_cpu = self.performance_data['cpu'][-1] if self.performance_data['cpu'] else 0
                current_memory = self.performance_data['memory'][-1] if self.performance_data['memory'] else 0
                current_tps = self.performance_data['tps'][-1] if self.performance_data['tps'] else 20.0
                
                self.cpu_label.config(text=f"{current_cpu:.1f}%")
                self.memory_label.config(text=f"{current_memory:.0f} MB")
                self.tps_label.config(text=f"{current_tps:.1f}")
                
                # Check for performance alerts
                self.check_performance_alerts(current_memory, current_cpu)
                
                # Update uptime
                if self.server_start_time:
                    uptime = datetime.now() - self.server_start_time
                    hours = int(uptime.total_seconds() // 3600)
                    minutes = int((uptime.total_seconds() % 3600) // 60)
                    seconds = int(uptime.total_seconds() % 60)
                    self.uptime_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
                
                # Color code based on performance
                if current_cpu > 80:
                    self.cpu_label.config(fg="#f44336")  # Red for high CPU
                elif current_cpu > 50:
                    self.cpu_label.config(fg="#FF9800")  # Orange for medium CPU
                else:
                    self.cpu_label.config(fg="#4CAF50")  # Green for low CPU
                    
                if current_tps < 15:
                    self.tps_label.config(fg="#f44336")  # Red for low TPS
                elif current_tps < 18:
                    self.tps_label.config(fg="#FF9800")  # Orange for medium TPS
                else:
                    self.tps_label.config(fg="#4CAF50")  # Green for good TPS
                
                # Update performance history
                self.update_performance_graph()
                
                # Update status based on server type
                if self.server_running:
                    self.analytics_status.config(text="Analytics: Active (Internal Server)", fg="#4CAF50")
                else:
                    self.analytics_status.config(text="Analytics: Active (External Server)", fg="#2196F3")
            else:
                # Server offline
                self.cpu_label.config(text="0.0%", fg="#666666")
                self.memory_label.config(text="0 MB", fg="#666666")
                self.uptime_label.config(text="00:00:00", fg="#666666")
                self.tps_label.config(text="--", fg="#666666")
                self.analytics_status.config(text="Analytics: No Server Detected", fg="#FF9800")
                
        except Exception as e:
            self.analytics_status.config(text=f"Analytics error: {e}", fg="#f44336")
            
    def update_performance_graph(self):
        """Update the performance graph display"""
        try:
            if not self.performance_data['timestamps']:
                return
                
            self.performance_text.config(state='normal')
            self.performance_text.delete(1.0, tk.END)
            
            # Show last 10 data points
            recent_data = list(zip(
                list(self.performance_data['timestamps'])[-10:],
                list(self.performance_data['cpu'])[-10:],
                list(self.performance_data['memory'])[-10:],
                list(self.performance_data['tps'])[-10:]
            ))
            
            header = f"{'Time':<8} {'CPU%':<6} {'Memory(MB)':<12} {'TPS':<6}\n"
            separator = "-" * 40 + "\n"
            
            self.performance_text.insert(tk.END, header)
            self.performance_text.insert(tk.END, separator)
            
            for timestamp, cpu, memory, tps in recent_data:
                time_str = timestamp.strftime("%H:%M:%S")
                line = f"{time_str:<8} {cpu:<6.1f} {memory:<12.0f} {tps:<6.1f}\n"
                self.performance_text.insert(tk.END, line)
                
            self.performance_text.config(state='disabled')
            self.performance_text.see(tk.END)
            
        except Exception:
            pass  # Ignore graph update errors
            
    def refresh_player_stats(self):
        """Refresh player statistics display"""
        self.player_activity_text.delete(1.0, tk.END)
        
        if not self.player_data:
            self.player_activity_text.insert(tk.END, "No player data available.\nPlayers will be tracked when they join the server.\n")
            return
            
        # Sort players by total playtime
        sorted_players = sorted(self.player_data.items(), 
                              key=lambda x: x[1].get('total_playtime', 0), reverse=True)
        
        header = f"{'Player':<20} {'Status':<10} {'Total Playtime':<15} {'Session Time'}\n"
        separator = "-" * 70 + "\n"
        
        self.player_activity_text.insert(tk.END, header)
        self.player_activity_text.insert(tk.END, separator)
        
        for player, data in sorted_players:
            total_seconds = data.get('total_playtime', 0)
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            
            status = "Online" if data.get('join_time') else "Offline"
            total_time_str = f"{hours}h {minutes}m"
            
            session_time = ""
            if data.get('join_time'):
                session_seconds = (datetime.now() - data['join_time']).total_seconds()
                session_hours = int(session_seconds // 3600)
                session_minutes = int((session_seconds % 3600) // 60)
                session_time = f"{session_hours}h {session_minutes}m"
            
            line = f"{player:<20} {status:<10} {total_time_str:<15} {session_time}\n"
            self.player_activity_text.insert(tk.END, line)
            
    def clear_player_stats(self):
        """Clear all player statistics"""
        if messagebox.askyesno("Clear Stats", "This will clear all player activity data.\n\nAre you sure?"):
            self.player_data.clear()
            self.refresh_player_stats()
            self.analytics_status.config(text="Player stats cleared", fg="#FF9800")
            
    def track_player_join(self, player_name):
        """Track when a player joins"""
        if player_name not in self.player_data:
            self.player_data[player_name] = {'total_playtime': 0}
        
        self.player_data[player_name]['join_time'] = datetime.now()
        
    def track_player_leave(self, player_name):
        """Track when a player leaves"""
        if player_name in self.player_data and 'join_time' in self.player_data[player_name]:
            join_time = self.player_data[player_name]['join_time']
            session_time = (datetime.now() - join_time).total_seconds()
            
            self.player_data[player_name]['total_playtime'] += session_time
            del self.player_data[player_name]['join_time']  # Remove join_time to mark as offline
    
    def detect_existing_bot(self):
        """Detect existing Discord bot process with improved search"""
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cwd']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    cwd = proc.info.get('cwd', '')
                    
                    if not cmdline:
                        continue
                        
                    # Check if it's a Python process
                    if 'python' not in cmdline[0].lower():
                        continue
                    
                    # Check multiple patterns for bot.py
                    cmdline_str = ' '.join(cmdline).lower()
                    if any(pattern in cmdline_str for pattern in ['bot.py', 'discord', 'bot']):
                        # Additional check: see if it's running from our bot directory
                        if self.bot_dir.lower() in cwd.lower():
                            return proc.info['pid']
                        # Or if bot.py is explicitly in the command line
                        if 'bot.py' in cmdline_str:
                            return proc.info['pid']
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except ImportError:
            pass
        return None
    
    def kill_all_bot_processes(self):
        """Force kill all Discord bot processes"""
        killed_count = 0
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cwd']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    cwd = proc.info.get('cwd', '')
                    
                    if not cmdline:
                        continue
                        
                    # Check if it's a Python process
                    if 'python' not in cmdline[0].lower():
                        continue
                    
                    # Check multiple patterns for bot.py
                    cmdline_str = ' '.join(cmdline).lower()
                    if any(pattern in cmdline_str for pattern in ['bot.py']):
                        # Additional check: see if it's running from our bot directory or has bot.py
                        if (self.bot_dir.lower() in cwd.lower()) or ('bot.py' in cmdline_str):
                            try:
                                process = psutil.Process(proc.info['pid'])
                                process.kill()
                                killed_count += 1
                                self.bot_log_display.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Killed bot process PID: {proc.info['pid']}\n")
                                self.bot_log_display.see(tk.END)
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass
                                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except ImportError:
            pass
        return killed_count
    
    def monitor_existing_bot(self, process):
        """Monitor an existing bot process we connected to"""
        try:
            import psutil
            # Wait for the process to end
            process.wait()
            # When it ends, update our state
            self.bot_running = False
            self.bot_process = None
            self.root.after(0, self.update_ui_state)  # Update UI in main thread
            self.root.after(0, lambda: self.bot_log_display.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Existing bot process ended\n"))
        except Exception:
            pass
    
    def find_running_bot(self):
        """Manually search for and connect to a running bot process"""
        try:
            import psutil
            found_processes = []
            
            # Search for potential bot processes
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cwd']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    name = proc.info.get('name', '')
                    cwd = proc.info.get('cwd', '')
                    
                    if not cmdline:
                        continue
                        
                    # Check if it's a Python process
                    if 'python' in cmdline[0].lower():
                        cmdline_str = ' '.join(cmdline).lower()
                        # Look for potential bot indicators
                        if any(indicator in cmdline_str for indicator in ['bot.py', 'discord', 'bot']):
                            found_processes.append((proc.info['pid'], name, ' '.join(cmdline)[:80] + '...'))
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if not found_processes:
                messagebox.showinfo("No Bot Found", "No potential Discord bot processes found.")
                self.bot_log_display.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 Manual search: No bot processes found\n")
                self.bot_log_display.see(tk.END)
                return
            
            # Always kill existing processes first
            killed_count = 0
            killed_details = []
            
            for pid, name, cmdline in found_processes:
                try:
                    process = psutil.Process(pid)
                    process.kill()
                    killed_count += 1
                    killed_details.append(f"PID {pid} ({name})")
                    self.add_bot_gui_message(f"Killed existing bot process PID {pid} ({name})")
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    self.add_bot_gui_message(f"Could not kill PID {pid}: {e}")
            
            if killed_count > 0:
                details_text = "\n".join(killed_details)
                messagebox.showinfo("Processes Cleaned Up", 
                                   f"Automatically killed {killed_count} existing bot process(es):\n\n{details_text}\n\nYou can now start a fresh bot if needed.")
                self.add_bot_gui_message(f"🧹 Cleaned up {killed_count} existing bot process(es)")
            
            # Reset bot state since we killed any existing processes
            self.bot_running = False
            self.bot_process = None
            self.update_ui_state()
                
        except ImportError:
            messagebox.showerror("Error", "psutil library not available for process detection.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to search for bot processes: {e}")
    
    def show_process_selection_dialog(self, processes):
        """Show interactive dialog to select which bot process to connect to"""
        # Create a new window for process selection
        selection_window = tk.Toplevel(self.root)
        selection_window.title("Multiple Bot Processes Found")
        selection_window.geometry("600x400")
        selection_window.configure(bg="#2b2b2b")
        selection_window.resizable(False, False)
        selection_window.grab_set()  # Make it modal
        
        # Center the window
        selection_window.transient(self.root)
        selection_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        # Title
        title_label = tk.Label(selection_window, 
                              text="🔍 Multiple Bot Processes Found",
                              bg="#2b2b2b", fg="white", 
                              font=('Arial', 14, 'bold'))
        title_label.pack(pady=(20, 10))
        
        # Instructions
        instruction_label = tk.Label(selection_window,
                                    text="Choose which process to connect to, or kill unnecessary processes:",
                                    bg="#2b2b2b", fg="#cccccc",
                                    font=('Arial', 10))
        instruction_label.pack(pady=(0, 20))
        
        # Process list frame
        list_frame = tk.Frame(selection_window, bg="#3b3b3b")
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        for i, (pid, name, cmdline) in enumerate(processes):
            # Process frame
            process_frame = tk.Frame(list_frame, bg="#404040", relief="ridge", bd=1)
            process_frame.pack(fill="x", pady=5, padx=10)
            
            # Process info
            info_label = tk.Label(process_frame,
                                 text=f"PID {pid}: {name}\nCommand: {cmdline}",
                                 bg="#404040", fg="white",
                                 font=('Consolas', 9),
                                 justify="left")
            info_label.pack(side="left", padx=10, pady=5)
            
            # Buttons frame
            button_frame = tk.Frame(process_frame, bg="#404040")
            button_frame.pack(side="right", padx=10, pady=5)
            
            # Connect button
            connect_btn = tk.Button(button_frame,
                                   text="Connect",
                                   command=lambda p=pid, w=selection_window: self.select_process(p, w),
                                   bg="#4CAF50", fg="white",
                                   font=('Arial', 9, 'bold'),
                                   padx=15)
            connect_btn.pack(side="right", padx=2)
            
            # Kill button
            kill_btn = tk.Button(button_frame,
                                text="Kill",
                                command=lambda p=pid, n=name: self.kill_specific_process(p, n, selection_window),
                                bg="#f44336", fg="white",
                                font=('Arial', 9, 'bold'),
                                padx=15)
            kill_btn.pack(side="right", padx=2)
        
        # Bottom buttons
        bottom_frame = tk.Frame(selection_window, bg="#2b2b2b")
        bottom_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        cancel_btn = tk.Button(bottom_frame,
                              text="Cancel",
                              command=selection_window.destroy,
                              bg="#666666", fg="white",
                              font=('Arial', 10),
                              padx=20)
        cancel_btn.pack(side="right", padx=5)
        
        kill_all_btn = tk.Button(bottom_frame,
                                text="🚨 Kill All Bot Processes",
                                command=lambda: self.kill_all_and_close(selection_window),
                                bg="#d32f2f", fg="white",
                                font=('Arial', 10, 'bold'),
                                padx=20)
        kill_all_btn.pack(side="left", padx=5)
    
    def select_process(self, pid, window):
        """Connect to selected process and close dialog"""
        window.destroy()
        self.connect_to_bot_process(pid)
    
    def kill_specific_process(self, pid, name, window):
        """Kill a specific process and refresh the dialog"""
        try:
            import psutil
            process = psutil.Process(pid)
            process.kill()
            self.add_bot_gui_message(f"Killed process PID {pid} ({name})")
            
            # Refresh the dialog by closing it and re-running find
            window.destroy()
            # Small delay then re-run the search
            self.root.after(500, self.find_running_bot)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to kill process {pid}: {e}")
    
    def kill_all_and_close(self, window):
        """Kill all bot processes and close dialog"""
        window.destroy()
        self.emergency_stop_bot()
    
    def connect_to_bot_process(self, pid):
        """Connect to a specific bot process by PID"""
        try:
            import psutil
            bot_process = psutil.Process(pid)
            self.bot_process = bot_process
            self.bot_running = True
            self.update_ui_state()
            
            self.bot_log_display.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] 🔗 Manually connected to bot process (PID: {pid})\n")
            self.bot_log_display.see(tk.END)
            
            # Start monitoring the process
            threading.Thread(target=self.monitor_existing_bot, args=(bot_process,), daemon=True).start()
            
            messagebox.showinfo("Connected", f"Successfully connected to bot process (PID: {pid})")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect to process {pid}: {e}")
        
    def start_server(self):
        """Start the Minecraft server"""
        if not self.server_running:
            # Check for existing server process
            existing_pid = self.check_existing_server_process()
            if existing_pid:
                result = messagebox.askyesno(
                    "Server Already Running", 
                    f"A Minecraft server appears to be already running (PID: {existing_pid}).\n\n"
                    "This may cause the 'file locked' error you're seeing.\n\n"
                    "Would you like to try starting anyway?\n"
                    "(You may need to stop the existing server first)"
                )
                if not result:
                    return
            
            try:
                os.chdir(self.server_dir)
                
                self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Attempting to start server...\n")
                if self.console_auto_scroll_var.get():
                    self.console_output.see(tk.END)
                
                # Start server process without console window
                self.server_process = subprocess.Popen(
                    ["java", "@user_jvm_args.txt", 
                     "@libraries/net/neoforged/neoforge/21.1.209/win_args.txt", 
                     "nogui"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    cwd=self.server_dir,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
                
                self.server_running = True
                # Reset analytics data for new server session
                self.server_start_time = datetime.now()
                self.performance_data['cpu'].clear()
                self.performance_data['memory'].clear()
                self.performance_data['timestamps'].clear()
                self.performance_data['tps'].clear()
                self.update_ui_state()
                
                # Start reading server output
                threading.Thread(target=self.read_server_output, daemon=True).start()
                
                self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Server starting...\n")
                if self.console_auto_scroll_var.get():
                    self.console_output.see(tk.END)
                
            except Exception as e:
                self.server_running = False
                self.update_ui_state()
                
                error_msg = str(e)
                if "file" in error_msg.lower() and "lock" in error_msg.lower():
                    error_details = (
                        f"Server startup failed - File lock error:\n\n"
                        f"{error_msg}\n\n"
                        f"This usually means:\n"
                        f"• Another Minecraft server is already running\n"
                        f"• Previous server didn't shut down properly\n"
                        f"• World files are locked by another process\n\n"
                        f"Try:\n"
                        f"1. Check Task Manager for existing Java processes\n"
                        f"2. Restart your computer if needed\n"
                        f"3. Make sure no other server launchers are running"
                    )
                else:
                    error_details = f"Failed to start server: {error_msg}"
                    
                messagebox.showerror("Server Start Error", error_details)
                
                self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Server failed to start: {error_msg}\n")
                if self.console_auto_scroll_var.get():
                    self.console_output.see(tk.END)
                
    def stop_server(self):
        """Stop the Minecraft server"""
        if self.server_running and self.server_process:
            try:
                # Check if it's a psutil process or subprocess
                is_psutil_process = hasattr(self.server_process, 'is_running')
                
                # Try to send stop command first (graceful shutdown)
                try:
                    if hasattr(self.server_process, 'stdin') and self.server_process.stdin:
                        self.send_server_command("stop")
                        self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Sending stop command...\n")
                        if self.console_auto_scroll_var.get():
                            self.console_output.see(tk.END)
                        time.sleep(3)  # Wait a bit longer for graceful shutdown
                except Exception:
                    # If we can't send command, proceed with termination
                    pass
                
                if is_psutil_process:
                    # Handle psutil process (external server we connected to)
                    try:
                        if self.server_process.is_running():
                            self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Terminating external server process...\n")
                            if self.console_auto_scroll_var.get():
                                self.console_output.see(tk.END)
                                
                            self.server_process.terminate()
                            time.sleep(3)
                            
                            if self.server_process.is_running():
                                self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Force killing server...\n")
                                if self.console_auto_scroll_var.get():
                                    self.console_output.see(tk.END)
                                self.server_process.kill()
                                time.sleep(1)
                                
                            if not self.server_process.is_running():
                                self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] External server stopped.\n")
                            else:
                                self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Warning: Server process may still be running.\n")
                        else:
                            self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] External server process already ended.\n")
                    except Exception as e:
                        self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Error stopping external server: {e}\n")
                        
                else:
                    # Handle subprocess process (server we started)
                    # Check if process is still running
                    if self.server_process.poll() is None:
                        self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Force stopping server...\n")
                        if self.console_auto_scroll_var.get():
                            self.console_output.see(tk.END)
                        self.server_process.terminate()
                        time.sleep(2)
                        
                        # If still running, force kill
                        if self.server_process.poll() is None:
                            self.server_process.kill()
                            self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Server force killed.\n")
                        else:
                            self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Server terminated.\n")
                    else:
                        self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Server stopped gracefully.\n")
                
                self.server_running = False
                self.server_process = None
                self.update_ui_state()
                
                if self.console_auto_scroll_var.get():
                    self.console_output.see(tk.END)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to stop server: {e}")
                
    def restart_server(self):
        """Restart the Minecraft server"""
        self.stop_server()
        time.sleep(3)
        self.start_server()
        
    def check_server_status(self):
        """Check if Minecraft server is running and accessible"""
        self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 Checking server status...\n")
        if self.console_auto_scroll_var.get():
            self.console_output.see(tk.END)
            
        # Run the check in a separate thread to avoid blocking the GUI
        threading.Thread(target=self._perform_server_check, daemon=True).start()
        
    def _perform_server_check(self):
        """Perform server status check in background thread"""
        results = []
        
        # Check 1: Process detection
        try:
            import psutil
            java_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cwd']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    name = proc.info.get('name', '')
                    cwd = proc.info.get('cwd', '')
                    
                    if not cmdline:
                        continue
                        
                    # Check if it's a Java process
                    if 'java' in name.lower():
                        cmdline_str = ' '.join(cmdline).lower()
                        # Look for server indicators
                        if any(indicator in cmdline_str for indicator in ['server', 'minecraft', 'forge', 'neoforge', 'fabric']):
                            java_processes.append((proc.info['pid'], name, cwd))
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if java_processes:
                for pid, name, cwd in java_processes:
                    results.append(f"✅ Found Java server process: PID {pid} ({name})")
                    if cwd and self.server_dir.lower() in cwd.lower():
                        results.append(f"   └── Running from correct directory: {cwd}")
                    elif cwd:
                        results.append(f"   └── Running from: {cwd}")
            else:
                results.append("❌ No Java server processes found")
                
        except ImportError:
            results.append("⚠️ psutil not available for process detection")
        except Exception as e:
            results.append(f"❌ Error checking processes: {e}")
            
        # Check 2: Port availability (25565)
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(3)
                result = sock.connect_ex(('localhost', 25565))
                if result == 0:
                    results.append("✅ Port 25565 is accessible locally")
                else:
                    results.append("❌ Port 25565 is not accessible (server may be offline)")
        except Exception as e:
            results.append(f"❌ Error checking port 25565: {e}")
            
        # Check 3: Server status query (if mcstatus is available)
        try:
            from mcstatus import JavaServer
            server = JavaServer.lookup("localhost:25565")
            status = server.status()
            results.append(f"✅ Server responding to queries")
            results.append(f"   └── Players online: {status.players.online}/{status.players.max}")
            results.append(f"   └── Version: {status.version.name}")
            if hasattr(status, 'description') and status.description:
                results.append(f"   └── MOTD: {status.description}")
        except ImportError:
            results.append("⚠️ mcstatus not available for server query")
        except Exception as e:
            results.append(f"❌ Server query failed: {e}")
            
        # Check 4: Log file activity
        if os.path.exists(self.log_file):
            try:
                stat = os.stat(self.log_file)
                mod_time = datetime.fromtimestamp(stat.st_mtime)
                time_diff = datetime.now() - mod_time
                
                if time_diff.seconds < 300:  # Less than 5 minutes
                    results.append(f"✅ Log file recently active (last update: {mod_time.strftime('%H:%M:%S')})")
                else:
                    results.append(f"⚠️ Log file not recently updated (last update: {mod_time.strftime('%H:%M:%S')})")
            except Exception as e:
                results.append(f"❌ Error checking log file: {e}")
        else:
            results.append(f"❌ Log file not found: {self.log_file}")
            
        # Display results in main thread
        self.root.after(0, lambda: self._display_server_check_results(results))
        
    def _display_server_check_results(self, results):
        """Display server check results in the console"""
        self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] 📊 Server Status Check Results:\n")
        
        for result in results:
            self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {result}\n")
            
        # Summary
        success_count = len([r for r in results if r.startswith("✅")])
        warning_count = len([r for r in results if r.startswith("⚠️")])
        error_count = len([r for r in results if r.startswith("❌")])
        
        if error_count == 0 and warning_count <= 1:
            summary = "🟢 Server appears to be running normally"
        elif success_count > error_count:
            summary = "🟡 Server running but with some issues"
        else:
            summary = "🔴 Server appears to be offline or having problems"
            
        self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {summary}\n")
        self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] ─────────────────────────────────────────\n")
        
        if self.console_auto_scroll_var.get():
            self.console_output.see(tk.END)
            
    def smart_server_check(self):
        """Smart server check - runs diagnostics and connects if server is found running"""
        self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 Smart server check starting...\n")
        if self.console_auto_scroll_var.get():
            self.console_output.see(tk.END)
            
        # Run the check in a separate thread
        threading.Thread(target=self._perform_smart_server_check, daemon=True).start()
        
    def _perform_smart_server_check(self):
        """Perform smart server check in background thread"""
        results = []
        found_server_processes = []
        server_responsive = False
        
        # Check 1: Process detection with connection capability
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cwd']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    name = proc.info.get('name', '')
                    cwd = proc.info.get('cwd', '')
                    
                    if not cmdline:
                        continue
                        
                    # Check if it's a Java process
                    if 'java' in name.lower():
                        cmdline_str = ' '.join(cmdline).lower()
                        # Look for server indicators
                        if any(indicator in cmdline_str for indicator in ['server', 'minecraft', 'forge', 'neoforge', 'fabric']):
                            is_our_server = cwd and self.server_dir.lower() in cwd.lower()
                            found_server_processes.append((proc.info['pid'], name, cwd, is_our_server))
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if found_server_processes:
                for pid, name, cwd, is_our_server in found_server_processes:
                    marker = " (OUR DIRECTORY)" if is_our_server else ""
                    results.append(f"✅ Found Java server process: PID {pid} ({name}){marker}")
                    if cwd:
                        results.append(f"   └── Running from: {cwd}")
            else:
                results.append("❌ No Java server processes found")
                
        except ImportError:
            results.append("⚠️ psutil not available for process detection")
        except Exception as e:
            results.append(f"❌ Error checking processes: {e}")
            
        # Check 2: Port availability (25565)
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(3)
                result = sock.connect_ex(('localhost', 25565))
                if result == 0:
                    results.append("✅ Port 25565 is accessible locally")
                else:
                    results.append("❌ Port 25565 is not accessible (server may be offline)")
        except Exception as e:
            results.append(f"❌ Error checking port 25565: {e}")
            
        # Check 3: Server status query
        try:
            from mcstatus import JavaServer
            server = JavaServer.lookup("localhost:25565")
            status = server.status()
            server_responsive = True
            results.append(f"✅ Server responding to queries")
            results.append(f"   └── Players online: {status.players.online}/{status.players.max}")
            results.append(f"   └── Version: {status.version.name}")
            if hasattr(status, 'description') and status.description:
                results.append(f"   └── MOTD: {status.description}")
        except ImportError:
            results.append("⚠️ mcstatus not available for server query")
        except Exception as e:
            results.append(f"❌ Server query failed: {e}")
            
        # Check 4: Log file activity
        if os.path.exists(self.log_file):
            try:
                stat = os.stat(self.log_file)
                mod_time = datetime.fromtimestamp(stat.st_mtime)
                time_diff = datetime.now() - mod_time
                
                if time_diff.seconds < 300:  # Less than 5 minutes
                    results.append(f"✅ Log file recently active (last update: {mod_time.strftime('%H:%M:%S')})")
                else:
                    results.append(f"⚠️ Log file not recently updated (last update: {mod_time.strftime('%H:%M:%S')})")
            except Exception as e:
                results.append(f"❌ Error checking log file: {e}")
        else:
            results.append(f"❌ Log file not found: {self.log_file}")
            
        # Determine if we should attempt connection
        can_connect = len(found_server_processes) > 0 and server_responsive
        
        # Display results and attempt connection if possible
        self.root.after(0, lambda: self._display_smart_check_results(results, found_server_processes, can_connect))
        
    def _display_smart_check_results(self, results, found_processes, can_connect):
        """Display smart check results and attempt connection if server is running"""
        self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] 📊 Smart Server Check Results:\n")
        
        for result in results:
            self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {result}\n")
            
        # Summary and connection attempt
        success_count = len([r for r in results if r.startswith("✅")])
        warning_count = len([r for r in results if r.startswith("⚠️")])
        error_count = len([r for r in results if r.startswith("❌")])
        
        if can_connect and not self.server_running:
            # Attempt to connect to the server
            try:
                import psutil
                # Prefer server from our directory, or pick the first one
                our_servers = [s for s in found_processes if s[3]]  # s[3] is is_our_server
                if our_servers:
                    selected_server = our_servers[0]
                else:
                    selected_server = found_processes[0]
                    
                pid, name, cwd, is_our_server = selected_server
                server_process = psutil.Process(pid)
                self.server_process = server_process
                self.server_running = True
                self.update_ui_state()
                
                self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] 🔗 Auto-connected to server process (PID: {pid})\n")
                
                if len(found_processes) > 1:
                    self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}]    └── Note: Found {len(found_processes)} server processes, connected to PID {pid}\n")
                    
                # Start monitoring
                threading.Thread(target=self.monitor_existing_server, args=(server_process,), daemon=True).start()
                
                summary = "🟢 Server running and connected successfully!"
                messagebox.showinfo("Connected", f"Server is running and GUI is now connected!\nProcess PID: {pid}")
                
            except Exception as e:
                summary = "🟡 Server running but connection failed"
                self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Failed to connect: {e}\n")
                
        elif self.server_running:
            summary = "🟢 Server already connected and running normally"
        elif error_count == 0 and warning_count <= 1:
            summary = "🟢 Server appears to be running normally (but GUI not connected)"
        elif success_count > error_count:
            summary = "🟡 Server running but with some issues"
        else:
            summary = "🔴 Server appears to be offline or having problems"
            
        self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {summary}\n")
        self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] ─────────────────────────────────────────\n")
        
        if self.console_auto_scroll_var.get():
            self.console_output.see(tk.END)
            
    def connect_to_existing_server(self):
        """Find and connect to existing server processes"""
        self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] 🔗 Searching for existing server processes...\n")
        if self.console_auto_scroll_var.get():
            self.console_output.see(tk.END)
            
        try:
            import psutil
            found_servers = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cwd']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    name = proc.info.get('name', '')
                    cwd = proc.info.get('cwd', '')
                    
                    if not cmdline:
                        continue
                        
                    # Check if it's a Java process running a server
                    if 'java' in name.lower():
                        cmdline_str = ' '.join(cmdline).lower()
                        # Look for server indicators
                        if any(indicator in cmdline_str for indicator in ['server', 'minecraft', 'forge', 'neoforge', 'fabric']):
                            # Prefer servers running from our server directory
                            is_our_server = cwd and self.server_dir.lower() in cwd.lower()
                            found_servers.append((proc.info['pid'], name, cwd, is_our_server))
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if not found_servers:
                self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] ❌ No server processes found\n")
                if self.console_auto_scroll_var.get():
                    self.console_output.see(tk.END)
                messagebox.showinfo("No Server Found", "No Minecraft server processes found running.")
                return
                
            # If multiple servers found, prefer one from our directory or pick the first
            our_servers = [s for s in found_servers if s[3]]  # s[3] is is_our_server
            if our_servers:
                selected_server = our_servers[0]
            else:
                selected_server = found_servers[0]
                
            pid, name, cwd, is_our_server = selected_server
            
            # Connect to the selected server
            try:
                server_process = psutil.Process(pid)
                self.server_process = server_process
                self.server_running = True
                self.update_ui_state()
                
                self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Connected to server process (PID: {pid})\n")
                if cwd:
                    self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}]    └── Running from: {cwd}\n")
                    
                # Show summary of all found servers
                if len(found_servers) > 1:
                    self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 Found {len(found_servers)} server processes total:\n")
                    for p_pid, p_name, p_cwd, p_is_ours in found_servers:
                        status = " (CONNECTED)" if p_pid == pid else ""
                        our_marker = " (OUR DIR)" if p_is_ours else ""
                        self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}]    • PID {p_pid}{status}{our_marker}\n")
                        
                if self.console_auto_scroll_var.get():
                    self.console_output.see(tk.END)
                
                # Start monitoring the existing process
                threading.Thread(target=self.monitor_existing_server, args=(server_process,), daemon=True).start()
                
                messagebox.showinfo("Connected", f"Successfully connected to server process (PID: {pid})\n\nFound {len(found_servers)} server process(es) total.")
                
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Cannot access server process {pid}: {e}\n")
                if self.console_auto_scroll_var.get():
                    self.console_output.see(tk.END)
                messagebox.showerror("Connection Error", f"Cannot connect to server process {pid}: {e}")
                
        except ImportError:
            messagebox.showerror("Error", "psutil library not available for process detection.")
        except Exception as e:
            self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error searching for servers: {e}\n")
            if self.console_auto_scroll_var.get():
                self.console_output.see(tk.END)
            messagebox.showerror("Error", f"Failed to search for server processes: {e}")
        
    def send_command(self, event=None):
        """Send command to server"""
        command = self.command_entry.get().strip()
        if command and self.server_running:
            self.send_server_command(command)
            self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] > {command}\n")
            if self.console_auto_scroll_var.get():
                self.console_output.see(tk.END)
            self.command_entry.delete(0, tk.END)
            
    def send_server_command(self, command):
        """Send command to server process"""
        # Check if we have a subprocess.Popen object (started by us) vs psutil.Process (existing)
        if hasattr(self.server_process, 'stdin') and self.server_process.stdin:
            # This is our own subprocess with stdin access
            try:
                self.server_process.stdin.write(command + "\n")
                self.server_process.stdin.flush()
                self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Command sent to server: {command}\n")
            except Exception as e:
                self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error sending command: {e}\n")
        else:
            # This is an existing process we connected to - can't send commands
            self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Cannot send commands to external server process\n")
            self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}]    └── Command '{command}' would need to be sent via server console\n")
            self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}]    └── Tip: Start server through this GUI to enable command input\n")
            
        if self.console_auto_scroll_var.get():
            self.console_output.see(tk.END)
                
    def read_server_output(self):
        """Read server output in separate thread"""
        if self.server_process and hasattr(self.server_process, 'stdout') and self.server_process.stdout:
            # Only works for subprocess.Popen objects we started
            try:
                for line in iter(self.server_process.stdout.readline, ''):
                    if line:
                        self.log_queue.put(('server', line.strip()))
            except Exception as e:
                self.log_queue.put(('server', f"Error reading server output: {e}"))
                    
    def start_log_monitoring(self):
        """Start monitoring the log file"""
        threading.Thread(target=self.monitor_log_file, daemon=True).start()
        self.process_log_queue()
        
    def monitor_log_file(self):
        """Monitor log file for changes"""
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r', encoding='utf-8') as f:
                # Go to end of file
                f.seek(0, 2)
                
                while True:
                    line = f.readline()
                    if line:
                        self.log_queue.put(('log', line.strip()))
                    else:
                        time.sleep(0.5)
                        
    def process_log_queue(self):
        """Process log messages from queue"""
        try:
            # Process server logs
            while True:
                source, message = self.log_queue.get_nowait()
                
                # Add timestamp if not present
                timestamp = datetime.now().strftime('%H:%M:%S')
                
                if source == 'server':
                    formatted_message = f"[{timestamp}] {message}\n"
                    self.console_output.insert(tk.END, formatted_message)
                    if self.console_auto_scroll_var.get():
                        self.console_output.see(tk.END)
                        
                # Add to log display
                self.log_display.insert(tk.END, f"[{timestamp}] {message}\n")
                if self.auto_scroll_var.get():
                    self.log_display.see(tk.END)
                
                # Update player list if join/leave detected
                self.update_players_from_message(message)
                
        except queue.Empty:
            pass
            
        try:
            # Process bot logs
            while True:
                message = self.bot_log_queue.get_nowait()
                
                # Add timestamp if not present
                timestamp = datetime.now().strftime('%H:%M:%S')
                formatted_message = f"[{timestamp}] {message}\n"
                
                # Add to bot log display
                self.bot_log_display.insert(tk.END, formatted_message)
                if self.bot_auto_scroll_var.get():
                    self.bot_log_display.see(tk.END)
                
                # Color code different types of bot messages
                self.colorize_bot_logs(message, len(self.bot_log_display.get(1.0, tk.END).splitlines()) - 1)
                
        except queue.Empty:
            pass
            
        # Schedule next check
        self.root.after(100, self.process_log_queue)
        
    def colorize_bot_logs(self, message, line_num):
        """Add color coding to bot logs based on content"""
        try:
            line_start = f"{line_num}.0"
            line_end = f"{line_num}.end"
            
            # Configure tags for different message types
            self.bot_log_display.tag_config("error", foreground="#ff4444")
            self.bot_log_display.tag_config("warning", foreground="#ffaa44")
            self.bot_log_display.tag_config("info", foreground="#44ff44")
            self.bot_log_display.tag_config("debug", foreground="#4444ff")
            self.bot_log_display.tag_config("success", foreground="#44ffaa")
            
            # Apply colors based on message content
            if any(word in message.lower() for word in ["error", "erro", "exception", "failed", "falha"]):
                self.bot_log_display.tag_add("error", line_start, line_end)
            elif any(word in message.lower() for word in ["warning", "warn", "aviso"]):
                self.bot_log_display.tag_add("warning", line_start, line_end)
            elif any(word in message.lower() for word in ["connected", "ready", "online"]):
                self.bot_log_display.tag_add("success", line_start, line_end)
            elif any(word in message.lower() for word in ["debug", "info"]):
                self.bot_log_display.tag_add("info", line_start, line_end)
                
        except Exception as e:
            print(f"Error colorizing logs: {e}")
        
    def update_players_from_message(self, message):
        """Update player list from log messages"""
        # Simple regex patterns for player join/leave
        join_pattern = r'(\w+) joined the game'
        leave_pattern = r'(\w+) left the game'
        
        join_match = re.search(join_pattern, message)
        leave_match = re.search(leave_pattern, message)
        
        if join_match:
            player = join_match.group(1)
            if player not in self.players_listbox.get(0, tk.END):
                self.players_listbox.insert(tk.END, player)
                # Track player join for analytics
                self.track_player_join(player)
                
        elif leave_match:
            player = leave_match.group(1)
            items = list(self.players_listbox.get(0, tk.END))
            if player in items:
                index = items.index(player)
                self.players_listbox.delete(index)
                # Track player leave for analytics
                self.track_player_leave(player)
    def start_bot(self):
        """Start the Discord bot"""
        if not self.bot_running:
            try:
                # Start bot process and capture console output
                self.bot_process = subprocess.Popen(
                    ["python.exe", "-u", "bot.py"],  # -u for unbuffered output
                    cwd=self.bot_dir,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                self.bot_running = True
                self.update_ui_state()
                
                # Start reading bot output
                threading.Thread(target=self.read_bot_output, daemon=True).start()
                
                self.add_bot_gui_message("Discord bot starting...")
                
                # Update bot info
                self.update_bot_info()
                
            except FileNotFoundError:
                # Fallback to regular python if pythonw is not available
                try:
                    self.bot_process = subprocess.Popen(
                        ["python.exe", "-u", "bot.py"],  # -u for unbuffered output
                        cwd=self.bot_dir,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                        universal_newlines=True
                    )
                    
                    self.bot_running = True
                    self.update_ui_state()
                    
                    # Start reading bot output
                    threading.Thread(target=self.read_bot_output, daemon=True).start()
                    
                    self.bot_log_display.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Discord bot starting...\n")
                    self.bot_log_display.see(tk.END)
                    
                    # Update bot info
                    self.update_bot_info()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to start Discord bot: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start Discord bot: {e}")
                
    def stop_bot(self):
        """Stop the Discord bot"""
        if self.bot_running and self.bot_process:
            try:
                self.bot_log_display.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Stopping Discord bot...\n")
                self.bot_log_display.see(tk.END)
                
                # Check if it's a psutil process or subprocess
                is_psutil_process = hasattr(self.bot_process, 'is_running')
                
                if is_psutil_process:
                    # Handle psutil process (connected to existing process)
                    try:
                        if self.bot_process.is_running():
                            self.bot_process.terminate()
                            time.sleep(3)
                            
                            if self.bot_process.is_running():
                                self.bot_log_display.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Force stopping bot...\n")
                                self.bot_log_display.see(tk.END)
                                self.bot_process.kill()
                                time.sleep(1)
                                
                                if self.bot_process.is_running():
                                    self.bot_log_display.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Bot process still running, using emergency kill...\n")
                                    self.bot_log_display.see(tk.END)
                                    # Emergency fallback - kill all bot processes
                                    killed_count = self.kill_all_bot_processes()
                                    if killed_count > 0:
                                        self.bot_log_display.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Emergency killed {killed_count} bot process(es)\n")
                                    else:
                                        self.bot_log_display.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Bot process may still be running\n")
                                else:
                                    self.bot_log_display.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Bot force stopped.\n")
                            else:
                                self.bot_log_display.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Bot stopped gracefully.\n")
                        else:
                            self.bot_log_display.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Bot process already ended.\n")
                    except Exception:
                        # Process might have already ended
                        self.bot_log_display.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Bot process ended.\n")
                        
                else:
                    # Handle subprocess.Popen process (started by GUI)
                    self.bot_process.terminate()
                    time.sleep(3)
                    
                    if self.bot_process.poll() is None:
                        self.bot_log_display.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Force stopping bot...\n")
                        self.bot_log_display.see(tk.END)
                        self.bot_process.kill()
                        time.sleep(1)
                        
                        if self.bot_process.poll() is None:
                            self.bot_log_display.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Bot process still running, using emergency kill...\n")
                            self.bot_log_display.see(tk.END)
                            # Emergency fallback - kill all bot processes
                            killed_count = self.kill_all_bot_processes()
                            if killed_count > 0:
                                self.bot_log_display.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Emergency killed {killed_count} bot process(es)\n")
                            else:
                                self.bot_log_display.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Bot process may still be running\n")
                        else:
                            self.bot_log_display.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Bot force stopped.\n")
                    else:
                        self.bot_log_display.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Bot stopped gracefully.\n")
                    
                self.bot_running = False
                self.bot_process = None
                self.update_ui_state()
                self.bot_log_display.see(tk.END)
                
            except Exception as e:
                self.bot_running = False  # Reset state even if stop failed
                self.bot_process = None
                self.update_ui_state()
                error_msg = f"Failed to stop Discord bot: {e}"
                self.bot_log_display.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] ❌ {error_msg}\n")
                self.bot_log_display.see(tk.END)
                messagebox.showerror("Error", error_msg)
        elif self.bot_running:
            # Handle case where bot is marked as running but no process reference
            self.bot_log_display.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Bot marked as running but no process found. Resetting state.\n")
            self.bot_log_display.see(tk.END)
            self.bot_running = False
            self.update_ui_state()
        else:
            # Bot not running
            self.bot_log_display.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Bot is not currently running.\n")
            self.bot_log_display.see(tk.END)
                
    def emergency_stop_bot(self):
        """Emergency stop - kills all Discord bot processes"""
        self.add_bot_gui_message("🚨 Emergency Stop - Killing all Discord bot processes...")
        
        killed_count = self.kill_all_bot_processes()
        
        if killed_count > 0:
            self.add_bot_gui_message(f"🚨 Emergency killed {killed_count} bot process(es)")
            messagebox.showinfo("Emergency Stop", f"Successfully killed {killed_count} Discord bot process(es)")
        else:
            self.add_bot_gui_message("No Discord bot processes found to kill")
            messagebox.showinfo("Emergency Stop", "No Discord bot processes found to kill")
        
        # Reset our state regardless
        self.bot_running = False
        self.bot_process = None
        self.update_ui_state()
                
    def restart_bot(self):
        """Restart the Discord bot"""
        self.stop_bot()
        time.sleep(2)
        self.start_bot()
        
    def read_bot_output(self):
        """Read bot console output in separate thread and display directly"""
        if self.bot_process and hasattr(self.bot_process, 'stdout') and self.bot_process.stdout:
            try:
                # Add debug message to see if this method is being called
                self.root.after(0, lambda: self.add_bot_console_output("📡 Bot output reader started"))
                
                for line in iter(self.bot_process.stdout.readline, ''):
                    if line:
                        # Display the raw console output directly
                        stripped_line = line.rstrip()
                        if stripped_line:  # Only add non-empty lines
                            # Add line directly to display with newline
                            self.root.after(0, lambda text=stripped_line: self.add_bot_console_output(text))
                    else:
                        # If readline returns empty string, process might have ended
                        break
                        
                self.root.after(0, lambda: self.add_bot_console_output("📡 Bot output reader ended"))
                
            except Exception as e:
                self.root.after(0, lambda err=str(e): self.add_bot_console_output(f"❌ Error reading bot output: {err}"))
        else:
            self.root.after(0, lambda: self.add_bot_console_output("⚠️ No bot stdout available for reading"))
                
    def add_bot_console_output(self, text):
        """Add bot console output to display (called from main thread)"""
        self.bot_log_display.insert(tk.END, text + "\n")
        if self.bot_auto_scroll_var.get():
            self.bot_log_display.see(tk.END)
        
        # Color code the console output
        line_count = len(self.bot_log_display.get(1.0, tk.END).splitlines()) - 1
        self.colorize_bot_logs(text, line_count)
        
    def add_bot_gui_message(self, message):
        """Add a GUI message to the bot console with timestamp"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_message = f"[GUI - {timestamp}] {message}"
        self.add_bot_console_output(formatted_message)
        
    def send_bot_input(self, event=None):
        """Send input to the bot console"""
        if not self.bot_running or not self.bot_process:
            self.add_bot_gui_message("⚠️ Bot is not running - cannot send input")
            return
            
        input_text = self.bot_input_entry.get().strip()
        
        # Check if it's placeholder text
        if not input_text or input_text == self.bot_input_placeholder:
            return
            
        try:
            # Check if it's a subprocess (has stdin) or psutil process
            if hasattr(self.bot_process, 'stdin') and self.bot_process.stdin:
                # Send input to bot process
                self.bot_process.stdin.write(input_text + '\n')
                self.bot_process.stdin.flush()
                
                # Display the input in console with a different format
                self.add_bot_console_output(f">>> {input_text}")
                
                # Clear the input field
                self.bot_input_entry.delete(0, tk.END)
                
            else:
                self.add_bot_gui_message("⚠️ Cannot send input to external bot process")
                
        except Exception as e:
            self.add_bot_gui_message(f"❌ Error sending input: {e}")
            
    def setup_bot_input_placeholder(self):
        """Setup placeholder text for bot input field"""
        def on_focus_in(event):
            if self.bot_input_entry.get() == self.bot_input_placeholder:
                self.bot_input_entry.delete(0, tk.END)
                self.bot_input_entry.config(fg="white")
                
        def on_focus_out(event):
            if not self.bot_input_entry.get():
                self.bot_input_entry.insert(0, self.bot_input_placeholder)
                self.bot_input_entry.config(fg="gray")
                
        # Set initial placeholder
        self.bot_input_entry.config(state="normal")
        self.bot_input_entry.insert(0, self.bot_input_placeholder)
        self.bot_input_entry.config(fg="gray", state="disabled")
        
        # Bind events
        self.bot_input_entry.bind('<FocusIn>', on_focus_in)
        self.bot_input_entry.bind('<FocusOut>', on_focus_out)
                    
                    
    def update_bot_info(self):
        """Update bot information display"""
        try:
            # Try to read .env file for bot info
            env_path = os.path.join(self.bot_dir, '.env')
            bot_info = "Discord Bot Information:\n"
            
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        if line.startswith('CHANNEL_ID'):
                            bot_info += f"Channel ID: {line.split('=')[1].strip()}\n"
                        elif line.startswith('SERVER_IP'):
                            bot_info += f"Monitoring Server: {line.split('=')[1].strip()}\n"
                        elif line.startswith('SERVER_PORT'):
                            bot_info += f"Server Port: {line.split('=')[1].strip()}\n"
            
            bot_info += f"Bot Status: {'Running' if self.bot_running else 'Stopped'}\n"
            bot_info += f"Process ID: {self.bot_process.pid if self.bot_process else 'N/A'}"
            
            self.bot_info_text.delete(1.0, tk.END)
            self.bot_info_text.insert(1.0, bot_info)
            
        except Exception as e:
            print(f"Error updating bot info: {e}")
            
    def clear_bot_logs(self):
        """Clear the bot log display"""
        self.bot_log_display.delete(1.0, tk.END)
        
    def force_server_check(self):
        """Force an immediate server status check in the bot"""
        if not self.bot_running:
            self.add_bot_gui_message("❌ Bot is not running - cannot force server check")
            messagebox.showwarning("Bot Not Running", "The Discord bot must be running to force a server check.")
            return
            
        self.add_bot_gui_message("🔍 Forcing immediate server status check...")
        
        try:
            # Create trigger file for the bot to detect
            trigger_file = os.path.join(self.bot_dir, "force_server_check.trigger")
            with open(trigger_file, 'w') as f:
                f.write(f"Force check requested at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
            self.add_bot_gui_message("🔄 Server check triggered - bot will check status within 10 seconds")
            self.add_bot_gui_message("👀 Watch the bot console for immediate results")
            messagebox.showinfo("Force Check Triggered", 
                              "Server status check has been triggered!\n\n" +
                              "The bot will check server connectivity within 10 seconds.\n" +
                              "Watch the bot console output for detailed results.")
                              
        except Exception as e:
            self.add_bot_gui_message(f"❌ Failed to trigger server check: {e}")
            messagebox.showerror("Error", f"Failed to create trigger file: {e}")
        
    def check_existing_processes(self):
        """Check if bot or server processes are already running"""
        # Check for existing Minecraft server
        server_pid = self.check_existing_server_process()
        if server_pid:
            try:
                import psutil
                existing_process = psutil.Process(server_pid)
                
                # Show notification about existing server but don't auto-connect
                self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] � Found existing server process (PID: {server_pid})\n")
                self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] 💡 Use server controls to manage it if needed\n")
                if hasattr(self, 'console_auto_scroll_var') and self.console_auto_scroll_var.get():
                    self.console_output.see(tk.END)
                    
            except (ImportError, Exception) as e:
                # If we can't access the process, just note it
                self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 Detected existing server (PID: {server_pid}) but cannot access it\n")
                if hasattr(self, 'console_auto_scroll_var') and self.console_auto_scroll_var.get():
                    self.console_output.see(tk.END)
        
        # Check for existing Discord bot (improved detection)
        bot_pid = self.detect_existing_bot()
        if bot_pid:
            try:
                import psutil
                existing_bot_process = psutil.Process(bot_pid)
                
                # Show notification about existing bot but don't auto-connect
                self.bot_log_display.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] � Found existing bot process (PID: {bot_pid})\n")
                self.bot_log_display.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] 💡 Use '🧹 Kill Running Bots' button to clean up existing processes\n")
                self.bot_log_display.see(tk.END)
                
            except (ImportError, Exception) as e:
                # If we can't access the process, just note it
                self.bot_log_display.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 Detected existing bot (PID: {bot_pid}) but cannot access it\n")
                self.bot_log_display.see(tk.END)
            
        # Update UI to reflect current state
        self.update_ui_state()
    
    def monitor_existing_server(self, process):
        """Monitor an existing server process we connected to"""
        try:
            import psutil
            # Wait for the process to end
            process.wait()
            # When it ends, update our state
            self.server_running = False
            self.server_process = None
            self.root.after(0, self.update_ui_state)  # Update UI in main thread
            self.root.after(0, lambda: self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Existing server process ended\n"))
        except Exception:
            pass
        
    def update_ui_state(self):
        """Update UI based on server and bot state"""
        # Server UI
        if self.server_running:
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.restart_btn.config(state="normal")
            self.check_server_btn.config(state="disabled")
            self.server_status_label.config(text="● ONLINE", fg="#4CAF50")
            
            # Enable command input only if we have stdin access (our own process)
            if hasattr(self.server_process, 'stdin') and self.server_process.stdin:
                self.command_entry.config(state="normal")
                self.command_entry.config(bg="#3b3b3b", fg="white")
                self.send_btn.config(state="normal")
            else:
                self.command_entry.config(state="disabled")
                self.command_entry.config(bg="#2b2b2b", fg="#666666")
                self.send_btn.config(state="disabled")
        else:
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            self.restart_btn.config(state="disabled")
            self.check_server_btn.config(state="normal")
            self.server_status_label.config(text="● OFFLINE", fg="#ff4444")
            
            # Disable command input when server is offline
            self.command_entry.config(state="disabled")
            self.command_entry.config(bg="#2b2b2b", fg="#666666")
            self.send_btn.config(state="disabled")
            
        # Bot UI
        if self.bot_running:
            self.start_bot_btn.config(state="disabled")
            self.stop_bot_btn.config(state="normal")
            self.restart_bot_btn.config(state="normal")
            self.force_check_btn.config(state="normal")
            self.bot_status_label.config(text="● ONLINE", fg="#4CAF50")
            # Enable bot input when bot is running and has stdin
            has_stdin = (hasattr(self.bot_process, 'stdin') and 
                        self.bot_process and self.bot_process.stdin)
            if hasattr(self, 'bot_input_entry'):
                if has_stdin:
                    self.bot_input_entry.config(state="normal", fg="white")
                    if self.bot_input_entry.get() == self.bot_input_placeholder:
                        self.bot_input_entry.delete(0, tk.END)
                else:
                    self.bot_input_entry.config(state="disabled")
        else:
            self.start_bot_btn.config(state="normal")
            self.stop_bot_btn.config(state="disabled")
            self.restart_bot_btn.config(state="disabled")
            self.force_check_btn.config(state="disabled")
            self.bot_status_label.config(text="● OFFLINE", fg="#ff4444")
            # Disable bot input when bot is not running
            if hasattr(self, 'bot_input_entry'):
                self.bot_input_entry.config(state="normal")
                self.bot_input_entry.delete(0, tk.END)
                self.bot_input_entry.insert(0, self.bot_input_placeholder)
                self.bot_input_entry.config(fg="gray", state="disabled")
            
    def clear_logs(self):
        """Clear the log display"""
        self.log_display.delete(1.0, tk.END)
        
    def kick_player(self):
        """Kick selected player"""
        selection = self.players_listbox.curselection()
        if selection:
            player = self.players_listbox.get(selection[0])
            self.send_server_command(f"kick {player}")
            
    def ban_player(self):
        """Ban selected player"""
        selection = self.players_listbox.curselection()
        if selection:
            player = self.players_listbox.get(selection[0])
            self.send_server_command(f"ban {player}")
            
    def make_op(self):
        """Make selected player OP"""
        selection = self.players_listbox.curselection()
        if selection:
            player = self.players_listbox.get(selection[0])
            self.send_server_command(f"op {player}")
            
    def remove_op(self):
        """Remove OP from selected player"""
        selection = self.players_listbox.curselection()
        if selection:
            player = self.players_listbox.get(selection[0])
            self.send_server_command(f"deop {player}")
    
    def apply_alert_settings(self):
        """Apply alert threshold settings from the UI"""
        try:
            # Check if UI elements exist
            if not hasattr(self, 'memory_threshold_var') or not hasattr(self, 'cpu_threshold_var'):
                messagebox.showwarning("Alert Settings", "Alert settings UI not initialized yet. Please wait for the interface to load completely.")
                return
            
            # Get memory threshold in MB
            memory_text = self.memory_threshold_var.get().strip()
            if memory_text:
                self.memory_threshold_mb = float(memory_text)
            
            # Get CPU threshold as percentage
            cpu_text = self.cpu_threshold_var.get().strip()
            if cpu_text:
                self.cpu_threshold_percent = float(cpu_text)
            
            # Get sound alerts setting
            if hasattr(self, 'alert_sound_var'):
                self.sound_alerts_enabled = self.alert_sound_var.get()
            
            # Show confirmation
            messagebox.showinfo("Alert Settings", 
                              f"Alert settings updated:\n"
                              f"Memory threshold: {self.memory_threshold_mb}MB\n"
                              f"CPU threshold: {self.cpu_threshold_percent}%\n"
                              f"Sound alerts: {'Enabled' if self.sound_alerts_enabled else 'Disabled'}")
        
        except ValueError as e:
            messagebox.showerror("Invalid Input", "Please enter valid numeric values for thresholds.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply alert settings: {str(e)}")
    
    def check_performance_alerts(self, memory_usage, cpu_usage):
        """Check if performance metrics exceed thresholds and trigger alerts"""
        current_time = time.time()
        
        # Skip if still in cooldown period
        if current_time - self.last_alert_time < self.alert_cooldown:
            return
        
        alert_triggered = False
        alert_messages = []
        
        # Check memory threshold
        if memory_usage > self.memory_threshold_mb:
            alert_messages.append(f"High memory usage: {memory_usage:.1f}MB (threshold: {self.memory_threshold_mb}MB)")
            alert_triggered = True
        
        # Check CPU threshold
        if cpu_usage > self.cpu_threshold_percent:
            alert_messages.append(f"High CPU usage: {cpu_usage:.1f}% (threshold: {self.cpu_threshold_percent}%)")
            alert_triggered = True
        
        if alert_triggered:
            self.trigger_performance_alert(alert_messages)
            self.last_alert_time = current_time
    
    def trigger_performance_alert(self, messages):
        """Trigger visual and audio performance alerts"""
        try:
            # Play sound alert if enabled
            if hasattr(self, 'alert_sound_var') and self.alert_sound_var.get():
                try:
                    import winsound
                    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                except Exception as e:
                    print(f"Sound alert failed: {e}")
            
            # Show non-intrusive notification in the analytics display
            alert_text = "⚠️ PERFORMANCE ALERT ⚠️\n" + "\n".join(messages)
            
            # Visual alert: Change label colors to red temporarily
            if hasattr(self, 'memory_label'):
                original_color = self.memory_label.cget('fg')
                self.memory_label.config(fg='#ff6b6b')  # Red text
                
                # Reset color after 3 seconds
                self.root.after(3000, lambda: self.memory_label.config(fg=original_color))
            
            if hasattr(self, 'cpu_label'):
                original_color = self.cpu_label.cget('fg')
                self.cpu_label.config(fg='#ff6b6b')  # Red text
                
                # Reset color after 3 seconds
                self.root.after(3000, lambda: self.cpu_label.config(fg=original_color))
            
            # Flash the notebook tab by changing its text temporarily
            try:
                # Get current tab count to find analytics tab index
                tab_count = self.notebook.index("end")
                for i in range(tab_count):
                    tab_text = self.notebook.tab(i, "text")
                    if "Analytics" in tab_text:
                        # Flash the tab text
                        self.notebook.tab(i, text="⚠️ ALERT - Analytics")
                        self.root.after(3000, lambda idx=i: self.notebook.tab(idx, text="📊 Analytics"))
                        break
            except Exception as e:
                print(f"Tab flash failed: {e}")
            
            # Log the alert
            print(f"Performance Alert: {'; '.join(messages)}")
            
            # Show a temporary popup message
            messagebox.showwarning("Performance Alert", "\n".join(messages))
            
        except Exception as e:
            print(f"Error triggering performance alert: {e}")
            # Fallback: at least show the message
            try:
                messagebox.showwarning("Performance Alert", f"Alert triggered!\n{'; '.join(messages)}")
            except:
                print(f"Fallback alert: {'; '.join(messages)}")
    
    def test_performance_alert(self):
        """Test the performance alert system with simulated high values"""
        test_messages = [
            "This is a test alert to demonstrate the system",
            f"Simulated memory usage: {self.memory_threshold_mb + 500:.1f}MB (threshold: {self.memory_threshold_mb}MB)",
            f"Simulated CPU usage: {self.cpu_threshold_percent + 15:.1f}% (threshold: {self.cpu_threshold_percent}%)"
        ]
        self.trigger_performance_alert(test_messages)

def main():
    root = tk.Tk()
    app = MinecraftServerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()