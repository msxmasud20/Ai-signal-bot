import os
import asyncio
import aiohttp
import json
import random
import logging
from datetime import datetime, timedelta

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
║         🤖 MASUD AI - SMART PREDICTION BOT                  ║
║         🚀 VERSION 6.0 - MULTI-FACTOR ALGORITHM            ║
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
# 🧠 স্মার্ট প্রেডিকশন ইঞ্জিন - মাল্টি-ফ্যাক্টর অ্যালগরিদম
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

    # ============================================================
    # 📊 ফ্যাক্টর ১: ট্রেন্ড অ্যানালাইসিস (৬০% ওয়েট)
    # ============================================================
    def analyze_trend(self, numbers):
        """ট্রেন্ড বিশ্লেষণ - BIG/SMALL রেশিও"""
        if not numbers or len(numbers) < 5:
            return {'trend': 'neutral', 'score': 0, 'confidence': 50}
        
        bigs = sum(1 for n in numbers if n >= 5)
        smalls = len(numbers) - bigs
        
        # রেশিও ক্যালকুলেশন
        big_ratio = bigs / len(numbers) if len(numbers) > 0 else 0
        
        # ট্রেন্ড ডিটেকশন
        if big_ratio >= 0.65:
            return {'trend': 'BIG', 'score': 60, 'confidence': 85}
        elif big_ratio <= 0.35:
            return {'trend': 'SMALL', 'score': 60, 'confidence': 85}
        elif big_ratio >= 0.55:
            return {'trend': 'BIG', 'score': 40, 'confidence': 70}
        elif big_ratio <= 0.45:
            return {'trend': 'SMALL', 'score': 40, 'confidence': 70}
        else:
            return {'trend': 'neutral', 'score': 0, 'confidence': 50}

    # ============================================================
    # 🔄 ফ্যাক্টর ২: কনসিকিউটিভ প্যাটার্ন (২৫% ওয়েট)
    # ============================================================
    def analyze_consecutive(self, numbers):
        """কনসিকিউটিভ প্যাটার্ন বিশ্লেষণ"""
        if not numbers or len(numbers) < 3:
            return {'trend': 'neutral', 'score': 0, 'confidence': 0}
        
        last_three = numbers[-3:]
        all_big = all(n >= 5 for n in last_three)
        all_small = all(n < 5 for n in last_three)
        
        # কনসিকিউটিভ কাউন্ট
        consecutive_big = 0
        consecutive_small = 0
        for n in reversed(numbers):
            if n >= 5:
                if consecutive_small > 0:
                    break
                consecutive_big += 1
            else:
                if consecutive_big > 0:
                    break
                consecutive_small += 1
        
        # সিদ্ধান্ত
        if consecutive_big >= 3:
            return {'trend': 'SMALL', 'score': 25, 'confidence': 80}  # রিভার্স
        elif consecutive_small >= 3:
            return {'trend': 'BIG', 'score': 25, 'confidence': 80}   # রিভার্স
        elif consecutive_big >= 2:
            return {'trend': 'SMALL', 'score': 15, 'confidence': 65}
        elif consecutive_small >= 2:
            return {'trend': 'BIG', 'score': 15, 'confidence': 65}
        else:
            return {'trend': 'neutral', 'score': 0, 'confidence': 0}

    # ============================================================
    # 🔀 ফ্যাক্টর ৩: অল্টারনেটিং প্যাটার্ন (১৫% ওয়েট)
    # ============================================================
    def analyze_alternating(self, numbers):
        """অল্টারনেটিং প্যাটার্ন বিশ্লেষণ"""
        if not numbers or len(numbers) < 4:
            return {'trend': 'neutral', 'score': 0, 'confidence': 0}
        
        last_four = numbers[-4:]
        alternating = True
        for i in range(1, len(last_four)):
            if (last_four[i-1] >= 5) == (last_four[i] >= 5):
                alternating = False
                break
        
        if alternating:
            # অল্টারনেটিং হলে শেষ সংখ্যার উল্টোটা
            last = last_four[-1]
            if last >= 5:
                return {'trend': 'SMALL', 'score': 15, 'confidence': 70}
            else:
                return {'trend': 'BIG', 'score': 15, 'confidence': 70}
        else:
            return {'trend': 'neutral', 'score': 0, 'confidence': 0}

    # ============================================================
    # 🎯 মেইন প্রেডিক্ট ফাংশন - ৩ ফ্যাক্টর কম্বাইন
    # ============================================================
    def smart_predict(self, numbers):
        """
        মাল্টি-ফ্যাক্টর স্মার্ট প্রেডিক্ট
        - ট্রেন্ড (৬০%)
        - কনসিকিউটিভ (২৫%)
        - অল্টারনেটিং (১৫%)
        """
        if not numbers or len(numbers) < 5:
            # পর্যাপ্ত ডাটা না থাকলে র্যান্ডম
            num = random.randint(0, 9)
            return {
                'number': num,
                'bs': 'BIG' if num >= 5 else 'SMALL',
                'confidence': 50,
                'signal': 'WAIT',
                'reason': 'Insufficient data'
            }
        
        # ৩টি ফ্যাক্টর অ্যানালাইসিস
        trend_result = self.analyze_trend(numbers)
        consecutive_result = self.analyze_consecutive(numbers)
        alternating_result = self.analyze_alternating(numbers)
        
        # স্কোর যোগ করা
        scores = {'BIG': 0, 'SMALL': 0, 'neutral': 0}
        confidence = 0
        
        # ফ্যাক্টর ১: ট্রেন্ড (৬০%)
        if trend_result['trend'] == 'BIG':
            scores['BIG'] += 60
            confidence += trend_result['confidence'] * 0.6
        elif trend_result['trend'] == 'SMALL':
            scores['SMALL'] += 60
            confidence += trend_result['confidence'] * 0.6
        else:
            scores['neutral'] += 60
        
        # ফ্যাক্টর ২: কনসিকিউটিভ (২৫%)
        if consecutive_result['trend'] == 'BIG':
            scores['BIG'] += 25
            confidence += consecutive_result['confidence'] * 0.25
        elif consecutive_result['trend'] == 'SMALL':
            scores['SMALL'] += 25
            confidence += consecutive_result['confidence'] * 0.25
        else:
            scores['neutral'] += 25
        
        # ফ্যাক্টর ৩: অল্টারনেটিং (১৫%)
        if alternating_result['trend'] == 'BIG':
            scores['BIG'] += 15
            confidence += alternating_result['confidence'] * 0.15
        elif alternating_result['trend'] == 'SMALL':
            scores['SMALL'] += 15
            confidence += alternating_result['confidence'] * 0.15
        else:
            scores['neutral'] += 15
        
        # ফাইনাল ডিসিশন
        if scores['BIG'] > scores['SMALL'] and scores['BIG'] > 40:
            predicted = 'BIG'
            num = random.randint(5, 9)
            conf = round(confidence / 100 * 100) if confidence > 0 else 60
            reason = f"BIG (Score: {scores['BIG']})"
        elif scores['SMALL'] > scores['BIG'] and scores['SMALL'] > 40:
            predicted = 'SMALL'
            num = random.randint(0, 4)
            conf = round(confidence / 100 * 100) if confidence > 0 else 60
            reason = f"SMALL (Score: {scores['SMALL']})"
        else:
            # কনফিউজড - WAIT
            num = random.randint(0, 9)
            predicted = 'WAIT'
            conf = 0
            reason = f"WAIT (BIG:{scores['BIG']}, SMALL:{scores['SMALL']})"
        
        return {
            'number': num,
            'bs': predicted,
            'confidence': min(95, max(50, conf)),
            'signal': predicted,
            'reason': reason,
            'scores': scores
        }

    # ============================================================
    # 📡 পিরিয়ড সিঙ্ক ফাংশন
    # ============================================================
    def get_current_win_go_period(self):
        """উইংগোর বর্তমান পিরিয়ড ক্যালকুলেট করে"""
        now = datetime.now()
        base = datetime(2024, 1, 1, 0, 0, 0)
        seconds_diff = int((now - base).total_seconds())
        period_number = seconds_diff // 30
        base_period = 728000
        current_period = base_period + period_number
        return str(current_period)

    # ============================================================
    # 📊 API ডাটা ফেচ
    # ============================================================
    async def fetch_data(self):
        """API থেকে ডাটা সংগ্রহ - পিরিয়ড সিঙ্ক সহ"""
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
                                
                                # পিরিয়ড সিঙ্ক
                                try:
                                    api_period_int = int(api_latest_issue)
                                    win_go_period_int = int(win_go_period)
                                    diff = win_go_period_int - api_period_int
                                    
                                    if diff == 1:
                                        use_period = win_go_period
                                        logger.info(f"🔄 Period sync: Using WinGo period {win_go_period}")
                                    elif diff == 0:
                                        use_period = api_latest_issue
                                        logger.info(f"✅ Periods in sync: {api_latest_issue}")
                                    else:
                                        use_period = api_latest_issue
                                        logger.info(f"⚠️ Using API period: {api_latest_issue}")
                                except:
                                    use_period = api_latest_issue
                                
                                # নতুন পিরিয়ড চেক
                                if use_period != self.last_issue:
                                    self.last_issue = use_period
                                    self.history = numbers[:30]
                                    self.last_10_numbers = numbers[:10]
                                    
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
                                    
                                    # 🧠 স্মার্ট প্রেডিক্ট
                                    prediction = self.smart_predict(self.history)
                                    
                                    self.current_prediction = {
                                        'period': use_period,
                                        'prediction': prediction['bs'],
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
                                        'signal': prediction.get('signal', ''),
                                        'api_period': api_latest_issue,
                                        'win_go_period': win_go_period
                                    }
                                    
                                    logger.info(f"🎯 SMART PREDICTION: {self.current_prediction}")
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
        logger.error("❌ Cannot send signal")
        return
    
    signal_count += 1
    engine.total_trade += 1
    
    bar = get_confidence_bar(prediction['confidence'])
    dots = get_history_dots(prediction.get('history', []))
    bs_emoji = "🟢" if prediction['prediction'] == "BIG" else "🔴" if prediction['prediction'] == "SMALL" else "⏳"
    
    # স্মার্ট অ্যালগরিদম ইনফো
    algo_info = f"\n🧠 অ্যালগরিদম: {prediction.get('reason', 'N/A')}"
    if 'scores' in prediction and prediction['scores']:
        scores = prediction['scores']
        algo_info += f"\n📊 স্কোর: BIG {scores.get('BIG', 0)} | SMALL {scores.get('SMALL', 0)}"
    
    # পিরিয়ড সিঙ্ক ইনফো
    period_info = ""
    if 'api_period' in prediction and 'win_go_period' in prediction:
        if prediction['api_period'] != prediction['win_go_period']:
            period_info = f"\n🔄 সিঙ্ক: {prediction['api_period']} → {prediction['win_go_period']}"
    
    # সিগন্যাল টাইপ
    signal_type = "🎯" if prediction['prediction'] != "WAIT" else "⏳"
    signal_text = prediction['prediction'] if prediction['prediction'] != "WAIT" else "⏳ অপেক্ষা করুন"
    
    msg = f"""
{signal_type} *MASUD AI - স্মার্ট প্রেডিক্ট*
━━━━━━━━━━━━━━━━━━━━━━

🔢 *পিরিয়ড:* `{prediction['period'][-6:]}`{period_info}
🎯 *সিগন্যাল:* {bs_emoji} *{signal_text}*
🔢 *প্রেডিক্টেড নম্বর:* `{prediction['number'] if prediction['prediction'] != 'WAIT' else '--'}`
📊 *কনফিডেন্স:* {prediction['confidence']}% {bar if prediction['prediction'] != 'WAIT' else '⏳'}

📈 *ট্রেন্ড অ্যানালাইসিস:*
• লাস্ট ১০: {dots}
• BIG: {prediction.get('big_count', 0)} | SMALL: {prediction.get('small_count', 0)}
• কনসিকিউটিভ BIG: {prediction.get('consecutive_big', 0)}
• কনসিকিউটিভ SMALL: {prediction.get('consecutive_small', 0)}
{algo_info}

📊 *পরিসংখ্যান:*
🏆 উইন: {engine.win_count} | 💔 লস: {engine.loss_count}
🎯 একুরেসি: {engine.accuracy}% | 📈 ট্রেড #{engine.total_trade}

⏱️ {prediction['timestamp']}
━━━━━━━━━━━━━━━━━━━━━━
🅿🅾🆆🅴🆁🅴🅳 🅱🆈 🅼🅰🆂🆄🅳 🅰🅸
    """
    
    logger.info(f"📤 SENDING SIGNAL #{signal_count}: {prediction['prediction']}")
    await send_telegram_message(msg)
    logger.info(f"✅ Signal #{signal_count} sent")

async def check_result(prediction, actual_number):
    global engine
    
    if not prediction or actual_number is None or not engine:
        return
    
    # WAIT সিগন্যালের রেজাল্ট চেক করি না
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
    global is_running, last_signal, last_period, engine, signal_count
    
    logger.info("🔄 Signal loop started - SMART ALGORITHM ACTIVE")
    
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
🤖 *MASUD AI - স্মার্ট প্রেডিক্টর*
━━━━━━━━━━━━━━━━━━━━━━

📊 *স্ট্যাটাস:* {status}
🏆 *উইন:* {engine.win_count if engine else 0}
💔 *লস:* {engine.loss_count if engine else 0}
📈 *ট্রেড:* {engine.total_trade if engine else 0}
🎯 *একুরেসি:* {engine.accuracy if engine else 0}%

📌 *লাস্ট ১০:* {get_history_dots(engine.last_10_numbers) if engine else '---'}

🧠 *স্মার্ট অ্যালগরিদম:* ৩-ফ্যাক্টর সিস্টেম
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

🧠 *স্মার্ট অ্যালগরিদম:*
• ট্রেন্ড অ্যানালাইসিস (৬০%)
• কনসিকিউটিভ প্যাটার্ন (২৫%)
• অল্টারনেটিং প্যাটার্ন (১৫%)

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
            await edit_message_text(chat_id, message_id, "✅ সিগন্যাল চালু হয়েছে! স্মার্ট অ্যালগরিদম সক্রিয়।")
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
🎯 সিগন্যাল: {'🟢' if p['prediction'] == 'BIG' else '🔴' if p['prediction'] == 'SMALL' else '⏳'} *{p['prediction']}*
📊 কনফিডেন্স: {p['confidence']}% {bar}

📈 *ট্রেন্ড অ্যানালাইসিস:*
• লাস্ট ১০: {dots}
• BIG: {p.get('big_count', 0)} | SMALL: {p.get('small_count', 0)}

🧠 *অ্যালগরিদম:* {p.get('reason', 'N/A')}

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
    logger.info("🧠 SMART ALGORITHM: Multi-Factor Analysis")
    logger.info("   📊 Trend (60%) + 🔄 Consecutive (25%) + 🔀 Alternating (15%)")
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
    print("  🧠 SMART ALGORITHM ACTIVE")
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
