import requests
from bs4 import BeautifulSoup
import random
from fake_useragent import UserAgent
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime 
import calendar

TELEGRAM_BOT_TOKEN = "8065212930:AAGf3f1KFR1rDKjWGsKrY4JlrYvUazm9uuA"

UA = UserAgent()
BASE = "https://www.onthisday.com/today"

def scrape_category(category_path):
    url = f"https://www.onthisday.com/{category_path}"
    headers = {"User-Agent": UA.random}
    r = requests.get(url, headers=headers, timeout=10)
    print(r.url)
    print(r.status_code)
    if r.status_code != 200:
        return None
    soup = BeautifulSoup(r.text, 'html.parser')
    items = [li.get_text(strip=True) for li in soup.select(".section__content li")[:5]]
    return items or None

async def today(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    events = scrape_category("events")
    births = scrape_category("births")
    deaths = scrape_category("deaths")

    msg = "<b>📅 Today in History</b>\n"
    def format_list(title, data):
        if data:
            return f"\n\n<b>{title}:</b>\n" + "\n".join(f"• {x}" for x in data)
        else:
            return f"\n\n<b>{title}:</b> Not available"

    msg += format_list("Events", events)
    msg += format_list("Births", births)
    msg += format_list("Deaths", deaths)

    await update.message.reply_html(msg)

async def ondate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("Usage: /ondate <month> <day> (e.g., /ondate 11 23)")
        return

    try:
        month = int(context.args[0])
        day = int(context.args[1])
        year = datetime.now().year
    except ValueError:
        await update.message.reply_text("Invalid input. Use numbers for month and day.")
        return

    if not (1 <= month <= 12 and 1 <= day <= 31):
        await update.message.reply_text("Month or day out of range.")
        return

    data = scrape_on_this_day(year, month, day)
    if not data:
        await update.message.reply_text("No data found for this date.")
        return

    msg = f"<b>🗓️ On {year}-{month:02d}-{day:02d}</b>"
    for title, items in data.items():
        msg += f"\n\n<b>{title}:</b>\n" + "\n".join(f"• {item}" for item in items or ["No data found."])

    await update.message.reply_html(msg, disable_web_page_preview=True)

def scrape_on_this_day(year, month_number, day):

    ua = UserAgent()
    month_name = calendar.month_name[month_number]  # 'November'

    url = f"https://www.onthisday.com/date/{year}/{month_name}/{day}"
    headers = {"User-Agent": ua.random}
    r = requests.get(url, headers=headers, timeout=10)
    print(url)
    print(r.status_code)
    print(r.url)
    if r.status_code != 200:
        return None

    soup = BeautifulSoup(r.text, 'html.parser')

    def extract_section(section_id):
        section = soup.find("section", {"id": section_id})
        if not section:
            return []
        return [li.get_text(strip=True) for li in section.find_all("li")[:5]]

    return {
        "Events": extract_section("events"),
        "Births": extract_section("births"),
        "Deaths": extract_section("deaths")
    }

# Main
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CommandHandler("ondate", ondate))
    app.run_polling()

if __name__ == "__main__":
    main()
