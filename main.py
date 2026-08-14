import os
import asyncio
import aiohttp
import json
import random
import logging
from datetime import datetime

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

# ============================================================
# BIG ASCII ART - MASUD
# ============================================================
def print_banner():
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ███╗   ███╗ █████╗ ███████╗██╗   ██╗██████╗              ║
║   ████╗ ████║██╔══██╗██╔════╝██║   ██║██╔══██╗             ║
║   ██╔████╔██║███████║███████╗██║   ██║██████╔╝             ║
║   ██║╚██╔╝██║██╔══██║╚════██║██║   ██║██╔══██╗             ║
║   ██║ ╚═╝ ██║██║  ██║███████║╚██████╔╝██║  ██║             ║
║   ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝             ║
║                                                              ║
║         🤖 MASUD AI - PREMIUM PREDICTION BOT                ║
║         🚀 VERSION 3.0 - FIXED SIGNAL ISSUE                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

# ============================================================
# টেলিগ্রাম API ফাংশন
# ============================================================
async def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=10) as response:
                if response.status == 200:
                    logger.info("✅ Message sent successfully")
                    return True
                return False
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return False

async def send_telegram_keyboard(message, keyboard):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    reply_markup = {"inline_keyboard": keyboard}
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "reply_markup": json.dumps(reply_markup)
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=10) as response:
                return response.status == 200
    except:
        return False

async def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=35) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("result", [])
                return []
    except:
        return []

async def answer_callback(callback_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
    payload = {
        "callback_query_id": callback_id,
        "text": text,
        "show_alert": False
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=10) as response:
                return response.status == 200
    except:
        return False

async def edit_message_text(chat_id, message_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if keyboard:
        reply_markup = {"inline_keyboard": keyboard}
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=10) as response:
                return response.status == 200
    except:
        return False

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
offset = None
signal_count = 0

# ============================================================
# প্রেডিকশন ইঞ্জিন - আপনার HTML ফাইলের মতো
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
        self.big_count = 0
        self.small_count = 0
        self.consecutive_big = 0
        self.consecutive_small = 0

    # ============================================================
    # আপনার HTML ফাইলের অ্যালগরিদম - হুবহু অনুকরণ
    # ============================================================
    def analyze_trend(self, numbers):
        """আপনার ফাইলের analyzeTrend ফাংশনের মতো"""
        if not numbers or len(numbers) < 3:
            return {'trend': 'neutral', 'confidence': 50}
        
        # BIG/SMALL কাউন্ট
        bigs = sum(1 for n in numbers if n >= 5)
        smalls = len(numbers) - bigs
        
        # কনসিকিউটিভ প্যাটার্ন চেক
        last_three = numbers[-3:] if len(numbers) >= 3 else numbers
        all_big = all(n >= 5 for n in last_three)
        all_small = all(n < 5 for n in last_three)
        
        # অল্টারনেটিং প্যাটার্ন
        alternating = True
        if len(last_three) >= 3:
            for i in range(1, len(last_three)):
                if (last_three[i-1] >= 5) == (last_three[i] >= 5):
                    alternating = False
                    break
        
        # কনফিডেন্স ক্যালকুলেশন
        big_ratio = bigs / len(numbers) if len(numbers) > 0 else 0
        confidence = min(95, round((abs(big_ratio - 0.5) * 2) * 100))
        
        # ট্রেন্ড ডিটেকশন - আপনার ফাইলের মতো
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
            # অল্টারনেটিং হলে আগের ট্রেন্ড অনুসরণ
            last = last_three[-1]
            trend = 'SMALL' if last >= 5 else 'BIG'
            confidence = min(90, confidence + 10)
        
        return {'trend': trend, 'confidence': max(55, confidence)}

    def predict_next(self, numbers):
        """আপনার ফাইলের predictNextNumber ফাংশনের মতো"""
        if not numbers:
            num = random.randint(0, 9)
            return {
                'number': num,
                'bs': 'BIG' if num >= 5 else 'SMALL',
                'confidence': 60
            }
        
        # ট্রেন্ড অ্যানালাইসিস
        analysis = self.analyze_trend(numbers)
        confidence = analysis['confidence']
        
        # স্মার্ট প্রেডিক্ট - আপনার ফাইলের মতো
        if analysis['trend'] == 'BIG':
            predicted_num = random.randint(5, 9)
            confidence = min(95, confidence + 5)
        elif analysis['trend'] == 'SMALL':
            predicted_num = random.randint(0, 4)
            confidence = min(95, confidence + 5)
        else:
            # নিউট্রাল - ডিস্ট্রিবিউশন অনুযায়ী
            avg = sum(numbers) / len(numbers) if numbers else 0
            if avg > 4.5:
                predicted_num = random.randint(4, 9)
                confidence = 65
            else:
                predicted_num = random.randint(0, 5)
                confidence = 65
        
        # ৫% চান্স রিভার্স - আপনার ফাইলের মতো
        if random.random() < 0.05 and len(numbers) > 5:
            predicted_num = random.randint(0, 4) if predicted_num >= 5 else random.randint(5, 9)
            confidence = max(50, confidence - 10)
        
        return {
            'number': predicted_num,
            'bs': 'BIG' if predicted_num >= 5 else 'SMALL',
            'confidence': round(confidence)
        }

    async def fetch_data(self):
        """API থেকে ডাটা সংগ্রহ - আপনার ফাইলের মতো"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(API_URL, headers=headers, timeout=15) as response:
                    logger.info(f"📡 API Response Status: {response.status}")
                    
                    if response.status == 200:
                        try:
                            data = await response.json()
                            logger.info(f"📊 API Data: {json.dumps(data, indent=2)[:500]}")
                        except Exception as e:
                            logger.error(f"JSON parse error: {e}")
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
                            
                            logger.info(f"📊 Numbers from API: {numbers[:10]}")
                            
                            if numbers:
                                latest_issue = items[0].get('issueNumber', '')
                                logger.info(f"📌 Latest Issue: {latest_issue}")
                                logger.info(f"📌 Last Issue: {self.last_issue}")
                                
                                if latest_issue != self.last_issue:
                                    self.last_issue = latest_issue
                                    self.history = numbers[:30]
                                    self.last_10_numbers = numbers[:10]
                                    
                                    # BIG/SMALL কাউন্ট আপডেট
                                    self.big_count = sum(1 for n in self.last_10_numbers if n >= 5)
                                    self.small_count = len(self.last_10_numbers) - self.big_count
                                    
                                    # কনসিকিউটিভ চেক
                                    self.consecutive_big = 0
                                    self.consecutive_small = 0
                                    for n in reversed(self.last_10_numbers):
                                        if n >= 5:
                                            if self.consecutive_small > 0:
                                                break
                                            self.consecutive_big += 1
                                        else:
                                            if self.consecutive_big > 0:
                                                break
                                            self.consecutive_small += 1
                                    
                                    # প্রেডিক্ট করুন
                                    prediction = self.predict_next(self.history)
                                    
                                    self.current_prediction = {
                                        'period': latest_issue,
                                        'prediction': prediction['bs'],
                                        'number': prediction['number'],
                                        'confidence': prediction['confidence'],
                                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                                        'big_count': self.big_count,
                                        'small_count': self.small_count,
                                        'consecutive_big': self.consecutive_big,
                                        'consecutive_small': self.consecutive_small,
                                        'history': self.last_10_numbers[:10]
                                    }
                                    
                                    logger.info(f"🎯 NEW PREDICTION: {self.current_prediction}")
                                    return self.current_prediction
                                else:
                                    logger.info("⏳ No new issue, waiting...")
                    else:
                        logger.warning(f"API status: {response.status}")
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

def get_start_keyboard():
    return [
        [
            {"text": "🚀 সিগন্যাল চালু", "callback_data": "start_signal"},
            {"text": "⏹️ সিগন্যাল বন্ধ", "callback_data": "stop_signal"}
        ],
        [
            {"text": "📊 পরিসংখ্যান", "callback_data": "stats"},
            {"text": "📡 লাইভ সিগন্যাল", "callback_data": "live"}
        ]
    ]

# ============================================================
# সিগন্যাল ফাংশন
# ============================================================
async def send_signal(prediction):
    """আপনার HTML ফাইলের মতো স্টাইলে সিগন্যাল পাঠায়"""
    global engine, signal_count
    
    if not prediction or not engine:
        logger.error("❌ Cannot send signal: prediction or engine is None")
        return
    
    signal_count += 1
    engine.total_trade += 1
    
    bar = get_confidence_bar(prediction['confidence'])
    dots = get_history_dots(prediction.get('history', []))
    bs_emoji = "🟢" if prediction['prediction'] == "BIG" else "🔴"
    
    # আপনার HTML ফাইলের মতো স্টাইল
    msg = f"""
🎯 *MASUD AI - রিয়েল প্রেডিক্ট*
━━━━━━━━━━━━━━━━━━━━━━

🔢 *পিরিয়ড:* `{prediction['period'][-6:]}`
🎯 *সিগন্যাল:* {bs_emoji} *{prediction['prediction']}*
🔢 *প্রেডিক্টেড নম্বর:* `{prediction['number']}`
📊 *কনফিডেন্স:* {prediction['confidence']}% {bar}

📈 *ট্রেন্ড অ্যানালাইসিস:*
• লাস্ট ১০: {dots}
• BIG: {prediction.get('big_count', 0)} | SMALL: {prediction.get('small_count', 0)}
• কনসিকিউটিভ BIG: {prediction.get('consecutive_big', 0)}
• কনসিকিউটিভ SMALL: {prediction.get('consecutive_small', 0)}

📊 *পরিসংখ্যান:*
🏆 উইন: {engine.win_count} | 💔 লস: {engine.loss_count}
🎯 একুরেসি: {engine.accuracy}% | 📈 ট্রেড #{engine.total_trade}

⏱️ {prediction['timestamp']}
━━━━━━━━━━━━━━━━━━━━━━
🅿🅾🆆🅴🆁🅴🅳 🅱🆈 🅼🅰🆂🆄🅳 🅰🅸
    """
    
    logger.info(f"📤 SENDING SIGNAL #{signal_count}: {prediction['prediction']}")
    await send_telegram_message(msg)
    logger.info(f"✅ Signal #{signal_count} sent successfully")

async def check_result(prediction, actual_number):
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
    
    await send_telegram_message(msg)

# ============================================================
# সিগন্যাল লুপ - ফিক্সড
# ============================================================
async def signal_loop():
    global is_running, last_signal, last_period, engine, signal_count
    
    logger.info("🔄 Signal loop started - waiting for signals...")
    
    while is_running:
        try:
            if engine:
                logger.info("🔍 Fetching data from API...")
                prediction = await engine.fetch_data()
                
                if prediction:
                    logger.info(f"📊 Got prediction: {prediction}")
                    
                    if prediction['period'] != last_period:
                        logger.info(f"🆕 New period detected: {prediction['period']}")
                        
                        # আগের ট্রেডের রেজাল্ট চেক
                        if last_period and last_signal:
                            if engine.history:
                                real_num = engine.history[0] if engine.history else None
                                if real_num is not None:
                                    logger.info(f"📊 Checking result for period {last_period}")
                                    await check_result(last_signal, real_num)
                        
                        # নতুন সিগন্যাল
                        last_period = prediction['period']
                        last_signal = prediction
                        
                        # সিগন্যাল পাঠান
                        logger.info(f"📤 Sending signal for period {prediction['period']}")
                        await send_signal(prediction)
                    else:
                        logger.info(f"⏳ Same period {prediction['period']}, waiting...")
                else:
                    logger.info("⏳ No prediction available, waiting...")
            
            await asyncio.sleep(30)
            
        except Exception as e:
            logger.error(f"❌ Loop error: {e}")
            await asyncio.sleep(30)

# ============================================================
# মেসেজ হ্যান্ডলার
# ============================================================
async def handle_message(message):
    global is_running, engine
    
    text = message.get('text', '')
    chat_id = message['chat']['id']
    
    if str(chat_id) != str(CHAT_ID):
        return
    
    if text == '/start':
        status = "🟢 চলমান" if is_running else "🔴 বন্ধ"
        msg = f"""
🤖 *MASUD AI - রিয়েল প্রেডিক্টর*
━━━━━━━━━━━━━━━━━━━━━━

📊 *স্ট্যাটাস:* {status}
🏆 *উইন:* {engine.win_count if engine else 0}
💔 *লস:* {engine.loss_count if engine else 0}
📈 *ট্রেড:* {engine.total_trade if engine else 0}
🎯 *একুরেসি:* {engine.accuracy if engine else 0}%

📌 *লাস্ট ১০:* {get_history_dots(engine.last_10_numbers) if engine else '---'}

💡 নিচের বাটন ব্যবহার করুন
        """
        await send_telegram_keyboard(msg, get_start_keyboard())
    
    elif text == '/predict':
        if engine:
            prediction = await engine.fetch_data()
            if prediction:
                await send_signal(prediction)
            else:
                await send_telegram_message("⏳ সিগন্যাল তৈরি হচ্ছে...")
        else:
            await send_telegram_message("⏳ ইঞ্জিন প্রস্তুত হচ্ছে...")
    
    elif text == '/stats':
        if not engine:
            await send_telegram_message("⏳ ডাটা সংগ্রহ করছি...")
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
        await send_telegram_message(stats)
    
    elif text == '/help':
        help_text = """
🤖 *MASUD AI Bot - সাহায্য*

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

⚡ *পাওয়ার্ড বাই MASUD AI*
        """
        await send_telegram_message(help_text)

# ============================================================
# Callback হ্যান্ডলার
# ============================================================
async def handle_callback(callback):
    global is_running, engine
    
    data = callback['data']
    callback_id = callback['id']
    message = callback.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    message_id = message.get('message_id')
    
    if data == "start_signal":
        if not is_running:
            is_running = True
            asyncio.create_task(signal_loop())
            await answer_callback(callback_id, "✅ সিগন্যাল চালু হয়েছে!")
            await edit_message_text(chat_id, message_id, "✅ সিগন্যাল চালু হয়েছে! প্রতি ৩০ সেকেন্ডে আপডেট আসবে।")
        else:
            await answer_callback(callback_id, "⚠️ সিগন্যাল ইতিমধ্যে চালু আছে!")
    
    elif data == "stop_signal":
        is_running = False
        await answer_callback(callback_id, "🔴 সিগন্যাল বন্ধ করা হয়েছে!")
        await edit_message_text(chat_id, message_id, "🔴 সিগন্যাল বন্ধ করা হয়েছে।")
    
    elif data == "stats":
        if not engine:
            await answer_callback(callback_id, "⏳ ইঞ্জিন প্রস্তুত হচ্ছে...")
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
        await answer_callback(callback_id, "📊 পরিসংখ্যান দেখানো হচ্ছে...")
        await edit_message_text(chat_id, message_id, stats)
    
    elif data == "live":
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
            await answer_callback(callback_id, "📡 লাইভ সিগন্যাল দেখানো হচ্ছে...")
            await edit_message_text(chat_id, message_id, signal)
        else:
            await answer_callback(callback_id, "⏳ কোনো সিগন্যাল নেই")

# ============================================================
# মেইন লুপ
# ============================================================
async def main_loop():
    global offset, engine, is_running
    
    logger.info("🔄 Starting main loop...")
    
    while True:
        try:
            updates = await get_updates(offset)
            
            for update in updates:
                offset = update['update_id'] + 1
                
                if 'message' in update:
                    await handle_message(update['message'])
                
                if 'callback_query' in update:
                    await handle_callback(update['callback_query'])
            
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            await asyncio.sleep(5)

# ============================================================
# বট চালু
# ============================================================
async def start_bot():
    global engine, is_running
    
    print_banner()
    logger.info("🤖 Starting Masud AI Bot...")
    logger.info(f"📡 Bot Token: {BOT_TOKEN[:10]}...")
    logger.info(f"📢 Chat ID: {CHAT_ID}")
    logger.info("=" * 60)
    
    # ইঞ্জিন তৈরি
    engine = PredictionEngine()
    
    # প্রথম ডাটা ফেচ
    logger.info("📡 Fetching initial data...")
    await engine.fetch_data()
    logger.info("✅ Initial data fetched")
    
    # সিগন্যাল অটো স্টার্ট
    is_running = True
    asyncio.create_task(signal_loop())
    
    logger.info("✅ Bot is ready and running!")
    print("\n" + "=" * 60)
    print("  ✅ MASUD AI BOT IS NOW RUNNING!")
    print("  📡 Waiting for signals...")
    print("=" * 60 + "\n")
    
    # মেইন লুপ চালু
    await main_loop()

# ============================================================
# মেইন
# ============================================================
if __name__ == "__main__":
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        raise
