from datetime import datetime
import logging
from random import choice
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CallbackContext, CommandHandler
from precomp import *
import psycopg2
from chatbot import *
import time

chatbot = chatbot()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: CallbackContext.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello, I'm Soal Undi bot\nReady to answer any questions about the elections as best I can!\nIf it is not a big deal, can you send me your location for me to take note?\nYou can just ask away if you don't want to!"
    )

async def echo(update: Update, context: CallbackContext.DEFAULT_TYPE):

    responses = ["yes", "no"]

    if "thank" in update.message.text.lower()  :
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Are you satisfied with the answers?")
        
    elif (update.message.text.lower() in responses) :

        sql_q = """INSERT INTO public."Satisfaction"("Timestamp", "Response")
                VALUES(%s, %s);"""

        if responses[0] in update.message.text.lower() : feedback = "Yes"
        elif responses[1] in update.message.text.lower() : feedback = "No"

        conn_out = psycopg2.connect("dbname=SoalUndiDB user=postgres password=")
        cur = conn_out.cursor()
        cur.execute(sql_q, (datetime.now(), feedback))
        conn_out.commit()
        conn_out.close()
        

    else :
        start = time.time()

        sql_q = """INSERT INTO public."Questions"("Timestamp", "Questions", "Response_time")
                VALUES(%s, %s, %s);"""

        answer = chatbot.response(update.message.text)
        if answer is None : 
            answer = "I'm sorry, I don't know how to answer your question"

            sql_b = """INSERT INTO public."Missed"("Timestamp", "Question")
                VALUES(%s, %s);"""

            conn_out = psycopg2.connect("dbname=SoalUndiDB user=postgres password=")
            cur = conn_out.cursor()
            cur.execute(sql_b, (datetime.now(), update.message.text))
            conn_out.commit()
            conn_out.close()

        
        await context.bot.send_message(chat_id=update.effective_chat.id, text=str(answer))

        end = time.time()

        response_time = end - start

        conn_out = psycopg2.connect("dbname=SoalUndiDB user=postgres password=")
        cur = conn_out.cursor()
        cur.execute(sql_q, (datetime.now(), update.message.text, response_time))
        conn_out.commit()
        conn_out.close()
        update_keywords(freq_list(get_Tokens(get_Questions())))

async def locate(update: Update, context: CallbackContext.DEFAULT_TYPE):

    sql_geo = """INSERT INTO public."Geolocation"("Latitude", "Longitude", "Timestamp")
                 VALUES(%s, %s, %s);"""

    conn_out = psycopg2.connect("dbname=SoalUndiDB user=postgres password=")
    cur = conn_out.cursor()
    cur.execute(sql_geo, (update.message.location.latitude, update.message.location.longitude, datetime.now()))
    conn_out.commit()
    conn_out.close()

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Thank You! You can ask your questions now!"
    )


if __name__ == '__main__':
    application = ApplicationBuilder().token('{TOKEN}').build()
    
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    start_handler = CommandHandler('start', start)
    locate_handler = MessageHandler(filters.LOCATION, locate)
    application.add_handler(echo_handler)
    application.add_handler(start_handler)
    application.add_handler(locate_handler)

    application.run_polling()
