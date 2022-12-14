
from pyrogram import filters
from pyrogram.types import Message

from config import BANNED_USERS
from strings import get_command
from kkvideobot import app
from kkvideobot.utils.database.memorydatabase import (get_loop,
                                                      set_loop)
from kkvideobot.utils.decorators import AdminRightsCheck

# Commands
LOOP_COMMAND = get_command("LOOP_COMMAND")


@app.on_message(
    filters.command(LOOP_COMMAND) & filters.group & ~BANNED_USERS
)
@AdminRightsCheck
async def admins(cli, message: Message, _, mystic, chat_id):
    usage = _["admin_24"]
    if len(message.command) != 2:
        return await mystic.edit_text(usage)
    state = message.text.split(None, 1)[1].strip()
    if state.isnumeric():
        state = int(state)
        if 1 <= state <= 10:
            got = await get_loop(chat_id)
            if got != 0:
                state = got + state
            if int(state) > 10:
                state = 10
            await set_loop(chat_id, state)
            return await mystic.edit_text(
                _["admin_25"].format(
                    message.from_user.first_name, state
                )
            )
        else:
            return await mystic.edit_text(_["admin_26"])
    elif state.lower() == "enable":
        await set_loop(chat_id, 10)
        return await mystic.edit_text(
            _["admin_25"].format(message.from_user.first_name, state)
        )
    elif state.lower() == "disable":
        await set_loop(chat_id, 0)
        return await mystic.edit_text(_["admin_27"])
    else:
        return await mystic.edit_text(usage)
