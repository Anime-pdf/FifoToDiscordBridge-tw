# FIFO to Discord bridge

**This python script will start discord bot that will pull lines from logfile to send them over discord, and read messages from  discord to push them into fifo file.**

# Requirments
**You will need:**
 * DDNet/Teeworlds server with `logfile path/to/logfile` and `sv_input_fifo path/to/fifo`
 * Discord bot with message content intent
 * Python3 with `nextcord` and `watchdog` packages installed

# Config
Copy `config.json.example` and rename it to `config.json`. Replace values with your own.

**Note: `servers` value is an array that should contain values with `logfile_path`, `fifo_path`, `channel_id`, `broadcast` and `mode`. Useful if you have multiple servers running at once.**

# Running

```bash
sudo apt update
sudo apt install python3-venv
cd path/to/bot
python3 -m venv venv
source venv/bin/activate
pip install nextcord watchdog
python main.py
deactivate
```

# Running As Service
For running your bot as a background service, you can create a systemd service file.

1. **Create a systemd Service File:**
   ```bash
   sudo nano /etc/systemd/system/discord-bot.service
   ```

2. **Add the Following Configuration:**
   Replace `path/to/bot/` with the actual path to bot repository.
   ```ini
   [Unit]
   Description=Discord Bot
   After=network.target

   [Service]
   User=your_username
   WorkingDirectory=/path/to/bot
   ExecStart=/path/to/bot/venv/bin/python /path/to/bot/main.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. **Reload systemd and Start the Service:**
   ```sh
   sudo systemctl daemon-reload
   sudo systemctl start discord-bot.service
   sudo systemctl enable discord-bot.service
   ```

4. **Check the Status:**
   You can check the status of your bot with:
   ```sh
   sudo systemctl status discord-bot.service
   ```

# Showcase
![example](https://github.com/user-attachments/assets/544b3899-48e6-4b2b-99b4-226216f0f8b3)
