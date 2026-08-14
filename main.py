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
║      🤖 MASUD AI - 25 ALGORITHM PREDICTION BOT             ║
║      🚀 VERSION 7.0 - VOTING SYSTEM ACTIVE                 ║
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

# ============================================================
# 🧠 ২৫টি স্মার্ট অ্যালগরিদম
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
        self.alternating_count = 0
        self.algorithm_votes = {'BIG': 0, 'SMALL': 0}
        self.winning_algorithms = []

    # ============================================================
    # অ্যালগরিদম ১-৫: ট্রেন্ড বেইজড
    # ============================================================
    def alg_trend_60(self, numbers):
        """ট্রেন্ড ৬০% - ৬০% এর বেশি BIG/SMALL হলে"""
        if len(numbers) < 5:
            return {'signal': None, 'confidence': 0}
        bigs = sum(1 for n in numbers if n >= 5)
        ratio = bigs / len(numbers)
        if ratio >= 0.60:
            return {'signal': 'BIG', 'confidence': 75}
        elif ratio <= 0.40:
            return {'signal': 'SMALL', 'confidence': 75}
        return {'signal': None, 'confidence': 0}

    def alg_trend_70(self, numbers):
        """ট্রেন্ড ৭০% - ৭০% এর বেশি BIG/SMALL হলে"""
        if len(numbers) < 8:
            return {'signal': None, 'confidence': 0}
        bigs = sum(1 for n in numbers if n >= 5)
        ratio = bigs / len(numbers)
        if ratio >= 0.70:
            return {'signal': 'SMALL', 'confidence': 85}  # রিভার্স
        elif ratio <= 0.30:
            return {'signal': 'BIG', 'confidence': 85}   # রিভার্স
        return {'signal': None, 'confidence': 0}

    def alg_trend_reverse(self, numbers):
        """ট্রেন্ড রিভার্স - বেশি সাইডের উল্টোটা"""
        if len(numbers) < 6:
            return {'signal': None, 'confidence': 0}
        bigs = sum(1 for n in numbers[-6:] if n >= 5)
        if bigs >= 4:
            return {'signal': 'SMALL', 'confidence': 70}
        elif bigs <= 2:
            return {'signal': 'BIG', 'confidence': 70}
        return {'signal': None, 'confidence': 0}

    def alg_moving_average(self, numbers):
        """মুভিং এভারেজ - গড়ের ভিত্তিতে"""
        if len(numbers) < 5:
            return {'signal': None, 'confidence': 0}
        avg = sum(numbers[-5:]) / 5
        if avg > 5.5:
            return {'signal': 'SMALL', 'confidence': 65}
        elif avg < 4.5:
            return {'signal': 'BIG', 'confidence': 65}
        return {'signal': None, 'confidence': 0}

    def alg_weighted_trend(self, numbers):
        """ওয়েটেড ট্রেন্ড - নতুন সংখ্যা বেশি ওয়েট"""
        if len(numbers) < 8:
            return {'signal': None, 'confidence': 0}
        weights = [1, 2, 3, 4, 5]  # নতুনদের বেশি ওয়েট
        last_5 = numbers[-5:]
        weighted_sum = sum(n * w for n, w in zip(last_5, weights))
        avg = weighted_sum / sum(weights)
        if avg > 5.5:
            return {'signal': 'SMALL', 'confidence': 70}
        elif avg < 4.5:
            return {'signal': 'BIG', 'confidence': 70}
        return {'signal': None, 'confidence': 0}

    # ============================================================
    # অ্যালগরিদম ৬-১০: কনসিকিউটিভ বেইজড
    # ============================================================
    def alg_consecutive_3(self, numbers):
        """৩টা কনসিকিউটিভ - রিভার্স"""
        if len(numbers) < 3:
            return {'signal': None, 'confidence': 0}
        last_3 = numbers[-3:]
        if all(n >= 5 for n in last_3):
            return {'signal': 'SMALL', 'confidence': 80}
        elif all(n < 5 for n in last_3):
            return {'signal': 'BIG', 'confidence': 80}
        return {'signal': None, 'confidence': 0}

    def alg_consecutive_4(self, numbers):
        """৪টা কনসিকিউটিভ - স্ট্রং রিভার্স"""
        if len(numbers) < 4:
            return {'signal': None, 'confidence': 0}
        last_4 = numbers[-4:]
        if all(n >= 5 for n in last_4):
            return {'signal': 'SMALL', 'confidence': 90}
        elif all(n < 5 for n in last_4):
            return {'signal': 'BIG', 'confidence': 90}
        return {'signal': None, 'confidence': 0}

    def alg_consecutive_5(self, numbers):
        """৫টা কনসিকিউটিভ - খুব স্ট্রং রিভার্স"""
        if len(numbers) < 5:
            return {'signal': None, 'confidence': 0}
        last_5 = numbers[-5:]
        if all(n >= 5 for n in last_5):
            return {'signal': 'SMALL', 'confidence': 95}
        elif all(n < 5 for n in last_5):
            return {'signal': 'BIG', 'confidence': 95}
        return {'signal': None, 'confidence': 0}

    def alg_consecutive_break(self, numbers):
        """কনসিকিউটিভ ব্রেক - কখন ব্রেক হবে"""
        if len(numbers) < 3:
            return {'signal': None, 'confidence': 0}
        last_2 = numbers[-2:]
        if (last_2[0] >= 5) != (last_2[1] >= 5):
            # ব্রেক হয়েছে, নতুন ট্রেন্ড ফলো
            return {'signal': 'BIG' if last_2[1] >= 5 else 'SMALL', 'confidence': 65}
        return {'signal': None, 'confidence': 0}

    def alg_consecutive_alternate(self, numbers):
        """কনসিকিউটিভ অল্টারনেট"""
        if len(numbers) < 6:
            return {'signal': None, 'confidence': 0}
        last_6 = numbers[-6:]
        pattern = [1 if n >= 5 else 0 for n in last_6]
        # ১,০,১,০,১,০ প্যাটার্ন চেক
        if pattern == [1, 0, 1, 0, 1, 0]:
            return {'signal': 'BIG', 'confidence': 75}
        elif pattern == [0, 1, 0, 1, 0, 1]:
            return {'signal': 'SMALL', 'confidence': 75}
        return {'signal': None, 'confidence': 0}

    # ============================================================
    # অ্যালগরিদম ১১-১৫: অল্টারনেটিং বেইজড
    # ============================================================
    def alg_alternating_3(self, numbers):
        """৩টা অল্টারনেটিং"""
        if len(numbers) < 3:
            return {'signal': None, 'confidence': 0}
        last_3 = numbers[-3:]
        if (last_3[0] >= 5) != (last_3[1] >= 5) and (last_3[1] >= 5) != (last_3[2] >= 5):
            return {'signal': 'BIG' if last_3[-1] < 5 else 'SMALL', 'confidence': 70}
        return {'signal': None, 'confidence': 0}

    def alg_alternating_4(self, numbers):
        """৪টা অল্টারনেটিং"""
        if len(numbers) < 4:
            return {'signal': None, 'confidence': 0}
        last_4 = numbers[-4:]
        if all((last_4[i] >= 5) != (last_4[i+1] >= 5) for i in range(3)):
            return {'signal': 'BIG' if last_4[-1] < 5 else 'SMALL', 'confidence': 80}
        return {'signal': None, 'confidence': 0}

    def alg_alternating_5(self, numbers):
        """৫টা অল্টারনেটিং"""
        if len(numbers) < 5:
            return {'signal': None, 'confidence': 0}
        last_5 = numbers[-5:]
        if all((last_5[i] >= 5) != (last_5[i+1] >= 5) for i in range(4)):
            return {'signal': 'BIG' if last_5[-1] < 5 else 'SMALL', 'confidence': 90}
        return {'signal': None, 'confidence': 0}

    def alg_alternating_break(self, numbers):
        """অল্টারনেটিং ব্রেক"""
        if len(numbers) < 4:
            return {'signal': None, 'confidence': 0}
        last_4 = numbers[-4:]
        if all((last_4[i] >= 5) == (last_4[i+1] >= 5) for i in range(3)):
            # অল্টারনেটিং ব্রেক হয়েছে
            return {'signal': 'BIG' if last_4[-1] >= 5 else 'SMALL', 'confidence': 70}
        return {'signal': None, 'confidence': 0}

    def alg_alternating_reverse(self, numbers):
        """অল্টারনেটিং রিভার্স"""
        if len(numbers) < 4:
            return {'signal': None, 'confidence': 0}
        last_4 = numbers[-4:]
        if all((last_4[i] >= 5) != (last_4[i+1] >= 5) for i in range(3)):
            return {'signal': 'BIG' if last_4[-1] >= 5 else 'SMALL', 'confidence': 65}
        return {'signal': None, 'confidence': 0}

    # ============================================================
    # অ্যালগরিদম ১৬-২০: স্পেশাল প্যাটার্ন
    # ============================================================
    def alg_double_big(self, numbers):
        """ডাবল বিগ - ২টা BIG পরপর"""
        if len(numbers) < 2:
            return {'signal': None, 'confidence': 0}
        if numbers[-1] >= 5 and numbers[-2] >= 5:
            return {'signal': 'SMALL', 'confidence': 70}
        return {'signal': None, 'confidence': 0}

    def alg_double_small(self, numbers):
        """ডাবল স্মল - ২টা SMALL পরপর"""
        if len(numbers) < 2:
            return {'signal': None, 'confidence': 0}
        if numbers[-1] < 5 and numbers[-2] < 5:
            return {'signal': 'BIG', 'confidence': 70}
        return {'signal': None, 'confidence': 0}

    def alg_fibonacci(self, numbers):
        """ফিবোনাচি প্যাটার্ন"""
        if len(numbers) < 5:
            return {'signal': None, 'confidence': 0}
        last_5 = numbers[-5:]
        # BIG/SMALL প্যাটার্ন চেক
        pattern = [1 if n >= 5 else 0 for n in last_5]
        if pattern == [1, 0, 1, 1, 0]:
            return {'signal': 'BIG', 'confidence': 75}
        elif pattern == [0, 1, 0, 0, 1]:
            return {'signal': 'SMALL', 'confidence': 75}
        return {'signal': None, 'confidence': 0}

    def alg_zigzag(self, numbers):
        """জিগজ্যাগ প্যাটার্ন"""
        if len(numbers) < 6:
            return {'signal': None, 'confidence': 0}
        last_6 = numbers[-6:]
        # HIGH-LOW-HIGH-LOW-HIGH-LOW
        if all((last_6[i] >= 5) != (last_6[i+1] >= 5) for i in range(5)):
            return {'signal': 'BIG' if last_6[-1] < 5 else 'SMALL', 'confidence': 80}
        return {'signal': None, 'confidence': 0}

    def alg_momentum(self, numbers):
        """মোমেন্টাম - উর্ধ্বমুখী/নিম্নমুখী"""
        if len(numbers) < 5:
            return {'signal': None, 'confidence': 0}
        last_5 = numbers[-5:]
        avg = sum(last_5) / 5
        if avg > sum(numbers[-10:-5]) / 5:
            return {'signal': 'BIG', 'confidence': 70}  # উর্ধ্বমুখী
        elif avg < sum(numbers[-10:-5]) / 5:
            return {'signal': 'SMALL', 'confidence': 70}  # নিম্নমুখী
        return {'signal': None, 'confidence': 0}

    # ============================================================
    # অ্যালগরিদম ২১-২৫: অ্যাডভান্সড স্ট্রাটেজি
    # ============================================================
    def alg_martingale(self, numbers):
        """মার্টিনগেল - লসের পর ডাবল"""
        if len(self.trade_history) < 2:
            return {'signal': None, 'confidence': 0}
        last_trade = self.trade_history[-1]
        if last_trade['result'] == 'Loss':
            # লসের পর উল্টোটা
            return {'signal': 'BIG' if last_trade['prediction'] == 'SMALL' else 'SMALL', 'confidence': 75}
        return {'signal': None, 'confidence': 0}

    def alg_anti_martingale(self, numbers):
        """অ্যান্টি-মার্টিনগেল - উইনের পর ডাবল"""
        if len(self.trade_history) < 2:
            return {'signal': None, 'confidence': 0}
        last_trade = self.trade_history[-1]
        if last_trade['result'] == 'Win':
            # উইনের পর একই
            return {'signal': last_trade['prediction'], 'confidence': 70}
        return {'signal': None, 'confidence': 0}

    def alg_mean_reversion(self, numbers):
        """মিন রিভার্সন - গড়ে ফিরে আসা"""
        if len(numbers) < 10:
            return {'signal': None, 'confidence': 0}
        avg = sum(numbers) / len(numbers)
        last = numbers[-1]
        if last > avg + 2:
            return {'signal': 'SMALL', 'confidence': 70}
        elif last < avg - 2:
            return {'signal': 'BIG', 'confidence': 70}
        return {'signal': None, 'confidence': 0}

    def alg_volatility(self, numbers):
        """ভোলাটিলিটি - বেশি ওঠানামা"""
        if len(numbers) < 5:
            return {'signal': None, 'confidence': 0}
        last_5 = numbers[-5:]
        variance = sum((n - sum(last_5)/5) ** 2 for n in last_5) / 5
        if variance > 5:
            return {'signal': 'BIG' if last_5[-1] >= 5 else 'SMALL', 'confidence': 75}
        return {'signal': None, 'confidence': 0}

    def alg_smart_vote(self, numbers):
        """স্মার্ট ভোট - সব অ্যালগরিদমের ভোট"""
        return self.get_voting_result(numbers)

    # ============================================================
    # 🗳️ ভোটিং সিস্টেম - সব অ্যালগরিদমের ভোট নেয়
    # ============================================================
    def get_voting_result(self, numbers):
        """২৫টি অ্যালগরিদমের ভোট নেয়"""
        algorithms = [
            self.alg_trend_60,
            self.alg_trend_70,
            self.alg_trend_reverse,
            self.alg_moving_average,
            self.alg_weighted_trend,
            self.alg_consecutive_3,
            self.alg_consecutive_4,
            self.alg_consecutive_5,
            self.alg_consecutive_break,
            self.alg_consecutive_alternate,
            self.alg_alternating_3,
            self.alg_alternating_4,
            self.alg_alternating_5,
            self.alg_alternating_break,
            self.alg_alternating_reverse,
            self.alg_double_big,
            self.alg_double_small,
            self.alg_fibonacci,
            self.alg_zigzag,
            self.alg_momentum,
            self.alg_martingale,
            self.alg_anti_martingale,
            self.alg_mean_reversion,
            self.alg_volatility,
        ]
        
        votes = {'BIG': 0, 'SMALL': 0, 'WAIT': 0}
        algo_results = []
        confidence_sum = 0
        confidence_count = 0
        
        for algo in algorithms:
            try:
                result = algo(numbers)
                if result and result.get('signal'):
                    votes[result['signal']] += 1
                    confidence_sum += result.get('confidence', 50)
                    confidence_count += 1
                    algo_results.append(f"{algo.__name__}: {result['signal']} ({result.get('confidence', 0)}%)")
            except:
                continue
        
        # ভোটের ভিত্তিতে সিদ্ধান্ত
        if votes['BIG'] > votes['SMALL'] and votes['BIG'] >= 3:
            avg_confidence = int(confidence_sum / confidence_count) if confidence_count > 0 else 60
            return {
                'signal': 'BIG',
                'confidence': min(95, avg_confidence + 5),
                'votes': votes,
                'algorithms': algo_results[:5]  # টপ ৫ দেখায়
            }
        elif votes['SMALL'] > votes['BIG'] and votes['SMALL'] >= 3:
            avg_confidence = int(confidence_sum / confidence_count) if confidence_count > 0 else 60
            return {
                'signal': 'SMALL',
                'confidence': min(95, avg_confidence + 5),
                'votes': votes,
                'algorithms': algo_results[:5]
            }
        else:
            return {
                'signal': 'WAIT',
                'confidence': 0,
                'votes': votes,
                'algorithms': ['No clear signal']
            }

    # ============================================================
    # 📡 পিরিয়ড সিঙ্ক - সম্পূর্ণ ফিক্স
    # ============================================================
    def get_current_win_go_period(self):
        """উইংগোর বর্তমান পিরিয়ড ক্যালকুলেট - অটো +১"""
        now = datetime.now()
        base = datetime(2024, 1, 1, 0, 0, 0)
        seconds_diff = int((now - base).total_seconds())
        period_number = (seconds_diff // 30) + 1  # +১ যোগ করা হয়েছে
        base_period = 728000
        current_period = base_period + period_number
        return str(current_period)

    def sync_period(self, api_period, win_go_period):
        """পিরিয়ড সিঙ্ক - অটো +১ যদি প্রয়োজন হয়"""
        try:
            api_int = int(api_period)
            win_go_int = int(win_go_period)
            diff = win_go_int - api_int
            
            if diff == 1:
                return win_go_period  # WinGo period ব্যবহার
            elif diff == 0:
                return api_period  # সিঙ্ক
            else:
                # বড় পার্থক্য - API + 1
                return str(api_int + 1)
        except:
            return api_period

    # ============================================================
    # 📊 API ডাটা ফেচ
    # ============================================================
    async def fetch_data(self):
        try:
            logger.info("📡 Fetching data from API...")
            
            win_go_period = self.get_current_win_go_period()
            logger.info(f"📌 Current WinGo Period: {win_go_period}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    API_URL, 
                    headers=API_HEADERS, 
                    timeout=15,
                    allow_redirects=True
                ) as response:
                    if response.status == 200:
                        try:
                            text = await response.text()
                            data = json.loads(text)
                        except Exception as e:
                            logger.error(f"❌ JSON parse error: {e}")
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
                                
                                # পিরিয়ড সিঙ্ক - অটো +১
                                use_period = self.sync_period(api_latest_issue, win_go_period)
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
                                    
                                    # 🗳️ ভোটিং সিস্টেম প্রেডিক্ট
                                    voting_result = self.get_voting_result(self.history)
                                    
                                    # নম্বর জেনারেট
                                    if voting_result['signal'] == 'BIG':
                                        num = random.randint(5, 9)
                                    elif voting_result['signal'] == 'SMALL':
                                        num = random.randint(0, 4)
                                    else:
                                        num = random.randint(0, 9)
                                    
                                    self.current_prediction = {
                                        'period': use_period,
                                        'prediction': voting_result['signal'],
                                        'number': num,
                                        'confidence': voting_result['confidence'],
                                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                                        'big_count': self.big_count,
                                        'small_count': self.small_count,
                                        'consecutive_big': self.consecutive_big,
                                        'consecutive_small': self.consecutive_small,
                                        'history': self.last_10_numbers[:10],
                                        'votes': voting_result.get('votes', {}),
                                        'algorithms': voting_result.get('algorithms', []),
                                        'api_period': api_latest_issue,
                                        'win_go_period': win_go_period
                                    }
                                    
                                    logger.info(f"🎯 VOTING RESULT: {voting_result}")
                                    return self.current_prediction
                    else:
                        logger.warning(f"⚠️ API status: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ API Error: {e}")
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
    global engine, signal_count
    
    if not prediction or not engine:
        return
    
    signal_count += 1
    engine.total_trade += 1
    
    bar = get_confidence_bar(prediction['confidence'])
    dots = get_history_dots(prediction.get('history', []))
    
    # সিগন্যাল টাইপ
    if prediction['prediction'] == 'BIG':
        bs_emoji = "🟢"
        signal_type = "🎯"
    elif prediction['prediction'] == 'SMALL':
        bs_emoji = "🔴"
        signal_type = "🎯"
    else:
        bs_emoji = "⏳"
        signal_type = "⏳"
    
    # ভোটিং ইনফো
    votes = prediction.get('votes', {})
    votes_info = f"\n🗳️ ভোট: BIG {votes.get('BIG', 0)} | SMALL {votes.get('SMALL', 0)}"
    
    # অ্যালগরিদম ইনফো
    algos = prediction.get('algorithms', [])
    algo_info = "\n🧠 অ্যালগরিদম:\n"
    for i, algo in enumerate(algos[:5], 1):
        algo_info += f"   {i}. {algo}\n"
    
    # পিরিয়ড সিঙ্ক ইনফো
    period_info = ""
    if 'api_period' in prediction and 'win_go_period' in prediction:
        if prediction['api_period'] != prediction['win_go_period']:
            period_info = f"\n🔄 সিঙ্ক: {prediction['api_period']} → {prediction['win_go_period']}"
    
    msg = f"""
{signal_type} *MASUD AI - ২৫ অ্যালগরিদম প্রেডিক্ট*
━━━━━━━━━━━━━━━━━━━━━━

🔢 *পিরিয়ড:* `{prediction['period'][-6:]}`{period_info}
🎯 *সিগন্যাল:* {bs_emoji} *{prediction['prediction']}*
🔢 *প্রেডিক্টেড নম্বর:* `{prediction['number'] if prediction['prediction'] != 'WAIT' else '--'}`
📊 *কনফিডেন্স:* {prediction['confidence']}% {bar if prediction['prediction'] != 'WAIT' else '⏳'}

📈 *ট্রেন্ড অ্যানালাইসিস:*
• লাস্ট ১০: {dots}
• BIG: {prediction.get('big_count', 0)} | SMALL: {prediction.get('small_count', 0)}
• কনসিকিউটিভ BIG: {prediction.get('consecutive_big', 0)}
• কনসিকিউটিভ SMALL: {prediction.get('consecutive_small', 0)}
{votes_info}
{algo_info}

📊 *পরিসংখ্যান:*
🏆 উইন: {engine.win_count} | 💔 লস: {engine.loss_count}
🎯 একুরেসি: {engine.accuracy}% | 📈 ট্রেড #{engine.total_trade}

⏱️ {prediction['timestamp']}
━━━━━━━━━━━━━━━━━━━━━━
🅿🅾🆆🅴🆁🅴🅳 🅱🆈 🅼🅰🆂🆄🅳 🅰🅸
    """
    
    await send_telegram_message(msg)
    logger.info(f"📤 Signal #{signal_count}: {prediction['prediction']} (Confidence: {prediction['confidence']}%)")

async def check_result(prediction, actual_number):
    global engine
    
    if not prediction or actual_number is None or not engine:
        return
    
    if prediction['prediction'] == 'WAIT':
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
# সিগন্যাল লুপ
# ============================================================
async def signal_loop():
    global is_running, last_signal, last_period, engine
    
    logger.info("🔄 Signal loop started - 25 ALGORITHMS ACTIVE")
    
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
                        logger.info(f"⏳ Same period {prediction['period']}")
                else:
                    logger.info("⏳ No prediction")
            
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
🤖 *MASUD AI - ২৫ অ্যালগরিদম প্রেডিক্টর*
━━━━━━━━━━━━━━━━━━━━━━

📊 *স্ট্যাটাস:* {status}
🏆 *উইন:* {engine.win_count if engine else 0}
💔 *লস:* {engine.loss_count if engine else 0}
📈 *ট্রেড:* {engine.total_trade if engine else 0}
🎯 *একুরেসি:* {engine.accuracy if engine else 0}%

📌 *লাস্ট ১০:* {get_history_dots(engine.last_10_numbers) if engine else '---'}

🧠 *২৫টি অ্যালগরিদম সক্রিয়*
🗳️ *ভোটিং সিস্টেম চালু*
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

🧠 *২৫টি অ্যালগরিদম:*
• ট্রেন্ড বেইজড (৫টি)
• কনসিকিউটিভ বেইজড (৫টি)
• অল্টারনেটিং বেইজড (৫টি)
• স্পেশাল প্যাটার্ন (৫টি)
• অ্যাডভান্সড স্ট্রাটেজি (৫টি)

🗳️ *ভোটিং সিস্টেম:* সব অ্যালগরিদমের ভোট নেয়

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
            await edit_message_text(chat_id, message_id, "✅ সিগন্যাল চালু! ২৫টি অ্যালগরিদম সক্রিয়।")
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
            
            votes = p.get('votes', {})
            votes_info = f"🗳️ ভোট: BIG {votes.get('BIG', 0)} | SMALL {votes.get('SMALL', 0)}"
            
            signal = f"""
📡 *লাইভ সিগন্যাল*
━━━━━━━━━━━━━━━━━━━

🔢 পিরিয়ড: `{p['period'][-6:]}`
🎯 সিগন্যাল: {'🟢' if p['prediction'] == 'BIG' else '🔴' if p['prediction'] == 'SMALL' else '⏳'} *{p['prediction']}*
📊 কনফিডেন্স: {p['confidence']}% {bar}

📈 *ট্রেন্ড অ্যানালাইসিস:*
• লাস্ট ১০: {dots}
• BIG: {p.get('big_count', 0)} | SMALL: {p.get('small_count', 0)}
{votes_info}

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
    logger.info("🧠 25 ALGORITHMS ACTIVE")
    logger.info("🗳️ VOTING SYSTEM ACTIVE")
    logger.info("🔄 PERIOD SYNC: AUTO +1 FIXED")
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
    print("  🧠 25 ALGORITHMS ACTIVE")
    print("  🗳️ VOTING SYSTEM ACTIVE")
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
