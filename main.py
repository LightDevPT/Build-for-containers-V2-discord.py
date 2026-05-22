import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

COGS = [
    "cogs.components",
]

@bot.event
async def on_ready():
    print(f"{bot.user} está online!")
    try:
        synced = await bot.tree.sync()
        print(f"Comandos sincronizados: {len(synced)}")
    except Exception as error:
        print(f"Erro ao sincronizar comandos: {error}")

async def load_cogs():
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            print(f"Cog carregado: {cog}")
        except Exception as error:
            print(f"Erro ao carregar cog {cog}: {error}")

if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("Defina DISCORD_TOKEN no arquivo .env ou na variável de ambiente.")

    asyncio.run(load_cogs())
    bot.run(TOKEN)
