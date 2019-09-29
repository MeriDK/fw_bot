from datetime import datetime
import time
import json
from random import randint

import schedule
import telebot
import config
import collections
from multiprocessing import Process

TOKEN = config.TOKEN
bot = telebot.TeleBot(TOKEN)

fw_id = config.fw_id
chat_id = config.chat_id
stickers = config.stickers
today = datetime.today()
last_refresh = datetime(today.year,today.month,today.day,9).timestamp()
schedule_work = True

# get sticker to answer on finished task
def get_sticker(user_tag):
    if user_tag == 'Sangu_007':
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
            bot.send_message(chat_id, message_text)
            counter=0
            message_text=''
        if v==False:
            message_text+=f'{k} '
            counter+=1
    bot.send_message(chat_id, message_text)
    bot.send_message(chat_id, 'Рабы галерные, а ну живо дейлики сдали!')
    
# refreshes time check for messages as well as whether the daily has been given in today
def refresh():
    global last_refresh
    with open('today.json', 'r') as f:
        today = json.loads(f.read())
        counter = 0
        message_text = ''
        for k in today:
            today[k]=False
            message_text+=f'{k} '
            counter+=1
            if counter==5:
                bot.send_message(chat_id, message_text)
                counter=0
                message_text=''
        bot.send_message(chat_id, message_text)
    bot.send_message(chat_id, 'Пошли за дейликами!')
    with open('today.json', 'w') as f:
         f.write(json.dumps(today))
    last_refresh=datetime.now().timestamp()

# remind people to complete their dailies automatically (uses "pin" function)
def run_schedule():
    schedule.every().day.at("16:00").do(pin, None)
    schedule.every().day.at("22:00").do(pin, None)
    schedule.every().day.at("07:00").do(pin, None)
    schedule.every().day.at("09:00").do(refresh)
    while schedule_work:
        schedule.run_pending()
        time.sleep(1)

# parse message with words 'Ты завершил/ла задание замка!' in it. Additionaly, allows Meri to mark one's daily as done
@bot.message_handler(regexp='Ты завершил(а|) задание замка!')
def get_finished_daylik(message):

    # should work only in our chat
    if message.chat.id == chat_id:

        # check if message from fw bot or our great and glorious leader
        if message.forward_from is not None and message.forward_from.id == fw_id:
            # get sender's username
            user_tag = message.from_user.username

            with open('today.json', 'r') as f:
                today = json.loads(f.read())
            # check if user already finished task and if the message is from today
            if today['@'+user_tag] is False and message.forward_date>last_refresh:
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
    else:
        # not our chat
        bot.reply_to(message, 'Киш')
        

@bot.message_handler(commands=['unpin'])
def count_today(message):
    #check for user and chat
    if message.from_user.id==config.my_user_id and message.chat.id == chat_id:
        if message.reply_to_message is not None:
            # get the user from the message you're replying to
            user_tag = message.reply_to_message.from_user.username
        else:
            bot.reply_to(message,'Моя не понимать')
            return
        with open('today.json', 'r') as f:
                today = json.loads(f.read())
        # check if user already finished task and if the message is from today
        if today['@'+user_tag] is False and message.forward_date>last_refresh:
            bot.reply_to(message,'Слушаюсь и повинуюсь, госпожа')
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
            if message.reply_to_message is not None:
                bot.reply_to(message,'Я бы с радостью, но дейлик уже сдан')
    elif message.from_user.id!=config.my_user_id and message.chat.id == chat_id:
        # send sticker "У тебя нет прав"
        bot.send_sticker(chat_id,"CAADAgADKwAD9CdhGBqHLEJrKytdFgQ",reply_to_message_id=message.message_id)
    else:
        bot.reply_to(message, 'Киш')       


# answer on command /topchik
@bot.message_handler(commands=['topchik'])
def top_func(message):

    # should work in our chat only
    if message.chat.id == chat_id:
        with open('top.json', 'r') as f:
            top = json.loads(f.read())
            sorted_top = collections.OrderedDict(sorted(top.items(), key=lambda kv: kv[1], reverse=True))
            ans = ''
            i = 1
            for key, val in sorted_top.items():
                ans += f'{i}. {key}: {val}\n'
                i += 1
            bot.reply_to(message, ans)
    else:
        # not our chat
         bot.reply_to(message, 'Киш')
        
if __name__=='__main__':
    sch = Process(target=run_schedule)
    sch.start()
    try:
        bot.polling()
    except Exception:
        schedule_work=False


