"""
Discord bot integration for the AI-Enhanced Crypto Onboarding Chatbot.

This module provides a Discord interface for users to interact with
the crypto onboarding assistant using slash commands.
"""

import os
import logging
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
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
LANGUAGE_CHOICES = [
    app_commands.Choice(name="🇺🇸 English", value="English"),
    app_commands.Choice(name="🇪🇸 Español", value="Español"),
    app_commands.Choice(name="🇨🇳 中文", value="中文"),
    app_commands.Choice(name="🇮🇳 हिन्दी", value="हिन्दी"),
    app_commands.Choice(name="🇫🇷 Français", value="Français"),
    app_commands.Choice(name="🇩🇪 Deutsch", value="Deutsch"),
    app_commands.Choice(name="🇯🇵 日本語", value="日本語"),
    app_commands.Choice(name="🇰🇷 한국어", value="한국어"),
    app_commands.Choice(name="🇧🇷 Português", value="Português"),
    app_commands.Choice(name="🇷🇺 Русский", value="Русский"),
]


class CryptoBot(commands.Bot):
    """Custom Discord bot class for crypto onboarding."""
    
    def __init__(self):
        """Initialize the bot with required intents."""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None  # We'll use custom help command
        )
    
    async def setup_hook(self):
        """Set up the bot and sync commands."""
        logger.info("Setting up bot commands...")
        await self.tree.sync()
        logger.info("Commands synced successfully")
    
    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f'{self.user} is now online!')
        logger.info(f'Connected to {len(self.guilds)} guild(s)')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="crypto enthusiasts | /ask"
            )
        )


# Initialize bot
bot = CryptoBot()


@bot.tree.command(name="ask", description="Ask the crypto onboarding assistant a question")
@app_commands.describe(
    question="Your question about crypto, staking, bridging, wallets, etc.",
    language="Language for the response (default: English)"
)
@app_commands.choices(language=LANGUAGE_CHOICES)
async def ask(
    interaction: discord.Interaction,
    question: str,
    language: Optional[app_commands.Choice[str]] = None
):
    """
    Handle the /ask slash command.
    
    Args:
        interaction: Discord interaction object
        question: User's question
        language: Preferred language for response
    """
    # Defer the response as processing may take time
    await interaction.response.defer(thinking=True)
    
    # Get language
    lang = language.value if language else "English"
    
    logger.info(
        f"User {interaction.user.name} asked: {question[:100]} (Language: {lang})"
    )
    
    try:
        # Get response from RAG pipeline
        response = query_rag(question, language=lang)
        bot_response = response.get('answer', 'Sorry, I encountered an error.')
        
        # Create embed for better formatting
        embed = discord.Embed(
            title="🤖 Crypto Assistant Response",
            description=bot_response[:4096],  # Discord embed description limit
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        
        # Add fields
        embed.add_field(name="Question", value=question[:1024], inline=False)
        embed.add_field(name="Language", value=lang, inline=True)
        
        # Set footer
        embed.set_footer(
            text=f"Requested by {interaction.user.name}",
            icon_url=interaction.user.display_avatar.url
        )
        
        # Send response
        await interaction.followup.send(embed=embed)
        
        logger.info(f"Successfully responded to {interaction.user.name}")
    
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}", exc_info=True)
        
        error_embed = discord.Embed(
            title="❌ Error",
            description="Sorry, I encountered an error processing your question. Please try again.",
            color=discord.Color.red()
        )
        
        await interaction.followup.send(embed=error_embed, ephemeral=True)


@bot.tree.command(name="help", description="Show help information about the crypto assistant")
async def help_command(interaction: discord.Interaction):
    """
    Handle the /help slash command.
    
    Args:
        interaction: Discord interaction object
    """
    embed = discord.Embed(
        title="🤖 Crypto Onboarding Assistant Help",
        description="I'm your AI-powered guide for navigating the crypto world!",
        color=discord.Color.green()
    )
    
    # Add fields with information
    embed.add_field(
        name="📋 Commands",
        value=(
            "`/ask` - Ask me any question about crypto\n"
            "`/examples` - See example questions\n"
            "`/help` - Show this help message\n"
            "`/about` - Learn about this bot"
        ),
        inline=False
    )
    
    embed.add_field(
        name="💡 Topics I Can Help With",
        value=(
            "• Cryptocurrency basics\n"
            "• Staking and yield farming\n"
            "• Cross-chain bridging\n"
            "• Wallet setup and security\n"
            "• DeFi protocols\n"
            "• NFTs and Web3"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🌍 Languages",
        value=(
            "I support 10+ languages! Use the `language` option in `/ask` "
            "to get responses in your preferred language."
        ),
        inline=False
    )
    
    embed.add_field(
        name="💪 Tips for Best Results",
        value=(
            "• Be specific in your questions\n"
            "• Ask one question at a time\n"
            "• Include context when relevant"
        ),
        inline=False
    )
    
    embed.set_footer(text="Powered by RAG and AI")
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="examples", description="See example questions you can ask")
async def examples(interaction: discord.Interaction):
    """
    Handle the /examples slash command.
    
    Args:
        interaction: Discord interaction object
    """
    embed = discord.Embed(
        title="💡 Example Questions",
        description="Here are some questions you can ask me:",
        color=discord.Color.gold()
    )
    
    embed.add_field(
        name="🔹 Staking",
        value=(
            "• How do I stake Ethereum?\n"
            "• What's the difference between staking and liquidity mining?\n"
            "• What are the risks of staking?"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🌉 Bridging",
        value=(
            "• How do I bridge USDC from Ethereum to Polygon?\n"
            "• What are the best cross-chain bridges?\n"
            "• Is bridging safe?"
        ),
        inline=False
    )
    
    embed.add_field(
        name="👛 Wallets",
        value=(
            "• How do I set up MetaMask?\n"
            "• What's the best hardware wallet?\n"
            "• How do I keep my seed phrase safe?"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🏦 DeFi",
        value=(
            "• What is Uniswap and how do I use it?\n"
            "• How do I provide liquidity?\n"
            "• What is impermanent loss?"
        ),
        inline=False
    )
    
    embed.set_footer(text="Try asking any of these or your own questions with /ask!")
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="about", description="Learn about the Crypto Onboarding Assistant")
async def about(interaction: discord.Interaction):
    """
    Handle the /about slash command.
    
    Args:
        interaction: Discord interaction object
    """
    embed = discord.Embed(
        title="🤖 About Crypto Onboarding Assistant",
        description=(
            "An AI-powered chatbot designed to help users navigate the crypto world "
            "with ease and confidence."
        ),
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="🚀 Technology",
        value=(
            "Built with Retrieval-Augmented Generation (RAG) technology, combining:\n"
            "• Large Language Models (LLMs)\n"
            "• Vector databases\n"
            "• Up-to-date crypto documentation"
        ),
        inline=False
    )
    
    embed.add_field(
        name="✨ Features",
        value=(
            "• Multi-language support (10+ languages)\n"
            "• Real-time, accurate information\n"
            "• Beginner-friendly explanations\n"
            "• Security-focused guidance"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🔗 Links",
        value=(
            "[GitHub](https://github.com/nvcs0101-hue/AI-Enhanced-Crypto-Onboarding-Chatbot) • "
            "[Documentation](#) • "
            "[Support](#)"
        ),
        inline=False
    )
    
    embed.set_footer(text="Version 1.0.0 | Powered by OpenAI and LangChain")
    
    await interaction.response.send_message(embed=embed)


@bot.event
async def on_message(message: discord.Message):
    """
    Handle direct messages to the bot.
    
    Args:
        message: Discord message object
    """
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Process commands
    await bot.process_commands(message)
    
    # Handle DMs
    if isinstance(message.channel, discord.DMChannel):
        # Send typing indicator
        async with message.channel.typing():
            try:
                # Get response from RAG pipeline
                response = query_rag(message.content)
                bot_response = response.get('answer', 'Sorry, I encountered an error.')
                
                # Split long messages if needed (Discord limit: 2000 chars)
                if len(bot_response) > 1900:
                    parts = [bot_response[i:i+1900] for i in range(0, len(bot_response), 1900)]
                    for part in parts:
                        await message.channel.send(part)
                else:
                    await message.channel.send(bot_response)
                
                logger.info(f"Responded to DM from {message.author.name}")
            
            except Exception as e:
                logger.error(f"Error handling DM: {str(e)}", exc_info=True)
                await message.channel.send(
                    "❌ Sorry, I encountered an error. Please try using `/ask` instead."
                )


@bot.event
async def on_error(event: str, *args, **kwargs):
    """Handle bot errors."""
    logger.error(f"Error in event {event}", exc_info=True)


def main():
    """Start the Discord bot."""
    # Get bot token from environment
    bot_token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not bot_token:
        logger.error("DISCORD_BOT_TOKEN not found in environment variables!")
        raise ValueError("DISCORD_BOT_TOKEN is required")
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("OPENAI_API_KEY not found in environment variables!")
        raise ValueError("OPENAI_API_KEY is required")
    
    logger.info("Starting Discord bot...")
    
    try:
        bot.run(bot_token)
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}", exc_info=True)
        raise


if __name__ == '__main__':
    main()
