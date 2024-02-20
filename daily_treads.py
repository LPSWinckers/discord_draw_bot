import discord
from datetime import datetime
from thread_json import add_thread

async def daily_job(client: discord.Client):
    channels = client.get_all_channels()
    for channel in channels:
        if channel.name == "daily-drawings":
            date = datetime.now().strftime("%Y-%m-%d")
            await create_tread(channel, name=f"Daily Drawing {date}")

async def create_tread(channel: discord.TextChannel, name: str = "Daily Drawing"):
    thread = await channel.create_thread(name=name, type=discord.ChannelType.public_thread, auto_archive_duration=1440)
    await thread.send(f'Thread "{thread.name}" created successfully!')
    add_thread(thread)