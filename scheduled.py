import schedule
import time
from datetime import datetime
import telebot


TOKEN = '946867453:AAFY657srK8t5bRuquYyCuuoo9ZxPXjGflE'
bot = telebot.TeleBot(TOKEN)
my_user_id = 409020404


def job():
    bot.send_message(my_user_id, str(datetime.now()))


schedule.every().day.at("17:02").do(job)
schedule.every().day.at("14:49").do(job)
schedule.every().day.at("14:50").do(job)
schedule.every().day.at("14:51").do(job)
schedule.every().day.at("14:52").do(job)




# schedule.every(3).seconds.do(send_time())


while True:
    schedule.run_pending()
    time.sleep(1)
