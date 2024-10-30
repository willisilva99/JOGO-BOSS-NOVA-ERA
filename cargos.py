import random
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
        cargos_atuais = {}
        
        # Atribuir cargos com base nos três maiores danos
        for rank, (player_id, dano) in enumerate(top_jogadores, start=1):
            cargo_id = self.cargos.get(rank)
            premio = self.premios.get(rank)
            if cargo_id:
                cargos_atuais[player_id] = cargo_id  # Armazena os cargos a serem atribuídos
                member = self.guild.get_member(player_id)
                cargo = self.guild.get_role(cargo_id)
                if member and cargo:
                    await member.add_roles(cargo)
                    await member.send(f"Você recebeu o prêmio: {premio}!")

        # Remover cargos dos jogadores que não estão mais nos 3 primeiros
        for member in self.guild.members:
            if member.id not in cargos_atuais:
                for rank in self.cargos.keys():
                    cargo_id = self.cargos[rank]
                    cargo = self.guild.get_role(cargo_id)
                    if cargo in member.roles:
                        await member.remove_roles(cargo)
                        await member.send(f"Você perdeu o cargo: {cargo.name}.")
