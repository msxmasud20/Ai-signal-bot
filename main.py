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
║      🤖 MASUD AI - IMAGE INTEGRATED BOT                     ║
║      🚀 VERSION 16.0 - FULL IMAGE SUPPORT                   ║
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
# 🖼️ ইমেজ ম্যানেজার - আপনার দেওয়া ইমেজ সহ
# ============================================================
class ImageManager:
    def __init__(self):
        # 🔥 আপনার দেওয়া ইমেজ URL গুলো
        self.images = {
            'BIG': 'https://i.ibb.co/BHwgsCBR/image.jpg',
            'SMALL': 'https://i.ibb.co/6J8pG77S/image.jpg',
            'WIN': 'https://i.ibb.co/93nTjNTW/image.jpg',
            'LOSS': 'https://i.ibb.co/1YPF3Hk0/image.jpg',
            'JACKPOT': 'https://i.ibb.co/VpkQySHZ/image.jpg'
        }
        self.pending_image = None
    
    def get_image(self, signal_type):
        """সিগন্যাল টাইপ অনুযায়ী ইমেজ URL রিটার্ন করে"""
        return self.images.get(signal_type, None)
    
    def set_image(self, signal_type, image_data):
        if signal_type in self.images:
            self.images[signal_type] = image_data
            return True
        return False

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
                return response.status == 200
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return False

async def send_telegram_photo(caption, photo_url, chat_id=None):
    """ইমেজ সহ মেসেজ পাঠায়"""
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

    def calculate_stats(self, numbers):
        if not numbers:
            return {'avg': 0, 'median': 0, 'mode': 0, 'big_ratio': 0}
        
        avg = sum(numbers) / len(numbers)
        sorted_nums = sorted(numbers)
        n = len(sorted_nums)
        if n % 2 == 0:
            median = (sorted_nums[n//2 - 1] + sorted_nums[n//2]) / 2
        else:
            median = sorted_nums[n//2]
        
        counter = Counter(numbers)
        mode = counter.most_common(1)[0][0] if counter else 0
        big_ratio = sum(1 for n in numbers if n >= 5) / len(numbers)
        
        return {
            'avg': round(avg, 2),
            'median': median,
            'mode': mode,
            'big_ratio': round(big_ratio * 100, 1)
        }

    def smart_predict(self, numbers):
        if not numbers or len(numbers) < 5:
            num = random.randint(0, 9)
            return {
                'signal': 'BIG' if num >= 5 else 'SMALL',
                'number': num,
                'confidence': 50,
                'stats': self.calculate_stats(numbers)
            }
        
        stats = self.calculate_stats(numbers)
        big_ratio = stats['big_ratio'] / 100
        
        score_big = 0
        score_small = 0
        
        if big_ratio >= 0.55:
            score_big += 40
        elif big_ratio <= 0.45:
            score_small += 40
        else:
            score_big += 20
            score_small += 20
        
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
        
        if consecutive_big >= 3:
            score_small += 30
        elif consecutive_small >= 3:
            score_big += 30
        elif consecutive_big >= 2:
            score_small += 15
        elif consecutive_small >= 2:
            score_big += 15
        else:
            score_big += 10
            score_small += 10
        
        last_5 = numbers[-5:]
        alternating = all((last_5[i] >= 5) != (last_5[i+1] >= 5) for i in range(4)) if len(last_5) >= 5 else False
        
        if alternating:
            last = numbers[-1]
            if last >= 5:
                score_small += 20
            else:
                score_big += 20
        else:
            score_big += 10
            score_small += 10
        
        if stats['avg'] >= 5.5:
            score_small += 10
        elif stats['avg'] <= 4.5:
            score_big += 10
        
        if stats['mode'] >= 5:
            score_small += 5
        elif stats['mode'] < 5:
            score_big += 5
        
        if score_big > score_small:
            signal = 'BIG'
            num = random.randint(5, 9)
            confidence = min(90, 55 + (score_big - score_small))
        elif score_small > score_big:
            signal = 'SMALL'
            num = random.randint(0, 4)
            confidence = min(90, 55 + (score_small - score_big))
        else:
            num = random.randint(0, 9)
            signal = 'BIG' if num >= 5 else 'SMALL'
            confidence = 55
        
        return {
            'signal': signal,
            'number': num,
            'confidence': min(95, confidence),
            'stats': stats,
            'scores': {'BIG': score_big, 'SMALL': score_small}
        }

    def sync_period(self, api_period):
        try:
            api_int = int(api_period)
            return str(api_int + 1)
        except:
            return api_period

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
                                        'scores': prediction.get('scores', {}),
                                        'api_period': api_latest_issue
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

def get_admin_keyboard():
    return [
        [
            {"text": "🟢 BIG ইমেজ", "callback_data": "upload_big"},
            {"text": "🔴 SMALL ইমেজ", "callback_data": "upload_small"}
        ],
        [
            {"text": "🏆 WIN ইমেজ", "callback_data": "upload_win"},
            {"text": "💔 LOSS ইমেজ", "callback_data": "upload_loss"}
        ],
        [
            {"text": "💰 JACKPOT ইমেজ", "callback_data": "upload_jackpot"},
            {"text": "📊 স্ট্যাটাস", "callback_data": "admin_stats"}
        ],
        [
            {"text": "🔙 ব্যাক", "callback_data": "back_to_main"}
        ]
    ]

# ============================================================
# 📤 সিগন্যাল ফাংশন - ইমেজ সহ
# ============================================================
async def send_signal(prediction, previous_result=None):
    global engine, signal_count, total_loss, total_profit
    
    if not prediction or not engine:
        return
    
    signal_count += 1
    engine.total_trade += 1
    
    # 🔥 সিগন্যাল অনুযায়ী ইমেজ সিলেক্ট
    signal_image = image_manager.get_image(prediction['prediction'])
    
    # 🖼️ ক্যাপশন তৈরি - ছোট ফরম্যাট
    caption = f"""
🎯 *Predicted signal:* {prediction['prediction']}
📌 *Period:* {prediction['period'][-6:]}
🔢 *Number:* {prediction['number']}
🏆 *Total win:* {engine.win_count}
💔 *Total loss:* {engine.loss_count}
    """
    
    # 🔥 জ্যাকপট চেক - নাম্বার + সাইড মিললে
    is_jackpot = False
    if (prediction['number'] >= 5 and prediction['prediction'] == 'BIG') or \
       (prediction['number'] < 5 and prediction['prediction'] == 'SMALL'):
        is_jackpot = True
        jackpot_image = image_manager.get_image('JACKPOT')
        caption += f"\n💰 *JACKPOT!* 🎯"
    
    # 📤 ইমেজ সহ মেসেজ পাঠান
    if signal_image:
        await send_telegram_photo(caption, signal_image)
        logger.info(f"📤 Signal #{signal_count}: {prediction['prediction']} with image")
    else:
        # ইমেজ না থাকলে টেক্সট মেসেজ
        await send_telegram_message(caption)
        logger.info(f"📤 Signal #{signal_count}: {prediction['prediction']} (no image)")
    
    # 🔥 জ্যাকপট হলে আলাদা জ্যাকপট ইমেজ পাঠান
    if is_jackpot and jackpot_image:
        jackpot_caption = f"🎰 *JACKPOT WINNER!*\n📌 Period: {prediction['period'][-6:]}\n🎯 {prediction['prediction']} + {prediction['number']} = JACKPOT! 🎰"
        await send_telegram_photo(jackpot_caption, jackpot_image)
        logger.info(f"🎰 Jackpot sent for period {prediction['period']}")

# ============================================================
# 📊 রেজাল্ট চেক - ইমেজ সহ
# ============================================================
async def check_result(prediction, actual_number):
    global engine, last_result, total_loss, total_profit
    
    if not prediction or actual_number is None or not engine:
        return
    
    actual_bs = "BIG" if actual_number >= 5 else "SMALL"
    is_win = prediction['prediction'] == actual_bs
    
    # 🔥 রেজাল্ট অনুযায়ী ইমেজ
    if is_win:
        engine.win_count += 1
        result_text = "✅ WIN 🏆"
        result_image = image_manager.get_image('WIN')
    else:
        engine.loss_count += 1
        result_text = "❌ LOSS 💔"
        result_image = image_manager.get_image('LOSS')
    
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
    
    # 📊 ক্যাপশন তৈরি
    caption = f"""
{result_text}
📌 *Period:* {prediction['period'][-6:]}
🎯 *Predict:* {prediction['prediction']} → *{actual_bs}* ({actual_number})
🏆 *Total win:* {engine.win_count}
💔 *Total loss:* {engine.loss_count}
🎯 *Accuracy:* {engine.accuracy}%
    """
    
    # 📤 রেজাল্ট ইমেজ পাঠান
    if result_image:
        await send_telegram_photo(caption, result_image)
    else:
        await send_telegram_message(caption)
    logger.info(f"📊 Result: {result_text}")

# ============================================================
# 🔄 সিগন্যাল লুপ
# ============================================================
async def signal_loop():
    global is_running, last_signal, last_period, engine, last_result
    
    logger.info("🔄 Signal loop started - Image integrated")
    
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
# মেসেজ হ্যান্ডলার
# ============================================================
async def handle_message(message):
    global is_running, engine, admin_session
    
    text = message.get('text', '')
    chat_id = str(message['chat']['id'])
    user_id = str(message['from']['id'])
    
    if chat_id != str(CHAT_ID):
        return
    
    if text == '/admin':
        admin_session[user_id] = {'step': 'awaiting_password'}
        await send_telegram_message(
            "🔐 *Admin Panel*\n\nPlease enter password:",
            chat_id
        )
        return
    
    if user_id in admin_session and admin_session[user_id].get('step') == 'awaiting_password':
        if text == ADMIN_PASSWORD:
            admin_session[user_id] = {'step': 'authenticated'}
            await send_telegram_keyboard(
                "✅ *Admin Panel Opened!*",
                get_admin_keyboard(),
                chat_id
            )
        else:
            await send_telegram_message("❌ *Wrong password!*", chat_id)
            admin_session.pop(user_id, None)
        return
    
    if text == '/start':
        status = "🟢 Running" if is_running else "🔴 Stopped"
        msg = f"""
🤖 *MASUD AI Bot*
━━━━━━━━━━━━━━━━━━━

📊 *Status:* {status}
🏆 *Win:* {engine.win_count if engine else 0}
💔 *Loss:* {engine.loss_count if engine else 0}
🎯 *Accuracy:* {engine.accuracy if engine else 0}%

⏱️ Collect :30 & :00, Signal :35 & :05
🖼️ Image integrated
        """
        await send_telegram_keyboard(msg, get_start_keyboard(), chat_id)
    
    elif text == '/predict':
        if engine:
            prediction = await engine.fetch_data()
            if prediction:
                await send_signal(prediction)
            else:
                await send_telegram_message("⏳ Signal generating...", chat_id)
        else:
            await send_telegram_message("⏳ Engine initializing...", chat_id)
    
    elif text == '/stats':
        if not engine:
            await send_telegram_message("⏳ Loading data...", chat_id)
            return
        
        stats = f"""
📊 *Statistics*
━━━━━━━━━━━━━━━━━━━

📈 Total Trade: {engine.total_trade}
🏆 Win: {engine.win_count}
💔 Loss: {engine.loss_count}
🎯 Accuracy: {engine.accuracy}%
📡 Status: {'🟢 Running' if is_running else '🔴 Stopped'}

📌 Last 10: {get_history_dots(engine.last_10_numbers)}
        """
        await send_telegram_message(stats, chat_id)
    
    elif text == '/help':
        help_text = """
🤖 *MASUD AI Bot - Help*

📌 *Commands:*
/start - Start bot
/predict - Instant signal
/stats - Statistics
/help - Help
/admin - Admin panel

⏱️ *Timing:*
• :30 Data collect
• :35 Signal
• :00 Data collect
• :05 Signal

🖼️ *Images:*
• BIG, SMALL, WIN, LOSS, JACKPOT
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
    
    if data in ['upload_big', 'upload_small', 'upload_win', 'upload_loss', 'upload_jackpot']:
        if not is_admin:
            await answer_callback(callback_id, "⛔ Admin only!")
            return
        
        image_type = data.replace('upload_', '').upper()
        admin_session[user_id]['pending_image'] = image_type
        await edit_message_text(
            chat_id, message_id,
            f"📤 *Upload {image_type} Image*\n\nSend image URL or file:",
            get_admin_keyboard()
        )
        await answer_callback(callback_id, f"📤 Waiting for {image_type} image...")
        return
    
    if data == 'admin_stats':
        if not is_admin:
            await answer_callback(callback_id, "⛔ Admin only!")
            return
        
        stats = f"""
📊 *Admin Stats*
━━━━━━━━━━━━━━━━━━━

📈 Trade: {engine.total_trade if engine else 0}
🏆 Win: {engine.win_count if engine else 0}
💔 Loss: {engine.loss_count if engine else 0}
🎯 Accuracy: {engine.accuracy if engine else 0}%
📡 Status: {'🟢 Running' if is_running else '🔴 Stopped'}

🖼️ *Images:*
• BIG: {image_manager.get_image('BIG')[:30]}...
• SMALL: {image_manager.get_image('SMALL')[:30]}...
• WIN: {image_manager.get_image('WIN')[:30]}...
• LOSS: {image_manager.get_image('LOSS')[:30]}...
• JACKPOT: {image_manager.get_image('JACKPOT')[:30]}...
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
🤖 *MASUD AI Bot*
━━━━━━━━━━━━━━━━━━━

📊 *Status:* {status}
🏆 *Win:* {engine.win_count if engine else 0}
💔 *Loss:* {engine.loss_count if engine else 0}
🎯 *Accuracy:* {engine.accuracy if engine else 0}%
        """
        await edit_message_text(chat_id, message_id, msg, get_start_keyboard())
        await answer_callback(callback_id, "🔙 Back to main menu")
        return
    
    if data == "start_signal":
        if not is_running:
            is_running = True
            asyncio.create_task(signal_loop())
            await answer_callback(callback_id, "✅ Signal started!")
            await edit_message_text(chat_id, message_id, "✅ Signal started!\n⏱️ :30 & :00 Data, :35 & :05 Signal\n🖼️ Images integrated")
        else:
            await answer_callback(callback_id, "⚠️ Already running!")
    
    elif data == "stop_signal":
        is_running = False
        await answer_callback(callback_id, "🔴 Signal stopped!")
        await edit_message_text(chat_id, message_id, "🔴 Signal stopped.")
    
    elif data == "stats":
        if not engine:
            await answer_callback(callback_id, "⏳ Loading data...")
            return
        
        stats = f"""
📊 *Statistics*
━━━━━━━━━━━━━━━━━━━

📈 Total Trade: {engine.total_trade}
🏆 Win: {engine.win_count}
💔 Loss: {engine.loss_count}
🎯 Accuracy: {engine.accuracy}%
📡 Status: {'🟢 Running' if is_running else '🔴 Stopped'}

📌 Last 10: {get_history_dots(engine.last_10_numbers)}
        """
        await edit_message_text(chat_id, message_id, stats)
        await answer_callback(callback_id, "📊 Showing stats")
    
    elif data == "live":
        if engine and engine.current_prediction:
            p = engine.current_prediction
            signal = f"""
📡 *Live Signal*
━━━━━━━━━━━━━━━━━━━

📌 Period: {p['period'][-6:]}
🎯 Predict: {p['prediction']}
🔢 Number: {p['number']}
📊 Confidence: {p['confidence']}%
⏱️ {p['timestamp']}
            """
            await edit_message_text(chat_id, message_id, signal)
            await answer_callback(callback_id, "📡 Showing live signal")
        else:
            await answer_callback(callback_id, "⏳ No signal available")
    
    elif data == "trade_history":
        if not engine or not engine.trade_history:
            await answer_callback(callback_id, "❌ No trades")
            return
        
        history = "📈 *Trade History*\n━━━━━━━━━━━━━━━━━━━\n"
        for i, t in enumerate(engine.trade_history[-10:], 1):
            icon = "✅" if t['result'] == "Win" else "❌"
            history += f"{i}. {icon} {t['prediction']} → {t['actual']} ({t['number']})\n"
        
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
            f"✅ *{pending} image uploaded successfully!*",
            chat_id
        )
        await send_telegram_keyboard(
            "🖼️ *Image Settings*",
            get_admin_keyboard(),
            chat_id
        )
        return
    
    if 'text' in message:
        text = message['text']
        if text.startswith(('http://', 'https://')):
            image_manager.set_image(pending, text)
            admin_session[user_id]['pending_image'] = None
            await send_telegram_message(
                f"✅ *{pending} image uploaded successfully!*",
                chat_id
            )
            await send_telegram_keyboard(
                "🖼️ *Image Settings*",
                get_admin_keyboard(),
                chat_id
            )
            return
    
    await send_telegram_message(
        "❌ *Invalid input!* Please send image file or URL.",
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
    global engine, is_running, image_manager
    
    print_banner()
    logger.info("🤖 Starting Masud AI Bot...")
    logger.info(f"📡 Bot Token: {BOT_TOKEN[:10]}...")
    logger.info(f"📢 Chat ID: {CHAT_ID}")
    logger.info("=" * 60)
    logger.info("🔐 ADMIN PANEL: /admin")
    logger.info("🔑 PASSWORD: msxmasud20")
    logger.info("🖼️ IMAGES INTEGRATED:")
    logger.info("   BIG: https://i.ibb.co/BHwgsCBR/image.jpg")
    logger.info("   SMALL: https://i.ibb.co/6J8pG77S/image.jpg")
    logger.info("   WIN: https://i.ibb.co/93nTjNTW/image.jpg")
    logger.info("   LOSS: https://i.ibb.co/1YPF3Hk0/image.jpg")
    logger.info("   JACKPOT: https://i.ibb.co/VpkQySHZ/image.jpg")
    logger.info("⏱️ Collect :30 & :00, Signal :35 & :05")
    logger.info("=" * 60)
    
    image_manager = ImageManager()
    engine = PredictionEngine()
    
    logger.info("📡 Fetching initial data...")
    await engine.fetch_data()
    logger.info("✅ Initial data fetched")
    
    is_running = True
    asyncio.create_task(signal_loop())
    
    logger.info("✅ Bot is ready and running!")
    print("\n" + "=" * 60)
    print("  ✅ MASUD AI BOT IS NOW RUNNING!")
    print("  🖼️ IMAGES INTEGRATED")
    print("  ⏱️ Collect :30 & :00, Signal :35 & :05")
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
