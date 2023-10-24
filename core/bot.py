import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Any, Union

import discord
import jishaku
from discord.ext import commands
from discord.gateway import DiscordWebSocket

import config

from .context import Context

jishaku.Flags.NO_UNDERSCORE = True
jishaku.Flags.HIDE = True
jishaku.Flags.NO_DM_TRACEBACK = True

async def identify(self):
    payload = {
            'op': self.IDENTIFY,
            'd': {
                'token': self.token,
                'properties': {
                    'os': 'Discord Android',
                    'browser': 'Discord Android',
                    'device': 'Asus X515',
                },
                'compress': True,
                'large_threshold': 250,
            },
        }

    if self.shard_id is not None and self.shard_count is not None:
        payload['d']['shard'] = [self.shard_id, self.shard_count]

    state = self._connection

    if state._intents is not None:
        payload['d']['intents'] = state._intents.value

    await self.call_hooks("before_identify", self.shard_id, initial=self._initial_identify)
    await self.send_as_json(payload)

DiscordWebSocket.identify = identify

class Krypton(commands.Bot):
    """
    A class representing a Discord bot.
    """
    def __init__(
            self, 
            intents=discord.Intents.all(),
            command_prefix=commands.when_mentioned_or(*config.prefixes), 
            **options: Any
            ) -> None:
        super().__init__(
            intents=intents,
            command_prefix=command_prefix, 
            **options
            )
        self.config = config
        self.setup_logging()
        self.uptime = None
        self.color = 0xffec00


    def setup_logging(self):
        self._log = logging.getLogger(__name__)
        self._log.setLevel(logging.INFO)  
        dt_fmt = '%Y-%m-%d %H:%M:%S'
        formatter = logging.Formatter('{asctime} {levelname:<8} {name} {message}', dt_fmt, style='{')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self._log.addHandler(handler)
        file_handler = RotatingFileHandler(filename='log.log', mode="a", maxBytes=1024 * 1024 * 5, backupCount=5)
        file_handler.setFormatter(formatter)
        self._log.addHandler(file_handler)

    async def get_context(self, message: Union[discord.Interaction, discord.Message], /, *, cls=Context) -> Context:
        return await super().get_context(message, cls=cls)
    
    async def process_commands(self, message: discord.Message):
        if message.content and message.guild is not None:
            ctx = await self.get_context(message)
            if ctx.command is None:
                return
            await self.invoke(ctx)

    async def on_ready(self):
        self._log.info(f"Logged in as {self.user}")
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"I'm coming soon"))

    async def setup_hook(self) -> None:
        self.uptime = discord.utils.utcnow().timestamp()
        await self.setup_extensions()
        await self.setup_application_commands()
        
    async def setup_application_commands(self) -> None:
        c = await self.tree.sync()
        self._log.info(f"Synced {len(c)} commands")
        
    async def setup_extensions(self) -> None:
        for extension in self.config.extensions:
            try:
                await self.load_extension(f"cogs.{extension}")
                self._log.info(f"Loaded extension: {extension}")
            except Exception as e:
                self._log.error(f"Failed to load extension {extension}: {e}") 

        await self.load_extension("jishaku")
        self._log.info(f"Loaded extension: jishaku")  
        
    def boot(self):
        """
        Boots up the bot by running the Discord client with the bot's token.
        """
        self._log.info(f"Booting up...")            
        super().run(self.config.token)
        if KeyboardInterrupt:
            self._log.info("Shutting down...")
            os._exit(0)