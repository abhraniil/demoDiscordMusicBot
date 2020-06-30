import queue
import discord
from discord.ext import commands
import youtube_dl
from discord.utils import get

client = commands.Bot(command_prefix='.')
queue = queue.Queue()
extracted_song = {}
COUNT = 0


@client.event
async def on_ready():
    print('Bot is Online')
    print(f'Current Ping : {round(client.latency*1000)} ms')


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


@client.command(pass_context=True, aliases=['pa', 'pau'])
async def pause(ctx):

    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Music paused")
        voice.pause()
        await ctx.send("Music paused")
    else:
        print("Music not playing failed pause")
        await ctx.send("Music not playing failed pause")


@client.command(pass_context=True, aliases=['r', 'res'])
async def resume(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_paused():
        print("Resumed music")
        voice.resume()
        await ctx.send("Resumed music")
    else:
        print("Music is not paused")
        await ctx.send("Music is not paused")




@client.command(pass_context=True, aliases=['s'])
async def stop(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    queue.queue.clear()
    if voice and voice.is_playing():
        print("Music stopped")
        voice.stop()
        await ctx.send("Music stopped")
    else:
        print("No music playing failed to stop")
        await ctx.send("No music playing failed to stop")


@client.command(pass_context=True, aliases=['song', 'p'])
async def play(ctx, url: str):
    if ctx.message.author.voice:
        channel = ctx.message.author.voice.channel
        voice = get(client.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            await channel.connect()
        await ctx.send(f"mugenMusicBot has joined the '{channel}' Channel")

    voice = get(client.voice_clients, guild=ctx.guild)
    queue.queue.clear()
    def queue_func():
        if queue.not_empty:
            ydl_opts = {
                'default_search': 'auto',
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                              'options': '-vn'}
            URL = queue.get()
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                extracted_song = ydl.extract_info(URL, download=False)
                title = extracted_song.get('title')
                print(f'Extracting song : "{title}"')

            voice.guild.voice_client.play(discord.FFmpegPCMAudio(extracted_song["formats"][0]["url"], **FFMPEG_OPTIONS),
                                          after=lambda e: queue_func())
            voice.source = discord.PCMVolumeTransformer(voice.guild.voice_client.source)
            voice.source.volume = 10.0
            print('beta')
        elif not voice.is_playing():
            queue.clear()
            print("No songs were queued before the ending of the last song\n")
            ctx.send('No songs were queued before the ending of the last song\n')
            server = ctx.message.guild.voice_client
            server.disconnect()


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

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        extracted_song = ydl.extract_info(url, download=False)
        title = extracted_song.get('title')
        print(f'Extracting song : "{title}"')

    voice.guild.voice_client.play(discord.FFmpegPCMAudio(extracted_song["formats"][0]["url"], **FFMPEG_OPTIONS),
                                  after=lambda e: queue_func())
    voice.source = discord.PCMVolumeTransformer(voice.guild.voice_client.source)
    voice.source.volume = 10.0


@client.command(pass_context=True, aliases=['a', 'add'])
async def add_to_queue(ctx, url: str):
    queue.put(url)
    await ctx.send('Song Added To Playlist')

client.run("NzIzOTM4NTQ4OTAxODcxNzEz.Xu47BA.bzxsTx6a4-dLaruzkzDIRZxogDM")
