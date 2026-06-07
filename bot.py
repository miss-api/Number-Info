import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional
import aiohttp
import json
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# API endpoints - Only Phone Number lookup kept
APIS = {
    "phone": {
        "name": "📱 Phone Number",
        "endpoint": "https://masked-leak-check-api.vercel.app/api/check?query=",
        "example": "91876543210",
        "emoji": "📱"
    }
}

# User sessions to store lookup type
user_sessions = {}

# Bot credits
BOT_CREDITS = """
🤖 *Multi-Service Lookup Bot*
━━━━━━━━━━━━━━━━━━━━
🔍 *Features:*
• 📱 Phone Number Lookup

━━━━━━━━━━━━━━━━━━━━
👨‍💻 *Developer:* @FroxtDevil
💡 *Note:* This bot is education purpose only
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message with inline keyboard"""
    user = update.effective_user
    welcome_text = f"""
👋 Hello *{user.first_name}*! 

{BOT_CREDITS}

👇 *Select a lookup type below:*"""
    
    keyboard = [
        [InlineKeyboardButton("📱 Phone Number", callback_data='phone')],
        [InlineKeyboardButton("ℹ️ Help", callback_data='help'),
         InlineKeyboardButton("📊 Stats", callback_data='stats')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help information"""
    help_text = """
*🤖 How to use this bot:*

1️⃣ *Select a lookup type* from the menu
2️⃣ *Enter the value* when prompted
3️⃣ *Wait* while we process your request
4️⃣ *View* the results

*📝 Examples:*
• 📱 Phone: `9876543210`

*⚠️ Important:*
• This bot uses public APIs
• Results depend on API availability
• Privacy is important - use responsibly

*Commands:*
/start - Show main menu
/help - Show this help message
/stats - Show bot statistics
"""
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        help_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show bot statistics"""
    stats_text = """
*📊 Bot Statistics*
━━━━━━━━━━━━━━━━━━━━
*👥 Total Users:* Data unavailable
*🔍 Total Lookups:* Data unavailable
*📅 Uptime:* Since last restart
*⚡ API Status:* All endpoints available

*🔧 Supported Lookups:*
"""
    
    for api_id, api_info in APIS.items():
        stats_text += f"• {api_info['emoji']} {api_info['name']}\n"
    
    stats_text += f"\n{BOT_CREDITS}"
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        stats_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data in APIS:
        # Store lookup type for user
        user_sessions[user_id] = data
        api_info = APIS[data]
        
        text = f"""
{api_info['emoji']} *{api_info['name']} Lookup*
━━━━━━━━━━━━━━━━━━━━
*📝 Example:* `{api_info['example']}`

👇 *Please enter the value below:*
"""
        keyboard = [
            [InlineKeyboardButton("❌ Cancel", callback_data='cancel'),
             InlineKeyboardButton("🔙 Back", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif data == 'help':
        help_text = """
*🤖 How to use this bot:*

1️⃣ *Select a lookup type* from the menu
2️⃣ *Enter the value* when prompted
3️⃣ *Wait* while we process your request
4️⃣ *View* the results

*📝 Examples:*
• 📱 Phone: `9876543210`

*⚠️ Important:*
• This bot uses public APIs
• Results depend on API availability
• Privacy is important - use responsibly
"""
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=help_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif data == 'stats':
        stats_text = """
*📊 Bot Statistics*
━━━━━━━━━━━━━━━━━━━━
*👥 Total Users:* Data unavailable
*🔍 Total Lookups:* Data unavailable
*📅 Uptime:* Since last restart
*⚡ API Status:* All endpoints available

*🔧 Supported Lookups:*
"""
        
        for api_id, api_info in APIS.items():
            stats_text += f"• {api_info['emoji']} {api_info['name']}\n"
        
        stats_text += f"\n{BOT_CREDITS}"
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=stats_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif data == 'back':
        # Show main menu again
        user = query.from_user
        welcome_text = f"""
👋 Welcome back *{user.first_name}*! 

{BOT_CREDITS}

👇 *Select a lookup type below:*"""
        
        keyboard = [
            [InlineKeyboardButton("📱 Phone Number", callback_data='phone')],
            [InlineKeyboardButton("ℹ️ Help", callback_data='help'),
             InlineKeyboardButton("📊 Stats", callback_data='stats')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=welcome_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif data == 'cancel':
        # Clear user session
        user_sessions.pop(user_id, None)
        await query.edit_message_text(
            text="❌ *Operation cancelled.*\n\nUse /start to begin again.",
            parse_mode='Markdown'
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user messages for lookup values"""
    user_id = update.effective_user.id
    user_input = update.message.text.strip()
    
    # Check if user has an active lookup session
    if user_id not in user_sessions:
        keyboard = [[InlineKeyboardButton("📋 Main Menu", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "❌ *No active lookup session.*\n\nPlease select a lookup type first.",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return
    
    lookup_type = user_sessions[user_id]
    api_info = APIS[lookup_type]
    
    # Send processing message
    processing_msg = await update.message.reply_text(
        f"{api_info['emoji']} *Processing your request...*\n\n⏳ Please wait...",
        parse_mode='Markdown'
    )
    
    try:
        # Perform lookup
        result = await perform_lookup(lookup_type, user_input)
        
        if result["success"]:
            # Format success message
            success_text = f"""
✅ *{api_info['name']} Lookup Successful*
━━━━━━━━━━━━━━━━━━━━
*🔍 Lookup Type:* {api_info['name']}
*📝 Value:* `{user_input}`
*📅 Timestamp:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
*⚡ Status:* HTTP {result['status_code']}

━━━━━━━━━━━━━━━━━━━━
*📋 Results:*
"""
            
            # Format JSON data
            formatted_data = json.dumps(result['data'], indent=2, ensure_ascii=False)
            
            # Split message if too long
            full_message = success_text + f"```json\n{formatted_data}\n```"
            
            if len(full_message) > 4000:
                # Send results in multiple messages
                await processing_msg.delete()
                
                # Send success header
                await update.message.reply_text(
                    success_text,
                    parse_mode='Markdown'
                )
                
                # Send data in chunks
                for i in range(0, len(formatted_data), 3000):
                    chunk = formatted_data[i:i+3000]
                    await update.message.reply_text(
                        f"```json\n{chunk}\n```",
                        parse_mode='Markdown'
                    )
            else:
                await processing_msg.edit_text(
                    full_message,
                    parse_mode='Markdown'
                )
        else:
            # Format error message
            error_text = f"""
❌ *{api_info['name']} Lookup Failed*
━━━━━━━━━━━━━━━━━━━━
*🔍 Lookup Type:* {api_info['name']}
*📝 Value:* `{user_input}`
*📅 Timestamp:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
*⚡ Status:* HTTP {result.get('status_code', 'N/A')}

*❌ Error:* {result['error']}
"""
            await processing_msg.edit_text(
                error_text,
                parse_mode='Markdown'
            )
        
        # Add action buttons after results
        keyboard = [
            [InlineKeyboardButton("🔄 New Lookup", callback_data='back'),
             InlineKeyboardButton("📊 Another Value", callback_data=lookup_type)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "👇 *What would you like to do next?*",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
        # Keep session active for same lookup type
        user_sessions[user_id] = lookup_type
        
    except Exception as e:
        logger.error(f"Error during lookup: {e}")
        await processing_msg.edit_text(
            f"❌ *An error occurred:*\n\n`{str(e)}`\n\nPlease try again.",
            parse_mode='Markdown'
        )

async def perform_lookup(lookup_type: str, value: str) -> Dict:
    """Perform API lookup asynchronously"""
    api_info = APIS[lookup_type]
    url = api_info['endpoint'] + value
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    try:
                        data = await response.json()
                        return {
                            "success": True,
                            "data": data,
                            "status_code": response.status,
                            "lookup_type": api_info['name'],
                            "value": value
                        }
                    except json.JSONDecodeError:
                        text = await response.text()
                        return {
                            "success": False,
                            "error": "Invalid JSON response",
                            "raw_response": text[:200],
                            "status_code": response.status
                        }
                else:
                    return {
                        "success": False,
                        "error": f"API returned status {response.status}",
                        "status_code": response.status
                    }
    except aiohttp.ClientError as e:
        return {
            "success": False,
            "error": f"Network error: {str(e)}"
        }
    except asyncio.TimeoutError:
        return {
            "success": False,
            "error": "Request timeout"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }

def main() -> None:
    """Start the bot"""
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token
    BOT_TOKEN = "8416527334:AAFgA1uQTT1RkNpuPLydsSmFJxUu3w4qY5Y"
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot
    print("🤖 Bot is starting...")
    print("👨‍💻 Developer: @FroxtDevil")
    print("🔗 Bot Token:", BOT_TOKEN[:10] + "..." if len(BOT_TOKEN) > 10 else BOT_TOKEN)
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
