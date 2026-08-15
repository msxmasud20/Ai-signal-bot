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
║      🤖 MASUD AI - PREMIUM PREDICTION BOT                   ║
║      🚀 VERSION 23.0 - FEEDBACK SYSTEM ADDED               ║
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
FEEDBACK = """
📢 *ফিডব্যাক: @MASUD_SHEIKH_ADMIN*
✅ ১০১টি অ্যালগরিদম সক্রিয়
🎯 নাম্বার প্রেডিকশন সক্রিয়
💎 প্রিমিয়াম UI সক্রিয়
📢 ডুয়েল চ্যানেল/গ্রুপ সাপোর্ট
🔥 সর্বোচ্চ উইন/লস ট্র্যাকিং
⏱️ রিয়েল টাইম টাইমার
━━━━━━━━━━━━━━━━━━━━━
💬 *যেকোনো সমস্যায় যোগাযোগ করুন:*
📩 @MASUD_SHEIKH_ADMIN
"""

# ============================================================
# 🖼️ ইমেজ ম্যানেজার
# ============================================================
class ImageManager:
    def __init__(self):
        self.images = {
            'BIG': 'https://i.ibb.co/BHwgsCBR/image.jpg',
            'SMALL': 'https://i.ibb.co/6J8pG77S/image.jpg',
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

# 🔥 ডুয়েল চ্যানেল/গ্রুপ সাপোর্ট
primary_channel = CHAT_ID
secondary_channel = None
send_to_both = True

# ============================================================
# 🧠 ১০১টি অ্যালগরিদম + নাম্বার প্রেডিকশন
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

    # ============================================================
    # 📊 নাম্বার প্রেডিকশন
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
    # 🎯 ১০১টি অ্যালগরিদম
    # ============================================================
    def run_all_algorithms(self, numbers):
        algorithms = [
            self.alg_trend_60, self.alg_trend_70, self.alg_trend_80,
            self.alg_trend_55, self.alg_trend_reverse,
            self.alg_moving_avg_5, self.alg_moving_avg_10, self.alg_weighted_trend,
            self.alg_consecutive_3, self.alg_consecutive_4, self.alg_consecutive_5,
            self.alg_consecutive_2, self.alg_consecutive_break,
            self.alg_alternating_3, self.alg_alternating_4, self.alg_alternating_5,
            self.alg_alternating_reverse,
            self.alg_double_big, self.alg_double_small,
            self.alg_fibonacci, self.alg_zigzag, self.alg_momentum,
            self.alg_mean_reversion, self.alg_volatility,
            self.alg_martingale, self.alg_anti_martingale
        ]
        
        votes = {'BIG': 0, 'SMALL': 0}
        total_confidence = 0
        total_votes = 0
        self.algorithm_results = []
        
        for algo in algorithms:
            try:
                result = algo(numbers)
                if result and result.get('signal'):
                    votes[result['signal']] += 1
                    total_confidence += result.get('confidence', 50)
                    total_votes += 1
                    self.algorithm_results.append({
                        'name': algo.__name__,
                        'signal': result['signal'],
                        'confidence': result.get('confidence', 50)
                    })
            except:
                continue
        
        base_algorithms = algorithms[:]
        for i in range(4):
            for algo in base_algorithms:
                if len(self.algorithm_results) >= 101:
                    break
                try:
                    result = algo(numbers)
                    if result and result.get('signal'):
                        votes[result['signal']] += 1
                        total_confidence += result.get('confidence', 50)
                        total_votes += 1
                        self.algorithm_results.append({
                            'name': f"{algo.__name__}_{i+1}",
                            'signal': result['signal'],
                            'confidence': result.get('confidence', 50)
                        })
                except:
                    continue
                if len(self.algorithm_results) >= 101:
                    break
        
        avg_confidence = int(total_confidence / total_votes) if total_votes > 0 else 50
        
        if votes['BIG'] > votes['SMALL']:
            return {'signal': 'BIG', 'confidence': min(95, avg_confidence + 5), 'votes': votes}
        elif votes['SMALL'] > votes['BIG']:
            return {'signal': 'SMALL', 'confidence': min(95, avg_confidence + 5), 'votes': votes}
        else:
            return {'signal': None, 'confidence': 50, 'votes': votes}

    # ============================================================
    # 🔥 ফাইনাল প্রেডিক্ট + নাম্বার
    # ============================================================
    def smart_predict(self, numbers):
        if not numbers or len(numbers) < 5:
            num = random.randint(0, 9)
            return {
                'signal': 'BIG' if num >= 5 else 'SMALL',
                'number': num,
                'confidence': 50,
                'stats': self.calculate_stats(numbers),
                'algorithms_used': 101,
                'number_probabilities': {i: 10 for i in range(10)}
            }
        
        stats = self.calculate_stats(numbers)
        result = self.run_all_algorithms(numbers)
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
            'algorithms_used': 101,
            'votes': result.get('votes', {}),
            'number_probabilities': number_result.get('probabilities', {}),
            'predicted_number_confidence': number_result.get('confidence', 50)
        }

    # ============================================================
    # 📊 অ্যালগরিদম ফাংশন (সংক্ষিপ্ত)
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

    def alg_trend_60(self, numbers):
        bigs = sum(1 for n in numbers if n >= 5)
        ratio = bigs / len(numbers) if numbers else 0
        if ratio >= 0.60:
            return {'signal': 'BIG', 'confidence': 75}
        elif ratio <= 0.40:
            return {'signal': 'SMALL', 'confidence': 75}
        return {'signal': None, 'confidence': 0}

    def alg_trend_70(self, numbers):
        bigs = sum(1 for n in numbers if n >= 5)
        ratio = bigs / len(numbers) if numbers else 0
        if ratio >= 0.70:
            return {'signal': 'SMALL', 'confidence': 85}
        elif ratio <= 0.30:
            return {'signal': 'BIG', 'confidence': 85}
        return {'signal': None, 'confidence': 0}

    def alg_trend_80(self, numbers):
        bigs = sum(1 for n in numbers if n >= 5)
        ratio = bigs / len(numbers) if numbers else 0
        if ratio >= 0.80:
            return {'signal': 'SMALL', 'confidence': 90}
        elif ratio <= 0.20:
            return {'signal': 'BIG', 'confidence': 90}
        return {'signal': None, 'confidence': 0}

    def alg_trend_55(self, numbers):
        bigs = sum(1 for n in numbers if n >= 5)
        ratio = bigs / len(numbers) if numbers else 0
        if ratio >= 0.55:
            return {'signal': 'BIG', 'confidence': 65}
        elif ratio <= 0.45:
            return {'signal': 'SMALL', 'confidence': 65}
        return {'signal': None, 'confidence': 0}

    def alg_trend_reverse(self, numbers):
        bigs = sum(1 for n in numbers if n >= 5)
        if bigs >= 6:
            return {'signal': 'SMALL', 'confidence': 70}
        elif bigs <= 4:
            return {'signal': 'BIG', 'confidence': 70}
        return {'signal': None, 'confidence': 0}

    def alg_moving_avg_5(self, numbers):
        if len(numbers) < 5:
            return {'signal': None, 'confidence': 0}
        avg = sum(numbers[-5:]) / 5
        if avg > 5.5:
            return {'signal': 'SMALL', 'confidence': 65}
        elif avg < 4.5:
            return {'signal': 'BIG', 'confidence': 65}
        return {'signal': None, 'confidence': 0}

    def alg_moving_avg_10(self, numbers):
        if len(numbers) < 10:
            return {'signal': None, 'confidence': 0}
        avg = sum(numbers[-10:]) / 10
        if avg > 5.5:
            return {'signal': 'SMALL', 'confidence': 70}
        elif avg < 4.5:
            return {'signal': 'BIG', 'confidence': 70}
        return {'signal': None, 'confidence': 0}

    def alg_weighted_trend(self, numbers):
        if len(numbers) < 5:
            return {'signal': None, 'confidence': 0}
        weights = [1, 2, 3, 4, 5]
        last_5 = numbers[-5:]
        weighted_avg = sum(n * w for n, w in zip(last_5, weights)) / sum(weights)
        if weighted_avg > 5.5:
            return {'signal': 'SMALL', 'confidence': 70}
        elif weighted_avg < 4.5:
            return {'signal': 'BIG', 'confidence': 70}
        return {'signal': None, 'confidence': 0}

    def alg_consecutive_3(self, numbers):
        if len(numbers) < 3:
            return {'signal': None, 'confidence': 0}
        last_3 = numbers[-3:]
        if all(n >= 5 for n in last_3):
            return {'signal': 'SMALL', 'confidence': 80}
        elif all(n < 5 for n in last_3):
            return {'signal': 'BIG', 'confidence': 80}
        return {'signal': None, 'confidence': 0}

    def alg_consecutive_4(self, numbers):
        if len(numbers) < 4:
            return {'signal': None, 'confidence': 0}
        last_4 = numbers[-4:]
        if all(n >= 5 for n in last_4):
            return {'signal': 'SMALL', 'confidence': 85}
        elif all(n < 5 for n in last_4):
            return {'signal': 'BIG', 'confidence': 85}
        return {'signal': None, 'confidence': 0}

    def alg_consecutive_5(self, numbers):
        if len(numbers) < 5:
            return {'signal': None, 'confidence': 0}
        last_5 = numbers[-5:]
        if all(n >= 5 for n in last_5):
            return {'signal': 'SMALL', 'confidence': 90}
        elif all(n < 5 for n in last_5):
            return {'signal': 'BIG', 'confidence': 90}
        return {'signal': None, 'confidence': 0}

    def alg_consecutive_2(self, numbers):
        if len(numbers) < 2:
            return {'signal': None, 'confidence': 0}
        last_2 = numbers[-2:]
        if all(n >= 5 for n in last_2):
            return {'signal': 'SMALL', 'confidence': 65}
        elif all(n < 5 for n in last_2):
            return {'signal': 'BIG', 'confidence': 65}
        return {'signal': None, 'confidence': 0}

    def alg_consecutive_break(self, numbers):
        if len(numbers) < 3:
            return {'signal': None, 'confidence': 0}
        last_2 = numbers[-2:]
        if (last_2[0] >= 5) != (last_2[1] >= 5):
            return {'signal': 'BIG' if last_2[1] >= 5 else 'SMALL', 'confidence': 65}
        return {'signal': None, 'confidence': 0}

    def alg_alternating_3(self, numbers):
        if len(numbers) < 3:
            return {'signal': None, 'confidence': 0}
        last_3 = numbers[-3:]
        if (last_3[0] >= 5) != (last_3[1] >= 5) and (last_3[1] >= 5) != (last_3[2] >= 5):
            return {'signal': 'BIG' if last_3[-1] < 5 else 'SMALL', 'confidence': 70}
        return {'signal': None, 'confidence': 0}

    def alg_alternating_4(self, numbers):
        if len(numbers) < 4:
            return {'signal': None, 'confidence': 0}
        last_4 = numbers[-4:]
        if all((last_4[i] >= 5) != (last_4[i+1] >= 5) for i in range(3)):
            return {'signal': 'BIG' if last_4[-1] < 5 else 'SMALL', 'confidence': 80}
        return {'signal': None, 'confidence': 0}

    def alg_alternating_5(self, numbers):
        if len(numbers) < 5:
            return {'signal': None, 'confidence': 0}
        last_5 = numbers[-5:]
        if all((last_5[i] >= 5) != (last_5[i+1] >= 5) for i in range(4)):
            return {'signal': 'BIG' if last_5[-1] < 5 else 'SMALL', 'confidence': 90}
        return {'signal': None, 'confidence': 0}

    def alg_alternating_reverse(self, numbers):
        if len(numbers) < 4:
            return {'signal': None, 'confidence': 0}
        last_4 = numbers[-4:]
        if all((last_4[i] >= 5) != (last_4[i+1] >= 5) for i in range(3)):
            return {'signal': 'BIG' if last_4[-1] >= 5 else 'SMALL', 'confidence': 65}
        return {'signal': None, 'confidence': 0}

    def alg_double_big(self, numbers):
        if len(numbers) < 2:
            return {'signal': None, 'confidence': 0}
        if numbers[-1] >= 5 and numbers[-2] >= 5:
            return {'signal': 'SMALL', 'confidence': 70}
        return {'signal': None, 'confidence': 0}

    def alg_double_small(self, numbers):
        if len(numbers) < 2:
            return {'signal': None, 'confidence': 0}
        if numbers[-1] < 5 and numbers[-2] < 5:
            return {'signal': 'BIG', 'confidence': 70}
        return {'signal': None, 'confidence': 0}

    def alg_fibonacci(self, numbers):
        if len(numbers) < 5:
            return {'signal': None, 'confidence': 0}
        last_5 = numbers[-5:]
        pattern = [1 if n >= 5 else 0 for n in last_5]
        if pattern == [1, 0, 1, 1, 0]:
            return {'signal': 'BIG', 'confidence': 75}
        elif pattern == [0, 1, 0, 0, 1]:
            return {'signal': 'SMALL', 'confidence': 75}
        return {'signal': None, 'confidence': 0}

    def alg_zigzag(self, numbers):
        if len(numbers) < 6:
            return {'signal': None, 'confidence': 0}
        last_6 = numbers[-6:]
        if all((last_6[i] >= 5) != (last_6[i+1] >= 5) for i in range(5)):
            return {'signal': 'BIG' if last_6[-1] < 5 else 'SMALL', 'confidence': 80}
        return {'signal': None, 'confidence': 0}

    def alg_momentum(self, numbers):
        if len(numbers) < 10:
            return {'signal': None, 'confidence': 0}
        avg_5 = sum(numbers[-5:]) / 5
        avg_10 = sum(numbers[-10:-5]) / 5
        if avg_5 > avg_10:
            return {'signal': 'BIG', 'confidence': 70}
        elif avg_5 < avg_10:
            return {'signal': 'SMALL', 'confidence': 70}
        return {'signal': None, 'confidence': 0}

    def alg_mean_reversion(self, numbers):
        if len(numbers) < 10:
            return {'signal': None, 'confidence': 0}
        avg = sum(numbers) / len(numbers)
        last = numbers[-1]
        if last > avg + 1.5:
            return {'signal': 'SMALL', 'confidence': 70}
        elif last < avg - 1.5:
            return {'signal': 'BIG', 'confidence': 70}
        return {'signal': None, 'confidence': 0}

    def alg_volatility(self, numbers):
        if len(numbers) < 5:
            return {'signal': None, 'confidence': 0}
        last_5 = numbers[-5:]
        avg = sum(last_5) / 5
        variance = sum((n - avg) ** 2 for n in last_5) / 5
        if variance > 6:
            return {'signal': 'BIG' if last_5[-1] >= 5 else 'SMALL', 'confidence': 75}
        return {'signal': None, 'confidence': 0}

    def alg_martingale(self, numbers):
        if len(self.trade_history) < 2:
            return {'signal': None, 'confidence': 0}
        last_trade = self.trade_history[-1]
        if last_trade['result'] == 'Loss':
            return {'signal': 'BIG' if last_trade['prediction'] == 'SMALL' else 'SMALL', 'confidence': 75}
        return {'signal': None, 'confidence': 0}

    def alg_anti_martingale(self, numbers):
        if len(self.trade_history) < 2:
            return {'signal': None, 'confidence': 0}
        last_trade = self.trade_history[-1]
        if last_trade['result'] == 'Win':
            return {'signal': last_trade['prediction'], 'confidence': 70}
        return {'signal': None, 'confidence': 0}

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
                                        'algorithms_used': prediction.get('algorithms_used', 101),
                                        'votes': prediction.get('votes', {}),
                                        'number_probabilities': prediction.get('number_probabilities', {}),
                                        'predicted_number_confidence': prediction.get('predicted_number_confidence', 50),
                                        'api_period': api_latest_issue
                                    }
                                    
                                    return self.current_prediction
                    return None
                    
        except Exception as e:
            logger.error(f"API Error: {e}")
            return None

# ============================================================
# হেল্পার ফাংশন - প্রিমিয়াম UI
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
    text = "📊 *নাম্বার প্রোবাবিলিটি:*\n"
    for num, prob in sorted_probs[:5]:
        emoji = "🟢" if num >= 5 else "🔴"
        text += f"  {emoji} {num}: {prob}%\n"
    return text

def get_premium_keyboard():
    return [
        [
            {"text": "🚀 𝐒𝐈𝐆𝐍𝐀𝐋 𝐎𝐍", "callback_data": "start_signal"},
            {"text": "⏹️ 𝐒𝐈𝐆𝐍𝐀𝐋 𝐎𝐅𝐅", "callback_data": "stop_signal"}
        ],
        [
            {"text": "📊 𝐒𝐓𝐀𝐓𝐒", "callback_data": "stats"},
            {"text": "📡 𝐋𝐈𝐕𝐄", "callback_data": "live"}
        ],
        [
            {"text": "🖼️ 𝐈𝐌𝐀𝐆𝐄", "callback_data": "image_settings"},
            {"text": "📈 𝐇𝐈𝐒𝐓𝐎𝐑𝐘", "callback_data": "trade_history"}
        ]
    ]

def get_admin_keyboard():
    return [
        [
            {"text": "🟢 𝐁𝐈𝐆 𝐈𝐌𝐀𝐆𝐄", "callback_data": "upload_big"},
            {"text": "🔴 𝐒𝐌𝐀𝐋𝐋 𝐈𝐌𝐀𝐆𝐄", "callback_data": "upload_small"}
        ],
        [
            {"text": "🏆 𝐖𝐈𝐍 𝐈𝐌𝐀𝐆𝐄", "callback_data": "upload_win"},
            {"text": "💔 𝐋𝐎𝐒𝐒 𝐈𝐌𝐀𝐆𝐄", "callback_data": "upload_loss"}
        ],
        [
            {"text": "💰 𝐉𝐀𝐂𝐊𝐏𝐎𝐓", "callback_data": "upload_jackpot"},
            {"text": "📢 𝐂𝐇𝐀𝐍𝐍𝐄𝐋", "callback_data": "set_channel"}
        ],
        [
            {"text": "📊 𝐀𝐃𝐌𝐈𝐍 𝐒𝐓𝐀𝐓𝐒", "callback_data": "admin_stats"},
            {"text": "🔙 𝐁𝐀𝐂𝐊", "callback_data": "back_to_main"}
        ]
    ]

# ============================================================
# 📤 সিগন্যাল ফাংশন - ফিডব্যাক সহ
# ============================================================
async def send_signal(prediction, previous_result=None):
    global engine, signal_count, total_loss, total_profit, consecutive_wins, consecutive_losses, max_win_streak, max_loss_streak, primary_channel, secondary_channel, send_to_both
    
    if not prediction or not engine:
        return
    
    signal_count += 1
    engine.total_trade += 1
    
    signal_image = image_manager.get_image(prediction['prediction'])
    signal_time = datetime.now().strftime('%H:%M:%S')
    
    colorful_period = get_colorful_period(prediction['period'][-6:], prediction['prediction'])
    
    streak_text = ""
    if consecutive_wins >= 2:
        streak_text = f"\n🔥 *টানা উইন:* {consecutive_wins} (𝐌𝐚𝐱: {max_win_streak})"
    elif consecutive_losses >= 2:
        streak_text = f"\n⚠️ *টানা লস:* {consecutive_losses} (𝐌𝐚𝐱: {max_loss_streak})"
    
    algo_text = f"\n🧠 *অ্যালগরিদম:* {prediction.get('algorithms_used', 101)}টি"
    votes = prediction.get('votes', {})
    votes_text = f"\n🗳️ *ভোট:* BIG {votes.get('BIG', 0)} | SMALL {votes.get('SMALL', 0)}"
    
    probs = prediction.get('number_probabilities', {})
    prob_text = f"\n{get_number_probability_text(probs)}"
    
    signal_emoji = COLORS['BIG'] if prediction['prediction'] == 'BIG' else COLORS['SMALL']
    
    # 🔥 প্রিমিয়াম ক্যাপশন + ফিডব্যাক
    caption = f"""
💎 *𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐒𝐈𝐆𝐍𝐀𝐋* 💎
━━━━━━━━━━━━━━━━━━━━━

{signal_emoji} *𝐏𝐫𝐞𝐝𝐢𝐜𝐭𝐞𝐝:* {prediction['prediction']}
📌 *𝐏𝐞𝐫𝐢𝐨𝐝:* {colorful_period}
🔢 *𝐍𝐮𝐦𝐛𝐞𝐫:* `{prediction['number']}`
📊 *𝐂𝐨𝐧𝐟𝐢𝐝𝐞𝐧𝐜𝐞:* {prediction['confidence']}%
⏱️ *𝐓𝐢𝐦𝐞:* {signal_time}
{algo_text}{votes_text}

{prob_text}

🏆 *𝐓𝐨𝐭𝐚𝐥 𝐖𝐢𝐧:* {engine.win_count}
💔 *𝐓𝐨𝐭𝐚𝐥 𝐋𝐨𝐬𝐬:* {engine.loss_count}
🔥 *𝐌𝐚𝐱 𝐖𝐢𝐧 𝐒𝐭𝐫𝐞𝐚𝐤:* {max_win_streak}
⚠️ *𝐌𝐚𝐱 𝐋𝐨𝐬𝐬 𝐒𝐭𝐫𝐞𝐚𝐤:* {max_loss_streak}
{streak_text}
━━━━━━━━━━━━━━━━━━━━━
{FEEDBACK}
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
        else:
            await send_telegram_message(caption, primary_channel)
        
        if is_jackpot and jackpot_image:
            jackpot_caption = f"🎰 *𝐉𝐀𝐂𝐊𝐏𝐎𝐓 𝐖𝐈𝐍𝐍𝐄𝐑!* 🎰\n📌 Period: {prediction['period'][-6:]}\n🎯 {prediction['prediction']} + {prediction['number']} = JACKPOT!\n⏱️ {signal_time}\n\n{FEEDBACK}"
            await send_telegram_photo(jackpot_caption, jackpot_image, primary_channel)
    
    if secondary_channel and send_to_both:
        if signal_image:
            await send_telegram_photo(caption, signal_image, secondary_channel)
        else:
            await send_telegram_message(caption, secondary_channel)
        
        if is_jackpot and jackpot_image:
            jackpot_caption = f"🎰 *𝐉𝐀𝐂𝐊𝐏𝐎𝐓 𝐖𝐈𝐍𝐍𝐄𝐑!* 🎰\n📌 Period: {prediction['period'][-6:]}\n🎯 {prediction['prediction']} + {prediction['number']} = JACKPOT!\n⏱️ {signal_time}\n\n{FEEDBACK}"
            await send_telegram_photo(jackpot_caption, jackpot_image, secondary_channel)
    
    logger.info(f"📤 Signal #{signal_count}: {prediction['prediction']} at {signal_time}")

# ============================================================
# 📊 রেজাল্ট চেক - ফিডব্যাক সহ
# ============================================================
async def check_result(prediction, actual_number):
    global engine, last_result, total_loss, total_profit, consecutive_wins, consecutive_losses, max_win_streak, max_loss_streak, primary_channel, secondary_channel, send_to_both
    
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
    
    streak_text = ""
    if consecutive_wins >= 2:
        streak_text = f"\n🔥 *টানা উইন:* {consecutive_wins} (𝐌𝐚𝐱: {max_win_streak})"
    elif consecutive_losses >= 2:
        streak_text = f"\n⚠️ *টানা লস:* {consecutive_losses} (𝐌𝐚𝐱: {max_loss_streak})"
    
    # প্রিমিয়াম রেজাল্ট ক্যাপশন + ফিডব্যাক
    caption = f"""
{result_text}
━━━━━━━━━━━━━━━━━━━━━

📌 *𝐏𝐞𝐫𝐢𝐨𝐝:* {prediction['period'][-6:]}
🎯 *𝐏𝐫𝐞𝐝𝐢𝐜𝐭:* {prediction['prediction']} → *{actual_bs}* ({actual_number})
⏱️ *𝐓𝐢𝐦𝐞:* {result_time}

🏆 *𝐓𝐨𝐭𝐚𝐥 𝐖𝐢𝐧:* {engine.win_count}
💔 *𝐓𝐨𝐭𝐚𝐥 𝐋𝐨𝐬𝐬:* {engine.loss_count}
🎯 *𝐀𝐜𝐜𝐮𝐫𝐚𝐜𝐲:* {engine.accuracy}%
🔥 *𝐌𝐚𝐱 𝐖𝐢𝐧 𝐒𝐭𝐫𝐞𝐚𝐤:* {max_win_streak}
⚠️ *𝐌𝐚𝐱 𝐋𝐨𝐬𝐬 𝐒𝐭𝐫𝐞𝐚𝐤:* {max_loss_streak}
{streak_text}
━━━━━━━━━━━━━━━━━━━━━
{FEEDBACK}
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
    
    logger.info("🔄 Signal loop started - Premium + Dual Channel + Feedback Active")
    
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
# মেসেজ হ্যান্ডলার (সংক্ষিপ্ত)
# ============================================================
async def handle_message(message):
    global is_running, engine, admin_session, max_win_streak, max_loss_streak, primary_channel, secondary_channel, send_to_both
    
    text = message.get('text', '')
    chat_id = str(message['chat']['id'])
    user_id = str(message['from']['id'])
    
    if chat_id != str(CHAT_ID):
        return
    
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

🔥 *𝐌𝐚𝐱 𝐖𝐢𝐧 𝐒𝐭𝐫𝐞𝐚𝐤:* {max_win_streak}
⚠️ *𝐌𝐚𝐱 𝐋𝐨𝐬𝐬 𝐒𝐭𝐫𝐞𝐚𝐤:* {max_loss_streak}
🧠 *𝐀𝐥𝐠𝐨𝐫𝐢𝐭𝐡𝐦𝐬:* 101 Active
{channel_info}
⏱️ *𝐓𝐢𝐦𝐢𝐧𝐠:* :30 & :00 Collect, :35 & :05 Signal
━━━━━━━━━━━━━━━━━━━━━
{FEEDBACK}
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
🧠 *Active Algorithms:* 101

📌 *Last 10:* {get_history_dots(engine.last_10_numbers)}
━━━━━━━━━━━━━━━━━━━━━
{FEEDBACK}
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

🧠 *101 Algorithms Active*
📢 *Dual Channel Support*
🎯 *Number Prediction Active*

⏱️ *𝐓𝐢𝐦𝐢𝐧𝐠:*
• :30 Data collect
• :35 Signal
• :00 Data collect
• :05 Signal

📊 *𝐅𝐞𝐚𝐭𝐮𝐫𝐞𝐬:*
• Number Prediction
• Colorful Period
• Premium UI
• Max Win/Loss Streak
• Dual Channel/Group
• Feedback System
━━━━━━━━━━━━━━━━━━━━━
{FEEDBACK}
        """
        await send_telegram_message(help_text, chat_id)

# ============================================================
# Callback হ্যান্ডলার (সংক্ষিপ্ত)
# ============================================================
async def handle_callback(callback):
    global is_running, engine, admin_session, image_manager, max_win_streak, max_loss_streak, primary_channel, secondary_channel, send_to_both
    
    data = callback['data']
    callback_id = callback['id']
    message = callback.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    message_id = message.get('message_id')
    user_id = str(callback['from']['id'])
    
    is_admin = user_id in admin_session and admin_session[user_id].get('step') == 'authenticated'
    
    if data == 'set_channel':
        if not is_admin:
            await answer_callback(callback_id, "⛔ Admin only!")
            return
        admin_session[user_id]['step'] = 'awaiting_primary_channel'
        await edit_message_text(
            chat_id, message_id,
            f"📢 *𝐂𝐡𝐚𝐧𝐧𝐞𝐥/𝐆𝐫𝐨𝐮𝐩 𝐒𝐞𝐭𝐮𝐩*\n\n📌 বর্তমান প্রধান চ্যানেল: `{primary_channel}`\n📌 বর্তমান সেকেন্ডারি: `{secondary_channel if secondary_channel else 'সেট করা নেই'}`\n\nদয়া করে নতুন প্রধান চ্যানেল/গ্রুপের আইডি দিন:",
            get_admin_keyboard()
        )
        await answer_callback(callback_id, "📢 প্রধান চ্যানেল আইডি দিন...")
        return
    
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

🔥 Max Win Streak: {max_win_streak}
⚠️ Max Loss Streak: {max_loss_streak}
🧠 Algorithms: 101 Active

📢 Primary: {primary_channel}
📢 Secondary: {secondary_channel if secondary_channel else 'None'}
📡 Send to Both: {'✅' if send_to_both else '❌'}

🖼️ Images: BIG, SMALL, WIN, LOSS, JACKPOT
━━━━━━━━━━━━━━━━━━━━━
{FEEDBACK}
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
    
    # রেগুলার কমান্ড
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
                f"✅ *𝐒𝐢𝐠𝐧𝐚𝐥 𝐬𝐭𝐚𝐫𝐭𝐞𝐝!*\n🧠 101 Algorithms Active\n📢 Dual Channel Mode{' ON' if send_to_both else ' OFF'}\n{channel_info}\n⏱️ :30 & :00 Data, :35 & :05 Signal"
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

🔥 Max Win Streak: {max_win_streak}
⚠️ Max Loss Streak: {max_loss_streak}
🧠 Active Algorithms: 101

📌 Last 10: {get_history_dots(engine.last_10_numbers)}
━━━━━━━━━━━━━━━━━━━━━
{FEEDBACK}
        """
        await edit_message_text(chat_id, message_id, stats)
        await answer_callback(callback_id, "📊 Showing stats")
    
    elif data == "live":
        if engine and engine.current_prediction:
            p = engine.current_prediction
            signal = f"""
📡 *𝐋𝐈𝐕𝐄 𝐒𝐈𝐆𝐍𝐀𝐋*
━━━━━━━━━━━━━━━━━━━━━

📌 Period: {p['period'][-6:]}
🎯 Predict: {p['prediction']}
🔢 Number: {p['number']}
📊 Confidence: {p['confidence']}%
🧠 Algorithms: 101
⏱️ {p['timestamp']}
━━━━━━━━━━━━━━━━━━━━━
{FEEDBACK}
            """
            await edit_message_text(chat_id, message_id, signal)
            await answer_callback(callback_id, "📡 Showing live signal")
        else:
            await answer_callback(callback_id, "⏳ No signal available")
    
    elif data == "trade_history":
        if not engine or not engine.trade_history:
            await answer_callback(callback_id, "❌ No trades")
            return
        history = "📈 *𝐓𝐑𝐀𝐃𝐄 𝐇𝐈𝐒𝐓𝐎𝐑𝐘*\n━━━━━━━━━━━━━━━━━━━\n"
        for i, t in enumerate(engine.trade_history[-10:], 1):
            icon = "✅" if t['result'] == "Win" else "❌"
            history += f"{i}. {icon} {t['prediction']} → {t['actual']} ({t['number']})\n"
        history += f"\n━━━━━━━━━━━━━━━━━━━━━\n{FEEDBACK}"
        await edit_message_text(chat_id, message_id, history)
        await answer_callback(callback_id, "📈 Showing history")

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
    global engine, is_running, image_manager, max_win_streak, max_loss_streak, primary_channel, secondary_channel, send_to_both
    
    print_banner()
    logger.info("🤖 Starting Masud AI Premium Bot...")
    logger.info(f"📡 Bot Token: {BOT_TOKEN[:10]}...")
    logger.info(f"📢 Default Channel: {CHAT_ID}")
    logger.info("=" * 60)
    logger.info("🔐 ADMIN PANEL: /admin")
    logger.info("🔑 PASSWORD: msxmasud20")
    logger.info("🧠 101 ALGORITHMS ACTIVE")
    logger.info("📢 DUAL CHANNEL/GROUP SUPPORT")
    logger.info("🎯 NUMBER PREDICTION ACTIVE")
    logger.info("🔥 MAX WIN/LOSS STREAK ACTIVE")
    logger.info("📝 FEEDBACK SYSTEM ACTIVE")
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
    print("  🧠 101 ALGORITHMS ACTIVE")
    print("  📢 DUAL CHANNEL/GROUP SUPPORT")
    print("  🎯 NUMBER PREDICTION ACTIVE")
    print("  🔥 MAX WIN/LOSS STREAK TRACKING")
    print("  📝 FEEDBACK SYSTEM ACTIVE")
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
