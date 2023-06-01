import discord
import asyncio
import youtube_dl
from discord import FFmpegPCMAudio
from discord.ext import commands
from subprocess import CalledProcessError

intents = discord.Intents.all()
intents.members = True

client = commands.Bot(command_prefix='!', intents=intents)


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))


@client.command(pass_context=True)
async def play(ctx, url: str):
    channel = ctx.message.author.voice.channel
    if not channel:
        await ctx.send('Error: You need to be in a voice channel to use this command.')
        return
    voice_client = await channel.connect()
    await asyncio.sleep(2)
    guild = ctx.guild
    voice_client: discord.VoiceClient = discord.utils.get(
        client.voice_clients, guild=guild)
    ytdl_opts = {'format': 'bestaudio'}
    with youtube_dl.YoutubeDL(ytdl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        try:
            
            voice_client.play(FFmpegPCMAudio(URL,
                                             options="-vn -ar 48000 -ac 2 -f mp3 -codec:a libopus"),
                              after=lambda e: print('done', e))
        except CalledProcessError as e:
            print(f"FFmpeg error: {e}")
    voice_client.source.volume = 0.5


client.run('')
