import discord

class CargoManager:
    def __init__(self, guild):
        self.guild = guild
        self.cargos = {
            1: 1300853285858578543,  # Cargo para o primeiro
            2: 1300850877585690655,  # Cargo para o segundo
            3: 1300854639658270761   # Cargo para o terceiro
        }
        self.premios = {
            1: "SNIPER EMBERIUM",
            2: "SNIPER BOSS",
            3: "SNIPER ADAMANTY"
        }

    async def atribuir_cargos(self, top_jogadores):
        print(f"Top jogadores: {top_jogadores}")  # Log dos top jogadores
        cargos_atuais = {member.id: member.roles for member in self.guild.members}

        # Atribuir cargos com base nos três maiores danos
        for rank, (player_id, dano) in enumerate(top_jogadores, start=1):
            cargo_id = self.cargos.get(rank)
            premio = self.premios.get(rank)
            if cargo_id:
                member = self.guild.get_member(player_id)
                cargo = self.guild.get_role(cargo_id)

                if member and cargo:
                    # Atribui o cargo se o jogador não o tiver
                    if cargo not in cargos_atuais.get(player_id, []):
                        await member.add_roles(cargo)
                        try:
                            await member.send(f"Você recebeu o prêmio: {premio}!")
                        except discord.Forbidden:
                            print(f"Não foi possível enviar mensagem para {member.name}.")
                        print(f"Atribuído {cargo.name} a {member.name} com dano {dano}.")
        
        # Remover cargos dos jogadores que não estão mais nos 3 primeiros
        await self.remover_cargos(top_jogadores)

    async def remover_cargos(self, top_jogadores):
        # Identificar IDs dos jogadores no top 3
        top_jogadores_ids = [player_id for player_id, _ in top_jogadores]

        # Verificar cada membro da guilda
        for member in self.guild.members:
            for rank in self.cargos.keys():
                cargo_id = self.cargos[rank]
                cargo = self.guild.get_role(cargo_id)

                if cargo in member.roles and member.id not in top_jogadores_ids:
                    await member.remove_roles(cargo)
                    try:
                        await member.send(f"Você perdeu o cargo: {cargo.name}.")
                    except discord.Forbidden:
                        print(f"Não foi possível enviar mensagem para {member.name}.")
                    print(f"Removido {cargo.name} de {member.name}.")
