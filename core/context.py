import asyncio
from contextlib import suppress
from typing import Any, List, Optional, Union

import discord
from discord.ext import commands


class Context(commands.Context):
    """Custom context class for the bot."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._log = self.bot._log
    
    async def send(
        self,
        content: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[discord.Message]:
        perms: discord.Permissions = self.channel.permissions_for(self.me)
        if not (perms.send_messages and perms.embed_links):
            with suppress(discord.Forbidden):
                await self.author.send(
                    (
                        "Bot don't have either Embed Links or Send Messages permission in that channel. "
                        "Please give sufficient permissions to the bot."
                    )
                )
                return None

        embeds: Union[discord.Embed, List[discord.Embed]] = kwargs.get(
            "embed"
        ) or kwargs.get("embeds")

        def __set_embed_defaults(embed: discord.Embed, /):
            if not embed.color:
                embed.color = 0xfc6f03
            if not embed.timestamp:
                embed.timestamp = discord.utils.utcnow()
            

        if isinstance(embeds, (list, tuple)):
            for embed in embeds:
                if isinstance(embed, discord.Embed):
                    __set_embed_defaults(embed)
        else:
            if isinstance(embeds, discord.Embed):
                __set_embed_defaults(embeds)

        return await super().send(str(content)[:1990] if content else None, **kwargs)
    
    async def error(self, message: str, delete_after: bool = None, **kwargs: Any) -> Optional[discord.Message]:
        with suppress(discord.HTTPException):
            msg: Optional[discord.Message] = await self.reply(
                embed=discord.Embed(description=message, color=discord.Color.red()),
                delete_after=delete_after,
                **kwargs,
            )
            try:
                await self.bot.wait_for("message_delete", check=lambda m: m.id == self.message.id, timeout=30)
            except asyncio.TimeoutError:
                pass
            else:
                if msg is not None:
                    await msg.delete(delay=0)
            finally:
                return msg

        return None
    
class GuildContext(Context):
    author: discord.Member
    guild: discord.Guild
    channel: Union[discord.VoiceChannel, discord.TextChannel, discord.Thread]
    me: discord.Member
    prefix: str