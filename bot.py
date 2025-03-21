import os
from uuid import uuid4

from dotenv import load_dotenv
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import (ApplicationBuilder, CommandHandler, ContextTypes,
                          InlineQueryHandler, MessageHandler, filters)

load_dotenv()

def generateBets(freebet_coef, money_coef, freebet, money_start = 100, money_step = 10, inaccuracy = 0.02):
    lowest_win = freebet / 2

    if freebet < 80:
      return 'таких фрибетов не бывает'

    bets = []
    for i in range(1000):
        bet = money_start + money_step * i
        freebet_win = round((freebet_coef - 1) * freebet - bet)
        money_win = round(bet * (money_coef - 1))
        
        bets.append({
            "bet": bet,
            "money_win": money_win,
            "freebet_win": freebet_win
        })

    profitable_bets = [
        bet for bet in bets
        if bet["money_win"] >= lowest_win * (1 - inaccuracy) and
          bet["freebet_win"] >= lowest_win * (1 - inaccuracy)
    ]

    if not profitable_bets:
        return "кэфы говно"
    
    def sort_key(bet):
      diff = bet["money_win"] + bet["freebet_win"] - 2 * lowest_win
      return (-diff, bet["bet"])

    profitable_bets_sorted = sorted(profitable_bets, key=sort_key)
    
    print(*profitable_bets_sorted, sep='\n')
    
    return profitable_bets_sorted


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(update.message.text_html)


async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    print(args)

    if (len(args) != 3): 
      await context.bot.send_message(chat_id=update.effective_chat.id, text='должно быть три параметра: [фрибет_кэф] [руб_кэф] [фрибет]')
      return

    bets = []
    try:
      bets = generateBets(*list(map(float, args)))
    except:
      await context.bot.send_message(chat_id=update.effective_chat.id, text='Не удалось конвертировать параметры')
      return
    
    if isinstance(bets, str):
      await context.bot.send_message(chat_id=update.effective_chat.id, text=bets)
      return

    message = "Список ставок:\n\n"
    print(bets)
    for item in bets:
        message += (
            f"💰 Ставка: {item['bet']}р\n"
            f"🎯 Выигрыш {args[0]} = {item['money_win']}р\n"
            f"🎁 Выигрыш {args[1]} = {item['freebet_win']}р\n\n"
        )

    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def main() -> None:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if  TELEGRAM_BOT_TOKEN is None:
        raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных окружения")
    
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    caps_handler = CommandHandler('calc', calc)
    application.add_handler(caps_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
