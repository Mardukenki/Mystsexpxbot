"""cmd .lol"""

from telethon import events
from uniborg.util import admin_cmd


@borg.on(admin_cmd(pattern="lol"))
async def _(event):
    if event.fwd_from:
        return
    await event.edit("š\nš\nš\nš\nšššš\n\n   ššš\n š         š\nš           š\n š         š\n   ššš\n\nš\nš\nš\nš\nšššš")
