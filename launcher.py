import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

class LauncherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Server Launcher")
        self.root.geometry("500x400")  # Increased size for better spacing
        self.root.configure(bg="#2b2b2b")
        self.root.resizable(False, False)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title_label = tk.Label(self.root, text="🎮 Minecraft Server Manager", 
                              bg="#2b2b2b", fg="white", 
                              font=('Arial', 16, 'bold'))
        title_label.pack(pady=(30, 10))
        
        # Description
        desc_label = tk.Label(self.root, 
                             text="Unified interface for managing your server and Discord bot:",
                             bg="#2b2b2b", fg="#cccccc", 
                             font=('Arial', 11))
        desc_label.pack(pady=(0, 25))
        
        # Buttons frame
        buttons_frame = tk.Frame(self.root, bg="#2b2b2b")
        buttons_frame.pack(pady=10, padx=30, fill="x")
        
        # Main Launch Button
        launch_btn = tk.Button(buttons_frame, 
                               text="� Launch Server Manager\n(Complete Interface)", 
                               command=self.launch_combined_mode,
                               bg="#4CAF50", fg="white", 
                               font=('Arial', 14, 'bold'),
                               width=35, height=4,
                               relief="flat", bd=0)
        launch_btn.pack(pady=15, fill="x")
        
        # Alternative options (smaller)
        alt_frame = tk.Frame(self.root, bg="#2b2b2b")
        alt_frame.pack(pady=(20, 10), padx=50, fill="x")
        
        tk.Label(alt_frame, text="Alternative Options:", 
                bg="#2b2b2b", fg="#888888", font=('Arial', 10)).pack()
        
        alt_buttons = tk.Frame(alt_frame, bg="#2b2b2b")
        alt_buttons.pack(fill="x", pady=10)
        
        # Discord Bot GUI only (smaller)
        bot_gui_btn = tk.Button(alt_buttons, 
                               text="🤖 Bot Only", 
                               command=self.launch_bot_gui,
                               bg="#7B1FA2", fg="white", 
                               font=('Arial', 9),
                               width=15, height=2)
        bot_gui_btn.pack(side="left", padx=5)
        
        # Standard mode button (smaller)
        standard_btn = tk.Button(alt_buttons, 
                                text="⚡ Console Mode", 
                                command=self.launch_standard_mode,
                                bg="#2196F3", fg="white", 
                                font=('Arial', 9),
                                width=15, height=2)
        standard_btn.pack(side="right", padx=5)
        
        # Info label at bottom
        info_label = tk.Label(self.root, 
                             text="Main interface includes server control, bot management, logs, and player monitoring",
                             bg="#2b2b2b", fg="#888888", 
                             font=('Arial', 9),
                             justify="center")
        info_label.pack(side="bottom", pady=20)
    def launch_combined_mode(self):
        """Launch with combined server + bot GUI interface"""
        # Show confirmation first, then launch after user clicks OK
        messagebox.showinfo("Launching", "Combined GUI interface will start after you click OK.\nThis launcher will then close.")
        
        try:
            subprocess.Popen([sys.executable.replace('python.exe', 'pythonw.exe'), "server_gui.py"],
                           creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
            self.root.destroy()  # Use destroy instead of quit
            sys.exit(0)
        except Exception as e:
            try:
                subprocess.Popen([sys.executable, "server_gui.py"])
                self.root.destroy()  # Use destroy instead of quit
                sys.exit(0)
            except Exception as e2:
                messagebox.showerror("Error", f"Failed to launch combined mode: {e2}")
            
    def launch_bot_gui(self):
        """Launch Discord bot GUI only"""
    def launch_bot_gui(self):
        """Launch Discord bot GUI only"""
        try:
            subprocess.Popen([sys.executable.replace('python.exe', 'pythonw.exe'), "bot.py"])
            messagebox.showinfo("Launched", "Discord Bot is starting...\nThis launcher will now close.")
            self.root.destroy()
            sys.exit(0)
        except Exception as e:
            try:
                subprocess.Popen([sys.executable, "bot.py"])
                messagebox.showinfo("Launched", "Discord Bot is starting...\nThis launcher will now close.")
                self.root.destroy()
                sys.exit(0)
            except Exception as e2:
                messagebox.showerror("Error", f"Failed to launch bot: {e2}")
            
    def launch_gui_mode(self):
        """Launch with GUI interface"""
        try:
            subprocess.Popen([sys.executable.replace('python.exe', 'pythonw.exe'), "server_gui.py"])
            messagebox.showinfo("Launched", "Server GUI interface is starting...\nThis launcher will now close.")
            self.root.destroy()
            sys.exit(0)
        except Exception as e:
            try:
                subprocess.Popen([sys.executable, "server_gui.py"])
                messagebox.showinfo("Launched", "Server GUI interface is starting...\nThis launcher will now close.")
                self.root.destroy()
                sys.exit(0)
            except Exception as e2:
                messagebox.showerror("Error", f"Failed to launch GUI mode: {e2}")
            
    def launch_standard_mode(self):
        """Launch in console mode"""
        try:
            subprocess.Popen([sys.executable, "bot.py"])
            messagebox.showinfo("Launched", "Console mode is starting...\nThis launcher will now close.")
            self.root.destroy()
            sys.exit(0)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch console mode: {e}")

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