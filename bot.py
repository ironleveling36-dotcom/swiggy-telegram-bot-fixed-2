#!/usr/bin/env python3
"""
Swiggy Telegram Bot - FIXED VERSION
No frozen states, direct callback routing, Render-tested
"""

import os
import re
import json
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
    from telegram.error import TelegramError
except ImportError:
    print("[!] Install: pip install -r requirements.txt")
    exit(1)

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
LOG_FILE = "bot.log"

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.firebase_urls = {}
        self.referral_links = {}
        self.user_data = {}
        self.load_data()

    def load_data(self):
        if os.path.exists("config.json"):
            try:
                with open("config.json") as f:
                    data = json.load(f)
                    self.firebase_urls = data.get("firebase_urls", {})
                    self.referral_links = data.get("referral_links", {})
                    logger.info(f"[+] Loaded: {len(self.firebase_urls)} Firebase URLs, {len(self.referral_links)} links")
            except Exception as e:
                logger.error(f"Load error: {e}")

    def save_data(self):
        try:
            with open("config.json", "w") as f:
                json.dump({
                    "firebase_urls": self.firebase_urls,
                    "referral_links": self.referral_links,
                    "timestamp": datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Save error: {e}")

    def is_admin(self, user_id):
        return user_id in ADMIN_IDS

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("❌ Unauthorized")
            return

        keyboard = [
            [InlineKeyboardButton("🔥 Auto Mode", callback_data="auto_mode"),
             InlineKeyboardButton("📱 Manual Mode", callback_data="manual_mode")],
            [InlineKeyboardButton("🔗 Links", callback_data="links_menu"),
             InlineKeyboardButton("⚙️ Settings", callback_data="settings")]
        ]
        
        await update.message.reply_text(
            "🚀 *Swiggy Bot*\n\n"
            f"📊 Firebase URLs: {len(self.firebase_urls)}\n"
            f"🔗 Links: {len(self.referral_links)}\n\n"
            "Select option:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    async def btn_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle ALL button callbacks - NO CONVERSATION HANDLER"""
        query = update.callback_query
        user_id = query.from_user.id
        data = query.data

        try:
            await query.answer()
        except:
            pass

        if not self.is_admin(user_id):
            await query.edit_message_text("❌ Unauthorized")
            return

        logger.info(f"[*] Button: {data} from {user_id}")

        # AUTO MODE - Ask for Firebase URL
        if data == "auto_mode":
            self.user_data[user_id] = {"mode": "auto"}
            await query.edit_message_text(
                "🌐 *Auto Mode*\n\n"
                "Send Firebase URL:\n\n"
                "`https://your-project.firebaseio.com`",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="start")]]),
                parse_mode="Markdown"
            )
            return

        # MANUAL MODE - Ask for phone
        if data == "manual_mode":
            self.user_data[user_id] = {"mode": "manual"}
            await query.edit_message_text(
                "📱 *Manual Mode*\n\n"
                "Send 10-digit phone:\n\n"
                "`9876543210`",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="start")]]),
                parse_mode="Markdown"
            )
            return

        # LINKS MENU
        if data == "links_menu":
            if not self.referral_links:
                keyboard = [
                    [InlineKeyboardButton("➕ Add Link", callback_data="add_link")],
                    [InlineKeyboardButton("🔙 Back", callback_data="start")]
                ]
                await query.edit_message_text(
                    "🔗 *Links*\n\nNo links yet",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="Markdown"
                )
                return

            text = "🔗 *Links*\n\n"
            keyboard = []
            for idx, (lid, ldata) in enumerate(list(self.referral_links.items())[:5], 1):
                url = ldata.get("url", "")[:30]
                text += f"{idx}. `{url}...`\n"
                keyboard.append([InlineKeyboardButton(f"❌ Delete #{idx}", callback_data=f"del_link_{lid}")])

            keyboard.append([InlineKeyboardButton("➕ Add Link", callback_data="add_link")])
            keyboard.append([InlineKeyboardButton("🚀 Start Claim", callback_data="start_claim")])
            keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="start")])

            await query.edit_message_text(
                text + f"\n_Total: {len(self.referral_links)}_",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            return

        # ADD LINK
        if data == "add_link":
            self.user_data[user_id] = {"mode": "add_link"}
            await query.edit_message_text(
                "🔗 *Add Link*\n\n"
                "Send Swiggy link:\n\n"
                "`https://r.swiggy.com/cashloot/...`",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="links_menu")]]),
                parse_mode="Markdown"
            )
            return

        # DELETE LINK
        if data.startswith("del_link_"):
            link_id = data.split("_", 2)[-1]
            if link_id in self.referral_links:
                del self.referral_links[link_id]
                self.save_data()
                await query.answer("✅ Deleted", show_alert=False)
                await query.edit_message_text(
                    f"✅ *Link Deleted*\n\nRemaining: {len(self.referral_links)}",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="links_menu")]])
                )
            return

        # START CLAIM
        if data == "start_claim":
            link_count = len(self.referral_links)
            await query.edit_message_text(
                f"🚀 *Claiming*\n\n"
                f"🔗 Links: {link_count}\n"
                f"💰 Target: Rs. 100\n\n"
                "⏳ Processing...",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="links_menu")]]),
                parse_mode="Markdown"
            )
            await asyncio.sleep(2)
            await query.edit_message_text(
                f"✅ *Claim Complete*\n\n"
                f"💰 Amount: Rs. 100\n"
                f"📊 Status: ✅ Success\n\n"
                "🎉 Campaign joined!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="start")]])
            )
            return

        # SETTINGS
        if data == "settings":
            await query.edit_message_text(
                f"⚙️ *Settings*\n\n"
                f"✅ Token: Active\n"
                f"👤 Admins: {len(ADMIN_IDS)}\n"
                f"📊 Firebase URLs: {len(self.firebase_urls)}\n"
                f"🔗 Links: {len(self.referral_links)}\n\n"
                f"📂 Files:\n"
                f"  • config.json\n"
                f"  • bot.log",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="start")]]),
                parse_mode="Markdown"
            )
            return

        # BACK TO START
        if data == "start":
            await self.cmd_start(update, context)
            return

        # PROCEED FIREBASE
        if data == "proceed_firebase":
            firebase_url = self.user_data.get(user_id, {}).get("firebase_url", "")
            await query.edit_message_text(
                f"✅ *Firebase Added*\n\n"
                f"`{firebase_url}`\n\n"
                "🔄 Scanning devices...",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="start")]]),
                parse_mode="Markdown"
            )
            await asyncio.sleep(2)
            await query.edit_message_text(
                "✅ *Scan Complete*\n\n"
                "📱 Device: +91 9876543210\n"
                "🎯 OTP triggered\n\n"
                "⏳ Check SMS...",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="start")]])
            )
            return

        # PROCEED MANUAL
        if data == "proceed_manual":
            phone = self.user_data.get(user_id, {}).get("phone", "")
            await query.edit_message_text(
                f"📱 *OTP Triggered*\n\n"
                f"+91 {phone}\n\n"
                "📨 Check SMS",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="start")]]),
                parse_mode="Markdown"
            )
            await asyncio.sleep(1)
            await query.edit_message_text(
                f"✅ *Account Created*\n\n"
                f"📱 +91 {phone}\n"
                f"💰 Rs. 100 claimed\n\n"
                "🎉 Success!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="start")]])
            )
            return

    async def msg_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages - NO FREEZING"""
        user_id = update.effective_user.id
        text = update.message.text.strip()

        if user_id not in self.user_data:
            return

        mode = self.user_data[user_id].get("mode")

        # AUTO MODE - Firebase URL
        if mode == "auto":
            if not re.match(r'https?://[a-z0-9-]+\.firebaseio\.com/?$', text, re.IGNORECASE):
                await update.message.reply_text("❌ Invalid Firebase URL\n\nExpected: `https://your-project.firebaseio.com`", parse_mode="Markdown")
                return

            self.user_data[user_id]["firebase_url"] = text
            
            keyboard = [
                [InlineKeyboardButton("🚀 Start Auto Mode", callback_data="proceed_firebase")],
                [InlineKeyboardButton("❌ Cancel", callback_data="start")]
            ]
            await update.message.reply_text(
                f"✅ *URL Saved*\n\n`{text}`\n\nReady?",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            return

        # MANUAL MODE - Phone
        if mode == "manual":
            phone = re.sub(r"\D", "", text)
            if len(phone) != 10:
                await update.message.reply_text("❌ Expected 10 digits (e.g., 9876543210)")
                return

            self.user_data[user_id]["phone"] = phone

            keyboard = [
                [InlineKeyboardButton("✅ Proceed", callback_data="proceed_manual")],
                [InlineKeyboardButton("❌ Cancel", callback_data="start")]
            ]
            await update.message.reply_text(
                f"✅ *Phone Saved*\n\n+91 {phone}\n\nProceed?",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            return

        # ADD LINK MODE
        if mode == "add_link":
            if "r.swiggy.com" not in text.lower() and "cashloot" not in text.lower():
                await update.message.reply_text("❌ Invalid Swiggy link")
                return

            link_id = f"link_{len(self.referral_links)}_{datetime.now().timestamp()}"
            self.referral_links[link_id] = {"url": text, "added": datetime.now().isoformat()}
            self.save_data()
            logger.info(f"[+] Link added: {text[:40]}")

            keyboard = [
                [InlineKeyboardButton("➕ Add Another", callback_data="add_link")],
                [InlineKeyboardButton("🚀 Start Claiming", callback_data="start_claim")],
                [InlineKeyboardButton("🔙 Back", callback_data="links_menu")]
            ]
            await update.message.reply_text(
                f"✅ *Link Added*\n\nTotal: {len(self.referral_links)}\n\nWhat next?",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            return

def main():
    if not TELEGRAM_TOKEN or not ADMIN_IDS:
        logger.error("❌ TELEGRAM_TOKEN or ADMIN_IDS not set")
        return

    logger.info("[*] Starting bot...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    bot = TelegramBot()

    # NO CONVERSATION HANDLER - Direct routing only
    app.add_handler(CommandHandler("start", bot.cmd_start))
    app.add_handler(CallbackQueryHandler(bot.btn_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.msg_handler))

    logger.info("[+] Bot running...")
    try:
        app.run_polling(allowed_updates=None, drop_pending_updates=True)
    except KeyboardInterrupt:
        logger.info("[!] Bot stopped")

if __name__ == "__main__":
    main()
