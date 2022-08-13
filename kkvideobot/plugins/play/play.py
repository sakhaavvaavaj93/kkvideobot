
import random
import string

from pyrogram import filters
from pyrogram.types import (InlineKeyboardMarkup, InputMediaPhoto,
                            Message)

from config import (BANNED_USERS, DURATION_LIMIT, DURATION_LIMIT_MIN,
                    PLAYLIST_FETCH_LIMIT, PLAYLIST_IMG_URL, lyrical)
from strings import get_command
from kkvideobot import (Apple, Resso, SoundCloud, Spotify, Telegram,
                        YouTube, app)
from kkvideobot.utils import seconds_to_min, time_to_seconds
from kkvideobot.utils.database import (get_chatmode, get_cmode,
                                       is_video_allowed)
from kkvideobot.utils.decorators.language import languageCB
from kkvideobot.utils.decorators.play import PlayWrapper
from kkvideobot.utils.formatters import formats
from kkvideobot.utils.inline.play import (livestream_markup,
                                          playlist_markup,
                                          slider_markup, track_markup)
from kkvideobot.utils.inline.playlist import botplaylist_markup
from kkvideobot.utils.logger import play_logs
from kkvideobot.utils.stream.stream import stream

# Command
PLAY_COMMAND = get_command("PLAY_COMMAND")


@app.on_message(
    filters.command(PLAY_COMMAND) & filters.group & ~BANNED_USERS
)
@PlayWrapper
async def play_commnd(
    client,
    message: Message,
    _,
    chat_id,
    video,
    channel,
    playmode,
    mystic,
    url,
):
    plist_id = None
    slider = None
    plist_type = None
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    audio_telegram = (
        (
            message.reply_to_message.audio
            or message.reply_to_message.voice
        )
        if message.reply_to_message
        else None
    )
    video_telegram = (
        (
            message.reply_to_message.video
            or message.reply_to_message.document
        )
        if message.reply_to_message
        else None
    )
    if audio_telegram:
        if audio_telegram.file_size > 104857600:
            return await mystic.edit_text(_["play_5"])
        duration_min = seconds_to_min(audio_telegram.duration)
        if (audio_telegram.duration) > DURATION_LIMIT:
            return await mystic.edit_text(
                _["play_6"].format(DURATION_LIMIT_MIN, duration_min)
            )
        file_path = await Telegram.get_filepath(audio=audio_telegram)
        if await Telegram.download(_, message, mystic, file_path):
            message_link = await Telegram.get_link(message)
            file_name = await Telegram.get_filename(
                audio_telegram, audio=True
            )
            dur = await Telegram.get_duration(audio_telegram)
            details = {
                "title": file_name,
                "link": message_link,
                "path": file_path,
                "dur": dur,
            }

            try:
                await stream(
                    _,
                    mystic,
                    user_id,
                    details,
                    chat_id,
                    user_name,
                    message.chat.id,
                    streamtype="telegram",
                )
            except Exception as e:
                ex_type = type(e).__name__
                err = (
                    e
                    if ex_type == "AssistantErr"
                    else _["general_3"].format(ex_type)
                )
                return await mystic.edit_text(err)
            return await mystic.delete()
        else:
            return await mystic.edit_text(_["tg_2"])
    elif video_telegram:
        if not await is_video_allowed(message.chat.id):
            return await mystic.edit_text(_["play_3"])
        if message.reply_to_message.document:
            ext = video_telegram.file_name.split(".")[-1]
            if ext.lower() not in formats:
                return await mystic.edit_text(
                    _["play_8"].format(f"{' | '.join(formats)}")
                )
        if video_telegram.file_size > 1073741824:
            return await mystic.edit_text(_["play_9"])
        file_path = await Telegram.get_filepath(video=video_telegram)
        if await Telegram.download(_, message, mystic, file_path):
            message_link = await Telegram.get_link(message)
            file_name = await Telegram.get_filename(video_telegram)
            dur = await Telegram.get_duration(video_telegram)
            details = {
                "title": file_name,
                "link": message_link,
                "path": file_path,
                "dur": dur,
            }
            try:
                await stream(
                    _,
                    mystic,
                    user_id,
                    details,
                    chat_id,
                    user_name,
                    message.chat.id,
                    video=True,
                    streamtype="telegram",
                )
            except Exception as e:
                ex_type = type(e).__name__
                err = (
                    e
                    if ex_type == "AssistantErr"
                    else _["general_3"].format(ex_type)
                )
                return await mystic.edit_text(err)
            return await mystic.delete()
        else:
            return await mystic.edit_text(_["tg_2"])
    elif url:
        if await YouTube.exists(url):
            if "playlist" in url:
                try:
                    details = await YouTube.playlist(
                        url,
                        PLAYLIST_FETCH_LIMIT,
                        message.from_user.id,
                    )
                except Exception:
                    return await mystic.edit_text(_["play_3"])
                streamtype = "playlist"
                plist_type = "yt"
                plist_id = url.split("=")[1]
                img = PLAYLIST_IMG_URL
                cap = _["play_10"]
            else:
                try:
                    details, track_id = await YouTube.track(url)
                except:
                    return await mystic.edit_text(_["play_3"])
                streamtype = "youtube"
                img = details["thumb"]
                cap = _["play_11"].format(
                    details["title"],
                    details["duration_min"],
                )
        elif await Spotify.valid(url):
            if "track" in url:
                try:
                    details, track_id = await Spotify.track(url)
                except Exception:
                    return await mystic.edit_text(_["play_3"])
                streamtype = "youtube"
                img = details["thumb"]
                cap = _["play_11"].format(
                    details["title"], details["duration_min"]
                )
            elif "playlist" in url:
                try:
                    details, plist_id, thumb = await Spotify.playlist(
                        url
                    )
                except Exception:
                    return await mystic.edit_text(_["play_3"])
                streamtype = "playlist"
                plist_type = "spotify"
                img = thumb
                cap = _["play_12"].format(
                    message.from_user.first_name
                )
        elif await Apple.valid(url):
            if "album" in url:
                try:
                    details, track_id = await Apple.track(url)
                except Exception:
                    return await mystic.edit_text(_["play_3"])
                streamtype = "youtube"
                img = details["thumb"]
                cap = _["play_11"].format(
                    details["title"], details["duration_min"]
                )
            elif "playlist" in url:
                try:
                    details, plist_id = await Apple.playlist(url)
                except Exception:
                    return await mystic.edit_text(_["play_3"])
                streamtype = "playlist"
                plist_type = "apple"
                cap = _["play_13"].format(
                    message.from_user.first_name
                )
                img = url
        elif await Resso.valid(url):
            try:
                details, track_id = await Resso.track(url)
            except Exception as e:
                print(e)
                return await mystic.edit_text(_["play_3"])
            streamtype = "youtube"
            img = details["thumb"]
            cap = _["play_11"].format(
                details["title"], details["duration_min"]
            )
        elif await SoundCloud.valid(url):
            try:
                details, track_path = await SoundCloud.download(url)
            except Exception:
                return await mystic.edit_text(_["play_3"])
            duration_sec = details["duration_sec"]
            if duration_sec > DURATION_LIMIT:
                return await mystic.edit_text(
                    _["play_6"].format(
                        DURATION_LIMIT_MIN, details["duration_min"]
                    )
                )
            try:
                await stream(
                    _,
                    mystic,
                    user_id,
                    details,
                    chat_id,
                    user_name,
                    message.chat.id,
                    streamtype="soundcloud",
                )
            except Exception as e:
                ex_type = type(e).__name__
                err = (
                    e
                    if ex_type == "AssistantErr"
                    else _["general_3"].format(ex_type)
                )
                return await mystic.edit_text(err)
            return await mystic.delete()
        else:
            return await mystic.edit_text(_["play_14"])
    else:
        if len(message.command) < 2:
            buttons = botplaylist_markup(_)
            return await mystic.edit_text(
                _["playlist_1"],
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        slider = True
        query = message.text.split(None, 1)[1]
        if "-v" in query:
            query = query.replace("-v", "")
        try:
            details, track_id = await YouTube.track(query)
        except Exception:
            return await mystic.edit_text(_["play_3"])
        streamtype = "youtube"
    if str(playmode) == "Direct":
        if not plist_type:
            if details["duration_min"]:
                duration_sec = time_to_seconds(
                    details["duration_min"]
                )
                if duration_sec > DURATION_LIMIT:
                    return await mystic.edit_text(
                        _["play_6"].format(
                            DURATION_LIMIT_MIN,
                            details["duration_min"],
                        )
                    )
            else:
                buttons = livestream_markup(
                    _, track_id, user_id, "v" if video else "a"
                )
                return await mystic.edit_text(
                    _["play_15"],
                    reply_markup=InlineKeyboardMarkup(buttons),
                )
        try:
            await stream(
                _,
                mystic,
                user_id,
                details,
                chat_id,
                user_name,
                message.chat.id,
                video=video,
                streamtype=streamtype,
                spotify=True if plist_type == "spotify" else False,
            )
        except Exception as e:
            ex_type = type(e).__name__
            err = (
                e
                if ex_type == "AssistantErr"
                else _["general_3"].format(ex_type)
            )
            return await mystic.edit_text(err)
        await mystic.delete()
        return await play_logs(message, streamtype=streamtype)
    else:
        if plist_type:
            ran_hash = "".join(
                random.choices(
                    string.ascii_uppercase + string.digits, k=10
                )
            )
            lyrical[ran_hash] = plist_id
            buttons = playlist_markup(
                _, ran_hash, message.from_user.id, plist_type
            )
            await mystic.delete()
            return await play_logs(
                message, streamtype=f"Playlist : {plist_type}"
            )
        else:
            if slider:
                buttons = slider_markup(
                    _, track_id, message.from_user.id, query, 0
                )
                await mystic.delete()
                await message.reply_photo(
                    photo=details["thumb"],
                    caption=_["play_11"].format(
                        details["title"].title(),
                        details["duration_min"],
                    ),
                    reply_markup=InlineKeyboardMarkup(buttons),
                )
                return await play_logs(
                    message, streamtype=f"Searched on Youtube"
                )
            else:
                buttons = track_markup(
                    _, track_id, message.from_user.id
                )
                await mystic.delete()
                return await play_logs(
                    message, streamtype=f"URL Searched Inline"
                )

@app.on_callback_query(
    filters.regex("AnonymousAdmin") & ~BANNED_USERS
)
async def anonymous_check(client, CallbackQuery):
    try:
        await CallbackQuery.answer(
            "You're an Anonymous Admin\n\nGo to your group's setting \n-> Administrators List \n-> Click on your name \n-> uncheck REMAIN ANONYMOUS button there.",
            show_alert=True,
        )
    except:
        return

