
import os
from random import randint
from typing import Union

from pyrogram.types import InlineKeyboardMarkup

import config
from kkvideobot import Carbon, Spotify, YouTube, app
from kkvideobot.core.call import Yukki
from kkvideobot.misc import db
from kkvideobot.utils.database import (add_active_chat,
                                       add_active_video_chat,
                                       is_active_chat,
                                       is_video_allowed, music_on)
from kkvideobot.utils.exceptions import AssistantErr
from kkvideobot.utils.inline.play import (stream_markup,
                                          telegram_markup)
from kkvideobot.utils.inline.playlist import close_markup
from kkvideobot.utils.pastebin import Yukkibin
from kkvideobot.utils.stream.queue import put_queue, put_queue_index
from kkvideobot.utils.thumbnails import gen_thumb


async def stream(
    _,
    mystic,
    user_id,
    result,
    chat_id,
    user_name,
    original_chat_id,
    video: Union[bool, str] = None,
    streamtype: Union[bool, str] = None,
    spotify: Union[bool, str] = None,
):
    if video:
        if not await is_video_allowed(chat_id):
            raise AssistantErr(_["play_6"])
    if streamtype == "playlist":
        msg = f"{_['playlist_16']}\n\n"
        count = 0
        for search in result:
            if int(count) == config.PLAYLIST_FETCH_LIMIT:
                continue
            if spotify:
                search = await Spotify.trackplaylist(search)
                (
                    title,
                    duration_min,
                    duration_sec,
                    thumbnail,
                    vidid,
                ) = await YouTube.details(search)
            else:
                (
                    title,
                    duration_min,
                    duration_sec,
                    thumbnail,
                    vidid,
                ) = await YouTube.details(search, True)
            if str(duration_min) == "None":
                continue
            if duration_sec > config.DURATION_LIMIT:
                continue
            if await is_active_chat(chat_id):
                await put_queue(
                    chat_id,
                    original_chat_id,
                    f"vid_{vidid}",
                    title,
                    duration_min,
                    user_name,
                    vidid,
                    user_id,
                    
                )
                position = len(db.get(chat_id)) - 1
                count += 1
                msg += f"{count}- {title[:70]}\n"
                msg += f"{_['playlist_17']} {position}\n\n"
            else:
                db[chat_id] = []
                status = True if video else None
                try:
                    file_path, direct = await YouTube.download(
                        vidid, mystic, video=status, videoid=True
                    )
                except:
                    raise AssistantErr(_["play_16"])
                await Yukki.join_call(
                    chat_id, original_chat_id, file_path, video=status
                )
                await add_active_chat(chat_id)
                await music_on(chat_id)
                await put_queue(
                    chat_id,
                    original_chat_id,
                    file_path if direct else f"vid_{vidid}",
                    title,
                    duration_min,
                    user_name,
                    vidid,
                    user_id,
                    "video" if video else "audio",
                )
                if video:
                    await add_active_video_chat(chat_id)
                
        if count == 0:
            return
        else:
            link = await Yukkibin(msg)
            lines = msg.count("\n")
            if lines >= 17:
                car = os.linesep.join(msg.split(os.linesep)[:17])
            else:
                car = msg
            carbon = await Carbon.generate(
                car, randint(100, 10000000)
            )
            upl = close_markup(_)
            return await app.send_photo(
                original_chat_id,
                photo=carbon,
                caption=_["playlist_18"].format(link, position),
                reply_markup=upl,
            )
    elif streamtype == "youtube":
        link = result["link"]
        vidid = result["vidid"]
        title = (result["title"]).title()
        duration_min = result["duration_min"]
        status = True if video else None
        try:
            file_path, direct = await YouTube.download(
                vidid, mystic, videoid=True, video=status
            )
        except:
            raise AssistantErr(_["play_16"])
        if await is_active_chat(chat_id):
            await put_queue(
                chat_id,
                original_chat_id,
                file_path if direct else f"vid_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                
            )
            position = len(db.get(chat_id)) - 1
            await app.send_message(
                original_chat_id,
                _["queue_4"].format(
                    position, title[:30], duration_min, user_name
                ),
            )
        else:
            db[chat_id] = []
            await Yukki.join_call(
                chat_id, original_chat_id, file_path, video=status
            )
            await add_active_chat(chat_id)
            await put_queue(
                chat_id,
                original_chat_id,
                file_path if direct else f"vid_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                
            )
            if video:
                await add_active_video_chat(chat_id)
            await music_on(chat_id)
            
    elif streamtype == "telegram":
        file_path = result["path"]
        link = result["link"]
        title = (result["title"]).title()
        duration_min = result["dur"]
        status = True if video else None
        if await is_active_chat(chat_id):
            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                streamtype,
                user_id,
                
            )
            position = len(db.get(chat_id)) - 1
            await app.send_message(
                original_chat_id,
                _["queue_4"].format(
                    position, title[:30], duration_min, user_name
                ),
            )
        else:
            db[chat_id] = []
            await Yukki.join_call(
                chat_id, original_chat_id, file_path, video=status
            )
            await add_active_chat(chat_id)
            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                streamtype,
                user_id,
                
            )
            if video:
                await add_active_video_chat(chat_id)
            await music_on(chat_id)
            
    elif streamtype == "live":
        link = result["link"]
        vidid = result["vidid"]
        title = (result["title"]).title()
        duration_min = "Live Track"
        status = True if video else None
        if await is_active_chat(chat_id):
            await put_queue(
                chat_id,
                original_chat_id,
                f"live_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                
            )
            position = len(db.get(chat_id)) - 1
        else:
            db[chat_id] = []
            n, file_path = await YouTube.video(link)
            if n == 0:
                raise AssistantErr(_["str_3"])
            await Yukki.join_call(
                chat_id, original_chat_id, file_path, video=status
            )
            await add_active_chat(chat_id)
            await put_queue(
                chat_id,
                original_chat_id,
                f"live_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                
            )
            if video:
                await add_active_video_chat(chat_id)
            await music_on(chat_id)
            
    elif streamtype == "index":
        link = result
        title = "Index or M3u8 Link"
        duration_min = "URL stream"
        if await is_active_chat(chat_id):
            await put_queue_index(
                chat_id,
                original_chat_id,
                "index_url",
                title,
                duration_min,
                user_name,
                link,
                "video",
            )
            position = len(db.get(chat_id)) - 1
            await mystic.edit_text(
                _["queue_4"].format(
                    position, title[:30], duration_min, user_name
                )
            )
        else:
            db[chat_id] = []
            await Yukki.join_call(
                chat_id, original_chat_id, link, video=True
            )
            await add_active_chat(chat_id)
            await put_queue_index(
                chat_id,
                original_chat_id,
                "index_url",
                title,
                duration_min,
                user_name,
                link,
                "video",
            )
            await add_active_video_chat(chat_id)
            await music_on(chat_id)
            await mystic.delete()
