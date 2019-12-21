# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for keeping control who PM you. """

from telethon.tl.functions.contacts import BlockRequest, UnblockRequest
from telethon.tl.functions.messages import ReportSpamRequest
from telethon.tl.types import User
from sqlalchemy.exc import IntegrityError

from userbot import (COUNT_PM, CMD_HELP, BOTLOG, BOTLOG_CHATID, PM_AUTO_BAN,
                     LASTMSG, LOGS)

from userbot.events import register

# ========================= CONSTANTS ============================
UNAPPROVED_MSG = (
    "𝐇𝐨𝐥𝐥𝐚...!\n\nThis is an automated message.\n"
    "I haven't approved you to PM yet.\n"
    "Please wait for me to approve your PM.\n"
    "Until then, please 𝐃𝐎𝐍'𝐓 send any messages to me.\nYou'll get 𝐁𝐋𝐎𝐂𝐊𝐄𝐃 and 𝐑𝐄𝐏𝐎𝐑𝐓𝐄𝐃 if you do so!")
# =================================================================


@register(incoming=True, disable_edited=True, disable_errors=True)
async def permitpm(event):
    """ Prohibits people from PMing you without approval. \
        Will block retarded nibbas automatically. """
    if PM_AUTO_BAN:
        self_user = await event.client.get_me()
        if event.is_private and event.chat_id != 777000 and event.chat_id != self_user.id and not (
                await event.get_sender()).bot:
            try:
                from userbot.modules.sql_helper.pm_permit_sql import is_approved
                from userbot.modules.sql_helper.globals import gvarstatus
            except AttributeError:
                return
            apprv = is_approved(event.chat_id)
            notifsoff = gvarstatus("NOTIF_OFF")

            # This part basically is a sanity check
            # If the message that sent before is Unapproved Message
            # then stop sending it again to prevent FloodHit
            if not apprv and event.text != UNAPPROVED_MSG:
                if event.chat_id in LASTMSG:
                    prevmsg = LASTMSG[event.chat_id]
                    # If the message doesn't same as previous one
                    # Send the Unapproved Message again
                    if event.text != prevmsg:
                        async for message in event.client.iter_messages(
                                event.chat_id,
                                from_user='me',
                                search=UNAPPROVED_MSG):
                            await message.delete()
                        await event.reply(UNAPPROVED_MSG)
                    LASTMSG.update({event.chat_id: event.text})
                else:
                    await event.reply(UNAPPROVED_MSG)
                    LASTMSG.update({event.chat_id: event.text})

                if notifsoff:
                    await event.client.send_read_acknowledge(event.chat_id)
                if event.chat_id not in COUNT_PM:
                    COUNT_PM.update({event.chat_id: 1})
                else:
                    COUNT_PM[event.chat_id] = COUNT_PM[event.chat_id] + 1

                if COUNT_PM[event.chat_id] > 4:
                    await event.respond(
                        "You were 𝐒𝐏𝐀𝐌𝐌𝐄𝐑, which I didn't like.\n"
                        "You have been 𝐁𝐋𝐎𝐂𝐊𝐄𝐃 and 𝐑𝐄𝐏𝐎𝐑𝐓𝐄𝐃 as 𝐒𝐏𝐀𝐌.\n𝐇𝐀𝐕𝐄 𝐀 𝐍𝐈𝐂𝐄 𝐃𝐀𝐘."
                    )

                    try:
                        del COUNT_PM[event.chat_id]
                        del LASTMSG[event.chat_id]
                    except KeyError:
                        if BOTLOG:
                            await event.client.send_message(
                                BOTLOG_CHATID,
                                "Count PM is seemingly going retard, plis restart bot!",
                            )
                        LOGS.info("CountPM wen't rarted boi")
                        return

                    await event.client(BlockRequest(event.chat_id))
                    await event.client(ReportSpamRequest(peer=event.chat_id))

                    if BOTLOG:
                        name = await event.client.get_entity(event.chat_id)
                        name0 = str(name.first_name)
                        await event.client.send_message(
                            BOTLOG_CHATID,
                            "[" + name0 + "](tg://user?id=" +
                            str(event.chat_id) + ")" +
                            " was just another 𝐑𝐄𝐓𝐀𝐑𝐓𝐄𝐃.",
                        )


@register(disable_edited=True, outgoing=True, disable_errors=True)
async def auto_accept(event):
    """ Will approve automatically if you texted them first. """
    if not PM_AUTO_BAN:
        return
    self_user = await event.client.get_me()
    if event.is_private and event.chat_id != 777000 and event.chat_id != self_user.id and not (
            await event.get_sender()).bot:
        try:
            from userbot.modules.sql_helper.pm_permit_sql import is_approved
            from userbot.modules.sql_helper.pm_permit_sql import approve
        except AttributeError:
            return

        chat = await event.get_chat()
        if isinstance(chat, User):
            if is_approved(event.chat_id) or chat.bot:
                return
            async for message in event.client.iter_messages(event.chat_id,
                                                            reverse=True,
                                                            limit=1):
                if message.message is not UNAPPROVED_MSG and message.from_id == self_user.id:
                    try:
                        approve(event.chat_id)
                    except IntegrityError:
                        return

                if is_approved(event.chat_id) and BOTLOG:
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        "#AUTO-APPROVED\n" + "User: " +
                        f"[{chat.first_name}](tg://user?id={chat.id})",
                    )


@register(outgoing=True, pattern="^.ntfoooooooooooo$")
async def notifoff(noff_event):
    """ For .notifoff command, stop getting notifications from unapproved PMs. """
    try:
        from userbot.modules.sql_helper.globals import addgvar
    except AttributeError:
        await noff_event.edit("Running on Non-SQL mode!")
        return
    addgvar("NOTIF_OFF", True)
    await noff_event.edit("Notifications from unapproved PM's are silenced!")


@register(outgoing=True, pattern="^.ntooooooooo$")
async def notifon(non_event):
    """ For .notifoff command, get notifications from unapproved PMs. """
    try:
        from userbot.modules.sql_helper.globals import delgvar
    except AttributeError:
        await non_event.edit("Running on Non-SQL mode!")
        return
    delgvar("NOTIF_OFF")
    await non_event.edit("Notifications from unapproved PM's unmuted!")


@register(outgoing=True, pattern="^.app$")
async def approvepm(apprvpm):
    """ For .approve command, give someone the permissions to PM you. """
    try:
        from userbot.modules.sql_helper.pm_permit_sql import approve
    except AttributeError:
        await apprvpm.edit("Non-SQL mode ON")
        return

    if apprvpm.reply_to_msg_id:
        reply = await apprvpm.get_reply_message()
        replied_user = await apprvpm.client.get_entity(reply.from_id)
        aname = replied_user.id
        name0 = str(replied_user.first_name)
        uid = replied_user.id

    else:
        aname = await apprvpm.client.get_entity(apprvpm.chat_id)
        name0 = str(aname.first_name)
        uid = apprvpm.chat_id

    try:
        approve(uid)
    except IntegrityError:
        await apprvpm.edit("User already 𝐀𝐏𝐏𝐑𝐎𝐕𝐄𝐃.")
        return

    await apprvpm.edit(f"[{name0}](tg://user?id={uid}) 𝐀𝐏𝐏𝐑𝐎𝐕𝐄𝐃 to PM!")

    async for message in apprvpm.client.iter_messages(apprvpm.chat_id,
                                                      from_user='me',
                                                      search=UNAPPROVED_MSG):
        await message.delete()

    if BOTLOG:
        await apprvpm.client.send_message(
            BOTLOG_CHATID,
            "#APPROVED\n" + "User: " + f"[{name0}](tg://user?id={uid})",
        )


@register(outgoing=True, pattern="^.dap$")
async def disapprovepm(disapprvpm):
    try:
        from userbot.modules.sql_helper.pm_permit_sql import dissprove
    except BaseException:
        await disapprvpm.edit("Non-SQL mode ON")
        return

    if disapprvpm.reply_to_msg_id:
        reply = await disapprvpm.get_reply_message()
        replied_user = await disapprvpm.client.get_entity(reply.from_id)
        aname = replied_user.id
        name0 = str(replied_user.first_name)
        dissprove(replied_user.id)
    else:
        dissprove(disapprvpm.chat_id)
        aname = await disapprvpm.client.get_entity(disapprvpm.chat_id)
        name0 = str(aname.first_name)

    await disapprvpm.edit(
        f"[{name0}](tg://user?id={disapprvpm.chat_id}) 𝐃𝐈𝐒𝐀𝐏𝐏𝐑𝐎𝐕𝐄𝐃 to PM!")

    if BOTLOG:
        await disapprvpm.client.send_message(
            BOTLOG_CHATID,
            f"[{name0}](tg://user?id={disapprvpm.chat_id})"
            " was 𝐃𝐈𝐒𝐀𝐏𝐏𝐑𝐎𝐕𝐄𝐃 to PM.",
        )


@register(outgoing=True, pattern="^.bl$")
async def blockpm(block):
    """ For .block command, block people from PMing you! """
    if block.reply_to_msg_id:
        reply = await block.get_reply_message()
        replied_user = await block.client.get_entity(reply.from_id)
        aname = replied_user.id
        name0 = str(replied_user.first_name)
        await block.client(BlockRequest(replied_user.id))
        await block.edit("You've been 𝐁𝐋𝐎𝐂𝐊𝐄𝐃!")
        uid = replied_user.id
    else:
        await block.client(BlockRequest(block.chat_id))
        aname = await block.client.get_entity(block.chat_id)
        await block.edit("You've been 𝐁𝐋𝐎𝐂𝐊𝐄𝐃!")
        name0 = str(aname.first_name)
        uid = block.chat_id

    try:
        from userbot.modules.sql_helper.pm_permit_sql import dissprove
        dissprove(uid)
    except AttributeError:
        pass

    if BOTLOG:
        await block.client.send_message(
            BOTLOG_CHATID,
            "#BLOCKED\n" + "User: " + f"[{name0}](tg://user?id={uid})",
        )


@register(outgoing=True, pattern="^.ubl$")
async def unblockpm(unblock):
    """ For .unblock command, let people PMing you again! """
    if unblock.reply_to_msg_id:
        reply = await unblock.get_reply_message()
        replied_user = await unblock.client.get_entity(reply.from_id)
        name0 = str(replied_user.first_name)
        await unblock.client(UnblockRequest(replied_user.id))
        await unblock.edit(" 𝐔𝐍𝐁𝐋𝐎𝐂𝐊𝐄𝐃 ")

    if BOTLOG:
        await unblock.client.send_message(
            BOTLOG_CHATID,
            f"[{name0}](tg://user?id={replied_user.id})"
            " was 𝐔𝐍𝐁𝐋𝐎𝐂𝐊𝐄𝐃.",
        )
@register(outgoing=True, pattern="^.chats$")
async def dumver(dumyer):
    await dumyer.edit("⊙ 𝐂𝐇𝐀𝐓𝐒 ⊙ :\n⊙ .pu ⊙ .d ⊙ .sd ⊙ .bl ⊙ .app ⊙ .dap ⊙ .ubl ⊙ .fi ⊙ .st ⊙ .fs ⊙ .rmf \n⊙ .sw ⊙ .cw ⊙ .rw ⊙ .user ⊙ .notes ⊙ .clear ⊙ .save ⊙ .rmn ⊙ .ninja\n⊙ Help : .h 𝐂𝐇𝐀𝐓𝐒 for Details.")

CMD_HELP.update({
    "chats":
	"⊙ 𝐂𝐇𝐀𝐓𝐒 ⊙ :\n⊙ .pu Purge ⊙ .d Delete ⊙ .sd Self Destruction\
	\n⊙ .sw Set Welcome ⊙ .cw Check Welcome ⊙ .rw Remove Welcome\
	\n⊙ .notes Notes ⊙ .clear Notes ⊙ .save Notes ⊙ .rmn Removes All Bot Notes\
	\n⊙ .app Approves PM ⊙ .dap Disapproves PM ⊙ .bl Blocks PM ⊙ ubl Unblocks PM\
	\n⊙ .fi Filter ⊙ .st Stop Filter ⊙ .fs List Filters ⊙ .rmf Remove Bot Filters."
	})

"""
.approve\
\nUsage: Approves the mentioned/replied person to PM.\
\n\n.disapprove\
\nUsage: Disapproves the mentioned/replied person to PM.\
\n\n.block\
\nUsage: Blocks the person.\
\n\n.unblock\
\nUsage: Unblocks the person so they can PM you.\
\n\n.notifoff\
\nUsage: Clears/Disables any notifications of unapproved PMs.\
\n\n.notifon\
\nUsage: Allows notifications for unapproved PMs."
})"""
