import tkinter as tk
from tkinter import messagebox, filedialog
import os
import subprocess
import webbrowser
from datetime import datetime

class FileManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Minecraft Server & Discord Bot Manager")
        self.root.geometry("600x700")
        self.root.configure(bg="#2b2b2b")
        self.root.resizable(False, False)
        
        self.bot_dir = r"E:\pessoal\Bot Discord"
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main title
        title_label = tk.Label(self.root, text="🎮 Minecraft Server & Discord Bot Manager", 
                              bg="#2b2b2b", fg="white", 
                              font=('Arial', 16, 'bold'))
        title_label.pack(pady=20)
        
        # Quick Launch Section
        quick_frame = tk.LabelFrame(self.root, text="🚀 Quick Launch", 
                                   bg="#3b3b3b", fg="white", 
                                   font=('Arial', 12, 'bold'))
        quick_frame.pack(fill="x", padx=20, pady=10)
        
        # Single main launch button
        launch_btn = tk.Button(quick_frame, 
                              text="🎮 Launch Server Manager\n(Complete Interface)", 
                              command=self.launch_combined,
                              bg="#4CAF50", fg="white", 
                              font=('Arial', 14, 'bold'),
                              width=30, height=3,
                              relief="flat", bd=0)
        launch_btn.pack(pady=15)
        
        # Alternative options (smaller)
        alt_frame = tk.Frame(quick_frame, bg="#3b3b3b")
        alt_frame.pack(pady=10)
        
        tk.Label(alt_frame, text="Alternative Options:", 
                bg="#3b3b3b", fg="#888888", font=('Arial', 9)).pack()
        
        alt_buttons = tk.Frame(alt_frame, bg="#3b3b3b") 
        alt_buttons.pack(pady=5)
        
        tk.Button(alt_buttons, text="🤖 Bot Only", command=self.launch_bot_gui, 
                 bg="#7B1FA2", fg="white", font=('Arial', 9), width=12, height=1).pack(side="left", padx=5)
        tk.Button(alt_buttons, text="⚡ Console Mode", command=self.launch_standard, 
                 bg="#FF9800", fg="white", font=('Arial', 9), width=12, height=1).pack(side="right", padx=5)
        
        # File Management Section
        file_frame = tk.LabelFrame(self.root, text="📁 File Management", 
                                  bg="#3b3b3b", fg="white", 
                                  font=('Arial', 12, 'bold'))
        file_frame.pack(fill="x", padx=20, pady=10)
        
        # File buttons
        file_buttons_frame = tk.Frame(file_frame, bg="#3b3b3b")
        file_buttons_frame.pack(fill="x", padx=10, pady=10)
        
        # Row 1
        file_row1 = tk.Frame(file_buttons_frame, bg="#3b3b3b")
        file_row1.pack(fill="x", pady=5)
        
        tk.Button(file_row1, text="📂 Bot Folder", command=self.open_bot_folder, 
                 bg="#607D8B", fg="white", font=('Arial', 10), width=15).pack(side="left", padx=5)
        tk.Button(file_row1, text="📄 Edit .env", command=self.edit_env, 
                 bg="#795548", fg="white", font=('Arial', 10), width=15).pack(side="left", padx=5)
        
        # Row 2
        file_row2 = tk.Frame(file_buttons_frame, bg="#3b3b3b")
        file_row2.pack(fill="x", pady=5)
        
        tk.Button(file_row2, text="📜 Edit bot.py", command=self.edit_bot_py, 
                 bg="#E91E63", fg="white", font=('Arial', 10), width=15).pack(side="left", padx=5)
        tk.Button(file_row2, text="🗂️ Server Folder", command=self.open_server_folder, 
                 bg="#3F51B5", fg="white", font=('Arial', 10), width=15).pack(side="left", padx=5)
        
        # Tools Section
        tools_frame = tk.LabelFrame(self.root, text="🔧 Tools & Utilities", 
                                   bg="#3b3b3b", fg="white", 
                                   font=('Arial', 12, 'bold'))
        tools_frame.pack(fill="x", padx=20, pady=10)
        
        tools_buttons_frame = tk.Frame(tools_frame, bg="#3b3b3b")
        tools_buttons_frame.pack(fill="x", padx=10, pady=10)
        
        # Tools row 1
        tools_row1 = tk.Frame(tools_buttons_frame, bg="#3b3b3b")
        tools_row1.pack(fill="x", pady=5)
        
        tk.Button(tools_row1, text="💻 Command Prompt", command=self.open_cmd, 
                 bg="#37474F", fg="white", font=('Arial', 10), width=18).pack(side="left", padx=3)
        tk.Button(tools_row1, text="🐍 Python Shell", command=self.open_python, 
                 bg="#4CAF50", fg="white", font=('Arial', 10), width=18).pack(side="left", padx=3)
        
        # Tools row 2
        tools_row2 = tk.Frame(tools_buttons_frame, bg="#3b3b3b")
        tools_row2.pack(fill="x", pady=5)
        
        tk.Button(tools_row2, text="📋 View Logs", command=self.view_logs, 
                 bg="#FF5722", fg="white", font=('Arial', 10), width=18).pack(side="left", padx=3)
        tk.Button(tools_row2, text="🔄 Restart Bot", command=self.quick_restart_bot, 
                 bg="#9C27B0", fg="white", font=('Arial', 10), width=18).pack(side="left", padx=3)
        
        # Status Section
        status_frame = tk.LabelFrame(self.root, text="📊 System Status", 
                                    bg="#3b3b3b", fg="white", 
                                    font=('Arial', 12, 'bold'))
        status_frame.pack(fill="x", padx=20, pady=10)
        
        # Status info
        self.status_text = tk.Text(status_frame, height=8, width=60,
                                  bg="#1e1e1e", fg="#cccccc", 
                                  font=('Consolas', 9),
                                  state='disabled')
        self.status_text.pack(padx=10, pady=10)
        
        # Update status button
        tk.Button(status_frame, text="🔄 Update Status", 
                 command=self.update_status,
                 bg="#009688", fg="white", font=('Arial', 10, 'bold')).pack(pady=5)
        
        # Help Section
        help_frame = tk.Frame(self.root, bg="#2b2b2b")
        help_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Button(help_frame, text="❓ Help & Documentation", 
                 command=self.show_help,
                 bg="#FFC107", fg="black", font=('Arial', 11, 'bold'),
                 width=30).pack(side="left", padx=5)
        
        tk.Button(help_frame, text="🚪 Exit", 
                 command=self.root.quit,
                 bg="#f44336", fg="white", font=('Arial', 11, 'bold'),
                 width=10).pack(side="right", padx=5)
        
        # Initial status update
        self.update_status()
        
    def launch_bot_gui(self):
        """Launch Discord bot GUI"""
        self.run_python_script("discord_bot_gui.py")
        messagebox.showinfo("Launched", "Discord Bot GUI is starting...\nFile Manager will now close.")
        self.root.destroy()
        
    def launch_combined(self):
        """Launch combined interface"""
        # Show confirmation first, then launch after user clicks OK
        messagebox.showinfo("Launching", "Combined interface will start after you click OK.\nFile Manager will then close.")
        self.run_python_script("start.py", ["gui"])
        self.root.destroy()
        
    def launch_standard(self):
        """Launch standard mode"""
        # Show confirmation first, then launch after user clicks OK
        messagebox.showinfo("Launching", "Standard mode will start after you click OK.\nFile Manager will then close.")
        self.run_python_script("start.py")
        self.root.destroy()
        
    def run_python_script(self, script_name, args=None):
        """Run a Python script without showing console window"""
        try:
            cmd = ["pythonw.exe", script_name]  # Use pythonw.exe instead of python
            if args:
                cmd.extend(args)
            
            subprocess.Popen(cmd, cwd=self.bot_dir,
                           creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
            
        except FileNotFoundError:
            # Fallback to regular python if pythonw is not found
            try:
                cmd = ["python.exe", script_name]
                if args:
                    cmd.extend(args)
                subprocess.Popen(cmd, cwd=self.bot_dir)
                messagebox.showinfo("Launched", f"{script_name} has been started!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to launch {script_name}: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch {script_name}: {e}")
            
    def open_bot_folder(self):
        """Open bot folder"""
        try:
            os.startfile(self.bot_dir)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open bot folder: {e}")
            
    def open_server_folder(self):
        """Open server folder"""
        try:
            server_dir = r"F:\server mine atm102\atm10 2"
            if os.path.exists(server_dir):
                os.startfile(server_dir)
            else:
                messagebox.showwarning("Warning", "Server folder not found at expected location.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open server folder: {e}")
            
    def edit_env(self):
        """Edit .env file"""
        try:
            env_path = os.path.join(self.bot_dir, ".env")
            if os.path.exists(env_path):
                os.startfile(env_path)
            else:
                messagebox.showwarning("Warning", ".env file not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit .env: {e}")
            
    def edit_bot_py(self):
        """Edit bot.py file"""
        try:
            bot_path = os.path.join(self.bot_dir, "bot.py")
            if os.path.exists(bot_path):
                os.startfile(bot_path)
            else:
                messagebox.showwarning("Warning", "bot.py file not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit bot.py: {e}")
            
    def open_cmd(self):
        """Open command prompt in bot directory"""
        try:
            subprocess.Popen(["cmd", "/k", f"cd /d \"{self.bot_dir}\""])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open command prompt: {e}")
            
    def open_python(self):
        """Open Python shell in bot directory"""
        try:
            subprocess.Popen(["cmd", "/k", f"cd /d \"{self.bot_dir}\" && python"])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Python shell: {e}")
            
    def view_logs(self):
        """View server logs"""
        try:
            log_path = r"F:\server mine atm102\atm10 2\logs\latest.log"
            if os.path.exists(log_path):
                os.startfile(log_path)
            else:
                messagebox.showwarning("Warning", "Log file not found at expected location.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to view logs: {e}")
            
    def quick_restart_bot(self):
        """Quick restart bot (if running)"""
        try:
            # This is a simple implementation - you might want to enhance it
            subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/FI", f"WINDOWTITLE eq *bot.py*"], 
                          capture_output=True)
            
            # Wait a moment then restart
            import time
            time.sleep(2)
            
            subprocess.Popen(["python", "bot.py"], cwd=self.bot_dir)
            messagebox.showinfo("Restart", "Bot restart attempted!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to restart bot: {e}")
            
    def update_status(self):
        """Update system status display"""
        self.status_text.config(state='normal')
        self.status_text.delete(1.0, tk.END)
        
        status_info = "🖥️ System Status:\n\n"
        
        # Check files
        files_to_check = [
            ("bot.py", "Discord Bot Script"),
            ("launcher.py", "Main Launcher"),
            ("server_gui.py", "Server GUI"),
            ("discord_bot_gui.py", "Bot GUI"),
            (".env", "Configuration File")
        ]
        
        for filename, description in files_to_check:
            file_path = os.path.join(self.bot_dir, filename)
            if os.path.exists(file_path):
                status_info += f"✅ {description}: Found\n"
            else:
                status_info += f"❌ {description}: Missing\n"
        
        # Check server folder
        server_dir = r"F:\server mine atm102\atm10 2"
        if os.path.exists(server_dir):
            status_info += f"✅ Server Folder: Found\n"
        else:
            status_info += f"❌ Server Folder: Not Found\n"
            
        # Check log file
        log_path = r"F:\server mine atm102\atm10 2\logs\latest.log"
        if os.path.exists(log_path):
            status_info += f"✅ Server Logs: Accessible\n"
        else:
            status_info += f"⚠️ Server Logs: Not Found\n"
            
        # Check Python
        try:
            result = subprocess.run(["python", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                status_info += f"✅ Python: {version}\n"
            else:
                status_info += f"❌ Python: Not Working\n"
        except:
            status_info += f"❌ Python: Not Found\n"
            
        status_info += f"\n📁 Bot Directory: {self.bot_dir}\n"
        status_info += f"🕒 Last Updated: {datetime.now().strftime('%H:%M:%S')}"
        
        self.status_text.insert(1.0, status_info)
        self.status_text.config(state='disabled')
        
    def show_help(self):
        """Show help information"""
        help_text = """
🎮 Minecraft Server & Discord Bot Manager Help

🚀 QUICK LAUNCH:
• Main Launcher: Opens the main interface selector
• Bot GUI: Opens Discord bot management only
• Combined: Opens server + bot in one interface
• Standard: Runs original console mode

📁 FILE MANAGEMENT:
• Bot Folder: Opens the bot directory in Explorer
• Edit .env: Edit bot configuration file
• Edit bot.py: Edit the bot script
• Server Folder: Opens Minecraft server directory

🔧 TOOLS:
• Command Prompt: Opens CMD in bot directory
• Python Shell: Opens Python interpreter
• View Logs: Opens server log file
• Restart Bot: Attempts to restart the Discord bot

📊 STATUS:
Shows the status of all important files and components

💡 TIPS:
- Double-click any .bat file to run it directly
- Use the status checker to verify everything is working
- The main launcher gives you the most options
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Help & Documentation")
        help_window.geometry("500x600")
        help_window.configure(bg="#2b2b2b")
        
        help_text_widget = tk.Text(help_window, bg="#1e1e1e", fg="#cccccc", 
                                  font=('Consolas', 10), wrap=tk.WORD)
        help_text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        help_text_widget.insert(1.0, help_text)
        help_text_widget.config(state='disabled')

def main():
    root = tk.Tk()
    app = FileManagerGUI(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()