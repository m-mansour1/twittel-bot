import snscrape.modules.twitter as sntwitter
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import logging

# Configure Telegram bot token
TELEGRAM_BOT_TOKEN = "8065212930:AAGf3f1KFR1rDKjWGsKrY4JlrYvUazm9uuA"

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Command handler
async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a Twitter username. Example: /getlocation elonmusk")
        return

    username = context.args[0].lstrip('@')
    tweets = sntwitter.TwitterUserScraper(username).get_items()
    count = 0

    for tweet in tweets:
        if tweet.coordinates:
            lat, lon = tweet.coordinates.latitude, tweet.coordinates.longitude
            message = (
                f"📍 *Location Found!*\n"
                f"📝 Tweet: {tweet.content}\n"
                f"🗓️ Date: {tweet.date.strftime('%Y-%m-%d %H:%M')}\n"
                f"🌐 Coordinates: [{lat}, {lon}]\n"
                f"🔗 [View Tweet]({tweet.url})"
            )
            await update.message.reply_text(message, parse_mode='Markdown', disable_web_page_preview=True)
            return
        count += 1
        if count > 50:
            break

    await update.message.reply_text("No geotagged tweets found in recent history.")

# Main bot function
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("getlocation", get_location))
    app.run_polling()

if __name__ == "__main__":
    main()
