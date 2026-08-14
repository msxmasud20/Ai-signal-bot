import os
import asyncio
import aiohttp
import json
import random
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ============================================================
# লগিং সেটআপ
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================
# এনভায়রনমেন্ট ভেরিয়েবল চেক
# ============================================================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN environment variable is not set!")
    raise ValueError("BOT_TOKEN is required")

if not CHAT_ID:
    logger.error("❌ CHAT_ID environment variable is not set!")
    raise ValueError("CHAT_ID is required")

logger.info("=" * 50)
logger.info("  🅼🅰🆂🆄🅳 🅰🅸 - 🅱🅾🆃")
logger.info("=" * 50)
logger.info(f"✅ BOT_TOKEN: {BOT_TOKEN[:10]}...")
logger.info(f"✅ CHAT_ID: {CHAT_ID}")

# ============================================================
# কনফিগারেশন
# ============================================================
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json?pageNo=1&pageSize=10"

# ============================================================
# গ্লোবাল ভেরিয়েবল
# ============================================================
is_running = False
last_signal = None
last_period = None
engine = None

# ============================================================
# প্রেডিকশন ইঞ্জিন
# ============================================================
class PredictionEngine:
    def __init__(self):
        self.history = []
        self.last_issue = None
        self.current_prediction = None
        self.trade_history = []
        self.win_count = 0
        self.loss_count = 0
        self.total_trade = 0
        self.accuracy = 0
        self.last_10_numbers = []

    def analyze_trend(self, numbers):
        if not numbers or len(numbers) < 3:
            return {'trend': 'neutral', 'confidence': 50}
        
        bigs = sum(1 for n in numbers if n >= 5)
        smalls = len(numbers) - bigs
        
        last_three = numbers[-3:] if len(numbers) >= 3 else numbers
        all_big = all(n >= 5 for n in last_three)
        all_small = all(n < 5 for n in last_three)
        
        alternating = True
        if len(last_three) >= 3:
            for i in range(1, len(last_three)):
                if (last_three[i-1] >= 5) == (last_three[i] >= 5):
                    alternating = False
                    break
        
        big_ratio = bigs / len(numbers) if len(numbers) > 0 else 0
        confidence = min(95, round((abs(big_ratio - 0.5) * 2) * 100))
        
        trend = 'neutral'
        if big_ratio > 0.6:
            trend = 'BIG'
        elif big_ratio < 0.4:
            trend = 'SMALL'
        elif all_big:
            trend = 'BIG'
            confidence = min(95, confidence + 10)
        elif all_small:
            trend = 'SMALL'
            confidence = min(95, confidence + 10)
        elif alternating and len(last_three) >= 3:
            last = last_three[-1]
            trend = 'SMALL' if last >= 5 else 'BIG'
            confidence = min(90, confidence + 10)
        
        return {'trend': trend, 'confidence': max(55, confidence)}

    def predict_next(self, numbers):
        if not numbers:
            num = random.randint(0, 9)
            return {
                'number': num,
                'bs': 'BIG' if num >= 5 else 'SMALL',
                'confidence': 60
            }
        
        analysis = self.analyze_trend(numbers)
        confidence = analysis['confidence']
        
        if analysis['trend'] == 'BIG':
            predicted_num = random.randint(5, 9)
            confidence = min(95, confidence + 5)
        elif analysis['trend'] == 'SMALL':
            predicted_num = random.randint(0, 4)
            confidence = min(95, confidence + 5)
        else:
            avg = sum(numbers) / len(numbers) if numbers else 0
            if avg > 4.5:
                predicted_num = random.randint(4, 9)
                confidence = 65
            else:
                predicted_num = random.randint(0, 5)
                confidence = 65
        
        if random.random() < 0.05 and len(numbers) > 5:
            predicted_num = random.randint(0, 4) if predicted_num >= 5 else random.randint(5, 9)
            confidence = max(50, confidence - 10)
        
        return {
            'number': predicted_num,
            'bs': 'BIG' if predicted_num >= 5 else 'SMALL',
            'confidence': round(confidence)
        }

    async def fetch_data(self):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(API_URL, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        try:
                            data = await response.json()
                        except:
                            return None
                            
                        if data and data.get('data') and data['data'].get('list'):
                            items = data['data']['list']
                            numbers = []
                            for item in items:
                                if 'number' in item:
                                    try:
                                        numbers.append(int(item['number']))
                                    except:
                                        pass
                            
                            if numbers:
                                latest_issue = items[0].get('issueNumber', '')
                                if latest_issue != self.last_issue:
                                    self.last_issue = latest_issue
                                    self.history = numbers[:30]
                                    self.last_10_numbers = numbers[:10]
                                    
                                    prediction = self.predict_next(self.history)
                                    
                                    big_count = sum(1 for n in self.last_10_numbers if n >= 5)
                                    small_count = len(self.last_10_numbers) - big_count
                                    
                                    self.current_prediction = {
                                        'period': latest_issue,
                                        'prediction': prediction['bs'],
                                        'number': prediction['number'],
                                        'confidence': prediction['confidence'],
                                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                                        'big_count': big_count,
                                        'small_count': small_count,
                                        'history': self.last_10_numbers[:10]
                                    }
                                    return self.current_prediction
                    return None
        except Exception as e:
            logger.error(f"API Error: {e}")
            return None

# ============================================================
# হেল্পার ফাংশন
# ============================================================
def get_history_dots(numbers):
    if not numbers:
        return "---"
    dots = []
    for num in numbers[:10]:
        dots.append("🟢" if num >= 5 else "🔴")
    return ' '.join(dots)

def get_confidence_bar(confidence):
    bar_length = 12
    filled = int((confidence / 100) * bar_length)
    return "█" * filled + "░" * (bar_length - filled)

def get_last_trades():
    if not engine or not engine.trade_history:
        return "❌ কোনো ট্রেড নেই"
    
    trades = engine.trade_history[-5:]
    lines = []
    for t in trades:
        icon = "✅" if t['result'] == "Win" else "❌"
        lines.append(f"{icon} {t['prediction']} → {t['actual']} ({t['number']})")
    return "\n".join(lines)

# ============================================================
# বট হ্যান্ডলার
# ============================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 সিগন্যাল চালু", callback_data="start_signal")],
        [InlineKeyboardButton("⏹️ সিগন্যাল বন্ধ", callback_data="stop_signal")],
        [InlineKeyboardButton("📊 পরিসংখ্যান", callback_data="stats")],
        [InlineKeyboardButton("📡 লাইভ সিগন্যাল", callback_data="live")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    status = "🟢 চলমান" if is_running else "🔴 বন্ধ"
    
    msg = f"""
🅼🅰🆂🆄🅳 🅰🅸 - 🆁🅸🅴🅻 🅿🆁🅴🅳🅸🅲🆃🅾🆁
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 *স্ট্যাটাস:* {status}
🏆 *উইন:* {engine.win_count if engine else 0}
💔 *লস:* {engine.loss_count if engine else 0}
📈 *ট্রেড:* {engine.total_trade if engine else 0}
🎯 *একুরেসি:* {engine.accuracy if engine else 0}%

📌 *লাস্ট ১০:* {get_history_dots(engine.last_10_numbers) if engine else '---'}

💡 নিচের বাটন ব্যবহার করুন
    """
    await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_running
    query = update.callback_query
    await query.answer()
    
    if query.data == "start_signal":
        if not is_running:
            is_running = True
            asyncio.create_task(signal_loop(context.bot))
            await query.edit_message_text("✅ সিগন্যাল চালু হয়েছে! প্রতি ৩০ সেকেন্ডে আপডেট আসবে।")
        else:
            await query.edit_message_text("⚠️ সিগন্যাল ইতিমধ্যে চালু আছে!")
    
    elif query.data == "stop_signal":
        is_running = False
        await query.edit_message_text("🔴 সিগন্যাল বন্ধ করা হয়েছে।")
    
    elif query.data == "stats":
        if not engine:
            await query.edit_message_text("⏳ ইঞ্জিন প্রস্তুত হচ্ছে...")
            return
        
        stats = f"""
📊 *পরিসংখ্যান*
━━━━━━━━━━━━━━━━━━━

• মোট ট্রেড: {engine.total_trade}
• 🏆 উইন: {engine.win_count}
• 💔 লস: {engine.loss_count}
• 🎯 একুরেসি: {engine.accuracy}%
• 📡 স্ট্যাটাস: {'🟢 চলমান' if is_running else '🔴 বন্ধ'}

📌 *লাস্ট ১০:* {get_history_dots(engine.last_10_numbers)}

📈 *লাস্ট ৫ ট্রেড:*
{get_last_trades()}
        """
        await query.edit_message_text(stats, parse_mode='Markdown')
    
    elif query.data == "live":
        if engine and engine.current_prediction:
            p = engine.current_prediction
            bar = get_confidence_bar(p['confidence'])
            dots = get_history_dots(p.get('history', []))
            
            signal = f"""
📡 *লাইভ সিগন্যাল*
━━━━━━━━━━━━━━━━━━━

🔢 পিরিয়ড: `{p['period'][-6:]}`
🎯 সিগন্যাল: {'🟢' if p['prediction'] == 'BIG' else '🔴'} *{p['prediction']}*
🔢 নম্বর: `{p['number']}`
📊 কনফিডেন্স: {p['confidence']}% {bar}

📈 *ট্রেন্ড অ্যানালাইসিস:*
• লাস্ট ১০: {dots}
• BIG: {p.get('big_count', 0)} | SMALL: {p.get('small_count', 0)}

⏱️ সময়: {p['timestamp']}
━━━━━━━━━━━━━━━━━━━
            """
            await query.edit_message_text(signal, parse_mode='Markdown')
        else:
            await query.edit_message_text("⏳ কোনো সিগন্যাল নেই, অপেক্ষা করুন...")

async def send_signal(bot, prediction):
    if not prediction or not engine:
        return
    
    engine.total_trade += 1
    
    bar = get_confidence_bar(prediction['confidence'])
    dots = get_history_dots(prediction.get('history', []))
    bs_emoji = "🟢" if prediction['prediction'] == "BIG" else "🔴"
    
    msg = f"""
🅼🅰🆂🆄🅳 🅰🅸 - 🆁🅸🅴🅻 🅿🆁🅴🅳🅸🅲🆃
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔢 *পিরিয়ড:* `{prediction['period'][-6:]}`
🎯 *সিগন্যাল:* {bs_emoji} *{prediction['prediction']}*
🔢 *প্রেডিক্টেড নম্বর:* `{prediction['number']}`
📊 *কনফিডেন্স:* {prediction['confidence']}% {bar}

📈 *ট্রেন্ড অ্যানালাইসিস:*
• লাস্ট ১০: {dots}
• BIG: {prediction.get('big_count', 0)} | SMALL: {prediction.get('small_count', 0)}

📊 *পরিসংখ্যান:*
🏆 উইন: {engine.win_count} | 💔 লস: {engine.loss_count}
🎯 একুরেসি: {engine.accuracy}% | 📈 ট্রেড #{engine.total_trade}

⏱️ {prediction['timestamp']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🅿🅾🆆🅴🆁🅴🅳 🅱🆈 🅼🅰🆂🆄🅳 🅰🅸
    """
    
    try:
        await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')
        logger.info(f"✅ Signal sent: {prediction['prediction']}")
    except Exception as e:
        logger.error(f"❌ Failed to send: {e}")

async def check_result(bot, prediction, actual_number):
    global engine
    
    if not prediction or actual_number is None or not engine:
        return
    
    actual_bs = "BIG" if actual_number >= 5 else "SMALL"
    is_win = prediction['prediction'] == actual_bs
    
    if is_win:
        engine.win_count += 1
        result_text = "✅ *উইন!* 🏆"
    else:
        engine.loss_count += 1
        result_text = "❌ *লস!* 💔"
    
    if engine.total_trade > 0:
        engine.accuracy = round((engine.win_count / engine.total_trade) * 100, 1)
    
    engine.trade_history.append({
        'prediction': prediction['prediction'],
        'actual': actual_bs,
        'number': actual_number,
        'result': 'Win' if is_win else 'Loss'
    })
    if len(engine.trade_history) > 50:
        engine.trade_history.pop(0)
    
    msg = f"""
📊 *ট্রেড আপডেট*
━━━━━━━━━━━━━━━━━━━

📌 পিরিয়ড: `{prediction['period'][-6:]}`
🔮 পূর্বাভাস: {prediction['prediction']}
🎯 রিয়েল: {actual_bs} (`{actual_number}`)
📈 ফলাফল: {result_text}

📊 *আপডেটেড স্ট্যাটস:*
🏆 উইন: {engine.win_count}
💔 লস: {engine.loss_count}
🎯 একুরেসি: {engine.accuracy}%
📈 ট্রেড #{engine.total_trade}

⏱️ {datetime.now().strftime('%H:%M:%S')}
━━━━━━━━━━━━━━━━━━━
    """
    
    try:
        await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Result update failed: {e}")

async def signal_loop(bot):
    global is_running, last_signal, last_period, engine
    
    logger.info("🔄 Signal loop started")
    
    while is_running:
        try:
            if engine:
                prediction = await engine.fetch_data()
                
                if prediction and prediction['period'] != last_period:
                    if last_period and last_signal:
                        if engine.history:
                            real_num = engine.history[0] if engine.history else None
                            if real_num is not None:
                                await check_result(bot, last_signal, real_num)
                    
                    last_period = prediction['period']
                    last_signal = prediction
                    await send_signal(bot, prediction)
                    logger.info(f"📡 New signal: {prediction['prediction']}")
            
            await asyncio.sleep(30)
            
        except Exception as e:
            logger.error(f"Loop error: {e}")
            await asyncio.sleep(30)

async def predict_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if engine:
        prediction = await engine.fetch_data()
        if prediction:
            await send_signal(context.bot, prediction)
        else:
            await update.message.reply_text("⏳ সিগন্যাল তৈরি হচ্ছে...")
    else:
        await update.message.reply_text("⏳ ইঞ্জিন প্রস্তুত হচ্ছে...")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not engine:
        await update.message.reply_text("⏳ ডাটা সংগ্রহ করছি...")
        return
    
    stats = f"""
📊 *পরিসংখ্যান*
━━━━━━━━━━━━━━━━━━━

• মোট ট্রেড: {engine.total_trade}
• 🏆 উইন: {engine.win_count}
• 💔 লস: {engine.loss_count}
• 🎯 একুরেসি: {engine.accuracy}%
• 📡 স্ট্যাটাস: {'🟢 চলমান' if is_running else '🔴 বন্ধ'}

📌 *লাস্ট ১০:* {get_history_dots(engine.last_10_numbers)}

📈 *লাস্ট ৫ ট্রেড:*
{get_last_trades()}
    """
    await update.message.reply_text(stats, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🤖 *Masud AI Bot - সাহায্য*

📌 *কমান্ডসমূহ:*
/start - বট চালু করুন
/predict - তাৎক্ষণিক সিগন্যাল
/stats - পরিসংখ্যান দেখুন
/help - এই মেসেজ দেখান

📊 *ফিচারসমূহ:*
✅ ৩০ সেকেন্ডে অটো সিগন্যাল
✅ BIG/SMALL প্রেডিক্ট
✅ উইন/লস ট্র্যাকার
✅ লাইভ স্ট্যাটাস

⚡ *পাওয়ার্ড বাই Masud AI*
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

# ============================================================
# বট চালু হওয়ার সাথে সাথে সিগন্যাল শুরু
# ============================================================
async def start_signal_automatically(application):
    global is_running, engine
    
    logger.info("🚀 Auto-starting signal system...")
    
    engine = PredictionEngine()
    await engine.fetch_data()
    
    is_running = True
    asyncio.create_task(signal_loop(application.bot))
    
    logger.info("✅ Signal system is now running automatically!")

# ============================================================
# মেইন ফাংশন
# ============================================================
def main():
    global engine
    
    # বড় করে MASUD লেখা
    print("=" * 60)
    print("  ███╗   ███╗ █████╗ ███████╗██╗   ██╗██████╗ ")
    print("  ████╗ ████║██╔══██╗██╔════╝██║   ██║██╔══██╗")
    print("  ██╔████╔██║███████║███████╗██║   ██║██████╔╝")
    print("  ██║╚██╔╝██║██╔══██║╚════██║██║   ██║██╔══██╗")
    print("  ██║ ╚═╝ ██║██║  ██║███████║╚██████╔╝██║  ██║")
    print("  ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝")
    print("=" * 60)
    print("  🤖 Masud AI - Premium Prediction Bot")
    print("  🚀 Version 2.0 - Ready for Action!")
    print("=" * 60)
    
    logger.info("🤖 Starting Masud AI Bot...")
    logger.info(f"📡 Bot Token: {BOT_TOKEN[:10]}...")
    logger.info(f"📢 Chat ID: {CHAT_ID}")
    
    try:
        # বট তৈরি
        application = Application.builder().token(BOT_TOKEN).build()
        
        # ইঞ্জিন তৈরি
        engine = PredictionEngine()
        
        # হ্যান্ডলার যোগ
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("predict", predict_command))
        application.add_handler(CommandHandler("stats", stats_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CallbackQueryHandler(button_handler))
        
        # বট চালু হওয়ার সাথে সাথে সিগন্যাল শুরু
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_signal_automatically(application))
        
        logger.info("✅ Bot is ready and running!")
        print("=" * 60)
        print("  ✅ MASUD AI BOT IS NOW RUNNING!")
        print("  📡 Waiting for signals...")
        print("=" * 60)
        
        # বট চালু
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Failed to start: {e}")
        raise

if __name__ == "__main__":
    main()
