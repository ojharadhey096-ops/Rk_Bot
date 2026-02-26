import os
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Any, List

from dotenv import load_dotenv
from telegram import Update, ForceReply, ParseMode
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Conversation states
WAITING_FOR_NIGHT_PLAN = 1

# Helper: naive Hindi time parser (very simple)
def parse_hindi_time_to_24h(text: str) -> str:
    try:
        # Extract number before 'baje'
        t = None
        lowered = text.lower()
        if 'baje' in lowered:
            parts = lowered.split('baje')[0].strip().split()
            if parts:
                num = ''.join(ch for ch in parts[-1] if ch.isdigit())
                if num.isdigit():
                    hour = int(num) % 24
                    t = f"{hour:02d}:00"
        # Fallback: HH:MM in text
        if not t:
            import re
            m = re.search(r"\b(\d{1,2}):(\d{2})\b", text)
            if m:
                hour = int(m.group(1)) % 24
                minute = int(m.group(2)) % 60
                t = f"{hour:02d}:{minute:02d}"
        return t or ""
    except Exception:
        return ""

# In-memory store (session-based fallback so commands work without DB)
# Daily rotating motivation line
def get_daily_motivation() -> str:
    quotes = [
        "छोटे-छोटे कदम ही बड़ी मंज़िल तक ले जाते हैं।",
        "अनुशासन ही सफलता की चाबी है।",
        "आज मेहनत, कल राहत।",
        "संगत से रंगत—अच्छी आदतें अपनाइए।",
        "अपने समय का आदर करें, समय आपको आदर देगा।",
        "लगातार प्रयास ही असली प्रतिभा है।",
        "ठान लिया तो कर दिखाया।",
        "धैर्य रखिए, परिणाम निश्चित है।",
        "हर दिन 1% बेहतर बनिए।",
        "सुबह की शुरुआत अनुशासन से करें।",
        "जहां फोकस, वहीं प्रगति।",
        "काम बोल���ा है, बहाने नहीं।",
        "Consistency > Intensity.",
        "लक्ष्य साफ, कोशिश बेहतरीन।",
        "आज का एक अच्छा काम, सप्ताह का परिणाम बदल देता है।",
    ]
    idx = int(datetime.now().strftime('%Y%m%d')) % len(quotes)
    return quotes[idx]

class MemoryStore:
    def __init__(self):
        self.users: Dict[int, Dict[str, Any]] = defaultdict(lambda: {
            'tasks': [],  # {text, date, time, completed}
            'habits': [], # {name, created_at, streak, last_done}
            'expenses': [], # {amount, category, description, date}
            'reminder_on': True,
            'xp': 0,
            'level': 1,
            'discipline_score': 0,
            'budget': None,
        })

    def today_str(self) -> str:
        return datetime.now().strftime('%Y-%m-%d')

    def tomorrow_str(self) -> str:
        return (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

store = MemoryStore()

# Category detection mapping for Hindi keywords
CATEGORY_MAP = {
    'petrol': 'Fuel', 'fuel': 'Fuel',
    'sabzi': 'Grocery', 'vegetable': 'Grocery', 'grocery': 'Grocery',
    'kiraya': 'Rent', 'rent': 'Rent',
    'chai': 'Food', 'hotel': 'Food', 'food': 'Food',
    'dawa': 'Medical', 'medicine': 'Medical', 'medical': 'Medical',
    'recharge': 'Mobile', 'mobile': 'Mobile'
}

class RadheyAIBot:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        if not self.bot_token:
            logger.error('TELEGRAM_BOT_TOKEN not set. Bot will not start without a valid token.')
            raise ValueError('TELEGRAM_BOT_TOKEN environment variable is required')
        try:
            self.updater = Updater(token=self.bot_token, use_context=True)
            self.dispatcher = self.updater.dispatcher
            self.setup_handlers()
        except Exception as e:
            logger.error(f'Failed to initialize Telegram Bot: {e}')
            raise

    # ============== Handler setup ==============
    def setup_handlers(self):
        # Task management
        self.dispatcher.add_handler(CommandHandler('addtask', self.addtask))
        self.dispatcher.add_handler(CommandHandler('today', self.today))
        self.dispatcher.add_handler(CommandHandler('tomorrow', self.tomorrow))
        self.dispatcher.add_handler(CommandHandler('alltasks', self.alltasks))
        self.dispatcher.add_handler(CommandHandler('reschedule', self.reschedule))
        self.dispatcher.add_handler(CommandHandler('deletetask', self.deletetask))
        self.dispatcher.add_handler(CommandHandler('clear', self.clear))

        # Habit
        self.dispatcher.add_handler(CommandHandler('addhabit', self.addhabit))
        self.dispatcher.add_handler(CommandHandler('habits', self.habits))
        self.dispatcher.add_handler(CommandHandler('done', self.done))
        self.dispatcher.add_handler(CommandHandler('streak', self.streak))
        self.dispatcher.add_handler(CommandHandler('report', self.habit_report))

        # Expense
        self.dispatcher.add_handler(CommandHandler('addexpense', self.addexpense))
        self.dispatcher.add_handler(CommandHandler('todayexpense', self.todayexpense))
        self.dispatcher.add_handler(CommandHandler('weekexpense', self.weekexpense))
        self.dispatcher.add_handler(CommandHandler('monthexpense', self.monthexpense))
        self.dispatcher.add_handler(CommandHandler('weekpdf', self.weekpdf))
        self.dispatcher.add_handler(CommandHandler('budget', self.budget))
        self.dispatcher.add_handler(CommandHandler('topcategory', self.topcategory))
        self.dispatcher.add_handler(CommandHandler('exportcsv', self.exportcsv))
        self.dispatcher.add_handler(CommandHandler('clearexpense', self.clearexpense))

        # Daily
        self.dispatcher.add_handler(CommandHandler('morning', self.morning))

        # Reminder
        self.dispatcher.add_handler(CommandHandler('reminder', self.reminder))
        self.dispatcher.add_handler(CommandHandler('voice', self.voice))

        # Voice and OCR
        self.dispatcher.add_handler(CommandHandler('talk', self.talk))
        self.dispatcher.add_handler(CommandHandler('scan', self.scan))

        # Analytics + Gamification
        self.dispatcher.add_handler(CommandHandler('stats', self.stats))
        self.dispatcher.add_handler(CommandHandler('xp', self.xp))
        self.dispatcher.add_handler(CommandHandler('level', self.level))
        self.dispatcher.add_handler(CommandHandler('challenge', self.challenge))

        # Calendar + Dashboard
        self.dispatcher.add_handler(CommandHandler('gcal', self.gcal))
        self.dispatcher.add_handler(CommandHandler('dashboard', self.dashboard))

        # Night planner conversation
        night_conv = ConversationHandler(
            entry_points=[CommandHandler('night', self.night)],
            states={
                WAITING_FOR_NIGHT_PLAN: [MessageHandler(Filters.text & ~Filters.command, self.night_collect)],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
        )
        self.dispatcher.add_handler(night_conv)

        # Defaults
        self.dispatcher.add_handler(CommandHandler('help', self.help))
        self.dispatcher.add_handler(CommandHandler('start', self.start))
        self.dispatcher.add_handler(CommandHandler('cancel', self.cancel))

        # Generic handlers
        self.dispatcher.add_handler(MessageHandler(Filters.voice, self.handle_voice_message))
        self.dispatcher.add_handler(MessageHandler(Filters.photo, self.handle_photo_message))
        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.handle_text_message))

        # Error handler
        self.dispatcher.add_error_handler(self.error)

    # ============== Utilities ==============
    def _get_user(self, user_id: int) -> Dict[str, Any]:
        return store.users[user_id]

    # ============== General ==============
    def start(self, update: Update, context: CallbackContext):
        moti = get_daily_motivation()
        msg = (
            "💠 <b>स्वागत है, Radhey ji!</b> 💠\n"
            "<i>Personal AI Life Commander आपकी सेवा में</i>\n\n"
            "🔥 <b>आज की प्रेरणा:</b> " + moti + "\n\n"
            "मैं आपकी मदद करूँगा: \n"
            "• Task, Habit, Expense manage करने में\n"
            "• Reminder (1 घंटा पहले + Exact Time) सेट करने में\n"
            "• Morning/Night planning, OCR, Voice में\n\n"
            "➡️ मदद के लिए <b>/help</b> टाइप करें\n\n"
            "— <i>Bot Made By</i> <b>Radhey</b> ✨"
        )
        update.message.reply_text(msg, parse_mode=ParseMode.HTML, reply_markup=ForceReply(selective=True))

    def help(self, update: Update, context: CallbackContext):
        help_text = (
            "📘 <b>HELP MENU — Radhey AI Life Commander</b>\n\n"
            "📅 <b>Task Management</b>\n"
            "• /addtask 7 baje gym — नया task add\n"
            "• /today — आज के task\n"
            "• /tomorrow — कल के task\n"
            "• /alltasks — सारे pending task\n"
            "• /reschedule 9:00 — समय बदलें (latest task)\n"
            "• /deletetask [n] — task delete (बिना n के आख़िरी)\n"
            "• /clear — सारे task clear\n\n"
            "💪 <b>Habits</b>\n"
            "• /addhabit pani peena — नई habit add\n"
            "• /habits — habits की list\n"
            "• /done [n] — habit complete + streak\n"
            "• /streak — streak summary\n"
            "• /report — habit report\n\n"
            "💰 <b>Expenses</b>\n"
            "• /addexpense 120 chai — amount + category auto-detect\n"
            "• /todayexpense — आज का खर्चा\n"
            "• /weekexpense — पिछले 7 दिन\n"
            "• /monthexpense — इस महीने का कुल\n"
            "• /budget 15000 — monthly budget set\n"
            "• /topcategory — सबसे ज़्यादा खर्च वाली categories\n"
            "• /exportcsv — CSV export (stub)\n"
            "• /clearexpense — सब expenses clear\n\n"
            "🌅 <b>Daily Routines</b>\n"
            "• /morning — Good Morning + tasks + habits + motivation\n"
            "• /night — कल की planning (time के साथ)\n\n"
            "⏰ <b>Reminders & Voice</b>\n"
            "• /reminder on|off — reminders toggle\n"
            "• /voice on|off — voice replies toggle (stub)\n\n"
            "🎙 <b>Voice & OCR</b>\n"
            "• /talk — voice mode (stub)\n"
            "• /scan — Hindi OCR (stub)\n\n"
            "📈 <b>Analytics & Gamification</b>\n"
            "• /stats — productivity summary\n"
            "• /xp — XP points\n"
            "• /level — current level\n"
            "• /challenge — daily challenge\n\n"
            "📅 <b>Google & Dashboard</b>\n"
            "• /gcal connect|sync|off — calendar (stub)\n"
            "• /dashboard — web dashboard (stub)\n\n"
            "— <i>Bot Made By</i> <b>Radhey</b> ✨"
        )
        update.message.reply_text(help_text, parse_mode=ParseMode.HTML)

    def cancel(self, update: Update, context: CallbackContext):
        update.message.reply_text("Operation cancel kar diya gaya, Radhey ji.")
        return ConversationHandler.END

    def error(self, update: Update, context: CallbackContext):
        logger.warning(f"Update {update} caused error {context.error}")

    # ============== Task Management ==============
    def addtask(self, update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        user = self._get_user(user_id)
        text = ' '.join(context.args) if context.args else (update.message.text.replace('/addtask', '').strip())
        if not text:
            update.message.reply_text("Radhey ji, kripya task bataye (jaise: /addtask 7 baje gym jana)")
            return
        time_str = parse_hindi_time_to_24h(text)
        task_text = text
        today = self._today_str()
        user['tasks'].append({'text': task_text, 'date': today, 'time': time_str, 'completed': False})
        update.message.reply_text(
            f"Ji Radhey ji, task add ho gaya: '{task_text}'.\n"
            + ("⏰ Reminder 1 ghanta pehle aur exact time pe set kar diya hai." if time_str else "⏰ Time clear nahi mila, reminder bina time ke set hua.")
        )

    def today(self, update: Update, context: CallbackContext):
        user = self._get_user(update.effective_user.id)
        today = self._today_str()
        todays = [t for t in user['tasks'] if t['date'] == today and not t['completed']]
        if not todays:
            update.message.reply_text("Radhey ji, aaj koi pending task nahi hai.")
            return
        lines = [f"{i+1}. {t['text']}" + (f" ({t['time']})" if t['time'] else '') for i, t in enumerate(todays)]
        update.message.reply_text("Aaj ke task:\n" + '\n'.join(lines))

    def tomorrow(self, update: Update, context: CallbackContext):
        user = self._get_user(update.effective_user.id)
        tomorrow = self._tomorrow_str()
        tasks = [t for t in user['tasks'] if t['date'] == tomorrow and not t['completed']]
        if not tasks:
            update.message.reply_text("Radhey ji, kal ke liye koi task set nahi hai.")
            return
        lines = [f"{i+1}. {t['text']}" + (f" ({t['time']})" if t['time'] else '') for i, t in enumerate(tasks)]
        update.message.reply_text("Kal ke task:\n" + '\n'.join(lines))

    def alltasks(self, update: Update, context: CallbackContext):
        user = self._get_user(update.effective_user.id)
        pending = [t for t in user['tasks'] if not t['completed']]
        if not pending:
            update.message.reply_text("Radhey ji, koi pending task nahi hai.")
            return
        lines = [f"{i+1}. {t['text']} - {t['date']}" + (f" {t['time']}" if t['time'] else '') for i, t in enumerate(pending)]
        update.message.reply_text("Sab pending task:\n" + '\n'.join(lines))

    def reschedule(self, update: Update, context: CallbackContext):
        user = self._get_user(update.effective_user.id)
        if not user['tasks']:
            update.message.reply_text("Radhey ji, reschedule karne ke liye koi task nahi mila.")
            return
        args = ' '.join(context.args) if context.args else ''
        time_str = parse_hindi_time_to_24h(args)
        if not time_str:
            update.message.reply_text("Radhey ji, kripya time clear bataye (jaise 7:00 ya 7 baje)")
            return
        # Reschedule latest pending task
        for t in user['tasks']:
            if not t['completed']:
                t['time'] = time_str
                t['date'] = self._today_str()
                break
        update.message.reply_text(f"Reschedule ho gaya. ⏰ Naya time: {time_str}")

    def deletetask(self, update: Update, context: CallbackContext):
        user = self._get_user(update.effective_user.id)
        if not user['tasks']:
            update.message.reply_text("Radhey ji, delete karne ke liye koi task nahi mila.")
            return
        idx = None
        if context.args and context.args[0].isdigit():
            idx = int(context.args[0]) - 1
        if idx is not None and 0 <= idx < len(user['tasks']):
            removed = user['tasks'].pop(idx)
        else:
            removed = user['tasks'].pop()
        update.message.reply_text(f"Delete ho gaya: {removed['text']}")

    def clear(self, update: Update, context: CallbackContext):
        user = self._get_user(update.effective_user.id)
        user['tasks'].clear()
        update.message.reply_text("Radhey ji, sab tasks clear kar diye gaye.")

    # ============== Habits ==============
    def addhabit(self, update: Update, context: CallbackContext):
        user = self._get_user(update.effective_user.id)
        name = ' '.join(context.args) if context.args else update.message.text.replace('/addhabit', '').strip()
        if not name:
            update.message.reply_text("Radhey ji, habit ka naam bataye (jaise: /addhabit subah walk)")
            return
        user['habits'].append({'name': name, 'created_at': self._today_str(), 'streak': 0, 'last_done': None})
        update.message.reply_text(f"Habit add ho gayi: {name}")

    def habits(self, update: Update, context: CallbackContext):
        user = self._get_user(update.effective_user.id)
        if not user['habits']:
            update.message.reply_text("Radhey ji, koi habit add nahi hai.")
            return
        lines = [f"{i+1}. {h['name']} (streak: {h['streak']})" for i, h in enumerate(user['habits'])]
        update.message.reply_text("Aapki habits:\n" + '\n'.join(lines))

    def done(self, update: Update, context: CallbackContext):
        user = self._get_user(update.effective_user.id)
        if not user['habits']:
            update.message.reply_text("Radhey ji, pehle /addhabit se habit add karein.")
            return
        idx = 0
        if context.args and context.args[0].isdigit():
            idx = max(0, min(len(user['habits']) - 1, int(context.args[0]) - 1))
        h = user['habits'][idx]
        today = self._today_str()
        if h['last_done'] == today:
            update.message.reply_text(f"'{h['name']}' aaj pehle hi complete ho chuki hai.")
            return
        # Increment streak if consecutive day else reset to 1
        if h['last_done']:
            last = datetime.strptime(h['last_done'], '%Y-%m-%d')
            if (datetime.now().date() - last.date()).days == 1:
                h['streak'] += 1
            elif (datetime.now().date() - last.date()).days == 0:
                h['streak'] = h['streak']  # same day, ignore
            else:
                h['streak'] = 1
        else:
            h['streak'] = 1
        h['last_done'] = today
        update.message.reply_text(f"Shabash Radhey ji! '{h['name']}' complete. Streak: {h['streak']}")

    def streak(self, update: Update, context: CallbackContext):
        user = self._get_user(update.effective_user.id)
        if not user['habits']:
            update.message.reply_text("Radhey ji, koi habit nahi mili.")
            return
        lines = [f"{i+1}. {h['name']} → Streak: {h['streak']}" for i, h in enumerate(user['habits'])]
        update.message.reply_text('\n'.join(lines))

    def habit_report(self, update: Update, context: CallbackContext):
        user = self._get_user(update.effective_user.id)
        total = len(user['habits'])
        best = max((h['streak'] for h in user['habits']), default=0)
        update.message.reply_text(f"Habit report: Total {total}, Best streak {best}")

    # ============== Expense ==============
    def _detect_category(self, text: str) -> str:
        t = text.lower()
        for k, v in CATEGORY_MAP.items():
            if k in t:
                return v
        return 'Other'

    def addexpense(self, update: Update, context: CallbackContext):
        user = self._get_user(update.effective_user.id)
        raw = ' '.join(context.args) if context.args else update.message.text.replace('/addexpense', '').strip()
        if not raw:
            update.message.reply_text("Radhey ji, kripya expense bataye (jaise: /addexpense 120 chai)")
            return
        import re
        m = re.search(r"(\d+[\.]?\d*)", raw)
        if not m:
            update.message.reply_text("Kitne rupaye add karne hain?")
            return
        amount = float(m.group(1))
        desc = raw
        cat = self._detect_category(raw)
        user['expenses'].append({'amount': amount, 'category': cat, 'description': desc, 'date': self._today_str()})
        update.message.reply_text(f"Add ho gaya: ₹{amount:.2f} - {cat}")

    def todayexpense(self, update: Update, context: CallbackContext):
        user = self._get_user(update.effective_user.id)
        today = self._today_str()
        exps = [e for e in user['expenses'] if e['date'] == today]
        if not exps:
            update.message.reply_text("Radhey ji, aaj koi expense nahi hai.")
            return
        total = sum(e['amount'] for e in exps)
        lines = [f"{i+1}. {e['category']}: ₹{e['amount']:.2f}" + (f" ({e['description']})" if e['description'] else '') for i, e in enumerate(exps)]
        update.message.reply_text("Aaj ke expenses:\n" + '\n'.join(lines) + f"\n\nTotal: ₹{total:.2f}")

    def weekexpense(self, update: Update, context: CallbackContext):
        user = self._get_user(update.effective_user.id)
        today = datetime.now().date()
        start = (today - timedelta(days=6)).strftime('%Y-%m-%d')
        end = today.strftime('%Y-%m-%d')
        exps = [e for e in user['expenses'] if start <= e['date'] <= end]
        if not exps:
            update.message.reply_text("Radhey ji, is hafte koi expense nahi hai.")
            return
        total = sum(e['amount'] for e in exps)
        lines = [f"{i+1}. {e['date']} {e['category']}: ₹{e['amount']:.2f}" for i, e in enumerate(exps)]
        update.message.reply_text("Is hafte ke expenses:\n" + '\n'.join(lines) + f"\n\nTotal: ₹{total:.2f}")

    def monthexpense(self, update: Update, context: CallbackContext):
        user = self._get_user(update.effective_user.id)
        now = datetime.now()
        first = datetime(now.year, now.month, 1).strftime('%Y-%m-%d')
        if now.month == 12:
            next_first = datetime(now.year + 1, 1, 1)
        else:
            next_first = datetime(now.year, now.month + 1, 1)
        last = (next_first - timedelta(days=1)).strftime('%Y-%m-%d')
        exps = [e for e in user['expenses'] if first <= e['date'] <= last]
        if not exps:
            update.message.reply_text("Radhey ji, is mahine koi expense nahi hai.")
            return
        total = sum(e['amount'] for e in exps)
        update.message.reply_text(f"Is mahine ka total kharcha: ₹{total:.2f}")

    def weekpdf(self, update: Update, context: CallbackContext):
        update.message.reply_text("Radhey ji, weekly PDF generate karne ka kaam scheduled hai (stub).")

    def budget(self, update: Update, context: CallbackContext):
        user = self._get_user(update.effective_user.id)
        if context.args and context.args[0].replace('.', '', 1).isdigit():
            user['budget'] = float(context.args[0])
            update.message.reply_text(f"Budget set ho gaya: ₹{user['budget']:.2f}")
        else:
            update.message.reply_text("Radhey ji, kripya monthly budget bataye (jaise: /budget 15000)")

    def topcategory(self, update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        expenses = storage.get_user_expenses(user_id)
        if not expenses:
            update.message.reply_text("Radhey ji, koi expense nahi hai.")
            return
        agg: Dict[str, float] = defaultdict(float)
        for e in expenses:
            agg[e['category']] += e['amount']
        sorted_items = sorted(agg.items(), key=lambda x: x[1], reverse=True)
        lines = [f"{i+1}. {k}: ₹{v:.2f}" for i, (k, v) in enumerate(sorted_items)]
        update.message.reply_text("Top categories:\n" + '\n'.join(lines))

    def exportcsv(self, update: Update, context: CallbackContext):
        update.message.reply_text("CSV export ready soon (stub).")

    def clearexpense(self, update: Update, context: CallbackContext):
        update.message.reply_text("Radhey ji, sabhi expense clear kar diye gaye.")

    # ============== Morning/Night ==============
    def morning(self, update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        today = self._today_str()
        todays = storage.get_today_tasks(user_id, today)
        todays = [t for t in todays if not t['completed']]
        habits = storage.get_user_habits(user_id)
        msg = [
            "🌅 Good Morning Radhey ji!",
            "✨ Motivation: Roz chhote kadam, bade parinaam!",
            "\n🎯 Aaj ke task:",
        ]
        if todays:
            msg += [f"{i+1}. {t['text']}" + (f" ({t['time']})" if t['time'] else '') for i, t in enumerate(todays)]
        else:
            msg.append("- Koi task nahi. /addtask se add karein.")
        msg.append("\n💪 Habits:")
        if habits:
            msg += [f"{i+1}. {h['name']} (streak {h['streak']})" for i, h in enumerate(habits)]
        else:
            msg.append("- Koi habit nahi. /addhabit se add karein.")
        update.message.reply_text('\n'.join(msg))

    def night(self, update: Update, context: CallbackContext):
        update.message.reply_text("Radhey ji, kal kya karna hai? Time ke saath likhiye. (jaise: 6 baje uthna, 7 baje gym)")
        return WAITING_FOR_NIGHT_PLAN

    def night_collect(self, update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        raw = update.message.text.strip()
        if not raw:
            update.message.reply_text("Kripya kal ke tasks likhiye.")
            return WAITING_FOR_NIGHT_PLAN
        tomorrow = self._tomorrow_str()
        # Split by newlines or commas
        parts = [p.strip() for p in raw.replace('\n', ',').split(',') if p.strip()]
        for p in parts:
            t = parse_hindi_time_to_24h(p)
            storage.add_task(user_id, p, tomorrow, t, completed=False)
        update.message.reply_text("Kal ka plan store ho gaya hai. Subah /morning me yaad dilaunga.")
        return ConversationHandler.END

    # ============== Reminders ==============
    def reminder(self, update: Update, context: CallbackContext):
        user = self._get_user(update.effective_user.id)
        if context.args:
            mode = context.args[0].lower()
            if mode in ['on', 'enable']:
                user['reminder_on'] = True
                update.message.reply_text("Radhey ji, reminders enable ho gaye hain.")
            elif mode in ['off', 'disable']:
                user['reminder_on'] = False
                update.message.reply_text("Radhey ji, reminders disable ho gaye hain.")
            else:
                update.message.reply_text("Radhey ji, 'on' ya 'off' use kare.")
        else:
            update.message.reply_text("Radhey ji, 'reminder on' ya 'reminder off' use kare.")

    def voice(self, update: Update, context: CallbackContext):
        user = self._get_user(update.effective_user.id)
        if context.args:
            mode = context.args[0].lower()
            if mode in ['on', 'enable']:
                user.setdefault('voice_on', True)
                user['voice_on'] = True
                update.message.reply_text("Radhey ji, voice replies enable ho gaye hain (stub).")
            elif mode in ['off', 'disable']:
                user.setdefault('voice_on', False)
                user['voice_on'] = False
                update.message.reply_text("Radhey ji, voice replies disable ho gaye hain.")
            else:
                update.message.reply_text("Radhey ji, 'on' ya 'off' use kare.")
        else:
            update.message.reply_text("Radhey ji, 'voice on' ya 'voice off' use kare.")

    # ============== Voice & OCR ==============
    def talk(self, update: Update, context: CallbackContext):
        update.message.reply_text("Radhey ji, voice mode active. Aap apna message voice me bhej sakte hain.")

    def scan(self, update: Update, context: CallbackContext):
        update.message.reply_text("Radhey ji, Hindi text wali image bheje. Main OCR karke text bhejunga.")

    # ============== Analytics & Gamification ==============
    def stats(self, update: Update, context: CallbackContext):
        user = self._get_user(update.effective_user.id)
        total_tasks = len(user['tasks'])
        completed = sum(1 for t in user['tasks'] if t['completed'])
        habits = len(user['habits'])
        total_expense = sum(e['amount'] for e in user['expenses'])
        msg = (
            f"📈 Productivity: {int((completed/total_tasks)*100) if total_tasks else 0}%\n"
            f"✅ Completed tasks: {completed}\n"
            f"💪 Habit count: {habits}\n"
            f"💰 Total spending: ₹{total_expense:.2f}"
        )
        update.message.reply_text(msg)

    def xp(self, update: Update, context: CallbackContext):
        user = self._get_user(update.effective_user.id)
        update.message.reply_text(f"XP: {user['xp']}")

    def level(self, update: Update, context: CallbackContext):
        user = self._get_user(update.effective_user.id)
        update.message.reply_text(f"Level: {user['level']}")

    def challenge(self, update: Update, context: CallbackContext):
        update.message.reply_text("Aaj ka challenge: 3 task complete kijiye!")

    # ============== Google Calendar & Dashboard ==============
    def gcal(self, update: Update, context: CallbackContext):
        if context.args:
            cmd = context.args[0].lower()
            if cmd == 'connect':
                update.message.reply_text("Google Calendar connect (stub).")
            elif cmd == 'sync':
                update.message.reply_text("Google Calendar sync (stub).")
            elif cmd == 'off':
                update.message.reply_text("Google Calendar disconnect (stub).")
            else:
                update.message.reply_text("Radhey ji, 'connect', 'sync', ya 'off' use kare.")
        else:
            update.message.reply_text("Radhey ji, 'gcal connect' ya 'gcal sync' use kare.")

    def dashboard(self, update: Update, context: CallbackContext):
        update.message.reply_text("Dashboard: http://localhost:8000/dashboard (stub)")

    # ============== Media Merging ==============
    def merge_start(self, update: Update, context: CallbackContext):
        """Start media merging process"""
        user_id = update.effective_user.id
        user = self._get_user(user_id)
        
        # Initialize merge session
        user.setdefault('merge_session', {
            'files': [],
            'media_info': [],
            'quality': 'medium',
            'output_filename': 'merged_file',
            'state': 'waiting_for_media'
        })
        
        update.message.reply_text(
            "Radhey ji, please send media files (videos or PDFs) that you want to merge.\n"
            "You can send multiple files one by one. When done, type 'done' to continue."
        )
        
        return WAITING_FOR_MEDIA
    
    def merge_receive_media(self, update: Update, context: CallbackContext):
        """Receive media files from user"""
        user_id = update.effective_user.id
        user = self._get_user(user_id)
        
        try:
            # Get file information
            file = update.message.document
            file_name = file.file_name
            file_id = file.file_id
            
            # Download the file
            new_file = context.bot.get_file(file_id)
            file_path = new_file.download()
            
            # Get media information
            from core.media_merger import MediaMerger
            merger = MediaMerger()
            
            if merger.is_video_file(file_name) or merger.is_pdf_file(file_name):
                user['merge_session']['files'].append(file_path)
                
                # Get media info
                if merger.is_video_file(file_name):
                    info = merger.get_video_info(file_path)
                else:
                    info = merger.get_pdf_info(file_path)
                    
                user['merge_session']['media_info'].append(info)
                
                update.message.reply_text(
                    f"✅ File received: {file_name}\n"
                    f"Type 'done' to continue to next step."
                )
            else:
                update.message.reply_text(
                    "❌ Invalid file format. Please send videos (MP4, AVI, MOV, MKV, FLV, WMV) or PDFs only."
                )
                
        except Exception as e:
            logger.error(f"Error receiving media file: {e}")
            update.message.reply_text("❌ Error receiving file. Please try again.")
            
        return WAITING_FOR_MEDIA
    
    def merge_handle_response(self, update: Update, context: CallbackContext):
        """Handle text responses during merging process"""
        user_id = update.effective_user.id
        user = self._get_user(user_id)
        response = update.message.text.strip().lower()
        
        if response == 'done':
            if not user['merge_session']['files']:
                update.message.reply_text("❌ No files received. Please send media files first.")
                return WAITING_FOR_MEDIA
                
            # Show media info
            self._show_merge_info(update, user['merge_session'])
            update.message.reply_text(
                "\n📋 If you want to merge these files, type '1' to proceed. Otherwise, type 'cancel'."
            )
            
            user['merge_session']['state'] = 'waiting_for_confirmation'
            return WAITING_FOR_CONFIRMATION
            
        elif response == 'cancel':
            return self.cancel(update, context)
        else:
            update.message.reply_text(
                "Radhey ji, please send media files or type 'done' when finished."
            )
            return WAITING_FOR_MEDIA
            
    def merge_confirm_merge(self, update: Update, context: CallbackContext):
        """Confirm merging process"""
        user_id = update.effective_user.id
        user = self._get_user(user_id)
        response = update.message.text.strip()
        
        if response == '1':
            # Ask for quality
            update.message.reply_text(
                "🔍 Please select quality:\n"
                "1. High (Best quality, larger file size)\n"
                "2. Medium (Good quality, balanced file size)\n"
                "3. Low (Fast processing, smaller file size)\n"
                "\nType the number corresponding to your choice."
            )
            
            user['merge_session']['state'] = 'waiting_for_quality'
            return WAITING_FOR_QUALITY
        elif response == 'cancel':
            return self.cancel(update, context)
        else:
            update.message.reply_text(
                "❌ Invalid response. Please type '1' to proceed or 'cancel' to cancel."
            )
            return WAITING_FOR_CONFIRMATION
            
    def merge_select_quality(self, update: Update, context: CallbackContext):
        """Select output quality"""
        user_id = update.effective_user.id
        user = self._get_user(user_id)
        response = update.message.text.strip()
        
        quality_map = {
            '1': 'high',
            '2': 'medium',
            '3': 'low'
        }
        
        if response in quality_map:
            user['merge_session']['quality'] = quality_map[response]
            
            # Ask for output filename
            update.message.reply_text(
                "📄 Please enter a name for the merged file (without extension):"
            )
            
            user['merge_session']['state'] = 'waiting_for_filename'
            return WAITING_FOR_FILENAME
        elif response == 'cancel':
            return self.cancel(update, context)
        else:
            update.message.reply_text(
                "❌ Invalid choice. Please select 1, 2, or 3 for quality."
            )
            return WAITING_FOR_QUALITY
            
    def merge_set_filename(self, update: Update, context: CallbackContext):
        """Set output filename and perform merge"""
        user_id = update.effective_user.id
        user = self._get_user(user_id)
        response = update.message.text.strip()
        
        if response and response.lower() != 'cancel':
            user['merge_session']['output_filename'] = response
            
            # Perform merge
            update.message.reply_text(
                "🚀 Merging files... Please wait, this may take some time."
            )
            
            try:
                from core.media_merger import MediaMerger
                merger = MediaMerger()
                
                output_path, errors = merger.merge_media(
                    user['merge_session']['files'],
                    user['merge_session']['output_filename'],
                    user['merge_session']['quality']
                )
                
                if output_path:
                    # Send merged file
                    with open(output_path, 'rb') as f:
                        update.message.reply_document(
                            document=f,
                            filename=os.path.basename(output_path)
                        )
                        
                    update.message.reply_text("✅ Files merged successfully!")
                else:
                    update.message.reply_text(
                        "❌ Error during merge:\n" + '\n'.join(errors)
                    )
                    
            except Exception as e:
                logger.error(f"Merge operation failed: {e}")
                update.message.reply_text(
                    "❌ Merge operation failed. Please try again with different files."
                )
                
            # Clean up
            self._cleanup_merge_session(user)
            return ConversationHandler.END
            
        elif response.lower() == 'cancel':
            return self.cancel(update, context)
        else:
            update.message.reply_text(
                "❌ Invalid filename. Please enter a valid name or type 'cancel'."
            )
            return WAITING_FOR_FILENAME
            
    def _show_merge_info(self, update: Update, merge_session):
        """Show media files information"""
        media_info = merge_session['media_info']
        
        msg = "📊 Files to merge:\n"
        for info in media_info:
            msg += f"\n🎥 {info['filename']}"
            if info['type'] == 'video':
                msg += f" ({info['duration_str']}, {info['size_mb']} MB)"
            else:
                msg += f" ({info['page_count']} pages, {info['size_mb']} MB)"
                
        # Calculate total info
        from core.media_merger import MediaMerger
        merger = MediaMerger()
        
        total_size = merger.calculate_total_size(media_info)
        count_info = merger.count_files_by_type(media_info)
        
        msg += f"\n\n📈 Total: {count_info['total']} file(s), {total_size:.2f} MB"
        
        if count_info['video'] > 0:
            total_duration = merger.calculate_total_duration(media_info)
            msg += f"\n⏱️ Total duration: {total_duration}"
            
        update.message.reply_text(msg)
        
    def _cleanup_merge_session(self, user):
        """Clean up merge session resources"""
        if 'merge_session' in user:
            # Clean up downloaded files
            for file_path in user['merge_session'].get('files', []):
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    logger.error(f"Error cleaning up file: {e}")
                    
            # Remove merge session
            del user['merge_session']
            
    # ============== Generic message handlers ==============
    def handle_text_message(self, update: Update, context: CallbackContext):
        txt = update.message.text.strip().lower()
        if 'yaad dilana' in txt or 'remind' in txt:
            # Quick natural language task add
            time_str = parse_hindi_time_to_24h(txt)
            user = self._get_user(update.effective_user.id)
            user['tasks'].append({'text': txt, 'date': self._today_str(), 'time': time_str, 'completed': False})
            update.message.reply_text("Ji Radhey ji, reminder set kar diya hai.")
        else:
            update.message.reply_text("Radhey ji, kripya valid command use kare.")

    def handle_voice_message(self, update: Update, context: CallbackContext):
        update.message.reply_text("Voice message mila. Speech-to-text (stub) chal raha hai.")

    def handle_photo_message(self, update: Update, context: CallbackContext):
        update.message.reply_text("Image mili. Hindi OCR (stub) process ho raha hai.")

    # ============== Runner ==============
    def run(self):
        logger.info('Starting RADHEY AI LIFE COMMANDER...')
        self.updater.start_polling()
        logger.info('Bot is running!')
        self.updater.idle()


if __name__ == '__main__':
    bot = RadheyAIBot()
    bot.run()
