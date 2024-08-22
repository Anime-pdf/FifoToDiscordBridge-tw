import logging
import json
import os
import asyncio

import nextcord
from watchdog.observers import Observer

from utili import LogFileHandler

# Load configuration
# For convenience, use PyYAML
with open('config.json', 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)

# Configure logging
log_formatter = logging.Formatter(
    '%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
)
log_handler = logging.StreamHandler()  # Output to console
log_handler.setFormatter(log_formatter)

logging.basicConfig(level=logging.INFO, handlers=[log_handler])

# Initialize the Discord client
client = nextcord.Client(intents=nextcord.Intents.all())

# Additional variables
servers = config['servers']
observer = Observer()


@client.event
async def on_ready():
    logging.info('Logged in as %s', client.user)
    for server in servers:
        handler = LogFileHandler(client, server)
        observer.schedule(handler, path=server['logfile_path'], recursive=False)
    observer.start()

    # Keep the script running and let observer handle events
    try:  # you can use atexit
        while True:
            await asyncio.sleep(0.3)  # Adjust sleep time if needed
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


@client.event
async def on_message(message):
    if message.bot:
        return

    for server in servers:
        if message.channel.id != int(server['channel_id']):
            continue
        try:
            with open(server['fifo_path'], 'w', encoding='utf-8') as fifo:
                fifo.write(f'{message.content}\n')
                fifo.flush()  # Ensure data is written immediately
        except IOError as ex:
            logging.info("Error writing to FIFO file: %s", ex)


client.run(config.get('discord_token', os.getenv("discord_token")))
