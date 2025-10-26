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
        await cb.answer("You ᴀʀᴇ ɴᴏᴛ ᴊᴏɪɴᴇᴅ ɪɴ ᴍʏ ᴄʜᴀɴɴᴇʟ, ᴊᴏɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ. 🎐", show_alert=True)
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
    added = await db.add_grp(message.chat.id)
    if added:
        try:
            c = await bot.get_chat(message.chat.id)
            m = await bot.get_chat_members_count(message.chat.id)
            await bot.send_message(
                1733124290,
                f"#GrouP\n📢 **New Group Added**\n🏷️ `{c.title or c.first_name or 'Unknown'}`\n🆔 `{message.chat.id}`\n👥 `{m}`"
            )
        except Exception as e:
            print(f"⚠️ Admin notify fail {message.chat.id}: {e}")

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
    if message.forward_from and message.forward_from.is_bot and message.forward_from.id in [273234066, 5605632845]:
        await safe_delete(message)
        await update_user_count(bot, message)
        return
    if message.forward_from_chat and message.forward_from_chat.id in [273234066, 5605632845]:
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
        if count in [10, 25, 30, 50, 60, 75, 90] or (count >= 100 and count % 25 == 0):
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
                syd = await bot.send_message(
                    chat_id,
                    f"⚠️ {', '.join(mentions)}\n"
                    f"Uꜱᴇʀ {user_mention} ʜᴀꜱ ꜱᴇɴᴛ **{count} ʟɪɴᴋ ᴍᴇꜱꜱᴀɢᴇꜱ**.\n"
                    f"Dᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴍᴜᴛᴇ ᴛʜᴇᴍ?",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("Mᴜᴛᴇ ⊘", callback_data=f"mute:{chat_id}:{user_id}"),
                        InlineKeyboardButton("Iɢɴᴏʀᴇ ⛌", callback_data=f"ignore:{chat_id}:{user_id}")
                    ]])
                )
            except Exception as e:
                await bot.send_message(1733124290, f"[WARN] Failed to notify group admins: {e}")

            # DM admins if possible
            for a in admins:
                if not a.user.is_bot:
                    try:
                        await bot.send_message(
                            a.user.id,
                            f"⚠️ Iɴ ɢʀᴏᴜᴩ **{message.chat.title}**, Uꜱᴇʀ {user_mention} ʜᴀꜱ ꜱᴇɴᴛ **{count} ʟɪɴᴋ ᴍᴇꜱꜱᴀɢᴇꜱ**.\n",
                            reply_markup=InlineKeyboardMarkup([[
                                InlineKeyboardButton("Mᴜᴛᴇ ⊘", callback_data=f"mute:{chat_id}:{user_id}"),
                                InlineKeyboardButton("Iɢɴᴏʀᴇ ⛌", callback_data=f"ignore:{chat_id}:{user_id}")
                            ]])
                        )
                    except Exception as e:
                        pass
                      #  await bot.send_message(1733124290, f"[WARN] Could not DM admin {a.user.id}: {e}")

            # reset user counter in DB
           # try:
               # await db.reset_violation(chat_id, user_id)
          #  except Exception as e:
           #     await bot.send_message(1733124290, f"[ERROR] Failed to reset violation counter: {e}")

            try:
                await asyncio.sleep(150)
                await syd.delete()
            except:
                pass
    except Exception as e:
        await bot.send_message(1733124290, f"[ERROR] update_user_count failed: {e}")




@Client.on_callback_query(filters.regex(r"^(mute|unmute|ignore):"))
async def handle_admin_action(bot: Client, query):
    action, chat_id, user_id = query.data.split(":")
    chat_id, user_id = int(chat_id), int(user_id)

    admin = await bot.get_chat_member(chat_id, query.from_user.id)
    if admin.status not in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER) and query.from_user.id not in Config.ADMIN:
        await query.answer("Oɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴛᴀᴋᴇ ᴀᴄᴛɪᴏɴ ⓘ", show_alert=True)
        return

    try:
        chat = await bot.get_chat(chat_id)
        chat_name = f" ɪɴ {chat.title or chat.first_name}"
    except Exception:
        chat_name = ""
        
    if action == "mute":
        try:
            u = await bot.get_users(user_id)
            syd = f"{u.first_name or ''} {u.last_name or ''}".strip() or u.username or "Unknown"
            await bot.restrict_chat_member(chat_id, user_id, ChatPermissions())
            await query.edit_message_text(
                f"Uꜱᴇʀ [{syd}](tg://user?id={user_id}) [ID: {user_id}] ʜᴀꜱ ʙᴇᴇɴ **ᴍᴜᴛᴇᴅ**{chat_name}. ✅",
                reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Uɴᴍᴜᴛᴇ ✓", callback_data=f"unmute:{chat_id}:{user_id}")]]
            ))
        except Exception as e:
            await query.answer(f"Error: {e}", show_alert=True)
    elif action == "unmute":
        try:
            u = await bot.get_users(user_id)
            syd = f"{u.first_name or ''} {u.last_name or ''}".strip() or u.username or "Unknown"
            await bot.restrict_chat_member(
                chat_id,
                user_id,
                ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True)
            )

            await query.edit_message_text(f"Uꜱᴇʀ [{syd}](tg://user?id={user_id}) [ID: {user_id}] ʜᴀꜱ ʙᴇᴇɴ **ᴜɴᴍᴜᴛᴇᴅ**{chat_name}. ✅")
        except Exception as e:
            await query.answer(f"Error: {e}", show_alert=True)

    elif action == "ignore":
        await db.reset_violation(chat_id, user_id)
        await query.edit_message_text("Aᴄᴛɪᴏɴ ɪɢɴᴏʀᴇᴅ, ᴄᴏᴜɴᴛᴇʀ ʀᴇꜱᴇᴛ ᵎ!ᵎ ")

    try:
        await asyncio.sleep(10)
        if query.message.chat.type != enums.ChatType.PRIVATE:
            await query.message.delete()
    except:
        pass

from pyrogram import Client, filters
import asyncio
from pyrogram.errors import FloodWait, ChatAdminRequired, ChatWriteForbidden, ChatInvalid

@Client.on_message(filters.command("groups") & filters.user(1733124290))
async def list_groups(bot: Client, msg):
    grps = await db.chas.find().to_list(None)
    if not grps:
        return await msg.reply("No groups stored yet.")

    text = "📋 **Stored Groups:**\n"
    for i, g in enumerate(grps, start=1):
        try:
            c = await bot.get_chat(g["_id"])
            m = await bot.get_chat_members_count(g["_id"])
            name = c.title or c.first_name or "Unknown"
            text += f"\n{i}. `{name}`\n   🆔 `{g['_id']}` | 👥 `{m}`"
            await asyncio.sleep(0.7)  # Flood-wait safety (Telegram API rate limit)
        except Exception as e:
            text += f"\n{i}. ⚠️ `{g['_id']}` — Error: {e}"
            await asyncio.sleep(0.5)

    # Telegram has message length limits (4096 chars), handle if too long
    if len(text) > 4000:
        for chunk in [text[i:i+4000] for i in range(0, len(text), 4000)]:
            await msg.reply(chunk)
            await asyncio.sleep(1)
    else:
        await msg.reply(text)



@Client.on_message(filters.command("invite") & filters.user(1733124290))
async def get_invites(bot: Client, msg):
    parts = msg.text.split()
    if len(parts) < 2:
        return await msg.reply("Usage:\n`/invite <chat_id1> <chat_id2> ...`", quote=True)

    chat_ids = parts[1:]
    text = "🔗 **Group Invite Links / Usernames:**\n"
    
    for i, cid in enumerate(chat_ids, start=1):
        try:
            cid = int(cid)
            chat = await bot.get_chat(cid)
            
            if chat.username:
                link = f"https://t.me/{chat.username}"
            else:
                try:
                    invite = await bot.create_chat_invite_link(cid)
                    link = invite.invite_link
                except ChatAdminRequired:
                    link = "❌ Bot not admin (can't create link)"
                except ChatWriteForbidden:
                    link = "❌ Bot restricted in group"
                except Exception as e:
                    link = f"⚠️ Error: {e}"

            name = chat.title or chat.first_name or "Unknown"
            text += f"\n{i}. `{name}`\n   🆔 `{cid}`\n   🔗 {link}"

        except FloodWait as f:
            await asyncio.sleep(f.value + 1)
        except ChatInvalid:
            text += f"\n{i}. ⚠️ Invalid chat ID: `{cid}`"
        except Exception as e:
            text += f"\n{i}. ⚠️ Error for `{cid}`: {e}"
        
        await asyncio.sleep(1)  # floodwait safety

    if len(text) > 4000:
        for chunk in [text[i:i+4000] for i in range(0, len(text), 4000)]:
            await msg.reply(chunk)
            await asyncio.sleep(1)
    else:
        await msg.reply(text)



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

