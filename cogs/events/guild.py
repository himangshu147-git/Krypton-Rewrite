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

            channel: discord.TextChannel = self.bot.get_channel(data[1])
            v_role: discord.Role = discord.utils.get(member.guild.roles, id=data[2])
            u_role: discord.Role = discord.utils.get(member.guild.roles, id=data[3])

            if channel is None:
                return
            
            if v_role is None:
                return
            
            if u_role is None:
                return

            view = VerifyButtons(bot=self.bot)
            await member.add_roles(u_role)
            await channel.send(content=f"Welcome {member.mention} to {member.guild.name}! Please verify yourself to gain access to the server.", view=view)
            await asyncio.sleep(300)
            if u_role in member.roles:
                for chan in member.guild.text_channels:
                    if chan.permissions_for(member).read_messages and chan.permissions_for(member).send_messages:
                        invite = await chan.create_invite(max_uses=1, max_age=300)
                        return
                await member.send(f"You failed to verify in time.\nYou have been kicked from the server.\njoin again {invite} \n`the invite will expire in 5 minutes`.")
                await member.kick(reason="Failed to verify.")
                await channel.purge(limit=10)