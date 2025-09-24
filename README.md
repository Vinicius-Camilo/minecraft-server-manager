# 🎮 Minecraft Server & Discord Bot Manager

A comprehensive Python-based management interface for Minecraft servers and Discord bots with real-time monitoring, performance analytics, and intelligent alerting system.

> **📝 Personal Note:** This project was created for fun to manage a small Minecraft server for friends. While it includes comprehensive features and professional documentation, it's designed for small-scale use and personal learning. Feel free to use, modify, or learn from it, but don't expect enterprise-level complexity! 😊

## 📋 Table of Contents
- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Technical Details](#-technical-details)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### 🖥️ Server Management
- **One-click server start/stop** with intelligent process detection
- **Real-time console output** with interactive command input
- **Automatic process cleanup** and management
- **Server status monitoring** with connection testing

### 🤖 Discord Bot Integration
- **Integrated Discord bot** with automatic status monitoring
- **Real-time server status updates** in Discord channels (every 30 seconds)
- **Player join/leave notifications** from server log monitoring
- **External and internal connectivity testing**
- **Persistent status message management** (remembers and updates existing messages)
- **Force server checks** via trigger file system
- **Bot process management** and monitoring from GUI

### 📊 Performance Analytics
- **Real-time performance monitoring** (CPU, Memory, TPS simulation)
- **Player activity tracking** with join/leave timestamps and playtime statistics
- **Performance history display** with tabular data format
- **Uptime tracking** and server health metrics
- **Performance data collection** with 60-point rolling history

### ⚠️ Intelligent Alerting
- **Configurable performance thresholds** for CPU and memory
- **Visual and audio alert system** with customizable settings
- **Non-intrusive notifications** with cooldown periods
- **Performance degradation warnings**

### ⚙️ Advanced Features
- **Server properties editor** with backup system
- **Player management tools** (kick, ban, OP management)
- **Log file monitoring** and analysis
- **Multi-tab interface** with organized functionality

## 🔧 Prerequisites

### System Requirements
- **Python 3.8+** (developed with Python 3.12.3)
- **Windows OS** (uses Windows-specific features)

### Required Services (Must be set up before installation)
- **Minecraft Server (Java Edition)** - A running Minecraft server instance
  - Server must be accessible locally (localhost:25565 or custom port)
  - Server log files must be accessible for player tracking
  - Compatible with standard Minecraft server software (Vanilla, Spigot, Paper, Fabric, Forge, etc.)

- **Discord Bot Application** - A created Discord bot with token
  - Bot must be created at [Discord Developer Portal](https://discord.com/developers/applications)
  - Bot token obtained and ready for configuration
  - Bot invited to your Discord server with appropriate permissions:
    - Send Messages
    - Embed Links
    - Read Message History
    - Use Slash Commands (if planning to extend functionality)

### Network Requirements
- **Local Network Access** - For server monitoring and control
- **Internet Connection** - For Discord bot functionality
- **Optional: External Domain** - For public server accessibility testing

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Vinicius-Camilo/minecraft-server-manager.git
   cd minecraft-server-manager
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   copy .env.example .env
   # Edit .env with your configuration
   ```

## ⚙️ Configuration

### Environment Variables (.env)
```env
# Discord Bot Configuration (Required)
TOKEN=your_discord_bot_token_here
CHANNEL_ID=your_discord_channel_id_here

# Minecraft Server Configuration (Required)
SERVER_IP=your.minecraft.server.ip
SERVER_PORT=25565
MINECRAFT_LOG_FILE=path\to\your\minecraft\server\logs\latest.log

# Optional: External domain for public server monitoring
EXTERNAL_DOMAIN=your.domain.com
```

### Discord Bot Setup (Required)

> ⚠️ **Important**: You must create and configure a Discord bot before using this application.

#### Step-by-Step Discord Bot Creation:

1. **Create Discord Application:**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application" and give it a name (e.g., "Minecraft Server Bot")
   - Save the application

2. **Create Bot User:**
   - Navigate to the "Bot" section in your application
   - Click "Add Bot" to create a bot user
   - Copy the **Bot Token** (you'll need this for your `.env` file)
   - ⚠️ **Keep this token secret!** Never share it publicly

3. **Configure Bot Permissions:**
   - In the "Bot" section, enable these **Privileged Gateway Intents**:
     - Message Content Intent (for reading server messages)
   - Under "Bot Permissions" select:
     - Send Messages
     - Embed Links
     - Read Message History
     - Attach Files

4. **Invite Bot to Your Server:**
   - Go to "OAuth2" → "URL Generator"
   - Select "bot" scope
   - Select the same permissions as above
   - Copy the generated URL and open it to invite the bot to your server

5. **Get Channel ID:**
   - In Discord, enable "Developer Mode" (User Settings → Advanced)
   - Right-click the channel where you want status updates
   - Click "Copy Channel ID"

### Minecraft Server Setup (Required)

> ⚠️ **Important**: You must have a working Minecraft server before using this application.

#### Requirements:
- **Server Type**: Java Edition (Vanilla, Spigot, Paper, Fabric, Forge, etc.)
- **Accessibility**: Server must be running and accessible locally
- **Log Access**: Application needs read access to server log files
- **Default Port**: Usually runs on port 25565 (configurable)

#### Supported Server Software:
- ✅ Vanilla Minecraft Server
- ✅ Spigot/Bukkit
- ✅ Paper
- ✅ Fabric
- ✅ Forge (ModLoader)
- ✅ Any Java Edition server that generates standard log files

## 🚀 Usage

### Quick Start
```bash
# Activate virtual environment
.venv\Scripts\activate

# Run the main GUI application
python server_gui.py
```

### Available Scripts
- `server_gui.py` - Main GUI application with full functionality
- `bot.py` - Standalone Discord bot (if running separately)
- `launcher.py` - Alternative launcher with file manager integration

### GUI Navigation
1. **Control Tab**: Start/stop server and bot, view status
2. **Bot Tab**: Monitor Discord bot logs and status
3. **Console Tab**: Interactive server console with command input
4. **Logs Tab**: View and analyze server log files
5. **Players Tab**: Manage connected players and permissions
6. **Properties Tab**: Edit server.properties with backup system
7. **Analytics Tab**: Performance monitoring and alert configuration

## 📁 Project Structure

```
minecraft-server-manager/
├── server_gui.py          # Main GUI application
├── bot.py                 # Discord bot implementation
├── launcher.py            # Alternative launcher
├── File Manager.py        # File management utilities
├── requirements.txt       # Python dependencies
├── .env.example          # Environment configuration template
├── .gitignore            # Git ignore rules
├── README.md             # Project documentation
└── backup_*/             # Automatic backups (gitignored)
```

## 🔧 Technical Details

### Architecture
- **GUI Framework**: Tkinter with custom dark theme
- **Process Management**: psutil and subprocess for cross-platform compatibility
- **Discord Integration**: discord.py library with async/await patterns
- **Server Communication**: mcstatus library for Minecraft server queries
- **Performance Monitoring**: Real-time system metrics collection
- **Data Persistence**: JSON-based configuration and statistics storage

### Key Components
- **MinecraftServerGUI**: Main application class with tabbed interface
- **Process Detection**: Smart detection of existing server/bot processes
- **Alert System**: Configurable thresholds with visual and audio notifications
- **Analytics Engine**: Real-time performance data collection and analysis
- **Console Integration**: Bidirectional communication with server console

### Performance Features
- **Memory Monitoring**: Real-time RAM usage tracking
- **CPU Tracking**: Process-specific CPU utilization
- **TPS Monitoring**: Server performance tick tracking
- **Player Analytics**: Join/leave events and playtime statistics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests (if available)
python -m pytest

# Format code
python -m black .
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Discord.py** community for excellent Discord API wrapper
- **mcstatus** developers for Minecraft server query functionality
- **psutil** contributors for cross-platform system monitoring
- **Tkinter** community for GUI development resources

## �️ Troubleshooting

### Common Setup Issues

#### Discord Bot Issues:
- **"TOKEN not found in environment variables"**
  - ✅ Ensure `.env` file exists and contains `TOKEN=your_bot_token`
  - ✅ Check that the bot token is correct (no extra spaces)
  - ✅ Verify the bot is created in Discord Developer Portal

- **"Could not find channel with ID"**
  - ✅ Enable Developer Mode in Discord settings
  - ✅ Right-click the target channel and copy the correct Channel ID
  - ✅ Ensure the bot has access to the channel (proper permissions)

- **Bot appears offline in Discord**
  - ✅ Check internet connection
  - ✅ Verify bot token is valid and not regenerated
  - ✅ Ensure bot has proper permissions in the Discord server

#### Minecraft Server Issues:
- **"Failed to connect to server"**
  - ✅ Confirm Minecraft server is running
  - ✅ Check server IP and port configuration in `.env`
  - ✅ Verify server is accessible (try connecting with Minecraft client)

- **"Failed to read log file"**
  - ✅ Check `MINECRAFT_LOG_FILE` path in `.env` is correct
  - ✅ Ensure the application has read permissions to the log file
  - ✅ Verify the server is generating logs in the expected location

- **Player tracking not working**
  - ✅ Confirm log file path is correct
  - ✅ Check that server is logging player join/leave events
  - ✅ Ensure log file format is standard (vanilla Minecraft format)

#### Application Issues:
- **GUI doesn't start**
  - ✅ Activate virtual environment before running
  - ✅ Install all dependencies: `pip install -r requirements.txt`
  - ✅ Check Python version is 3.8+

- **Performance monitoring shows no data**
  - ✅ Ensure server is running when starting the application
  - ✅ Check that the server process is detectable by the application

### Getting Help
If these solutions don't resolve your issue:
1. Check the console output for specific error messages
2. Verify all prerequisites are properly set up
3. Ensure both Discord bot and Minecraft server are working independently

## �📞 Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/Vinicius-Camilo/minecraft-server-manager/issues) page
2. Create a new issue with detailed information
3. Include system information and error messages

