from discord import File as File
from discord.ext import commands
from Defs import PlayerStats, get_stats, get_stat, titles, get_key
import requests
import asyncio
import discord
import bs4

class Default(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server_role, self.former_role, self.captain_role, self.coach_role, self.scout_role = None, None, None, None, None
        self.team_roles = []
        self.saved_message = ""

        self.link = "https://www.rocketsoccarconfederation.com/na/s9-stats/s9-player-stats/"
        self.tiers = "Premier,Master,Elite,Major,Minor,Challenger,Prospect,Contender,Amateur".split(",")

        self.stats = []
        self.stats_names = []
        self.table_min = 446

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
                    elif role.name == "Scout":
                        self.scout_role = role
                    for team in "Chargers (Premier),Blackout (Master),Bolts (Elite),Lightning (Major),Surge (Minor),Shock (Challenger),Sparks (Prospect),Thunder Buddies (Contender),Watts (Amateur)".split(","):
                        if team in role.name:
                            self.team_roles.append(role)

    @commands.command()
    async def set_status(self, ctx, *status):
        s = ""
        for stat in status:
            s += str(stat) + " "
        await self.bot.change_presence(activity=discord.Game(name=str(s[:-1])))
        await ctx.send(f"Status changed to: {str(s)}")

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
    async def send_saved_team_message(self, ctx, *roles: discord.role.Role):
        for player in ctx.guild.members:
            for role in roles:
                if role in player.roles:
                    ctx.send(f"{self.saved_message}")
                    break

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

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, arg: int):
        print(f"Clearing {arg} messages.")
        messages = await ctx.channel.history(limit=arg + 1).flatten()
        for message in reversed(messages):
            await message.delete()

    @commands.command()
    async def stats(self, ctx, *player):
        player_name = ""
        for p in player:
            player_name += p + " "
        player_name = player_name[:-1]

        if self.stats is []:
            await self.update_stats(ctx)

        for stat in self.stats:
            if stat.name.lower() == player_name.lower():
                embed = discord.Embed(
                    title=f"{player_name}\'s Stats",
                    colour=self.get_color_from_tier(stat.tier)
                )
                embed.set_thumbnail(url="https://www.rocketsoccarconfederation.com/wp-content/uploads/2018/01/cropped-rsc-logo-500-1.png")

                embed.add_field(name="Tier", value=stat.tier, inline=True)

                for i, title in enumerate(titles[2::]):
                    embed.add_field(name=title, value=stat.stats[i], inline=True)

                await ctx.send(embed=embed)
                return
        await ctx.send(f"Player \'{player_name}\' not Found")

    @commands.command()
    async def update_stats(self, ctx):
        self.stats = []
        self.stats_names = []

        stats = bs4.BeautifulSoup(requests.get(self.link).text, "lxml")
        table_nums = [i for i in range(self.table_min, self.table_min + 9)]
        tables = []

        for num in table_nums:
            tables.append(stats.find(id=f"tablepress-{num}"))

        for a, table in enumerate(tables):

            table_sliced = None
            for i, _line in enumerate(table):
                if i == 3:
                    table_sliced = str(_line).split("</tr>")

            for stats in table_sliced:
                name = get_stat(stats, "column-1")
                if name is None:
                    continue
                self.stats.append(PlayerStats(self.tiers[a], name, get_stats(stats)))
                self.stats_names.append(name)

        self.remove_duplicates()

    @staticmethod
    def get_color_from_tier(tier):
        if tier == "Premier":
            return discord.Colour.from_rgb(255, 0, 255)
        elif tier == "Master":
            return discord.Colour.from_rgb(148, 115, 199)
        elif tier == "Elite":
            return discord.Colour.from_rgb(96, 167, 224)
        elif tier == "Major":
            return discord.Colour.from_rgb(79, 175, 70)
        elif tier == "Minor":
            return discord.Colour.from_rgb(255, 220, 80)
        elif tier == "Challenger":
            return discord.Colour.from_rgb(243, 141, 18)
        elif tier == "Prospect":
            return discord.Colour.from_rgb(224, 102, 102)
        elif tier == "Contender":
            return discord.Colour.from_rgb(222, 35, 0)
        elif tier == "Amateur":
            return discord.Colour.from_rgb(252, 201, 203)
        else:
            return None

    def get_stats_pos(self, user):
        if user not in self.stats_names:
            return -1
        for i, name in enumerate(self.stats_names):
            if name == user:
                return i

    def remove_duplicates(self):
        for name in self.stats_names:
            stats = []
            for stat in self.stats:
                if stat.name == name:
                    stats.append(stat)
            if len(stats) == 1:
                continue
            most_games, games = None, 0
            for stat in stats:
                if stat.games_played > games:
                    games = stat.games_played
                    most_games = stat
            for stat in stats:
                if stat != most_games:
                    self.stats.remove(stat)

    # @commands.command()
    async def format(self, ctx):
        await ctx.send(f"__Stars__\nRole (Role), Channel to Send Message (TextChannel), Week Number (Int), Star 1 (Member), Star 2 (Member), "
                 f"Star 3 (Member), Team of the Week (Role), Team of the Week Team Channel (TextChannel), "
                       f"Time to Wait _Optional_ (Seconds)\n\n__Sign__\nPlayer (Member), Team (Role), Time to Wait _Optional"
                       f"_ (Seconds)\n\n__Cut__\nPlayer (Member), Time to Wait _Optional_ (Seconds)\n\n__Promote__\n"
                       f"Player (Member), Team (Role), Time for (xhymzs) Ex. 6h20m30s = 6 hours 20 minutes 30 seconds")
        await ctx.message.delete()

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def stars(self, ctx, role: discord.role.Role, to_send: discord.channel.TextChannel, week_num: int, member1: discord.member.Member, member2: discord.member.Member, member3: discord.member.Member, team_of_week: discord.role.Role, team_channel: discord.channel.TextChannel):

        if ctx.message.attachements is []:
            await ctx.send(f"Please add an attachment when doing stars of the week.")
            return

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

        await to_send.send(f"Hello <@&{role.id}>, here are your 3 Stars of the Week for Week {week_num}, <@{member1.id}>,"
                       f" <@{member2.id}>, and <@{member3.id}>, and your team of the week <@&{team_of_week.id}>!",
                       file=ctx.message.attachments[0])

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
    async def sign(self, ctx, player: discord.member.Member, team: discord.role.Role, post_channel: discord.TextChannel=None):
        if self.server_role is None:
            return
        try:
            await player.add_roles(self.server_role, team)
            await ctx.send(f"Signed <@{player.id}> to <@&{team.id}>")
        except Exception as e:
            await ctx.send(f"Failed to sign <@{player.id}> from Electric Mayhem\nReason: {e}")
            print(e)
        if post_channel is not None:
            try:
                i = str(team.name).index("(")
                await post_channel.send(f"Welcome to the {str(team.name)[0:i - 1]}, <@{player.id}>!")
            except:
                pass

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def cut(self, ctx, *players: discord.member.Member):
        for player in players:
            try:
                await player.remove_roles(self.server_role)
                await player.add_roles(self.former_role)

                await player.remove_roles(self.captain_role)
                await player.remove_roles(self.coach_role)
                await player.remove_roles(self.scout_role)

                for role in self.team_roles:
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
    async def mvp(self, ctx, role: discord.role.Role, channel: discord.channel.TextChannel, master: discord.member.Member, elite: discord.member.Member, major: discord.member.Member,
                  minor: discord.member.Member, challenger: discord.member.Member, prospect: discord.member.Member, contender: discord.member.Member, amateur: discord.member.Member, time_to_wait=""):
        await asyncio.sleep(self.convert_time(time_to_wait))
        await channel.send(f"Hello <@&{role}>. Here are the results of the MVP voting:\n\n"
                       f"<@&{self.team_roles[1].id}>: <@{master.id}>\n"
                       f"<@&{self.team_roles[2].id}>: <@{elite.id}>\n"
                       f"<@&{self.team_roles[3].id}>: <@{major.id}>\n"
                       f"<@&{self.team_roles[4].id}>: <@{minor.id}>\n"
                       f"<@&{self.team_roles[5].id}>: <@{challenger.id}>\n"
                       f"<@&{self.team_roles[6].id}>: <@{prospect.id}>\n"
                       f"<@&{self.team_roles[7].id}>: <@{contender.id}>\n"
                       f"<@&{self.team_roles[8].id}>: <@{amateur.id}>\n\n"
                       f"Thank you all for a wonderful season 9!")
        await ctx.send(f"MVP Vote successfully sent out.")

    @commands.command()
    async def show_roles(self, ctx):
        for role in self.team_roles:
            await ctx.send(f"<@&{role.id}>")

    @commands.command()
    async def id(self, ctx, member: discord.member.Member):
        await ctx.send(f"{member.id}")

    @commands.command()
    async def restart(self, ctx):
        author_id = ctx.author.id
        if author_id == 336146049053753346:
            await ctx.send('Restarting the bot!')
            await ctx.bot.logout()
        else:
            await ctx.send(f"You don\'t have sufficient permissions to perform this action!")

    @commands.command()
    async def decal(self, ctx):
        await ctx.message.delete()
        await ctx.author.send(f"To install:\n"
                       f"0.\tMake sure you have the Alpha Console plugin installed. Here is the link if you don\'t: https://bakkesplugins.com/plugins/view/108\n\n"
                       f"1.\tGo to my drive https://drive.google.com/drive/u/0/folders/1cYqM9G1qH1NxdclEn-xbaqaH3LigSIlT and download the folder. Make sure to keep those files in the folder.\n\n"
                       f"2.\tGo to the Bakkesmod injector. If you can't find it or have it hidden, you can access it by clicking the little arrow pointed up on the right side of your task bar, and then clicking the bakkesmod image.\n\n"
                       f"3.\tWhen there, click on File > Open Bakkesmod Folder.\n\n"
                       f"4.\tIn that Folder go from data > acplugin > decal textures. Copy and paste the folder you downloaded into this folder.\n\n"
                       f"5.\tNow, open Rocket League. Navigate to the Bakkesmod plugin tab. Click on Alpha Console (Should be near the top). Navigate to the Cosmetics tab and then find the Decal Texture Mod. Now, just click on the dropdown and find the Blue and Yellow decals.\n\n"
                       f"Tip: you can\'t have a decal on your car while using this one.\n\n"
                       f"If you have any questions, please message Dolphino.")

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong")

    @commands.command()
    async def test(self, ctx):
        await ctx.send(f"Test\n{ctx.message.attachments[0].url}")

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
