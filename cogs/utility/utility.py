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
                
                u_perms = discord.Permissions()
                u_perms.update(**dict(read_messages=False, send_messages=False, view_channels=False))
                v_perms = discord.Permissions()
                v_perms.update(**dict(read_messages=True, send_messages=True))
                v_role: discord.Role = await ctx.guild.create_role(name="Verified", color=discord.Color.green(), permissions=v_perms)
                u_role: discord.Role = await ctx.guild.create_role(name="Unverified", color=discord.Color.red(), permissions=u_perms)
                v_channel: discord.TextChannel = await ctx.guild.create_text_channel(name="captcha-verification", position=0, topic="Verify yourself to gain access to the server.")
                await v_channel.set_permissions(u_role, read_messages=True, send_messages=True)
                await v_channel.set_permissions(v_role, read_messages=False, send_messages=False)
                await v_channel.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False)
                await v_channel.set_permissions(ctx.guild.me, read_messages=True, send_messages=True, embed_links=True)
                await cur.execute("INSERT INTO captcha VALUES (?, ?, ?, ?)", (ctx.guild.id, v_channel.id, v_role.id, u_role.id))
                await self.bot.db.commit()
                embed = discord.Embed(
                    title="Captcha Setup", 
                    description=(
                        f"**Verified Role:** {v_role.mention}\n"
                        f"**Unverified Role:** {u_role.mention}\n"
                        f"**Verification Channel:** {v_channel.mention}"
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
            channel: discord.TextChannel = ctx.guild.get_channel(data[1])
            role1: discord.Role = ctx.guild.get_role(data[2])
            role2: discord.Role = ctx.guild.get_role(data[3])

            confirm = await ctx.confirm("Are you sure you want to disable captcha?")
            if not confirm:
                await ctx.send("Cancelled.")
                return
            
            await role1.delete()
            await role2.delete()
            await channel.delete()
            await cur.execute("DELETE FROM captcha WHERE guild_id = ?", (ctx.guild.id,))
            await self.bot.db.commit()
            await ctx.channel.send(embed=discord.Embed(title="Captcha Verification Disabled", color=self.bot.config.color), delete_after=10)

