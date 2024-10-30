import discord
from discord.ext import commands, tasks
import os
import random
import asyncio  # Adicione esta linha
from database import Database
from boss import Boss
from cargos import CargoManager
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True  # Permite que o bot gerencie reações
bot = commands.Bot(command_prefix="!", intents=intents)

# Variáveis e configuração do boss e do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL")
database = Database(DATABASE_URL)
boss = Boss(1000)  # HP inicial do boss
cargo_manager = None

@bot.event
async def on_ready():
    global cargo_manager

    # Conectar ao banco de dados
    database.connect()
    
    # Verificar se a conexão foi bem-sucedida
    if database.conn is None:
        print("Falha ao conectar ao banco de dados. O bot não pode continuar.")
        return

    print(f"Logged in as {bot.user}")
    guild = bot.guilds[0]  # Pega a primeira guilda
    cargo_manager = CargoManager(guild)
    database.setup()  # Configurar a tabela
    atualizar_cargos.start()

@bot.command()
async def atacar(ctx):
    player_id = ctx.author.id

    # Gera um dano aleatório entre 10 e 50
    dano = random.randint(10, 50)
    
    # Chance de bloqueio do boss (30% de chance)
    if random.random() < 0.3:  # 30% de chance
        dano = 0  # O boss bloqueou o ataque

    if dano > 0:
        if boss.receber_dano(dano):
            await ctx.send("O boss foi derrotado!")
            # Aqui você pode adicionar lógica para redefinir o boss
        else:
            message = await ctx.send(f"{ctx.author.mention}, você causou {dano} de dano ao boss. Reaja para verificar a chance de ganhar um cargo!")
            await message.add_reaction("👍")  # Adiciona uma reação à mensagem

            def check(reaction, user):
                return user == ctx.author and reaction.message.id == message.id and str(reaction.emoji) == "👍"

            try:
                await bot.wait_for("reaction_add", timeout=30.0, check=check)  # Aguarda a reação por 30 segundos
                await ctx.send(f"{ctx.author.mention}, você reagiu e agora verificamos se você ganha um cargo...")
                await verificar_cargo(ctx.author)
            except asyncio.TimeoutError:
                await ctx.send(f"{ctx.author.mention}, você não reagiu a tempo!")

    else:
        await ctx.send(f"{ctx.author.mention}, o boss bloqueou seu ataque!")

    # Adiciona o dano ao banco de dados
    database.add_dano(player_id, dano)

async def verificar_cargo(player):
    top_jogadores = database.get_top_danos()
    if any(player.id == player_id for player_id, _ in top_jogadores):
        cargo_id = 1300853285858578543  # Substitua pelo ID do cargo correto
        member = bot.get_guild(player.guild.id).get_member(player.id)
        
        if member is not None:
            cargo = member.guild.get_role(cargo_id)
            if cargo:
                await member.add_roles(cargo)
                await player.send(f"Você ganhou o cargo: {cargo.name}!")
            else:
                await player.send("Cargo não encontrado.")
        else:
            await player.send("Membro não encontrado no guilda.")
    else:
        await player.send("Você não está entre os três maiores danos.")

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
bot.run(os.getenv("TOKEN"))
