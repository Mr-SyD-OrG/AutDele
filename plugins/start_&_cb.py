import random
import logging
from pyrogram import Client, filters, enums
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait, ChatAdminRequired, UserNotParticipant, PeerIdInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, CallbackQuery, Message
from .database import db
from config import Config, Txt
from info import AUTH_CHANNEL
from helper.utils import is_req_subscribed
import humanize
from time import sleep
from syd import send_log
logger = logging.getLogger(__name__)

@Client.on_message(filters.command("start"))
async def start(client, message):
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        await db.add_grp(message.chat.id)
    if message.from_user.id in Config.BANNED_USERS:
        await message.reply_text("Sorry, You are banned.")
        return

    user = message.from_user
    if not await db.users.find_one({"_id": user.id}):
        await db.add_user(user.id)
        await send_log(client, message)
    button = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            '✧ ᴜᴘᴅᴀᴛᴇꜱ', url='https://t.me/Bot_Cracker'),
        InlineKeyboardButton(
            'ꜱᴜᴘᴘᴏʀᴛ ✧', url='https://t.me/+O1mwQijo79s2MjJl')],
        [InlineKeyboardButton('✧ ᴏᴡɴᴇʀ ✧', user_id=1733124290)
    ], [
        InlineKeyboardButton('✧ ʙᴏᴛꜱ', url='https://t.me/Bot_Cracker/17'),
        InlineKeyboardButton('ᴜᴩᴅᴀᴛᴇꜱ ✧', url='https://t.me/Mod_Moviez_X')]])
    if Config.PICS:
        await message.reply_photo(random.choice(Config.PICS), caption=Txt.START_TXT.format(user.mention), reply_markup=button)
    else:
        await message.reply_text(text=Txt.START_TXT.format(user.mention), reply_markup=button, disable_web_page_preview=True)


@Client.on_message(filters.private & filters.command("disclaimer"))
async def disclaimer(client, message):
    await message.reply_text(
        text="""ᴅɪꜱᴄʟᴀɪᴍᴇʀ:
                ɴᴇᴠᴇʀ ꜱᴇɴᴅ ᴩᴇʀꜱᴏɴᴀʟ ꜰɪʟᴇꜱ, ꜱɪɴᴄᴇ ᴛʜᴇʏ ᴀʀᴇ ꜱᴛᴏʀᴇᴅ ᴛᴏ ꜰɪɴᴅ ᴀɴʏ ꜱᴜꜱᴩɪᴄɪᴏᴜꜱ ᴀᴄᴛɪᴠɪᴛʏ ᴅᴏɴᴇ ʙʏ ᴛʜᴇ ᴜꜱᴇʀꜱ
                ᴀʟᴡᴀʏ ᴜꜱᴇ ᴛʜᴇ ʙᴏᴛ ᴩʀᴏᴩᴇʀʟʏ ᴀɴᴅ ᴛᴀᴋᴇ ʀᴇꜱᴩᴏɴꜱɪʙɪʟᴛʏ ᴏꜰ ᴛʜᴇ ꜰɪʟᴇ, ᴛʜᴇʏ ᴀʀᴇ ʏᴏᴜʀ ᴩʀᴏᴩᴇʀᴛɪᴇꜱ ꜱᴏ ᴛʜᴇ ꜰɪʟᴇꜱ ᴀᴛ ʏᴏᴜʀ ᴏᴡɴ ʀɪꜱᴋ.
                ꜱʜᴀʀɪɴɢ ᴀᴅᴜʟᴛ ꜰɪʟᴇꜱ ᴡɪʟʟ ʟᴇᴀᴅ ᴛᴏ ʏᴏᴜʀ ʙᴀɴ, ᴀɴᴅ ꜰᴜʀᴛʜᴇʀ ʏᴏᴜ ᴍᴀʏ ɴᴏᴛ ʙᴇ ᴀʙʟᴇ ᴛᴏ ᴜꜱᴇ ᴛʜᴇ ʙᴏᴛ.""", 
        disable_web_page_preview=True
    )
    
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
import asyncio, re

# --- Constants ---
SYD_CHANNELS = ["Bot_Cracker", "Mod_Moviez_X"] #"@MrSyD_TG", 
SYD_BACKUP_LINK = "https://t.me/bot_crackers"
REQUIRED_CHAT_IDS = [-1001823125512]
CHAT_INVITE_LINKS = {
    -1001823125512: "https://t.me/+sBspXGfNFYtmZWRl"  # Replace with actual invite links
}

# --- Time Parser ---
def parse_time(time_str):
    match = re.match(r'^(\d+)([smh])$', time_str.lower())
    if not match:
        return None
    value, unit = match.groups()
    value = int(value)
    return value * {"s": 1, "m": 60, "h": 3600}[unit]


# --- Bot Admin Check ---
async def is_bot_admin(bot, chat_id: int):
    try:
        member = await bot.get_chat_member(chat_id, "me")
        return member.status in ["administrator", "creator"]
    except:
        return False

async def is_user_admin(bot, user_id: int, chat_id: int):
    try:
        user = await bot.get_chat_member(chat_id, user_id)
        if (
            user.status != enums.ChatMemberStatus.ADMINISTRATOR
            and user.status != enums.ChatMemberStatus.OWNER
            and user_id not in Config.ADMIN
        ):
            return False
        return True
    except Exception as e:
        print(f"is_user_admin error: {e}")
        return False


async def ensure_member(client, msg, user_id):
    """
    Ensures the user is in all required SYD_CHANNELS and private chats (REQUIRED_CHAT_IDS).
    Sends join/invite buttons if not.
    """
    replyable = msg #.message if hasattr(msg, "message") else msg

    not_joined = []

    # Check public channels (username-based)
    for ch in SYD_CHANNELS:
        try:
            member = await client.get_chat_member(ch, user_id)
            if member.status in {"left", "kicked"}:
                not_joined.append(("channel", ch))
        except UserNotParticipant:
            not_joined.append(("channel", ch))
        except Exception:
            pass

    # Check private groups/chats by ID
    for chat_id in REQUIRED_CHAT_IDS:
        try:
            member = await client.get_chat_member(chat_id, user_id)
            if member.status in {"left", "kicked"}:
                not_joined.append(("private", chat_id))
        except UserNotParticipant:
            not_joined.append(("private", chat_id))
        except Exception:
            pass

    if not not_joined:
        return True

    # Build button rows
    join_buttons = []

    for kind, chat in not_joined:
        if kind == "channel":
            join_buttons.append([
                InlineKeyboardButton(
                    text=f"✧ Join {str(chat).replace('_', ' ').title()} ✧",
                    url=f"https://t.me/{str(chat).lstrip('@')}"
                )
            ])
        elif kind == "private":
            invite_link = CHAT_INVITE_LINKS.get(chat)
            if invite_link:
                join_buttons.append([
                    InlineKeyboardButton(
                        text="✧ Join Private Chat ✧",
                        url=invite_link
                    )
                ])

    join_buttons.append([
        InlineKeyboardButton("❄️ Jᴏɪɴᴇᴅ ❄️", callback_data="check_subscription")
    ])

    await replyable.reply_text(
        text="**Pʟᴇᴀꜱᴇ ᴊᴏɪɴ ɪɴ ᴏᴜʀ ᴀʟʟ ʀᴇqᴜɪʀᴇᴅ ᴄʜᴀɴɴᴇʟꜱ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ..🫧 \nᴡᴇ ᴩʀᴏᴠɪᴅᴇꜱ ɢᴏᴏᴅ ꜱᴇʀᴠɪᴄᴇꜱ ʜᴇɴᴄᴇ ᴡᴇ ᴀʟꜱᴏ ɴᴇᴇᴅ ʏᴏᴜʀ ꜱᴜᴩᴩᴏʀᴛ ᴩʟᴇᴀꜱᴇ ᴅᴏ ꜱᴏ 🎐**",
        reply_markup=InlineKeyboardMarkup(join_buttons),
        quote=True,
        disable_web_page_preview=True
    )
    return False



@Client.on_callback_query(filters.regex("^check_subscription$"))
async def check_subscription(bot, cb: CallbackQuery):
    if await ensure_member(bot, cb.message, cb.from_user.id):
        # User has now joined everything
        await cb.answer("Yᴏᴜ ʜᴀᴠᴇ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴊᴏɪɴᴇᴅ! ✅ Pʟᴇᴀꜱᴇ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ ᴀɢᴀɪɴ. 😀", show_alert=True)
        await cb.message.delete()
        
    else:
        # Still missing some channels
        await cb.answer("Yᴏᴜ ʜᴀᴠᴇ'ɴᴛ ᴊᴏɪɴᴇᴅ ᴏɴ ᴀʟʟ ᴄʜᴀɴɴᴇʟꜱ. Pʟᴇᴀꜱᴇ ᴊᴏɪɴ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.", show_alert=True)
        await cb.message.delete()
# --- /setdelete ---
@Client.on_message(filters.command("setdelete"))
async def set_delete_handler(bot, message: Message):
    user_id = message.from_user.id  # msg is cb.message
    if not await ensure_member(bot, message, user_id):
        return
    args = message.text.split()
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        await db.add_grp(message.chat.id)
        await message.reply_text(f"{message.chat.id}")
        if len(args) != 2:
            return await message.reply("⚠️ Usage: `/setdelete 30s`, `2m`, or `1h`", quote=True)

        time_sec = parse_time(args[1])
        if not time_sec:
            return await message.reply("❌ Invalid format. Use `s`, `m`, or `h`.")

        try:
            await message.delete()
        except Exception as e:
            return await message.reply("❌ I need to be admin (with delete permission) to auto-delete messages.")

        if not await is_user_admin(bot, message.from_user.id, message.chat.id):
            return await message.reply("❌ Only group admins can view auto-delete time.")

        await db.chats.update_one(
            {"chat_id": message.chat.id},
            {"$set": {"delete_after": time_sec}},
            upsert=True
        )
        await message.reply(f"✅ Messages will auto-delete after {time_sec} seconds.")
        return 
    
    if len(args) != 3:
        return await message.reply("⚠️ Usage: `/setdelete chat_id time` Or Send In The Group.", quote=True)

    try:
        chat_id = int(args[1])
    except ValueError:
        return await message.reply("❌ Invalid chat ID.")

    time_sec = parse_time(args[2])
      
    if not time_sec:
        return await message.reply("❌ Invalid time format.")

      
    try:
        await message.delete()
    except Exception as e:
        return await message.reply("❌ I need to be admin (with delete permission) to auto-delete messages.")

    if not await is_user_admin(bot, message.from_user.id, chat_id):
        return await message.reply("❌ You must be admin in that group.")

    await db.chats.update_one(
        {"chat_id": chat_id},
        {"$set": {"delete_after": time_sec}},
        upsert=True
    )
    await message.reply(f"✅ Messages will auto-delete in `{chat_id}` after {time_sec} seconds.\n⚠️ Note: Bot Must Have Admin Permission (With Delete)")


# --- /getdelete ---
@Client.on_message(filters.command("getdelete"))
async def get_delete_handler(bot, message: Message):
    user_id = message.from_user.id  # msg is cb.message
    if not await ensure_member(bot, message, user_id):
        return

    args = message.text.split()

    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        await db.add_grp(message.chat.id)
        if not await is_user_admin(bot, message.from_user.id, message.chat.id):
            return await message.reply("❌ Only group admins can view auto-delete time.")

        
        seconds = await db.get_chat_delete_time(message.chat.id)
        if seconds:
            await message.reply(f"🕒 Auto-delete is set to **{seconds} seconds**.")
        else:
            await message.reply("❌ Auto-delete not set in this group.")
        return
    
    if len(args) != 2:
        return await message.reply("⚠️ Usage: `/getdelete chat_id` Or Send In The Group.")
    try:
        chat_id = int(args[1])
    except ValueError:
        return await message.reply("❌ Invalid chat_id.")

    if not await is_user_admin(bot, message.from_user.id, chat_id):
        return await message.reply("❌ You must be admin in that group.")

    seconds = await db.get_chat_delete_time(chat_id)
    if seconds:
        await message.reply(f"🕒 Auto-delete for `{chat_id}` is set to **{seconds} seconds**.")
    else:
        await message.reply("❌ Auto-delete not set in that group.")


@Client.on_message(filters.command("deldelete"))
async def del_delete_handler(bot, message: Message):
    user_id = message.from_user.id  # msg is cb.message
    if not await ensure_member(bot, message, user_id):
        return

    args = message.text.split()

    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        await db.add_grp(message.chat.id)
        if not await is_user_admin(bot, message.from_user.id, message.chat.id):
            return await message.reply("❌ Only group admins can remove auto-delete.")
        await db.remove_chat_delete_time(message.chat.id)
        await message.reply("✅ Auto-delete removed for this group.")
        return
    if len(args) != 2:
        return await message.reply("⚠️ Usage: `/deldelete chat_id` Or Send In The Group.")
    try:
        chat_id = int(args[1])
    except ValueError:
        return await message.reply("❌ Invalid chat_id.")

    if not await is_user_admin(bot, message.from_user.id, chat_id):
        return await message.reply("❌ You must be admin in that group.")

    await db.remove_chat_delete_time(chat_id)
    await message.reply(f"✅ Auto-delete removed for chat `{chat_id}`.")



# --- Auto Delete Group Messages ---
@Client.on_message(filters.group)
async def auto_delete_message(bot: Client, message: Message):
    config = await db.chats.find_one({"chat_id": message.chat.id})
    if config and config.get("delete_after"):
        delay = config["delete_after"]
        await asyncio.sleep(delay)
        try:
            await message.delete()
        except Exception as e:
            await message.reply(e)
            print(f"Failed to delete: {e}")
