# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot help command """

from userbot import CMD_HELP
from userbot.events import register


@register(outgoing=True, pattern="^.h(?: |$)(.*)")
async def help(event):
    """ For .help command,"""
    args = event.pattern_match.group(1).lower()
    if args:
        if args in CMD_HELP:
            await event.edit(str(CMD_HELP[args]))
        else:
            await event.edit("Invalid CMD...!!! Are u Blind ???")
    else:
        await event.edit(".h <module name> for Detail or .<module> Retrieves All Available CMD.")
        string = ""
        for i in CMD_HELP:
            string += ""
            string += " ⊙ "
        await event.reply(string)
