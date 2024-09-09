import logging
import os

import nextcord
from watchdog.events import FileSystemEventHandler


def send_fifo(fifo_path, message):
    try:
        with open(fifo_path, 'w', encoding='utf-8') as fifo:
            fifo.write(f'{message}\n')
            fifo.flush()  # Ensure data is written immediately
    except IOError as ex:
        logging.info("Error writing to FIFO file: %s", ex)


def sanitize_message(message: str) -> str:
    """Escape special Markdown characters used in Discord.

    :param message: str
    :return: str
    """
    escape_chars = ['\\', '_', '*', '~', '`', '|', '<', '>', '(', ')', '[', ']']
    for char in escape_chars:
        message = message.replace(char, f'\\{char}')
    return message


class LogFileHandler(FileSystemEventHandler):
    def __init__(self, client: nextcord.Client, server):
        self.logfile_path = server['logfile_path']
        self.fifo_path = server['fifo_path']
        self.channel_id = int(server['channel_id'])
        self.client = client
        self.last_position = 0
        if os.path.exists(self.logfile_path):
            self.last_position = os.path.getsize(self.logfile_path)

    def on_modified(self, event):
        if event.src_path == self.logfile_path:
            self.process_logfile()

    def process_logfile(self):
        with open(self.logfile_path, 'r', encoding='utf-8') as f:
            f.seek(self.last_position)
            new_lines = f.readlines()
            self.last_position = f.tell()
            buffer = ""
            for line in new_lines:
                sanitized_line = sanitize_message(line)
                buffer += sanitized_line
            self.client.loop.create_task(self.send_message(buffer))

    async def send_message(self, message):
        channel = self.client.get_channel(self.channel_id)
        await channel.send(message)
