# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import traceback
from pyrogram.types import Message
from pyrogram import Client, filters
from asyncio.exceptions import TimeoutError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from config import Config
from .database import get_session, set_session

SESSION_STRING_SIZE = 351
API_ID, API_HASH = Config.API_ID, Config.API_HASH
@Client.on_message(filters.private & ~filters.forwarded & filters.command(["logout"]))
async def logout(client, message):
    user_data = get_session(message.from_user.id)  
    if user_data is None:
        return 
    await set_session(message.from_user.id, session=None)  
    await message.reply("**Logout Successfully** ♦")

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["login"]))
async def main(bot: Client, message: Message):
    user_data = get_session(message.from_user.id)
    if user_data is not None:
        await message.reply("**Your Are Already Logged In. First /logout Your Old Session. Then Do Login.**")
        return 
    user_id = int(message.from_user.id)
    phone_number_msg = await bot.ask(chat_id=user_id, text="<b>Please send your phone number which includes country code</b>\n<b>Example:</b> <code>+13124562345, +9171828181889</code>")
    if phone_number_msg.text=='/cancel':
        return await phone_number_msg.reply('<b>process cancelled !</b>')
    phone_number = phone_number_msg.text
    client = Client(":memory:", API_ID, API_HASH)
    await client.connect()
    #client = Client(session_name=":memory:", api_id=API_ID, api_hash=API_HASH, in_memory=True)

  #  await client.start(phone_number=phone_number)
    await phone_number_msg.reply("Sending OTP...")
    try:
        code = await client.send_code(phone_number)
        phone_code_msg = await bot.ask(user_id, "Please check for an OTP in official telegram account. If you got it, send OTP here after reading the below format. \n\nIf OTP is `12345`, **please send it as** `1 2 3 4 5`.\n\n**Enter /cancel to cancel The Procces**", filters=filters.text, timeout=600)
    except PhoneNumberInvalid:
        await phone_number_msg.reply('`PHONE_NUMBER` **is invalid.**')
        return
    except Exception as e:
        await message.reply(e)
        
    if phone_code_msg.text=='/cancel':
        return await phone_code_msg.reply('<b>process cancelled !</b>')
    try:
        phone_code = phone_code_msg.text.replace(" ", "")
        await client.sign_in(phone_number, code.phone_code_hash, phone_code)
    except PhoneCodeInvalid:
        await phone_code_msg.reply('**OTP is invalid.**')
        return
    except PhoneCodeExpired:
        await phone_code_msg.reply('**OTP is expired.**')
        return
    except SessionPasswordNeeded:
        two_step_msg = await bot.ask(user_id, '**Your account has enabled two-step verification. Please provide the password.\n\nEnter /cancel to cancel The Procces**', filters=filters.text, timeout=300)
        if two_step_msg.text=='/cancel':
            return await two_step_msg.reply('<b>process cancelled !</b>')
        try:
            password = two_step_msg.text
            await client.check_password(password=password)
        except PasswordHashInvalid:
            await two_step_msg.reply('**Invalid Password Provided**')
            return
    string_session = await client.export_session_string()
    await client.disconnect()
    if len(string_session) < SESSION_STRING_SIZE:
        return await message.reply('<b>invalid session sring</b>')
    try:
        user_data = await db.get_session(message.from_user.id)
        if user_data is None:
            uclient = Client(":memory:", session_string=string_session, api_id=API_ID, api_hash=API_HASH)
            await uclient.connect()
            set_session(message.from_user.id, session=string_session)
    except Exception as e:
        return await message.reply_text(f"<b>ERROR IN LOGIN:</b> `{e}`")
    await bot.send_message(message.from_user.id, "<b>Account Login Successfully.\n\nIf You Get Any Error Related To AUTH KEY Then /logout first and /login again</b>")

CHAT_ID = -1002965604896
@Client.on_message(filters.command("accept") & filters.private & filters.document)
async def accept_users(client, message):
    if not message.document:
        return await message.reply("❌ Please attach a file with user IDs.")

    show = await message.reply("**Processing file...**")

    # Get user session
    user_data = get_session(message.from_user.id)
    if not user_data:
        return await show.edit("**You need to /login first.**")

    # Start client with string session
    acc = Client(
        session_name=":memory:",
        api_id=API_ID,
        api_hash=API_HASH,
        in_memory=True,
        session_string=user_data
    )
    await acc.start()

    # Read excluded IDs from file
    file = await message.download(in_memory=True)
    content = file.read().decode("utf-8")
    excluded_ids = set(int(line.strip()) for line in content.splitlines() if line.strip().isdigit())

    await show.edit("**Accepting all pending join requests except listed users...**")

    try:
        while True:
            pending_requests = [req async for req in acc.get_chat_join_requests(CHAT_ID)]
            if not pending_requests:
                break
            for req in pending_requests:
                if req.from_user.id not in excluded_ids:
                    await acc.approve_chat_join_request(CHAT_ID, req.from_user.id)
            await asyncio.sleep(1)
        await show.edit("✅ Done! All requests accepted (excluding listed users).")
    except Exception as e:
        await show.edit(f"❌ Error: {str(e)}")
    finally:
        await acc.stop()
