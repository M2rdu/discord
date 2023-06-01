import discord
import asyncio
import youtube_dl
from discord.utils import get
from discord import FFmpegPCMAudio

intents = discord.Intents.all()
intents.members = True

client = discord.Client(intents=intents)

# Järjekord
queue = []
paused = False


async def join(message):
    # Ühendus channeliga
    channel = message.author.voice.channel
    if message.guild.voice_client:
        await message.guild.voice_client.move_to(channel)
    else:
        await channel.connect()
    await message.channel.send(f'Ühendus kanaliga {channel}')


async def play(video_link, voice, message):
    # Audio mängimine lingi järgi
    ydl_opts = {'format': 'bestaudio', 'noplaylist': True}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_link, download=False)
    URL = info['formats'][0]['url']
    title = info['title']
    options = {
        'options': '-vn',
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
    }
    voice.play(FFmpegPCMAudio(URL, **options), after=lambda e: asyncio.run_coroutine_threadsafe(
        play_next(voice=voice, message=message), client.loop).result())
    await message.channel.send(f'Nüüd mängib: {title}')


async def play_next(voice, message):
    # Mängi järgmine laul queue's
    if len(queue) > 0:
        video_link = queue.pop(0)
        if not voice.is_playing():
            await play(video_link, voice, message)
    elif voice and voice.is_connected():
        await message.channel.send('Muusika järjekord on tühi. Ootan uusi laule...')




async def skip(voice, message):
    # Jäta laul vahele
    voice.stop()
    await play_next(voice, message)


async def show_queue(message):
    # Näita järjekorda
    if queue:
        queue_list = '\n'.join(queue)
        await message.channel.send(f"Muusika järjekord:\n{queue_list}")
    else:
        await message.channel.send("Muusika järjekord on tühi.")


async def disconnect(message):
    # Lahuta kanalist
    if message.guild.voice_client:
        await message.guild.voice_client.disconnect()
        await message.channel.send('Lahkusin häälekanalist.')
    else:
        await message.channel.send('Ei ole ühendatud häälekanaliga.')


async def stop(message):
    # Peata muusika mängimine ja tühjenda järjekord
    voice = get(client.voice_clients, guild=message.guild)
    queue.clear()
    if voice and voice.is_playing():
        voice.stop()
        await play_next(voice, message)
    else:
        await disconnect(message)


async def pause(voice):
    # Pane audio mängija pausile
    if voice.is_playing():
        voice.pause()
        global paused
        paused = True


async def resume(voice):
    # Jätka muusika mängimist
    if voice.is_paused():
        voice.resume()
        global paused
        paused = False


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('&join'):
        await join(message)

    if message.content.startswith('&play'):
        # Ühendus kanaliga ja audio mängimine
        await join(message)
        voice = get(client.voice_clients, guild=message.guild)
        msg = message.content.split()
        if len(msg) < 2:
            await message.channel.send('Palun lisa korrektne link')
            return
        video_link = msg[1]
        if not voice.is_playing() and not queue:
            await play(video_link, voice, message)
        else:
            queue.append(video_link)
            await message.channel.send(f'Lisatud järjekorda: {video_link}')

    if message.content.startswith('&skip'):
        # Jäta laul vahele
        voice = get(client.voice_clients, guild=message.guild)
        if not voice.is_playing():
            await message.channel.send('Pole midagi vahele jätta')
        else:
            await skip(voice, message)

    if message.content.startswith('&queue'):
        # Näita muusika järjekorda
        await show_queue(message)

    if message.content.startswith('&disconnect'):
        # Lahku häälekanalist
        voice = get(client.voice_clients, guild=message.guild)
        if not voice.is_playing() and not queue:
            await disconnect(message)
        else:
            await message.channel.send('Palun lõpeta muusika mängimine enne lahkumist.')

    if message.content.startswith('&stop'):
        # Peata muusika mängimine ja tühjenda järjekord
        voice = get(client.voice_clients, guild=message.guild)
        if voice.is_playing() or queue:
            await stop(message)

    if message.content.startswith('&pause'):
        # Pane audio mängija pausile
        voice = get(client.voice_clients, guild=message.guild)
        if voice.is_playing() and not paused:
            await pause(voice)

    if message.content.startswith('&continue'):
        # Jätka muusika mängimist
        voice = get(client.voice_clients, guild=message.guild)
        if voice.is_paused() and paused:
            await resume(voice)


client.run(
    'MTA5NjAzNDMzMTM0MTkwMTg3NQ.GCi3_z.KwlAi4YWt8cSTjBEbwYj4QeDjWnxTP-9GDWcww')
