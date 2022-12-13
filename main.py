from datetime import datetime
import logging
from random import choice
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CallbackContext, CommandHandler
from chatdoc import chatdoc
import psycopg2

chatbot = chatdoc('Training')

def write_data(text, file):
    file_obj = open(file, "a", encoding="utf-8")
    file_obj.write(str(datetime.now()) + " : " +text + "\n")
    file_obj.close()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: CallbackContext.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello, I'm Soal Undi bot\nReady to answer any questions about PRU as best I can!"
    )

async def echo(update: Update, context: CallbackContext.DEFAULT_TYPE):

    sql = """INSERT INTO public."Questions"("Timestamp", "Questions")
             VALUES(%s, %s);"""

    await context.bot.send_message(chat_id=update.effective_chat.id, text=str(chatbot.generateResponse(update.message.text)))
    conn_out = psycopg2.connect("dbname=SoalUndiDB user=postgres password=")
    write_data(update.message.text, "logtest1.txt")
    cur = conn_out.cursor()
    cur.execute(sql, (datetime.now(), update.message.text))
    conn_out.commit()
    conn_out.close()

if __name__ == '__main__':
    application = ApplicationBuilder().token('5224908027:AAEL_d9wym2Sh291PAN4fVfKK7qkwWjkUqg').build()
    
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    start_handler = CommandHandler('start', start)
    application.add_handler(echo_handler)
    application.add_handler(start_handler)

    application.run_polling()
