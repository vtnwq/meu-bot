
import asyncio
import ast
import operator
import os
import random

import discord
from discord.ext import commands


# =========================
# CONFIGURAÇÃO DO BOT
# =========================

TOKEN = os.getenv("DISCORD_TOKEN", "COLOQUE_SEU_TOKEN_AQUI")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = commands.Bot(
    command_prefix="ms!",
    intents=intents
)


# =========================
# PRESENÇA AUTOMÁTICA
# =========================

@client.event
async def on_ready():
    await client.change_presence(
        activity=discord.Game(name="peidando guloso")
    )
    print(f"Bot conectado: {client.user}")
    print(f"ID: {client.user.id}")


# =========================
# PING
# =========================

@client.command()
async def ping(ctx):
    latencia = round(client.latency * 1000)
    await ctx.reply(f"Pong! {latencia}ms")


# =========================
# CALCULADORA
# =========================

OPERADORES = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def calcular(no):
    if isinstance(no, ast.Expression):
        return calcular(no.body)

    if isinstance(no, ast.Constant) and type(no.value) in (int, float):
        return no.value

    if isinstance(no, ast.BinOp) and type(no.op) in OPERADORES:
        esquerda = calcular(no.left)
        direita = calcular(no.right)

        if isinstance(no.op, ast.Pow) and abs(direita) > 100:
            raise ValueError("Expoente muito grande.")

        resultado = OPERADORES[type(no.op)](esquerda, direita)

        if isinstance(resultado, (int, float)) and abs(resultado) > 1e100:
            raise ValueError("Resultado muito grande.")

        return resultado

    if isinstance(no, ast.UnaryOp) and type(no.op) in OPERADORES:
        return OPERADORES[type(no.op)](calcular(no.operand))

    raise ValueError("Expressão não permitida.")


@client.command()
async def calc(ctx, *, expressao: str):
    try:
        arvore = ast.parse(expressao, mode="eval")
        resultado = calcular(arvore)

        await ctx.reply(f"Resultado: `{resultado}`")

    except (ValueError, TypeError, SyntaxError, ZeroDivisionError,
            OverflowError) as erro:
        await ctx.reply(f"Não foi possível calcular: {erro}")


# =========================
# TRANSMITIR MENSAGEM
# =========================

@client.command()
@commands.is_owner()
async def transmitir(ctx, *, mensagem: str):
    embed = discord.Embed(
        description=mensagem,
        color=discord.Color.blue()
    )

    await ctx.send(embed=embed)


# =========================
# ALTERAR PRESENÇA
# =========================

@client.command()
@commands.is_owner()
async def status(ctx, *, texto: str):
    await client.change_presence(
        activity=discord.Game(name=texto)
    )

    await ctx.reply(f"Presença alterada para: **{texto}**")


@client.command()
@commands.is_owner()
async def statuspadrao(ctx):
    await client.change_presence(
        activity=discord.Game(name="peidando guloso")
    )

    await ctx.reply("Presença padrão restaurada.")


# =========================
# AJUDA
# =========================

@client.command()
async def ajuda(ctx):
    embed = discord.Embed(
        title="Comandos do bot",
        description="Prefixo: `ms!`",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="Utilidades",
        value=(
            "`ping` — latência\n"
            "`calc expressão` — calculadora\n"
            "`say mensagem` — repetir mensagem\n"
            "`ship @pessoa1 @pessoa2` — compatibilidade fictícia\n"
            "`userinfo @membro` — informações do membro\n"
            "`avatar [@membro]` — avatar\n"
            "`servidor` — informações do servidor"
        ),
        inline=False
    )

    embed.add_field(
        name="Administração",
        value=(
            "`transmitir mensagem` — enviar embed\n"
            "`status texto` — alterar presença\n"
            "`statuspadrao` — restaurar presença\n"
            "`criarcanal nome` — criar canal\n"
            "`criarcargo nome` — criar cargo\n"
            "`addcargo @membro cargo` — adicionar cargo\n"
            "`remcargo @membro cargo` — remover cargo\n"
            "`kick @membro motivo` — expulsar membro\n"
            "`limpar quantidade` — apagar mensagens"
        ),
        inline=False
    )

    await ctx.send(embed=embed)


# =========================
# CRIAR CANAL
# =========================

@client.command()
@commands.is_owner()
@commands.has_permissions(manage_channels=True)
async def criarcanal(ctx, *, nome: str):
    if ctx.guild is None:
        return await ctx.reply("Use este comando em um servidor.")

    canal = await ctx.guild.create_text_channel(name=nome)
    await ctx.reply(f"Canal criado: {canal.mention}")


# =========================
# CRIAR CARGO
# =========================

@client.command()
@commands.is_owner()
@commands.has_permissions(manage_roles=True)
async def criarcargo(ctx, *, nome: str):
    if ctx.guild is None:
        return await ctx.reply("Use este comando em um servidor.")

    cargo = await ctx.guild.create_role(name=nome)
    await ctx.reply(f"Cargo **{cargo.name}** criado com sucesso!")


# =========================
# SAY
# =========================

@client.command()
@commands.is_owner()
async def say(ctx, *, mensagem: str):
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass

    await ctx.send(mensagem)


# =========================
# SHIP
# =========================

@client.command()
async def ship(
    ctx,
    pessoa1: discord.Member,
    pessoa2: discord.Member
):
    porcentagem = random.randint(0, 100)

    embed = discord.Embed(
        title="Compatibilidade de Ship",
        description=(
            f"{pessoa1.mention} + {pessoa2.mention}\n\n"
            f"Compatibilidade fictícia: **{porcentagem}%**"
        ),
        color=discord.Color.pink()
    )

    await ctx.send(embed=embed)


# =========================
# LOCALIZAR CARGO
# =========================

def localizar_cargo(guild, nome):
    return discord.utils.find(
        lambda cargo: cargo.name.casefold() == nome.casefold(),
        guild.roles
    )


# =========================
# ADICIONAR CARGO
# =========================

@client.command()
@commands.is_owner()
@commands.has_permissions(manage_roles=True)
async def addcargo(
    ctx,
    membro: discord.Member,
    *,
    nome_cargo: str
):
    if ctx.guild is None:
        return await ctx.reply("Use este comando em um servidor.")

    cargo = localizar_cargo(ctx.guild, nome_cargo)

    if cargo is None:
        return await ctx.reply("Cargo não encontrado.")

    if cargo.is_default() or cargo.managed:
        return await ctx.reply("Esse cargo não pode ser gerenciado manualmente.")

    if cargo >= ctx.guild.me.top_role:
        return await ctx.reply(
            "O cargo está acima ou no mesmo nível do meu."
        )

    if membro == ctx.guild.owner:
        return await ctx.reply(
            "Não posso alterar os cargos do dono do servidor."
        )

    try:
        await membro.add_roles(
            cargo,
            reason=f"Comando usado por {ctx.author}"
        )
        await ctx.reply(
            f"Cargo **{cargo.name}** adicionado a {membro.mention}."
        )

    except discord.Forbidden:
        await ctx.reply("Não tenho permissão para adicionar esse cargo.")


# =========================
# REMOVER CARGO
# =========================

@client.command()
@commands.is_owner()
@commands.has_permissions(manage_roles=True)
async def remcargo(
    ctx,
    membro: discord.Member,
    *,
    nome_cargo: str
):
    if ctx.guild is None:
        return await ctx.reply("Use este comando em um servidor.")

    cargo = localizar_cargo(ctx.guild, nome_cargo)

    if cargo is None:
        return await ctx.reply("Cargo não encontrado.")

    if cargo.is_default() or cargo.managed:
        return await ctx.reply("Esse cargo não pode ser gerenciado manualmente.")

    if cargo >= ctx.guild.me.top_role:
        return await ctx.reply(
            "O cargo está acima ou no mesmo nível do meu."
        )

    if membro == ctx.guild.owner:
        return await ctx.reply(
            "Não posso alterar os cargos do dono do servidor."
        )

    if cargo not in membro.roles:
        return await ctx.reply("Esse membro não possui esse cargo.")

    try:
        await membro.remove_roles(
            cargo,
            reason=f"Comando usado por {ctx.author}"
        )
        await ctx.reply(
            f"Cargo **{cargo.name}** removido de {membro.mention}."
        )

    except discord.Forbidden:
        await ctx.reply("Não tenho permissão para remover esse cargo.")


# =========================
# KICK
# =========================

@client.command()
@commands.is_owner()
@commands.has_permissions(kick_members=True)
async def kick(
    ctx,
    membro: discord.Member,
    *,
    motivo: str = "Nenhum motivo informado"
):
    if ctx.guild is None:
        return await ctx.reply("Use este comando em um servidor.")

    if membro == ctx.author:
        return await ctx.reply("Você não pode expulsar a si mesmo.")

    if membro == ctx.guild.owner:
        return await ctx.reply("Não posso expulsar o dono do servidor.")

    if membro.top_role >= ctx.guild.me.top_role:
        return await ctx.reply(
            "O cargo desse membro está acima ou no mesmo nível do meu."
        )

    try:
        await membro.kick(
            reason=f"{motivo} | Por: {ctx.author}"
        )
        await ctx.reply(
            f"**{membro}** foi expulso. Motivo: {motivo}"
        )

    except discord.Forbidden:
        await ctx.reply("Não tenho permissão para expulsar esse membro.")


# =========================
# LIMPAR MENSAGENS
# =========================

@client.command()
@commands.is_owner()
@commands.has_permissions(manage_messages=True)
async def limpar(ctx, quantidade: int):
    if ctx.guild is None:
        return await ctx.reply("Use este comando em um servidor.")

    if quantidade < 1 or quantidade > 100:
        return await ctx.reply(
            "Informe uma quantidade entre 1 e 100."
        )

    apagadas = await ctx.channel.purge(
        limit=quantidade + 1
    )

    await ctx.send(
        f"{len(apagadas) - 1} mensagens apagadas.",
        delete_after=5
    )


# =========================
# INFORMAÇÕES DO MEMBRO
# =========================

@client.command()
async def userinfo(ctx, membro: discord.Member = None):
    membro = membro or ctx.author

    embed = discord.Embed(
        title=f"Informações de {membro}",
        color=discord.Color.blue()
    )

    embed.set_thumbnail(url=membro.display_avatar.url)
    embed.add_field(name="ID", value=str(membro.id), inline=False)
    embed.add_field(
        name="Conta criada",
        value=discord.utils.format_dt(membro.created_at, style="D"),
        inline=False
    )
    embed.add_field(
        name="Entrou no servidor",
        value=(
            discord.utils.format_dt(membro.joined_at, style="D")
            if membro.joined_at else "Data indisponível"
        ),
        inline=False
    )

    await ctx.send(embed=embed)


# =========================
# AVATAR
# =========================

@client.command()
async def avatar(ctx, membro: discord.Member = None):
    membro = membro or ctx.author

    embed = discord.Embed(
        title=f"Avatar de {membro}",
        color=discord.Color.blue()
    )
    embed.set_image(url=membro.display_avatar.url)

    await ctx.send(embed=embed)


# =========================
# INFORMAÇÕES DO SERVIDOR
# =========================

@client.command()
async def servidor(ctx):
    guild = ctx.guild

    if guild is None:
        return await ctx.reply("Use este comando em um servidor.")

    embed = discord.Embed(
        title=guild.name,
        color=discord.Color.blue()
    )

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    embed.add_field(name="ID", value=str(guild.id), inline=False)
    embed.add_field(name="Membros", value=str(guild.member_count))
    embed.add_field(name="Canais", value=str(len(guild.channels)))
    embed.add_field(name="Cargos", value=str(len(guild.roles)))
    embed.add_field(
        name="Criado em",
        value=discord.utils.format_dt(guild.created_at, style="D"),
        inline=False
    )

    await ctx.send(embed=embed)


# =========================
# TRATAMENTO DE ERROS
# =========================

@client.event
async def on_command_error(ctx, erro):
    if isinstance(erro, commands.CommandNotFound):
        return

    if isinstance(erro, commands.MissingRequiredArgument):
        await ctx.reply(
            f"Falta um argumento: `{erro.param.name}`."
        )
        return

    if isinstance(erro, commands.MemberNotFound):
        await ctx.reply("Não encontrei esse membro.")
        return

    if isinstance(erro, commands.CommandOnCooldown):
        await ctx.reply("Aguarde antes de usar esse comando novamente.")
        return

    if isinstance(erro, commands.NotOwner):
        await ctx.reply("Este comando é exclusivo do dono do bot.")
        return

    if isinstance(erro, commands.MissingPermissions):
        await ctx.reply("Você não tem as permissões necessárias.")
        return

    if isinstance(erro, commands.BotMissingPermissions):
        await ctx.reply("Está faltando uma permissão para o bot.")
        return

    if isinstance(erro, commands.NoPrivateMessage):
        await ctx.reply("Esse comando só funciona em servidores.")
        return

    print(f"Erro no comando {ctx.command}: {repr(erro)}")

    if isinstance(erro, discord.Forbidden):
        await ctx.reply("O Discord negou a ação por falta de permissão.")
    elif isinstance(erro, discord.HTTPException):
        await ctx.reply("O Discord não conseguiu concluir a ação.")
    else:
        await ctx.reply("Ocorreu um erro ao executar o comando.")


# =========================
# INICIALIZAÇÃO
# =========================

async def main():
    if not TOKEN or TOKEN == "COLOQUE_SEU_TOKEN_AQUI":
        raise RuntimeError(
            "Configure o token do bot na variável DISCORD_TOKEN."
        )

    async with client:
        await client.start(TOKEN)


asyncio.run(main())
