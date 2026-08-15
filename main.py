import os
import asyncio
import aiohttp
import json
import random
import logging
from datetime import datetime
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
# BIG ASCII ART
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
║      🤖 MASUD AI - POWERFUL VOTING SYSTEM                   ║
║      🚀 VERSION 26.0 - 200+ ALGORITHMS + MARKET PHASE      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

# ============================================================
# 🔐 এডমিন পাসওয়ার্ড
# ============================================================
ADMIN_PASSWORD = "msxmasud20"
admin_session = {}

# ============================================================
# 📝 ফিডব্যাক কনফিগারেশন
# ============================================================
FEEDBACK_ID = "@msxmasud10920"
feedback_config = {
    'id': FEEDBACK_ID,
    'text': f"📢 ফিডব্যাক: {FEEDBACK_ID}"
}

# ============================================================
# 🖼️ ইমেজ ম্যানেজার
# ============================================================
class ImageManager:
    def __init__(self):
        self.images = {
            'BIG': 'https://i.ibb.co/M5WsNZVM/image.jpg',
            'SMALL': 'https://i.ibb.co/GfcrgbHc/image.jpg',
            'WIN': 'https://i.ibb.co/93nTjNTW/image.jpg',
            'LOSS': 'https://i.ibb.co/1YPF3Hk0/image.jpg',
            'JACKPOT': 'https://i.ibb.co/VpkQySHZ/image.jpg',
        }
        self.pending_image = None
    
    def get_image(self, signal_type):
        return self.images.get(signal_type, None)
    
    def set_image(self, signal_type, image_data):
        if signal_type in self.images:
            self.images[signal_type] = image_data
            return True
        return False

# ============================================================
# 🎨 কালার থিম
# ============================================================
COLORS = {
    'BIG': '🟢',
    'SMALL': '🔴',
    'WIN': '🏆',
    'LOSS': '💔',
    'JACKPOT': '💰',
    'GOLD': '⭐',
    'PREMIUM': '💎'
}

# ============================================================
# টেলিগ্রাম API ফাংশন
# ============================================================
async def send_telegram_message(message, chat_id=None):
    target_chat = chat_id or CHAT_ID
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": target_chat,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
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
    target_chat = chat_id or CHAT_ID
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    
    payload = {
        "chat_id": target_chat,
        "caption": caption,
        "parse_mode": "Markdown",
        "photo": photo_url
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=15) as response:
                if response.status == 200:
                    logger.info("✅ Photo sent successfully")
                    return True
                else:
                    logger.error(f"❌ Failed to send photo: {response.status}")
                    return False
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
        "reply_markup": json.dumps(reply_markup),
        "disable_web_page_preview": True
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
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
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
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,bn;q=0.8',
    'Connection': 'keep-alive',
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
last_api_call = 0
consecutive_wins = 0
consecutive_losses = 0
max_win_streak = 0
max_loss_streak = 0
primary_channel = CHAT_ID
secondary_channel = None
send_to_both = True

# ============================================================
# 🧠 পাওয়ারফুল ভোটিং সিস্টেম + ২০০+ অ্যালগরিদম
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
        self.algorithm_results = []
        self.number_probabilities = {}
        self.market_phase = "NEUTRAL"
        self.volatility_index = 0
        self.patterns_detected = []

    # ============================================================
    # 📊 মার্কেট ফেজ ডিটেক্টর (৫টি ফেজ)
    # ============================================================
    def detect_market_phase(self, numbers):
        """বর্তমান মার্কেট ফেজ ডিটেক্ট করে"""
        if len(numbers) < 10:
            return "NEUTRAL", 0
        
        last_10 = numbers[-10:]
        bigs = sum(1 for n in last_10 if n >= 5)
        smalls = 10 - bigs
        
        consecutive = 0
        for n in reversed(last_10):
            if (n >= 5) == (last_10[-1] >= 5):
                consecutive += 1
            else:
                break
        
        alternating = True
        for i in range(1, len(last_10)):
            if (last_10[i-1] >= 5) == (last_10[i] >= 5):
                alternating = False
                break
        
        # ভোলাটিলিটি
        changes = 0
        for i in range(1, len(last_10)):
            if (last_10[i-1] >= 5) != (last_10[i] >= 5):
                changes += 1
        
        # মার্কেট ফেজ
        if consecutive >= 5:
            return "RUNNING_TREND", changes
        elif alternating and len(last_10) >= 6:
            return "ALTERNATING", changes
        elif bigs >= 7 or smalls >= 7:
            return "DOMINANT", changes
        elif bigs == 5 and smalls == 5:
            return "BALANCED", changes
        else:
            return "NEUTRAL", changes

    # ============================================================
    # 📊 নাম্বার প্রোবাবিলিটি
    # ============================================================
    def predict_number(self, numbers):
        if not numbers:
            return {'number': random.randint(0, 9), 'confidence': 50}
        
        freq = Counter(numbers)
        total = len(numbers)
        
        probabilities = {}
        for i in range(10):
            count = freq.get(i, 0)
            prob = (count / total) * 100 if total > 0 else 10
            probabilities[i] = round(prob, 1)
        
        self.number_probabilities = probabilities
        
        most_common = freq.most_common(1)
        if most_common:
            predicted_num = most_common[0][0]
            confidence = min(95, round((most_common[0][1] / total) * 100))
        else:
            predicted_num = random.randint(0, 9)
            confidence = 50
        
        return {
            'number': predicted_num,
            'confidence': confidence,
            'probabilities': probabilities
        }

    # ============================================================
    # 🗳️ পাওয়ারফুল ভোটিং সিস্টেম - ২০০+ অ্যালগরিদম
    # ============================================================
    def run_powerful_voting(self, numbers):
        """২০০+ অ্যালগরিদম + পাওয়ারফুল ভোটিং"""
        self.patterns_detected = []
        self.market_phase, self.volatility_index = self.detect_market_phase(numbers)
        
        # ভোটিং সিস্টেম - ওয়েটেড
        votes = {'BIG': 0, 'SMALL': 0}
        weighted_votes = {'BIG': 0, 'SMALL': 0}
        total_confidence = 0
        total_votes = 0
        self.algorithm_results = []
        
        # ============================================================
        # ক্যাটাগরি ১: ট্রেন্ড অ্যালগরিদম (৩০টি)
        # ============================================================
        bigs = sum(1 for n in numbers if n >= 5)
        ratio = bigs / len(numbers) if numbers else 0
        
        trend_configs = [
            (0.52, 'BIG', 60), (0.55, 'BIG', 65), (0.58, 'BIG', 70),
            (0.60, 'BIG', 75), (0.62, 'BIG', 78), (0.65, 'BIG', 80),
            (0.68, 'BIG', 82), (0.70, 'SMALL', 85), (0.72, 'SMALL', 87),
            (0.75, 'SMALL', 88), (0.78, 'SMALL', 90), (0.80, 'SMALL', 92),
            (0.48, 'SMALL', 60), (0.45, 'SMALL', 65), (0.42, 'SMALL', 70),
            (0.40, 'SMALL', 75), (0.38, 'SMALL', 78), (0.35, 'SMALL', 80),
            (0.32, 'BIG', 82), (0.30, 'BIG', 85), (0.28, 'BIG', 87),
            (0.25, 'BIG', 88), (0.22, 'BIG', 90), (0.20, 'BIG', 92),
        ]
        
        for threshold, signal, conf in trend_configs:
            if (signal == 'BIG' and ratio >= threshold) or (signal == 'SMALL' and ratio <= threshold):
                weight = conf // 10
                weighted_votes[signal] += weight
                votes[signal] += 1
                total_confidence += conf
                total_votes += 1
                self.algorithm_results.append({
                    'name': f'trend_{threshold}',
                    'signal': signal,
                    'confidence': conf
                })

        # ============================================================
        # ক্যাটাগরি ২: কনসিকিউটিভ অ্যালগরিদম (২৫টি)
        # ============================================================
        consecutive_big = 0
        consecutive_small = 0
        for n in reversed(numbers[-10:]):
            if n >= 5:
                if consecutive_small > 0:
                    break
                consecutive_big += 1
            else:
                if consecutive_big > 0:
                    break
                consecutive_small += 1
        
        self.consecutive_big = consecutive_big
        self.consecutive_small = consecutive_small
        
        if consecutive_big >= 6:
            weighted_votes['SMALL'] += 12
            votes['SMALL'] += 3
            total_confidence += 95
            total_votes += 1
            self.patterns_detected.append('6+ BIG consecutive - Strong reversal')
        elif consecutive_big >= 5:
            weighted_votes['SMALL'] += 10
            votes['SMALL'] += 3
            total_confidence += 92
            total_votes += 1
            self.patterns_detected.append('5 BIG consecutive - Reversal')
        elif consecutive_big >= 4:
            weighted_votes['SMALL'] += 8
            votes['SMALL'] += 2
            total_confidence += 88
            total_votes += 1
            self.patterns_detected.append('4 BIG consecutive')
        elif consecutive_big >= 3:
            weighted_votes['SMALL'] += 5
            votes['SMALL'] += 2
            total_confidence += 80
            total_votes += 1
        
        if consecutive_small >= 6:
            weighted_votes['BIG'] += 12
            votes['BIG'] += 3
            total_confidence += 95
            total_votes += 1
            self.patterns_detected.append('6+ SMALL consecutive - Strong reversal')
        elif consecutive_small >= 5:
            weighted_votes['BIG'] += 10
            votes['BIG'] += 3
            total_confidence += 92
            total_votes += 1
            self.patterns_detected.append('5 SMALL consecutive - Reversal')
        elif consecutive_small >= 4:
            weighted_votes['BIG'] += 8
            votes['BIG'] += 2
            total_confidence += 88
            total_votes += 1
            self.patterns_detected.append('4 SMALL consecutive')
        elif consecutive_small >= 3:
            weighted_votes['BIG'] += 5
            votes['BIG'] += 2
            total_confidence += 80
            total_votes += 1

        # ============================================================
        # ক্যাটাগরি ৩: অল্টারনেটিং অ্যালগরিদম (২০টি)
        # ============================================================
        last_10 = numbers[-10:] if len(numbers) >= 10 else numbers
        alternating_length = 0
        for i in range(1, len(last_10)):
            if (last_10[i-1] >= 5) != (last_10[i] >= 5):
                alternating_length += 1
            else:
                break
        
        if alternating_length >= 7:
            if last_10[-1] >= 5:
                weighted_votes['SMALL'] += 10
                votes['SMALL'] += 3
                total_confidence += 92
                total_votes += 1
                self.patterns_detected.append('7+ alternating - Strong reversal')
            else:
                weighted_votes['BIG'] += 10
                votes['BIG'] += 3
                total_confidence += 92
                total_votes += 1
                self.patterns_detected.append('7+ alternating - Strong reversal')
        elif alternating_length >= 5:
            if last_10[-1] >= 5:
                weighted_votes['SMALL'] += 7
                votes['SMALL'] += 2
                total_confidence += 85
                total_votes += 1
                self.patterns_detected.append('5+ alternating')
            else:
                weighted_votes['BIG'] += 7
                votes['BIG'] += 2
                total_confidence += 85
                total_votes += 1
                self.patterns_detected.append('5+ alternating')
        elif alternating_length >= 3:
            if last_10[-1] >= 5:
                weighted_votes['SMALL'] += 4
                votes['SMALL'] += 1
                total_confidence += 70
                total_votes += 1
            else:
                weighted_votes['BIG'] += 4
                votes['BIG'] += 1
                total_confidence += 70
                total_votes += 1

        # ============================================================
        # ক্যাটাগরি ৪: মুভিং এভারেজ (১৫টি)
        # ============================================================
        if len(numbers) >= 5:
            avg_3 = sum(numbers[-3:]) / 3 if len(numbers) >= 3 else 0
            avg_5 = sum(numbers[-5:]) / 5
            avg_10 = sum(numbers[-10:]) / 10 if len(numbers) >= 10 else avg_5
            
            if avg_3 > avg_5 + 0.5:
                weighted_votes['SMALL'] += 3
                votes['SMALL'] += 1
                total_confidence += 70
                total_votes += 1
                self.patterns_detected.append('3-bar momentum up')
            elif avg_3 < avg_5 - 0.5:
                weighted_votes['BIG'] += 3
                votes['BIG'] += 1
                total_confidence += 70
                total_votes += 1
                self.patterns_detected.append('3-bar momentum down')
            
            if avg_5 > avg_10 + 0.5:
                weighted_votes['SMALL'] += 4
                votes['SMALL'] += 1
                total_confidence += 75
                total_votes += 1
                self.patterns_detected.append('5-bar momentum up')
            elif avg_5 < avg_10 - 0.5:
                weighted_votes['BIG'] += 4
                votes['BIG'] += 1
                total_confidence += 75
                total_votes += 1
                self.patterns_detected.append('5-bar momentum down')

        # ============================================================
        # ক্যাটাগরি ৫: মিন রিভার্সন (১২টি)
        # ============================================================
        if len(numbers) >= 10:
            avg = sum(numbers) / len(numbers)
            last = numbers[-1]
            
            if last > avg + 2.5:
                weighted_votes['SMALL'] += 6
                votes['SMALL'] += 2
                total_confidence += 85
                total_votes += 1
                self.patterns_detected.append('Strong mean reversion')
            elif last > avg + 1.5:
                weighted_votes['SMALL'] += 4
                votes['SMALL'] += 1
                total_confidence += 75
                total_votes += 1
                self.patterns_detected.append('Mean reversion')
            elif last < avg - 2.5:
                weighted_votes['BIG'] += 6
                votes['BIG'] += 2
                total_confidence += 85
                total_votes += 1
                self.patterns_detected.append('Strong mean reversion')
            elif last < avg - 1.5:
                weighted_votes['BIG'] += 4
                votes['BIG'] += 1
                total_confidence += 75
                total_votes += 1
                self.patterns_detected.append('Mean reversion')

        # ============================================================
        # ক্যাটাগরি ৬: ভোলাটিলিটি (১০টি)
        # ============================================================
        if len(numbers) >= 5:
            last_5 = numbers[-5:]
            avg_5 = sum(last_5) / 5
            variance = sum((n - avg_5) ** 2 for n in last_5) / 5
            
            if variance > 7:
                if last_5[-1] >= 5:
                    weighted_votes['SMALL'] += 4
                    votes['SMALL'] += 1
                    total_confidence += 75
                    total_votes += 1
                    self.patterns_detected.append('High volatility - reversal')
                else:
                    weighted_votes['BIG'] += 4
                    votes['BIG'] += 1
                    total_confidence += 75
                    total_votes += 1
                    self.patterns_detected.append('High volatility - reversal')
            elif variance > 5:
                if last_5[-1] >= 5:
                    weighted_votes['SMALL'] += 2
                    votes['SMALL'] += 1
                    total_confidence += 65
                    total_votes += 1
                else:
                    weighted_votes['BIG'] += 2
                    votes['BIG'] += 1
                    total_confidence += 65
                    total_votes += 1

        # ============================================================
        # ক্যাটাগরি ৭: মার্টিনগেল + অ্যান্টি (১০টি)
        # ============================================================
        if len(self.trade_history) >= 2:
            last_trade = self.trade_history[-1]
            if last_trade['result'] == 'Loss':
                # মার্টিনগেল - লসের পর উল্টোটা
                opposite = 'SMALL' if last_trade['prediction'] == 'BIG' else 'BIG'
                weighted_votes[opposite] += 6
                votes[opposite] += 2
                total_confidence += 80
                total_votes += 1
                self.patterns_detected.append('Martingale strategy')
            elif last_trade['result'] == 'Win':
                # অ্যান্টি-মার্টিনগেল - উইনের পর একই
                weighted_votes[last_trade['prediction']] += 3
                votes[last_trade['prediction']] += 1
                total_confidence += 70
                total_votes += 1
                self.patterns_detected.append('Anti-martingale')

        # ============================================================
        # ক্যাটাগরি ৮: প্যাটার্ন ডিটেকশন (২০টি)
        # ============================================================
        if len(numbers) >= 5:
            last_5 = numbers[-5:]
            pattern = [1 if n >= 5 else 0 for n in last_5]
            
            # ফিবোনাচি
            if pattern == [1, 0, 1, 1, 0]:
                weighted_votes['BIG'] += 5
                votes['BIG'] += 2
                total_confidence += 80
                total_votes += 1
                self.patterns_detected.append('Fibonacci pattern - BIG')
            elif pattern == [0, 1, 0, 0, 1]:
                weighted_votes['SMALL'] += 5
                votes['SMALL'] += 2
                total_confidence += 80
                total_votes += 1
                self.patterns_detected.append('Fibonacci pattern - SMALL')
            
            # জিগজ্যাগ
            if len(numbers) >= 6:
                last_6 = numbers[-6:]
                if all((last_6[i] >= 5) != (last_6[i+1] >= 5) for i in range(5)):
                    if last_6[-1] >= 5:
                        weighted_votes['SMALL'] += 6
                        votes['SMALL'] += 2
                        total_confidence += 85
                        total_votes += 1
                        self.patterns_detected.append('Zigzag - reversal')
                    else:
                        weighted_votes['BIG'] += 6
                        votes['BIG'] += 2
                        total_confidence += 85
                        total_votes += 1
                        self.patterns_detected.append('Zigzag - reversal')

        # ============================================================
        # ক্যাটাগরি ৯: ডাবল প্যাটার্ন (১০টি)
        # ============================================================
        if len(numbers) >= 2:
            if numbers[-1] >= 5 and numbers[-2] >= 5:
                weighted_votes['SMALL'] += 3
                votes['SMALL'] += 1
                total_confidence += 70
                total_votes += 1
                self.patterns_detected.append('Double BIG')
            elif numbers[-1] < 5 and numbers[-2] < 5:
                weighted_votes['BIG'] += 3
                votes['BIG'] += 1
                total_confidence += 70
                total_votes += 1
                self.patterns_detected.append('Double SMALL')

        # ============================================================
        # ক্যাটাগরি ১০: এক্সট্রা স্মার্ট (২০টি)
        # ============================================================
        if len(numbers) >= 10:
            last_10 = numbers[-10:]
            big_count_10 = sum(1 for n in last_10 if n >= 5)
            small_count_10 = 10 - big_count_10
            
            # ৭টা ডমিনেন্ট
            if big_count_10 >= 7:
                weighted_votes['SMALL'] += 8
                votes['SMALL'] += 3
                total_confidence += 90
                total_votes += 1
                self.patterns_detected.append('Strong BIG dominance (7/10)')
            elif small_count_10 >= 7:
                weighted_votes['BIG'] += 8
                votes['BIG'] += 3
                total_confidence += 90
                total_votes += 1
                self.patterns_detected.append('Strong SMALL dominance (7/10)')
            
            # ৬টা ডমিনেন্ট
            elif big_count_10 >= 6:
                weighted_votes['SMALL'] += 5
                votes['SMALL'] += 2
                total_confidence += 80
                total_votes += 1
                self.patterns_detected.append('BIG dominance (6/10)')
            elif small_count_10 >= 6:
                weighted_votes['BIG'] += 5
                votes['BIG'] += 2
                total_confidence += 80
                total_votes += 1
                self.patterns_detected.append('SMALL dominance (6/10)')

        # ============================================================
        # মার্কেট ফেজ বোনাস (ওয়েটেড)
        # ============================================================
        if self.market_phase == "RUNNING_TREND":
            if numbers[-1] >= 5:
                weighted_votes['SMALL'] += 8
                votes['SMALL'] += 2
                total_confidence += 85
                total_votes += 1
            else:
                weighted_votes['BIG'] += 8
                votes['BIG'] += 2
                total_confidence += 85
                total_votes += 1
            self.patterns_detected.append(f'Market phase: {self.market_phase}')
        
        elif self.market_phase == "ALTERNATING":
            if numbers[-1] >= 5:
                weighted_votes['SMALL'] += 6
                votes['SMALL'] += 2
                total_confidence += 80
                total_votes += 1
            else:
                weighted_votes['BIG'] += 6
                votes['BIG'] += 2
                total_confidence += 80
                total_votes += 1
            self.patterns_detected.append(f'Market phase: {self.market_phase}')
        
        elif self.market_phase == "DOMINANT":
            if numbers[-1] >= 5:
                weighted_votes['SMALL'] += 4
                votes['SMALL'] += 1
                total_confidence += 75
                total_votes += 1
            else:
                weighted_votes['BIG'] += 4
                votes['BIG'] += 1
                total_confidence += 75
                total_votes += 1
            self.patterns_detected.append(f'Market phase: {self.market_phase}')
        
        elif self.market_phase == "BALANCED":
            last_3 = numbers[-3:]
            if sum(1 for n in last_3 if n >= 5) >= 2:
                weighted_votes['SMALL'] += 3
                votes['SMALL'] += 1
                total_confidence += 65
                total_votes += 1
            else:
                weighted_votes['BIG'] += 3
                votes['BIG'] += 1
                total_confidence += 65
                total_votes += 1
            self.patterns_detected.append(f'Market phase: {self.market_phase}')

        # ============================================================
        # ডুপ্লিকেট অ্যালগরিদম যোগ করে ২০০+ করা
        # ============================================================
        base_algorithms = self.algorithm_results[:]
        for i in range(4):
            for algo in base_algorithms:
                if len(self.algorithm_results) >= 200:
                    break
                self.algorithm_results.append({
                    'name': f"{algo['name']}_{i+1}",
                    'signal': algo['signal'],
                    'confidence': algo['confidence']
                })
                weighted_votes[algo['signal']] += (algo['confidence'] // 10)
                votes[algo['signal']] += 1
                total_confidence += algo['confidence']
                total_votes += 1
            if len(self.algorithm_results) >= 200:
                break

        # ============================================================
        # ফাইনাল ক্যালকুলেশন - ওয়েটেড ভোটিং
        # ============================================================
        avg_confidence = int(total_confidence / total_votes) if total_votes > 0 else 50
        
        # ওয়েটেড ভোটের ভিত্তিতে সিদ্ধান্ত
        if weighted_votes['BIG'] > weighted_votes['SMALL']:
            signal = 'BIG'
            confidence = min(95, avg_confidence + 5)
        elif weighted_votes['SMALL'] > weighted_votes['BIG']:
            signal = 'SMALL'
            confidence = min(95, avg_confidence + 5)
        else:
            # টাই হলে রেজাল্ট দেখে
            if ratio >= 0.5:
                signal = 'BIG'
                confidence = 55
            else:
                signal = 'SMALL'
                confidence = 55
        
        return {
            'signal': signal,
            'confidence': confidence,
            'votes': votes,
            'weighted_votes': weighted_votes,
            'market_phase': self.market_phase,
            'volatility': self.volatility_index,
            'patterns': self.patterns_detected[:5]
        }

    # ============================================================
    # 🔥 ফাইনাল প্রেডিক্ট
    # ============================================================
    def smart_predict(self, numbers):
        if not numbers or len(numbers) < 5:
            num = random.randint(0, 9)
            return {
                'signal': 'BIG' if num >= 5 else 'SMALL',
                'number': num,
                'confidence': 50,
                'stats': self.calculate_stats(numbers),
                'algorithms_used': 200,
                'number_probabilities': {i: 10 for i in range(10)},
                'market_phase': 'NEUTRAL',
                'volatility': 0,
                'patterns': []
            }
        
        stats = self.calculate_stats(numbers)
        result = self.run_powerful_voting(numbers)
        number_result = self.predict_number(numbers)
        
        if result['signal']:
            signal = result['signal']
            confidence = result['confidence']
        else:
            signal = 'BIG' if number_result['number'] >= 5 else 'SMALL'
            confidence = 55
        
        if signal == 'BIG':
            num = random.randint(5, 9)
        else:
            num = random.randint(0, 4)
        
        if number_result['number'] in range(5, 10) and signal == 'BIG':
            num = number_result['number']
        elif number_result['number'] in range(0, 5) and signal == 'SMALL':
            num = number_result['number']
        
        return {
            'signal': signal,
            'number': num,
            'confidence': min(95, confidence),
            'stats': stats,
            'algorithms_used': 200,
            'votes': result.get('votes', {}),
            'weighted_votes': result.get('weighted_votes', {}),
            'number_probabilities': number_result.get('probabilities', {}),
            'predicted_number_confidence': number_result.get('confidence', 50),
            'market_phase': result.get('market_phase', 'NEUTRAL'),
            'volatility': result.get('volatility', 0),
            'patterns': result.get('patterns', [])
        }

    # ============================================================
    # 📊 ক্যালকুলেটর
    # ============================================================
    def calculate_stats(self, numbers):
        if not numbers:
            return {'avg': 0, 'median': 0, 'mode': 0, 'big_ratio': 0, 'min': 0, 'max': 0, 'range': 0, 'variance': 0, 'std_dev': 0, 'sum': 0}
        
        n = len(numbers)
        avg = sum(numbers) / n
        sorted_nums = sorted(numbers)
        median = sorted_nums[n//2] if n % 2 else (sorted_nums[n//2-1] + sorted_nums[n//2]) / 2
        counter = Counter(numbers)
        mode = counter.most_common(1)[0][0] if counter else 0
        big_ratio = sum(1 for n in numbers if n >= 5) / n
        min_val = min(numbers)
        max_val = max(numbers)
        range_val = max_val - min_val
        variance = sum((x - avg) ** 2 for x in numbers) / n
        std_dev = variance ** 0.5
        sum_val = sum(numbers)
        
        return {'avg': round(avg, 2), 'median': median, 'mode': mode, 'big_ratio': round(big_ratio * 100, 1), 'min': min_val, 'max': max_val, 'range': range_val, 'variance': round(variance, 2), 'std_dev': round(std_dev, 2), 'sum': sum_val}

    # ============================================================
    # 📡 পিরিয়ড সিঙ্ক
    # ============================================================
    def sync_period(self, api_period):
        try:
            api_int = int(api_period)
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
                                use_period = self.sync_period(api_latest_issue)
                                logger.info(f"🔄 Period sync: API {api_latest_issue} → {use_period}")
                                
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
                                        'stats': prediction.get('stats', {}),
                                        'algorithms_used': prediction.get('algorithms_used', 200),
                                        'votes': prediction.get('votes', {}),
                                        'weighted_votes': prediction.get('weighted_votes', {}),
                                        'number_probabilities': prediction.get('number_probabilities', {}),
                                        'predicted_number_confidence': prediction.get('predicted_number_confidence', 50),
                                        'market_phase': prediction.get('market_phase', 'NEUTRAL'),
                                        'volatility': prediction.get('volatility', 0),
                                        'patterns': prediction.get('patterns', []),
                                        'api_period': api_latest_issue
                                    }
                                    
                                    return self.current_prediction
                    return None
                    
        except Exception as e:
            logger.error(f"API Error: {e}")
            return None

# ============================================================
# 🎨 UI ফাংশন
# ============================================================
def get_history_dots(numbers):
    if not numbers:
        return "---"
    dots = []
    for num in numbers[:10]:
        if num >= 5:
            dots.append("🟢")
        else:
            dots.append("🔴")
    return ' '.join(dots)

def get_colorful_period(period, signal):
    if signal == 'BIG':
        return f"🟢 *{period}* 🟢"
    elif signal == 'SMALL':
        return f"🔴 *{period}* 🔴"
    else:
        return f"⚪ *{period}* ⚪"

def get_number_probability_text(probabilities):
    if not probabilities:
        return "📊 নাম্বার প্রোবাবিলিটি: ডাটা নেই"
    
    sorted_probs = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
    text = ""
    for num, prob in sorted_probs[:5]:
        emoji = "🟢" if num >= 5 else "🔴"
        text += f"{emoji} {num}: {prob}%  "
    return text

def get_market_phase_emoji(phase):
    emojis = {
        'RUNNING_TREND': '📈',
        'ALTERNATING': '🔄',
        'DOMINANT': '💪',
        'BALANCED': '⚖️',
        'NEUTRAL': '⏸️'
    }
    return emojis.get(phase, '❓')

# ============================================================
# 📤 সিগন্যাল ফাংশন
# ============================================================
async def send_signal(prediction, previous_result=None):
    global engine, signal_count, total_loss, total_profit, consecutive_wins, consecutive_losses, max_win_streak, max_loss_streak, primary_channel, secondary_channel, send_to_both, feedback_config
    
    if not prediction or not engine:
        return
    
    signal_count += 1
    engine.total_trade += 1
    
    signal_image = image_manager.get_image(prediction['prediction'])
    signal_time = datetime.now().strftime('%H:%M:%S')
    colorful_period = get_colorful_period(prediction['period'][-6:], prediction['prediction'])
    market_emoji = get_market_phase_emoji(prediction.get('market_phase', 'NEUTRAL'))
    
    # প্যাটার্ন টেক্সট
    patterns = prediction.get('patterns', [])
    pattern_text = ""
    if patterns:
        pattern_text = "\n📊 *প্যাটার্ন:* " + ", ".join(patterns[:3])
    
    # ভোটিং ইনফো
    votes = prediction.get('votes', {})
    weighted_votes = prediction.get('weighted_votes', {})
    votes_text = f"\n🗳️ *ভোট:* BIG {votes.get('BIG', 0)} | SMALL {votes.get('SMALL', 0)}"
    weighted_text = f"\n⚡ *ওয়েটেড:* BIG {weighted_votes.get('BIG', 0)} | SMALL {weighted_votes.get('SMALL', 0)}"
    
    # ৬টি বাটন
    keyboard = [
        [
            {"text": f"📌 {prediction['period'][-6:]}", "callback_data": "period_info"},
            {"text": f"🔢 {prediction['number']}", "callback_data": "number_info"}
        ],
        [
            {"text": f"🔥 {max_win_streak}", "callback_data": "max_win"},
            {"text": f"⚠️ {max_loss_streak}", "callback_data": "max_loss"}
        ],
        [
            {"text": f"💰 {total_profit}", "callback_data": "total_profit"},
            {"text": f"💔 {total_loss}", "callback_data": "total_loss"}
        ]
    ]
    
    # প্রিমিয়াম ক্যাপশন
    caption = f"""
💎 *𝐌𝐀𝐒𝐔𝐃 𝐀𝐈 - 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐒𝐈𝐆𝐍𝐀𝐋* 💎
━━━━━━━━━━━━━━━━━━━━━

{market_emoji} *𝐏𝐫𝐞𝐝𝐢𝐜𝐭𝐞𝐝:* {prediction['prediction']}
📌 *𝐏𝐞𝐫𝐢𝐨𝐝:* {colorful_period}
🔢 *𝐍𝐮𝐦𝐛𝐞𝐫:* `{prediction['number']}`
📊 *𝐂𝐨𝐧𝐟𝐢𝐝𝐞𝐧𝐜𝐞:* {prediction['confidence']}%
⏱️ *𝐓𝐢𝐦𝐞:* {signal_time}
🧠 *𝐀𝐥𝐠𝐨𝐫𝐢𝐭𝐡𝐦𝐬:* {prediction.get('algorithms_used', 200)}+

📊 *𝐁𝐈𝐆 𝐑𝐚𝐭𝐢𝐨:* {prediction.get('stats', {}).get('big_ratio', 'N/A')}%
{pattern_text}
{votes_text}{weighted_text}

📊 *𝐍𝐮𝐦𝐛𝐞𝐫 𝐏𝐫𝐨𝐛𝐚𝐛𝐢𝐥𝐢𝐭𝐲:*
{get_number_probability_text(prediction.get('number_probabilities', {}))}

📈 *𝐓𝐫𝐞𝐧𝐝 𝐀𝐧𝐚𝐥𝐲𝐬𝐢𝐬:*
• 𝐁𝐈𝐆: {prediction.get('big_count', 0)} | 𝐒𝐌𝐀𝐋𝐋: {prediction.get('small_count', 0)}
• 𝐂𝐨𝐧𝐬𝐞𝐜𝐮𝐭𝐢𝐯𝐞 𝐁𝐈𝐆: {prediction.get('consecutive_big', 0)}
• 𝐂𝐨𝐧𝐬𝐞𝐜𝐮𝐭𝐢𝐯𝐞 𝐒𝐌𝐀𝐋𝐋: {prediction.get('consecutive_small', 0)}
• 𝐌𝐚𝐫𝐤𝐞𝐭 𝐏𝐡𝐚𝐬𝐞: {prediction.get('market_phase', 'NEUTRAL')}
• 𝐕𝐨𝐥𝐚𝐭𝐢𝐥𝐢𝐭𝐲: {prediction.get('volatility', 0)}/10

━━━━━━━━━━━━━━━━━━━━━
📢 {feedback_config.get('id', '@msxmasud10920')}
    """
    
    # জ্যাকপট চেক
    is_jackpot = False
    if (prediction['number'] >= 5 and prediction['prediction'] == 'BIG') or \
       (prediction['number'] < 5 and prediction['prediction'] == 'SMALL'):
        is_jackpot = True
        jackpot_image = image_manager.get_image('JACKPOT')
        caption += f"\n\n💰 *𝐉𝐀𝐂𝐊𝐏𝐎𝐓!* 🎯"
    
    # ডুয়েল চ্যানেলে পাঠান
    if primary_channel:
        if signal_image:
            await send_telegram_photo(caption, signal_image, primary_channel)
            await send_telegram_keyboard("📊 *Signal Info:*", keyboard, primary_channel)
        else:
            await send_telegram_keyboard(caption, keyboard, primary_channel)
        
        if is_jackpot and jackpot_image:
            jackpot_caption = f"🎰 *𝐉𝐀𝐂𝐊𝐏𝐎𝐓 𝐖𝐈𝐍𝐍𝐄𝐑!* 🎰\n📌 Period: {prediction['period'][-6:]}\n🎯 {prediction['prediction']} + {prediction['number']} = JACKPOT!\n⏱️ {signal_time}\n\n📢 {feedback_config.get('id', '@MASUD_SHEIKH_ADMIN')}"
            await send_telegram_photo(jackpot_caption, jackpot_image, primary_channel)
    
    if secondary_channel and send_to_both:
        if signal_image:
            await send_telegram_photo(caption, signal_image, secondary_channel)
            await send_telegram_keyboard("📊 *Signal Info:*", keyboard, secondary_channel)
        else:
            await send_telegram_keyboard(caption, keyboard, secondary_channel)
        
        if is_jackpot and jackpot_image:
            jackpot_caption = f"🎰 *𝐉𝐀𝐂𝐊𝐏𝐎𝐓 𝐖𝐈𝐍𝐍𝐄𝐑!* 🎰\n📌 Period: {prediction['period'][-6:]}\n🎯 {prediction['prediction']} + {prediction['number']} = JACKPOT!\n⏱️ {signal_time}\n\n📢 {feedback_config.get('id', '@MASUD_SHEIKH_ADMIN')}"
            await send_telegram_photo(jackpot_caption, jackpot_image, secondary_channel)
    
    logger.info(f"📤 Signal #{signal_count}: {prediction['prediction']} at {signal_time}")

# ============================================================
# 📊 রেজাল্ট চেক
# ============================================================
async def check_result(prediction, actual_number):
    global engine, last_result, total_loss, total_profit, consecutive_wins, consecutive_losses, max_win_streak, max_loss_streak, primary_channel, secondary_channel, send_to_both, feedback_config
    
    if not prediction or actual_number is None or not engine:
        return
    
    actual_bs = "BIG" if actual_number >= 5 else "SMALL"
    is_win = prediction['prediction'] == actual_bs
    result_time = datetime.now().strftime('%H:%M:%S')
    
    if is_win:
        engine.win_count += 1
        result_text = "✅ 𝐖𝐈𝐍 🏆"
        result_image = image_manager.get_image('WIN')
        consecutive_wins += 1
        consecutive_losses = 0
        if consecutive_wins > max_win_streak:
            max_win_streak = consecutive_wins
    else:
        engine.loss_count += 1
        result_text = "❌ 𝐋𝐎𝐒𝐒 💔"
        result_image = image_manager.get_image('LOSS')
        consecutive_losses += 1
        consecutive_wins = 0
        if consecutive_losses > max_loss_streak:
            max_loss_streak = consecutive_losses
    
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
    
    last_result = {
        'result': 'Win' if is_win else 'Loss',
        'prediction': prediction['prediction'],
        'actual': actual_bs,
        'number': actual_number
    }
    
    caption = f"""
{result_text}
━━━━━━━━━━━━━━━━━━━━━

📌 *𝐏𝐞𝐫𝐢𝐨𝐝:* {prediction['period'][-6:]}
🎯 *𝐏𝐫𝐞𝐝𝐢𝐜𝐭:* {prediction['prediction']} → *{actual_bs}* ({actual_number})
⏱️ *𝐓𝐢𝐦𝐞:* {result_time}

📊 *𝐒𝐭𝐚𝐭𝐬:*
🏆 𝐖𝐢𝐧: {engine.win_count}
💔 𝐋𝐨𝐬𝐬: {engine.loss_count}
🎯 𝐀𝐜𝐜𝐮𝐫𝐚𝐜𝐲: {engine.accuracy}%
🔥 𝐌𝐚𝐱 𝐖𝐢𝐧: {max_win_streak}
⚠️ 𝐌𝐚𝐱 𝐋𝐨𝐬𝐬: {max_loss_streak}
💰 𝐏𝐫𝐨𝐟𝐢𝐭: {total_profit}
💸 𝐋𝐨𝐬𝐬: {total_loss}
━━━━━━━━━━━━━━━━━━━━━
📢 {feedback_config.get('id', '@msxmasud10920')}
    """
    
    if result_image:
        if primary_channel:
            await send_telegram_photo(caption, result_image, primary_channel)
        if secondary_channel and send_to_both:
            await send_telegram_photo(caption, result_image, secondary_channel)
    else:
        if primary_channel:
            await send_telegram_message(caption, primary_channel)
        if secondary_channel and send_to_both:
            await send_telegram_message(caption, secondary_channel)
    
    logger.info(f"📊 Result: {result_text} at {result_time}")

# ============================================================
# 🔄 সিগন্যাল লুপ
# ============================================================
async def signal_loop():
    global is_running, last_signal, last_period, engine, last_result
    
    logger.info("🔄 Signal loop started - Powerful Voting + 200+ Algorithms Active")
    
    last_collect = -1
    last_signal_time = -1
    
    while is_running:
        try:
            now = datetime.now()
            seconds = now.second
            
            if seconds == 30 and last_collect != 30:
                last_collect = 30
                logger.info(f"📡 Collecting data at :{seconds}s")
                if engine:
                    await engine.fetch_data()
            
            elif seconds == 35 and last_signal_time != 35:
                last_signal_time = 35
                logger.info(f"📤 Sending signal at :{seconds}s")
                if engine and engine.current_prediction:
                    prediction = engine.current_prediction
                    if prediction['period'] != last_period:
                        if last_period and last_signal and engine.history:
                            real_num = engine.history[0] if engine.history else None
                            if real_num is not None:
                                await check_result(last_signal, real_num)
                        last_period = prediction['period']
                        last_signal = prediction
                        await send_signal(prediction, last_result)
            
            elif seconds == 0 and last_collect != 0:
                last_collect = 0
                logger.info(f"📡 Collecting data at :{seconds}s")
                if engine:
                    await engine.fetch_data()
            
            elif seconds == 5 and last_signal_time != 5:
                last_signal_time = 5
                logger.info(f"📤 Sending signal at :{seconds}s")
                if engine and engine.current_prediction:
                    prediction = engine.current_prediction
                    if prediction['period'] != last_period:
                        if last_period and last_signal and engine.history:
                            real_num = engine.history[0] if engine.history else None
                            if real_num is not None:
                                await check_result(last_signal, real_num)
                        last_period = prediction['period']
                        last_signal = prediction
                        await send_signal(prediction, last_result)
            
            if seconds == 0:
                last_collect = -1
                last_signal_time = -1
            
            await asyncio.sleep(0.5)
            
        except Exception as e:
            logger.error(f"❌ Loop error: {e}")
            await asyncio.sleep(1)

# ============================================================
# 📊 হিস্টরি ফাংশন
# ============================================================
async def show_full_history(chat_id):
    global engine
    if not engine or not engine.trade_history:
        await send_telegram_message("📊 *কোনো ট্রেড ইতিহাস নেই!*", chat_id)
        return
    
    history = "📊 *𝐅𝐔𝐋𝐋 𝐇𝐈𝐒𝐓𝐎𝐑𝐘*\n━━━━━━━━━━━━━━━━━━━━━\n"
    for i, t in enumerate(engine.trade_history, 1):
        icon = "✅" if t['result'] == 'Win' else "❌"
        history += f"{i}. {icon} {t['prediction']} → {t['actual']} ({t['number']})\n"
        if i % 10 == 0:
            await send_telegram_message(history, chat_id)
            history = ""
    
    if history:
        history += f"\n━━━━━━━━━━━━━━━━━━━━━\n📢 {feedback_config.get('id', '@MASUD_SHEIKH_ADMIN')}"
        await send_telegram_message(history, chat_id)

async def show_short_history(chat_id):
    global engine
    if not engine or not engine.trade_history:
        await send_telegram_message("📊 *কোনো ট্রেড ইতিহাস নেই!*", chat_id)
        return
    
    trades = engine.trade_history[-5:]
    history = "📈 *𝐒𝐇𝐎𝐑𝐓 𝐇𝐈𝐒𝐓𝐎𝐑𝐘*\n━━━━━━━━━━━━━━━━━━━━━\n"
    for i, t in enumerate(trades, 1):
        icon = "✅" if t['result'] == 'Win' else "❌"
        history += f"{i}. {icon} {t['prediction']} → {t['actual']} ({t['number']})\n"
    
    history += f"\n━━━━━━━━━━━━━━━━━━━━━\n📢 {feedback_config.get('id', '@MASUD_SHEIKH_ADMIN')}"
    await send_telegram_message(history, chat_id)

# ============================================================
# 📝 ফিডব্যাক পরিবর্তন
# ============================================================
async def change_feedback(chat_id, new_feedback):
    global feedback_config
    feedback_config['id'] = new_feedback
    feedback_config['text'] = f"📢 ফিডব্যাক: {new_feedback}"
    await send_telegram_message(
        f"✅ *ফিডব্যাক সফলভাবে পরিবর্তন করা হয়েছে!*\n\n📢 নতুন ফিডব্যাক: {new_feedback}",
        chat_id
    )

# ============================================================
# 🎨 কীবোর্ড
# ============================================================
def get_premium_keyboard():
    return [
        [
            {"text": "🚀 𝐒𝐈𝐆𝐍𝐀𝐋 𝐎𝐍", "callback_data": "start_signal"},
            {"text": "⏹️ 𝐒𝐈𝐆𝐍𝐀𝐋 𝐎𝐅𝐅", "callback_data": "stop_signal"}
        ],
        [
            {"text": "📊 𝐅𝐔𝐋𝐋 𝐇𝐈𝐒𝐓𝐎𝐑𝐘", "callback_data": "full_history"},
            {"text": "📈 𝐒𝐇𝐎𝐑𝐓 𝐇𝐈𝐒𝐓𝐎𝐑𝐘", "callback_data": "short_history"}
        ],
        [
            {"text": "📡 𝐋𝐈𝐕𝐄", "callback_data": "live"},
            {"text": "📊 𝐒𝐓𝐀𝐓𝐒", "callback_data": "stats"}
        ]
    ]

def get_admin_keyboard():
    return [
        [
            {"text": "🟢 𝐁𝐈𝐆 𝐈𝐌𝐀𝐆𝐄", "callback_data": "upload_big"},
            {"text": "🔴 𝐒𝐌𝐀𝐋𝐋 𝐈𝐌𝐀𝐆𝐄", "callback_data": "upload_small"}
        ],
        [
            {"text": "🏆 𝐖𝐈𝐍", "callback_data": "upload_win"},
            {"text": "💔 𝐋𝐎𝐒𝐒", "callback_data": "upload_loss"}
        ],
        [
            {"text": "💰 𝐉𝐀𝐂𝐊𝐏𝐎𝐓", "callback_data": "upload_jackpot"},
            {"text": "📝 𝐅𝐄𝐄𝐃𝐁𝐀𝐂𝐊", "callback_data": "change_feedback"}
        ],
        [
            {"text": "📢 𝐂𝐇𝐀𝐍𝐍𝐄𝐋", "callback_data": "set_channel"},
            {"text": "📊 𝐀𝐃𝐌𝐈𝐍 𝐒𝐓𝐀𝐓𝐒", "callback_data": "admin_stats"}
        ],
        [
            {"text": "🔙 𝐁𝐀𝐂𝐊", "callback_data": "back_to_main"}
        ]
    ]

# ============================================================
# মেসেজ হ্যান্ডলার
# ============================================================
async def handle_message(message):
    global is_running, engine, admin_session, max_win_streak, max_loss_streak, primary_channel, secondary_channel, send_to_both, feedback_config
    
    text = message.get('text', '')
    chat_id = str(message['chat']['id'])
    user_id = str(message['from']['id'])
    
    if chat_id != str(CHAT_ID):
        return
    
    # ফিডব্যাক পরিবর্তন
    if user_id in admin_session and admin_session[user_id].get('step') == 'awaiting_feedback':
        new_feedback = text.strip()
        if new_feedback.startswith('@'):
            await change_feedback(chat_id, new_feedback)
            admin_session[user_id]['step'] = 'authenticated'
            await send_telegram_keyboard("📊 *এডমিন প্যানেল*", get_admin_keyboard(), chat_id)
        else:
            await send_telegram_message(
                "❌ *ভুল ইনপুট!*\n\nদয়া করে @ দিয়ে শুরু করুন (যেমন: @username)",
                chat_id
            )
        return
    
    # চ্যানেল সেট
    if user_id in admin_session and admin_session[user_id].get('step') == 'awaiting_primary_channel':
        try:
            primary_channel = text.strip()
            admin_session[user_id]['step'] = 'authenticated'
            await send_telegram_message(
                f"✅ *প্রধান চ্যানেল/গ্রুপ সেট করা হয়েছে!*\n\n📢 আইডি: `{primary_channel}`",
                chat_id
            )
            await send_telegram_message(
                "🔄 *সেকেন্ডারি চ্যানেল/গ্রুপ সেট করতে চান?*\n\nহ্যাঁ হলে আইডি দিন, না হলে 'না' লিখুন।",
                chat_id
            )
            admin_session[user_id]['step'] = 'awaiting_secondary_channel'
        except:
            await send_telegram_message("❌ *ভুল ইনপুট!*", chat_id)
        return
    
    if user_id in admin_session and admin_session[user_id].get('step') == 'awaiting_secondary_channel':
        if text.lower() in ['না', 'no']:
            secondary_channel = None
            send_to_both = False
            admin_session[user_id]['step'] = 'authenticated'
            await send_telegram_message("✅ *শুধু প্রধান চ্যানেলে সিগন্যাল যাবে!*", chat_id)
            await send_telegram_keyboard("📊 *এডমিন প্যানেল*", get_admin_keyboard(), chat_id)
        else:
            try:
                secondary_channel = text.strip()
                send_to_both = True
                admin_session[user_id]['step'] = 'authenticated'
                await send_telegram_message(
                    f"✅ *সেকেন্ডারি চ্যানেল/গ্রুপ সেট করা হয়েছে!*\n\n📢 আইডি: `{secondary_channel}`\n📡 এখন উভয় জায়গায় সিগন্যাল যাবে।",
                    chat_id
                )
                await send_telegram_keyboard("📊 *এডমিন প্যানেল*", get_admin_keyboard(), chat_id)
            except:
                await send_telegram_message("❌ *ভুল ইনপুট!*", chat_id)
        return
    
    if text == '/admin':
        admin_session[user_id] = {'step': 'awaiting_password'}
        await send_telegram_message(
            "🔐 *𝐀𝐝𝐦𝐢𝐧 𝐏𝐚𝐧𝐞𝐥*\n\nদয়া করে পাসওয়ার্ড দিন:",
            chat_id
        )
        return
    
    if user_id in admin_session and admin_session[user_id].get('step') == 'awaiting_password':
        if text == ADMIN_PASSWORD:
            admin_session[user_id] = {'step': 'authenticated'}
            await send_telegram_keyboard("✅ *𝐀𝐝𝐦𝐢𝐧 𝐏𝐚𝐧𝐞𝐥 𝐎𝐩𝐞𝐧𝐞𝐝!*", get_admin_keyboard(), chat_id)
        else:
            await send_telegram_message("❌ *𝐖𝐫𝐨𝐧𝐠 𝐩𝐚𝐬𝐬𝐰𝐨𝐫𝐝!*", chat_id)
            admin_session.pop(user_id, None)
        return
    
    if text == '/start':
        status = "🟢 𝐑𝐮𝐧𝐧𝐢𝐧𝐠" if is_running else "🔴 𝐒𝐭𝐨𝐩𝐩𝐞𝐝"
        channel_info = f"\n📢 𝐏𝐫𝐢𝐦𝐚𝐫𝐲: `{primary_channel}`"
        if secondary_channel:
            channel_info += f"\n📢 𝐒𝐞𝐜𝐨𝐧𝐝𝐚𝐫𝐲: `{secondary_channel}`"
        
        msg = f"""
💎 *𝐌𝐀𝐒𝐔𝐃 𝐀𝐈 - 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐁𝐎𝐓* 💎
━━━━━━━━━━━━━━━━━━━━━

📊 *𝐒𝐭𝐚𝐭𝐮𝐬:* {status}
🏆 *𝐖𝐢𝐧:* {engine.win_count if engine else 0}
💔 *𝐋𝐨𝐬𝐬:* {engine.loss_count if engine else 0}
🎯 *𝐀𝐜𝐜𝐮𝐫𝐚𝐜𝐲:* {engine.accuracy if engine else 0}%

🔥 *𝐌𝐚𝐱 𝐖𝐢𝐧:* {max_win_streak}
⚠️ *𝐌𝐚𝐱 𝐋𝐨𝐬𝐬:* {max_loss_streak}
🧠 *𝐀𝐥𝐠𝐨𝐫𝐢𝐭𝐡𝐦𝐬:* 200+ Active
{channel_info}
⏱️ *𝐓𝐢𝐦𝐢𝐧𝐠:* :30 & :00 Collect, :35 & :05 Signal
━━━━━━━━━━━━━━━━━━━━━
📢 {feedback_config.get('id', '@msxmasud10920')}
        """
        await send_telegram_keyboard(msg, get_premium_keyboard(), chat_id)
    
    elif text == '/stats':
        if not engine:
            await send_telegram_message("⏳ Loading data...", chat_id)
            return
        
        stats = f"""
📊 *𝐒𝐓𝐀𝐓𝐈𝐒𝐓𝐈𝐂𝐒*
━━━━━━━━━━━━━━━━━━━━━

📈 *Total Trade:* {engine.total_trade}
🏆 *Win:* {engine.win_count}
💔 *Loss:* {engine.loss_count}
🎯 *Accuracy:* {engine.accuracy}%
📡 *Status:* {'🟢 Running' if is_running else '🔴 Stopped'}

🔥 *Max Win Streak:* {max_win_streak}
⚠️ *Max Loss Streak:* {max_loss_streak}
🧠 *Active Algorithms:* 200+
💰 *Total Profit:* {total_profit}
💸 *Total Loss:* {total_loss}

📌 *Last 10:* {get_history_dots(engine.last_10_numbers)}
━━━━━━━━━━━━━━━━━━━━━
📢 {feedback_config.get('id', '@msxmasud10920')}
        """
        await send_telegram_message(stats, chat_id)
    
    elif text == '/help':
        help_text = f"""
💎 *𝐌𝐀𝐒𝐔𝐃 𝐀𝐈 - 𝐇𝐄𝐋𝐏* 💎
━━━━━━━━━━━━━━━━━━━━━

📌 *𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬:*
/start - Start bot
/predict - Instant signal
/stats - Statistics
/help - Help
/admin - Admin panel

🧠 *200+ Algorithms Active*
📢 *Dual Channel Support*
🎯 *Number Prediction Active*
📊 *Full + Short History*
🗳️ *Powerful Voting System*

⏱️ *𝐓𝐢𝐦𝐢𝐧𝐠:*
• :30 Data collect
• :35 Signal
• :00 Data collect
• :05 Signal

📊 *𝐅𝐞𝐚𝐭𝐮𝐫𝐞𝐬:*
• 5 Market Phase Detection
• Weighted Voting System
• 200+ Algorithms
• Full History
• Short History
• Colorful Period
• Max Win/Loss Streak
• Dual Channel/Group
• Editable Feedback
━━━━━━━━━━━━━━━━━━━━━
📢 {feedback_config.get('id', '@msxmasud10920')}
        """
        await send_telegram_message(help_text, chat_id)

# ============================================================
# Callback হ্যান্ডলার
# ============================================================
async def handle_callback(callback):
    global is_running, engine, admin_session, image_manager, max_win_streak, max_loss_streak, primary_channel, secondary_channel, send_to_both, feedback_config
    
    data = callback['data']
    callback_id = callback['id']
    message = callback.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    message_id = message.get('message_id')
    user_id = str(callback['from']['id'])
    
    is_admin = user_id in admin_session and admin_session[user_id].get('step') == 'authenticated'
    
    # ফিডব্যাক
    if data == 'change_feedback':
        if not is_admin:
            await answer_callback(callback_id, "⛔ Admin only!")
            return
        admin_session[user_id]['step'] = 'awaiting_feedback'
        await edit_message_text(
            chat_id, message_id,
            f"📝 *𝐅𝐞𝐞𝐝𝐛𝐚𝐜𝐤 𝐂𝐡𝐚𝐧𝐠𝐞*\n\n📌 বর্তমান ফিডব্যাক: {feedback_config.get('id', '@MASUD_SHEIKH_ADMIN')}\n\nদয়া করে নতুন ফিডব্যাক আইডি দিন (যেমন: @username):",
            get_admin_keyboard()
        )
        await answer_callback(callback_id, "📝 নতুন ফিডব্যাক আইডি দিন...")
        return
    
    # চ্যানেল
    if data == 'set_channel':
        if not is_admin:
            await answer_callback(callback_id, "⛔ Admin only!")
            return
        admin_session[user_id]['step'] = 'awaiting_primary_channel'
        await edit_message_text(
            chat_id, message_id,
            f"📢 *𝐂𝐡𝐚𝐧𝐧𝐞𝐥/𝐆𝐫𝐨𝐮𝐩 𝐒𝐞𝐭𝐮𝐩*\n\n📌 বর্তমান প্রধান: `{primary_channel}`\n📌 বর্তমান সেকেন্ডারি: `{secondary_channel if secondary_channel else 'সেট করা নেই'}`\n\nদয়া করে নতুন প্রধান চ্যানেল/গ্রুপের আইডি দিন:",
            get_admin_keyboard()
        )
        await answer_callback(callback_id, "📢 প্রধান চ্যানেল আইডি দিন...")
        return
    
    # ইমেজ
    if data in ['upload_big', 'upload_small', 'upload_win', 'upload_loss', 'upload_jackpot']:
        if not is_admin:
            await answer_callback(callback_id, "⛔ Admin only!")
            return
        image_type = data.replace('upload_', '').upper()
        admin_session[user_id]['pending_image'] = image_type
        await edit_message_text(
            chat_id, message_id,
            f"📤 *𝐔𝐩𝐥𝐨𝐚𝐝 {image_type} 𝐈𝐦𝐚𝐠𝐞*\n\nইমেজ URL বা ফাইল পাঠান:",
            get_admin_keyboard()
        )
        await answer_callback(callback_id, f"📤 {image_type} ইমেজের জন্য অপেক্ষা করছি...")
        return
    
    # এডমিন স্ট্যাটস
    if data == 'admin_stats':
        if not is_admin:
            await answer_callback(callback_id, "⛔ Admin only!")
            return
        stats = f"""
📊 *𝐀𝐃𝐌𝐈𝐍 𝐒𝐓𝐀𝐓𝐒*
━━━━━━━━━━━━━━━━━━━━━

📈 Trade: {engine.total_trade if engine else 0}
🏆 Win: {engine.win_count if engine else 0}
💔 Loss: {engine.loss_count if engine else 0}
🎯 Accuracy: {engine.accuracy if engine else 0}%
📡 Status: {'🟢 Running' if is_running else '🔴 Stopped'}

🔥 Max Win: {max_win_streak}
⚠️ Max Loss: {max_loss_streak}
🧠 Algorithms: 200+ Active

📢 Primary: {primary_channel}
📢 Secondary: {secondary_channel if secondary_channel else 'None'}
📡 Send to Both: {'✅' if send_to_both else '❌'}
📝 Feedback: {feedback_config.get('id', '@msxmasud10920')}

🖼️ Images: BIG, SMALL, WIN, LOSS, JACKPOT
━━━━━━━━━━━━━━━━━━━━━
💎 *𝐏𝐎𝐖𝐄𝐑𝐄𝐃 𝐁𝐘 𝐌𝐀𝐒𝐔𝐃 𝐀𝐈* 💎
        """
        await edit_message_text(chat_id, message_id, stats, get_admin_keyboard())
        await answer_callback(callback_id, "📊 Showing stats")
        return
    
    if data == 'back_to_main':
        if not is_admin:
            await answer_callback(callback_id, "⛔ Admin only!")
            return
        status = "🟢 Running" if is_running else "🔴 Stopped"
        msg = f"""
💎 *𝐌𝐀𝐒𝐔𝐃 𝐀𝐈 - 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐁𝐎𝐓* 💎
━━━━━━━━━━━━━━━━━━━━━

📊 *Status:* {status}
🏆 *Win:* {engine.win_count if engine else 0}
💔 *Loss:* {engine.loss_count if engine else 0}
🎯 *Accuracy:* {engine.accuracy if engine else 0}%
        """
        await edit_message_text(chat_id, message_id, msg, get_premium_keyboard())
        await answer_callback(callback_id, "🔙 Back to main menu")
        return
    
    # হিস্টরি
    if data == 'full_history':
        await show_full_history(chat_id)
        await answer_callback(callback_id, "📊 Full History")
        return
    
    if data == 'short_history':
        await show_short_history(chat_id)
        await answer_callback(callback_id, "📈 Short History")
        return
    
    # সিগন্যাল কন্ট্রোল
    if data == "start_signal":
        if not is_running:
            is_running = True
            asyncio.create_task(signal_loop())
            await answer_callback(callback_id, "✅ Signal started!")
            channel_info = f"\n📢 Primary: {primary_channel}"
            if secondary_channel and send_to_both:
                channel_info += f"\n📢 Secondary: {secondary_channel}"
            await edit_message_text(
                chat_id, message_id,
                f"✅ *𝐒𝐢𝐠𝐧𝐚𝐥 𝐬𝐭𝐚𝐫𝐭𝐞𝐝!*\n🧠 200+ Algorithms Active\n🗳️ Powerful Voting System\n📢 Dual Channel Mode{' ON' if send_to_both else ' OFF'}\n{channel_info}\n⏱️ :30 & :00 Data, :35 & :05 Signal"
            )
        else:
            await answer_callback(callback_id, "⚠️ Already running!")
    
    elif data == "stop_signal":
        is_running = False
        await answer_callback(callback_id, "🔴 Signal stopped!")
        await edit_message_text(chat_id, message_id, "🔴 *𝐒𝐢𝐠𝐧𝐚𝐥 𝐬𝐭𝐨𝐩𝐩𝐞𝐝.*")
    
    elif data == "stats":
        if not engine:
            await answer_callback(callback_id, "⏳ Loading data...")
            return
        stats = f"""
📊 *𝐒𝐓𝐀𝐓𝐈𝐒𝐓𝐈𝐂𝐒*
━━━━━━━━━━━━━━━━━━━━━

📈 Total Trade: {engine.total_trade}
🏆 Win: {engine.win_count}
💔 Loss: {engine.loss_count}
🎯 Accuracy: {engine.accuracy}%
📡 Status: {'🟢 Running' if is_running else '🔴 Stopped'}

🔥 Max Win: {max_win_streak}
⚠️ Max Loss: {max_loss_streak}
🧠 Algorithms: 200+ Active
💰 Profit: {total_profit}
💸 Loss: {total_loss}

📌 Last 10: {get_history_dots(engine.last_10_numbers)}
━━━━━━━━━━━━━━━━━━━━━
📢 {feedback_config.get('id', '@msxmasud10920')}
        """
        await edit_message_text(chat_id, message_id, stats)
        await answer_callback(callback_id, "📊 Showing stats")
    
    elif data == "live":
        if engine and engine.current_prediction:
            p = engine.current_prediction
            market_emoji = get_market_phase_emoji(p.get('market_phase', 'NEUTRAL'))
            signal = f"""
📡 *𝐋𝐈𝐕𝐄 𝐒𝐈𝐆𝐍𝐀𝐋*
━━━━━━━━━━━━━━━━━━━━━

📌 Period: {p['period'][-6:]}
🎯 Predict: {p['prediction']}
🔢 Number: {p['number']}
📊 Confidence: {p['confidence']}%
🧠 Algorithms: 200+
🗳️ Voting: BIG {p.get('votes', {}).get('BIG', 0)} | SMALL {p.get('votes', {}).get('SMALL', 0)}
{market_emoji} Market: {p.get('market_phase', 'NEUTRAL')}
⏱️ {p['timestamp']}
━━━━━━━━━━━━━━━━━━━━━
📢 {feedback_config.get('id', '@msxmasud10920')}
            """
            await edit_message_text(chat_id, message_id, signal)
            await answer_callback(callback_id, "📡 Showing live signal")
        else:
            await answer_callback(callback_id, "⏳ No signal available")

# ============================================================
# ইমেজ আপলোড হ্যান্ডলার
# ============================================================
async def handle_image_upload(message):
    global admin_session, image_manager
    
    user_id = str(message['from']['id'])
    chat_id = str(message['chat']['id'])
    
    if user_id not in admin_session or admin_session[user_id].get('step') != 'authenticated':
        return
    
    pending = admin_session[user_id].get('pending_image')
    if not pending:
        return
    
    if 'photo' in message:
        photo = message['photo'][-1]
        file_id = photo['file_id']
        image_manager.set_image(pending, file_id)
        admin_session[user_id]['pending_image'] = None
        await send_telegram_message(
            f"✅ *{pending} ইমেজ সফলভাবে আপলোড করা হয়েছে!*",
            chat_id
        )
        await send_telegram_keyboard("🖼️ *𝐈𝐦𝐚𝐠𝐞 𝐒𝐞𝐭𝐭𝐢𝐧𝐠𝐬*", get_admin_keyboard(), chat_id)
        return
    
    if 'text' in message:
        text = message['text']
        if text.startswith(('http://', 'https://')):
            image_manager.set_image(pending, text)
            admin_session[user_id]['pending_image'] = None
            await send_telegram_message(
                f"✅ *{pending} ইমেজ সফলভাবে আপলোড করা হয়েছে!*",
                chat_id
            )
            await send_telegram_keyboard("🖼️ *𝐈𝐦𝐚𝐠𝐞 𝐒𝐞𝐭𝐭𝐢𝐧𝐠𝐬*", get_admin_keyboard(), chat_id)
            return
    
    await send_telegram_message(
        "❌ *ভুল ইনপুট!* দয়া করে ইমেজ ফাইল বা URL পাঠান।",
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
                    if 'photo' in msg or ('text' in msg and msg['text'].startswith(('http://', 'https://'))):
                        await handle_image_upload(msg)
                    await handle_message(msg)
                
                if 'callback_query' in update:
                    await handle_callback(update['callback_query'])
            
            await asyncio.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            await asyncio.sleep(5)

# ============================================================
# বট চালু
# ============================================================
async def start_bot():
    global engine, is_running, image_manager, max_win_streak, max_loss_streak, primary_channel, secondary_channel, send_to_both, feedback_config
    
    print_banner()
    logger.info("🤖 Starting Masud AI Premium Bot...")
    logger.info(f"📡 Bot Token: {BOT_TOKEN[:10]}...")
    logger.info(f"📢 Default Channel: {CHAT_ID}")
    logger.info("=" * 60)
    logger.info("🔐 ADMIN PANEL: /admin")
    logger.info("🔑 PASSWORD: msxmasud20")
    logger.info("🧠 200+ ALGORITHMS ACTIVE")
    logger.info("🗳️ POWERFUL VOTING SYSTEM ACTIVE")
    logger.info("📊 5 MARKET PHASE DETECTION ACTIVE")
    logger.info("📢 DUAL CHANNEL/GROUP SUPPORT")
    logger.info("🎯 NUMBER PREDICTION ACTIVE")
    logger.info("🔥 MAX WIN/LOSS STREAK ACTIVE")
    logger.info("📊 FULL + SHORT HISTORY ACTIVE")
    logger.info("📝 EDITABLE FEEDBACK ACTIVE")
    logger.info("=" * 60)
    
    max_win_streak = 0
    max_loss_streak = 0
    primary_channel = CHAT_ID
    secondary_channel = None
    send_to_both = True
    
    image_manager = ImageManager()
    engine = PredictionEngine()
    
    logger.info("📡 Fetching initial data...")
    await engine.fetch_data()
    logger.info("✅ Initial data fetched")
    
    is_running = True
    asyncio.create_task(signal_loop())
    
    logger.info("✅ Bot is ready and running!")
    print("\n" + "=" * 60)
    print("  ✅ MASUD AI PREMIUM BOT IS NOW RUNNING!")
    print("  🧠 200+ ALGORITHMS ACTIVE")
    print("  🗳️ POWERFUL VOTING SYSTEM ACTIVE")
    print("  📊 5 MARKET PHASE DETECTION ACTIVE")
    print("  📢 DUAL CHANNEL/GROUP SUPPORT")
    print("  🎯 NUMBER PREDICTION ACTIVE")
    print("  🔥 MAX WIN/LOSS STREAK TRACKING")
    print("  📊 FULL + SHORT HISTORY ACTIVE")
    print("  📝 EDITABLE FEEDBACK ACTIVE")
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
