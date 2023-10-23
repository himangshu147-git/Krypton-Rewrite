from __future__ import annotations

__version__ = "rewrite-0.0.1"
__author__ = "himangshu147-git"
__license__ = "MIT"
# help command source : RoboDanny
# https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/meta.py


import inspect
import itertools
from typing import TYPE_CHECKING, Any, Optional, Union
import datetime
import discord
from discord.ext import commands, menus
import platform
from utils import Pages, format_dt, get_latest_change
import config

if TYPE_CHECKING:
    from core import Krypton, Context, GuildContext

display_cogs = [
    "META",
    "UTILITY",
    "MUSIC",
    "MISC"
]

class Prefix(commands.Converter):
    async def convert(self, ctx: GuildContext, argument: str) -> str:
        user_id = ctx.bot.user.id
        if argument.startswith((f'<@{user_id}>', f'<@!{user_id}>')):
            raise commands.BadArgument('That is a reserved prefix already in use.')
        if len(argument) > 150:
            raise commands.BadArgument('That prefix is too long.')
        return argument


class GroupHelpPageSource(menus.ListPageSource):
    def __init__(self, group: Union[commands.Group, commands.Cog], entries: list[commands.Command], *, prefix: str):
        super().__init__(entries=entries, per_page=6)
        self.group: Union[commands.Group, commands.Cog] = group
        self.prefix: str = prefix
        self.title: str = f'{self.group.qualified_name} Commands'
        self.description: str = self.group.description

    async def format_page(self, menu: Pages, commands: list[commands.Command]):
        embed = discord.Embed(title=self.title, description=self.description, colour=__import__('config').color)

        for command in commands:
            signature = f'{command.qualified_name} {command.signature}'
            embed.add_field(name=signature, value=command.short_doc or 'No help given...', inline=False)

        maximum = self.get_max_pages()
        if maximum > 1:
            embed.set_author(name=f'Page {menu.current_page + 1}/{maximum} ({len(self.entries)} commands)')

        embed.set_footer(text=f'Use "{self.prefix}help command" for more info on a command.')
        return embed

class HelpSelectMenu(discord.ui.Select['HelpMenu']):
    def __init__(self, entries: dict[commands.Cog, list[commands.Command]], bot: Krypton):
        super().__init__(
            placeholder='Select a category...',
            min_values=1,
            max_values=1,
            row=0,
        )
        self.commands: dict[commands.Cog, list[commands.Command]] = entries
        self.bot: Krypton = bot
        self.__fill_options()

    def __fill_options(self) -> None:
        self.add_option(
            label='Index',
            emoji='<Commands:1120667756300353638>',
            value='__index',
            description='The help page showing how to use the bot.',
        )
        for cog, command in self.commands.items():
            if (
                cog.qualified_name.upper() in display_cogs
                and command
                and len(cog.get_commands()) != 0
            ):
                description = cog.description.split('\n', 1)[0] or None
                # emoji = getattr(cog, 'display_emoji', None)
                # self.add_option(label=cog.qualified_name, value=cog.qualified_name, description=description, emoji=emoji)
                self.add_option(label=cog.qualified_name, value=cog.qualified_name, description=description)

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        value = self.values[0]
        if value == '__index':
            await self.view.rebind(FrontPageSource(), interaction)
        else:
            cog = self.bot.get_cog(value)
            if cog is None:
                await interaction.response.send_message('Somehow this category does not exist?', ephemeral=True)
                return

            commands = self.commands[cog]
            if not commands:
                await interaction.response.send_message('This category has no commands for you', ephemeral=True)
                return

            source = GroupHelpPageSource(cog, commands, prefix=self.view.ctx.clean_prefix)
            await self.view.rebind(source, interaction)


class FrontPageSource(menus.PageSource):
    def is_paginating(self) -> bool:
        # This forces the buttons to appear even in the front page
        return True

    def get_max_pages(self) -> Optional[int]:
        return 2

    async def get_page(self, page_number: int) -> Any:
        self.index = page_number
        return self

    def format_page(self, menu: HelpMenu, page: Any):
        embed = discord.Embed(title='Bot Help', colour=__import__('config').color)
        embed.description = inspect.cleandoc(
            f"""
            Hello! Welcome to the help page.

            Use "`{menu.ctx.clean_prefix}help <command>`" for more info on a command.
            Use "`{menu.ctx.clean_prefix}help <category>`" for more info on a category.
            Use the dropdown menu below to select a category.
        """
        )

        embed.add_field(
            name='Support Server',
            value='For more help, consider joining the official server over at https://discord.gg/vwpjsppbwx',
            inline=False,
        )

        created_at = format_dt(menu.ctx.bot.user.created_at, 'F')
        if self.index == 0:
            embed.add_field(
                name='Who am I?',
                value=(
                    "I'm a bot made by himangshu.147. I've been running since "
                    f'{created_at}. I have features such as moderation, music,  and more. You can get more '
                    'information on my commands by using the dropdown below.\n\n'
                ),
                inline=False,
            )
        elif self.index == 1:
            entries = (
                ('`<argument>`', 'This means the argument is **required**.'),
                ('`[argument]`', 'This means the argument is **optional**.'),
                ('`[A|B]`', 'This means that it can be **either A or B**.'),
                (
                    '[argument...]',
                    'This means you can have multiple arguments.\n'
                    'Now that you know the basics, it should be noted that...\n'
                    '**You do not type in the brackets!**',
                ),
            )

            embed.add_field(name='How do I use this bot?', value='Reading the bot signature is pretty simple.')

            for name, value in entries:
                embed.add_field(name=name, value=value, inline=False)

        return embed


class HelpMenu(Pages):
    def __init__(self, source: menus.PageSource, ctx: Context):
        super().__init__(source, ctx=ctx, compact=True)

    def add_categories(self, commands: dict[commands.Cog, list[commands.Command]]) -> None:
        self.clear_items()
        self.add_item(HelpSelectMenu(commands, self.ctx.bot))
        self.fill_items()

    async def rebind(self, source: menus.PageSource, interaction: discord.Interaction) -> None:
        self.source = source
        self.current_page = 0

        await self.source._prepare_once()
        page = await self.source.get_page(0)
        kwargs = await self._get_kwargs_from_page(page)
        self._update_labels(0)
        await interaction.response.edit_message(**kwargs, view=self)


class HelpCommand(commands.HelpCommand):
    context: Context
    def __init__(self):
        super().__init__(
            command_attrs={
                'cooldown': commands.CooldownMapping.from_cooldown(1, 3.0, commands.BucketType.member),
                'help': 'Shows help about the bot, a command, or a category',
                'aliases': ['he', 'commands', 'h', 'cmd', 'cmds'],
            }
        )

    async def on_help_command_error(self, ctx: Context, error: commands.CommandError):
        if isinstance(error, commands.CommandInvokeError):
            # Ignore missing permission errors
            if isinstance(error.original, discord.HTTPException) and error.original.code == 50013:
                return

            await ctx.send(str(error.original))

    def get_command_signature(self, command: commands.Command) -> str:
        parent = command.full_parent_name
        if len(command.aliases) > 0:
            aliases = '|'.join(command.aliases)
            fmt = f'[{command.name}|{aliases}]'
            if parent:
                fmt = f'{parent} {fmt}'
            alias = fmt
        else:
            alias = command.name if not parent else f'{parent} {command.name}'
        return f'{alias} {command.signature}'

    async def send_bot_help(self, mapping):
        bot = self.context.bot

        def key(command) -> str:
            cog = command.cog
            return cog.qualified_name if cog else '\U0010ffff'

        entries: list[commands.Command] = await self.filter_commands(bot.commands, sort=True, key=key)

        all_commands: dict[commands.Cog, list[commands.Command]] = {}
        for name, children in itertools.groupby(entries, key=key):
            if name == '\U0010ffff':
                continue

            cog = bot.get_cog(name)
            assert cog is not None
            all_commands[cog] = sorted(children, key=lambda c: c.qualified_name)

        menu = HelpMenu(FrontPageSource(), ctx=self.context)
        menu.add_categories(all_commands)
        await menu.start()

    async def send_cog_help(self, cog):
        entries = await self.filter_commands(cog.get_commands(), sort=True)
        menu = HelpMenu(GroupHelpPageSource(cog, entries, prefix=self.context.clean_prefix), ctx=self.context)
        await menu.start()

    def common_command_formatting(self, embed_like, command):
        embed_like.title = self.get_command_signature(command)
        if command.description:
            embed_like.description = f'{command.description or command.help}'
        else:
            embed_like.description = command.help or 'No help found...'

    async def send_command_help(self, command):
        # No pagination necessary for a single command.
        embed = discord.Embed(colour=__import__('config').color)
        self.common_command_formatting(embed, command)
        await self.context.send(embed=embed)

    async def send_group_help(self, group):
        subcommands = group.commands
        if len(subcommands) == 0:
            return await self.send_command_help(group)

        entries = await self.filter_commands(subcommands, sort=True)
        if len(entries) == 0:
            return await self.send_command_help(group)

        source = GroupHelpPageSource(group, entries, prefix=self.context.clean_prefix)
        self.common_command_formatting(source, group)
        menu = HelpMenu(source, ctx=self.context)
        await menu.start()

class Meta(commands.Cog):
    def __init__(self, bot: Krypton) -> None:
        self.bot = bot
        self.bot.help_command = None
        bot.help_command = HelpCommand()
        bot.help_command.cog = self

    async def cog_unload(self):
        self.bot.help_command = self.old_help_command


    @commands.hybrid_command()
    async def ping(self, ctx: Context):
        """Shows the bot's latency\n**Example**```k.ping```"""
        latency = round(self.bot.latency * 1000)
        await ctx.send(f'Pong! `{latency}ms`')

    @commands.hybrid_command()
    async def stats(self, ctx: Context):
        """Shows the bot's stats\n**Example**```k.stats```"""
        changes = get_latest_change()
        embed = discord.Embed(title=f"{self.bot.user.name}", color=self.bot.config.color)
        embed.description = (
            f"**Latest Changes**\n"
            f"[{(changes[0][:8])}]({changes[1]}) - {changes[2]} - [{changes[3]}](https://github.com/{changes[3]}) - <t:{int(changes[4])}:R>\n"
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.add_field(name="Guilds", value=format(len(self.bot.guilds), ",d"))
        embed.add_field(name="Users", value=format(len(self.bot.users), ",d"))
        embed.add_field(name="Uptime", value=F"<t:{int(self.bot.uptime)}:R>")
        embed.add_field(name="Version", value=f"{__version__}")
        embed.add_field(name="Python", value=f"v{platform.python_version()}")
        embed.add_field(name="discord.py", value=f"v{discord.__version__}")
        embed.set_footer(text=f"Made by {__author__} with ❤️")
        await ctx.send(embed=embed)
        
        