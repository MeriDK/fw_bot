"""
TODO
- change sticker sending to replying after finishing task
- DONE
- add time checking in scheduled file, delete here:
    should open 'today.json' at 9 am and set all values on Fault
- finish pinning players at 9:01 13:00 19:00 22:00 7:00
    should send message 'it's high time to get/finish task'
- add /pin command
    should pin everyone who hasn't finished task by this time yet
    only 5 users per message
TODO
"""


import datetime
import json
from random import randint

import telebot
import config
import collections


TOKEN = config.TOKEN
bot = telebot.TeleBot(TOKEN)

fw_id = config.fw_id

chat_id = config.chat_id

stickers = config.stickers


# TODO day should change with checking time before/after 9 am
def check_time(timestamp):
    return timestamp > datetime.datetime(year=2019, month=9, day=25, hour=9)


# get sticker to answer on finished task
def get_sticker(user_id):
    if user_id == config.sasha_id:
        return config.sasha_sticker
    return stickers[randint(0, len(stickers))]


# parse message with words 'Ты завершил/ла задание замка!' in it
@bot.message_handler(regexp='Ты завершил(а|) задание замка!')
def get_finished_daylik(message):

    # should work only in our chat (commented out for debug purposes)
    #if message.chat.id == chat_id:

        # check if message from fw bot
        if message.forward_from is not None and message.forward_from.id == fw_id:

            user_id = message.from_user.id

            with open('today.json', 'r') as f:
                today = json.loads(f.read())

            # check if user already finished task
            if today[str(user_id)] is False:

                # TODO add reply
                bot.send_sticker(chat_id, get_sticker(user_id), reply_to_message_id = message.message_id)

                # mark user's task as finished
                # DEBUG
                if user_id!=409020404:
                    today[str(user_id)] = True
                with open('today.json', 'w') as f:
                    f.write(json.dumps(today))

                # renew top
                with open('top.json', 'r') as f:
                    top = json.loads(f.read())

                top[config.users[user_id][1:]] += 1

                with open('top.json', 'w') as f:
                    f.write(json.dumps(top))
            else:
                # user already finished task
                bot.reply_to(message, 'Совсем ничего нового 🙄\nХвастаешься?')
        #else:
            # not our chat
        #    bot.reply_to(message, 'Киш')


# answer on command /topchik
@bot.message_handler(commands=['topchik'])
def top_func(message):

    # should work in our chat only
    #if message.chat.id == chat_id:
        with open('top.json', 'r') as f:
            top = json.loads(f.read())
            sorted_top = collections.OrderedDict(sorted(top.items(), key=lambda kv: kv[1], reverse=True))
            ans = ''
            i = 1
            for key, val in sorted_top.items():
                ans += f'{i}. {key}: {val}\n'
                i += 1
            bot.reply_to(message, ans)
    #else:
        # not our chat
        # bot.reply_to(message, 'Киш')


bot.polling()


