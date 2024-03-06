#(©)Codexbotz
# (©) Jigarvarma2005

import base64
import re
import asyncio
from config import FORCE_SUB_CHANNELS
from pyrogram.errors import FloodWait
from database.database import get_fsub
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def force_sub(func):
    """Force Sub decorator for handling force subscribe logic"""
    async def decorator(client, message):
        msg_text = "You are not subscribed to use this bot. Please send join request to below channel."
        buttons = []
        count = 1
        for x in FORCE_SUB_CHANNELS:
            user_ = await get_fsub(x[0], message.from_user.id)
            if not user_:
                buttons.append([InlineKeyboardButton(text=f"Channel {count}", url=x[1])])
                count += 1
        if buttons:
            buttons.append([
                   InlineKeyboardButton("🔒 Close", callback_data = "close")
                ])
            reply_markup = InlineKeyboardMarkup(buttons)
            return await message.reply_text(
                text=msg_text,
                reply_markup=reply_markup,
                quote=True
            )  
        await func(client, message)
    return decorator

async def encode(string):
    string_bytes = string.encode("ascii")
    return (base64.urlsafe_b64encode(string_bytes).decode("ascii")).strip("=")

async def decode(base64_string):
    base64_string = base64_string.strip("=") # links generated before this commit will be having = sign, hence striping them to handle padding errors.
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes) 
    return string_bytes.decode("ascii")

async def get_messages(client, message_ids):
    messages = []
    total_messages = 0
    while total_messages != len(message_ids):
        temb_ids = message_ids[total_messages:total_messages+200]
        try:
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=temb_ids
            )
        except FloodWait as e:
            await asyncio.sleep(e.x)
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=temb_ids
            )
        except:
            pass
        total_messages += len(temb_ids)
        messages.extend(msgs)
    return messages

async def get_message_id(client, message):
    if message.forward_from_chat:
        if message.forward_from_chat.id == client.db_channel.id:
            return message.forward_from_message_id
        else:
            return 0
    elif message.forward_sender_name:
        return 0
    elif message.text:
        pattern = "https://t.me/(?:c/)?(.*)/(\\d+)"
        matches = re.match(pattern,message.text)
        if not matches:
            return 0
        channel_id = matches.group(1)
        msg_id = int(matches.group(2))
        if channel_id.isdigit():
            if f"-100{channel_id}" == str(client.db_channel.id):
                return msg_id
        else:
            if channel_id == client.db_channel.username:
                return msg_id
    else:
        return 0


def get_readable_time(seconds: int) -> str:
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    hmm = len(time_list)
    for x in range(hmm):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        up_time += f"{time_list.pop()}, "
    time_list.reverse()
    up_time += ":".join(time_list)
    return up_time
