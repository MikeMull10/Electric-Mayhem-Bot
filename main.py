from discord.ext import commands
from cogs import *

bot = commands.Bot(command_prefix=get_key("prefix"))

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(error)

cogs = [Default(bot)]
for cog in cogs:
    bot.add_cog(cog)
    print(f"Loaded \"{cog.qualified_name}\" cog!")

bot.run(get_key("token"))
