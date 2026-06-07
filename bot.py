import asyncio
import logging
import os
from datetime import datetime
from typing import Dict
import aiohttp
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

APIS = {
    "phone": {
        "name": "📱 Phone Number",
        "endpoint": "https://masked-leak-check-api.vercel.app/api/check?query=",
        "example": "91876543210",
        "emoji": "📱"
    }
}

user_sessions = {}

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
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    await update.message.reply_text(stats_text, parse_mode='Markdown', reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data in APIS:
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
        await query.edit_message_text(text=text, parse_mode='Markdown', reply_markup=reply_markup)

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
        keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=help_text, parse_mode='Markdown', reply_markup=reply_markup)

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
        await query.edit_message_text(text=stats_text, parse_mode='Markdown', reply_markup=reply_markup)

    elif data == 'back':
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
        await query.edit_message_text(text=welcome_text, parse_mode='Markdown', reply_markup=reply_markup)

    elif data == 'cancel':
        user_sessions.pop(user_id, None)
        await query.edit_message_text(
            text="❌ *Operation cancelled.*\n\nUse /start to begin again.",
            parse_mode='Markdown'
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_input = update.message.text.strip()

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

    processing_msg = await update.message.reply_text(
        f"{api_info['emoji']} *Processing your request...*\n\n⏳ Please wait...",
        parse_mode='Markdown'
    )

    try:
        result = await perform_lookup(lookup_type, user_input)

        if result["success"]:
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
            formatted_data = json.dumps(result['data'], indent=2, ensure_ascii=False)
            full_message = success_text + f"```json\n{formatted_data}\n```"

            if len(full_message) > 4000:
                await processing_msg.delete()
                await update.message.reply_text(success_text, parse_mode='Markdown')
                for i in range(0, len(formatted_data), 3000):
                    chunk = formatted_data[i:i+3000]
                    await update.message.reply_text(f"```json\n{chunk}\n```", parse_mode='Markdown')
            else:
                await processing_msg.edit_text(full_message, parse_mode='Markdown')
        else:
            error_text = f"""
❌ *{api_info['name']} Lookup Failed*
━━━━━━━━━━━━━━━━━━━━
*🔍 Lookup Type:* {api_info['name']}
*📝 Value:* `{user_input}`
*📅 Timestamp:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
*⚡ Status:* HTTP {result.get('status_code', 'N/A')}

*❌ Error:* {result['error']}
"""
            await processing_msg.edit_text(error_text, parse_mode='Markdown')

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
        user_sessions[user_id] = lookup_type

    except Exception as e:
        logger.error(f"Error during lookup: {e}")
        await processing_msg.edit_text(
            f"❌ *An error occurred:*\n\n`{str(e)}`\n\nPlease try again.",
            parse_mode='Markdown'
        )

async def perform_lookup(lookup_type: str, value: str) -> Dict:
    api_info = APIS[lookup_type]
    url = api_info['endpoint'] + value
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    try:
                        data = await response.json()
                        return {"success": True, "data": data, "status_code": response.status}
                    except json.JSONDecodeError:
                        text = await response.text()
                        return {"success": False, "error": "Invalid JSON response", "status_code": response.status}
                else:
                    return {"success": False, "error": f"API returned status {response.status}", "status_code": response.status}
    except aiohttp.ClientError as e:
        return {"success": False, "error": f"Network error: {str(e)}"}
    except asyncio.TimeoutError:
        return {"success": False, "error": "Request timeout"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

def main() -> None:
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "8416527334:AAFgA1uQTT1RkNpuPLydsSmFJxUu3w4qY5Y")
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://number-info-3tw0.onrender.com")
    PORT = int(os.environ.get("PORT", 10000))

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is starting with webhook...")
    print(f"🌐 Webhook URL: {WEBHOOK_URL}")
    print("👨‍💻 Developer: @FroxtDevil")

    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"{WEBHOOK_URL}/webhook",
    )

if __name__ == '__main__':
    main()
