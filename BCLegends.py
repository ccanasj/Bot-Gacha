import discord
from discord.ext import commands
from discord.ext.commands.core import after_invoke
from discord.commands import permissions
from discord.commands import Option
from random import choice, choices
import db
import datetime
from collections import Counter
from TOKEN import BOT

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or("BC!"),case_insensitive=True)

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("----------------------------------------------")

bot = Bot()
bot.remove_command('help')

Rareza = [0,1,2,3,4]
Probabilidades = [0.55,0.2,0.15,0.07,0.03]
RarezaCarta = ('N','R','SR','SSR','UR')
RarezaCartaEmoji = {'N':'<:N_:919717111725694977>','R':'<:R_:919717112728133682>','SR':'<:SR:919717112543580232>','SSR':'<:SSR:919717113025953832>','UR':'<:UR:919717111964774430>'}

@bot.command()
async def help(ctx):
    embedVar = discord.Embed()
    embedVar.set_author(name = 'Comandos BC Legends')
    embedVar.add_field(name="🌀Gacha", value='Legend')
    embedVar.add_field(name="🃏Cartas🎴", value='Cards \n Stats [Id carta]')
    await ctx.send(embed = embedVar)

@bot.command()
async def Kirbo(ctx):
    await ctx.send('Poyo')

@bot.command()
@after_invoke(db.CerrarDB)
@commands.cooldown(rate = 1,per = 43200, type = commands.BucketType.user)
async def Legend(ctx):
    valor = choices(population = Rareza ,weights = Probabilidades)[0]
    cartas = await db.GetCartasRareza(RarezaCarta[valor])
    carta = choice(cartas)
    await db.GuardarUsuario(ctx.author.id,carta['_id'])
    embedVar = discord.Embed(title = '<a:SpinningStar:919691664757514270> En hora buena tu leyenda ganadora es...')
    embedVar.set_image(url = 'https://media.discordapp.net/attachments/918887492583821412/919036646308085780/GIF-211210_221247.gif')
    await ctx.send(embed = embedVar)
    embedVar = discord.Embed(title = carta['nombre'],description = carta['descripcion'])
    embedVar.add_field(name = 'Rareza',value = carta['rarity'])
    embedVar.add_field(name = 'Power',value = f'{carta["power"]}/100')
    embedVar.add_field(name = 'Raza',value = carta['raza'])
    embedVar.set_image(url = carta['foto'])
    await ctx.send(embed = embedVar)


@bot.command()
@after_invoke(db.CerrarDB)
@commands.max_concurrency(1,per = commands.BucketType.user)
async def Cards(ctx):
    mazo,cartas = await db.GetMazo(ctx.author.id)
    if not mazo:
        await ctx.send('Aun no tienes cartas guardadas')
        return
    mazo = dict(Counter(mazo))
    embedVar = discord.Embed()
    embedVar.add_field(name = '<a:SpinningStar:919691664757514270>',value = '\n'.join([f'`{ids:03d}` {RarezaCartaEmoji[cartas[ids][1]]} | **{cartas[ids][0]}** x{numero}' for ids,numero in mazo.items()]))
    embedVar.set_author(name = f'Mazo de {ctx.author.name}',icon_url = ctx.author.avatar.url)
    await ctx.send(embed = embedVar)

@bot.command()
@after_invoke(db.CerrarDB)
@commands.max_concurrency(1,per = commands.BucketType.user)
async def Stats(ctx,id:int):
    carta = await db.GetCarta(id)
    if not carta:
        await ctx.send('Esta no es una id valida')
        return
    embedVar = discord.Embed(title = carta['nombre'],description = carta['descripcion'])
    embedVar.add_field(name = 'Rareza',value = carta['rarity'])
    embedVar.add_field(name = 'Power',value = f'{carta["power"]}/100')
    embedVar.add_field(name = 'Raza',value = carta['raza'])
    embedVar.set_image(url = carta['foto'])
    await ctx.send(embed = embedVar)

@bot.slash_command(guild_ids=[919678098352525412,855596151415898173,909582357848285215])
@permissions.has_role("admin") 
@after_invoke(db.CerrarDB)
async def guardarcarta(ctx:commands.Context,
    nombre: Option(str, "Ingresa el nombre de la carta"),
    descripcion: Option(str, "Ingresa la descripcion de la carta"),
    rareza: Option(str, "Ingresa la rareza de la carta", choices=['N','R','SR','SSR','UR']),
    poder: Option(int, "Ingresa el poder de la carta"),
    raza: Option(str, "Ingresa la raza de la carta"),
    imagen: Option(str, "Ingresa el link de la imagen de la carta"),
    ):
    datos = {
    "rarity": rareza,
    "nombre": nombre,
    "foto": imagen,
    "descripcion": descripcion,
    "power": poder,
    "raza": raza
    }
    await db.GuardarCarta(datos)
    await ctx.respond("La carta se ha guardado correctamente")

@bot.event
async def on_command_error(ctx,error):
    if isinstance(error,commands.BotMissingPermissions):
        await ctx.send(f"{ctx.author.mention} No tengo permisos para usar este comando")
    elif isinstance(error,commands.NoPrivateMessage):
        await ctx.reply('El bot solo se puede usar en el servidor')
    elif isinstance(error,commands.MissingPermissions):
        await ctx.send(f"{ctx.author.mention} No tienes permisos para usar este comando")
    elif isinstance(error,commands.CommandNotFound):
        await ctx.send(f"{ctx.author.mention} Este comando no existe")
    elif isinstance(error,commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author.mention} Te falta un parametro en el comando")
    elif isinstance(error,commands.MemberNotFound):
        await ctx.send(f"{ctx.author.mention} Este no es un miembro valido")
    elif isinstance(error,commands.CommandOnCooldown):
        await ctx.reply(f'Este Comando se esta recargando, Intentalo en **{datetime.timedelta(seconds = round(error.retry_after))}** ⏳')
    elif isinstance(error,commands.MaxConcurrencyReached):
        await ctx.reply('Acaba el comando anterior para seguir con uno nuevo')
    elif isinstance(error,commands.BadArgument):
        await ctx.reply('Este no es un parametro correcto')
    else:
        raise error

bot.run(BOT)