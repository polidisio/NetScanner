"""Main Telegram bot."""
import logging
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from config import Config
from news_fetcher import NewsFetcher
from summarizer import Summarizer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsBot:
    """Telegram bot for personalized news."""
    
    def __init__(self, config: Config):
        self.config = config
        self.fetcher = NewsFetcher()
        self.summarizer = Summarizer(
            api_key=config.minimax_api_key or "",
            model=config.minimax_model
        )
        self.subscriptions = {
            5640773790: ["cycling", "ai", "ios", "gaming", "cybersecurity"]  # Jose
        }  # user_id -> list of topics
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        await update.message.reply_text(
            "👋 *NewsBot Activated!*\n\n"
            "I send you personalized news based on your interests.\n\n"
            "Use /help to see available commands.",
            parse_mode="Markdown"
        )
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_text = (
            "📚 *Available Commands:*\n\n"
            "/subscribe `<topic>` - Subscribe to a topic\n"
            "/unsubscribe `<topic>` - Unsubscribe from a topic\n"
            "/list - List your subscriptions\n"
            "/news - Get latest news now\n"
            "/topics - See available topics\n\n"
            "Available topics: cycling, ai, ios, gaming, cybersecurity"
        )
        await update.message.reply_text(help_text, parse_mode="Markdown")
    
    async def topics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /topics command."""
        topics_text = (
            "📋 *Available Topics:*\n\n"
            "• `cycling` - 🚴 Cycling & Zwift news\n"
            "• `ai` - 🤖 AI & Machine Learning\n"
            "• `ios` - 📱 iOS Development\n"
            "• `gaming` - 🎮 Gaming news\n"
            "• `cybersecurity` - 🔒 Security news"
        )
        await update.message.reply_text(topics_text, parse_mode="Markdown")
    
    async def subscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /subscribe command."""
        user_id = update.effective_user.id
        if not context.args:
            await update.message.reply_text("Usage: /subscribe <topic>\nUse /topics to see available topics.")
            return
        
        topic = context.args[0].lower()
        if topic not in self.config.news_sources:
            await update.message.reply_text(f"Unknown topic: {topic}\nUse /topics to see available topics.")
            return
        
        if user_id not in self.subscriptions:
            self.subscriptions[user_id] = []
        
        if topic in self.subscriptions[user_id]:
            await update.message.reply_text(f"Already subscribed to {topic}!")
            return
        
        self.subscriptions[user_id].append(topic)
        await update.message.reply_text(f"✅ Subscribed to {topic}!")
    
    async def unsubscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unsubscribe command."""
        user_id = update.effective_user.id
        if not context.args:
            await update.message.reply_text("Usage: /unsubscribe <topic>")
            return
        
        topic = context.args[0].lower()
        if user_id in self.subscriptions and topic in self.subscriptions[user_id]:
            self.subscriptions[user_id].remove(topic)
            await update.message.reply_text(f"❌ Unsubscribed from {topic}")
        else:
            await update.message.reply_text(f"Not subscribed to {topic}")
    
    async def list_subscriptions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /list command."""
        user_id = update.effective_user.id
        if user_id not in self.subscriptions or not self.subscriptions[user_id]:
            await update.message.reply_text("No subscriptions yet.\nUse /subscribe <topic> to subscribe.")
            return
        
        subs = "\n".join(f"• {t}" for t in self.subscriptions[user_id])
        await update.message.reply_text(f"📋 *Your subscriptions:*\n\n{subs}", parse_mode="Markdown")
    
    async def news(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /news command."""
        user_id = update.effective_user.id
        topics = self.subscriptions.get(user_id, ["ai"])  # Default to AI if no subscriptions
        
        await update.message.reply_text("🔍 Fetching latest news...")
        
        all_news = []
        for topic in topics:
            sources = self.config.news_sources.get(topic, [])
            items = self.fetcher.fetch_topic(sources, topic)
            all_news.extend(items)
        
        if all_news:
            formatted = self.fetcher.format_news(all_news[:10])
            await update.message.reply_text(formatted, parse_mode="Markdown", disable_web_page_preview=True)
        else:
            await update.message.reply_text("😕 No news found right now. Try again later!")
    
    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle unknown messages."""
        await update.message.reply_text(
            "I don't understand that. Use /help to see available commands."
        )
    
    def run(self):
        """Start the bot."""
        app = Application.builder().token(self.config.telegram_token).build()
        
        # Add handlers
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("help", self.help))
        app.add_handler(CommandHandler("topics", self.topics))
        app.add_handler(CommandHandler("subscribe", self.subscribe))
        app.add_handler(CommandHandler("unsubscribe", self.unsubscribe))
        app.add_handler(CommandHandler("list", self.list_subscriptions))
        app.add_handler(CommandHandler("news", self.news))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo))
        
        logger.info("Starting NewsBot...")
        app.run_polling()

def main():
    """Entry point."""
    config = Config.from_env()
    if not config.validate():
        print("Error: TELEGRAM_BOT_TOKEN not set!")
        print("Set it with: export TELEGRAM_BOT_TOKEN='your-token'")
        return
    
    bot = NewsBot(config)
    bot.run()

if __name__ == "__main__":
    main()
