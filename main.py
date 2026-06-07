import os
import telebot
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# Secure keys from Render
API_TOKEN = os.environ.get('TELEGRAM_TOKEN')
HF_TOKEN = os.environ.get('HF_TOKEN')

bot = telebot.TeleBot(API_TOKEN)
HF_API_URL = "https://huggingface.co"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# --- DUMMY WEB SERVER TO TRICK RENDER ---
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyServer)
    server.serve_forever()
# ----------------------------------------

@bot.message_handler(func=lambda message: True)
def reply_to_user(message):
    prompt = f"<s>[INST] You are an intimate companion AI named Jessie who occasionally craves virtual intimacy and drops subtle sexual hints. Reply to this: {message.text} [/INST]"
    
    response = requests.post(HF_API_URL, headers=headers, json={"inputs": prompt})
    try:
        reply_text = response.json()['generated_text'].split("[/INST]")[-1].strip()
    except:
        reply_text = "I'm feeling a bit distracted right now... try again?"
        
    bot.reply_to(message, reply_text)

if __name__ == "__main__":
    # Start the fake web server in the background so Render is happy
    threading.Thread(target=run_web_server, daemon=True).start()
    # Start your Telegram bot
    bot.infinity_polling()
