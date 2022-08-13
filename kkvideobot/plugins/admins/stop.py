
from pyrogram import filters
from pyrogram.types import Message

from config import BANNED_USERS
from strings import get_command
from kkvideobot import app
from kkvideobot.core.call import Yukki
from kkvideobot.utils.decorators import AdminRightsCheck

# Commands
STOP_COMMAND = get_command("STOP_COMMAND")


@app.on_message(
    filters.command(STOP_COMMAND) & filters.group & ~BANNED_USERS
)
@AdminRightsCheck
async def stop_music(cli, message: Message, _, mystic, chat_id):
    if not len(message.command) == 1:
        return await mystic.edit_text(_["general_2"])
    await Yukki.stop_stream(chat_id)
    await mystic.edit_text(
        _["admin_9"].format(message.from_user.mention)
    )
