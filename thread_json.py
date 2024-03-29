import json
import discord

config = json.load(open('config.json'))
file = 'threads.json'

def open_json() -> dict:
    with open(file, 'r') as f:
        return json.load(f)

def write_json(data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

def add_thread(thread: discord.Thread):
    data = open_json()
    new_thread = {
        "id": thread.id,
        "name": thread.name,
        "archived": thread.archived,
        "members": [],
        "messages": []
    }
    data['threads'].append(new_thread)
    write_json(data)


def add_message_to_json(message: discord.message):
    update_members(message)

    if isinstance(message.channel, discord.Thread):
        data = open_json()
        for thread in data['threads']:
            if thread['id'] == message.channel.id:
                massege_data = convert_message(message)
                thread['messages'].append(massege_data)
                write_json(data)
                break

def update_members(message: discord.message):
    data = open_json()
    for thread in data['threads']:
        if thread['id'] == message.channel.id:
            if message.author.name not in thread['members']:
                thread['members'].append(message.author.name)
                write_json(data)
                break

def close_thread(thread_id):
    data = open_json()
    for thread in data['threads']:
        if thread['id'] == thread_id:
            thread['archived'] = True
            write_json(data)
            break

def convert_message(message):
    is_image = any(attachment.content_type and attachment.content_type.startswith('image/') for attachment in message.attachments)

    message_data = {
        "time": message.created_at.isoformat(),
        "user": message.author.name,
        "content": message.content,
        "attachment": [attachment.url for attachment in message.attachments],
        "isImage": is_image
    }

    return message_data

def get_all_images(message: discord.message):
    if len(message.content.split(' ')) == 1:
        user = message.author.name
    else:
        user = message.content.split(' ')[1]

    data = open_json()
    images = []

    for thread in data['threads']:
        if user == 'all' or user in thread['members']:
            for message in thread['messages']:
                if message['isImage']:
                    images.append(message)
    
    if len(images) == 0:
        return False
    return images


def get_stats(message: discord.message):
    if len(message.content.split(' ')) == 1:
        user = message.author.name
    else:
        user = message.content.split(' ')[1]

    data = open_json()
    stats = {
        "user": user,
        "total_messages": 0,
        "total_images": 0,
        "how_many_days": 0,
        "longest_streak": 0,
        "first_image": "",
        "last_image": ""
    }

    current_streak = 0
    for thread in data['threads']:
        if user in thread['members']:
            stats["how_many_days"] += 1
            current_streak += 1
            for message in thread['messages']:
                if message['user'] == user:
                    stats["total_messages"] += 1
                    if message['isImage']:
                        if stats["first_image"] == "":
                            stats["first_image"] = message["attachment"]
                        stats["last_image"] = message["attachment"]
                        stats["total_images"] += 1
        else:
            if current_streak > stats["longest_streak"]:
                stats["longest_streak"] = current_streak
            current_streak = 0
    if current_streak > stats["longest_streak"]:
        stats["longest_streak"] = current_streak
    
    return f"User: {stats['user']}\nTotal messages: {stats['total_messages']}\nTotal images: {stats['total_images']}\nHow many days: {stats['how_many_days']}\nLongest streak: {stats['longest_streak']} days\n", stats['first_image'], stats['last_image']