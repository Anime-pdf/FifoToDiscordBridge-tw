import time
import discord
import json
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

discord_token = config['discord_token']
servers = config['servers']

intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)

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
                client.loop.create_task(self.send_message(line))
    
    async def send_message(self, message):
        channel = client.get_channel(self.channel_id)
        await channel.send(message)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    observer = Observer()
    for server in servers:
        handler = LogFileHandler(server)
        observer.schedule(handler, path=server['logfile_path'], recursive=False)
    observer.start()
    # Polling loop to check for file changes more frequently
    while True:
        observer.dispatch_events()
        time.sleep(0.1)  # Adjust sleep time for faster polling

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    for server in servers:
        if message.channel.id == server['channel_id']:
            with open(server['fifo_path'], 'a') as fifo:
                fifo.write(f'{message.content}\n')

client.run(discord_token)
