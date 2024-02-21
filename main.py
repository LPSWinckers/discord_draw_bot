import os
from dotenv import load_dotenv
import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from daily_treads import daily_job
from thread_json import add_message_to_json, get_all_images, get_stats, close_thread
import json

config = json.load(open('config.json'))

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

scheduler = AsyncIOScheduler()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

    scheduler.add_job(
        await_daily_job,
        trigger=CronTrigger(minute=config["schedule"]["minute"], hour=config["schedule"]["hour"], timezone="EUROPE/BERLIN")
    )

    scheduler.start()

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    add_message_to_json(message)

    if message.content.split()[0] == '-getAllImages':
        images = get_all_images(message)

        if not images:
            await message.author.send("No images found")
            return
        
        for image_message in images:

            await message.author.send("date: " + image_message["time"][:10] + " user: " + image_message["user"])
            for image in image_message["attachment"]:
                await message.author.send(image)

    if message.content.split()[0] == '-stats':
        stats, first_image, last_image = get_stats(message)
        await message.author.send(stats)
        await message.author.send("first image:")
        await message.author.send(first_image)
        await message.author.send("last image: ")
        await message.author.send(last_image)

@client.event
async def on_thread_update(before, after):
        if not before.archived and after.archived:
            close_thread(before.id)
            

async def await_daily_job():
    await daily_job(client)

def main():
    client.run(TOKEN)

if __name__ == '__main__':
    main()