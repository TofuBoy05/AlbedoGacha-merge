import asyncio
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging

load_dotenv()
TOKEN = os.getenv('TOKEN')
TOKEN2 = os.getenv('TOKEN2')
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix= "!", intents=intents, help_command=None, application_id='1007934486815723520')

async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
    # for filename in os.listdir('./cogs2'):
    #     if filename.endswith('.py'):
    #         await bot.load_extension(f'cogs.{filename[:-3]}')

async def main():
    await load()
    await bot.start(TOKEN)

@bot.command()
@commands.has_any_role(1008304083213488229, 904248711771746314)
async def l(ctx, extension):
  await bot.load_extension(f'cogs.{extension}')

@bot.command()
@commands.has_any_role(1008304083213488229, 904248711771746314)
async def ul(ctx, extension):
  await bot.unload_extension(f'cogs.{extension}')

@bot.command()
@commands.has_any_role(1008304083213488229, 904248711771746314)
async def r(ctx, extension):
  await ctx.message.delete()
  await bot.unload_extension(f'cogs.{extension}')
  await bot.load_extension(f'cogs.{extension}')


asyncio.run(main())