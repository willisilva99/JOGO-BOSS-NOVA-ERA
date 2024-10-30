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
