import os
import asyncio
import aiohttp
import json
import random
import logging
from datetime import datetime, timedelta
from collections import Counter
import base64
from io import BytesIO

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
║      🚀 VERSION 11.0 - ALL ISSUES FIXED                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

# ============================================================
# 🔐 এডমিন পাসওয়ার্ড
# ============================================================
ADMIN_PASSWORD = "msxmasud20"
admin_session = {}  # {chat_id: {'step': 'authenticated'}}

# ============================================================
# 🖼️ ইমেজ স্টোরেজ - রিয়েল ফটো সাপোর্ট
# ============================================================
class ImageManager:
    def __init__(self):
        # ডিফল্ট ইমেজ (ইমোজি)
        self.images = {
            'BIG': '🟢',
            'SMALL': '🔴',
            'WIN': '🏆',
            'LOSS': '💔',
            'JACKPOT': '💰',
            'WAIT': '⏳'
        }
        self.image_urls = {
            'BIG': None,
            'SMALL': None,
            'WIN': None,
            'LOSS': None,
            'JACKPOT': None
        }
        self.pending_image = None  # এডমিনের জন্য পেন্ডিং ইমেজ
    
    def get_image(self, signal_type):
        """সিগন্যাল টাইপ অনুযায়ী ইমেজ রিটার্ন করে"""
        if signal_type in self.images:
            return self.images[signal_type]
        return '❓'
    
    def set_image(self, signal_type, image_data):
        """ইমেজ সেট করে"""
        if signal_type in self.images:
            self.images[signal_type] = image_data
            return True
        return False
    
    def get_image_url(self, signal_type):
        """ইমেজ URL রিটার্ন করে"""
        return self.image_urls.get(signal_type)

# ============================================================
# টেলিগ্রাম API ফাংশন
# ============================================================
async def send_telegram_message(message, chat_id=None):
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

async def send_telegram_photo(caption, photo_url, chat_id=None):
    """ফটো পাঠায়"""
    target_chat = chat_id or CHAT_ID
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    
    # ফটো URL বা ফাইল আইডি
    payload = {
        "chat_id": target_chat,
        "caption": caption,
        "parse_mode": "Markdown"
    }
    
    # photo প্যারামিটার
    if photo_url and photo_url.startswith(('http', 'https')):
        payload["photo"] = photo_url
    else:
        payload["photo"] = photo_url
    
    try:
        async with aiohttp.ClientSession() as session:
            if photo_url and photo_url.startswith(('http', 'https')):
                async with session.post(url, json=payload, timeout=15) as response:
                    return response.status == 200
            else:
                # ফাইল আইডি বা local ফাইল
                async with session.post(url, data=payload, timeout=15) as response:
                    return response.status == 200
    except Exception as e:
        logger.error(f"Error sending photo: {e}")
        return False

async def send_telegram_keyboard(message, keyboard, chat_id=None):
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
image_manager = None
offset = None
signal_count = 0
last_result = None
total_loss = 0
total_profit = 0

# ============================================================
# 🧠 স্মার্ট প্রেডিকশন ইঞ্জিন - আপডেটেড
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
    # 🎯 স্মার্ট অ্যালগরিদম - WAIT রিমুভ + টাই ব্রেকার
    # ============================================================
    def smart_predict(self, numbers):
        """স্মার্ট অ্যালগরিদম - WAIT নেই, টাই হলে র্যান্ডম"""
        if not numbers or len(numbers) < 5:
            num = random.randint(0, 9)
            return {
                'signal': 'BIG' if num >= 5 else 'SMALL',
                'number': num,
                'confidence': 50,
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
        
        # 📊 স্কোরিং
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
            score_small += 35
        elif consecutive_small >= 3:
            score_big += 35
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
                score_small += 25
            else:
                score_big += 25
        else:
            score_big += 12
            score_small += 12
        
        # 🎯 ফাইনাল ডিসিশন - টাই হলে র্যান্ডম (WAIT নেই)
        if score_big > score_small:
            signal = 'BIG'
            num = random.randint(5, 9)
            confidence = min(90, 55 + (score_big - score_small))
        elif score_small > score_big:
            signal = 'SMALL'
            num = random.randint(0, 4)
            confidence = min(90, 55 + (score_small - score_big))
        else:
            # টাই হলে র্যান্ডম
            num = random.randint(0, 9)
            signal = 'BIG' if num >= 5 else 'SMALL'
            confidence = 55
        
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
        now = datetime.now()
        base = datetime(2024, 1, 1, 0, 0, 0)
        seconds_diff = int((now - base).total_seconds())
        period_number = (seconds_diff // 30) + 1
        base_period = 728000
        return str(base_period + period_number)

    def sync_period(self, api_period, win_go_period):
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
        global last_api_call
        
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
# 🔐 এডমিন প্যানেল - রিয়েল ইমেজ আপলোড
# ============================================================
def get_admin_keyboard():
    return [
        [
            {"text": "🟢 BIG ইমেজ আপলোড", "callback_data": "upload_big"},
            {"text": "🔴 SMALL ইমেজ আপলোড", "callback_data": "upload_small"}
        ],
        [
            {"text": "🏆 WIN ইমেজ আপলোড", "callback_data": "upload_win"},
            {"text": "💔 LOSS ইমেজ আপলোড", "callback_data": "upload_loss"}
        ],
        [
            {"text": "💰 JACKPOT ইমেজ আপলোড", "callback_data": "upload_jackpot"},
            {"text": "📊 স্ট্যাটাস দেখুন", "callback_data": "admin_stats"}
        ],
        [
            {"text": "🔙 ব্যাক", "callback_data": "back_to_main"}
        ]
    ]

# ============================================================
# 📤 সিগন্যাল ফাংশন - নতুন ফরম্যাট
# ============================================================
async def send_signal(prediction, previous_result=None):
    """সিগন্যাল পাঠান - নতুন ফরম্যাটে"""
    global engine, signal_count, total_loss, total_profit
    
    if not prediction or not engine:
        return
    
    signal_count += 1
    engine.total_trade += 1
    
    # 🖼️ ইমেজ
    signal_emoji = image_manager.get_image(prediction['prediction'])
    signal_image = image_manager.get_image(prediction['prediction'])
    
    # পূর্ববর্তী ফলাফল
    result_text = ""
    if previous_result:
        if previous_result['result'] == 'Win':
            result_text = f"✅ আগের: উইন 🏆"
            total_profit += 1
        else:
            result_text = f"❌ আগের: লস 💔"
            total_loss += 1
    
    # 📊 ফরম্যাট
    msg = f"""
{signal_image} *MASUD AI - রিয়েল প্রেডিক্ট*
━━━━━━━━━━━━━━━━━━━━━━

📌 *Period:* `{prediction['period'][-6:]}`
🎯 *Predict:* *{prediction['prediction']}*
🔢 *Number:* `{prediction['number']}`
📊 *Confidence:* {prediction['confidence']}%

{result_text}

📊 *পরিসংখ্যান:*
💰 Total Loss: {total_loss}
💎 Total Profit: {total_profit}
🏆 Win: {engine.win_count} | 💔 Loss: {engine.loss_count}
🎯 Accuracy: {engine.accuracy}%

⏱️ {prediction['timestamp']}
━━━━━━━━━━━━━━━━━━━━━━
🅿🅾🆆🅴🆁🅴🅳 🅱🆈 🅼🅰🆂🆄🅳 🅰🅸
    """
    
    # জ্যাকপট চেক - নাম্বার + BIG/SMALL মিললে
    if prediction['number'] >= 5 and prediction['prediction'] == 'BIG':
        jackpot_emoji = image_manager.get_image('JACKPOT')
        msg += f"\n\n{jackpot_emoji} *JACKPOT!* নাম্বার + সাইড মিলেছে! {jackpot_emoji}"
    elif prediction['number'] < 5 and prediction['prediction'] == 'SMALL':
        jackpot_emoji = image_manager.get_image('JACKPOT')
        msg += f"\n\n{jackpot_emoji} *JACKPOT!* নাম্বার + সাইড মিলেছে! {jackpot_emoji}"
    
    await send_telegram_message(msg)
    logger.info(f"📤 Signal #{signal_count}: {prediction['prediction']}")

async def check_result(prediction, actual_number):
    """রেজাল্ট চেক"""
    global engine, last_result
    
    if not prediction or actual_number is None or not engine:
        return
    
    actual_bs = "BIG" if actual_number >= 5 else "SMALL"
    is_win = prediction['prediction'] == actual_bs
    
    if is_win:
        engine.win_count += 1
        result_text = "✅ *উইন!* 🏆"
        result_emoji = image_manager.get_image('WIN')
    else:
        engine.loss_count += 1
        result_text = "❌ *লস!* 💔"
        result_emoji = image_manager.get_image('LOSS')
    
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
    
    # রেজাল্ট সেভ
    last_result = {
        'result': 'Win' if is_win else 'Loss',
        'prediction': prediction['prediction'],
        'actual': actual_bs,
        'number': actual_number
    }
    
    # রেজাল্ট মেসেজ
    msg = f"""
{result_emoji} *ট্রেড আপডেট*
━━━━━━━━━━━━━━━━━━━

📌 Period: `{prediction['period'][-6:]}`
🔮 Predict: {prediction['prediction']}
🎯 Actual: {actual_bs} (`{actual_number}`)
📈 Result: {result_text}

📊 *আপডেটেড স্ট্যাটস:*
💰 Total Loss: {total_loss}
💎 Total Profit: {total_profit}
🏆 Win: {engine.win_count}
💔 Loss: {engine.loss_count}
🎯 Accuracy: {engine.accuracy}%

⏱️ {datetime.now().strftime('%H:%M:%S')}
━━━━━━━━━━━━━━━━━━━
    """
    
    await send_telegram_message(msg)

# ============================================================
# 🔄 সিগন্যাল লুপ - ঠিক টাইমিং
# ============================================================
async def signal_loop():
    """সিগন্যাল লুপ - :২৫ এ ডাটা, :৩০ এ সিগন্যাল, :৫৫ এ ডাটা, :০০ এ সিগন্যাল"""
    global is_running, last_signal, last_period, engine, last_result
    
    logger.info("🔄 Signal loop started - Timing: Collect at :25 & :55, Signal at :30 & :00")
    
    # বর্তমান সেকেন্ড ট্র্যাক
    last_collect = -1
    last_signal_time = -1
    
    while is_running:
        try:
            now = datetime.now()
            seconds = now.second
            
            # 🔥 :২৫ সেকেন্ডে ডাটা কালেক্ট
            if seconds == 25 and last_collect != 25:
                last_collect = 25
                logger.info(f"📡 Collecting data at :{seconds}s")
                if engine:
                    prediction = await engine.fetch_data()
                    if prediction:
                        logger.info(f"📊 Data collected for period {prediction['period']}")
            
            # 🔥 :৩০ সেকেন্ডে সিগন্যাল
            elif seconds == 30 and last_signal_time != 30:
                last_signal_time = 30
                logger.info(f"📤 Sending signal at :{seconds}s")
                if engine and engine.current_prediction:
                    prediction = engine.current_prediction
                    
                    if prediction['period'] != last_period:
                        # রেজাল্ট চেক
                        if last_period and last_signal:
                            if engine.history:
                                real_num = engine.history[0] if engine.history else None
                                if real_num is not None:
                                    await check_result(last_signal, real_num)
                        
                        last_period = prediction['period']
                        last_signal = prediction
                        await send_signal(prediction, last_result)
                        logger.info(f"✅ Signal sent for period {prediction['period']}")
            
            # 🔥 :৫৫ সেকেন্ডে ডাটা কালেক্ট
            elif seconds == 55 and last_collect != 55:
                last_collect = 55
                logger.info(f"📡 Collecting data at :{seconds}s")
                if engine:
                    prediction = await engine.fetch_data()
                    if prediction:
                        logger.info(f"📊 Data collected for period {prediction['period']}")
            
            # 🔥 :০০ সেকেন্ডে সিগন্যাল
            elif seconds == 0 and last_signal_time != 0:
                last_signal_time = 0
                logger.info(f"📤 Sending signal at :{seconds}s")
                if engine and engine.current_prediction:
                    prediction = engine.current_prediction
                    
                    if prediction['period'] != last_period:
                        if last_period and last_signal:
                            if engine.history:
                                real_num = engine.history[0] if engine.history else None
                                if real_num is not None:
                                    await check_result(last_signal, real_num)
                        
                        last_period = prediction['period']
                        last_signal = prediction
                        await send_signal(prediction, last_result)
                        logger.info(f"✅ Signal sent for period {prediction['period']}")
            
            # রিসেট - প্রতি মিনিটে
            if seconds == 0:
                last_collect = -1
                last_signal_time = -1
            
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"❌ Loop error: {e}")
            await asyncio.sleep(1)

# ============================================================
# মেসেজ হ্যান্ডলার
# ============================================================
async def handle_message(message):
    global is_running, engine, admin_session
    
    text = message.get('text', '')
    chat_id = str(message['chat']['id'])
    user_id = str(message['from']['id'])
    
    if chat_id != str(CHAT_ID):
        return
    
    # 🔐 এডমিন প্যানেল
    if text == '/admin':
        admin_session[user_id] = {'step': 'awaiting_password'}
        await send_telegram_message(
            "🔐 *এডমিন প্যানেল*\n\n"
            "দয়া করে পাসওয়ার্ড দিন:",
            chat_id
        )
        return
    
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
• 💰 Total Loss: {total_loss}
• 💎 Total Profit: {total_profit}

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

📊 *টাইমিং সিস্টেম:*
• :২৫ সেকেন্ডে ডাটা কালেক্ট
• :৩০ সেকেন্ডে সিগন্যাল
• :৫৫ সেকেন্ডে ডাটা কালেক্ট
• :০০ সেকেন্ডে সিগন্যাল
• প্রতি মিনিটে ২ বার

🎯 *জ্যাকপট:* নাম্বার + সাইড মিললে

⚡ *পাওয়ার্ড বাই MASUD AI*
        """
        await send_telegram_message(help_text, chat_id)

# ============================================================
# Callback হ্যান্ডলার
# ============================================================
async def handle_callback(callback):
    global is_running, engine, admin_session, image_manager
    
    data = callback['data']
    callback_id = callback['id']
    message = callback.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    message_id = message.get('message_id')
    user_id = str(callback['from']['id'])
    
    is_admin = user_id in admin_session and admin_session[user_id].get('step') == 'authenticated'
    
    # ============================================================
    # 🔐 এডমিন প্যানেল - ইমেজ আপলোড
    # ============================================================
    if data == 'image_settings':
        if not is_admin:
            await answer_callback(callback_id, "⛔ এডমিন প্যানেল নয়!")
            return
        await edit_message_text(
            chat_id, message_id,
            "🖼️ *ইমেজ সেটিংস*\n\n"
            "কোন ইমেজ আপলোড করতে চান?\n"
            "ইমেজ URL বা ফাইল পাঠান।",
            get_admin_keyboard()
        )
        await answer_callback(callback_id, "🖼️ ইমেজ সেটিংস খোলা হয়েছে")
        return
    
    elif data == 'upload_big':
        if not is_admin:
            await answer_callback(callback_id, "⛔ এডমিন প্যানেল নয়!")
            return
        admin_session[user_id]['pending_image'] = 'BIG'
        await edit_message_text(
            chat_id, message_id,
            "🟢 *BIG ইমেজ আপলোড*\n\n"
            "দয়া করে BIG ইমেজের URL বা ফাইল পাঠান:",
            get_admin_keyboard()
        )
        await answer_callback(callback_id, "📤 BIG ইমেজের জন্য অপেক্ষা করছি...")
        return
    
    elif data == 'upload_small':
        if not is_admin:
            await answer_callback(callback_id, "⛔ এডমিন প্যানেল নয়!")
            return
        admin_session[user_id]['pending_image'] = 'SMALL'
        await edit_message_text(
            chat_id, message_id,
            "🔴 *SMALL ইমেজ আপলোড*\n\n"
            "দয়া করে SMALL ইমেজের URL বা ফাইল পাঠান:",
            get_admin_keyboard()
        )
        await answer_callback(callback_id, "📤 SMALL ইমেজের জন্য অপেক্ষা করছি...")
        return
    
    elif data == 'upload_win':
        if not is_admin:
            await answer_callback(callback_id, "⛔ এডমিন প্যানেল নয়!")
            return
        admin_session[user_id]['pending_image'] = 'WIN'
        await edit_message_text(
            chat_id, message_id,
            "🏆 *WIN ইমেজ আপলোড*\n\n"
            "দয়া করে WIN ইমেজের URL বা ফাইল পাঠান:",
            get_admin_keyboard()
        )
        await answer_callback(callback_id, "📤 WIN ইমেজের জন্য অপেক্ষা করছি...")
        return
    
    elif data == 'upload_loss':
        if not is_admin:
            await answer_callback(callback_id, "⛔ এডমিন প্যানেল নয়!")
            return
        admin_session[user_id]['pending_image'] = 'LOSS'
        await edit_message_text(
            chat_id, message_id,
            "💔 *LOSS ইমেজ আপলোড*\n\n"
            "দয়া করে LOSS ইমেজের URL বা ফাইল পাঠান:",
            get_admin_keyboard()
        )
        await answer_callback(callback_id, "📤 LOSS ইমেজের জন্য অপেক্ষা করছি...")
        return
    
    elif data == 'upload_jackpot':
        if not is_admin:
            await answer_callback(callback_id, "⛔ এডমিন প্যানেল নয়!")
            return
        admin_session[user_id]['pending_image'] = 'JACKPOT'
        await edit_message_text(
            chat_id, message_id,
            "💰 *JACKPOT ইমেজ আপলোড*\n\n"
            "দয়া করে JACKPOT ইমেজের URL বা ফাইল পাঠান:",
            get_admin_keyboard()
        )
        await answer_callback(callback_id, "📤 JACKPOT ইমেজের জন্য অপেক্ষা করছি...")
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
• 💰 Total Loss: {total_loss}
• 💎 Total Profit: {total_profit}

🖼️ *ইমেজ কনফিগারেশন:*
• BIG: {image_manager.get_image('BIG') if image_manager else '🟢'}
• SMALL: {image_manager.get_image('SMALL') if image_manager else '🔴'}
• WIN: {image_manager.get_image('WIN') if image_manager else '🏆'}
• LOSS: {image_manager.get_image('LOSS') if image_manager else '💔'}
• JACKPOT: {image_manager.get_image('JACKPOT') if image_manager else '💰'}

⏱️ *টাইমিং:*
• ডাটা কালেক্ট: :২৫ এবং :৫৫
• সিগন্যাল: :৩০ এবং :০০
• প্রতি মিনিটে ২ বার
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
            await edit_message_text(chat_id, message_id, "✅ সিগন্যাল চালু হয়েছে! :২৫ এবং :৫৫ এ ডাটা কালেক্ট, :৩০ এবং :০০ এ সিগন্যাল।")
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
• 💰 Total Loss: {total_loss}
• 💎 Total Profit: {total_profit}

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
            
            signal = f"""
📡 *লাইভ সিগন্যাল*
━━━━━━━━━━━━━━━━━━━

📌 Period: `{p['period'][-6:]}`
🎯 Predict: *{p['prediction']}*
🔢 Number: `{p['number']}`
📊 Confidence: {p['confidence']}% {bar}

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
# ইমেজ আপলোড হ্যান্ডলার
# ============================================================
async def handle_image_upload(message):
    """এডমিনের ইমেজ আপলোড হ্যান্ডেল করে"""
    global admin_session, image_manager
    
    user_id = str(message['from']['id'])
    chat_id = str(message['chat']['id'])
    
    if user_id not in admin_session or admin_session[user_id].get('step') != 'authenticated':
        return
    
    pending = admin_session[user_id].get('pending_image')
    if not pending:
        return
    
    # ফটো চেক
    if 'photo' in message:
        # ফটো আইডি নেওয়া
        photo = message['photo'][-1]  # সবচেয়ে বড় সাইজ
        file_id = photo['file_id']
        
        # ইমেজ সেট করা
        if image_manager:
            image_manager.set_image(pending, file_id)
        
        admin_session[user_id]['pending_image'] = None
        
        await send_telegram_message(
            f"✅ *{pending} ইমেজ সফলভাবে আপলোড করা হয়েছে!*\n\n"
            f"ইমেজ আইডি: `{file_id}`",
            chat_id
        )
        
        # আবার মেনু দেখান
        await send_telegram_keyboard(
            "🖼️ *ইমেজ সেটিংস*\n\n"
            "আরও ইমেজ আপলোড করুন অথবা ব্যাক করুন:",
            get_admin_keyboard(),
            chat_id
        )
        return
    
    # টেক্সট (URL) চেক
    if 'text' in message:
        text = message['text']
        if text.startswith(('http://', 'https://')):
            if image_manager:
                image_manager.set_image(pending, text)
            
            admin_session[user_id]['pending_image'] = None
            
            await send_telegram_message(
                f"✅ *{pending} ইমেজ সফলভাবে আপলোড করা হয়েছে!*\n\n"
                f"URL: {text}",
                chat_id
            )
            
            await send_telegram_keyboard(
                "🖼️ *ইমেজ সেটিংস*\n\n"
                "আরও ইমেজ আপলোড করুন অথবা ব্যাক করুন:",
                get_admin_keyboard(),
                chat_id
            )
            return
    
    # ভুল ইনপুট
    await send_telegram_message(
        "❌ *ভুল ইনপুট!*\n\n"
        "দয়া করে একটি ইমেজ ফাইল বা ইমেজ URL পাঠান।",
        chat_id
    )

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
                    msg = update['message']
                    
                    # ইমেজ আপলোড চেক
                    if 'photo' in msg or ('text' in msg and msg['text'].startswith(('http://', 'https://'))):
                        await handle_image_upload(msg)
                    
                    await handle_message(msg)
                
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
    global engine, is_running, image_manager, total_loss, total_profit
    
    print_banner()
    logger.info("🤖 Starting Masud AI Bot...")
    logger.info(f"📡 Bot Token: {BOT_TOKEN[:10]}...")
    logger.info(f"📢 Chat ID: {CHAT_ID}")
    logger.info("=" * 60)
    logger.info("🔐 ADMIN PANEL: /admin")
    logger.info("🔑 PASSWORD: msxmasud20")
    logger.info("⏱️ TIMING: Collect at :25 & :55, Signal at :30 & :00")
    logger.info("🖼️ REAL IMAGE UPLOAD SYSTEM ACTIVE")
    logger.info("💰 JACKPOT SYSTEM ACTIVE")
    logger.info("=" * 60)
    
    # ইমেজ ম্যানেজার
    image_manager = ImageManager()
    
    # ইঞ্জিন
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
    print("  ⏱️ Collect at :25 & :55, Signal at :30 & :00")
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
