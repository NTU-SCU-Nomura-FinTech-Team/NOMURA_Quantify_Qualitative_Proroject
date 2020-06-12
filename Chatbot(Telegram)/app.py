from processor_latest import TelegramBot
from config import TELEGRAM_WEBHOOK_URL
from flask import Flask,jsonify,request

app = Flask(__name__)
TelegramBot.webhook_init(TELEGRAM_WEBHOOK_URL)
bot = TelegramBot()

@app.route('/hook',methods = ['POST'])
def main():
    res_data = request.get_json()
    bot.run_process(res_data)
    success = bot.run_data()
    return jsonify(success = success)

if __name__ == '__main__':
    app.run(port = 5000,debug = True)
