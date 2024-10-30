import discord

class CargoManager:
    def __init__(self, guild):
        self.guild = guild
        self.cargos = {
            1: 1300853285858578543,
            2: 1300850877585690655,
            3: 1300854639658270761
        }
        self.premios = {
            1: "SNIPER EMBERIUM",
            2: "SNIPER BOSS",
            3: "SNIPER ADAMANTY"
        }

    async def atribuir_cargos(self, top_jogadores):
        # Atribuir cargos com base nos três maiores danos
        for rank, (player_id, dano) in enumerate(top_jogadores, start=1):
            cargo_id = self.cargos.get(rank)
            premio = self.premios.get(rank)
            if cargo_id:
                member = self.guild.get_member(player_id)
                cargo = self.guild.get_role(cargo_id)
                if member and cargo:
                    await member.add_roles(cargo)
                    # Mensagem de premiação com chance de quebra
                    if random.random() > 0.3:  # 30% de chance de quebrar
                        await member.send(f"Você recebeu o prêmio: {premio}!")
                    else:
                        await member.send(f"O prêmio {premio} quebrou!")
