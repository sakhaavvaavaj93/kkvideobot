
import random

from pyrogram import filters
from pyrogram.types import Message

from config import BANNED_USERS
from strings import get_command
from kkvideobot import app
from kkvideobot.misc import db
from kkvideobot.utils.decorators import AdminRightsCheck

# Commands
SHUFFLE_COMMAND = get_command("SHUFFLE_COMMAND")


@app.on_message(
    filters.command(SHUFFLE_COMMAND) & filters.group & ~BANNED_USERS
)
@AdminRightsCheck
async def admins(Client, message: Message, _, mystic, chat_id):
    if not len(message.command) == 1:
        return await mystic.edit_text(_["general_2"])
    check = db.get(chat_id)
    if not check:
        return await mystic.edit_text(_["admin_21"])
    print(len(check))
    try:
        popped = check.pop(0)
    except:
        return await mystic.edit_text(_["admin_22"])
    check = db.get(chat_id)
    if not check:
        check.insert(0, popped)
        return await mystic.edit_text(_["admin_22"])
    random.shuffle(check)
    check.insert(0, popped)
    await mystic.edit_text(
        _["admin_23"].format(message.from_user.first_name)
    )
