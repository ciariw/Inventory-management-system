import logging
import re
from QueryManager import receive_query as query_
import asyncio
import telegram.ext
from telegram.ext.updater import Updater as Updater
from telegram import Update
from telegram.ext import Filters, CallbackContext, ConversationHandler, CommandHandler, InlineQueryHandler
from telegram.ext.messagehandler import MessageHandler


subs = {}
# The regex is being used to help flag handoffs giving wiggle room for spelling mistakes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

with open('APIkey.txt', encoding="utf-8") as key_file:  # read API key from text
    bot_token, bot_id = key_file.read().splitlines()
    # bot_id is the private chat id for the bot you're using

def enroll(update: Update, context: CallbackContext):
    # Not being used
    if update.effective_chat.id == update.effective_user.id:
        context.bot.send_message(chat_id=update.effective_chat.id,text="You can't /enroll here!")
        return
    if f"{update.effective_user.id}" not in subs:
        # If the person is not enrolled, add them to the list of enrolled folk
        subs[f"{update.effective_user.id}"] = dict()
        subs[f"{update.effective_user.id}"] = {"group": {f"{update.effective_chat.id}"},
                                               "name": update.effective_user.full_name}

    else:  # Otherwise, update the name and add the chat id to the set of chat IDs - prevents duplicates
        subs[f"{update.effective_user.id}"]["name"] = update.effective_user.full_name

        subs[f"{update.effective_user.id}"]["group"].add(update.effective_chat.id)

    # command /enroll adds the user to the list of subs.
    # It then sends a confirmation message to the person who typed the command below
    context.bot.send_message(chat_id=update.effective_user.id,text="Thank you for enrolling in translation messages")


def list_of_people(update: Update, context:CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"{subs}")


def migrate_querry(update:Update, context:CallbackContext):
    if update.message.chat.type != 'private':  # Not in the correct chat
        return
    query_(update.message)

def initialize():
    # on listen, I want to send info to a handler that connects to the database,
    # parses and searches the keywords in the database and returns a 'script' that displays key item information
    # API doenst interact with the database directly

    updater = Updater(token=bot_token, use_context=True)

    dispatcher = updater.dispatcher

    migrate = MessageHandler(callback=migrate_querry,filters=Filters.text)


    # mounting handler
    dispatcher.add_handler(migrate)

    # start listening
    updater.start_polling()


if __name__ == "__main__":
    initialize()