import random, re
import logging
from pyrogram import Client, filters, enums
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait, ChatAdminRequired, UserNotParticipant, PeerIdInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, CallbackQuery, Message, ChatPermissions
from .database import db
from config import Config, Txt
from info import AUTH_CHANNEL
from helper.utils import is_req_subscribed
import humanize
from time import sleep
from syd import send_log
logger = logging.getLogger(__name__)
CHID = -1001541018556
@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):

    if message.from_user.id in Config.BANNED_USERS:
        await message.reply_text("Sorry, You are banned.")
        return

    user = message.from_user
    
    if not await db.users.find_one({"_id": user.id}):
        await db.add_user(user.id)
        await send_log(client, message)
    try:
        await client.get_chat_member(CHID, message.from_user.id)
    except UserNotParticipant:
        
        key = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("↱ Jᴏɪɴ Cʜᴀɴɴᴇʟ ↲", url="https://t.me/bot_Cracker"),
                InlineKeyboardButton("Cᴏɴᴛɪɴᴜᴇ ↯", callback_data="chk")
            ]]
        )
        await message.reply_text("**Pʟᴇᴀꜱᴇ Jᴏɪɴ Iɴ Oᴜʀ Cʜᴀɴɴᴇʟ Tᴏ Uꜱᴇ Mᴇ 🥶.\nIꜰ Yᴏᴜ Jᴏɪɴᴇᴅ Tʜᴇ Cʜᴀɴɴᴇʟ Tʜᴇɴ Cʟɪᴄᴋ Oɴ Cᴏɴᴛɪɴᴜᴇ Bᴜᴛᴛᴏɴ Tᴏ Pʀᴏᴄᴇꜱꜱ ✨.\n\n__Jᴏɪɴ: @Bot_Cracker 🌡️__**", reply_markup=key)
        return 
    except Exception as e:
        try:
            await client.send_message(1733124290, f"Fsub: {e}")
        except:
            pass
    button = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            'Uᴘᴅᴀᴛᴇꜱ ¹', url='https://t.me/Bot_Cracker'),
        InlineKeyboardButton(
            'Sᴜᴘᴘᴏʀᴛ', url='https://t.me/+O1mwQijo79s2MjJl')],
        [InlineKeyboardButton('Oᴡɴᴇʀ', user_id=1733124290)
    ], [
        InlineKeyboardButton('Bᴏᴛꜱ', url='https://t.me/Bot_Cracker/17'),
        InlineKeyboardButton('Uᴩᴅᴀᴛᴇꜱ ²', url='https://t.me/Mod_Moviez_X')]])
    if Config.PICS:
        await message.reply_photo(random.choice(Config.PICS), caption=Txt.STRT_TXT.format(user.mention), reply_markup=button)
    else:
        await message.reply_text(text=Txt.STRT_TXT.format(user.mention), reply_markup=button, disable_web_page_preview=True)


@Client.on_callback_query(filters.regex("chk"))
async def chk(_, cb : CallbackQuery):
    try:
        await _.get_chat_member(CHID, cb.from_user.id)
    except:
        await cb.answer("You ᴀʀᴇ ɴᴏᴛ ᴊᴏɪɴᴇᴅ ɪɴ ᴍʏ ᴄʜᴀɴɴᴇʟ, ᴊᴏɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴛʜᴇɴ ᴄʜᴇᴄᴋ ᴀɢᴀɪɴ. 🎐", show_alert=True)
        return 

    user = cb.from_user
    button = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            'Uᴘᴅᴀᴛᴇꜱ ¹', url='https://t.me/Bot_Cracker'),
        InlineKeyboardButton(
            'Sᴜᴘᴘᴏʀᴛ', url='https://t.me/+O1mwQijo79s2MjJl')],
        [InlineKeyboardButton('Oᴡɴᴇʀ', user_id=1733124290)
    ], [
        InlineKeyboardButton('Bᴏᴛꜱ', url='https://t.me/Bot_Cracker/17'),
        InlineKeyboardButton('Uᴩᴅᴀᴛᴇꜱ ²', url='https://t.me/Mod_Moviez_X')]])
    if Config.PICS:
        await cb.message.reply_photo(random.choice(Config.PICS), caption=Txt.STRT_TXT.format(user.mention), reply_markup=button)
    else:
        await cb.message.reply_text(text=Txt.STRT_TXT.format(user.mention), reply_markup=button, disable_web_page_preview=True)

import re

LINK_REGEX = re.compile(
    r"(https?://|www\.|t\.me/|telegram\.me/|bit\.ly|goo\.gl|@)"
    r"|([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(/[^\s]*)?",
    re.IGNORECASE
)


from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# in-memory storage {chat_id: {user_id: count}}
link_counter = {}

@Client.on_message(filters.group & ~filters.service)
async def delete_message(bot: Client, message: Message):
    await db.add_grp(message.chat.id)

    # skip messages without sender
    if not message.from_user:
        return

    user_id = message.from_user.id

    # check user status (skip admins/owners)
    try:
        user = await bot.get_chat_member(message.chat.id, user_id)
        if user.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER) or user_id in Config.ADMIN:
            return
    except:
        pass

    text = (message.text or "").lower().replace("@admin", "")

    # 🚫 check forwarded from bot
    if message.forward_from and message.forward_from.is_bot and message.forward_from.id == 273234066:
        await safe_delete(message)
        await update_user_count(bot, message)
        return
    if message.forward_from_chat and message.forward_from_chat.id == 273234066:
        await safe_delete(message)
        await update_user_count(bot, message)
        return

    # 🚫 check plain text links
    if LINK_REGEX.search(text):
        await safe_delete(message)
        await update_user_count(bot, message)
        return

    # 🚫 check hyperlink entities
    if message.entities:
        for entity in message.entities:
            if entity.type == enums.MessageEntityType.TEXT_LINK:
                await safe_delete(message)
                await update_user_count(bot, message)
                return


async def safe_delete(message: Message):
    try:
        await message.delete()
    except Exception:
        pass


async def update_user_count(bot: Client, message: Message):
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id

        # increment in DB
        count = await db.increment_violation(chat_id, user_id)
        # await message.reply(f"{count}")  # debug if needed

        # 🚨 threshold reached
        if count >= 10:
            user_mention = message.from_user.mention
            admins = [
                    m async for m in bot.get_chat_members(
                        chat_id,
                        filter=enums.ChatMembersFilter.ADMINISTRATORS
                    )
                ]
            # notify inside group
            mentions = [
                f"[{a.user.first_name}](tg://user?id={a.user.id})"
                for a in admins
                if a.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER)
                and not a.user.is_bot
            ]

            try:
                await bot.send_message(
                    chat_id,
                    f"⚠️ {', '.join(mentions)}\n"
                    f"User {user_mention} has sent **{count} link messages**.\n"
                    f"Do you want to mute them?",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔇 Mute", callback_data=f"mute:{chat_id}:{user_id}")],
                        [InlineKeyboardButton("❌ Ignore", callback_data=f"ignore:{chat_id}:{user_id}")]
                    ])
                )
            except Exception as e:
                await bot.send_message(1733124290, f"[WARN] Failed to notify group admins: {e}")

            # DM admins if possible
            for a in admins:
                if not a.user.is_bot:
                    try:
                        await bot.send_message(
                            a.user.id,
                            f"⚠️ In group **{message.chat.title}**, user {user_mention} "
                            f"has sent **{count} link messages**.",
                            reply_markup=InlineKeyboardMarkup([
                                [InlineKeyboardButton("🔇 Mute", callback_data=f"mute:{chat_id}:{user_id}")],
                                [InlineKeyboardButton("❌ Ignore", callback_data=f"ignore:{chat_id}:{user_id}")]
                            ])
                        )
                    except Exception as e:
                        await bot.send_message(1733124290, f"[WARN] Could not DM admin {a.user.id}: {e}")

            # reset user counter in DB
            try:
                await db.reset_violation(chat_id, user_id)
            except Exception as e:
                await bot.send_message(1733124290, f"[ERROR] Failed to reset violation counter: {e}")

    except Exception as e:
        await bot.send_message(1733124290, f"[ERROR] update_user_count failed: {e}")




@Client.on_callback_query(filters.regex(r"^(mute|ignore):"))
async def handle_admin_action(bot: Client, query):
    action, chat_id, user_id = query.data.split(":")
    chat_id, user_id = int(chat_id), int(user_id)

    # only admins can press
    admin = await bot.get_chat_member(chat_id, query.from_user.id)
    if admin.status not in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER) and query.from_user.id not in Config.ADMIN:
        await query.answer("Only admins can take action.", show_alert=True)
        return

    if action == "mute":
        try:
            await bot.restrict_chat_member(chat_id, user_id, ChatPermissions())
            await query.edit_message_text(f"✅ User [{user_id}](tg://user?id={user_id}) has been muted.")
        except Exception as e:
            await query.answer(f"Error: {e}", show_alert=True)
    elif action == "ignore":
        await db.reset_violation(chat_id, user_id)
        await query.edit_message_text("ℹ️ Action ignored, counter reset.")


from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
import os
import sys
import time
import asyncio
import logging
import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@Client.on_message(filters.command(["stats", "status"]) & filters.user(Config.ADMIN))
async def get_stats(bot, message):
    total_users = await db.total_users_count()
    total_grp = await db.total_grps_count()
    uptime = time.strftime("%Hh%Mm%Ss", time.gmtime(
        time.time() - Config.BOT_UPTIME))
    start_t = time.time()
    st = await message.reply('**Aᴄᴄᴇꜱꜱɪɴɢ Tʜᴇ Dᴇᴛᴀɪʟꜱ.....**')
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await st.edit(text=f"**--Bᴏᴛ Sᴛᴀᴛᴜꜱ--** \n\n**⌚️ Bᴏᴛ Uᴩᴛɪᴍᴇ:** {uptime} \n**🐌 Cᴜʀʀᴇɴᴛ Pɪɴɢ:** `{time_taken_s:.3f} ᴍꜱ` \n**👭 Tᴏᴛᴀʟ Uꜱᴇʀꜱ:** `{total_users}`\n 🍹Tᴏᴛᴀʟ Gʀᴏᴜᴩꜱ: `{total_grp}`")


# Restart to cancell all process
@Client.on_message(filters.private & filters.command("restart") & filters.user(Config.ADMIN))
async def restart_bot(b, m):
    await m.reply_text("🔄__Rᴇꜱᴛᴀʀᴛɪɴɢ.....__")
    os.execl(sys.executable, sys.executable, *sys.argv)


@Client.on_message(filters.command("broadcast") & filters.user(Config.ADMIN) & filters.reply)
async def broadcast_handler(bot: Client, m: Message):
    await bot.send_message(Config.LOG_CHANNEL, f"{m.from_user.mention} or {m.from_user.id} Iꜱ ꜱᴛᴀʀᴛᴇᴅ ᴛʜᴇ Bʀᴏᴀᴅᴄᴀꜱᴛ......")
    all_users = await db.get_all_users()
    broadcast_msg = m.reply_to_message
    sts_msg = await m.reply_text("Bʀᴏᴀᴅᴄᴀꜱᴛ Sᴛᴀʀᴛᴇᴅ..!")
    done = 0
    failed = 0
    success = 0
    start_time = time.time()
    total_users = await db.total_users_count()
    async for user in all_users:
        sts = await send_msg(user['_id'], broadcast_msg)
        if sts == 200:
            success += 1
        else:
            failed += 1
        if sts == 400:
            await db.delete_user(user['_id'])
        done += 1
        if not done % 20:
            await sts_msg.edit(f"Bʀᴏᴀᴅᴄᴀꜱᴛ Iɴ Pʀᴏɢʀᴇꜱꜱ: \nTᴏᴛᴀʟ Uꜱᴇʀꜱ {total_users} \nCᴏᴍᴩʟᴇᴛᴇᴅ: {done} / {total_users}\nSᴜᴄᴄᴇꜱꜱ: {success}\nFᴀɪʟᴇᴅ: {failed}")
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts_msg.edit(f"Bʀᴏᴀᴅᴄᴀꜱᴛ Cᴏᴍᴩʟᴇᴛᴇᴅ: \nCᴏᴍᴩʟᴇᴛᴇᴅ Iɴ `{completed_in}`.\n\nTᴏᴛᴀʟ Uꜱᴇʀꜱ {total_users}\nCᴏᴍᴩʟᴇᴛᴇᴅ: {done} / {total_users}\nSᴜᴄᴄᴇꜱꜱ: {success}\nFᴀɪʟᴇᴅ: {failed}")


@Client.on_message(filters.command("group_broadcast") & filters.user(Config.ADMIN) & filters.reply)
async def broadcst_handler(bot: Client, m: Message):
    await bot.send_message(Config.LOG_CHANNEL, f"{m.from_user.mention} or {m.from_user.id} Iꜱ ꜱᴛᴀʀᴛᴇᴅ ᴛʜᴇ Gʀᴩ Bʀᴏᴀᴅᴄᴀꜱᴛ......")
    all_grps = await db.get_all_grps()
    broadcast_msg = m.reply_to_message
    sts_msg = await m.reply_text("Bʀᴏᴀᴅᴄᴀꜱᴛ Sᴛᴀʀᴛᴇᴅ..!")
    done = 0
    failed = 0
    success = 0
    start_time = time.time()
    total_grps = await db.total_grps_count()
    async for user in all_grps:
        sts = await send_msg(user['_id'], broadcast_msg)
        if sts == 200:
            success += 1
        else:
            failed += 1
        if sts == 400:
            await m.reply(f"Cant Send To {user['_id']}")
        done += 1
        if not done % 20:
            await sts_msg.edit(f"Bʀᴏᴀᴅᴄᴀꜱᴛ Iɴ Pʀᴏɢʀᴇꜱꜱ: \nTᴏᴛᴀʟ Uꜱᴇʀꜱ {total_users} \nCᴏᴍᴩʟᴇᴛᴇᴅ: {done} / {total_users}\nSᴜᴄᴄᴇꜱꜱ: {success}\nFᴀɪʟᴇᴅ: {failed}")
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts_msg.edit(f"Bʀᴏᴀᴅᴄᴀꜱᴛ Cᴏᴍᴩʟᴇᴛᴇᴅ: \nCᴏᴍᴩʟᴇᴛᴇᴅ Iɴ `{completed_in}`.\n\nTᴏᴛᴀʟ Uꜱᴇʀꜱ {total_users}\nCᴏᴍᴩʟᴇᴛᴇᴅ: {done} / {total_users}\nSᴜᴄᴄᴇꜱꜱ: {success}\nFᴀɪʟᴇᴅ: {failed}")


async def send_msg(user_id, message):
    try:
        await message.forward(chat_id=int(user_id))
        return 200
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return send_msg(user_id, message)
    except InputUserDeactivated:
        logger.info(f"{user_id} : Dᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ")
        return 400
    except UserIsBlocked:
        logger.info(f"{user_id} : Bʟᴏᴄᴋᴇᴅ Tʜᴇ Bᴏᴛ")
        return 400
    except PeerIdInvalid:
        logger.info(f"{user_id} : Uꜱᴇʀ Iᴅ Iɴᴠᴀʟɪᴅ")
        return 400
    except Exception as e:
        logger.error(f"{user_id} : {e}")
        return 500

