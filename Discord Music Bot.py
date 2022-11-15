import nextcord, os, asyncio, random, youtube_dl
from nextcord.ext.commands.errors import TooManyArguments
from nextcord import permissions
from nextcord import guild
from nextcord import FFmpegPCMAudio
from nextcord import message
from nextcord import channel
from nextcord.ext import commands
from nextcord.utils import get
from nextcord.ext import tasks
from youtube_dl import YoutubeDL

#Author @DBanks93

# this is still very much work in progress

# Feel free to edit it to make it your own :)

client = commands.Bot(command_prefix = '.') # bot client
voice = None 
channelName = None # name of the channel to send text about song updates
channel_Ctx = None # ctx of the channel to send text about song updates
songs = [] # array of songs or "playlist"


servers = [] # list of servers the bot is currently playing songs in

HELP_ICON_URL = 'https://cdn.discordapp.com/attachments/792720413083566095/887434101576069170/unnamed.png' 
YOUTUBE_ICON_URL = 'https://cdn.discordapp.com/attachments/792720413083566095/887432799722827806/YouTube-Emblem.png'

class server(object):
    def __init__(self, ID, channelName, channel_Ctx, voice):
        self.serverId = ID
        self.channelName = channelName
        self.channel_Ctx = channel_Ctx
        self.voice = voice
        self.songs = []




@client.event
async def on_ready():
    await client.change_presence(status=nextcord.Status.idle, activity=nextcord.Game(name ="Playing Music...", type=3))
    print("Bot is ready.")
    client.loop.create_task(status_task())
    

async def status_task():
    while True:
        await client.change_presence(status=nextcord.Status.idle, activity=nextcord.Game(name ="༼ つ ◕_◕ ༽つ", type=3))
        await asyncio.sleep(5)
        await client.change_presence(status=nextcord.Status.idle, activity=nextcord.Streaming(name ="◖ᵔᴥᵔ◗ ♪ ♫ ", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley"))
        await asyncio.sleep(5)
        
        # Checks if a song is playing if it isn't it plays the next sone in the playlist 
        for i in servers:
            try:
                if not i.voice.is_playing():
                    if i.channel_Ctx.guild.voice_client in client.voice_clients:
                        name = play_Youtube(i)
                        embed = nextcord.Embed(
                        colour = nextcord.Colour.blue()
                        )
                        embed.set_author(name="Zonico's Music Bot", icon_url=HELP_ICON_URL)
                        embed.set_thumbnail(url=YOUTUBE_ICON_URL)    
                        embed.add_field(name='Now playing:', value=name, inline = False)
                        embed.set_footer(text="(Created by Zonico)")
                        await channel_Ctx.send(embed = embed)      
            except:
                pass

# help command - shows all the commands of the bot
client.remove_command('help')
@client.command()
async def help(ctx):
    embed = nextcord.Embed(
        colour = nextcord.Colour.orange(),  description="***PLEASE NOTE: This bot is still very much Work In Progress, If you find any bugs please let my owner Zonico know :)***"
    )
    embed.set_author(name='Help', icon_url=HELP_ICON_URL)
    embed.add_field(name='!play / !p, url / songtitle', value='To play a song', inline = False)
    embed.add_field(name='!skip', value='To skip a song', inline = False)
    embed.add_field(name='!playlist', value='To view the list of current songs', inline = False)
    embed.add_field(name='!disconnect', value='To dissconnect the bot', inline = False)
    embed.add_field(name='!join', value="To make the bot join your vc *(Only to be used if it doesn't join  with the !p command)*", inline = False)
    embed.set_footer(text="(Created by Zonico)")
    await ctx.send(embed = embed)



# adds the bot to the voice channel
@client.command()
async def join(ctx):
    ID = ctx.guild.id
    found = False
    print(client.voice_clients)
    for i in servers:
        if i.serverId == ID:
            found = True
            if i.voice == None:
                currentServer = i
                found = 'Meh'
            if i.channel_Ctx.guild.voice_client not in client.voice_clients:
                found = 'Meh'
                currentServer = i
    
    if found == False:
        channelName = ctx.author.voice.channel
        voice = await channelName.connect()
        Newserver = server(ctx.guild.id, channelName, ctx, voice)
        servers.append(Newserver)
        await ctx.send("Successfully joined, type !play song, to play a song :)")
    elif found == 'Meh':
        channelName = ctx.author.voice.channel
        voice = await channelName.connect()
        currentServer.channelName = channelName
        currentServer.voice = voice
        await ctx.send("Successfully joined, type !play song, to play a song :)")
    else:
        await ctx.send("I am already in a Voice channel")


# disconnects bot from the voice channel
@client.command()
async def disconnect(ctx):
    for i in servers:
        if i.serverId == ctx.guild.id:
            if i.voice != None:
                await i.channelName.guild.voice_client.disconnect()    
                await ctx.send("Successfully Disconnected :)")
                i.voice = None
                break
    await ctx.send("I am not in a VC")


# searches and finds a song
# if the bot is not currently playing a song it'll play this song
# otherwise it'll add the song to a playlist to be played later
@client.command(aliases=['pl','p'])
async def play(ctx, *,url):
    ID = ctx.guild.id
    found = False
    for i in servers:
        if i.serverId == ID:
            found = True
            currentServer = i
            if i.voice == None:
                currentServer = i
                found = 'Meh'
            if i.channel_Ctx.guild.voice_client not in client.voice_clients:
                found = 'Meh'
                currentServer = i
                channelName = ctx.author.voice.channel
                i.voice = await channelName.connect()
    channel_Ctx = ctx
    if found == False:
        channelName = ctx.author.voice.channel
        voice = await channelName.connect()
        currentServer = server(ctx.guild.id, channelName, channel_Ctx, voice)
        servers.append(currentServer)
    elif found == 'Meh':
        channelName = ctx.author.voice.channel
        voice = await channelName.connect()
        currentServer.channelName = channelName
        currentServer.channel_Ctx = channel_Ctx
        currentServer.voice = voice
    if currentServer.channelName == ctx.author.voice.channel:
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        currentServer.voice = get(client.voice_clients, guild=ctx.guild)

        with YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                url_used = True
            except:
                try:
                    newStr = str("ytsearch:" + url)
                    info = ydl.extract_info(newStr, download=False)
                except:
                    await ctx.send("Sorry Song not found")
                url_used = False
        if url_used:
            URL = info['formats'][0]['url']
            name = info["title"]
        else:
            video_format = info['entries'][0]["formats"][0]
            name = info['entries'][0]["title"]
            URL = video_format["url"]
        if not currentServer.voice.is_playing():
            currentServer.voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
            currentServer.voice.is_playing()
            embed = nextcord.Embed(
            colour = nextcord.Colour.blue()
            )
            embed.set_author(name="Zonico's Music Bot", icon_url=HELP_ICON_URL)
            embed.set_thumbnail(url=YOUTUBE_ICON_URL)    
            embed.add_field(name='Now playing:', value=name, inline = False)
            embed.set_footer(text="(Created by Zonico)")
            await ctx.send(embed = embed)
        else:
            await ctx.send(f"Added {name} to the playlist")
            currentServer.songs.append(info)
        return
    await ctx.send("Sorry I'm already in another VC in the server")

# Skips the current song and plays the next song in the playlist if there is one
@client.command()
async def skip(ctx):
    for i in servers:
        if i.serverId == ctx.guild.id:
            if i.channelName == ctx.author.voice.channel:
                name = play_Youtube(i)
                if name == False:
                    await ctx.send("Error No more Songs")
                else:
                    await ctx.send("Skipped song successfully")
                    embed = nextcord.Embed(
                    colour = nextcord.Colour.blue()
                    )
                    embed.set_author(name="Zonico's Music Bot", icon_url=HELP_ICON_URL)
                    embed.set_thumbnail(url=YOUTUBE_ICON_URL)    
                    embed.add_field(name='Now playing:', value=name, inline = False)
                    embed.set_footer(text="(Created by Zonico)")
                    await ctx.send(embed = embed)
        pass

# Shows all the songs current;y in the playlist
@client.command(aliases=['list','songs', 'q', 'queue'])
async def playlist(ctx):
    for i in servers:
        if i.serverId == ctx.guild.id:
            embed = nextcord.Embed(
            colour = nextcord.Colour.blue())
            embed.set_author(name="Zonico's Music Bot", icon_url=HELP_ICON_URL)
            embed.set_thumbnail(url=YOUTUBE_ICON_URL)
            x = 1
            if len(i.songs) >= 1:
                for info in i.songs:
                    try:
                        name = info["title"]
                    except:
                        name = info['entries'][0]["title"]
                    title = str(x) + ':'
                    embed.add_field(name=title, value=name, inline = False)  
                    x += 1
                embed.set_footer(text="(Created by Zonico)")
                await ctx.send(embed = embed)
            else:
                await ctx.send("No more songs will play")

# Plays the next song in a playlist
def play_Youtube(currentServer):
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        currentServer.voice.pause()
        if len(currentServer.songs) == 0:
            return False
        info = currentServer.songs[0]
        try:
            URL = info['formats'][0]['url']
            name = info["title"]
        except:
            video_format = info['entries'][0]["formats"][0]
            URL = video_format["url"]
            name = info['entries'][0]["title"]
        currentServer.voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        currentServer.voice.is_playing()
        currentServer.songs.pop(0)
        return name


# Replace <YOUR_BOT_TOCKEN> 
client.run(<YOUR_BOT_TOCKEN>)


        
