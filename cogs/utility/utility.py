import discord
import aiosqlite
from discord.ext import commands
from core import Krypton, Context
from utils import ConfirmationView

class Utility(commands.Cog):
    def __init__(self, bot: Krypton):
        self.bot = bot


    
    @commands.hybrid_group(invoke_without_command=True)
    async def captcha(self, ctx: Context):
        """
        Captcha commands.
        """
        async with self.bot.db.cursor() as cur:
            data = await cur.execute("SELECT * FROM captcha WHERE guild_id = ?", (ctx.guild.id,))
            data = await data.fetchone()
            if data is None:
                await ctx.send_help(ctx.command)
                return
            
    
    @captcha.command(name="enable")
    async def captcha_enable(self, ctx: Context):
        """
        Enable captcha.
        """
        await ctx.defer()
        try:
            async with self.bot.db.cursor() as cur:
                data = await cur.execute("SELECT * FROM captcha WHERE guild_id = ?", (ctx.guild.id,))
                data = await data.fetchone()
                if data is not None:
                    await ctx.send(f"This server already has a captcha enabled, Please run `{ctx.prefix}captcha disable` to disable it.")
                    return
                
                v_perms = discord.Permissions()
                v_perms.update(**dict(read_messages=True, send_messages=True))

                v_role: discord.Role = await ctx.guild.create_role(name="Verified", color=discord.Color.green(), permissions=v_perms)
                
                for channel in ctx.guild.text_channels:
                    if channel.permissions_for(ctx.guild.default_role).view_channel:
                        await channel.set_permissions(
                            v_role, read_messages=True, send_messages=True, view_channel=True
                        )
                    else:
                        await channel.set_permissions(
                            v_role, read_messages=False, send_messages=False, view_channel=False
                        )

                for channel in ctx.guild.voice_channels:
                    if channel.permissions_for(ctx.guild.default_role).view_channel:
                        await channel.set_permissions(
                            v_role, connect=True, speak=True, view_channel=True
                        )
                    else:
                        await channel.set_permissions(
                            v_role, connect=False, speak=False, view_channel=False
                        )

                    
                await cur.execute("INSERT INTO captcha VALUES (?, ?)", (ctx.guild.id, v_role.id))
                await self.bot.db.commit()

                embed = discord.Embed(
                    title="Captcha Setup", 
                    description=(
                        f"**Verified Role:** {v_role.mention}\n"
                    )
                    )
                await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"Failed to setup captcha: {e}")

            
    @captcha.command(name="disable")
    @commands.has_permissions(manage_guild=True)
    async def captcha_disable(self, ctx: Context):
        """
        Disable captcha.
        """
        await ctx.defer()
        async with self.bot.db.cursor() as cur:
            data = await cur.execute("SELECT * FROM captcha WHERE guild_id = ?", (ctx.guild.id,))
            data = await data.fetchone()
            if data is None:
                await ctx.send(f"This server does not have a captcha enabled, Please run `{ctx.prefix}captcha enable` to enable.")
                return
            role1: discord.Role = ctx.guild.get_role(data[1])

            confirm = await ctx.confirm("Are you sure you want to disable captcha?")
            if not confirm:
                await ctx.send("Cancelled.")
                return
            
            await role1.delete()
            await cur.execute("DELETE FROM captcha WHERE guild_id = ?", (ctx.guild.id,))
            await self.bot.db.commit()
            await ctx.channel.send(embed=discord.Embed(title="Captcha Verification Disabled", color=self.bot.config.color), delete_after=10)