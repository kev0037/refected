import discord
from discord.ext import commands
import random
import os
from dotenv import load_dotenv
import pyfiglet
import aiohttp
import io
import requests
from colorama import init, Fore, Style
from googletrans import Translator
import requests
import json
import os
import asyncio
import html
import base64
import re

init(autoreset=True)

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.reactions = True
intents.members = True
#intents.message_content = True  # Needed for message content access
# ✅ DEFINE THIS BEFORE bot = commands.Bot(...)
def get_prefix(bot, message):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
    return prefixes.get(str(message.guild.id), prefixes["default"])

bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)


def command_category(category: str):
    def wrapper(func):
        func.help_category = category
        return func
    return wrapper

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            description=f"❌ Command not found: `{ctx.invoked_with}`",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return  # Prevents further error handling

    elif isinstance(error, commands.MissingPermissions):
        missing = ", ".join(error.missing_perms)
        embed = discord.Embed(
            title="❌ Missing Permissions",
            description=f"You don't have permission to run this command.\nMissing permission(s): `{missing}`.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="❌ Missing Argument",
            description=f"Please provide all required arguments for this command.\nUsage: `{ctx.prefix}{ctx.command} {ctx.command.signature}`",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)

    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            title="❌ Invalid Argument",
            description="One or more arguments are invalid or of the wrong type.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)

    else:
        embed = discord.Embed(
            title="❌ Error",
            description=f"An unexpected error occurred:\n```py\n{str(error)}\n```",
            color=discord.Color.dark_red()
        )
        await ctx.send(embed=embed)
        raise error  # Keep this if you want to see traceback in console


def print_active_message(bot_user):
    print(Fore.GREEN + Style.BRIGHT + "╔══════════════════════════════╗")
    print(Fore.GREEN + Style.BRIGHT + f"║  Bot is ACTIVE! Logged in as ║")
    print(Fore.GREEN + Style.BRIGHT + f"║        {bot_user}          ║")
    print(Fore.GREEN + Style.BRIGHT + "╚══════════════════════════════╝")

@bot.event
async def on_ready():
    print_active_message(bot.user)
    stream = discord.Streaming(name="!help", url="https://twitch.tv/raydoncc")
    await bot.change_presence(activity=stream)

auto_react_map = {}

# Storage for snipes, edits, removed reactions
snipe_data = {}
edited_messages = {}
removed_reactions = {}


@bot.command(name="help", aliases=["h"])
@command_category("Help")
async def help_command(ctx, *, command_name=None):
    if command_name:
        command = bot.get_command(command_name)
        if command:
            embed = discord.Embed(
                title=f"Help for `{command.name}`",
                color=discord.Color.blue()
            )
           
            embed.add_field(
                name="Usage",
                value=f"`{ctx.prefix}{command.name} {command.signature}`",
                inline=False
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"No command named '{command_name}' found.")
        return

    # Group commands by category
    categories = {}
    for command in bot.commands:
        if command.hidden:
            continue
        category = getattr(command.callback, 'help_category', "Uncategorized")
        categories.setdefault(category, []).append(command)

    embed = discord.Embed(
        title="📜 Help - Command Categories",
        color=discord.Color.blue()
    )

    for category, cmds in sorted(categories.items()):
        command_list = " | ".join(f"`{cmd.name}`" for cmd in sorted(cmds, key=lambda c: c.name))
        embed.add_field(
            name=f"📂 {category}",
            value=command_list,
            inline=False
        )

    embed.set_footer(text="Use !help <command> for detailed info.")
    await ctx.send(embed=embed)

@bot.command()
@command_category("Moderation")
async def react(ctx, user: discord.Member, emoji):
    auto_react_map[user.id] = emoji
    await ctx.send(embed=discord.Embed(description=f"Started auto-reacting to messages from {user.display_name} with {emoji}.", color=discord.Color.green()))

@bot.command(aliases=['reactstop', 'autoreactend'])
@command_category("Moderation")
async def reactend(ctx):
    auto_react_map.clear()
    await ctx.send(embed=discord.Embed(description="Stopped all auto reactions.", color=discord.Color.green()))

@bot.command(aliases=['fb', 'fem'])
@command_category("Fun")
async def femboy(ctx, member: discord.Member = None):
    member = member or ctx.author
    percentage = random.randint(0, 100)
    embed = discord.Embed(description=f"🌸 {member.mention} is **{percentage}%** femboy! 🌸", color=discord.Color.magenta())
    await ctx.send(embed=embed)

@bot.command()
@command_category("Fun")
async def ping(ctx):
    latency = bot.latency * 1000  # seconds to ms
    embed = discord.Embed(title="Ping!", description=f"Latency: {latency:.2f} ms", color=discord.Color.green())
    await ctx.send(embed=embed)

@bot.command(aliases=['members', 'mc'])
@command_category("Info")
async def membercount(ctx):
    guild = ctx.guild
    total_members = guild.member_count
    humans = sum(1 for m in guild.members if not m.bot)
    bots = total_members - humans

    embed = discord.Embed(color=discord.Color.blue())
    embed.set_author(name=f"{guild.name} Statistics", icon_url=guild.icon_url)
    embed.add_field(name="Users", value=str(total_members), inline=True)
    embed.add_field(name="Humans", value=str(humans), inline=True)
    embed.add_field(name="Bots", value=str(bots), inline=True)

    await ctx.send(embed=embed)


@bot.command()
@command_category("Fun")
async def black(ctx, member: discord.Member = None):
    member = member or ctx.author
    percentage = random.randint(0, 100)
    embed = discord.Embed(description=f"🖤 {member.mention} is **{percentage}%** black! 🖤", color=discord.Color.dark_grey())
    await ctx.send(embed=embed)

@bot.command()
@command_category("Fun")
async def cuck(ctx, member: discord.Member = None):
    member = member or ctx.author
    percentage = random.randint(0, 100)
    embed = discord.Embed(description=f"🍆 {member.mention} is **{percentage}%** cuck! 🍆", color=discord.Color.red())
    await ctx.send(embed=embed)

@bot.command()
@command_category("Fun")
async def compliment(ctx, member: discord.Member = None):
    compliments = [
        "You're awesome!",
        "You have a great sense of humor!",
        "Your positivity is infectious.",
        "You're a smart cookie!",
        "You're a ray of sunshine!",
        "You have a magnetic personality that draws people in.",
        "Your wisdom is beyond your years.",
        "You always know how to make someone feel special.",
        "You're a breath of fresh air.",
        "Your energy lights up the darkest days.",
        "You have a smile that could brighten anyone's day.",
        "Your presence is calming and reassuring.",
        "You’re a natural leader.",
        "You make hard things look easy.",
        "Your enthusiasm is inspiring.",
        "You have an amazing way with words.",
         "You radiate confidence and grace.",
        "You’re the kind of person everyone wishes they knew.",
        "Your optimism is truly contagious.",
        "You have a heart full of compassion.",
    ]
    member = member or ctx.author
    embed = discord.Embed(description=f"{member.mention}, {random.choice(compliments)}", color=discord.Color.blue())
    await ctx.send(embed=embed)

@bot.command()
@command_category("Fun")
async def hug(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(description=f"🤗 {ctx.author.mention} hugs {member.mention}!", color=discord.Color.gold())
    await ctx.send(embed=embed)


@bot.command()
@command_category("Fun")
async def ship(ctx, member1: discord.Member, member2: discord.Member):
    try:
        percentage = random.randint(0, 100)
        embed = discord.Embed(description=f"❤️ Shipping {member1.display_name} and {member2.display_name}: **{percentage}%** compatible!", color=discord.Color.red())
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Something went wrong: {e}")

@bot.command(aliases=['gay'])
@command_category("Fun")
async def gayrate(ctx, member: discord.Member = None):
    member = member or ctx.author
    percentage = random.randint(0, 100)
    embed = discord.Embed(description=f"🏳️‍🌈 {member.mention} is **{percentage}%** gay! 🏳️‍🌈", color=discord.Color.purple())
    await ctx.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Auto react if set
    emoji = auto_react_map.get(message.author.id)
    if emoji:
        try:
            await message.add_reaction(emoji)
        except Exception as e:
            print(f"Failed to add reaction: {e}")

    await bot.process_commands(message)

# Sniping deleted messages
@bot.event
async def on_message_delete(message):
    if message.author.bot or not message.content:
        return
    channel_id = message.channel.id
    snipe_data.setdefault(channel_id, [])
    snipe_data[channel_id].insert(0, {
        "content": message.content,
        "author": str(message.author),
        "time": message.created_at.strftime("%Y-%m-%d %H:%M:%S")
    })
    if len(snipe_data[channel_id]) > 10:
        snipe_data[channel_id].pop()

# Edited messages tracking
@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content:
        return
    channel_id = before.channel.id
    edited_messages.setdefault(channel_id, [])
    edited_messages[channel_id].insert(0, {
        "author": str(before.author),
        "before": before.content,
        "after": after.content,
        "time": before.edited_at.strftime("%Y-%m-%d %H:%M:%S") if before.edited_at else "Unknown time"
    })
    if len(edited_messages[channel_id]) > 10:
        edited_messages[channel_id].pop()

# Removed reactions tracking
@bot.event
async def on_reaction_remove(reaction, user):
    if user.bot:
        return
    channel_id = reaction.message.channel.id
    removed_reactions.setdefault(channel_id, [])
    removed_reactions[channel_id].insert(0, {
        "user": str(user),
        "emoji": str(reaction.emoji),
        "message_content": reaction.message.content or "No content",
        "time": reaction.message.created_at.strftime("%Y-%m-%d %H:%M:%S")
    })
    if len(removed_reactions[channel_id]) > 10:
        removed_reactions[channel_id].pop()

# !s - show sniped messages
@bot.command()
@command_category("Sniping")
async def s(ctx, index: int = 1):
    channel_id = ctx.channel.id
    snipes = snipe_data.get(channel_id)
    if not snipes:
        await ctx.send(embed=discord.Embed(description="❌ No messages to snipe in this channel.", color=discord.Color.red()))
        return
    if index < 1 or index > len(snipes):
        await ctx.send(embed=discord.Embed(description=f"⚠️ Only {len(snipes)} snipes available.", color=discord.Color.orange()))
        return
    snipe = snipes[index - 1]
    embed = discord.Embed(title=f"💬 Sniped Message #{index}", description=snipe["content"], color=discord.Color.purple())
    embed.set_footer(text=f"Author: {snipe['author']} • Sent at {snipe['time']}")
    await ctx.send(embed=embed)

# !cs - clear all snipes in channel
@bot.command()
@command_category("Sniping")
async def cs(ctx):
    channel_id = ctx.channel.id
    if channel_id in snipe_data:
        del snipe_data[channel_id]
        await ctx.send(embed=discord.Embed(description="🧹 Cleared all sniped messages in this channel.", color=discord.Color.green()))
    else:
        await ctx.send(embed=discord.Embed(description="❌ Nothing to clear.", color=discord.Color.red()))

# !es - show last edited message
@bot.command()
@command_category("Sniping")
async def es(ctx, index: int = 1):
    channel_id = ctx.channel.id
    edits = edited_messages.get(channel_id)
    if not edits:
        await ctx.send(embed=discord.Embed(description="❌ No edited messages in this channel.", color=discord.Color.red()))
        return
    if index < 1 or index > len(edits):
        await ctx.send(embed=discord.Embed(description=f"⚠️ Only {len(edits)} edited messages available.", color=discord.Color.orange()))
        return
    edit = edits[index - 1]
    embed = discord.Embed(title=f"✏️ Edited Message #{index}", color=discord.Color.blue())
    embed.add_field(name="Author", value=edit["author"], inline=False)
    embed.add_field(name="Before", value=edit["before"] or "No content", inline=False)
    embed.add_field(name="After", value=edit["after"] or "No content", inline=False)
    embed.set_footer(text=f"Edited at {edit['time']}")
    await ctx.send(embed=embed)

# !rs - show last removed reaction
@bot.command()
@command_category("Sniping")
async def rs(ctx, index: int = 1):
    channel_id = ctx.channel.id
    reacts = removed_reactions.get(channel_id)
    if not reacts:
        await ctx.send(embed=discord.Embed(description="❌ No removed reactions in this channel.", color=discord.Color.red()))
        return
    if index < 1 or index > len(reacts):
        await ctx.send(embed=discord.Embed(description=f"⚠️ Only {len(reacts)} removed reactions available.", color=discord.Color.orange()))
        return
    react = reacts[index - 1]
    embed = discord.Embed(title=f"❌ Removed Reaction #{index}", color=discord.Color.dark_red())
    embed.add_field(name="User", value=react["user"], inline=False)
    embed.add_field(name="Emoji", value=react["emoji"], inline=False)
    embed.add_field(name="Message", value=react["message_content"], inline=False)
    embed.set_footer(text=f"Message sent at {react['time']}")
    await ctx.send(embed=embed)


@bot.command(aliases=['si', 'guildinfo'])
@command_category("Info")
async def serverinfo(ctx):
    guild = ctx.guild
    
    # Icon URL with gif support
    icon_url = guild.icon_url_as(format='gif') if guild.icon and str(guild.icon).startswith("a_") else guild.icon_url_as(format='png') if guild.icon else None
    
    # Owner name (fetching guild owner can be async, so await)
    owner = await guild.fetch_member(guild.owner_id)
    
    # Count members by type
    total_members = guild.member_count
    bots = sum(1 for m in guild.members if m.bot)
    humans = total_members - bots
    
    # Verification level readable name
    verification = str(guild.verification_level).replace('_', ' ').title()
    
    # Boost info
    boosts = guild.premium_subscription_count
    boost_level = guild.premium_tier
    
    # Splash, Banner URLs (may be None)
    splash_url = guild.splash_url if guild.splash else "N/A"
    banner_url = guild.banner_url if guild.banner else "N/A"
    
    # Channel counts
    text_channels = len(guild.text_channels)
    voice_channels = len(guild.voice_channels)
    categories = len(guild.categories)
    
    # Roles and emojis count
    roles_count = len(guild.roles)
    emojis_count = len(guild.emojis)
    boosters_count = sum(1 for m in guild.members if m.premium_since)
    
    embed = discord.Embed(color=discord.Color(int("35383b", 16)))
    
    embed.set_author(name=f"{owner.display_name}", icon_url=owner.avatar_url)
    embed.title = guild.name
    embed.description = (
        f"Server created on <t:{int(guild.created_at.timestamp())}:D> "
        f"(<t:{int(guild.created_at.timestamp())}:R>)\n"
        f"__{guild.name}__ is on bot shard ID: **{ctx.guild.shard_id}/{bot.shard_count}**"
    )
    
    embed.set_footer(text=f"Guild ID: {guild.id}")
    
    if icon_url:
        embed.set_thumbnail(url=str(icon_url))
    
    embed.add_field(name="Owner", value=str(owner), inline=True)
    embed.add_field(
        name="Members",
        value=f"**Total**: {total_members}\n**Humans**: {humans}\n**Bots**: {bots}",
        inline=True,
    )
    embed.add_field(
        name="Information",
        value=f"**Verification**: {verification}\n**Boosts**: {boosts} (level {boost_level})",
        inline=True,
    )
    embed.add_field(
        name="Design",
        value=(
            f"**Splash**: [{('Click here' if splash_url != 'N/A' else 'N/A')}]({splash_url})\n"
            f"**Banner**: [{('Click here' if banner_url != 'N/A' else 'N/A')}]({banner_url})\n"
            f"**Icon**: [Click here]({icon_url})"
        ),
        inline=True,
    )
    embed.add_field(
        name=f"Channels ({text_channels + voice_channels + categories})",
        value=f"**Text**: {text_channels}\n**Voice**: {voice_channels}\n**Category**: {categories}",
        inline=True,
    )
    embed.add_field(
        name="Counts",
        value=f"**Roles**: {roles_count}\n**Emojis**: {emojis_count}\n**Boosters**: {boosters_count}",
        inline=True,
    )
    
    embed.timestamp = guild.created_at
    
    await ctx.send(embed=embed)


@bot.command()
@command_category("Fun")
async def quote(ctx):
    quotes = [
        "Life is what happens when you're busy making other plans. — John Lennon",
        "Be yourself; everyone else is already taken. — Oscar Wilde",
        "The only way to do great work is to love what you do. — Steve Jobs",
        "Success is not how high you have climbed, but how you make a positive difference to the world. — Roy T. Bennett",
        "In the middle of every difficulty lies opportunity. — Albert Einstein",
         "Believe you can and you're halfway there. – Theodore Roosevelt",
    "The only way to do great work is to love what you do. – Steve Jobs",
    "Success is not final, failure is not fatal: It is the courage to continue that counts. – Winston Churchill",
    "In the middle of every difficulty lies opportunity. – Albert Einstein",
    "Happiness is not something ready made. It comes from your own actions. – Dalai Lama",
    "Don't watch the clock; do what it does. Keep going. – Sam Levenson",
    "The best time to plant a tree was 20 years ago. The second best time is now. – Chinese Proverb",
    "You miss 100 of the shots you don’t take. – Wayne Gretzky",
    "Dream big and dare to fail. – Norman Vaughan",
    "What lies behind us and what lies before us are tiny matters compared to what lies within us. – Ralph Waldo Emerson",
    "Do what you can, with what you have, where you are. – Theodore Roosevelt",
    "Act as if what you do makes a difference. It does. – William James",
    "Success usually comes to those who are too busy to be looking for it. – Henry David Thoreau",
    "Keep your face always toward the sunshine—and shadows will fall behind you. – Walt Whitman",
    "It does not matter how slowly you go as long as you do not stop. – Confucius"

    ]
    embed = discord.Embed(title="Random Quote", description=random.choice(quotes), color=discord.Color.gold())
    await ctx.send(embed=embed)

@bot.command(aliases=['purge', 'c'])
@command_category("Moderation")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, target):
    deleted = []
    if target.isdigit():
        # target is a number: delete that many messages
        amount = int(target)
        deleted = await ctx.channel.purge(limit=amount)
        description = f"🧹 Cleared {len(deleted)} messages."
    else:
        # Try to get the member from mention or name
        user = None
        if ctx.message.mentions:
            user = ctx.message.mentions[0]
        else:
            user = discord.utils.get(ctx.guild.members, name=target)

        if not user:
            return await ctx.send("❌ Could not find that user.")

        def check(m):
            return m.author == user

        deleted = await ctx.channel.purge(limit=100, check=check)
        description = f"🧹 Cleared {len(deleted)} messages from {user.display_name}."

    embed = discord.Embed(
        description=description,
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed, delete_after=5)


@bot.command()
@command_category("Fun")
async def kiss(ctx, member: discord.Member):
    kiss_gifs = [
        "https://media.giphy.com/media/G3va31oEEnIkM/giphy.gif",
        "https://media.giphy.com/media/FqBTvSNjNzeZG/giphy.gif",
        "https://media.giphy.com/media/bGm9FuBCGg4SY/giphy.gif",
        "https://media.giphy.com/media/nyGFcsP0kAobm/giphy.gif"
    ]
    gif = random.choice(kiss_gifs)
    embed = discord.Embed(
        description=f"{ctx.author.mention} kissed {member.mention} 💋",
        color=discord.Color.from_rgb(255, 105, 180)  # hot pink color
    )
    embed.set_image(url=gif)
    await ctx.send(embed=embed)




import aiohttp
import discord
from discord.ext import commands

@bot.command(name='meme')
@command_category("Fun")
async def meme(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://meme-api.com/gimme') as response:
            if response.status != 200:
                await ctx.send("Couldn't fetch a meme right now. Try again later.")
                return
            meme = await response.json()

    embed = discord.Embed(color=discord.Color.random())
    embed.set_image(url=meme.get('url'))

    await ctx.send(embed=embed)
    print("[+] MEME COMMAND USED")

@bot.command(aliases=['asc'])
@command_category("Fun")
async def ascii(ctx, *, text: str):
    ascii_art = pyfiglet.figlet_format(text)
    if len(ascii_art) > 2000:
        await ctx.send("The ASCII art is too large to send in one message.")
    else:
        await ctx.send(f"```\n{ascii_art}\n```")


@bot.command(aliases=["phc"])
@command_category("Fun")
async def phcomment(ctx, user: discord.User = None, *, args=None):
    if user is None or args is None:
        await ctx.send(f'[ERROR]: Invalid input! Command: phcomment <user> <message>')
        return

    avatar_url = user.avatar_url_as(format="png")

    endpoint = f"https://nekobot.xyz/api/imagegen?type=phcomment&text={args}&username={user.name}&image={avatar_url}"
    r = requests.get(endpoint)
    res = r.json()

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(res["message"]) as resp:
                image = await resp.read()
        with io.BytesIO(image) as file:
            await ctx.send(file=discord.File(file, f"{user.name}_pornhub_comment.png"))
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")
    
@bot.command()
@command_category("Fun")
async def pp(ctx, member: commands.MemberConverter = None):
    member = member or ctx.author
    inches = random.randint(1, 12)
    size_visual = "8" + "=" * inches + "D"
    embed = discord.Embed(
        title=f"{member.display_name}'s PP Size",
        description=f"`{size_visual}` ({inches} inches)",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@bot.command(aliases=['av'])
@command_category("Info")
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    if member.is_avatar_animated():
        avatar_url = member.avatar_url_as(format='gif')
    else:
        avatar_url = member.avatar_url_as(format='png')
    embed = discord.Embed(
        title=f"{member.display_name}'s Avatar",
        color=discord.Color.blue()
    )
    embed.set_image(url=str(avatar_url))
    await ctx.send(embed=embed)

translator = Translator()

from googletrans import LANGUAGES  # import this at the top of your file

@bot.command()
@command_category("Info")
async def tr(ctx, *, text: str = None):
    try:
        if text is None:
            if ctx.message.reference and ctx.message.reference.resolved:
                replied_msg = ctx.message.reference.resolved
                text = replied_msg.content
            else:
                return await ctx.send("❌ Please provide text to translate or reply to a message.")

        translated = translator.translate(text, dest='en')
        source_code = translated.src.lower()
        source_lang = LANGUAGES.get(source_code, "Unknown").title()

        embed = discord.Embed(
            title=f"Translated from {source_lang} to English",
            description=f"```{translated.text}```",
            color=discord.Color.green()
        )
        embed.set_author(
            name=ctx.author.display_name,
            icon_url=ctx.author.avatar_url  # Works in discord.py v1.x
        )
        embed.set_footer(
            text="Google Translate",
            icon_url="https://bleed.bot/img/google.png"
        )

        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Error translating text: {e}")


@bot.command()
@command_category("Info")
async def define(ctx, *, word: str):
    try:
        response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
        data = response.json()
        if isinstance(data, list):
            definition = data[0]['meanings'][0]['definitions'][0]['definition']
            embed = discord.Embed(title=f"Definition of '{word}'", description=definition, color=discord.Color.blue())
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ No definition found for '{word}'.")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@bot.command()
@command_category("Info")
async def crypto(ctx, symbol: str):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            if symbol.lower() not in data:
                return await ctx.send(" Cryptocurrency not found.")
    price = data[symbol.lower()]['usd']
    embed = discord.Embed(title=f"{symbol.upper()} Price", description=f"${price}", color=discord.Color.gold())
    await ctx.send(embed=embed)

@bot.command()
@command_category("Info")
async def weather(ctx, *, city: str):
    url = f"https://wttr.in/{city}?format=j1"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return await ctx.send(embed=discord.Embed(description="❌ Could not get weather info.", color=discord.Color.red()))
            data = await resp.json()
    current_condition = data["current_condition"][0]
    desc = current_condition["weatherDesc"][0]["value"]
    temp_c = current_condition["temp_C"]
    humidity = current_condition["humidity"]
    wind_kph = current_condition["windspeedKmph"]

    embed = discord.Embed(title=f"Weather in {city.title()}", color=discord.Color.blue())
    embed.add_field(name="Condition", value=desc, inline=True)
    embed.add_field(name="Temperature", value=f"{temp_c}°C", inline=True)
    embed.add_field(name="Humidity", value=f"{humidity}%", inline=True)
    embed.add_field(name="Wind Speed", value=f"{wind_kph} km/h", inline=True)
    await ctx.send(embed=embed)

@bot.command()
@command_category("Info")
async def iplookup(ctx, ip: str):
    url = f"http://ip-api.com/json/{ip}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return await ctx.send(embed=discord.Embed(description=" Could not get IP info.", color=discord.Color.red()))
            data = await resp.json()
    
    if data["status"] != "success":
        return await ctx.send(embed=discord.Embed(description=" Invalid IP or no data found.", color=discord.Color.red()))
    
    embed = discord.Embed(title=f"IP Lookup: {ip}", color=discord.Color.blue())
    embed.add_field(name="Country", value=data.get("country", "N/A"), inline=True)
    embed.add_field(name="Region", value=data.get("regionName", "N/A"), inline=True)
    embed.add_field(name="City", value=data.get("city", "N/A"), inline=True)
    embed.add_field(name="ISP", value=data.get("isp", "N/A"), inline=False)
    embed.add_field(name="Org", value=data.get("org", "N/A"), inline=False)
    embed.add_field(name="Timezone", value=data.get("timezone", "N/A"), inline=True)
    embed.add_field(name="ZIP", value=data.get("zip", "N/A"), inline=True)
    embed.add_field(name="Lat/Lon", value=f"{data.get('lat', 'N/A')}, {data.get('lon', 'N/A')}", inline=True)

    await ctx.send(embed=embed)


@bot.command()
@command_category("Moderation")
@commands.has_permissions(manage_messages=True)
async def bc(ctx):
    def is_bot(m):
        return m.author.bot  # checks if the author is any bot

    deleted = await ctx.channel.purge(check=is_bot)
    embed = discord.Embed(
        title="Bot Messages Cleared",
        description=f"Cleared {len(deleted)} bot messages.",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed, delete_after=5)



@bot.command()
@command_category("Moderation")
@commands.has_permissions(manage_nicknames=True)
async def nick(ctx, member: discord.Member, *, new_nick: str = None):
    try:
        if new_nick:
            await member.edit(nick=new_nick)
            embed = discord.Embed(
                description=f"✅ Changed nickname of {member.mention} to **{new_nick}**.",
                color=discord.Color.green()
            )
        else:
            await member.edit(nick=None)
            embed = discord.Embed(
                description=f"✅ Removed nickname of {member.mention}.",
                color=discord.Color.orange()
            )
        await ctx.send(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(
            description="❌ I don't have permission to change that nickname.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            description=f"❌ An error occurred: {e}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

#LF COMMANDS

LASTFM_API_KEY = "6182206853dcf843d52c8bb40132d9aa"

# Simple in-memory store, replace with DB/file for persistence
lastfm_users = {}
LASTFM_LINKS_FILE = "lastfm_users.json"

# Load linked users from file
def load_lastfm_users():
    if os.path.exists(LASTFM_LINKS_FILE):
        with open(LASTFM_LINKS_FILE, "r") as f:
            return json.load(f)
    return {}

# Save linked users to file
def save_lastfm_users(data):
    with open(LASTFM_LINKS_FILE, "w") as f:
        json.dump(data, f, indent=4)

lastfm_users = load_lastfm_users()

@bot.command(aliases=["lflogin"])
@command_category("Last.fm")
async def linklf(ctx, lastfm_username: str):
    """Link your Discord user to a Last.fm username."""
    lastfm_users[str(ctx.author.id)] = lastfm_username
    save_lastfm_users(lastfm_users)
    await ctx.send(f"Linked your Discord account to Last.fm user `{lastfm_username}`.")

@bot.command(aliases=["fm", "np"])
@command_category("Last.fm")
async def lf(ctx, member: discord.Member = None):
    """Show currently playing or last played track from Last.fm with styled embed."""
    member = member or ctx.author
    discord_id = str(member.id)

    if discord_id not in lastfm_users:
        return await ctx.send(f"{member.display_name} has not linked their Last.fm username. Use `!linklf <username>` to link it.")

    username = lastfm_users[discord_id]

    try:
        # Get recent track
        recent_url = (
            f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks"
            f"&user={username}&api_key={LASTFM_API_KEY}&format=json&limit=1"
        )
        recent = requests.get(recent_url).json()
        track = recent["recenttracks"]["track"][0]

        song = track["name"]
        artist = track["artist"]["#text"]
        album = track.get("album", {}).get("#text", "Unknown album")
        album_art = track.get("image", [])[-1]["#text"] if track.get("image") else None
        now_playing = track.get("@attr", {}).get("nowplaying") == "true"

        # Get track info (playcount)
        track_info_url = (
            f"http://ws.audioscrobbler.com/2.0/?method=track.getInfo"
            f"&api_key={LASTFM_API_KEY}&artist={artist}&track={song}"
            f"&username={username}&format=json"
        )
        track_info = requests.get(track_info_url).json()
        user_playcount = track_info.get("track", {}).get("userplaycount", "0")
        track_url = track_info.get("track", {}).get("url", "https://www.last.fm")

        # Get artist info (total scrobbles)
        artist_info_url = (
            f"http://ws.audioscrobbler.com/2.0/?method=artist.getInfo"
            f"&artist={artist}&username={username}&api_key={LASTFM_API_KEY}&format=json"
        )
        artist_info = requests.get(artist_info_url).json()
        total_scrobbles = artist_info.get("artist", {}).get("stats", {}).get("userplaycount", "0")
        artist_url = artist_info.get("artist", {}).get("url", "https://www.last.fm")

        # Get user info (avatar)
        user_info_url = (
            f"http://ws.audioscrobbler.com/2.0/?method=user.getinfo"
            f"&user={username}&api_key={LASTFM_API_KEY}&format=json"
        )
        user_info = requests.get(user_info_url).json()
        lastfm_avatar = user_info.get("user", {}).get("image", [])[-1]["#text"]

        # Build embed
        embed = discord.Embed(color=discord.Color.red())
        embed.set_author(
            name=f"Last.fm: {username}",
            icon_url=lastfm_avatar,
            url=f"https://www.last.fm/user/{username}"
        )
        embed.add_field(
            name="**Track**",
            value=f"[{song}]({track_url})",
            inline=True
        )
        embed.add_field(
            name="**Artist**",
            value=f"[{artist}]({artist_url})",
            inline=True
        )
        embed.set_thumbnail(url=album_art)
        embed.set_footer(text=f"Playcount: {user_playcount} ∙ Total Scrobbles: {total_scrobbles} ∙ Album: {album}")

        message = await ctx.send(embed=embed)
        await message.add_reaction("👍")
        await message.add_reaction("👎")

    except Exception as e:
        await ctx.send(f"❌ An error occurred while fetching Last.fm data for `{username}`.")
        print(f"[Last.fm] Error: {e}")


from urllib.parse import quote_plus

@bot.command(aliases=["lfttt"])
@command_category("Last.fm")
async def toptracks(ctx, member: discord.Member = None):
    """Show all-time top 10 tracks for a linked user."""
    member = member or ctx.author
    discord_id = str(member.id)
    if discord_id not in lastfm_users:
        await ctx.send(f"{member.display_name} has not linked their Last.fm username. Use `!linklf <username>`.") 
        return

    username = lastfm_users[discord_id]
    url = (
        f"http://ws.audioscrobbler.com/2.0/?method=user.gettoptracks"
        f"&user={username}&period=overall&limit=10&api_key={LASTFM_API_KEY}&format=json"
    )
    resp = requests.get(url)
    data = resp.json()
    tracks = data.get('toptracks', {}).get('track', [])

    if not tracks:
        await ctx.send(f"No top tracks found for `{username}`.")
        return

    description_lines = []
    for i, track in enumerate(tracks, start=1):
        name = track.get('name')
        artist = track.get('artist', {}).get('name')
        playcount = track.get('playcount')
        track_encoded = quote_plus(name)
        artist_encoded = quote_plus(artist)
        track_url = f"https://www.last.fm/music/{artist_encoded}/_/{track_encoded}"
        line = f"`{i}` **[{name}]({track_url})** by **{artist}** ({int(playcount):,} plays)"
        description_lines.append(line)

    description = "\n".join(description_lines)

    embed = discord.Embed(
        title=f"{member.display_name}'s overall top tracks",
        description=description,
        color=discord.Color.purple()
    )
    # older discord.py avatar access
    embed.set_author(name=member.display_name, icon_url=str(member.avatar_url) if member.avatar else str(member.default_avatar_url))

    await ctx.send(embed=embed)


@bot.command()
@command_category("Last.fm")
async def scrobbles(ctx, member: discord.Member = None):
    """Show total scrobbles for a user in an embed."""
    member = member or ctx.author
    discord_id = str(member.id)
    if discord_id not in lastfm_users:
        await ctx.send(f"{member.display_name} has not linked their Last.fm username. Use `!linklf <username>`.")
        return
    
    username = lastfm_users[discord_id]
    url = (
        f"http://ws.audioscrobbler.com/2.0/?method=user.getinfo"
        f"&user={username}&api_key={LASTFM_API_KEY}&format=json"
    )
    resp = requests.get(url)
    data = resp.json()
    user_data = data.get('user')
    
    if not user_data:
        await ctx.send(f"Could not find Last.fm user `{username}`.")
        return
    
    playcount = user_data.get('playcount', '0')
    
    embed = discord.Embed(
        title=f"Last.fm Scrobbles for {member.display_name}",
        description=f"Linked Last.fm user: `{username}`",
        color=discord.Color.gold()
    )
    embed.add_field(name="Total Scrobbles", value=playcount)
    await ctx.send(embed=embed)

@bot.command(aliases=["topartist", "lfta"])
@command_category("Last.fm")
async def topartists(ctx, member: discord.Member = None):
    """Show all-time top artists for a linked user."""
    member = member or ctx.author
    discord_id = str(member.id)

    if discord_id not in lastfm_users:
        embed = discord.Embed(
            title="❌ Not Linked",
            description=f"`{member.display_name}` has not linked their Last.fm username.\nUse `!linklf <username>`.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    username = lastfm_users[discord_id]
    url = (
        f"http://ws.audioscrobbler.com/2.0/?method=user.gettopartists"
        f"&user={username}&period=overall&limit=10&api_key={LASTFM_API_KEY}&format=json"
    )

    try:
        resp = requests.get(url)
        data = resp.json()
        artists = data.get('topartists', {}).get('artist', [])
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description=f"Failed to fetch data from Last.fm:\n```{str(e)}```",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    if not artists:
        embed = discord.Embed(
            title="No Top Artists",
            description=f"No top artists found for `{username}`.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Build the track list
    description = ""
    for i, artist in enumerate(artists, start=1):
        name = artist.get('name')
        playcount = artist.get('playcount')
        artist_url = artist.get('url')
        description += f"`{i}` **[{name}]({artist_url})** ({playcount} plays)\n"

    # Embed construction
    embed = discord.Embed(
        title=f"{member.display_name}'s overall top artists",
        description=description,
        color=discord.Color.dark_magenta()
    )
    embed.set_author(
        name=ctx.author.display_name,
        icon_url=ctx.author.avatar_url  # Use .avatar.url for discord.py 2.x
    )

    await ctx.send(embed=embed)

@bot.command(aliases=["lfai"])
@command_category("Last.fm")
async def artistinfo(ctx, *, artist_name: str):
    """Show info about an artist, including user playcount and user's unique track count if possible."""
    discord_id = str(ctx.author.id)
    if discord_id not in lastfm_users:
        await ctx.send("Link your Last.fm account with `!linklf <username>` first.")
        return
    
    username = lastfm_users[discord_id]

    # Get artist info with user playcount
    url = (
        f"http://ws.audioscrobbler.com/2.0/?method=artist.getinfo"
        f"&artist={artist_name}&username={username}&api_key={LASTFM_API_KEY}&format=json"
    )
    resp = requests.get(url)
    data = resp.json()

    if 'error' in data:
        await ctx.send(f"Artist `{artist_name}` not found.")
        return

    artist = data['artist']
    bio = artist.get('bio', {}).get('summary', 'No bio available').split('<a')[0]
    user_playcount = int(artist.get('stats', {}).get('userplaycount', 0))
    listeners = artist.get('stats', {}).get('listeners', 'Unknown')  # global listeners, fallback
    image = artist.get('image', [])[-1]['#text'] if artist.get('image') else None

    embed = discord.Embed(title=f"Artist Info: {artist['name']}", description=bio, color=discord.Color.green())
    embed.add_field(name="User Playcount (total plays)", value=str(user_playcount))
    if image:
        embed.set_thumbnail(url=image)

    await ctx.send(embed=embed)

from datetime import datetime

@bot.command(aliases=["lfus"])
@command_category("Last.fm")
async def userstats(ctx, member: discord.Member = None):
    """Show overall Last.fm stats for a linked user, including profile picture."""
    member = member or ctx.author
    discord_id = str(member.id)
    if discord_id not in lastfm_users:
        await ctx.send(f"{member.display_name} has not linked their Last.fm username. Use `!linklf <username>`.")
        return

    username = lastfm_users[discord_id]
    url = (
        f"http://ws.audioscrobbler.com/2.0/?method=user.getinfo"
        f"&user={username}&api_key={LASTFM_API_KEY}&format=json"
    )
    resp = requests.get(url)
    data = resp.json()

    if 'error' in data:
        await ctx.send(f"Could not fetch stats for `{username}`.")
        return

    user_info = data.get('user', {})
    playcount = user_info.get('playcount', 'Unknown')
    artist_count = user_info.get('artist_count', 'Unknown')
    album_count = user_info.get('album_count', 'Unknown')
    track_count = user_info.get('track_count', 'Unknown')

    registered_ts = int(user_info.get('registered', {}).get('unixtime', 0))
    if registered_ts > 0:
        registered_date = datetime.utcfromtimestamp(registered_ts).strftime('%Y-%m-%d')
    else:
        registered_date = "Unknown"

    # Get profile image URL
    images = user_info.get('image', [])
    pfp_url = images[-1]['#text'] if images and images[-1]['#text'] else None

    embed = discord.Embed(title=f"Last.fm Stats for {member.display_name}", color=discord.Color.gold())
    embed.add_field(name="Total Scrobbles", value=playcount)
    embed.add_field(name="Unique Artists", value=artist_count)
    embed.add_field(name="Unique Albums", value=album_count)
    embed.add_field(name="Unique Tracks", value=track_count)
    embed.add_field(name="Registered Since", value=registered_date, inline=False)

    if pfp_url:
        embed.set_thumbnail(url=pfp_url)

    await ctx.send(embed=embed)



#------------------ NEWS-------------------
NEWS_API_KEY = "087cc775b90c47338ed91b8572d19f48"

@bot.command()
@command_category("Info")
async def news(ctx, *, topic="technology"):
    url = f"https://newsapi.org/v2/top-headlines?q={topic}&language=en&pageSize=3&apiKey={NEWS_API_KEY}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                await ctx.send("❌ Failed to fetch news.")
                return
            data = await response.json()

    if not data["articles"]:
        await ctx.send("❌ No news found for that topic.")
        return

    embed = discord.Embed(title=f" Top News: {topic.title()}", color=discord.Color.blue())
    for article in data["articles"]:
        embed.add_field(
            name=article["title"],
            value=article["url"],
            inline=False
        )
    await ctx.send(embed=embed)

@bot.command()
@command_category("Fun")
async def joke(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://v2.jokeapi.dev/joke/Any") as response:
            if response.status != 200:
                await ctx.send("❌ Couldn't fetch a joke right now.")
                return
            data = await response.json()

    if data["type"] == "single":
        joke_text = data["joke"]
    else:
        joke_text = f"**{data['setup']}**\n{data['delivery']}"

    embed = discord.Embed(title=" Here's a joke!", description=joke_text, color=discord.Color.orange())
    await ctx.send(embed=embed)

@bot.command()
@command_category("Fun")
async def trivia(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://opentdb.com/api.php?amount=1&type=multiple") as resp:
            data = await resp.json()

    q = data["results"][0]
    question = html.unescape(q["question"])
    correct_answer = html.unescape(q["correct_answer"])
    options = [html.unescape(opt) for opt in q["incorrect_answers"]] + [correct_answer]
    random.shuffle(options)

    # Map options to letters
    letter_map = {chr(65 + i): options[i] for i in range(len(options))}
    correct_letter = [k for k, v in letter_map.items() if v == correct_answer][0]

    formatted_options = "\n".join([f"{letter}. {opt}" for letter, opt in letter_map.items()])

    embed = discord.Embed(
        title="🎲 Trivia Time!",
        description=f"**{question}**\n\n{formatted_options}\n\nReply with A, B, C, or D.",
        color=discord.Color.blurple()
    )
    await ctx.send(embed=embed)

    def check(m):
        return (
            m.author == ctx.author and
            m.channel == ctx.channel and
            m.content.upper() in letter_map
        )

    try:
        msg = await bot.wait_for('message', timeout=15.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ Time's up! The correct answer was **{correct_letter}: {correct_answer}**.")
        return

    user_answer = msg.content.upper()

    if user_answer == correct_letter:
        await ctx.send(f"✅ Correct! Well done, {ctx.author.mention}!")
    else:
        await ctx.send(f"❌ Incorrect! The correct answer was **{correct_letter}: {correct_answer}**.")

@bot.command()
@command_category("Fun")
async def slap(ctx, member: discord.Member):
    slap_gifs = [
        "https://media.giphy.com/media/Gf3AUz3eBNbTW/giphy.gif",
        "https://media.giphy.com/media/jLeyZWgtwgr2U/giphy.gif",
        "https://media.giphy.com/media/mEtSQlxqBtWWA/giphy.gif",
        "https://media.giphy.com/media/81kHQ5v9zbqzC/giphy.gif"
    ]
    gif = random.choice(slap_gifs)
    embed = discord.Embed(
        description=f"{ctx.author.mention} slapped {member.mention}!",
        color=discord.Color.red()
    )
    embed.set_image(url=gif)
    await ctx.send(embed=embed)

@bot.command()
@command_category("Fun")
async def fuck(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("Please mention someone!")
        return

    fuck_gifs = [
        "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExYm02OXA2aGF4d3VyZmdjc2k4djV4ZnF5dm56OGlqaWJoZnozajBndiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/qrXz6Wj2b4FmeXyIed/giphy.gif",
        # Add more direct GIF URLs here if you want multiple
    ]
    gif = random.choice(fuck_gifs)

    embed = discord.Embed(
        description=f"{ctx.author.mention} is fucking {member.mention} 🍑",
        color=discord.Color.red()
    )
    embed.set_image(url=gif)
    embed.set_footer(text="Getting Freaky 🔞")

    await ctx.send(embed=embed)

@bot.command(aliases=["r"])
@command_category("Moderation")
@commands.has_permissions(manage_roles=True)
async def role(ctx, subcommand: str = None, *, args: str = None):
    if subcommand is None:
        embed = discord.Embed(
            title="📘 Role Command Help",
            description=(
                "**Subcommands:**\n"
                "`!role list` – List all server roles\n"
                "`!role create <name>` – Create a new role\n"
                "`!role icon <role_name> <emoji>` – Set a role icon\n"
                "`!role color <color_name> <role_name>` – Change role color\n"
                "`!role toggle @user <role_name>` – Toggle role on/off for a user"
            ),
            color=discord.Color.blurple()
        )
        await ctx.send(embed=embed)
        return

    if subcommand == "list":
        roles = [r for r in ctx.guild.roles if r.name != "@everyone"]
        description = "\n".join(f"- {r.name}" for r in roles) or "No roles found."

        embed = discord.Embed(
            title=f"🎭 Roles in {ctx.guild.name}",
            description=description,
            color=discord.Color.purple()
        )
        embed.set_footer(text=f"Total roles: {len(roles)}")
        await ctx.send(embed=embed)

    elif subcommand == "create":
        if not args:
            embed = discord.Embed(
                description="❗ Usage: `!role create <role_name>`",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return
        role = await ctx.guild.create_role(name=args)
        embed = discord.Embed(
            description=f"✅ Created role **`{role.name}`**.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    elif subcommand == "icon":
        if not args or len(args.split()) < 2:
            embed = discord.Embed(
                description="❗ Usage: `!role icon <role_name> <emoji>`",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return

        parts = args.split()
        role_name = " ".join(parts[:-1])
        emoji = parts[-1]
        role = discord.utils.get(ctx.guild.roles, name=role_name)

        if not role:
            embed = discord.Embed(
                description=f"❌ Role `{role_name}` not found.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if emoji.isascii():
            try:
                await role.edit(unicode_emoji=emoji)
                embed = discord.Embed(
                    description=f"✅ Set emoji {emoji} for `{role.name}`.",
                    color=discord.Color.green()
                )
            except discord.HTTPException as e:
                embed = discord.Embed(
                    description=f"❌ Failed to set emoji: `{e}`",
                    color=discord.Color.red()
                )
            await ctx.send(embed=embed)

        elif emoji.startswith("<:") or emoji.startswith("<a:"):
            try:
                emoji_id = int(emoji.split(":")[-1].replace(">", ""))
                ext = "gif" if emoji.startswith("<a:") else "png"
                cdn_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{ext}?v=1"

                async with aiohttp.ClientSession() as session:
                    async with session.get(cdn_url) as resp:
                        if resp.status != 200:
                            raise ValueError("Emoji not found")
                        image_data = await resp.read()

                await role.edit(display_icon=image_data)
                embed = discord.Embed(
                    description=f"✅ Set custom emoji icon for `{role.name}`.",
                    color=discord.Color.green()
                )
            except Exception as e:
                embed = discord.Embed(
                    description=f"❌ Error setting emoji: `{e}`",
                    color=discord.Color.red()
                )
            await ctx.send(embed=embed)

    elif subcommand == "color":
        if not args or len(args.split()) < 2:
            embed = discord.Embed(
                description="❗ Usage: `!role color <color_name> <role_name>`\nExample: `!role color red Admin`",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return

        parts = args.split()
        color_name = parts[0].lower()
        role_name = " ".join(parts[1:])

        color_map = {
            "red": discord.Color.red(),
            "green": discord.Color.green(),
            "blue": discord.Color.blue(),
            "orange": discord.Color.orange(),
            "yellow": discord.Color.from_rgb(255, 255, 0),
            "purple": discord.Color.purple(),
            "pink": discord.Color.magenta(),
            "gold": discord.Color.gold(),
            "teal": discord.Color.teal(),
            "grey": discord.Color.greyple(),
            "dark_red": discord.Color.dark_red(),
            "dark_green": discord.Color.dark_green(),
            "dark_blue": discord.Color.dark_blue(),
            "dark_purple": discord.Color.dark_purple(),
            "dark_orange": discord.Color.dark_orange(),
            "dark_grey": discord.Color.dark_grey(),
            "light_grey": discord.Color.light_grey(),
            "darker_grey": discord.Color.darker_grey(),
            "navy": discord.Color.from_rgb(0, 0, 128),
            "blurple": discord.Color.blurple(),
        }

        if color_name not in color_map:
            embed = discord.Embed(
                description=f"❌ Unknown color `{color_name}`.\nAvailable: {', '.join(color_map)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        role = discord.utils.find(lambda r: role_name.lower() in r.name.lower(), ctx.guild.roles)
        if not role:
            embed = discord.Embed(
                description=f"❌ Role `{role_name}` not found.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            await role.edit(color=color_map[color_name])
            embed = discord.Embed(
                description=f"✅ Color of role **`{role.name}`** set to `{color_name}`.",
                color=color_map[color_name]
            )
            await ctx.send(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(
                description="❌ I don't have permission to edit that role.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                description=f"❌ Error updating role color: `{e}`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    elif subcommand == "add":
        if not args or len(ctx.message.mentions) == 0:
            embed = discord.Embed(
                description="❗ Usage: `!role toggle @member <role_name>`",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return

        member = ctx.message.mentions[0]
        role_name = args.replace(member.mention, "").strip()

        role = discord.utils.find(lambda r: role_name.lower() in r.name.lower(), ctx.guild.roles)
        if not role:
            embed = discord.Embed(
                description=f"❌ Role `{role_name}` not found.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            if role in member.roles:
                await member.remove_roles(role)
                embed = discord.Embed(
                    description=f"✅ Removed role `{role.name}` from {member.mention}.",
                    color=discord.Color.orange()
                )
            else:
                await member.add_roles(role)
                embed = discord.Embed(
                    description=f"✅ Added role `{role.name}` to {member.mention}.",
                    color=discord.Color.green()
                )
            await ctx.send(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(
                description="❌ I don't have permission to manage that role.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                description=f"❌ An error occurred: `{e}`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    else:
        embed = discord.Embed(
            description="❌ Unknown subcommand. Use `!role` to see available options.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.command()
@command_category("Fun")
async def rizz(ctx, target: discord.Member = None):
    """Send a pickup line from RizzApi mentioning users inside an embed."""
    url = "https://rizzapi.vercel.app/random"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise ValueError(f"API returned status {resp.status}")
                data = await resp.json()

                # Correct key for the line is 'text'
                line = data.get("text", "🤷‍♂️ No line found!")
        except Exception as e:
            return await ctx.send(embed=discord.Embed(
                description=f"❌ Error fetching rizz: `{e}`",
                color=discord.Color.red()
            ))

    if target:
        description = f"{ctx.author.mention} rizzed up {target.mention}:\n\n💬 *{line}*"
    else:
        description = f"{ctx.author.mention} drops a line:\n\n💬 *{line}*"

    embed = discord.Embed(
        
        description=description,
        color=discord.Color.blurple()
    )

    await ctx.send(embed=embed)


import base64 as b64

@bot.command(name="base64", aliases=["b64"])
@command_category("Fun")
async def base64(ctx, mode: str = None, *, text: str = None):
    """
    Encode or decode Base64 text.
    Usage: !base64 encode|e <text> OR !base64 decode|d <base64_text>
    """
    if mode is None or text is None:
        embed = discord.Embed(
            title="Base64 Command Usage",
            description=(
                " `!base64 e <text>` - Encode text to Base64\n"
                " `!base64 d <base64_text>` - Decode Base64 text"
            ),
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        return

    mode = mode.lower()
    if mode in ("encode", "e"):
        try:
            encoded_bytes = b64.b64encode(text.encode("utf-8"))
            encoded_str = encoded_bytes.decode("utf-8")
            embed = discord.Embed(
                title="Base64 Encoded Text",
                description=f"`{encoded_str}`",
                color=discord.Color.green()
            )
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"❌ Failed to encode Base64: `{e}`",
                color=discord.Color.red()
            )
    elif mode in ("decode", "d"):
        try:
            decoded_bytes = b64.b64decode(text.encode("utf-8"))
            decoded_str = decoded_bytes.decode("utf-8")
            embed = discord.Embed(
                title="Base64 Decoded Text",
                description=f"`{decoded_str}`",
                color=discord.Color.green()
            )
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"❌ Failed to decode Base64: `{e}`",
                color=discord.Color.red()
            )
    else:
        embed = discord.Embed(
            title="Base64 Command Usage",
            description=(
                "`!base64 encode <text>` or `!base64 e <text>` - Encode text to Base64\n"
                "`!base64 decode <base64_text>` or `!base64 d <base64_text>` - Decode Base64 text"
            ),
            color=discord.Color.orange()
        )

    await ctx.send(embed=embed)

@bot.command()
@command_category("Fun")
async def poll(ctx, *, question):
    embed = discord.Embed(title="Poll", description=question, color=discord.Color.orange())
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("👎")

#=====================MODERATION=========================
MOD_HISTORY_FILE = "modhistory.json"

def load_mod_history():
    if not os.path.isfile(MOD_HISTORY_FILE):
        with open(MOD_HISTORY_FILE, "w") as f:
            json.dump({}, f)
        return {}
    with open(MOD_HISTORY_FILE, "r") as f:
        return json.load(f)

def save_mod_history(data):
    with open(MOD_HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_mod_action(user_id: int, action: dict):
    data = load_mod_history()
    str_id = str(user_id)
    if str_id not in data:
        data[str_id] = []
    data[str_id].append(action)
    save_mod_history(data)

def error_embed(text):
    return discord.Embed(description=text, color=discord.Color.red())

def success_embed(text):
    return discord.Embed(description=text, color=discord.Color.green())

def info_embed(text):
    return discord.Embed(description=text, color=discord.Color.blue())


from datetime import datetime

import re
import asyncio
from datetime import datetime
import discord
from discord.ext import commands

def mod_action_embed(user: discord.Member, action: str):
    embed = discord.Embed(
        description=f"\n\n> {user.mention} has been {action}.\n> the reason has been sent to their DMs.\n\n",
        color=0xffffff
    )
    embed.set_thumbnail(url=user.avatar.url if hasattr(user.avatar, "url") else user.avatar_url)
    return embed

@bot.command()
@command_category("Moderation")
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
    if not member:
        return await ctx.send(embed=error_embed("❗ Please mention a user to warn."))

    add_mod_action(member.id, {
        "action": "warn",
        "mod": str(ctx.author.id),
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat()
    })

    await ctx.send(embed=mod_action_embed(member, "warned"))

    dm_embed = discord.Embed(
        title="Warned",
        description=f"You have been warned in **{ctx.guild.name}**",
        color=discord.Color.orange()
    )
    dm_embed.set_author(name=ctx.guild.name)  # No icon_url here
    dm_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
    dm_embed.add_field(name="Reason", value=reason, inline=True)

    try:
        await member.send(embed=dm_embed)
    except Exception:
        await ctx.send(embed=discord.Embed(
            description=f"⚠️ Could not send DM to {member.mention}. They might have DMs disabled.",
            color=discord.Color.orange()
        ))



@bot.command(aliases=["ma"])
@command_category("Moderation")
@commands.has_permissions(manage_roles=True, manage_channels=True)
async def mute(ctx, member: discord.Member = None, duration: str = None, *, reason: str = "No reason provided"):
    if not member:
        return await ctx.send(embed=error_embed("❗ Mention a user to mute."))

    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

    if not muted_role:
        try:
            muted_role = await ctx.guild.create_role(
                name="Muted",
                reason="Auto-created Muted role for muting users"
            )
        except discord.Forbidden:
            return await ctx.send(embed=error_embed("❌ I don't have permission to create roles."))

        for channel in ctx.guild.channels:
            if isinstance(channel, discord.TextChannel):
                try:
                    await channel.set_permissions(
                        muted_role,
                        send_messages=False,
                        add_reactions=False,
                        speak=False
                    )
                except discord.Forbidden:
                    await ctx.send(embed=error_embed(f"⚠️ Couldn't set permissions in channel {channel.name}"))

    if muted_role in member.roles:
        return await ctx.send(embed=info_embed(f"{member.mention} is already muted."))

    if not duration:
        return await ctx.send(embed=error_embed("❗ Please specify duration (e.g., 10s, 5m, 1h)."))

    time_regex = re.compile(r"(\d+)([smh])")
    matches = time_regex.findall(duration.lower())
    if not matches:
        return await ctx.send(embed=error_embed("❌ Invalid duration format! Use `s` for seconds, `m` for minutes, `h` for hours. Example: 10m"))

    seconds = 0
    for value, unit in matches:
        value = int(value)
        if unit == "s":
            seconds += value
        elif unit == "m":
            seconds += value * 60
        elif unit == "h":
            seconds += value * 3600

    try:
        await member.add_roles(muted_role, reason=reason)
        await ctx.send(embed=mod_action_embed(member, "muted"))
        add_mod_action(member.id, {
            "action": "mute",
            "mod": str(ctx.author.id),
            "reason": reason,
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat()
        })

        dm_embed = discord.Embed(
            title="Muted",
            description=f"You have been muted in **{ctx.guild.name}**",
            color=discord.Color.orange()
        )
        dm_embed.set_author(
            name=ctx.guild.name,
        )
        dm_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        dm_embed.add_field(name="Reason", value=reason, inline=True)
        dm_embed.add_field(name="Duration", value=duration, inline=True)

        try:
            await member.send(embed=dm_embed)
        except Exception:
            await ctx.send(f"⚠️ Could not send DM to {member.mention}. They might have DMs disabled.")

    except discord.Forbidden:
        return await ctx.send(embed=error_embed("❌ I can't manage that user's roles."))

    await asyncio.sleep(seconds)

    if muted_role in member.roles:
        try:
            await member.remove_roles(muted_role, reason="Timed mute expired")
            await ctx.send(embed=mod_action_embed(member, "unmuted"))
        except discord.Forbidden:
            await ctx.send(embed=error_embed(f"❌ I can't unmute {member.mention}. Please do it manually."))


@bot.command(aliases=["uma"])
@command_category("Moderation")
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member = None):
    if not member:
        return await ctx.send(embed=error_embed("❗ Mention a user to unmute."))

    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        return await ctx.send(embed=error_embed("❌ No 'Muted' role found."))

    if muted_role not in member.roles:
        return await ctx.send(embed=info_embed(f"{member.mention} is not muted."))

    try:
        await member.remove_roles(muted_role)
        await ctx.send(embed=mod_action_embed(member, "unmuted"))
        add_mod_action(member.id, {
            "action": "unmute",
            "mod": str(ctx.author.id),
            "reason": "Manual unmute",
            "timestamp": datetime.utcnow().isoformat()
        })
    except discord.Forbidden:
        await ctx.send(embed=error_embed("❌ I can't manage that user's roles."))
    except Exception as e:
        await ctx.send(embed=error_embed(f"❌ Failed to unmute user: `{e}`"))


@bot.command(aliases=["k"])
@command_category("Moderation")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
    if not member:
        return await ctx.send(embed=error_embed("❗ Please mention a user to kick."))

    try:
        await member.kick(reason=reason)
        await ctx.send(embed=mod_action_embed(member, "kicked"))
        add_mod_action(member.id, {
            "action": "kick",
            "mod": str(ctx.author.id),
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        })

        dm_embed = discord.Embed(
            title="Kicked",
            description=f"You have been kicked from **{ctx.guild.name}**",
            color=discord.Color.orange()
        )
        dm_embed.set_author(
            name=ctx.guild.name,
        )
        dm_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        dm_embed.add_field(name="Reason", value=reason, inline=True)

        try:
            await member.send(embed=dm_embed)
        except Exception:
            pass  # User might be kicked before DM, ignore

    except discord.Forbidden:
        await ctx.send(embed=error_embed("❌ I do not have permission to kick this member."))
    except Exception as e:
        await ctx.send(embed=error_embed(f"❌ Failed to kick user: `{e}`"))


@bot.command(aliases=["b"])
@command_category("Moderation")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member = None, days: int = 7, *, reason: str = "No reason provided"):
    if not member:
        return await ctx.send(embed=error_embed("❗ Please mention a user to ban."))

    try:
        await member.ban(reason=reason, delete_message_days=days)
        await ctx.send(embed=mod_action_embed(member, "banned"))
        add_mod_action(member.id, {
            "action": "ban",
            "mod": str(ctx.author.id),
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        })

        dm_embed = discord.Embed(
            title="Banned",
            description=f"You have been banned from **{ctx.guild.name}**",
            color=discord.Color.orange()
        )
        dm_embed.set_author(
            name=ctx.guild.name,
        )
        dm_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        dm_embed.add_field(name="Reason", value=reason, inline=True)

        try:
            await member.send(embed=dm_embed)
        except Exception:
            pass  # User might block DMs or be banned before DM sent

    except discord.Forbidden:
        await ctx.send(embed=error_embed("❌ I do not have permission to ban this member."))
    except Exception as e:
        await ctx.send(embed=error_embed(f"❌ Failed to ban user: `{e}`"))


@bot.command(aliases=["unb"])
@command_category("Moderation")
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member: str = None):
    if not member:
        return await ctx.send(embed=error_embed("❗ Please provide the user ID or username#discriminator to unban."))

    try:
        banned_users = await ctx.guild.bans()
    except discord.Forbidden:
        return await ctx.send(embed=error_embed("❌ I do not have permission to access the ban list."))
    except Exception as e:
        return await ctx.send(embed=error_embed(f"❌ Failed to fetch ban list: `{e}`"))

    user_obj = None
    for ban_entry in banned_users:
        user = ban_entry.user
        if str(user.id) == member or str(user) == member:
            user_obj = user
            break

    if not user_obj:
        return await ctx.send(embed=error_embed(f"❌ User `{member}` not found in ban list."))

    try:
        await ctx.guild.unban(user_obj)
        await ctx.send(embed=mod_action_embed(user_obj, "unbanned"))
        add_mod_action(user_obj.id, {
            "action": "unban",
            "mod": str(ctx.author.id),
            "reason": "Manual unban",
            "timestamp": datetime.utcnow().isoformat()
        })
    except discord.Forbidden:
        await ctx.send(embed=error_embed("❌ I do not have permission to unban this user."))
    except Exception as e:
        await ctx.send(embed=error_embed(f"❌ Failed to unban user: `{e}`"))


from datetime import datetime

@bot.command(aliases=["modhistory"])
@command_category("Moderation")
@commands.has_permissions(kick_members=True)
async def mh(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = load_mod_history()
    entries = data.get(str(member.id), [])

    if not entries:
        return await ctx.send(embed=info_embed(f"No moderation history found for {member.mention}."))

    embed = discord.Embed(title=f"Mod History for {member}", color=discord.Color.blue())
    for entry in entries[-10:]:  # last 10 mod actions
        action = entry.get("action", "Unknown").capitalize()
        mod_id = entry.get("mod")
        mod = ctx.guild.get_member(int(mod_id)) if mod_id else None
        mod_name = mod.display_name if mod else f"Mod ID {mod_id}"
        reason = entry.get("reason", "No reason provided")
        timestamp = entry.get("timestamp")
        duration = entry.get("duration", "")

        value = f"**Moderator:** {mod_name}\n**Reason:** {reason}\n**Date:** {timestamp}"
        if duration:
            value += f"\n**Duration:** {duration}"

        embed.add_field(name=action, value=value, inline=False)

    await ctx.send(embed=embed)

@bot.command(aliases=["myhistory", "punishments", "hist"])
@command_category("Info")
async def history(ctx):
    """Show the user's own moderation history in styled embed format."""
    member = ctx.author
    data = load_mod_history()
    entries = data.get(str(member.id), [])

    if not entries:
        embed = discord.Embed(
            title="Punishment History",
            description="✅ You have no moderation history.",
            color=discord.Color.green()
        )
        embed.set_author(name=member.display_name, icon_url=member.avatar_url)
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(
        title=f"Punishment History for {member.display_name}",
        color=discord.Color.red()
    )
    embed.set_author(name=member.display_name, icon_url=member.avatar_url)
    embed.set_footer(text=f"{len(entries)} punishments, 0 notes")

    for i, entry in enumerate(entries[-5:], start=1):  # Last 5 entries
        case_id = entry.get("case_id", f"#{100 + i}")  # Fake case ID if missing
        action = entry.get("action", "Unknown").capitalize()
        timestamp = entry.get("timestamp", "Unknown")
        mod_id = entry.get("mod", "Unknown")
        reason = entry.get("reason", "No reason provided")
        duration = entry.get("duration", "")

        try:
            timestamp_int = int(timestamp)
            punished_line = f"<t:{timestamp_int}>"
        except:
            punished_line = timestamp

        field_title = f"**Case Log {case_id} | {action}**"
        field_value = f"**Punished:** {punished_line}\n"
        field_value += f"**Moderator:** <@{mod_id}> (`{mod_id}`)\n"
        field_value += f"**Reason:** {reason}"
        if duration:
            field_value += f"\n**Duration:** {duration}"

        embed.add_field(name=field_title, value=field_value, inline=False)

    await ctx.send(embed=embed)


@bot.command()
@command_category("Moderation")
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    try:
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send(embed=success_embed("🔒 Channel locked."))
    except discord.Forbidden:
        await ctx.send(embed=error_embed("❌ I don't have permission to manage channel permissions."))
    except Exception as e:
        await ctx.send(embed=error_embed(f"❌ Failed to lock channel: `{e}`"))

@bot.command()
@command_category("Moderation")
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    try:
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = True
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send(embed=success_embed("🔓 Channel unlocked."))
    except discord.Forbidden:
        await ctx.send(embed=error_embed("❌ I don't have permission to manage channel permissions."))
    except Exception as e:
        await ctx.send(embed=error_embed(f"❌ Failed to unlock channel: `{e}`"))

# Optional: combined lockdown toggle command
@bot.command()
@command_category("Moderation") 
@commands.has_permissions(manage_channels=True)
async def lockdown(ctx):
    try:
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        if overwrite.send_messages is False:
            overwrite.send_messages = None  # Remove overwrite to unlock
            await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            await ctx.send(embed=success_embed("🔓 Channel unlocked."))
        else:
            overwrite.send_messages = False
            await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            await ctx.send(embed=success_embed("🔒 Channel locked."))
    except discord.Forbidden:
        await ctx.send(embed=error_embed("❌ I don't have permission to manage channel permissions."))
    except Exception as e:
        await ctx.send(embed=error_embed(f"❌ Failed to toggle lockdown: `{e}`"))


import discord
from discord.ext import commands
import aiohttp
import io

@bot.command()
@command_category("Fun")
async def tweet(ctx, username: str = None, *, message: str = None):

    if not username or not message:
        embed = discord.Embed(
            title="❌ Missing Parameters",
            description="Correct Usage:\n`!tweet <username> <message>`\nExample: `!tweet elonmusk I'm going to Mars!`",
            color=discord.Color.red()
        )
        return await ctx.send(embed=embed)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://nekobot.xyz/api/imagegen?type=tweet&username={username}&text={message}"
            ) as r:
                data = await r.json()

        tweet_img_url = data.get("message")
        if not tweet_img_url or not tweet_img_url.startswith("http"):
            raise ValueError("Invalid image URL returned from API.")

        async with aiohttp.ClientSession() as session:
            async with session.get(tweet_img_url) as resp:
                if resp.status != 200:
                    raise Exception("Failed to fetch image.")
                image_bytes = await resp.read()

        with io.BytesIO(image_bytes) as image_file:
            await ctx.send(file=discord.File(image_file, filename="fake_tweet.png"))

    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description=f"Couldn't generate tweet.\n`{str(e)}`",
            color=discord.Color.dark_red()
        )
        await ctx.send(embed=embed)

import instaloader
from discord.ext import commands
import discord

@bot.command(aliases=['ig', 'instagram'])
@command_category("Info")
async def insta(ctx, username: str):
    """Lookup Instagram profile info by username using instaloader."""
    L = instaloader.Instaloader()
    
    try:
        profile = instaloader.Profile.from_username(L.context, username)
    except instaloader.exceptions.ProfileNotExistsException:
        embed = discord.Embed(
            title="Instagram Lookup Error",
            description=f"❌ The user `{username}` does not exist on Instagram.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    except instaloader.exceptions.ConnectionException:
        embed = discord.Embed(
            title="Instagram Lookup Error",
            description="❌ Failed to connect to Instagram. Please try again later.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    except Exception as e:
        embed = discord.Embed(
            title="Instagram Lookup Error",
            description=f"❌ An unexpected error occurred:\n```{str(e)}```",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    lock_emoji = " 🔒" if profile.is_private else ""
    title = f"{profile.username}{lock_emoji}"
    description = profile.biography.strip() if profile.biography.strip() else ":3"

    embed = discord.Embed(
        title=title,
        url=f"https://instagram.com/{profile.username}",
        description=description,
        color=discord.Color.purple()
    )
    
    embed.set_author(name=profile.username, icon_url=profile.profile_pic_url)
    embed.set_thumbnail(url=profile.profile_pic_url)
    embed.set_footer(text="Instagram", icon_url="https://bleed.bot/img/instagram.png")

    embed.add_field(name="**Posts**", value=f"{profile.mediacount:,}", inline=True)
    embed.add_field(name="**Following**", value=f"{profile.followees:,}", inline=True)
    embed.add_field(name="**Followers**", value=f"{profile.followers:,}", inline=True)

    await ctx.send(embed=embed)

@bot.command(aliases=['audit', 'al', 'modlog'])
@command_category("Moderation")
@commands.has_permissions(view_audit_log=True)
async def auditlog(ctx, limit: int = 1):
    """Show recent audit log entries (default 1)"""

    entries = await ctx.guild.audit_logs(limit=limit).flatten()
    if not entries:
        return await ctx.send(embed=discord.Embed(
            description="No audit log entries found.",
            color=discord.Color.orange()
        ))

    # Map action numeric values to readable names (older version compatibility)
    action_map = {
        1: "Guild Updated",
        10: "Channel Created",
        11: "Channel Updated",
        12: "Channel Deleted",
        20: "Member Kicked",
        21: "Member Pruned",
        22: "Member Banned",
        23: "Member Unbanned",
        24: "Member Updated",
        25: "Member Role Updated",
        26: "Member Moved Voice Channel",
        27: "Member Disconnected Voice",
        28: "Bot Added",
        30: "Role Created",
        31: "Role Updated",
        32: "Role Deleted",
        40: "Invite Created",
        41: "Invite Deleted",
        50: "Webhook Created",
        51: "Webhook Updated",
        52: "Webhook Deleted",
        60: "Emoji Created",
        61: "Emoji Updated",
        62: "Emoji Deleted",
        72: "Message Deleted",
        73: "Bulk Message Deleted",
        74: "Message Pinned",
        75: "Message Unpinned",
    }

    embed = discord.Embed(
        title=f"Last {limit} Audit Log Entries",
        color=discord.Color.dark_gold(),
        timestamp=ctx.message.created_at
    )

    for entry in entries:
        action_name = action_map.get(entry.action.value if hasattr(entry.action, "value") else entry.action, str(entry.action).replace("_", " ").title())
        target = entry.target
        user = entry.user
        reason = entry.reason or "No reason provided"
        time = entry.created_at.strftime("%Y-%m-%d %H:%M:%S")

        embed.add_field(
            name=f"**{action_name}**",
            value=(
                f"**Target:** {target}\n"
                f"**By:** {user}\n"
                f"**Reason:** {reason}\n"
                f"**At:** {time}"
            ),
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command()
@command_category("Utility")
@commands.has_permissions(administrator=True)  # Optional: restrict who can use this command
async def dm(ctx, member: discord.Member = None, *, message: str = None):
    if not member:
        embed = discord.Embed(description="❗ Please mention a user to DM.", color=discord.Color.orange())
        return await ctx.send(embed=embed)
    if not message:
        embed = discord.Embed(description="❗ Please provide a message to send.", color=discord.Color.orange())
        return await ctx.send(embed=embed)

    try:
        await member.send(message)
        embed = discord.Embed(description=f"✅ Successfully sent a DM to {member.mention}.", color=discord.Color.green())
        await ctx.send(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(description=f"❌ I can't send a DM to {member.mention}. They might have DMs disabled.", color=discord.Color.red())
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(description=f"❌ Failed to send DM: `{e}`", color=discord.Color.red())
        await ctx.send(embed=embed)

# ===================== INVITE SCANNER =====================

import re

INVITE_REGEX = re.compile(r"(discord\.gg/|discord\.com/invite/)")
anti_invite_enabled = True  # Default enabled

@bot.event
async def on_message(message):
    if message.author == bot.user or isinstance(message.channel, discord.DMChannel):
        return

    # Anti-invite logic
    if anti_invite_enabled:
        if INVITE_REGEX.search(message.content):
            if not message.author.guild_permissions.administrator:
                try:
                    await message.delete()
                    await message.channel.send(
                        f"🚫 {message.author.mention}, invite links are not allowed!",
                        delete_after=5
                    )
                except discord.Forbidden:
                    pass  # Can't delete message or notify

    await bot.process_commands(message)

from discord import Embed

@bot.command()
@commands.has_permissions(administrator=True)
@command_category("Moderation")
async def antiinvite(ctx, state: str):
    """Toggle the invite link blocker on/off"""
    global anti_invite_enabled

    state = state.lower()
    embed = Embed(title="Anti-invite Protection", color=0x00ff00)  # default green

    if state in ("on", "enable", "true"):
        anti_invite_enabled = True
        embed.description = "✅ Anti-invite protection is now **enabled**."
        embed.color = 0x00ff00  # green
        await ctx.send(embed=embed)
    elif state in ("off", "disable", "false"):
        anti_invite_enabled = False
        embed.description = "❌ Anti-invite protection is now **disabled**."
        embed.color = 0xff0000  # red
        await ctx.send(embed=embed)
    else:
        embed.description = "⚠️ Use `!antiinvite on` or `!antiinvite off`."
        embed.color = 0xffa500  # orange
        await ctx.send(embed=embed)


@bot.command(aliases=['ri'])
@command_category("Info")
async def roleinfo(ctx, *, role_name: str):
    role = discord.utils.find(lambda r: role_name.lower() in r.name.lower(), ctx.guild.roles)

    if not role:
        await ctx.send(embed=discord.Embed(
            description=f"❌ No role found matching `{role_name}`.",
            color=discord.Color.red()
        ))
        return

    member_list = role.members
    created = role.created_at.strftime('%d %B %Y %I:%M %p')
    relative_time = f"<t:{int(role.created_at.timestamp())}:R>"

    # Fallback avatar logic for older discord.py
    avatar_url = ctx.author.avatar_url if ctx.author.avatar else ctx.author.default_avatar_url

    embed = discord.Embed(title=f"{role.name}", color=role.color or discord.Color.default())
    embed.set_author(name=str(ctx.author.display_name), icon_url=str(avatar_url))

    embed.add_field(name="Role ID", value=f"{role.id}", inline=True)
    embed.add_field(name="Guild", value=f"{ctx.guild.name} (`{ctx.guild.id}`)", inline=True)
    embed.add_field(name="Color", value=f"`{str(role.color)}`", inline=True)

    embed.add_field(name="Creation Date", value=f"{created} ({relative_time})", inline=False)

    if member_list:
        embed.add_field(
            name=f"{len(member_list)} Member(s)",
            value=", ".join(m.display_name for m in member_list[:10]) + ("..." if len(member_list) > 10 else ""),
            inline=False
        )
    else:
        embed.add_field(name="0 Member(s)", value="No members in this role", inline=False)

    await ctx.send(embed=embed)


@bot.command(aliases=['ui', 'user'])
@command_category("Info")
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author

    avatar_url = member.avatar_url_as(format='gif' if member.is_avatar_animated() else 'png')
    join_position = sorted(ctx.guild.members, key=lambda m: m.joined_at or ctx.guild.created_at).index(member) + 1
    mutual_guilds = len(member.mutual_guilds)

    roles = [role.mention for role in member.roles if role != ctx.guild.default_role]
    role_string = ', '.join(roles) if roles else "None"

    embed = discord.Embed(color=discord.Color.dark_theme())
    embed.set_author(name=f"{member.display_name} ({member.id})")
    embed.set_thumbnail(url=avatar_url)

    created = member.created_at
    joined = member.joined_at
    boosted = member.premium_since

    embed.add_field(
        name="Dates",
        value=(
            f"**Created:** {created.strftime('%m/%d/%Y, %I:%M %p')} (<t:{int(created.timestamp())}:R>)\n"
            f"**Joined:** {joined.strftime('%m/%d/%Y, %I:%M %p')} (<t:{int(joined.timestamp())}:R>)\n"
            + (f"**Boosted:** {boosted.strftime('%m/%d/%Y, %I:%M %p')} (<t:{int(boosted.timestamp())}:R>)" if boosted else "")
        ),
        inline=False
    )

    embed.add_field(name=f"Roles ({len(roles)})", value=role_string, inline=False)
    embed.set_footer(text=f"Join position: {join_position} • {mutual_guilds} mutual servers")

    await ctx.send(embed=embed)

import json
import os
import discord
from discord.ext import commands

WELCOME_SETTINGS_FILE = "welcome_settings.json"

# Load welcome settings from JSON file or create empty dict
if os.path.exists(WELCOME_SETTINGS_FILE):
    with open(WELCOME_SETTINGS_FILE, "r") as f:
        welcome_settings = json.load(f)
else:
    welcome_settings = {}

def save_welcome_settings():
    with open(WELCOME_SETTINGS_FILE, "w") as f:
        json.dump(welcome_settings, f, indent=4)

intents = discord.Intents.default()
intents.members = True  # Enable member intents to receive member join events


def error_embed(msg):
    return discord.Embed(description=msg, color=0xFF0000)

def success_embed(msg):
    return discord.Embed(description=msg, color=0x00FF00)

@bot.command()
@command_category("Moderation")
@commands.has_permissions(manage_guild=True)
async def welcome(ctx, channel: discord.TextChannel = None, toggle: str = None):
    if not channel or toggle not in ("on", "off"):
        await ctx.send(embed=error_embed("❗ Usage: `!welcome #channel on` or `!welcome #channel off`"))
        return

    guild_id = str(ctx.guild.id)

    welcome_settings[guild_id] = {
        "channel_id": channel.id,
        "enabled": toggle == "on"
    }
    save_welcome_settings()

    status = "enabled" if toggle == "on" else "disabled"
    await ctx.send(embed=success_embed(f"✅ Welcome messages {status} in {channel.mention}"))

@bot.event
async def on_member_join(member):
    guild_id = str(member.guild.id)
    settings = welcome_settings.get(guild_id)

    if not settings:
        print(f"[DEBUG] No welcome settings for guild {guild_id}")
        return

    if not settings.get("enabled", False):
        print(f"[DEBUG] Welcome message disabled for guild {guild_id}")
        return

    channel_id = settings.get("channel_id")
    if not channel_id:
        print(f"[DEBUG] No channel_id in settings for guild {guild_id}")
        return

    channel = member.guild.get_channel(channel_id)
    if not channel:
        print(f"[DEBUG] Channel ID {channel_id} not found in guild {guild_id}")
        return

    try:
        embed = discord.Embed(
            description=(
                f"\n\n"
                f"-# _ _ _ _ _ _ _ _ _ _ _ _ .  .  _𝓦𝓮𝓵𝓬𝓸𝓶𝓮 {member.mention}_ 🎉\n"
                f"-# _ _ _ _ _ _ _ _ _ _ _ _ _𝓽𝓱𝓪𝓷𝓴  𝔂𝓸𝓾  𝓯𝓸𝓻 𝓳𝓸𝓲𝓷𝓲𝓷𝓰 𓂅_\n\n"
            ),
            color=0xffeafc
        )
        if member.guild.icon:
            embed.set_thumbnail(url=member.guild.icon_url)
        await channel.send(embed=embed)
        print(f"[DEBUG] Sent welcome message in guild {guild_id} channel {channel_id}")
    except Exception as e:
        print(f"[ERROR] Failed to send welcome message: {e}")

import discord
from datetime import datetime, timezone

afk_users = {}  # user_id: (reason, start_time)
GREEN_COLOR = 0xA5EB78

@bot.command()
@command_category("Utility")
async def afk(ctx, *, reason: str = "AFK"):
    afk_users[ctx.author.id] = (reason, datetime.now(timezone.utc))

    embed = discord.Embed(
        color=GREEN_COLOR,
        description=f" {ctx.author.mention}: You're now AFK with the status: **{reason}**"
    )
    await ctx.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Remove AFK on message from user
    if message.author.id in afk_users:
        reason, start_time = afk_users.pop(message.author.id)
        now = datetime.now(timezone.utc)
        diff = now - start_time
        seconds = int(diff.total_seconds())

        embed = discord.Embed(
            color=GREEN_COLOR,
            description=f"👋 {message.author.mention}: Welcome back, you were away for **{seconds} seconds**"
        )
        await message.channel.send(embed=embed)

    # Notify if mentioned user is AFK
    for user in message.mentions:
        if user.id in afk_users and user != message.author:
            reason, start_time = afk_users[user.id]
            unix_timestamp = int(start_time.timestamp())

            embed = discord.Embed(
                color=GREEN_COLOR,
                description=f"💤 {user.mention} is AFK: **{reason}** - <t:{unix_timestamp}:R>"
            )
            await message.channel.send(embed=embed)

    await bot.process_commands(message)

DATA_FILE = "economy.json"
import discord
from discord.ext import commands
import json
import random
from datetime import datetime, timedelta
import os

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            f.write("{}")  # create empty JSON object
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_user_data(data, user_id):
    if str(user_id) not in data:
        data[str(user_id)] = {
            "coins": 0,
            "bank": 0,
            "last_daily": None,
            "last_rob": None,
            "last_work": None,
            "last_payday": None,
            "last_crime": None
        }
    return data[str(user_id)]

def time_left(last_time_iso, cooldown_seconds):
    if last_time_iso is None:
        return 0
    last_time = datetime.fromisoformat(last_time_iso)
    now = datetime.utcnow()
    delta = (last_time + timedelta(seconds=cooldown_seconds)) - now
    return max(delta.total_seconds(), 0)

def format_time(seconds):
    mins, secs = divmod(int(seconds), 60)
    if mins > 0:
        return f"{mins}m {secs}s"
    return f"{secs}s"

@bot.command(help="Show your or another member's coin balance.", aliases=["coins", "bal"])
@command_category("Game")
async def balance(ctx, member: discord.Member=None):
    member = member or ctx.author
    data = load_data()
    user_data = get_user_data(data, member.id)

    embed = discord.Embed(
        title=f"{member.display_name}'s Balance",
        color=0xA5EB78
    )
    embed.add_field(name="Wallet", value=f"💰 {user_data['coins']} coins", inline=True)
    embed.add_field(name="Bank", value=f"🏦 {user_data.get('bank',0)} coins", inline=True)
    embed.set_thumbnail(url=member.avatar.url if hasattr(member.avatar, "url") else member.avatar_url)
    await ctx.send(embed=embed)

@bot.command(help="Claim your daily coins (24-hour cooldown).")
@command_category("Game")
async def daily(ctx):
    data = load_data()
    user_data = get_user_data(data, ctx.author.id)

    cooldown = 24 * 3600
    remaining = time_left(user_data["last_daily"], cooldown)

    if remaining > 0:
        embed = discord.Embed(
            description=f"⏳ You already claimed your daily! Come back in **{format_time(remaining)}**.",
            color=0xFAA61A
        )
        await ctx.send(embed=embed)
        return

    reward = random.randint(50, 150)
    user_data["coins"] += reward
    user_data["last_daily"] = datetime.utcnow().isoformat()
    save_data(data)

    embed = discord.Embed(
        description=f"🎉 You claimed your daily **{reward} coins!**",
        color=0x00FF00
    )
    await ctx.send(embed=embed)

@bot.command(help="Work to earn coins (10-minute cooldown).")
@command_category("Game")
async def work(ctx):
    data = load_data()
    user_data = get_user_data(data, ctx.author.id)

    cooldown = 60 * 10  # 10 minutes cooldown
    remaining = time_left(user_data["last_work"], cooldown)

    if remaining > 0:
        embed = discord.Embed(
            description=f"⏳ You are tired! Come back in **{format_time(remaining)}** to work again.",
            color=0xFAA61A
        )
        await ctx.send(embed=embed)
        return

    reward = random.randint(20, 100)
    user_data["coins"] += reward
    user_data["last_work"] = datetime.utcnow().isoformat()
    save_data(data)

    embed = discord.Embed(
        description=f"💼 You worked hard and earned **{reward} coins!**",
        color=0x00FF00
    )
    await ctx.send(embed=embed)

@bot.command(help="Rob coins from another member (30-minute cooldown).")
@command_category("Game")
async def rob(ctx, target: discord.Member):
    if target == ctx.author:
        await ctx.send("You can't rob yourself!")
        return

    data = load_data()
    robber_data = get_user_data(data, ctx.author.id)
    target_data = get_user_data(data, target.id)

    cooldown = 60 * 30  # 30 minutes cooldown
    remaining = time_left(robber_data["last_rob"], cooldown)

    if remaining > 0:
        embed = discord.Embed(
            description=f"⏳ You must wait **{format_time(remaining)}** before robbing again.",
            color=0xFAA61A
        )
        await ctx.send(embed=embed)
        return

    if target_data["coins"] < 100:
        embed = discord.Embed(
            description=f"{target.display_name} doesn't have enough coins to rob.",
            color=0xFAA61A
        )
        await ctx.send(embed=embed)
        return

    success_chance = 0.5
    robber_data["last_rob"] = datetime.utcnow().isoformat()

    if random.random() < success_chance:
        stolen_amount = random.randint(50, min(150, target_data["coins"]))
        target_data["coins"] -= stolen_amount
        robber_data["coins"] += stolen_amount
        save_data(data)
        embed = discord.Embed(
            description=f"💰 You successfully robbed **{target.display_name}** and got **{stolen_amount} coins!**",
            color=0x00FF00
        )
    else:
        penalty = random.randint(20, 70)
        robber_data["coins"] = max(0, robber_data["coins"] - penalty)
        save_data(data)
        embed = discord.Embed(
            description=f"🚨 You got caught and paid a fine of **{penalty} coins!**",
            color=0xFF0000
        )
    await ctx.send(embed=embed)

@bot.command(help="Show the top 10 richest users.")
@command_category("Game")
async def leaderboard(ctx):
    data = load_data()

    # Only include users who are members of this server
    server_user_ids = {str(member.id) for member in ctx.guild.members}
    server_data = {uid: info for uid, info in data.items() if uid in server_user_ids}

    # Sort the filtered data by coins
    sorted_users = sorted(server_data.items(), key=lambda x: x[1].get("coins", 0), reverse=True)

    embed = discord.Embed(
        title="🏆 Leaderboard",
        description="Top richest users in this server:",
        color=0xA5EB78
    )

    for i, (user_id, user_data) in enumerate(sorted_users[:10], 1):
        member = ctx.guild.get_member(int(user_id))
        name = member.display_name if member else f"User ID {user_id}"
        coins = user_data.get("coins", 0)
        embed.add_field(name=f"{i}. {name}", value=f"💰 {coins} coins", inline=False)

    await ctx.send(embed=embed)


@bot.command(help="Gamble an amount of coins to try to double them.")
@command_category("Game")
async def gamble(ctx, amount: int):
    if amount <= 0:
        embed = discord.Embed(description="❌ Amount must be greater than 0.", color=0xFF0000)
        await ctx.send(embed=embed)
        return
    
    data = load_data()
    user_data = get_user_data(data, ctx.author.id)
    
    if user_data["coins"] < amount:
        embed = discord.Embed(description="❌ You don't have enough coins to gamble.", color=0xFF0000)
        await ctx.send(embed=embed)
        return
    
    win_chance = 0.45
    user_data["coins"] -= amount
    
    if random.random() < win_chance:
        winnings = amount * 2
        user_data["coins"] += winnings
        save_data(data)
        embed = discord.Embed(description=f"🎉 You won {winnings} coins!", color=0x00FF00)
    else:
        save_data(data)
        embed = discord.Embed(description=f"😢 You lost {amount} coins!", color=0xFF0000)
    await ctx.send(embed=embed)

@bot.command(help="Play slots for a chance to win coins (costs 50 coins).")
@command_category("Game")
async def slots(ctx):
    data = load_data()
    user_data = get_user_data(data, ctx.author.id)
    
    cost = 50
    if user_data["coins"] < cost:
        embed = discord.Embed(description=f"❌ You need at least {cost} coins to play slots.", color=0xFF0000)
        await ctx.send(embed=embed)
        return
    
    user_data["coins"] -= cost
    
    emojis = ["🍎", "🍌", "🍇", "🍒", "🍋"]
    result = [random.choice(emojis) for _ in range(3)]
    
    if len(set(result)) == 1:  # all three match
        reward = cost * 5
        user_data["coins"] += reward
        save_data(data)
        embed = discord.Embed(description=f"🎰 {' '.join(result)}\nJackpot! You won {reward} coins!", color=0xA5EB78)
    elif len(set(result)) == 2:  # two match
        reward = cost * 2
        user_data["coins"] += reward
        save_data(data)
        embed = discord.Embed(description=f"🎰 {' '.join(result)}\nNice! You won {reward} coins!", color=0xA5EB78)
    else:
        save_data(data)
        embed = discord.Embed(description=f"🎰 {' '.join(result)}\nNo luck this time!", color=0xFAA61A)
    await ctx.send(embed=embed)

@bot.command(help="Receive your payday bonus (1-hour cooldown).")
@command_category("Game")
async def payday(ctx):
    data = load_data()
    user_data = get_user_data(data, ctx.author.id)
    
    cooldown = 3600  # 1 hour
    remaining = time_left(user_data.get("last_payday"), cooldown)
    
    if remaining > 0:
        embed = discord.Embed(description=f"⏳ You already took payday! Wait {format_time(remaining)}.", color=0xA5EB78)
        await ctx.send(embed=embed)
        return
    
    reward = random.randint(100, 300)
    user_data["coins"] += reward
    user_data["last_payday"] = datetime.utcnow().isoformat()
    save_data(data)
    
    embed = discord.Embed(description=f"💵 Payday! You received {reward} coins.", color=0x00FF00)
    await ctx.send(embed=embed)

@bot.command(help="Commit a crime to steal coins with risk (30-minute cooldown).")
@command_category("Game")
async def crime(ctx):
    data = load_data()
    user_data = get_user_data(data, ctx.author.id)
    
    cooldown = 1800  # 30 minutes cooldown
    remaining = time_left(user_data.get("last_crime"), cooldown)
    
    if remaining > 0:
        embed = discord.Embed(
            description=f"⏳ You are laying low. Wait {format_time(remaining)} before committing another crime.",
            color=0xFAA61A
        )
        await ctx.send(embed=embed)
        return
    
    success_chance = 0.4
    user_data["last_crime"] = datetime.utcnow().isoformat()
    
    if random.random() < success_chance:
        reward = random.randint(200, 500)
        user_data["coins"] += reward
        save_data(data)
        embed = discord.Embed(
            description=f"🕵️ Crime success! You stole {reward} coins.",
            color=0x00FF00
        )
    else:
        penalty = random.randint(100, 300)
        user_data["coins"] = max(0, user_data["coins"] - penalty)
        save_data(data)
        embed = discord.Embed(
            description=f"🚓 You got caught! Paid {penalty} coins fine.",
            color=0xFF0000
        )
    await ctx.send(embed=embed)

@bot.command(help="Deposit coins into your bank (safe from robbery). Usage: deposit <amount> or no amount to deposit all.")
@command_category("Game")
async def deposit(ctx, amount: int = None):
    data = load_data()
    user_data = get_user_data(data, ctx.author.id)

    wallet_coins = user_data.get("coins", 0)
    if wallet_coins <= 0:
        embed = discord.Embed(description="❌ You have no coins to deposit.", color=0xA5EB78)
        await ctx.send(embed=embed)
        return

    if amount is None:
        amount = wallet_coins
    elif amount <= 0:
        embed = discord.Embed(description="❌ Amount must be greater than 0.", color=0xA5EB78)
        await ctx.send(embed=embed)
        return
    elif amount > wallet_coins:
        embed = discord.Embed(description="❌ You don't have enough coins to deposit that amount.", color=0xFFFF00)
        await ctx.send(embed=embed)
        return

    user_data["coins"] -= amount
    user_data["bank"] = user_data.get("bank", 0) + amount
    save_data(data)

    embed = discord.Embed(
        description=f"🏦 You deposited **{amount}** coins to your bank.",
        color=0xFFFF00
    )
    await ctx.send(embed=embed)


@bot.command(help="Withdraw coins from your bank. Usage: withdraw <amount> or no amount to withdraw all.")
@command_category("Game")
async def withdraw(ctx, amount: int = None):
    data = load_data()
    user_data = get_user_data(data, ctx.author.id)

    bank_coins = user_data.get("bank", 0)
    if bank_coins <= 0:
        embed = discord.Embed(description="❌ You have no coins to withdraw.", color=0xFFFF00)
        await ctx.send(embed=embed)
        return

    if amount is None:
        amount = bank_coins
    elif amount <= 0:
        embed = discord.Embed(description="❌ Amount must be greater than 0.", color=0xFFFF00)
        await ctx.send(embed=embed)
        return
    elif amount > bank_coins:
        embed = discord.Embed(description="❌ You don't have enough coins to withdraw that amount.", color=0xFFFF00)
        await ctx.send(embed=embed)
        return

    user_data["bank"] -= amount
    user_data["coins"] += amount
    save_data(data)

    embed = discord.Embed(
        description=f"💵 You withdrew **{amount}** coins from your bank.",
        color=0xFFFF00
    )
    await ctx.send(embed=embed)


@bot.command(name="transfer", aliases=["pay", "give"])
@command_category("Game")
async def transfer(ctx, member: discord.Member, amount: int):
    if amount <= 0:
        embed = discord.Embed(description="❌ Amount must be greater than 0.", color=0xFFFF00)
        await ctx.send(embed=embed)
        return

    if member == ctx.author:
        embed = discord.Embed(description="❌ You cannot transfer coins to yourself.", color=0xFFFF00)
        await ctx.send(embed=embed)
        return

    data = load_data()
    sender_data = get_user_data(data, ctx.author.id)
    receiver_data = get_user_data(data, member.id)

    if sender_data.get("coins", 0) < amount:
        embed = discord.Embed(description="❌ You don't have enough coins to transfer.", color=0xFFFF00)
        await ctx.send(embed=embed)
        return

    sender_data["coins"] -= amount
    receiver_data["coins"] += amount
    save_data(data)

    embed = discord.Embed(
        description=f"✅ You transferred **{amount}** coins to {member.display_name}.",
        color=0xFFFF00
    )
    await ctx.send(embed=embed)
   
import json
import discord
from discord.ext import commands
import aiohttp
import random
import io
import asyncio

async def fetch_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()

@bot.command()
@command_category("Fun")
async def doxuser(ctx):
    data = await fetch_json("https://randomuser.me/api/")
    user = data['results'][0]

    # Realistic name
    first = user['name']['first'].lower()
    last = user['name']['last'].lower()

    # Random realistic email domain
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com", "icloud.com", "protonmail.com"]
    domain = random.choice(domains)
    email = f"{first}.{last}@{domain}"

    # Detailed info
    name = f"{user['name']['title']} {user['name']['first']} {user['name']['last']}"
    gender = user['gender'].capitalize()
    dob = user['dob']['date'][:10]
    age = user['dob']['age']
    phone = user['phone']
    location = f"{user['location']['city']}, {user['location']['state']}, {user['location']['country']}"
    picture_url = user['picture']['large']

    # Embed
    embed = discord.Embed(
        title="Random Doxx",
        color=discord.Color.teal()
    )
    embed.set_thumbnail(url=picture_url)
    embed.add_field(name="Name", value=name, inline=True)
    embed.add_field(name="Gender", value=gender, inline=True)
    embed.add_field(name="Birthday", value=f"{dob} ({age} y/o)", inline=False)
    embed.add_field(name="Email", value=email, inline=False)
    embed.add_field(name="Phone", value=phone, inline=False)
    embed.add_field(name="Location", value=location, inline=False)
    embed.set_footer(text="bros cooked")

    await ctx.send(embed=embed)

bot.command()
async def wallpaper(ctx):
    # 1920x1080 random photo from picsum.photos
    url = "https://picsum.photos/1920/1080"
    
    embed = discord.Embed(title="🎨 Random Gradient Wallpaper", color=discord.Color.blue())
    embed.set_image(url=url)
    await ctx.send(embed=embed)

GREEN_COLOR = 0xA5EB78
@bot.command(name="cook", aliases=["insult", "roast"])
@command_category("Fun")
async def cook(ctx, member: discord.Member = None):
    data = await fetch_json("https://evilinsult.com/generate_insult.php?lang=en&type=json")
    insult = data.get("insult", "Couldn't fetch roast.")
    mention = f"{member.mention} " if member else ""
    emoji = "😭"  # You can change this to any emoji you like
    embed = discord.Embed(description=f"{emoji} {mention}{insult}", color=GREEN_COLOR)
    await ctx.send(embed=embed)


import discord
from discord.ext import commands
import json
import os

# Ensure prefixes.json exists
if not os.path.exists("prefixes.json"):
    with open("prefixes.json", "w") as f:
        json.dump({"default": "!"}, f, indent=4)

@bot.command(help="Change the bot's prefix for this server.")
@commands.has_permissions(administrator=True)
@command_category("Moderation")
async def setprefix(ctx, new_prefix: str):
    if len(new_prefix) > 5:
        return await ctx.send("❌ Prefix too long. Use 5 characters or fewer.")

    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = new_prefix

    with open("prefixes.json", "w") as f:
        json.dump(prefixes, f, indent=4)

    embed = discord.Embed(
        title="Prefix Changed",
        description=f"✅ Prefix changed to `{new_prefix}` for this server.",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)


# Optional cleanup on server leave
@bot.event
async def on_guild_remove(guild):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    if str(guild.id) in prefixes:
        del prefixes[str(guild.id)]
        with open("prefixes.json", "w") as f:
            json.dump(prefixes, f, indent=4)


import discord
from discord.ext import commands
import requests
import json
import asyncio
from discord.ext.commands import BucketType

OPENROUTER_API_KEY = "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"

# Store conversation history per user
conversations = {}

@bot.command(help="Chat with AI using OpenRouter DeepSeek API with memory, in an embed.")
@commands.cooldown(rate=1, per=10, type=BucketType.user)
@command_category("ChatGPT")
async def talk(ctx, *, message: str):
    user_id = ctx.author.id

    if user_id not in conversations:
        conversations[user_id] = [{"role": "system", "content": "You are a helpful assistant."}]

    conversations[user_id].append({"role": "user", "content": message})

    api_url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek/deepseek-r1:free",
        "messages": conversations[user_id],
        "temperature": 0.7,
        "max_tokens": 500
    }

 # Send initial embed thinking message
    loading_embed = discord.Embed(description="💬 Thinking.", color=0xA5EB78)
    loading_msg = await ctx.send(embed=loading_embed)

    async def animate_loading_embed(msg):
        dots = ["💬 Thinking.", "💬 Thinking..", "💬 Thinking..."]
        i = 0
        while True:
            embed = discord.Embed(description=dots[i % len(dots)], color=0xA5EB78)
            await msg.edit(embed=embed)
            i += 1
            await asyncio.sleep(0.5)

    task = asyncio.create_task(animate_loading_embed(loading_msg))

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise HTTP errors if any
        data = response.json()

        reply = data['choices'][0]['message']['content']
        conversations[user_id].append({"role": "assistant", "content": reply})

        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        chatgpt_icon_url = "https://i.postimg.cc/fRvNV13L/chatgpt-7977357-1280.png"

        embed = discord.Embed(
            title="🤖 ChatGPT Response",
            description=reply,
            color=0xA5EB78
        )
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=chatgpt_icon_url)

        await loading_msg.edit(content=None, embed=embed)

    except requests.exceptions.HTTPError as http_err:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        await ctx.send(f"❌ HTTP error occurred: {http_err}")
        print(f"HTTP error: {http_err}")

    except requests.exceptions.RequestException as req_err:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        await ctx.send(f"❌ Request error: {req_err}")
        print(f"Request error: {req_err}")

    except KeyError:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        await ctx.send("❌ Unexpected response structure from AI API.")
        print(f"Response JSON: {response.text}")

    except commands.CommandOnCooldown as cooldown_exc:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        await ctx.send(f"⏳ Please wait {int(cooldown_exc.retry_after)} seconds before using this command again.")

    except Exception as e:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        await ctx.send("Oops! Something went wrong while contacting the AI.")
        print(f"Unexpected error: {e}")

import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import textwrap
import aiohttp



def rounded_rectangle(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.pieslice([x0, y0, x0 + 2*radius, y0 + 2*radius], 180, 270, fill=fill)
    draw.pieslice([x1 - 2*radius, y0, x1, y0 + 2*radius], 270, 360, fill=fill)
    draw.pieslice([x0, y1 - 2*radius, x0 + 2*radius, y1], 90, 180, fill=fill)
    draw.pieslice([x1 - 2*radius, y1 - 2*radius, x1, y1], 0, 90, fill=fill)

@bot.command(help="Quote a replied message as a nice image")
@command_category("Fun")
async def quotemsg(ctx):
    if not ctx.message.reference:
        await ctx.send("Please reply to a message to quote.")
        return

    try:
        replied_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
    except:
        await ctx.send("Could not fetch the replied message.")
        return

    author = replied_msg.author
    author_name = f"@{author.display_name}"
    content = replied_msg.content
    if not content:
        await ctx.send("The replied message has no text to quote.")
        return

    # Fetch avatar (discord.py 1.7.3)
    avatar_url = author.avatar_url_as(format='png', size=64)
    async with aiohttp.ClientSession() as session:
        async with session.get(str(avatar_url)) as resp:
            avatar_bytes = await resp.read()

    avatar_img = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
    avatar_img = avatar_img.resize((64, 64))
    avatar_img = ImageOps.fit(avatar_img, (64, 64), centering=(0.5, 0.5))

    # Fonts - update path to your font file location
    font_path = "DejaVuSans.ttf"
    font_bold = ImageFont.truetype(font_path, 28)
    font_regular = ImageFont.truetype(font_path, 22)

    # Wrap text
    wrapper = textwrap.TextWrapper(width=50)
    wrapped_text = wrapper.fill(text=content)
    lines = wrapped_text.split('\n')

    # Calculate line height with getbbox fix
    bbox = font_regular.getbbox("A")
    line_height = (bbox[3] - bbox[1]) + 6
    text_height = line_height * len(lines)

    padding = 20
    img_height = max(64 + padding*2, 60 + text_height + padding*2)
    img_width = 600

    background_color = (54, 57, 63)  # Discord dark bg
    bubble_color = (67, 181, 129)    # Discord green
    text_color = (255, 255, 255)

    img = Image.new("RGBA", (img_width, img_height), background_color)
    draw = ImageDraw.Draw(img)

    # Paste avatar
    img.paste(avatar_img, (padding, padding), avatar_img)

    # Draw username
    text_x = padding + 64 + 20
    text_y = padding
    draw.text((text_x, text_y), author_name, font=font_bold, fill=bubble_color)

    # Draw rounded rectangle bubble behind message
    bubble_x0 = text_x
    bubble_y0 = text_y + 36
    bubble_x1 = img_width - padding
    bubble_y1 = bubble_y0 + text_height + 20
    rounded_rectangle(draw, (bubble_x0, bubble_y0, bubble_x1, bubble_y1), radius=15, fill=(44, 47, 51))

    # Draw message lines
    current_y = bubble_y0 + 10
    for line in lines:
        draw.text((bubble_x0 + 15, current_y), line, font=font_regular, fill=text_color)
        current_y += line_height

    # Save to bytes and send
    with io.BytesIO() as image_binary:
        img.save(image_binary, "PNG")
        image_binary.seek(0)
        await ctx.send(file=discord.File(fp=image_binary, filename="quote.png"))


@bot.command(name="readmind")
async def readmind(ctx):
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.lower() == "done"

    steps = [
        "🧠 Think of a number in your head, but don’t say it out loud.",
        "✖️ Multiply that number by 3.",
        "➕ Add 12 to the result.",
        "➗ Divide the total by 3.",
        "➖ Subtract the number you originally thought of."
    ]

    intro = discord.Embed(
        title="🧠 Mind Reading Trick",
        description="Follow the instructions one at a time. Type `done` after each step.",
        color=discord.Color.purple()
    )
    await ctx.send(embed=intro)

    for step in steps:
        step_embed = discord.Embed(description=step, color=discord.Color.blurple())
        await ctx.send(embed=step_embed)

        try:
            await bot.wait_for('message', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                description="⏰ You took too long! Try the command again when you're ready.",
                color=discord.Color.red()
            )
            await ctx.send(embed=timeout_embed)
            return

    await asyncio.sleep(2)
    result_embed = discord.Embed(
        title="😱 I got it!",
        description="The number in your mind is... **4**! Am I right? 😄",
        color=discord.Color.purple()
    )
    await ctx.send(embed=result_embed)


questions = [
    # Old / Fun
    ("Would you rather be able to teleport anywhere or be able to read minds?", "Teleport anywhere", "Read minds"),
    ("Would you rather never be stuck in traffic again or never get a cold?", "Never stuck in traffic", "Never get a cold"),
    ("Would you rather have the ability to fly or be invisible?", "Fly", "Be invisible"),
    ("Would you rather always have to sing instead of speak or dance everywhere you go?", "Sing instead of speak", "Dance everywhere"),
    ("Would you rather live without internet or live without AC and heating?", "Without internet", "Without AC and heating"),
    ("Would you rather have unlimited money but no friends or lots of friends but no money?", "Unlimited money", "Lots of friends"),
    ("Would you rather lose your keys or lose your phone?", "Lose keys", "Lose phone"),
    ("Would you rather only be able to whisper or only be able to shout?", "Whisper", "Shout"),
    ("Would you rather explore space or the deep sea?", "Explore space", "Explore deep sea"),
    ("Would you rather be famous or be rich?", "Famous", "Rich"),
    ("Would you rather never eat your favorite food again or only eat your favorite food?", "Never eat again", "Only eat favorite food"),
    ("Would you rather have a rewind button or a pause button on your life?", "Rewind", "Pause"),
    ("Would you rather always know when someone is lying or always get away with lying?", "Know lies", "Get away with lies"),
    ("Would you rather have a personal chef or a personal driver?", "Personal chef", "Personal driver"),
    ("Would you rather never have to sleep or never have to eat?", "Never sleep", "Never eat"),
    ("Would you rather be able to speak every language or be able to talk to animals?", "Speak every language", "Talk to animals"),
    ("Would you rather have the ability to see 10 minutes into the future or 10 years into the future?", "10 minutes", "10 years"),
    ("Would you rather live without music or without movies?", "Without music", "Without movies"),
    ("Would you rather be stuck on a broken ski lift or in a broken elevator?", "Ski lift", "Elevator"),
    ("Would you rather have free Wi-Fi wherever you go or free coffee where/whenever you want?", "Free Wi-Fi", "Free coffee"),
    ("Would you rather be able to control fire or water?", "Control fire", "Control water"),
    ("Would you rather be always hot or always cold?", "Always hot", "Always cold"),
    ("Would you rather have a flying carpet or a car that can drive underwater?", "Flying carpet", "Underwater car"),
    ("Would you rather live one life that lasts 1,000 years or live 10 lives that last 100 years each?", "1,000 years", "10 lives"),
    ("Would you rather have a completely automated home or a self-driving car?", "Automated home", "Self-driving car"),
    ("Would you rather never have internet access again or never be able to take an airplane again?", "No internet", "No airplanes"),
    ("Would you rather be a master at every musical instrument or fluent in every language?", "Master instruments", "Fluent languages"),
    ("Would you rather always have to wear heavy boots or never be able to wear shoes?", "Heavy boots", "No shoes"),
    ("Would you rather be able to control time or be able to control people's thoughts?", "Control time", "Control thoughts"),
    ("Would you rather live in a world without pizza or a world without burgers?", "No pizza", "No burgers"),
    ("Would you rather never be able to use a touchscreen or never be able to use a keyboard and mouse?", "No touchscreen", "No keyboard/mouse"),
    ("Would you rather be allergic to chocolate or allergic to cheese?", "Chocolate", "Cheese"),
    ("Would you rather always have to say everything on your mind or never speak again?", "Say everything", "Never speak"),
    ("Would you rather have a pet dragon or a pet unicorn?", "Dragon", "Unicorn"),
    ("Would you rather be the smartest person in the room or the funniest?", "Smartest", "Funniest"),
    ("Would you rather only be able to eat sweet or only be able to eat salty foods?", "Sweet", "Salty"),
    ("Would you rather have super speed or super strength?", "Super speed", "Super strength"),
    ("Would you rather live without caffeine or live without sugar?", "No caffeine", "No sugar"),
    ("Would you rather go back in time to meet your ancestors or forward to meet your descendants?", "Back in time", "Forward in time"),
    ("Would you rather have free flights for life or free hotel stays?", "Free flights", "Free hotels"),
    ("Would you rather never use social media again or never watch TV again?", "No social media", "No TV"),
    ("Would you rather be able to breathe underwater or be able to fly?", "Breathe underwater", "Fly"),
    ("Would you rather always have a full phone battery or always have a full tank of gas?", "Full phone battery", "Full gas tank"),
    ("Would you rather live on the Moon or live on Mars?", "Moon", "Mars"),
    ("Would you rather have unlimited free pizza or unlimited free sushi?", "Pizza", "Sushi"),
    ("Would you rather never have to do laundry or never have to wash dishes?", "No laundry", "No dishes"),
    ("Would you rather have a pause or rewind button in your life?", "Pause", "Rewind"),

    # Dark humor / mild adult
    ("Would you rather have a zombie apocalypse or robot takeover happen first?", "Zombie apocalypse", "Robot takeover"),
    ("Would you rather forget who you are every morning or never be able to remember anyone else's name?", "Forget self", "Forget others"),
    ("Would you rather be infamous in history or forgotten completely?", "Infamous", "Forgotten"),
    ("Would you rather always have bad luck or never be able to catch a break?", "Always bad luck", "Never catch a break"),
    ("Would you rather live forever but be poor or live one year rich and famous?", "Forever poor", "One year rich"),
    ("Would you rather always have to whisper during intimate moments or always shout?", "Whisper", "Shout"),
    ("Would you rather have your parents walk in on you or your boss?", "Parents", "Boss"),
    ("Would you rather kiss a stranger or hug a stranger?", "Kiss", "Hug"),
    ("Would you rather be caught watching an embarrassing video or caught singing out loud?", "Watching video", "Singing out loud"),
    ("Would you rather have a one night stand with your celebrity crush or date your best friend forever?", "One night stand", "Date best friend"),
    ("Would you rather never have sex again or never eat your favorite food again?", "No sex", "No favorite food"),
    ("Would you rather have a terrible date but a great story or a boring date with no story?", "Terrible date", "Boring date"),
    ("Would you rather always be turned on or never be able to get aroused?", "Always turned on", "Never aroused"),
    ("Would you rather send a sext to the wrong person or receive a sext by mistake?", "Send to wrong person", "Receive by mistake"),
    ("Would you rather live in a horror movie or a comedy movie?", "Horror", "Comedy"),
    ("Would you rather have your thoughts broadcasted for a day or never be able to speak your mind again?", "Thoughts broadcasted", "Never speak mind"),
    ("Would you rather accidentally like a 5-year-old post on your crush's profile or accidentally send a text about your crush to them?", "Like old post", "Send text"),
    ("Would you rather lose all your money or all your memories?", "Lose money", "Lose memories"),
    ("Would you rather be in jail for a year or lose a year off your life?", "Jail year", "Lose year"),
    ("Would you rather be rich and alone or poor with a huge family?", "Rich alone", "Poor family"),
]

@bot.command(name="wouldyourather", aliases=["wyr"])
@command_category("Fun")
async def wouldyourather(ctx):
    question, option1, option2 = random.choice(questions)

    embed = discord.Embed(
        title="🤔 Would You Rather...",
        description=f"**{question}**\n\n"
                    f"🅰️ {option1}\n"
                    f"🅱️ {option2}",
        color=discord.Color(0xA5EB78)
    )
    message = await ctx.send(embed=embed)
    await message.add_reaction("🅰️")
    await message.add_reaction("🅱️")

@bot.command(name="qp")
async def quickpoll(ctx, *, question: str):
    # Just add reactions to the message that invoked the command
    await ctx.message.add_reaction("⬆️")
    await ctx.message.add_reaction("⬇️")

sexts = [
    "I can’t stop imagining your body pressed against mine, feeling every curve and every inch. 🔥",
    "I want to run my hands all over you and hear you moan my name. 😈",
    "Thinking about sliding inside you slowly and making you scream with pleasure. 😏",
    "I’m craving the taste of your skin and the heat of your breath on my neck.",
    "I want to explore every part of you until you’re begging for more.",
    "My fingers are itching to tease you, to find all your secret spots.",
    "I’m dying to feel you trembling under my touch, lost in pure ecstasy.",
    "Imagining you naked, spread out for me, ready for all the things I want to do.",
    "I want to bury myself deep inside you and never let go.",
    "I’ll make you forget your own name with every stroke and kiss.",
    "I want to hear you gasp and cry out as I push you to the edge again and again.",
    "I’m ready to taste you, worship you, and drive you wild all night long.",
    "My lips will leave marks all over your body while my hands roam freely.",
    "I want to dominate you, making you surrender to every wicked desire.",
    "Let me be the fire that burns through your skin and the addiction you can’t quit.",
    "I want to feel your breath hitch as I kiss down your neck.",
    "My hands ache to trace the curves of your body under the moonlight.",
    "Imagine my lips trailing down your spine, setting your skin on fire.",
    "I want to hear your moans echo as I explore every inch of you.",
    "Let me be the reason you can’t sleep tonight — and I won’t stop until dawn.",
    "I’m obsessed with the way your body responds to my touch.",
    "I want to pull you close and lose myself inside your heat.",
    "Your skin tastes like heaven, and I can’t get enough.",
    "I want to make you scream louder than you ever thought possible.",
    "My lips crave the taste of you, and my hands want to feel your every curve.",
    "Let me tease you until you’re trembling, begging for more.",
    "I want to take you slowly, savoring every second and every gasp.",
    "You’re my favorite addiction, and I’m hopelessly hooked.",
    "I want to discover all your secret places and worship them.",
    "Imagine me whispering naughty things into your ear as my hands roam your body.",
    "I want to feel your nails digging into my back as I lose control.",
    "Let me be the one who wakes you up with kisses and takes you again and again.",
    "I can’t wait to hear you say my name between gasps and moans.",
    "The thought of you naked drives me crazy — I need you now.",
    "I want to trace my fingers along your spine, feeling every shiver.",
    "You have no idea how badly I want you right now — and I won’t wait.",
    "Let me show you just how much I want you, starting with slow, deep kisses.",
    "I want to feel your body arch under mine, craving every touch.",
    "I’m already picturing us tangled in sheets, lost in desire.",
    "The idea of your skin on mine is making me burn up.",
    "I want to explore your body like a map, discovering every secret spot.",
    "Your moans are the sweetest music, and I want to hear more.",
    "I want to take you to places you’ve never been, pleasure you’ve never known.",
]

@bot.command()
@command_category("Fun")
async def sext(ctx, member: discord.Member):
    msg = random.choice(sexts)
    embed = discord.Embed(description=msg, color=0xA5EB78)
    embed.set_author(name=f"{ctx.author.display_name} said to {member.display_name}")
    await ctx.send(embed=embed)

nsfw_urls = [
    "https://nekobot.xyz/api/image?type=hentai",
    "https://nekobot.xyz/api/image?type=hboobs",
    "https://nekobot.xyz/api/image?type=hentai_anal",
    "https://nekobot.xyz/api/image?type=hyuri",
    "https://nekobot.xyz/api/image?type=hass",
    "https://nekobot.xyz/api/image?type=hmidriff",
    "https://nekobot.xyz/api/image?type=paizuri",
    "https://nekobot.xyz/api/image?type=tentacle",
    "https://nekobot.xyz/api/image?type=hkitsune"
]

auto_post_channels = {}

async def fetch_nsfw_image():
    api_url = random.choice(nsfw_urls)
    try:
        response = requests.get(api_url)
        data = response.json()
        return data.get("message")
    except Exception as e:
        print(f"Failed to fetch image: {e}")
        return None
    
from discord.ext import commands, tasks
@bot.command()
@commands.has_permissions(manage_channels=True, manage_webhooks=True)
@command_category("NSFW")
async def hentai(ctx):
    guild = ctx.guild

    existing_channel = discord.utils.get(guild.channels, name="hentai")
    if existing_channel:
        embed = discord.Embed(
            title="Channel Exists",
            description=f"The channel {existing_channel.mention} already exists! Auto-post should be running.",
            color=0xA5EB78
        )
        await ctx.send(embed=embed)
        return

    confirm_embed = discord.Embed(
        title="Confirmation Needed",
        description="This command will create an **NSFW channel** named `hentai` and start auto-posting hentai images every 1 minute.\n\nReply with `yes` to confirm or `no` to cancel.",
        color=0xA5EB78
    )
    await ctx.send(embed=confirm_embed)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["yes", "no"]

    try:
        msg = await bot.wait_for('message', check=check, timeout=30)
    except asyncio.TimeoutError:
        timeout_embed = discord.Embed(
            title="Timeout",
            description="No response received in time. Command cancelled.",
            color=0xA5EB78
        )
        await ctx.send(embed=timeout_embed)
        return

    if msg.content.lower() != "yes":
        cancel_embed = discord.Embed(
            title="Cancelled",
            description="Operation cancelled by the user.",
            color=0xA5EB78
        )
        await ctx.send(embed=cancel_embed)
        return

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
    }
    channel = await guild.create_text_channel('hentai', overwrites=overwrites, nsfw=True, reason="Created hentai channel for auto-posting")
    webhook = await channel.create_webhook(name="HentaiPoster")

    auto_post_channels[guild.id] = {
        "channel_id": channel.id,
        "webhook_id": webhook.id,
        "webhook_token": webhook.token
    }

    success_embed = discord.Embed(
        title="Channel Created!",
        description=f"Created channel {channel.mention} and started auto-posting hentai images every 10 minutes.\nDelete the channel to stop.",
        color=0xE91E63
    )
    await ctx.send(embed=success_embed)

    if not auto_poster.is_running():
        auto_poster.start()

@tasks.loop(minutes=1)
async def auto_poster():
    for guild_id, data in list(auto_post_channels.items()):
        guild = bot.get_guild(guild_id)
        if not guild:
            auto_post_channels.pop(guild_id)
            continue

        channel = guild.get_channel(data["channel_id"])
        if not channel:
            auto_post_channels.pop(guild_id)
            continue

        try:
            webhook = discord.Webhook.partial(data["webhook_id"], data["webhook_token"], adapter=discord.RequestsWebhookAdapter())
        except Exception as e:
            print(f"Failed to get webhook for guild {guild_id}: {e}")
            auto_post_channels.pop(guild_id)
            continue

        image_url = await fetch_nsfw_image()
        if not image_url:
            continue

        embed = discord.Embed(
            title="💖 Here's something spicy for you!",
            description="Enjoy a fresh Hentai drop. 🔞",
            color=0xE91E63,
            timestamp=datetime.utcnow()
        )
        embed.set_image(url=image_url)
        embed.set_footer(text="AutoPoster by refected bot")

        try:
            await webhook.send(embed=embed, username="refected", avatar_url="https://i.postimg.cc/PxbPZ8yk/1159e3a020be04eede0cb5506b3517da.jpg")
        except Exception as e:
            print(f"Failed to send webhook message in guild {guild_id}: {e}")

@bot.event
async def on_guild_channel_delete(channel):
    if channel.name == "hentai" and channel.guild.id in auto_post_channels:
        data = auto_post_channels[channel.guild.id]
        if data["channel_id"] == channel.id:
            auto_post_channels.pop(channel.guild.id)
            print(f"Stopped auto-posting for guild {channel.guild.id} because hentai channel was deleted.")

@auto_poster.before_loop
async def before_auto_poster():
    await bot.wait_until_ready()

bot.run(TOKEN)
