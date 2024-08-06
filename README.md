# FIFO to Discord bridge

**This python script will start discord bot that will pull lines from logfile and push lines to fifo file.**

# Requirments
**You will need:**
 * DDNet/Teeworlds server with `logfile path/to/logfile` and `sv_input_fifo path/to/fifo`
 * Discord bot with message content intent
 * Python3 with `discord.py` and `watchdog` packages installed

# Config
Copy `config.json.example` and rename it to `config.json`.

`servers` value is an array that should contain values with `logfile_path`, `fifo_path` and `channel_id`. Useful if you have multiple servers running at once.

# Running

```bash
sudo apt update
sudo apt install python3-venv
cd path/to/bot
python3 -m venv venv
source venv/bin/activate
pip install discord.py watchdog
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