import telebot
import requests
import feedparser
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# === CONFIGURATION ===
BOT_TOKEN = "7253081903:AAGhTu6nCRJLRw0B6V02Qxhn0ZU_Hv2BGhE"  # 🔹 Replace with your Telegram bot token
CHANNEL_ID = "@YOUR_CHANNEL_USERNAME"  # 🔹 Replace with your Telegram channel username
DISCUSSION_CHANNEL_ID = "-100XXXXXXXXXX"  # 🔹 Replace with your Discussion Channel ID (optional)
BLOG_FEED_URL = "https://YOURBLOGNAME.blogspot.com/feeds/posts/default"  # 🔹 Replace with your Blogger feed URL
JOIN_CHANNEL_LINK = "https://t.me/YOUR_CHANNEL_USERNAME"  # 🔹 Replace with your channel join link

bot = telebot.TeleBot(BOT_TOKEN)

# === Function to Fetch Latest Blog Post ===
def get_latest_blog_post():
    feed = feedparser.parse(BLOG_FEED_URL)
    latest_post = feed.entries[0]  
    title = latest_post.title  
    link = latest_post.link  

    # Extracting Image from Blog Post
    if "media_thumbnail" in latest_post:
        image_url = latest_post.media_thumbnail[0]['url']
    else:
        image_url = "https://via.placeholder.com/600x400.png?text=No+Image"

    return title, link, image_url

# === Command to Post in Channel ===
@bot.message_handler(commands=['post'])
def send_blog_update(message):
    title, link, image_url = get_latest_blog_post()

    # Create "Join Channel" Button
    markup = InlineKeyboardMarkup()
    join_button = InlineKeyboardButton("🔒 Join Channel to Get Link", url=JOIN_CHANNEL_LINK)
    unlock_button = InlineKeyboardButton("✅ I've Joined! Give Me Link", callback_data=f"unlock_{link}")
    markup.add(join_button)
    markup.add(unlock_button)

    # Send Post with Image
    bot.send_photo(CHANNEL_ID, image_url, caption=f"📢 **New Blog Post:** {title}\n\n🔗 Click below to unlock the link!", reply_markup=markup, parse_mode="Markdown")

# === Callback to Unlock Link After Joining ===
@bot.callback_query_handler(func=lambda call: call.data.startswith("unlock_"))
def unlock_link(call):
    user_id = call.from_user.id
    link = call.data.split("_")[1]

    try:
        chat_member = bot.get_chat_member(CHANNEL_ID, user_id)
        if chat_member.status in ["member", "administrator", "creator"]:
            bot.send_message(call.message.chat.id, f"✅ Here is your link: {link}")
        else:
            retry_markup = InlineKeyboardMarkup()
            retry_button = InlineKeyboardButton("🔄 Try Again", callback_data=f"unlock_{link}")
            retry_markup.add(retry_button)
            bot.send_message(call.message.chat.id, "❌ You haven't joined the channel yet. Join and try again!", reply_markup=retry_markup)
    except:
        bot.send_message(call.message.chat.id, "❌ Error verifying your membership. Try again later.")

# === Start Bot Polling ===
bot.polling()
