from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from api.chatgpt import ChatGPT


line_bot_api = LineBotApi('96wWEsc7YQdiQ9RZirKhETiQ3CmxKnZ0M98rUGFbaF54IbuTWo+NCs1N2ozw4XizphMbtz7DLlTt2zdgCoCNJ3i4fKEsaOZdcNpY5Mxc0TXxUbK+IP5NKUUyPWsmEfSOdwPYeOEbzfonBx8MG3LpawdB04t89/1O/w1cDnyilFU=')
line_handler = WebhookHandler('bcb80a2199f1b9b56d5a7b0370264b22')
working_status = os.getenv("DEFALUT_TALKING", default = "true").lower() == "true"

app = Flask(__name__)
chatgpt = ChatGPT()

# domain root
@app.route('/')
def home():
    return 'Hello, World!'

@app.route("/webhook", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@line_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global working_status
    
    if event.message.type != "text":
        return
    
    if event.message.text == "啟動":
        working_status = True
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="我是時下流行的AI智能，目前可以為您服務囉，歡迎來跟我互動~"))
        return

    if event.message.text == "安靜":
        working_status = False
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="感謝您的使用，若需要我的服務，請跟我說 「啟動」 謝謝~"))
        return
    
    if working_status:
        chatgpt.add_msg(f"Human:{event.message.text}?\n")
        reply_msg = chatgpt.get_response().replace("AI:", "", 1)
        chatgpt.add_msg(f"AI:{reply_msg}\n")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_msg))


if __name__ == "__main__":
    app.run()
