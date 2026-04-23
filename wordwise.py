import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8681456340:AAExgTjjBWWK9JqxpBEmJBre0SJdBsyyQK4"
AUTHOR = "Khaled M.M. Alrantisi"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def get_definition(word):
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word.lower().strip()}"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None
        data = response.json()
        if not data or not isinstance(data, list):
            return None
        entry = data[0]
        result = {
            'word': entry.get('word', word),
            'phonetic': entry.get('phonetic', ''),
            'meanings': []
        }
        for meaning in entry.get('meanings', [])[:3]:
            part = meaning.get('partOfSpeech', '')
            definitions = meaning.get('definitions', [])
            synonyms = meaning.get('synonyms', [])[:4]
            antonyms = meaning.get('antonyms', [])[:3]
            if definitions:
                d = definitions[0]
                result['meanings'].append({
                    'part': part,
                    'definition': d.get('definition', ''),
                    'example': d.get('example', ''),
                    'synonyms': synonyms,
                    'antonyms': antonyms
                })
        return result
    except Exception as e:
        logging.error(f"API error: {e}")
        return None

def format_response(data):
    word = data['word'].upper()
    phonetic = data['phonetic']

    msg = f"📖 *{word}*"
    if phonetic:
        msg += f"  `{phonetic}`"
    msg += "\n"
    msg += "─" * 30 + "\n\n"

    for i, meaning in enumerate(data['meanings'], 1):
        part = meaning['part'].upper()
        definition = meaning['definition']
        example = meaning['example']
        synonyms = meaning['synonyms']
        antonyms = meaning['antonyms']

        part_icons = {
            'NOUN': '🔷', 'VERB': '🔶', 'ADJECTIVE': '🟣',
            'ADVERB': '🟢', 'PREPOSITION': '🔵', 'CONJUNCTION': '🟡',
        }
        icon = part_icons.get(part, '📌')

        msg += f"{icon} *{part}*\n"
        msg += f"📝 {definition}\n"

        if example:
            msg += f"💬 _\"{example}\"_\n"

        if synonyms:
            syns = " • ".join(synonyms)
            msg += f"🔗 *Synonyms:* {syns}\n"

        if antonyms:
            ants = " • ".join(antonyms)
            msg += f"↔️ *Antonyms:* {ants}\n"

        msg += "\n"

    msg += "─" * 30 + "\n"
    msg += f"_WordWise by {AUTHOR}_"
    return msg

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "👋 *Welcome to WordWise!*\n\n"
        "I'm your personal dictionary bot.\n\n"
        "Simply send me *any English word* and I'll give you:\n"
        "📖 Definition\n"
        "💬 Example sentence\n"
        "🔗 Synonyms & Antonyms\n"
        "🔊 Phonetic pronunciation\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Try sending: *resilience* or *ephemeral*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"_Built by {AUTHOR}_"
    )
    await update.message.reply_text(welcome, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📚 *WordWise Help*\n\n"
        "Just send any English word!\n\n"
        "*Commands:*\n"
        "/start — Welcome message\n"
        "/help — Show this help\n"
        "/about — About WordWise\n\n"
        "*Examples:*\n"
        "• resilience\n"
        "• ephemeral\n"
        "• serendipity\n"
        "• ambiguous\n\n"
        f"_WordWise by {AUTHOR}_"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = (
        "ℹ️ *About WordWise*\n\n"
        "WordWise is an AI-powered dictionary bot "
        "that gives you instant word definitions, "
        "examples, synonyms and antonyms.\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👨‍💻 *Developer:* {AUTHOR}\n"
        "🔧 *Built with:* Python, Telegram Bot API\n"
        "📡 *Data:* Free Dictionary API\n"
        "📅 *Version:* 1.0.0\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "_Expanding your vocabulary, one word at a time._"
    )
    await update.message.reply_text(about_text, parse_mode='Markdown')

async def define_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = update.message.text.strip()

    if len(word.split()) > 3:
        await update.message.reply_text(
            "⚠️ Please send *one word* at a time for best results.",
            parse_mode='Markdown'
        )
        return

    thinking = await update.message.reply_text(
        f"🔍 Looking up *{word}*...", parse_mode='Markdown'
    )

    data = get_definition(word)

    if not data:
        await thinking.edit_text(
            f"❌ Sorry, I couldn't find a definition for *{word}*.\n\n"
            "Make sure it's spelled correctly and try again!",
            parse_mode='Markdown'
        )
        return

    response = format_response(data)
    await thinking.edit_text(response, parse_mode='Markdown')

async def error_handler(update, context):
    logging.error(f"Error: {context.error}")

def main():
    print("=" * 50)
    print(f"  WordWise Bot — by {AUTHOR}")
    print("  Starting up...")
    print("=" * 50)

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, define_word))
    app.add_error_handler(error_handler)

    print("  Bot is running! Open Telegram and search:")
    print("  @wordwise_khaled_bot")
    print("=" * 50)

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()