# Copyright (C) 2020 Adek Maulana.
# All rights reserved.
"""
  **Heroku manager for your userbot**
      Syntax :
      
    .usage
    Usage: Check your heroku dyno hours remaining
    
    .set var <NEW VAR> <VALUE>
    Usage: add new variable or update existing value variable
    !!! WARNING !!!, after setting a variable the bot will restarted
    
    .get var or .get var <VAR>
    Usage: get your existing varibles, use it only on your private group!
    This returns all of your private information, please be caution...
    
    .del var <VAR>
    Usage: delete existing variable
    !!! WARNING !!!, after deleting variable the bot will restarted
"""


import heroku3
import asyncio
import os
import requests
import math
import asyncio
from asyncio import sleep
import datetime
import shutil 
import random, re
from random import choice, randint
import time
from time import gmtime, strftime
from datetime import timedelta
from datetime import datetime
from telethon import events
from telethon.tl import functions, types
from uniborg.util import progress, is_read, humanbytes, time_formatter, admin_cmd
from uniborg.prettyjson import prettyjson
from platform import python_version, uname
from sample_config import Config
from uniborg.util import admin_cmd

# ================= CONSTANT =================
Heroku = heroku3.from_key(Config.HEROKU_API_KEY)
heroku_api = "https://api.heroku.com"
HEROKU_APP_NAME = Config.HEROKU_APP_NAME
HEROKU_API_KEY = Config.HEROKU_API_KEY
DEFAULTUSER = Config.ALIVE_NAME if Config.ALIVE_NAME else uname().node
# ================= CONSTANT =================

#@register(outgoing=True, pattern=r"^.(set|get|del) var(?: |$)(.*)(?: |$)")
@borg.on(admin_cmd(pattern=r"^.(set|get|del) var ?(.*)", outgoing=True))
#@register(outgoing=True, pattern=r"^.(set|get|del) var(?: |$)(.*)")
async def variable(var):
    """
        Manage most of ConfigVars setting, set new var, get current var,
        or delete var...
    """
    if HEROKU_APP_NAME is not None:
        app = Heroku.app(HEROKU_APP_NAME)
    else:
        return await var.edit("`[HEROKU]:"
                              "\nPlease setup your` **HEROKU_APP_NAME**")
    exe = var.pattern_match.group(1)
    heroku_var = app.config()
    if exe == "get":
        await var.edit("`Getting information...`")
        await asyncio.sleep(1.5)
        try:
            val = var.pattern_match.group(2).split()[0]
            if val in heroku_var:
                return await var.edit("**Config vars**:"
                                      f"\n\n`{val} = {heroku_var[val]}`\n")
            else:
                return await var.edit("**Config vars**:"
                                      f"\n\n`Error -> {val} not exists`")
        except IndexError:
            configs = prettyjson(heroku_var.to_dict(), indent=2)
            with open("configs.json", "w") as fp:
                fp.write(configs)
            with open("configs.json", "r") as fp:
                result = fp.read()
                if len(result) >= 4096:
                    await var.client.send_file(
                        var.chat_id,
                        "configs.json",
                        reply_to=var.id,
                        caption="`Output too large, sending it as a file`",
                    )
                else:
                    await var.edit("`[HEROKU]` variables:\n\n"
                                   "================================"
                                   f"\n```{result}```\n"
                                   "================================"
                                   )
            os.remove("configs.json")
            return
    elif exe == "set":
        await var.edit("`Setting information...`")
        val = var.pattern_match.group(2).split()
        try:
            val[1]
        except IndexError:
            return await var.edit("`.set var <config name> <value>`")
        await asyncio.sleep(1.5)
        if val[0] in heroku_var:
            await var.edit(f"**{val[0]}**  `successfully changed to`  **{val[1]}**")
        else:
            await var.edit(f"**{val[0]}**  `successfully added with value: **{val[1]}**")
        heroku_var[val[0]] = val[1]
    elif exe == "del":
        await var.edit("`Getting information to deleting vars...`")
        try:
            val = var.pattern_match.group(2).split()[0]
        except IndexError:
            return await var.edit("`Please specify config vars you want to delete`")
        await asyncio.sleep(1.5)
        if val in heroku_var:
            await var.edit(f"**{val}**  `successfully deleted`")
            del heroku_var[val]
        else:
            return await var.edit(f"**{val}**  `is not exists`")


#@register(outgoing=True, pattern=r"^.usage(?: |$)")
#@register(outgoing=True, pattern=r"^.usage(?: |$)(.*)")
@borg.on(events.NewMessage(pattern=r"\.usage ?(.*)", outgoing=True))  # pylint:disable=E0602
async def _(event):
#async def dyno_usage(dyno):
    """
        Get your account Dyno Usage
    """
    await event.edit("`Processing...`")
    useragent = ('Mozilla/5.0 (Linux; Android 10; SM-G975F) '
                 'AppleWebKit/537.36 (KHTML, like Gecko) '
                 'Chrome/80.0.3987.149 Mobile Safari/537.36'
                 )
    u_id = Heroku.account().id
    headers = {
     'User-Agent': useragent,
     'Authorization': f'Bearer {HEROKU_API_KEY}',
     'Accept': 'application/vnd.heroku+json; version=3.account-quotas',
    }
    path = "/accounts/" + u_id + "/actions/get-quota"
    r = requests.get(heroku_api + path, headers=headers)
    if r.status_code != 200:
        return await event.edit("`Error: something bad happened`\n\n"
                               f">.`{r.reason}`\n")
    result = r.json()
    quota = result['account_quota']
    quota_used = result['quota_used']

    """ - Used - """
    remaining_quota = quota - quota_used
    percentage = math.floor(remaining_quota / quota * 100)
    minutes_remaining = remaining_quota / 60
    hours = math.floor(minutes_remaining / 60)
    minutes = math.floor(minutes_remaining % 60)

    """ - Current - """
    App = result['apps']
    try:
        App[0]['quota_used']
    except IndexError:
        AppQuotaUsed = 0
        AppPercentage = 0
    else:
        AppQuotaUsed = App[0]['quota_used'] / 60
        AppPercentage = math.floor(App[0]['quota_used'] * 100 / quota)
    AppHours = math.floor(AppQuotaUsed / 60)
    AppMinutes = math.floor(AppQuotaUsed % 60)

    await asyncio.sleep(1.5)

    return await event.edit("**Dyno Usage**:\n\n"
                           f" -> `Dyno usage for`  **[{DEFAULTUSER}]({HEROKU_APP_NAME})**:\n"
                           f"     ???  `{AppHours}`**h**  `{AppMinutes}`**m**  "
                           f"**|**  [`{AppPercentage}`**%**]"
                           "\n"
                           " -> `Dyno hours quota remaining this month`:\n"
                           f"     ???  `{hours}`**h**  `{minutes}`**m**  "
                           f"**|**  [`{percentage}`**%**]"
                           )


