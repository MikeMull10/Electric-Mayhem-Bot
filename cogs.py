import asyncio
import discord
from discord import File as File
from discord.ext import commands

class Default(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in and listening as {self.bot.user}!")
        await self.bot.change_presence(activity=discord.Game(name="being Programmed"))  # Set Discord status

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author == self.bot.user:
            return
        if 'hello' in ctx.content.lower():
            await ctx.channel.send("Hello!")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, arg: int):
        print(f"Clearing {arg} messages.")
        messages = await ctx.channel.history(limit=arg).flatten()
        for message in reversed(messages):
            await message.delete()

    @commands.command()
    async def format(self, ctx):
        await ctx.send(f"Role (Role), Channel to Send Message (TextChannel), Week Number (Int), Star 1 (Member), Star 2 (Member), "
                 f"Star 3 (Member), Team of the Week (Role), Team of the Week Team Channel (TextChannel)")

    @commands.command()
    async def send(self, ctx, role: discord.role.Role, to_send: discord.channel.TextChannel, week_num: int,
                   member1: discord.member.Member, member2: discord.member.Member, member3: discord.member.Member,
                   team_of_week: discord.role.Role, team_channel: discord.channel.TextChannel):
        star = "⭐"
        members_with_role = []
        star_members = [member1, member2, member3]
        channels_in_category = []

        for member in ctx.guild.members:
            if role in member.roles:
                members_with_role.append(member)
        for channel in ctx.guild.channels:
            if channel.category_id == team_channel.category_id:
                channels_in_category.append(channel)

        for member in members_with_role:
            if member not in star_members:
                await self.remove_star(member)
            elif member in star_members:
                nick = member.nick + star
                await member.edit(nick=nick)

        for channel in channels_in_category:
            if channel == team_channel:
                await channel.edit(name=channel.name + star)
            else:
                await self.remove_star_chat(channel)

        await to_send.send(f"Hello <@&{role.id}>, here are your 3 Stars of the Week for Week {week_num}, <@{member1.id}>,"
                       f"<@{member2.id}>, and <@{member3.id}>, and your team of the week <@&{team_of_week.id}>!",
                       file=File("./Stars of the Week.png", spoiler=False))

    async def remove_star(self, member):
        while "⭐" in member.nick:
            i = member.nick.index("⭐")
            nick = member.nick[0:i] + member.nick[i+1:]
            await member.edit(nick=nick)

    async def remove_star_chat(self, channel):
        while "⭐" in channel.name:
            i = channel.name.index("⭐")
            name = channel.name[0:i] + channel.name[i+1:]
            await channel.edit(name=name)


    @commands.command()
    async def setup(self, ctx):
        guild = ctx.guild
        # Category/Channel creation
        category = discord.utils.find(lambda cat: cat.name == "Game Channels", guild.categories)
        if category is None:
            category = await guild.create_category("Game Channels")
        channel = discord.utils.get(category.channels, name="Join for Game Channel", type=discord.ChannelType.voice)
        if channel is None:
            channel = await guild.create_voice_channel('Join for Game Channel', category=category)
        bots_message = await ctx.send("Game channel setup complete.")
        await ctx.message.delete()
        await asyncio.sleep(5)
        await bots_message.delete()
