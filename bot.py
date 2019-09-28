"""
TODO
- add time checking in scheduled file, delete here:
    should open 'today.json' at 9 am and set all values on Fault
- finish pinning players at 9:01 13:00 19:00 22:00 7:00
    should send message 'it's high time to get/finish task'
TODO
"""


import datetime
import json
from random import randint

import telebot
import config
import collections
from telebot.apihelper import ApiException


TOKEN = config.TOKEN
bot = telebot.TeleBot(TOKEN)

fw_id = config.fw_id

chat_id = config.chat_id

stickers = config.stickers


# TODO day should change with checking time before/after 9 am
def check_time(timestamp):
    return timestamp > datetime.datetime(year=2019, month=9, day=25, hour=9)


# get sticker to answer on finished task
def get_sticker(user_tag):
    if user_tag == '@Sangu_007':
        return config.sasha_sticker
    return stickers[randint(0, len(stickers)-1)]

# parse command '/pin'
@bot.message_handler(commands=['pin'])
def pin(message):
    with open('today.json', 'r') as f:
        today = json.loads(f.read())
    counter = 0
    message_text = ''
    for k, v in today.items():
        # parse out by 5 users per message
        if counter==5:
            bot.send_message(message.chat.id, message_text)
            counter=0
            message_text=''
        if v==False:
            message_text+=f'{k} '
            counter+=1
    bot.send_message(message.chat.id, message_text)
    bot.send_message(message.chat.id, 'Рабы галерные, а ну живо дейлики поделали!')

# parse message with words 'Ты завершил/ла задание замка!' in it
@bot.message_handler(regexp='Ты завершил(а|) задание замка!')
def get_finished_daylik(message):

    # should work only in our chat (commented out for debug purposes)
    #if message.chat.id == chat_id:

        # check if message from fw bot
        if message.forward_from is not None and message.forward_from.id == fw_id:
            
            user_tag = message.from_user.username

            with open('today.json', 'r') as f:
                today = json.loads(f.read())

            # check if user already finished task
            if today['@'+user_tag] is False:
                #send reply
                bot.send_sticker(message.chat.id, get_sticker(user_tag), reply_to_message_id=message.message_id)
                # mark user's task as finished
                today['@'+user_tag] = True
                with open('today.json', 'w') as f:
                    f.write(json.dumps(today))

                # renew top
                with open('top.json', 'r') as f:
                    top = json.loads(f.read())

                top[user_tag] += 1

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


