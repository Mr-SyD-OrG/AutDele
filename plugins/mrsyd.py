import math, time, random, os, tempfile, asyncio, re
from pyrogram import Client, enums, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from helper.database import db
from info import AUTH_CHANNEL
# ── helper UI builders ─────────────────────────────────────────────────────────
from pyrogram.errors import UserNotParticipant
SYD_CHANNELS = ["Bot_Cracker", "Mod_Moviez_X", "MrSyD_Tg"]
SYD_BACKUP_LINK = "https://t.me/+0Zi1FC4ulo8zYzVl"        # your backup group

async def is_req_subscribed(bot, query):
    if await db.find_join_req(query.from_user.id):
        return True
    try:
        user = await bot.get_chat_member(AUTH_CHANNEL, query.from_user.id)
    except UserNotParticipant:
        pass
    except Exception as e:
        logger.exception(e)
    else:
        if user.status != enums.ChatMemberStatus.BANNED:
            return True

    return False
async def ensure_member(client, msg):
    """
    Returns True if the user is a member of every channel in SYD_CHANNELS.
    Otherwise sends a join-prompt and returns False.
    Works with both Message and CallbackQuery objects.
    """
    user_id   = msg.from_user.id
    chat_id   = msg.message.chat.id
    replyable = msg.message

    # Figure out the correct message to reply to
    reply_to_msg = replyable.reply_to_message or replyable

    not_joined = []
    for ch in SYD_CHANNELS:
        try:
            member = await client.get_chat_member(ch, user_id)
            if member.status in {"kicked", "left"}:
                not_joined.append(ch)
        except UserNotParticipant:
            not_joined.append(ch)
        except Exception:
            pass

    if not not_joined:
        return True

    join_rows = [[
        InlineKeyboardButton(
            text=f"✧ Jᴏɪɴ {str(ch).replace('_',' ').title()} ✧",
            url=f"https://t.me/{str(ch).lstrip('@')}"
        )
    ] for ch in not_joined]

    join_rows.append([InlineKeyboardButton("✧ Jᴏɪɴ Bᴀᴄᴋ Uᴩ ✧", url=SYD_BACKUP_LINK)])
    join_rows.append([InlineKeyboardButton("☑ ᴊᴏɪɴᴇᴅ ☑", callback_data="check_subscription")])

    text = (
        "**ꜱᴏʀʀʏ, ᴅᴜᴇ ᴛᴏ ᴏᴠᴇʀʟᴏᴀᴅ ᴜꜱᴇʀꜱ ᴊᴏɪɴᴇᴅ ɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ꜰᴇᴀᴛᴜʀᴇ.**\n"
        "ᴩʟᴇᴀꜱᴇ ᴊᴏɪɴ ᴀɴᴅ ᴘʀᴇꜱꜱ **ᴊᴏɪɴᴇᴅ** ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ.."
    )

    await reply_to_msg.reply_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(join_rows),
        quote=True,
        disable_web_page_preview=True
    )
    return False


async def handle_process_flags(client, query):
    user_id = query.from_user.id

    # ── read current flags (None → False) ────────────────────────────────────
    oneprocess = await db.get_user_value(user_id, "oneprocess") or False
    twoprocess = await db.get_user_value(user_id, "twoprocess") or False

    if oneprocess and twoprocess:
        await query.message.reply_text(
            "⚠️ Yᴏᴜ'ʀᴇ ᴀʟʀᴇᴀᴅʏ ɪɴ **ᴛᴡᴏ ᴀᴄᴛɪᴠᴇ ꜱᴇꜱꜱɪᴏɴꜱ**.\n"
            "Pʟᴇᴀꜱᴇ ᴡᴀɪᴛ ᴜɴᴛɪʟʟ ᴛʜᴇʏ ꜰɪɴɪꜱʜ ᴏʀ ɢᴇᴛ ᴩʀᴇᴍɪᴜᴍ.",
            quote=True
        )
        return False

    # first job is active → allow second only if member
    if oneprocess:
        if await ensure_member(client, query):
            if not twoprocess:
                await db.set_user_value(user_id, "twoprocess", True)
            return True
        return False  # ensure_member already sent join prompt

    # no job yet → start first one
    await db.set_user_value(user_id, "oneprocess", True)
    return True



def build_even_keyboard() -> InlineKeyboardMarkup:
    rows, row = [], []
    for sec in range(2, 22, 2):
        row.append(InlineKeyboardButton(str(sec), callback_data=f"getshot#{sec}"))
        if len(row) == 5:
            rows.append(row); row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(rows)

def generate_progress_bar(percentage: float) -> str:
    filled = "⬢" * math.floor(percentage / 5)
    empty  = "⬡" * (20 - math.floor(percentage / 5))
    return filled + empty
    
def parse_hms(text: str) -> int | None:
    """
    Convert h:m:s or m:s (hours optional) to seconds (int).
    Returns None if the format is invalid.
    """
    parts = text.strip().split(":")
    if not 2 <= len(parts) <= 3:
        return None
    try:
        parts = [int(p) for p in parts]
    except ValueError:
        return None
    if len(parts) == 2:  # m:s
        m, s = parts
        h = 0
    else:                # h:m:s
        h, m, s = parts
    if m > 59 or s > 59 or h < 0 or m < 0 or s < 0:
        return None
    return h * 3600 + m * 60 + s
def humanbytes(size: int) -> str:
    power, unit = 1024, 0
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    while size >= power and unit < len(units) - 1:
        size /= power; unit += 1
    return f"{size:.2f} {units[unit]}"

def calculate_times(diff, current, total, speed):
    if speed == 0:
        return diff, 0, ""
    time_to_completion = (total - current) / speed
    return diff, time_to_completion, time_to_completion + diff

async def progress_for_pyrogram(current, total, ud_type, message, start):
    now, diff = time.time(), time.time() - start
    if int(diff) % 5 == 0 or current == total:
        percentage = current * 100 / total
        speed      = current / diff if diff else 0
        _, eta, _  = calculate_times(diff, current, total, speed)

        bar = generate_progress_bar(percentage)
        text = (
            f"{ud_type}\n\n"
            f"{bar} `{percentage:.2f}%`\n"
            f"**{humanbytes(current)} / {humanbytes(total)}** "
            f"at **{humanbytes(speed)}/s**\n"
            f"ETA: `{round(eta)} s`"
        )
        try:
            await message.edit(text=text)
        except Exception as e:
            print("Progress update failed:", e)

# ── FFmpeg helpers ─────────────────────────────────────────────────────────────

async def ffmpeg_trim_async(src: str, start_sec: int, end_sec: int,
                            dst: str, reencode: bool = False):
    if not reencode:
        cmd = [
            "ffmpeg", "-ss", str(start_sec), "-to", str(end_sec),
            "-i", src, "-c", "copy", "-metadata", f"title=Trim By: @Videos_Sample_Bot 🧊", "-y", dst
        ]
    else:
        cmd = [
            "ffmpeg", "-ss", str(start_sec), "-to", str(end_sec),
            "-i", src, "-c:v", "libx264", "-c:a", "aac",
            "-preset", "medium", "-metadata", f"title=Trim By: @Videos_Sample_Bot 🧊", "-y", dst
        ]
    
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL
    )
    await proc.communicate()
    return proc.returncode

                                
async def ffmpeg_sample_async(src: str, start: int, length: int, dst: str):
    cmd = [
        "ffmpeg", "-ss", str(start), "-i", src, "-t", str(length),
        "-metadata", "title= Sample By: @Videos_Sample_Bot 🧊",
        "-c:v", "libx264", "-c:a", "aac",
        "-preset", "ultrafast", "-y", dst
    ]
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL
    )
    await process.communicate()

async def ffmpeg_screenshot_async(src: str, sec: int, dst: str):
    cmd = [
        "ffmpeg", "-ss", str(sec), "-i", src,
        "-vframes", "1", "-q:v", "2", "-y", dst
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL
    )
    await proc.communicate()

# ── main callback handler ──────────────────────────────────────────────────────
@Client.on_callback_query()
async def callback_handler(client: Client, query):
    if AUTH_CHANNEL and not await is_req_subscribed(client, query):
        btn = [[InlineKeyboardButton("⊛ Jᴏɪɴ Uᴘᴅᴀᴛᴇꜱ CʜᴀɴɴᴇL ⊛", url=invite_link.invite_link)],
               [InlineKeyboardButton("↻ Tʀʏ Aɢᴀɪɴ ↻", callback_data="checksub")]]

        await query.message.reply(
            text="Jᴏɪɴ Oᴜʀ Uᴘᴅᴀᴛᴇꜱ Cʜᴀɴɴᴇʟ Aɴᴅ Tʜᴇɴ Cʟɪᴄᴋ Oɴ Tʀʏ Aɢᴀɪɴ Tᴏ Cᴏɴᴛɪɴᴜᴇ.",
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return
    orig = query.message.reply_to_message
    if not orig or not (orig.video or orig.document):
        return await query.answer("❌ Please reply to a media file.", show_alert=True)

    media = orig.video or orig.document
    duration = getattr(media, "duration", 120) or 120

    # ─ 1. 30-second sample
    if query.data == "sample":
        await query.answer("Generating sample…", show_alert=False)
        proceed = await handle_process_flags(client, query)
        if not proceed:
            return
            

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            full_path = tmp.name
        sample_path = full_path.replace(".mp4", "_@GetTGlinks_sample.mp4")

        try:
            progress_msg = await query.message.reply("Sᴛᴀʀᴛɪɴɢ ᴅᴏᴡɴʟᴏᴀᴅ...", quote=True)
            await client.download_media(
                message=media,
                file_name=full_path,
                progress=progress_for_pyrogram,
                progress_args=("__Dᴏᴡɴʟᴏᴀᴅɪɴɢ…__", progress_msg, time.time())
            )
            await progress_msg.edit("Gᴇɴᴇʀᴀᴛɪɴɢ...")
            start = random.randint(0, max(0, duration - 30))
            await ffmpeg_sample_async(full_path, start, 30, sample_path)
            await orig.reply_video(
                video=sample_path,
                caption=f"Sᴀᴍᴩʟᴇ 30ꜱ (Fʀᴏᴍ {start}s)",
                quote=True,
                progress=progress_for_pyrogram,                    # <<< NEW
                progress_args=("__Uᴩʟᴏᴀᴅɪɴɢ Sᴀᴍᴩʟᴇ__", progress_msg, time.time())  # <<< NEW
            )
            await progress_msg.delete()

        except Exception as e:
            await query.message.reply(
                f"❌ FFmpeg error:\n<code>{e.stderr.decode()}</code>",
                parse_mode=enums.ParseMode.HTML,
                quote=True
            )
        finally:
            for f in (full_path, sample_path):
                if os.path.exists(f):
                    os.remove(f)

        syd = await query.message.reply("Yᴏᴜ ʜᴀᴠᴇ ᴛᴏ ᴡᴀɪᴛ 5 ᴍɪɴᴜᴛᴇꜱ ꜰᴏʀ ɴᴇxᴛ ᴩʀᴏᴄᴇꜱꜱ ᴏʀ ɢᴏ ᴩᴀʀᴀʟʟᴇʟ..!")
        await asyncio.sleep(2)
        await syd.delete()
        await query.message.reply("Sᴇɴᴅ ꜰɪʟᴇ ꜰᴏʀ ɴᴇxᴛ ᴩʀᴏᴄᴇꜱꜱ...! 🧊")
        twoprocess = await db.get_user_value(query.from_user.id, "twoprocess") or False
        if twoprocess:
            await db.set_user_value(query.from_user.id, "twoprocess", False)
        else:
            await db.set_user_value(query.from_user.id, "oneprocess", False)


    # ─ 2. Ask for screenshot count
    elif query.data == "screenshot":
        await query.answer()
        await orig.reply(
            "Cʜᴏᴏꜱᴇ ɴᴜᴍʙᴇʀ ᴏꜰ ꜱᴄʀᴇᴇɴꜱʜᴏᴛꜱ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ:",
            reply_markup=build_even_keyboard(),
            quote=True
        )

    # ─ 3. Take screenshots
    elif query.data.startswith("getshot#"):
        count = int(query.data.split("#")[1])
        await query.answer(f"Taking {count} random screenshots…", show_alert=False)

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            full_path = tmp.name

        try:
            progress_msg = await query.message.reply("📥 Starting download...", quote=True)
            await client.download_media(
                message=media,
                file_name=full_path,
                progress=progress_for_pyrogram,
                progress_args=("__Downloading…__", progress_msg, time.time())
            )

            timestamps = sorted(random.sample(range(2, max(duration - 1, 3)), count))
            media_group = []
            paths = []

            for idx, ts in enumerate(timestamps, start=1):
                shot_path = full_path.replace(".mp4", f"_s{idx}.jpg")
                await ffmpeg_screenshot_async(full_path, ts, shot_path)
                paths.append(shot_path)
                media_group.append(InputMediaPhoto(
                    media=shot_path,
                    caption=f"Sᴄʀᴇᴇɴꜱʜᴏᴛꜱ {count}" if idx == 1 else None
                ))

            await client.send_media_group(
                chat_id=query.message.chat.id,
                media=media_group,
                reply_to_message_id=orig.id
            )
            await progress_msg.delete()
        except Exception as e:
            await query.message.reply(
                f"❌ FFmpeg error:\n<code>{e.stderr.decode()}</code>",
                parse_mode=enums.ParseMode.HTML,
                quote=True
            )
        finally:
            if os.path.exists(full_path):
                os.remove(full_path)
            for p in paths:
                if os.path.exists(p):
                    os.remove(p)

    elif query.data == "extract_audio":
        await query.answer("🎧 Exᴛʀᴀᴄᴛɪɴɢ ᴀᴜᴅɪᴏ…", show_alert=False)

        orig = query.message.reply_to_message
        if not orig or not (orig.video or orig.document):
            return await query.message.reply(
                "❌ Please reply to a video or audio-supported file.",
                quote=True
            )

        media = orig.video or orig.document

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            full_path = tmp.name
        audio_path = full_path.replace(".mp4", "_@GetTGlinks.m4a")

        try:
            await client.download_media(
                message=media,
                file_name=full_path,
                progress=progress_for_pyrogram,
                progress_args=("__Dᴏᴡɴʟᴏᴀᴅɪɴɢ…__", query.message, time.time())
            )
            await query.message.edit("Gᴇɴᴇʀᴀᴛɪɴɢ ᴀɴᴅ ᴜᴩʟᴏᴀᴅɪɴɢ ᴀᴜᴅɪᴏ")

            cmd = [
                "ffmpeg", "-i", full_path, "-vn",
                "-c:a", "aac", "-b:a", "192k", "-y", audio_path
            ]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE
            )
            _, err = await proc.communicate()
            if proc.returncode != 0:
                raise RuntimeError(err.decode() or "ffmpeg failed")

            await orig.reply_audio(
                audio=audio_path,
                caption="Exᴛʀᴀᴄᴛᴇᴅ Aᴜᴅɪᴏ",
                quote=True
            )
        except Exception as e:
            await query.message.reply(
                f"❌ FFmpeg error:\n<code>{e}</code>",
                parse_mode=enums.ParseMode.HTML,
                quote=True
            )
        finally:
            for f in (full_path, audio_path):
                if os.path.exists(f):
                    os.remove(f)



    elif query.data == "trim":
       # await query.answer()
        prompt1 = await orig.reply(
            "Tʀɪᴍ: \nNᴏᴡ ꜱᴇɴᴅ **ꜱᴛᴀʀᴛ ᴛɪᴍᴇ**: \n\nᴇɢ: `0:00:30` (ʜᴏᴜʀ:ᴍɪɴ:ꜱᴇᴄ)",
            quote=True
        )

        try:
            start_msg = await client.listen(
                chat_id=query.from_user.id,
                timeout=90
            )
        except asyncio.TimeoutError:
            await prompt1.edit("⏰ Timed-out. Trim cancelled.")
            return
        except Exception as e:
            await orig.reply(f"Error {e}")

        start_sec = parse_hms(start_msg.text)
        await orig.reply(f"Sᴛᴀʀᴛ : {start_sec}")
        if start_sec is None:
            return await start_msg.reply("Iɴᴠᴀʟɪᴅ ᴛɪᴍᴇ ꜰᴏʀᴍᴀᴛ (ᴜꜱᴇ `0:00` ʟɪᴋᴇ). Tʀɪᴍ ᴄᴀɴᴄᴇʟʟᴇᴅ.", quote=True)

        # Ask for end time
        prompt2 = await start_msg.reply(
            "Nᴏᴡ ꜱᴇɴᴅ **ᴇɴᴅ ᴛɪᴍᴇ**: \n\nᴇɢ: `1:20:30` (ʜᴏᴜʀ:ᴍɪɴ:ꜱᴇᴄ)", quote=True
        )
        try:
            end_msg = await client.listen(
                chat_id=query.from_user.id,
                timeout=90
            )
        except asyncio.TimeoutError:
            await prompt2.edit("ᴛɪᴍᴇ-ᴏᴜᴛ. ᴛʀɪᴍ ᴄᴀɴᴄᴇʟʟᴇᴅ. ᴩʟᴇᴀꜱᴇ ʀᴇꜱᴛᴀʀᴛ ᴀɢᴀɪɴ.")
            return
        id_sec = parse_hms(end_msg.text)
        if end_sec is None:
            return await end_msg.reply("❌ Invalid time format. Trim cancelled.", quote=True)

        await orig.reply(f"Eɴᴅ : {end_sec}")
        # Validation
        if end_sec <= start_sec:
            return await end_msg.reply("⚠️ End time must be greater than start time.", quote=True)
        if end_sec > duration:
            return await end_msg.reply("⚠️ End time exceeds video length.", quote=True)
        if end_sec - start_sec > 600:
            return await end_msg.reply("⚠️ Segment must be ≤ 10 minutes.", quote=True)

        # Start processing
        ack = await end_msg.reply("📥 Downloading for trim…", quote=True)
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            full_path = tmp.name
        trimmed_path = full_path.replace(".mp4", "_@GetTGlinks_trim.mp4")
        try:
            await client.download_media(
                message=media,
                file_name=full_path,
                progress=progress_for_pyrogram,
                progress_args=("__Dᴏᴡɴʟᴏᴀᴅɪɴɢ…__", ack, time.time())
            )

            # First try a fast copy
            code = await ffmpeg_trim_async(full_path, start_sec, end_sec, trimmed_path)
            if code != 0:  # fallback to re-encode
                await ffmpeg_trim_async(
                    full_path, start_sec, end_sec,
                    trimmed_path, reencode=True
                )

            await orig.reply_video(
                video=trimmed_path,
                caption=f"Tʀɪᴍᴍᴇᴅ ꜰʀᴏᴍ {start_msg.text} ᴛᴏ {end_msg.text}",
                quote=True
            )
        except Exception as e:
            await ack.edit(
                f"❌ FFmpeg error:\n<code>{e}</code>",
                parse_mode=enums.ParseMode.HTML
            )
        finally:
            for p in (full_path, trimmed_path):
                if os.path.exists(p):
                    os.remove(p)

        

    elif query.data == "hardcode":
        await query.answer("🎞 Send subtitle file…", show_alert=False)

        # 1️⃣ prompt user for subtitle
        prompt = await orig.reply(
            "📄 **Pʟᴇᴀꜱᴇ ꜱᴇɴᴅ ʏᴏᴜʀ ꜱᴜʙᴛɪᴛʟᴇ ꜰɪʟᴇ** "
            "(`.srt` or `.ass`).", quote=True
        )

        try:
            sub_msg = await client.listen(chat_id=query.from_user.id, timeout=90)
        except asyncio.TimeoutError:
            return await prompt.edit("⏰ Timed-out. Cancelled.")

        if not (sub_msg.document and sub_msg.document.file_name.lower().endswith((".srt", ".ass"))):
            return await sub_msg.reply("❌ Need a `.srt` or `.ass` file.", quote=True)

        # temp paths
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tv:
            video_path = tv.name
        with tempfile.NamedTemporaryFile(suffix=os.path.splitext(sub_msg.document.file_name)[1], delete=False) as ts:
            sub_path = ts.name
        ass_path  = sub_path                       # may be overwritten
        out_path  = video_path.replace(".mp4", "_hardcoded.mp4")

        try:
            # ⬇ download video (progress)
            prog = await query.message.reply("📥 Downloading video…", quote=True)
            await client.download_media(
                media, video_path,
                progress=progress_for_pyrogram,
                progress_args=("Video", prog, time.time())
            )
            # ⬇ download subtitle (small, no progress)
            await client.download_media(sub_msg, sub_path)

            # convert .srt → .ass if needed
            						# convert .srt → .ass if needed
            # convert .srt → .ass if needed
            if sub_path.endswith(".srt"):
                ass_path = sub_path.replace(".srt", ".ass")
                
                convert_proc = await asyncio.create_subprocess_exec(
                    "ffmpeg", "-i", sub_path, ass_path,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL
                )
                await convert_proc.communicate()

                # confirm .ass was created
                if not os.path.exists(ass_path):
                    return await query.message.reply("❌ Failed to convert .srt to .ass. Make sure subtitle is valid.")

                # prepend styling for white text / black border, center-bottom
                style = (
                    "[Script Info]\n\n[V4+ Styles]\n"
                    "Format: Name,Fontname,Fontsize,PrimaryColour,OutlineColour,"
                    "BorderStyle,Outline,Shadow,Alignment\n"
                    "Style: Default,Arial,48,&H00FFFFFF,&H00000000,1,2,0,2\n\n"
                    "[Events]\nFormat: Layer, Start, End, Style, Text\n"
                )
                with open(ass_path, "r+", encoding="utf-8") as f:
                    content = f.read()
                    f.seek(0)
                    f.write(style + content)

            # video duration for progress
            duration = getattr(media, "duration", 1) or 1

            # 🔥 burn subs + watermark
            await prog.edit("Bᴜʀɴɪɴɢ ꜱᴜʙᴛɪᴛʟᴇꜱ…")
            burn_cmd = [
                "ffmpeg", "-i", video_path,
                "-vf", (
                    f"ass={ass_path},"
                    "drawtext=text='Hard Coded By : @Videos_Sample_Bot':"
                    "fontsize=34:fontcolor=white:bordercolor=black:borderw=2:"
                    "x=20:y=(h-text_h)/2:"
                    "enable='mod(t\\,1800)<5'"
                ),
                "-c:v", "libx264", "-preset", "medium",
                "-c:a", "copy", "-y", out_path
            ]
            proc = await asyncio.create_subprocess_exec(
                *burn_cmd, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE
            )

            regex = re.compile(r"time=(\d+):(\d+):([\d.]+)")
            last = time.time()
            while True:
                ln = await proc.stderr.readline()
                if not ln:
                    break
                m = regex.search(ln.decode("utf-8", "ignore"))
                if m:
                    h, m_, s = map(float, m.groups())
                    pct = min(100, int(((h*3600+m_*60+s)/duration)*100))
                    if time.time() - last > 2:
                        try:
                            await prog.edit(f"⏳ Burning… {pct}%")
                            last = time.time()
                        except:
                            pass
            await proc.wait()

            # ⬆ upload
            await prog.edit("📤 Uploading result…")
            await orig.reply_video(
                video=out_path,
                caption="🎬 Hard-subbed + watermark",
                quote=True,
                progress=progress_for_pyrogram,
                progress_args=("Upload", prog, time.time())
            )
            await prog.delete()

        except Exception as e:
            await query.message.reply(f"❌ Error:\n<code>{e}</code>",
                                      parse_mode=enums.ParseMode.HTML, quote=True)
        finally:
            for p in (video_path, sub_path, ass_path, out_path):
                if os.path.exists(p):
                    os.remove(p)

    elif query.data == "check_subscription":
        if await ensure_member(client, query):
            await query.message.reply_text("**ᴄʟɪᴄᴋ ᴏɴ ᴩʀᴏᴄᴇꜱꜱ** ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ...!")
            await query.message.delete()
        else:
            await query.answer("ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴊᴏɪɴᴇᴅ ɪɴ ᴀʟʟ, ᴩʟᴇᴀꜱᴇ ᴊᴏɪɴ.... 🎐", show_alert=True)
    elif query.data == "checksub":
        await query.answer("🔍 Checking access…", show_alert=False)

        buttons = [
            [InlineKeyboardButton("Sᴀᴍᴩʟᴇ - 30ꜱ", callback_data="sample")],
            [InlineKeyboardButton("Gᴇɴᴇʀᴀᴛᴇ Sᴄʀᴇᴇɴꜱʜᴏᴛ", callback_data="screenshot")],
            [InlineKeyboardButton("Tʀɪᴍ", callback_data="trim")],
            [InlineKeyboardButton("Exᴛʀᴀᴄᴛ Aᴜᴅɪᴏ", callback_data="extract_audio")],
            [InlineKeyboardButton("Rᴇɴᴀᴍᴇ", url="https://t.me/MS_ReNamEr_BoT"),
             InlineKeyboardButton("Sᴛʀᴇᴀᴍ", url="https://t.me/Ms_FiLe2LINk_bOt")],
        
            [InlineKeyboardButton("Sᴜᴩᴩᴏʀᴛ", url="https://t.me/Bot_cracker")],
            [InlineKeyboardButton("Rᴇqᴜᴇꜱᴛ Mᴏʀᴇ Fᴇᴀᴛᴜʀᴇꜱ", url="https://t.me/syd_xyz")]
        ]


        await query.message.reply(
            "Cʜᴏᴏꜱᴇ ᴀɴ ᴀᴄᴛɪᴏɴ ʙᴇʟᴏᴡ:",
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )
