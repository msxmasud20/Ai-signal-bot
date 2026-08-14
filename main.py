import os
import asyncio
import aiohttp
import json
import random
import logging
from datetime import datetime, timedelta
from collections import Counter

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
║      🤖 MASUD AI - ULTIMATE PREDICTION BOT                 ║
║      🚀 VERSION 9.0 - ADMIN PANEL ADDED                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

# ============================================================
# 🔐 এডমিন পাসওয়ার্ড
# ============================================================
ADMIN_PASSWORD = "msxmasud20"
admin_session = {}  # {chat_id: authenticated}

# ============================================================
# 🖼️ ইমেজ কনফিগারেশন (ইমোজি বেইজড)
# ============================================================
IMAGE_CONFIG = {
    'BIG': '🟢',
    'SMALL': '🔴',
    'WIN': '🏆',
    'LOSS': '💔',
    'WAIT': '⏳',
    'BIG_IMAGE': '🟢🔮 BIG SIGNAL',
    'SMALL_IMAGE': '🔴🔮 SMALL SIGNAL',
    'WIN_IMAGE': '🏆✅ WINNER',
    'LOSS_IMAGE': '💔❌ LOSS'
}

# ============================================================
# টেলিগ্রাম API ফাংশন
# ============================================================
async def send_telegram_message(message, chat_id=None):
    """টেক্সট মেসেজ পাঠায়"""
    target_chat = chat_id or CHAT_ID
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": target_chat,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=10) as response:
                if response.status == 200:
                    return True
                return False
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return False

async def send_telegram_keyboard(message, keyboard, chat_id=None):
    """কীবোর্ড সহ মেসেজ পাঠায়"""
    target_chat = chat_id or CHAT_ID
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    reply_markup = {"inline_keyboard": keyboard}
    payload = {
        "chat_id": target_chat,
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
# API কনফিগারেশন
# ============================================================
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json?pageNo=1&pageSize=10"

API_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,bn;q=0.8',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Referer': 'https://draw.ar-lottery01.com/',
    'Origin': 'https://draw.ar-lottery01.com',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache'
}

# ============================================================
# গ্লোবাল ভেরিয়েবল
# ============================================================
is_running = False
last_signal = None
last_period = None
engine = None
offset = None
signal_count = 0
last_api_call = 0

# ============================================================
# 🧠 স্মার্ট প্রেডিকশন ইঞ্জিন
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
        
        # 🔥 ইমেজ কনফিগারেশন
        self.images = {
            'BIG': '🟢',
            'SMALL': '🔴',
            'WIN': '🏆',
            'LOSS': '💔',
            'WAIT': '⏳'
        }

    # ============================================================
    # 🎯 ব্যালান্সড অ্যালগরিদম
    # ============================================================
    def smart_predict(self, numbers):
        """ব্যালান্সড অ্যালগরিদম - BIG/SMALL সমান সুযোগ"""
        if not numbers or len(numbers) < 5:
            return {
                'signal': 'WAIT',
                'number': random.randint(0, 9),
                'confidence': 0,
                'reason': 'Insufficient data'
            }
        
        # ট্রেন্ড অ্যানালাইসিস
        bigs = sum(1 for n in numbers if n >= 5)
        smalls = len(numbers) - bigs
        big_ratio = bigs / len(numbers)
        
        # কনসিকিউটিভ চেক
        consecutive_big = 0
        consecutive_small = 0
        for n in reversed(numbers[-5:]):
            if n >= 5:
                if consecutive_small > 0:
                    break
                consecutive_big += 1
            else:
                if consecutive_big > 0:
                    break
                consecutive_small += 1
        
        # অল্টারনেটিং চেক
        last_5 = numbers[-5:]
        alternating = all((last_5[i] >= 5) != (last_5[i+1] >= 5) for i in range(4)) if len(last_5) >= 5 else False
        
        # 🎯 ডিসিশন মেকিং - ব্যালান্সড
        score_big = 0
        score_small = 0
        
        # ফ্যাক্টর ১: ট্রেন্ড (৪০%)
        if big_ratio >= 0.55:
            score_big += 40
        elif big_ratio <= 0.45:
            score_small += 40
        else:
            score_big += 20
            score_small += 20
        
        # ফ্যাক্টর ২: কনসিকিউটিভ (৩৫%)
        if consecutive_big >= 3:
            score_small += 35  # রিভার্স
        elif consecutive_small >= 3:
            score_big += 35   # রিভার্স
        elif consecutive_big >= 2:
            score_small += 20
        elif consecutive_small >= 2:
            score_big += 20
        else:
            score_big += 15
            score_small += 15
        
        # ফ্যাক্টর ৩: অল্টারনেটিং (২৫%)
        if alternating:
            last = numbers[-1]
            if last >= 5:
                score_small += 25  # BIG এর পর SMALL
            else:
                score_big += 25    # SMALL এর পর BIG
        else:
            score_big += 12
            score_small += 12
        
        # 🗳️ ফাইনাল সিদ্ধান্ত
        if score_big > score_small + 10:
            signal = 'BIG'
            num = random.randint(5, 9)
            confidence = min(90, 60 + (score_big - score_small))
        elif score_small > score_big + 10:
            signal = 'SMALL'
            num = random.randint(0, 4)
            confidence = min(90, 60 + (score_small - score_big))
        else:
            signal = 'WAIT'
            num = random.randint(0, 9)
            confidence = 0
        
        return {
            'signal': signal,
            'number': num,
            'confidence': min(95, confidence),
            'reason': f"BIG:{score_big} SMALL:{score_small}",
            'scores': {'BIG': score_big, 'SMALL': score_small}
        }

    # ============================================================
    # 📡 পিরিয়ড সিঙ্ক
    # ============================================================
    def get_current_win_go_period(self):
        """দ্রুত পিরিয়ড ক্যালকুলেশন"""
        now = datetime.now()
        base = datetime(2024, 1, 1, 0, 0, 0)
        seconds_diff = int((now - base).total_seconds())
        period_number = (seconds_diff // 30) + 1
        base_period = 728000
        return str(base_period + period_number)

    def sync_period(self, api_period, win_go_period):
        """পিরিয়ড সিঙ্ক - অটো +১"""
        try:
            api_int = int(api_period)
            win_go_int = int(win_go_period)
            diff = win_go_int - api_int
            
            if diff == 1:
                return win_go_period
            elif diff == 0:
                return api_period
            else:
                return str(api_int + 1)
        except:
            return api_period

    # ============================================================
    # 📊 API ডাটা ফেচ
    # ============================================================
    async def fetch_data(self):
        """API থেকে ডাটা সংগ্রহ"""
        global last_api_call
        
        # Rate limiting - 2 সেকেন্ডের কমে আবার কল না
        current_time = datetime.now().timestamp()
        if current_time - last_api_call < 2:
            return None
        last_api_call = current_time
        
        try:
            win_go_period = self.get_current_win_go_period()
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    API_URL, 
                    headers=API_HEADERS, 
                    timeout=8,
                    allow_redirects=True
                ) as response:
                    if response.status == 200:
                        try:
                            text = await response.text()
                            data = json.loads(text)
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
                                api_latest_issue = items[0].get('issueNumber', '')
                                use_period = self.sync_period(api_latest_issue, win_go_period)
                                
                                if use_period != self.last_issue:
                                    self.last_issue = use_period
                                    self.history = numbers[:30]
                                    self.last_10_numbers = numbers[:10]
                                    
                                    self.big_count = sum(1 for n in self.last_10_numbers if n >= 5)
                                    self.small_count = len(self.last_10_numbers) - self.big_count
                                    
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
                                    
                                    prediction = self.smart_predict(self.history)
                                    
                                    self.current_prediction = {
                                        'period': use_period,
                                        'prediction': prediction['signal'],
                                        'number': prediction['number'],
                                        'confidence': prediction['confidence'],
                                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                                        'big_count': self.big_count,
                                        'small_count': self.small_count,
                                        'consecutive_big': self.consecutive_big,
                                        'consecutive_small': self.consecutive_small,
                                        'history': self.last_10_numbers[:10],
                                        'reason': prediction.get('reason', ''),
                                        'scores': prediction.get('scores', {}),
                                        'api_period': api_latest_issue,
                                        'win_go_period': win_go_period
                                    }
                                    
                                    return self.current_prediction
                    return None
                    
        except asyncio.TimeoutError:
            logger.warning("API timeout")
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
        ],
        [
            {"text": "🖼️ ইমেজ সেটিং", "callback_data": "image_settings"},
            {"text": "📈 ট্রেড হিস্টরি", "callback_data": "trade_history"}
        ]
    ]

# ============================================================
# 🔐 এডমিন প্যানেল
# ============================================================
def get_admin_keyboard():
    """এডমিন প্যানেল কীবোর্ড"""
    return [
        [
            {"text": "🟢 BIG ইমেজ সেট", "callback_data": "set_big"},
            {"text": "🔴 SMALL ইমেজ সেট", "callback_data": "set_small"}
        ],
        [
            {"text": "🏆 WIN ইমেজ সেট", "callback_data": "set_win"},
            {"text": "💔 LOSS ইমেজ সেট", "callback_data": "set_loss"}
        ],
        [
            {"text": "📊 স্ট্যাটাস দেখুন", "callback_data": "admin_stats"},
            {"text": "🔙 ব্যাক", "callback_data": "back_to_main"}
        ]
    ]

def create_signal_image(signal, number, confidence):
    """সিগন্যাল ইমেজ তৈরি"""
    if signal == 'BIG':
        emoji = '🟢'
        text = '🔮 BIG SIGNAL'
    elif signal == 'SMALL':
        emoji = '🔴'
        text = '🔮 SMALL SIGNAL'
    elif signal == 'WIN':
        emoji = '🏆'
        text = '✅ WINNER'
    elif signal == 'LOSS':
        emoji = '💔'
        text = '❌ LOSS'
    else:
        emoji = '⏳'
        text = '⏳ WAIT'
    
    return f"""
╔══════════════════════════════════╗
║                                  ║
║        {emoji} {text} {emoji}         ║
║                                  ║
║     🎯 Number: {number}              ║
║     📊 Confidence: {confidence}%     ║
║                                  ║
╚══════════════════════════════════╝
"""

# ============================================================
# সিগন্যাল ফাংশন
# ============================================================
async def send_signal(prediction):
    """সিগন্যাল পাঠান"""
    global engine, signal_count
    
    if not prediction or not engine:
        return
    
    signal_count += 1
    engine.total_trade += 1
    
    signal_emoji = engine.images.get(prediction['prediction'], '❓')
    signal_image = create_signal_image(
        prediction['prediction'],
        prediction['number'],
        prediction['confidence']
    )
    
    bar = get_confidence_bar(prediction['confidence'])
    dots = get_history_dots(prediction.get('history', []))
    
    # পিরিয়ড সিঙ্ক ইনফো
    period_info = ""
    if 'api_period' in prediction and 'win_go_period' in prediction:
        if prediction['api_period'] != prediction['win_go_period']:
            period_info = f"\n🔄 সিঙ্ক: {prediction['api_period']} → {prediction['win_go_period']}"
    
    scores = prediction.get('scores', {})
    scores_info = f"\n📊 স্কোর: BIG {scores.get('BIG', 0)} | SMALL {scores.get('SMALL', 0)}"
    
    msg = f"""
{signal_image}

{signal_emoji} *MASUD AI - রিয়েল প্রেডিক্ট*
━━━━━━━━━━━━━━━━━━━━━━

🔢 *পিরিয়ড:* `{prediction['period'][-6:]}`{period_info}
🎯 *সিগন্যাল:* {signal_emoji} *{prediction['prediction']}*
🔢 *প্রেডিক্টেড নম্বর:* `{prediction['number'] if prediction['prediction'] != 'WAIT' else '--'}`
📊 *কনফিডেন্স:* {prediction['confidence']}% {bar if prediction['prediction'] != 'WAIT' else '⏳'}

📈 *ট্রেন্ড অ্যানালাইসিস:*
• লাস্ট ১০: {dots}
• BIG: {prediction.get('big_count', 0)} | SMALL: {prediction.get('small_count', 0)}
• কনসিকিউটিভ BIG: {prediction.get('consecutive_big', 0)}
• কনসিকিউটিভ SMALL: {prediction.get('consecutive_small', 0)}
{scores_info}

📊 *পরিসংখ্যান:*
🏆 উইন: {engine.win_count} | 💔 লস: {engine.loss_count}
🎯 একুরেসি: {engine.accuracy}% | 📈 ট্রেড #{engine.total_trade}

⏱️ {prediction['timestamp']}
━━━━━━━━━━━━━━━━━━━━━━
🅿🅾🆆🅴🆁🅴🅳 🅱🆈 🅼🅰🆂🆄🅳 🅰🅸
    """
    
    await send_telegram_message(msg)
    logger.info(f"📤 Signal #{signal_count}: {prediction['prediction']}")

async def check_result(prediction, actual_number):
    """রেজাল্ট চেক"""
    global engine
    
    if not prediction or actual_number is None or not engine:
        return
    
    if prediction['prediction'] == 'WAIT':
        return
    
    actual_bs = "BIG" if actual_number >= 5 else "SMALL"
    is_win = prediction['prediction'] == actual_bs
    
    if is_win:
        engine.win_count += 1
        result_emoji = engine.images.get('WIN', '🏆')
        result_text = f"{result_emoji} *উইন!* 🏆"
    else:
        engine.loss_count += 1
        result_emoji = engine.images.get('LOSS', '💔')
        result_text = f"{result_emoji} *লস!* 💔"
    
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
    
    # WIN/LOSS ইমেজ
    result_image = create_signal_image(
        'WIN' if is_win else 'LOSS',
        actual_number,
        engine.accuracy
    )
    
    msg = f"""
{result_image}

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
# সিগন্যাল লুপ
# ============================================================
async def signal_loop():
    """সিগন্যাল লুপ"""
    global is_running, last_signal, last_period, engine
    
    logger.info("🔄 Signal loop started")
    
    while is_running:
        try:
            if engine:
                prediction = await engine.fetch_data()
                
                if prediction:
                    if prediction['period'] != last_period:
                        if last_period and last_signal:
                            if engine.history:
                                real_num = engine.history[0] if engine.history else None
                                if real_num is not None:
                                    await check_result(last_signal, real_num)
                        
                        last_period = prediction['period']
                        last_signal = prediction
                        await send_signal(prediction)
                    else:
                        logger.debug(f"⏳ Same period {prediction['period']}")
                else:
                    logger.debug("⏳ No prediction")
            
            await asyncio.sleep(30)
            
        except Exception as e:
            logger.error(f"❌ Loop error: {e}")
            await asyncio.sleep(30)

# ============================================================
# মেসেজ হ্যান্ডলার
# ============================================================
async def handle_message(message):
    global is_running, engine, admin_session
    
    text = message.get('text', '')
    chat_id = str(message['chat']['id'])
    user_id = str(message['from']['id'])
    
    # শুধু আমাদের CHAT_ID এর মেসেজ প্রসেস করি
    if chat_id != str(CHAT_ID):
        return
    
    # 🔐 এডমিন প্যানেল - /admin কমান্ড
    if text == '/admin':
        # পাসওয়ার্ড চাওয়া
        admin_session[user_id] = {'step': 'awaiting_password'}
        await send_telegram_message(
            "🔐 *এডমিন প্যানেল*\n\n"
            "দয়া করে পাসওয়ার্ড দিন:",
            chat_id
        )
        return
    
    # পাসওয়ার্ড চেক
    if user_id in admin_session and admin_session[user_id].get('step') == 'awaiting_password':
        if text == ADMIN_PASSWORD:
            admin_session[user_id] = {'step': 'authenticated'}
            await send_telegram_keyboard(
                "✅ *এডমিন প্যানেল খোলা হয়েছে!*\n\n"
                "নিচের অপশনগুলি থেকে বেছে নিন:",
                get_admin_keyboard(),
                chat_id
            )
        else:
            await send_telegram_message(
                "❌ *ভুল পাসওয়ার্ড!*\n\n"
                "আবার চেষ্টা করুন অথবা /admin দিয়ে শুরু করুন।",
                chat_id
            )
            admin_session.pop(user_id, None)
        return
    
    # রেগুলার কমান্ড
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
        await send_telegram_keyboard(msg, get_start_keyboard(), chat_id)
    
    elif text == '/predict':
        if engine:
            prediction = await engine.fetch_data()
            if prediction:
                await send_signal(prediction)
            else:
                await send_telegram_message("⏳ সিগন্যাল তৈরি হচ্ছে...", chat_id)
        else:
            await send_telegram_message("⏳ ইঞ্জিন প্রস্তুত হচ্ছে...", chat_id)
    
    elif text == '/stats':
        if not engine:
            await send_telegram_message("⏳ ডাটা সংগ্রহ করছি...", chat_id)
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
        await send_telegram_message(stats, chat_id)
    
    elif text == '/help':
        help_text = """
🤖 *MASUD AI Bot - সাহায্য*

📌 *কমান্ডসমূহ:*
/start - বট চালু করুন
/predict - তাৎক্ষণিক সিগন্যাল
/stats - পরিসংখ্যান দেখুন
/help - এই মেসেজ দেখান
/admin - এডমিন প্যানেল খুলুন

📊 *ফিচারসমূহ:*
✅ ৩০ সেকেন্ডে অটো সিগন্যাল
✅ BIG/SMALL প্রেডিক্ট
✅ উইন/লস ট্র্যাকার
✅ লাইভ স্ট্যাটাস
✅ ইমেজ সাপোর্ট
✅ এডমিন প্যানেল

⚡ *পাওয়ার্ড বাই MASUD AI*
        """
        await send_telegram_message(help_text, chat_id)

# ============================================================
# Callback হ্যান্ডলার
# ============================================================
async def handle_callback(callback):
    global is_running, engine, admin_session
    
    data = callback['data']
    callback_id = callback['id']
    message = callback.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    message_id = message.get('message_id')
    user_id = str(callback['from']['id'])
    
    # এডমিন চেক
    is_admin = user_id in admin_session and admin_session[user_id].get('step') == 'authenticated'
    
    # ============================================================
    # 🔐 এডমিন প্যানেল কমান্ড
    # ============================================================
    if data == 'image_settings':
        if not is_admin:
            await answer_callback(callback_id, "⛔ এডমিন প্যানেল নয়!")
            return
        await edit_message_text(
            chat_id, message_id,
            "🖼️ *ইমেজ সেটিংস*\n\n"
            "কোন ইমেজ পরিবর্তন করতে চান?",
            get_admin_keyboard()
        )
        await answer_callback(callback_id, "🖼️ ইমেজ সেটিংস খোলা হয়েছে")
        return
    
    elif data == 'set_big':
        if not is_admin:
            await answer_callback(callback_id, "⛔ এডমিন প্যানেল নয়!")
            return
        if engine:
            engine.images['BIG'] = '🟢'
        await answer_callback(callback_id, "✅ BIG ইমেজ সেট করা হয়েছে!")
        await edit_message_text(
            chat_id, message_id,
            "✅ *BIG ইমেজ সেট করা হয়েছে!*\n\n"
            "বর্তমান BIG ইমেজ: 🟢",
            get_admin_keyboard()
        )
        return
    
    elif data == 'set_small':
        if not is_admin:
            await answer_callback(callback_id, "⛔ এডমিন প্যানেল নয়!")
            return
        if engine:
            engine.images['SMALL'] = '🔴'
        await answer_callback(callback_id, "✅ SMALL ইমেজ সেট করা হয়েছে!")
        await edit_message_text(
            chat_id, message_id,
            "✅ *SMALL ইমেজ সেট করা হয়েছে!*\n\n"
            "বর্তমান SMALL ইমেজ: 🔴",
            get_admin_keyboard()
        )
        return
    
    elif data == 'set_win':
        if not is_admin:
            await answer_callback(callback_id, "⛔ এডমিন প্যানেল নয়!")
            return
        if engine:
            engine.images['WIN'] = '🏆'
        await answer_callback(callback_id, "✅ WIN ইমেজ সেট করা হয়েছে!")
        await edit_message_text(
            chat_id, message_id,
            "✅ *WIN ইমেজ সেট করা হয়েছে!*\n\n"
            "বর্তমান WIN ইমেজ: 🏆",
            get_admin_keyboard()
        )
        return
    
    elif data == 'set_loss':
        if not is_admin:
            await answer_callback(callback_id, "⛔ এডমিন প্যানেল নয়!")
            return
        if engine:
            engine.images['LOSS'] = '💔'
        await answer_callback(callback_id, "✅ LOSS ইমেজ সেট করা হয়েছে!")
        await edit_message_text(
            chat_id, message_id,
            "✅ *LOSS ইমেজ সেট করা হয়েছে!*\n\n"
            "বর্তমান LOSS ইমেজ: 💔",
            get_admin_keyboard()
        )
        return
    
    elif data == 'admin_stats':
        if not is_admin:
            await answer_callback(callback_id, "⛔ এডমিন প্যানেল নয়!")
            return
        stats = f"""
📊 *এডমিন - স্ট্যাটাস*
━━━━━━━━━━━━━━━━━━━

• মোট ট্রেড: {engine.total_trade if engine else 0}
• 🏆 উইন: {engine.win_count if engine else 0}
• 💔 লস: {engine.loss_count if engine else 0}
• 🎯 একুরেসি: {engine.accuracy if engine else 0}%
• 📡 স্ট্যাটাস: {'🟢 চলমান' if is_running else '🔴 বন্ধ'}

🖼️ *ইমেজ কনফিগারেশন:*
• BIG: {engine.images.get('BIG', '🟢') if engine else '🟢'}
• SMALL: {engine.images.get('SMALL', '🔴') if engine else '🔴'}
• WIN: {engine.images.get('WIN', '🏆') if engine else '🏆'}
• LOSS: {engine.images.get('LOSS', '💔') if engine else '💔'}
        """
        await edit_message_text(chat_id, message_id, stats, get_admin_keyboard())
        await answer_callback(callback_id, "📊 স্ট্যাটাস দেখানো হচ্ছে")
        return
    
    elif data == 'back_to_main':
        if not is_admin:
            await answer_callback(callback_id, "⛔ এডমিন প্যানেল নয়!")
            return
        status = "🟢 চলমান" if is_running else "🔴 বন্ধ"
        msg = f"""
🤖 *MASUD AI - রিয়েল প্রেডিক্টর*
━━━━━━━━━━━━━━━━━━━━━━

📊 *স্ট্যাটাস:* {status}
🏆 *উইন:* {engine.win_count if engine else 0}
💔 *লস:* {engine.loss_count if engine else 0}
📈 *ট্রেড:* {engine.total_trade if engine else 0}
🎯 *একুরেসি:* {engine.accuracy if engine else 0}%

💡 নিচের বাটন ব্যবহার করুন
        """
        await edit_message_text(chat_id, message_id, msg, get_start_keyboard())
        await answer_callback(callback_id, "🔙 মেইন মেনুতে ফিরে গেলাম")
        return
    
    # ============================================================
    # রেগুলার কমান্ড
    # ============================================================
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
            
            scores = p.get('scores', {})
            scores_info = f"🗳️ স্কোর: BIG {scores.get('BIG', 0)} | SMALL {scores.get('SMALL', 0)}"
            
            signal = f"""
📡 *লাইভ সিগন্যাল*
━━━━━━━━━━━━━━━━━━━

🔢 পিরিয়ড: `{p['period'][-6:]}`
🎯 সিগন্যাল: {'🟢' if p['prediction'] == 'BIG' else '🔴' if p['prediction'] == 'SMALL' else '⏳'} *{p['prediction']}*
📊 কনফিডেন্স: {p['confidence']}% {bar}

📈 *ট্রেন্ড অ্যানালাইসিস:*
• লাস্ট ১০: {dots}
• BIG: {p.get('big_count', 0)} | SMALL: {p.get('small_count', 0)}
{scores_info}

⏱️ সময়: {p['timestamp']}
━━━━━━━━━━━━━━━━━━━
            """
            await answer_callback(callback_id, "📡 লাইভ সিগন্যাল দেখানো হচ্ছে...")
            await edit_message_text(chat_id, message_id, signal)
        else:
            await answer_callback(callback_id, "⏳ কোনো সিগন্যাল নেই")
    
    elif data == "trade_history":
        if not engine or not engine.trade_history:
            await answer_callback(callback_id, "❌ কোনো ট্রেড নেই")
            return
        
        history = "📈 *ট্রেড হিস্টরি*\n━━━━━━━━━━━━━━━━━━━\n"
        for i, t in enumerate(engine.trade_history[-10:], 1):
            icon = "✅" if t['result'] == "Win" else "❌"
            history += f"{i}. {icon} {t['prediction']} → {t['actual']} ({t['number']})\n"
        
        await answer_callback(callback_id, "📈 ট্রেড হিস্টরি দেখানো হচ্ছে...")
        await edit_message_text(chat_id, message_id, history)

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
    logger.info("🔐 ADMIN PANEL: /admin")
    logger.info("🔑 PASSWORD: msxmasud20")
    logger.info("=" * 60)
    
    engine = PredictionEngine()
    
    logger.info("📡 Fetching initial data...")
    await engine.fetch_data()
    logger.info("✅ Initial data fetched")
    
    is_running = True
    asyncio.create_task(signal_loop())
    
    logger.info("✅ Bot is ready and running!")
    print("\n" + "=" * 60)
    print("  ✅ MASUD AI BOT IS NOW RUNNING!")
    print("  🔐 ADMIN PANEL: /admin")
    print("  🔑 PASSWORD: msxmasud20")
    print("  📡 Waiting for signals...")
    print("=" * 60 + "\n")
    
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
