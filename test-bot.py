import asyncio
import datetime
from queue import Queue
import discord
from discord.ext import commands
import youtube_dl
from discord.utils import get
import pafy


client = commands.Bot(command_prefix='.')
players = {}
queue = Queue()
song_info = {}


@client.event
async def on_ready():
    print('Bot is ready')


@client.command(pass_context=True)
async def join(ctx):
    if ctx.message.author.voice:
        channel = ctx.message.author.voice.channel
        await channel.connect()


@client.command(pass_context=True)
async def leave(ctx):
    if ctx.message.author.voice:
        server = ctx.message.guild.voice_client
        await server.disconnect()


@client.command(pass_context=True)
async def pause(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        voice.pause()
        await ctx.send("Music paused")
    else:
        await ctx.send("Music not playing failed pause")


@client.command(pass_context=True)
async def resume(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        voice.resume()
        await ctx.send("Resumed music")
    else:
        await ctx.send("Music is not paused")


@client.command(pass_context=True)
async def stop(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        voice.stop()
        await ctx.send("Music stopped")
    else:
        await ctx.send("No music playing failed to stop")


@client.command(pass_context=True, aliases=['song'])
async def play(ctx, url: str):
    if ctx.message.author.voice:
        channel = ctx.message.author.voice.channel
        voice = get(client.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            await channel.connect()
        await ctx.send(f"MugenBot has joined the '{channel}' Channel")

    voice = get(client.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'default_search': 'auto',
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    queue.empty()
    if queue.empty():
        queue.put(url)
        while queue.qsize() > 0:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                print('Extracting song')
                extracted_song = ydl.extract_info(url, download=False)
            voice.guild.voice_client.play(discord.FFmpegPCMAudio(extracted_song["formats"][0]["url"], **FFMPEG_OPTIONS))
            voice.source = discord.PCMVolumeTransformer(voice.source)
            voice.source.volume = 01.00
            pafy_obj = pafy.new(url)
            date_time = datetime.datetime.strptime(pafy_obj.duration, "%H:%M:%S")
            a_timedelta = date_time - datetime.datetime(1900, 1, 1)
            seconds = a_timedelta.total_seconds()
            queue.get(url)
            await asyncio.sleep(seconds)


@client.command(pass_context=True, aliases=['q', 'queue', 'add'])
async def add_to_queue(ctx, url: str):
    queue.put(url)


@client.command(pass_context=True, aliases=['d', 'delete', 'remove'])
async def delete_to_queue(ctx, url: str):
    queue.get(url)


client.run("NzIzOTM4NTQ4OTAxODcxNzEz.Xu47BA.bzxsTx6a4-dLaruzkzDIRZxogDM")
