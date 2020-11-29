import asyncio
import discord
from discord import File as File
from discord.ext import commands
from random import choice

class Default(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server_role = None
        self.former_role = None
        self.captain_role = None
        self.coach_role = None
        self.team_roles = []
        self.saved_message = ""

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in and listening as {self.bot.user}!")
        await self.bot.change_presence(activity=discord.Game(name="Electric Mayhem"))  # Set Discord status

        for guild in self.bot.guilds:
            if guild.name == "Electric Mayhem (Flez)":
                for role in guild.roles:
                    if role.name == "EM|Electric Mayhem":
                        self.server_role = role
                    elif role.name == "Former Player":
                        self.former_role = role
                    elif role.name == "Captains":
                        self.captain_role = role
                    elif role.name == "Coach":
                        self.coach_role = role
                    for team in "Premier,Master,Elite,Major,Minor,Challenger,Prospect,Contender,Amateur".split(","):
                        if team in role.name:
                            self.team_roles.append(role)

        # print(self.server_role, self.former_role, self.captain_role, self.coach_role)

    @commands.command()
    async def send(self, ctx, member: discord.member.Member, *message):
        mes = ""
        for m in message:
            mes += str(m) + " "
        await member.send(f"{mes[:-1]}")
        await ctx.send(f"Message sent to <@{member.id}> member.")

    @commands.command()
    async def send_saved_message(self, ctx, *members: discord.member.Member):
        for member in members:
            await member.send(f"{self.saved_message}")
        await ctx.send(f"Messages sent to {len(members)} members.")

    @commands.command()
    async def save_message(self, ctx, *message):
        mes = ""
        for m in message:
            mes += str(m) + " "
        self.saved_message = f"{mes[:-1]}"
        msg= await ctx.send(f"Saved Message: \"{self.saved_message}\"")
        await asyncio.sleep(30)
        await ctx.message.delete()
        await msg.delete()

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author == self.bot.user:
            return
        # if 'hello' in ctx.content.lower():
        #     await ctx.channel.send("Hello!")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, arg: int):
        print(f"Clearing {arg} messages.")
        messages = await ctx.channel.history(limit=arg).flatten()
        for message in reversed(messages):
            await message.delete()

    @commands.command()
    async def format(self, ctx):
        await ctx.send(f"__Stars__\nRole (Role), Channel to Send Message (TextChannel), Week Number (Int), Star 1 (Member), Star 2 (Member), "
                 f"Star 3 (Member), Team of the Week (Role), Team of the Week Team Channel (TextChannel), "
                       f"Time to Wait _Optional_ (Seconds)\n\n__Sign__\nPlayer (Member), Team (Role), Time to Wait _Optional"
                       f"_ (Seconds)\n\n__Cut__\nPlayer (Member), Time to Wait _Optional_ (Seconds)\n\n__Promote__\n"
                       f"Player (Member), Team (Role), Time for (xhymzs) Ex. 6h20m30s = 6 hours 20 minutes 30 seconds")
        await ctx.message.delete()

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def stars(self, ctx, role: discord.role.Role, to_send: discord.channel.TextChannel, week_num: int,
                   member1: discord.member.Member, member2: discord.member.Member, member3: discord.member.Member,
                   team_of_week: discord.role.Role, team_channel: discord.channel.TextChannel, wait_time=0):
        await asyncio.sleep(wait_time)

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
                try:
                    await self.remove_star(member)
                except Exception as e:
                    ctx.send(f"{e}")
            elif member in star_members:
                try:
                    if member.nick is None:
                        nick = member.name + star
                    else:
                        nick = member.nick + star
                    await member.edit(nick=nick)
                except Exception as e:
                    ctx.send(f"{e}")

        for channel in channels_in_category:
            if channel == team_channel:
                await channel.edit(name=channel.name + star)
            else:
                await self.remove_star_chat(channel)

        msg = await to_send.send(f"Hello <@&{role.id}>, here are your 3 Stars of the Week for Week {week_num}, <@{member1.id}>,"
                       f" <@{member2.id}>, and <@{member3.id}>, and your team of the week <@&{team_of_week.id}>!",
                       file=File("./Stars of the Week.png", spoiler=False))
        try:
            await msg.add_reaction(ctx.guild.get_emoji(563508808073216021))
        except Exception as e:
            await ctx.send(f"{e}")
        await team_channel.send(f"Congrats on team of the week <@&{team_of_week.id}>!")
        await ctx.send(f"Stars of the week for week {week_num} was successful!")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def stars2(self, ctx, role: discord.role.Role, to_send: discord.channel.TextChannel, week_num: int,
                    member1: discord.member.Member, member2: discord.member.Member, member3: discord.member.Member,
                    team_of_week: discord.role.Role, team_channel: discord.channel.TextChannel, wait_time=0):
        await asyncio.sleep(wait_time)

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
            if member in star_members:
                try:
                    if member.nick is None:
                        nick = member.name + star
                    else:
                        nick = member.nick + star
                    await member.edit(nick=nick)
                except Exception as e:
                    ctx.send(f"{e}")

        for channel in channels_in_category:
            if channel == team_channel:
                await channel.edit(name=channel.name + star)

        msg = await to_send.send(
            f"Hello <@&{role.id}>, here are your 3 Stars of the Week for Week {week_num}, <@{member1.id}>,"
            f" <@{member2.id}>, and <@{member3.id}>, and your team of the week <@&{team_of_week.id}>!",
            file=File("./Stars of the Week.png", spoiler=False))

        try:
            await msg.add_reaction(ctx.guild.get_emoji(563508808073216021))
        except Exception as e:
            await ctx.send(f"{e}")

        await team_channel.send(f"Congrats on team of the week <@&{team_of_week.id}>!")
        await ctx.send(f"Stars of the week for week {week_num} was successful!")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def give_star(self, ctx, member: discord.member.Member):
        star = "⭐"
        if member.nick is None:
            nick = member.name + star
        else:
            nick = member.nick + star
        await member.edit(nick=nick)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def show_stars(self, ctx):
        await ctx.send(file=File("./Stars of the Week.png"))

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def emojis(self, ctx):
        for emoji in ctx.guild.emojis:
            await ctx.send(f"{emoji}:{emoji.id}")

    async def remove_star(self, member):
        if member.nick is None:
            print(f"{member.name} has no nickname.")
            return
        while "⭐" in member.nick:
            i = member.nick.index("⭐")
            nick = member.nick[0:i] + member.nick[i+1:]
            await member.edit(nick=nick)
            if member.nick is None:
                return

    async def remove_star_chat(self, channel):
        while "⭐" in channel.name:
            i = channel.name.index("⭐")
            name = channel.name[0:i] + channel.name[i+1:]
            await channel.edit(name=name)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def sign(self, ctx, player: discord.member.Member, team: discord.role.Role, wait_time=0):
        await asyncio.sleep(int(wait_time))

        if self.server_role is None:
            return
        try:
            await player.add_roles(self.server_role, team)
            await ctx.send(f"Signed <@{player.id}> to <@&{team.id}>")
        except Exception as e:
            await ctx.send(f"Failed to sign <@{player.id}> from Electric Mayhem\nReason: {e}")
            print(e)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def cut(self, ctx, *players: discord.member.Member):
        for player in players:
            try:
                await player.remove_roles(self.server_role)
                await player.add_roles(self.former_role)

                if self.captain_role in player.roles:
                    await player.remove_roles(self.captain_role)

                if self.coach_role in player.roles:
                    await player.remove_roles(self.coach_role)

                for role in self.team_roles:
                    if role in player.roles:
                        await player.remove_roles(role)
                await ctx.send(f"Cut <@{player.id}> from Electric Mayhem")
            except Exception as e:
                await ctx.send(f"Failed to cut <@{player.id}> from Electric Mayhem\nReason: {e}")
                print(e)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def promote(self, ctx, player: discord.member.Member, team: discord.role.Role, time: str):
        try:
            await ctx.send(f"Promoting <@{player.id}> for {self.convert_time(time)} seconds.")
            await player.add_roles(team)
            await asyncio.sleep(self.convert_time(time))
            await player.remove_roles(team)
            await ctx.send(f"Promotion time of <@{player.id}> has ended.")
        except Exception as e:
            await ctx.send(f"Failed to promote <@{player.id}>. Reason: {e}")
            print(e)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def tempsub(self, ctx, player: discord.member.Member, team: discord.role.Role, time: str, channel=None, msg=None):
        try:
            await ctx.send(f"Subbing <@{player.id}> for {self.convert_time(time)} seconds.")
            await player.add_roles(team, self.server_role)

            if channel is not None and msg is not None:
                await channel.send(f"Welcome to Electric Mayhem, <@{player.id}! Thank you for subbing tonight for <@&{team.id}!")

            await asyncio.sleep(self.convert_time(time))
            await player.remove_roles(team)
            await player.add_roles(self.former_role)
            await ctx.send(f"Sub time of <@{player.id}> has ended.")
        except Exception as e:
            await ctx.send(f"Failed to tempsub <@{player.id}>. Reason: {e}")
            print(e)

    @commands.command()
    async def id(self, ctx, member: discord.member.Member):
        await ctx.send(f"{member.id}")

    @staticmethod
    def convert_time(string: str):
        total = 0
        if "h" in string:
            i = string.index("h")
            time = int(string[0:i])
            total += 60 * 60 * time
            string = string[i + 1::]
        if "m" in string:
            i = string.index("m")
            time = int(string[0:i])
            total += 60 * time
            string = string[i + 1::]
        if "s" in string:
            i = string.index("s")
            time = int(string[0:i])
            total += time
            string = string[i + 1::]
        return total
