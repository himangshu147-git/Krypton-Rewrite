import asyncio

import discord
from discord.ext import commands

from core import Context, Krypton
from utils.buttons import VerifyButtons
from utils.captcha import generate


class Guild(commands.Cog):
    def __init__(self, bot: Krypton) -> None:
        self.bot = bot

    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member: discord.Member):

        async with self.bot.db.cursor() as cur:
            data = await cur.execute("SELECT * FROM captcha WHERE guild_id = ?", (member.guild.id,))
            data = await data.fetchone()
            if data is None:
                return
            
            v_role = discord.utils.get(member.guild.roles, id=data[1])

            for text in member.guild.text_channels:
                await text.set_permissions(
                    member, read_messages=False, send_messages=False, view_channel=False
                )
            
            for voice in member.guild.voice_channels:
                await voice.set_permissions(
                    member, connect=False, speak=False, view_channel=False
                )

            channel: discord.TextChannel = await member.guild.create_text_channel(name=f"verification-{member.name}", overwrites={
                    v_role: discord.PermissionOverwrite(send_messages = False, read_message_history = False, view_channel = False),
                    member.guild.default_role: discord.PermissionOverwrite(send_messages = False, read_message_history = False, view_channel = False),
                    member.guild.me: discord.PermissionOverwrite(view_channel = True, send_messages = True, read_message_history = True),
                    member: discord.PermissionOverwrite(send_messages = True, read_message_history = True, view_channel = True),
                })
                
            view = VerifyButtons(bot=self.bot, member=member)

            await channel.send(content=f"Welcome {member.mention} to {member.guild.name}! Please verify yourself to gain access to the server.", view=view)

            await asyncio.sleep(300)

            for role in member.roles:
                if role.id == v_role.id:
                    return
                else:
                    invite = await channel.create_invite(max_uses=1, max_age=300)
                    await member.send(f"You failed to verify in time.\nYou have been kicked from the server.\njoin again {invite} \n`the invite will expire in 5 minutes`.")
                    await member.kick(reason="Failed to verify.")