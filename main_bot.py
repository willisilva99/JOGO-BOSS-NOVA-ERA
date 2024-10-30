import discord
from discord.ext import commands, tasks
import os
import random
import asyncio
from database import Database
from boss import Boss
from cargos import CargoManager
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração de Intents do bot
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Configuração de variáveis
DATABASE_URL = os.getenv("DATABASE_URL")
TOKEN = os.getenv("TOKEN")  # Certifique-se de que a variável TOKEN está configurada no arquivo .env
database = Database(DATABASE_URL)
boss = Boss(1000)
cargo_manager = None

@bot.event
async def on_ready():
    global cargo_manager
    database.connect()

    # Verificar conexão com o banco de dados
    if database.conn is None:
        print("Falha ao conectar ao banco de dados. O bot não pode continuar.")
        return

    print(f"Logged in as {bot.user}")

    # Verificar se o bot está em alguma guilda
    if not bot.guilds:
        print("O bot não está em nenhuma guilda. Adicione o bot a um servidor.")
        return

    guild = bot.guilds[0]
    cargo_manager = CargoManager(guild)
    database.setup()
    atualizar_cargos.start()

@bot.command()
async def atacar(ctx):
    player_id = ctx.author.id
    dano = random.randint(10, 50)

    if random.random() < 0.3:
        dano = 0

    if dano > 0:
        if boss.receber_dano(dano):
            await ctx.send("O boss foi derrotado!")
        else:
            message = await ctx.send(f"{ctx.author.mention}, você causou {dano} de dano ao boss. Reaja para verificar sua posição no top 3!")
            await message.add_reaction("👍")

            def check(reaction, user):
                return user == ctx.author and reaction.message.id == message.id and str(reaction.emoji) == "👍"

            try:
                await bot.wait_for("reaction_add", timeout=30.0, check=check)
                await verificar_top(ctx.author)
            except asyncio.TimeoutError:
                await ctx.send(f"{ctx.author.mention}, você não reagiu a tempo!")

    else:
        await ctx.send(f"{ctx.author.mention}, o boss bloqueou seu ataque!")

    database.add_dano(player_id, dano)

async def verificar_top(player):
    top_jogadores = database.get_top_danos(3)
    guild = bot.guilds[0]
    cargos_ids = {1: 1300853285858578543, 2: 1300850877585690655, 3: 1300854639658270761}

    for rank, (player_id, _) in enumerate(top_jogadores, start=1):
        cargo_id = cargos_ids.get(rank)
        if cargo_id:
            member = guild.get_member(player_id)
            cargo = guild.get_role(cargo_id)

            if member and cargo:
                # Remove o cargo anterior do jogador que perdeu a posição
                for other_rank, other_cargo_id in cargos_ids.items():
                    other_cargo = guild.get_role(other_cargo_id)
                    if other_cargo in member.roles and other_cargo_id != cargo_id:
                        await member.remove_roles(other_cargo)

                # Adiciona o novo cargo ao jogador na posição correta
                if cargo not in member.roles:
                    await member.add_roles(cargo)
                    try:
                        await member.send(f"Você agora ocupa a posição {rank} no ranking e recebeu o cargo: {cargo.name}!")
                    except discord.Forbidden:
                        print(f"Não foi possível enviar mensagem para {member.name}.")
                    
                print(f"Atribuído {cargo.name} a {member.name} com dano acumulado.")

@tasks.loop(minutes=5)
async def atualizar_cargos():
    top_jogadores = database.get_top_danos()
    
    if top_jogadores:
        await cargo_manager.atribuir_cargos(top_jogadores)

        # Mensagem de atualização
        jogadores_mensagem = ', '.join([f"<@{player_id}> (Dano: {dano})" for player_id, dano in top_jogadores])
        channel_id = 1299092242673303552  # ID do canal
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(f"Atualização de danos: {jogadores_mensagem}")

# Executa o bot
if TOKEN is None:
    print("TOKEN não encontrado. Certifique-se de que a variável TOKEN está definida no arquivo .env.")
else:
    bot.run(TOKEN)
