import os
import random
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update, ReactionTypeEmoji
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
PORT = int(os.environ.get("PORT", 10000))

EMOJIS = [
    "❤️", "👍", "🔥", "🥰", "🤣", "🗿",
    "❤️‍🔥", "💘", "💔", "💋", "😘", "💯",
]


class HealthHandler(BaseHTTPRequestHandler):
    """Cron-job.org va Render uchun oddiy 200 OK javob beradi."""

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"OK")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        # Har bir so'rovni logga yozmaslik uchun
        pass


def run_health_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    logger.info("Health server %s portida ishga tushdi", PORT)
    server.serve_forever()


async def react_to_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post = update.channel_post
    if post is None:
        return

    emoji = random.choice(EMOJIS)
    try:
        await context.bot.set_message_reaction(
            chat_id=post.chat_id,
            message_id=post.message_id,
            reaction=[ReactionTypeEmoji(emoji)],
        )
        logger.info("Post %s ga %s reaksiyasi qo'yildi", post.message_id, emoji)
    except Exception as e:
        logger.error("Reaksiya qo'yishda xato (post %s): %s", post.message_id, e)


async def on_startup(application):
    # Polling ishlashi uchun eski webhook bo'lsa o'chiramiz
    await application.bot.delete_webhook(drop_pending_updates=True)
    logger.info("Webhook o'chirildi, polling boshlanmoqda")


def main():
    threading.Thread(target=run_health_server, daemon=True).start()

    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(on_startup)
        .build()
    )
    application.add_handler(
        MessageHandler(filters.UpdateType.CHANNEL_POST, react_to_post)
    )

    application.run_polling(allowed_updates=["channel_post"])


if __name__ == "__main__":
    main()
