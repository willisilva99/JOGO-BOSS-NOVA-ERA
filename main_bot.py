import discord
from discord.ext import commands, tasks
import os
from database import Database
from boss import Boss
from cargos import CargoManager
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Variáveis e configuração do boss e do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL")
database = Database(DATABASE_URL)
boss = Boss(1000)  # HP inicial do boss
cargo_manager = None

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    guild = bot.guilds[0]  # Pega a primeira guilda
    global cargo_manager
    cargo_manager = CargoManager(guild)
    database.setup()
    atualizar_cargos.start()

@bot.command()
async def atacar(ctx, dano: int):
    player_id = ctx.author.id
    # Verifica se o dano é um número válido
    if dano <= 0:
        await ctx.send("O dano deve ser um número positivo.")
        return

    if boss.receber_dano(dano):
        await ctx.send("O boss foi derrotado!")
        # Reseta o HP ou redefine o boss para uma nova fase

    else:
        contra_ataque = boss.contra_atacar()
        if contra_ataque == "contra_atacar":
            await ctx.send(f"{ctx.author.mention}, o boss contra-atacou!")
        elif contra_ataque == "roubar_premio":
            await ctx.send(f"{ctx.author.mention}, o boss roubou seu prêmio!")

    # Adiciona o dano ao banco de dados
    database.add_dano(player_id, dano)
    
    # Mensagem de confirmação de dano
    await ctx.send(f"{ctx.author.mention}, você causou {dano} de dano ao boss.")

@tasks.loop(minutes=5)
async def atualizar_cargos():
    top_jogadores = database.get_top_danos()
    
    if top_jogadores:
        await cargo_manager.atribuir_cargos(top_jogadores)

        # Mensagem de atualização
        jogadores_mensagem = ', '.join([f"<@{player_id}> (Dano: {dano})" for player_id, dano in top_jogadores])
        channel_id = <1299092242673303552>  # Substitua pelo ID do canal
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(f"Atualização de danos: {jogadores_mensagem}")

bot.run(os.getenv("TOKEN"))
