"""
Telegram bot integration for the AI-Enhanced Crypto Onboarding Chatbot.

This module provides a Telegram interface for users to interact with
the crypto onboarding assistant.
"""

import os
import logging
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from dotenv import load_dotenv

from src.rag_pipeline import query_rag

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Language mappings
LANGUAGES = {
    'en': '🇺🇸 English',
    'es': '🇪🇸 Español',
    'zh': '🇨🇳 中文',
    'hi': '🇮🇳 हिन्दी',
    'fr': '🇫🇷 Français',
    'de': '🇩🇪 Deutsch',
    'ja': '🇯🇵 日本語',
    'ko': '🇰🇷 한국어',
    'pt': '🇧🇷 Português',
    'ru': '🇷🇺 Русский'
}

LANGUAGE_NAMES = {
    'en': 'English',
    'es': 'Español',
    'zh': '中文',
    'hi': 'हिन्दी',
    'fr': 'Français',
    'de': 'Deutsch',
    'ja': '日本語',
    'ko': '한국어',
    'pt': 'Português',
    'ru': 'Русский'
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /start command.
    
    Args:
        update: Telegram update object
        context: Callback context
    """
    user = update.effective_user
    logger.info(f"User {user.id} ({user.username}) started the bot")
    
    # Initialize user language preference
    if 'language' not in context.user_data:
        context.user_data['language'] = 'en'
    
    welcome_message = (
        f"👋 Welcome to the **Crypto Onboarding Assistant**, {user.first_name}!\n\n"
        "I'm your AI-powered guide for navigating the crypto world. I can help you with:\n\n"
        "🔹 **Staking** - Learn how to stake your tokens\n"
        "🔹 **Bridging** - Transfer assets between blockchains\n"
        "🔹 **Wallets** - Set up and secure your crypto wallets\n"
        "🔹 **Protocols** - Navigate DeFi protocols and dApps\n\n"
        "Just ask me anything! For example:\n"
        "• _How do I stake ETH?_\n"
        "• _What's the best hardware wallet?_\n"
        "• _How do I bridge tokens to Polygon?_\n\n"
        "**Commands:**\n"
        "/help - Show help message\n"
        "/language - Change response language\n"
        "/examples - See example questions\n\n"
        "Let's get started! What would you like to know?"
    )
    
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /help command.
    
    Args:
        update: Telegram update object
        context: Callback context
    """
    help_text = (
        "🤖 **Crypto Onboarding Assistant Help**\n\n"
        "**How to use:**\n"
        "Simply send me a message with your question about crypto, and I'll provide detailed answers!\n\n"
        "**Available Commands:**\n"
        "/start - Start the bot and see welcome message\n"
        "/help - Show this help message\n"
        "/language - Change response language\n"
        "/examples - See example questions\n\n"
        "**Topics I can help with:**\n"
        "• Cryptocurrency basics\n"
        "• Staking and yield farming\n"
        "• Cross-chain bridging\n"
        "• Wallet setup and security\n"
        "• DeFi protocols\n"
        "• NFTs and Web3\n\n"
        "**Tips:**\n"
        "• Be specific in your questions\n"
        "• Ask one question at a time for best results\n"
        "• Use /language to get responses in your preferred language\n\n"
        "Need more help? Just ask! 😊"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def examples_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /examples command.
    
    Args:
        update: Telegram update object
        context: Callback context
    """
    examples_text = (
        "💡 **Example Questions You Can Ask:**\n\n"
        "**Staking:**\n"
        "• How do I stake Ethereum?\n"
        "• What's the difference between staking and liquidity mining?\n"
        "• What are the risks of staking?\n\n"
        "**Bridging:**\n"
        "• How do I bridge USDC from Ethereum to Polygon?\n"
        "• What are the best cross-chain bridges?\n"
        "• Is bridging safe?\n\n"
        "**Wallets:**\n"
        "• How do I set up MetaMask?\n"
        "• What's the best hardware wallet?\n"
        "• How do I keep my seed phrase safe?\n\n"
        "**DeFi:**\n"
        "• What is Uniswap and how do I use it?\n"
        "• How do I provide liquidity?\n"
        "• What is impermanent loss?\n\n"
        "Try asking any of these or your own questions!"
    )
    
    await update.message.reply_text(examples_text, parse_mode='Markdown')


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /language command - show language selection keyboard.
    
    Args:
        update: Telegram update object
        context: Callback context
    """
    # Create inline keyboard with language options
    keyboard = []
    row = []
    for i, (code, name) in enumerate(LANGUAGES.items()):
        row.append(InlineKeyboardButton(name, callback_data=f"lang_{code}"))
        if (i + 1) % 2 == 0:  # 2 buttons per row
            keyboard.append(row)
            row = []
    
    if row:  # Add remaining buttons
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    current_lang = context.user_data.get('language', 'en')
    current_lang_name = LANGUAGE_NAMES.get(current_lang, 'English')
    
    await update.message.reply_text(
        f"🌍 **Select Your Preferred Language**\n\n"
        f"Current language: **{current_lang_name}**\n\n"
        f"Choose a language from the options below:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle language selection callback.
    
    Args:
        update: Telegram update object
        context: Callback context
    """
    query = update.callback_query
    await query.answer()
    
    # Extract language code from callback data
    language_code = query.data.replace('lang_', '')
    
    # Update user's language preference
    context.user_data['language'] = language_code
    language_name = LANGUAGE_NAMES.get(language_code, 'English')
    
    logger.info(f"User {update.effective_user.id} changed language to {language_name}")
    
    await query.edit_message_text(
        f"✅ Language changed to **{language_name}**!\n\n"
        f"I'll now respond in {language_name}. You can change this anytime using /language",
        parse_mode='Markdown'
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle regular text messages from users.
    
    Args:
        update: Telegram update object
        context: Callback context
    """
    user = update.effective_user
    user_message = update.message.text
    
    logger.info(f"Received message from {user.id} ({user.username}): {user_message[:100]}")
    
    # Get user's language preference
    language_code = context.user_data.get('language', 'en')
    language_name = LANGUAGE_NAMES.get(language_code, 'English')
    
    # Send typing action
    await update.message.chat.send_action(action="typing")
    
    try:
        # Get response from RAG pipeline
        response = query_rag(user_message, language=language_name)
        
        # Send response
        bot_response = response.get('answer', 'Sorry, I encountered an error.')
        
        # Split long messages if needed (Telegram limit: 4096 chars)
        if len(bot_response) > 4000:
            parts = [bot_response[i:i+4000] for i in range(0, len(bot_response), 4000)]
            for part in parts:
                await update.message.reply_text(part, parse_mode='Markdown')
        else:
            await update.message.reply_text(bot_response, parse_mode='Markdown')
        
        logger.info(f"Successfully responded to user {user.id}")
    
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}", exc_info=True)
        await update.message.reply_text(
            "❌ Sorry, I encountered an error processing your question. "
            "Please try again or rephrase your question."
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle errors in the bot.
    
    Args:
        update: Telegram update object
        context: Callback context
    """
    logger.error(f"Update {update} caused error {context.error}", exc_info=context.error)
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ An error occurred. Please try again later."
        )


def main() -> None:
    """Start the Telegram bot."""
    # Get bot token from environment
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        raise ValueError("TELEGRAM_BOT_TOKEN is required")
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("OPENAI_API_KEY not found in environment variables!")
        raise ValueError("OPENAI_API_KEY is required")
    
    logger.info("Initializing Telegram bot...")
    
    # Create application
    application = Application.builder().token(bot_token).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("examples", examples_command))
    application.add_handler(CommandHandler("language", language_command))
    
    # Register callback query handler for language selection
    application.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
    
    # Register message handler for regular messages
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    logger.info("Telegram bot is running! Press Ctrl+C to stop.")
    
    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
