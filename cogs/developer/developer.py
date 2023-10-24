from typing import Optional

import discord
import asyncio
import config
from core import Context, Krypton, commands


class Developer(commands.Cog):
    def __init__(self, bot: Krypton):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx: Context, *, cog: str):
        """Reloads a cog"""
        if cog == "all":
            for cog in config.extensions:
                try:
                    await self.bot.unload_extension("cogs."+cog)
                    await self.bot.load_extension("cogs."+cog)
                except Exception as e:
                    return await ctx.error(f'Failed to reload cog `{cog}`: `{e}`')
                else:
                    await ctx.send(f'Reloaded cog `{cog}`')
        else:
            try:
                await self.bot.unload_extension("cogs."+cog)
                await self.bot.load_extension("cogs."+cog)
            except Exception as e:
                return await ctx.error(f'Failed to reload cog `{cog}`: `{e}`')
            else:
                await ctx.send(f'Reloaded cog `{cog}`')


    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx: Context, *, cog: str):
        """Loads a cog"""
        if cog == "all":
            for cog in config.extensions:
                try:
                    await self.bot.load_extension("cogs."+cog)
                except Exception as e:
                    return await ctx.error(f'Failed to reload cog `{cog}`: `{e}`')
                else:
                    await ctx.send(f'Reloaded cog `{cog}`')
        else:
            try:
                await self.bot.load_extension("cogs."+cog)
            except Exception as e:
                return await ctx.error(f'Failed to load cog `{cog}`: `{e}`')
            else:
                await ctx.send(f'Loaded cog `{cog}`')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def sync(self, ctx: Context, scope:Optional[str]) -> None:
        if scope == "global":
            await ctx.send("Synchronizing. It may take more then 30 sec", delete_after=15)
            synced=await ctx.bot.tree.sync()
            await asyncio.sleep(5)
            await ctx.send(f"{len(synced)} Slash commands have been globally synchronized.")
            return
        elif scope == "guild":
            await ctx.send("Synchronizing. It may take more then 30 sec", delete_after=15)
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
            await asyncio.sleep(5)
            await ctx.send(f"{len(synced)} Slash commands have been synchronized in this guild.", delete_after=5)
            return
        await ctx.send("The scope must be `global` or `guild`.", delete_after=5)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unsync(self, ctx: Context, scope:Optional[str]) -> None:
        if scope == "global":
            await ctx.send("Unsynchronizing...", delete_after=5)
            ctx.bot.tree.clear_commands(guild=None)
            unsynced = await ctx.bot.tree.sync()
            await asyncio.sleep(5)
            await ctx.send(f"{len(unsynced)} Slash commands have been globally unsynchronized.", delete_after=5)
            return
        elif scope == "guild":
            await ctx.send("Unsynchronizing...", delete_after=5)
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            unsynced = await ctx.bot.tree.sync(guild=ctx.guild)
            await asyncio.sleep(5)
            await ctx.send(f"{len(unsynced)} Slash commands have been unsynchronized in this guild.", delete_after=5)
            return
        await ctx.send("The scope must be `global` or `guild`.", delete_after=5)