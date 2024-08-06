import logging
import discord
import json
import os
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
log_formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
log_handler = logging.StreamHandler()  # Output to console
log_handler.setFormatter(log_formatter)

logging.basicConfig(level=logging.INFO, handlers=[log_handler])

# Load configuration
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

discord_token = config['discord_token']
servers = config['servers']

# Initialize the Discord client
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

def sanitize_message(message):
    # Escape special Markdown characters used in Discord
    escape_chars = ['\\', '_', '*', '~', '`', '|', '>', '(', ')', '[', ']']
    for char in escape_chars:
        message = message.replace(char, f'\\{char}')
    return message

class LogFileHandler(FileSystemEventHandler):
    def __init__(self, server):
        self.logfile_path = server['logfile_path']
        self.fifo_path = server['fifo_path']
        self.channel_id = int(server['channel_id'])
        self.last_position = 0
        if os.path.exists(self.logfile_path):
            self.last_position = os.path.getsize(self.logfile_path)
    
    def on_modified(self, event):
        if event.src_path == self.logfile_path:
            self.process_logfile()
    
    def process_logfile(self):
        with open(self.logfile_path, 'r') as f:
            f.seek(self.last_position)
            new_lines = f.readlines()
            self.last_position = f.tell()
            for line in new_lines:
                sanitized_line = sanitize_message(line)
                client.loop.create_task(self.send_message(sanitized_line))
    
    async def send_message(self, message):
        channel = client.get_channel(self.channel_id)
        await channel.send(message)

@client.event
async def on_ready():
    logging.info(f'Logged in as {client.user}')
    observer = Observer()
    for server in servers:
        handler = LogFileHandler(server)
        observer.schedule(handler, path=server['logfile_path'], recursive=False)
    observer.start()
    
    # Keep the script running and let observer handle events
    try:
        while True:
            await asyncio.sleep(0.1)  # Adjust sleep time if needed
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    for server in servers:
        if str(message.channel.id).strip() == server['channel_id'].strip():
            try:
                with open(server['fifo_path'], 'w') as fifo:
                    fifo.write(f'{message.content}\n')
                    fifo.flush()  # Ensure data is written immediately
            except Exception as e:
                logging.info(f"Error writing to FIFO file: {e}")

client.run(discord_token)
