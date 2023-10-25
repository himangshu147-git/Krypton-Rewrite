
from __future__ import annotations
from typing import List, NamedTuple, Optional, Union
import discord
from discord.interactions import Interaction
import config
import asyncio
import io
from .captcha import generate
from discord.ext.commands import Context
from discord.ext import commands

class LinkType(NamedTuple):
    name: Optional[str] = None
    url: Optional[str] = None
    emoji: Optional[str] = None

class LinkButton(discord.ui.View):
    def __init__(self, links: Union[LinkType, List[LinkType]]):
        super().__init__()

        links = links if isinstance(links, list) else [links]

        for link in links:
            self.add_item(discord.ui.Button(label=link.name, url=link.url, emoji=link.emoji))

class ConfirmationView(discord.ui.View):
    def __init__(self, *, timeout: float, author_id: int, delete_after: bool) -> None:
        super().__init__(timeout=timeout)
        self.value: Optional[bool] = None
        self.delete_after: bool = delete_after
        self.author_id: int = author_id
        self.message: Optional[discord.Message] = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user and interaction.user.id == self.author_id:
            return True
        else:
            await interaction.response.send_message('This confirmation dialog is not for you.', ephemeral=True)
            return False

    async def on_timeout(self) -> None:
        if self.delete_after and self.message:
            await self.message.delete()

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        await interaction.response.defer()
        if self.delete_after:
            await interaction.delete_original_response()

        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        await interaction.response.defer()
        if self.delete_after:
            await interaction.delete_original_response()
        self.stop()

class LockView(discord.ui.View):
    def __init__(self, ctx: Context):
        super().__init__()
        self.ctx = ctx
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
       if interaction.user.id == self.ctx.author.id:
            return True
       else:
            await interaction.response.send_message("You cannot use this button.", ephemeral=True)
            return False
    
    @discord.ui.button(emoji="🔓", style=discord.ButtonStyle.grey)
    async def unlock(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = False
        overwrites = {
                    self.ctx.guild.default_role: discord.PermissionOverwrite(send_messages = True, read_message_history = True),
                    self.ctx.guild.me: discord.PermissionOverwrite(view_channel = True, send_messages = True, read_message_history = True),
                }
        await self.ctx.channel.edit(overwrites=overwrites)
        button.disabled = True
        self.lock.disabled = False
        await interaction.response.edit_message(embed=discord.Embed(description=f"Unlocked {self.ctx.channel.mention}", color=discord.Color.green()) ,view=self)

    @discord.ui.button(emoji="🔒", style=discord.ButtonStyle.grey, disabled=True)
    async def lock(self, interaction: discord.Interaction, button: discord.ui.Button):
        overwrites = {
                self.ctx.guild.default_role: discord.PermissionOverwrite(send_messages = False, read_message_history = False),
                self.ctx.guild.me: discord.PermissionOverwrite(view_channel = True, send_messages = True, read_message_history = True),
            }
        await self.ctx.channel.edit(overwrites=overwrites)
        button.disabled = True
        self.unlock.disabled = False
        await interaction.response.edit_message(embed=discord.Embed(description=f"Locked {self.ctx.channel.mention}", color=discord.Color.red()) ,view=self)

class SomeLinks(discord.ui.View):
    def __init__(self, *, timeout = None):
        super().__init__(timeout=timeout)
        self.add_item(discord.ui.Button(style=discord.ButtonStyle.url, label="Support", url=config.support))
        self.add_item(discord.ui.Button(style=discord.ButtonStyle.url, label="Invite", url=config.invite))

class VerifyButtons(discord.ui.View):
    def __init__(
            self,
            bot: commands.Bot,
            member: discord.Member,
            timeout= None):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.member = member
        self.attepmts = 0

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id == self.member.id:
            return True
        else:
            await interaction.response.send_message(f"You cannot use this button.\nOnly {self.member.name} can use this", ephemeral=True)
            return False
            

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green)
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with self.bot.db.cursor() as cur:
            data = await cur.execute(
                """SELECT verified_role FROM captcha WHERE guild_id = ?""",
                (interaction.guild.id,)
            )
            data = await data.fetchall()

        v_role = data[0][0]

        x = generate()

        role_verified = discord.utils.get(interaction.guild.roles, id=v_role)
        
        file=discord.File(io.BytesIO(x[0]), filename="captcha.png")
        em = discord.Embed(
            title="Verification",
            description="Please type the text in the image below to gain access to the server!",
            color=discord.Color.green()
        )
        em.set_image(url="attachment://captcha.png")

        mmm: discord.Message = await interaction.response.send_message(file=file, embed=em)

        while True:
            try:
                msg = await self.bot.wait_for("message", check=lambda m: m.author == interaction.user and m.channel == interaction.channel, timeout=180)
                await asyncio.sleep(3)
                await msg.delete()

            except asyncio.TimeoutError:
                break
            else:
                if msg.content == x[1] or msg.content.lower() == x[1].lower() or msg.content.upper() == x[1].upper() or msg.content.capitalize() == x[1].capitalize() or msg.content.title() == x[1].title() or msg.content.swapcase() == x[1].swapcase() or msg.content.casefold() == x[1].casefold() or msg.content.replace(" ", "") == x[1].replace(" ", "") or msg.content.replace(" ", "").lower() == x[1].replace(" ", "").lower() or msg.content.replace(" ", "").upper() == x[1].replace(" ", "").upper() or msg.content.replace(" ", "").capitalize() == x[1].replace(" ", "").capitalize() or msg.content.replace(" ", "").title() == x[1].replace(" ", "").title() or msg.content.replace(" ", "").swapcase() == x[1].replace(" ", "").swapcase() or msg.content.replace(" ", "").casefold() == x[1].replace(" ", "").casefold() or msg.content.replace(" ", "") == x[1].replace(" ", ""):
                    
                    await interaction.channel.send("Verified! You now have access to the server!", delete_after=10)
                    for channel in interaction.guild.text_channels:
                        if channel.permissions_for(interaction.guild.default_role).view_channel:
                            await channel.set_permissions(
                                interaction.user, read_messages=True, send_messages=True, view_channel=True
                            )
                        else:
                            await channel.set_permissions(
                                interaction.user, read_messages=False, send_messages=False, view_channel=False
                            )

                    for channel in interaction.guild.voice_channels:
                        if channel.permissions_for(interaction.guild.default_role).view_channel:
                            await channel.set_permissions(
                                interaction.user, connect=True, speak=True, view_channel=True
                            )
                        else:
                            await channel.set_permissions(
                                interaction.user, connect=False, speak=False, view_channel=False
                            )

                    await interaction.user.add_roles(role_verified)
                    await interaction.channel.delete()
                    break
                else:
                    await interaction.channel.send("Incorrect! please try again!", delete_after=5)
                    self.attepmts += 1
                    if self.attepmts == 3:
                        await mmm.delete()  
                        await interaction.channel.send("Too many attempts!, Please press the button again.", delete_after=10)
                        break