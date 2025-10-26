import re
import os
import time

id_pattern = re.compile(r'^.\d+$')


class Config(object):
    # pyro client config
    API_ID = os.environ.get("API_ID", "")  # ⚠️ Required
    API_HASH = os.environ.get("API_HASH", "")  # ⚠️ Required
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")  # ⚠️ Required
    REQ_TOKEN = os.environ.get("REQ_TOKEN", "")
    LNK_TOKEN = os.environ.get("LNK_TOKEN", "")
    
    # database config
    DB_NAME = os.environ.get("DB_NAME", "Sigma_Rename")
    DB_URL = os.environ.get("DB_URL", "")  # ⚠️ Required
    REQ_URL = os.environ.get("REQ_URL", "")
    LNK_URL = os.environ.get("LNK_URL", "")
    # other configs
    BOT_UPTIME = time.time()
    PICS = os.environ.get("PICS", 'https://i.ibb.co/zV0gZjyC/x.jpg https://i.ibb.co/vvchyjBN/x.jpg https://i.ibb.co/QFHL0x0p/x.jpg https://i.ibb.co/WW3M16ZY/x.jpg https://i.ibb.co/YTyVsDSv/x.jpg https://i.ibb.co/W4GzgT0g/x.jpg https://i.ibb.co/MkHqCqyv/x.jpg https://i.ibb.co/V0jjskHZ/x.jpg https://i.ibb.co/Nn7dZPkn/x.jpg https://i.ibb.co/ynV7MMKN/x.jpg https://envs.sh/XN2.jpg https://envs.sh/XNu.jpg https://envs.sh/yqA.jpg https://envs.sh/XNh.jpg').split()
    ADMIN = [int(admin) if id_pattern.search(
        admin) else admin for admin in os.environ.get('ADMIN', '').split()]  # ⚠️ Required

    FORCE_SUB = os.environ.get("FORCE_SUB", "") # ⚠️ Required Username without @
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", ""))  # ⚠️ Required
    FLOOD = int(os.environ.get("FLOOD", '10'))
    BANNED_USERS = set(int(x) for x in os.environ.get(
        "BANNED_USERS", "1234567890").split())

    # wes response configuration
    WEBHOOK = bool(os.environ.get("WEBHOOK", True))
    PORT = int(os.environ.get("PORT", "8080"))


class Txt(object):
    # part of text configuration
    START_TXT = """<b>ʜᴇʏ {} 👋,
───────── ⋆⋅☆⋅⋆ ─────────
ɪ'ᴍ ᴀɴ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ʙᴏᴛ ᴜꜱᴇᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀʟʟ ᴍᴇꜱꜱᴀɢᴇꜱ ɪɴ ɢʀᴏᴜᴩ ᴀꜰᴛᴇʀ ᴀ ᴄᴇʀᴛᴀɪɴ ɪɴᴛᴇʀᴠᴀʟ ꜱᴇᴛ ʙʏ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ.

ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴩ ᴛᴏ ᴇɴᴊᴏʏ ᴛʜᴇ ᴩʀᴇᴍɪᴜᴍ ꜱᴇʀᴠɪᴄᴇ. 🍹
───────── ⋆⋅☆⋅⋆ ───────── </b>"""

    STRT_TXT = """<b>ʜᴇʏ {} 👋,
━━━━━━━━━━━━━━━━━━━━━━━
ɪ'ᴍ ᴀ ʟɪɴᴋ ᴅᴇʟᴇᴛᴇ ʙᴏᴛ ᴜꜱᴇᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀʟʟ ᴍᴇꜱꜱᴀɢᴇꜱ ᴄᴏɴᴛᴀɪɴɪɴɢ ʟɪɴᴋꜱ ᴀɴᴅ ʜʏᴩᴇʀʟɪɴᴋꜱ ɪɴ ᴀɴʏ ɢʀᴏᴜᴩ. 🍹
━━━━━━━━━━━━━━━━━━━━━━━
ᴊᴜꜱᴛ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴩ ᴀɴᴅ ɪ ᴡɪʟʟ ᴩʀᴇᴠᴇɴᴛ ᴜꜱᴇʀꜱ ꜰʀᴏᴍ ꜱᴇɴᴅɪɴɢ ʟɪɴᴋ. 🀄
━━━━━━━━━━━━━━━━━━━━━━━</b>"""

    ABOUT_TXT = """<b>╭───────────⍟
➥ Mʏ ɴᴀᴍᴇ : {}
➥ Pʀᴏɢʀᴀᴍᴇʀ : <a href=https://t.me/SyD_Xyz>ꪑ𝘳 𝘴ꪗᦔ 🌐</a> 
➥ Fᴏᴜɴᴅᴇʀ ᴏꜰ : <a href=https://t.me/BOT_cracker>B𝚘ᴛ ᑕяΔ¢к℮ґ 🎋</a>
➥ Lɪʙʀᴀʀy : <a href=https://t.me/+oej8cujHMFJhNmI9>Cᴏʟʟᴇᴄᴛɪᴏɴ...</a>
➥ Lᴀɴɢᴜᴀɢᴇ: <a href=https://t.me/+0Zi1FC4ulo8zYzVl>Bᴀᴄᴋ-Uᴩ 💦</a>
➥ ᴍʏ ꜱᴇʀᴠᴇʀ : <a href=https://t.me/Mod_Moviez_X>Tɢ 🗯️</a>
➥ ᴠᴇʀsɪᴏɴ : v1.0
╰───────────────⍟ """

    HELP_TXT = """Hᴇʀᴇ Iꜱ Mʏ Hᴇʟᴩ Cᴏᴍᴍᴀɴᴅ.
    
<b>⦿ Dᴇᴠᴇʟᴏᴩᴇʀ:</b> <a href=https://t.me/SyD_Xyz>🔅 ᴍ.ʀ Sʏᦔ 🔅</a>
""" 
    PIC_TXT = """ 
◽ <b><u>Hᴏᴡ Tᴏ Sᴇᴛ Tʜᴜᴍʙɴɪʟᴇ</u></b>
  
<b>•></b> /start Tʜᴇ Bᴏᴛ Aɴᴅ Sᴇɴᴅ Aɴy Pʜᴏᴛᴏ Tᴏ Aᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟy Sᴇᴛ Tʜᴜᴍʙɴɪʟᴇ.
<b>•></b> /del_thumb Uꜱᴇ Tʜɪꜱ Cᴏᴍᴍᴀɴᴅ Tᴏ Dᴇʟᴇᴛᴇ Yᴏᴜʀ Oʟᴅ Tʜᴜᴍʙɴɪʟᴇ.
<b>•></b> /view_thumb Uꜱᴇ Tʜɪꜱ Cᴏᴍᴍᴀɴᴅ Tᴏ Vɪᴇᴡ Yᴏᴜʀ Cᴜʀʀᴇɴᴛ Tʜᴜᴍʙɴɪʟᴇ.

<u><b><blockqoute>Jᴜꜱᴛ Sᴇɴᴅ Tʜᴇ Pɪᴄᴛᴜʀᴇ.. ⚡</blockqoute></u></b>"""

    
    
    META_TXT = """
❪ SET CUSTOM METADATA ❫
◽ <b><u>Tᴏ Cʜᴀɴɢᴇ Fɪʟᴇ Iɴꜰᴏʀᴍᴀᴛɪᴏɴꜱ </b></u>
<b>•></b> /metadata - Tᴏ ᴛᴜʀɴ ᴏꜰꜰ/ᴏɴ ᴀɴᴅ ꜱᴇᴇ ᴍᴇᴛᴀᴅᴀᴛᴀ
<b>•></b> /set_metadata - Tᴏ ᴄʜᴀɴɢᴇ ᴍᴇᴛᴅᴀᴛᴀ
☞ Fᴏʀ Exᴀᴍᴘʟᴇ:-

◦ <code> --change-title Powered By:- @ --change-author @ --change-video-title By:- @ --change-audio-title By :- @ --change-subtitle-title Subtitled By :- @ </code>

📥 Fᴏʀ Hᴇʟᴘ Cᴏɴᴛᴀᴄᴛ..: @SyD_XyZ
"""
    DUMP_TXT = """<b><u>Dᴜᴍᴩ Cʜᴀɴɴᴇʟ:</u></b>
A Cʜᴀɴɴᴇʟ Tᴏ Wʜɪᴄʜ Aʟʟ Rᴇɴᴀᴍᴇᴅ Fɪʟᴇꜱ Mᴜꜱᴛ Bᴇ Sᴇɴᴛ Aᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟ
◽ <b><u>Sᴇᴛ ᴅᴜᴍᴩ ᴄʜᴀɴɴᴇʟ.</b></u>
<b>•></b> /set_dump - Sᴇᴛ ᴅᴜᴍᴩ ᴄʜᴀɴɴᴇʟ
<b>•></b> /del_dump - Dᴇʟᴇᴛᴇ ᴅᴜᴍᴩ(ᴅᴇꜰᴜᴀʟᴛ ᴛᴏ ᴛʜᴇ ꜱᴇɴᴅᴇʀ ɪᴅ)
<b>•></b> /see_dump - Sᴇᴇ ᴄᴜʀʀᴇɴᴛ ᴅᴜᴍᴩ ɪᴅ"""
    
    SEND_METADATA = """
❪ SET CUSTOM METADATA ❫

☞ Fᴏʀ Exᴀᴍᴘʟᴇ:-

◦ <code> --change-title Powered By:- @ --change-author @ --change-video-title By:- @ --change-audio-title By :- @ --change-subtitle-title Subtitled By :- @ </code>

📥 Fᴏʀ Hᴇʟᴘ Cᴏɴᴛᴀᴄᴛ..: @SyD_XyZ
"""

    
