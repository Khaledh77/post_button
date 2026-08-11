
import asyncio, os, json
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from pathlib import Path

import aiohttp
import aiosqlite
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup,
    InputMediaPhoto, InputMediaVideo, BotCommand, ReplyKeyboardMarkup, KeyboardButton
)

load_dotenv(Path(__file__).with_name(".env"))

BOT_TOKEN = os.getenv("BOT_TOKEN","").strip()
ADMIN_ID = int(os.getenv("ADMIN_ID","6435057666"))
BOT_USERNAME = os.getenv("BOT_USERNAME","Post_button_online_bot")
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME","Tnatc").lstrip("@")
PREMIUM_PRICE = float(os.getenv("PREMIUM_MONTH_PRICE_USD","1"))
MIN_TOPUP = float(os.getenv("MIN_TOPUP_USD","2"))
BEP20_WALLET = os.getenv("BEP20_WALLET","").strip()
TRC20_WALLET = os.getenv("TRC20_WALLET","").strip()
ETHERSCAN_KEY = os.getenv("ETHERSCAN_API_KEY","").strip()
TRONGRID_KEY = os.getenv("TRONGRID_API_KEY","").strip()
BEP20_USDT = os.getenv("BEP20_USDT_CONTRACT","").strip()
TRC20_USDT = os.getenv("TRC20_USDT_CONTRACT","").strip()
DB_PATH = os.getenv("DATABASE_PATH","data/post_button.sqlite3")

LANGS = {
    "uz":"🇺🇿 O‘zbekcha", "tr":"🇹🇷 Türkçe", "ru":"🇷🇺 Русский",
    "ar":"🇸🇦 العربية", "en":"🇬🇧 English"
}

T = {
"uz":{
"welcome":"👋 Post Button 🔘 ga xush kelibsiz!",
"choose":"🌐 Tilni tanlang:",
"join":"🔐 Botdan foydalanish uchun quyidagilarga a'zo bo'ling:",
"check":"✅ Tekshirish","new":"📢 Yangi post","saved_posts":"🗂 Saqlangan postlar","dests":"📡 Kanallar va guruhlar",
"premium":"⭐ Premium","balance":"💰 Balans","support":"💬 Support","admin":"👑 Admin panel",
"media":"🖼 Rasm yoki video yuboring. O‘tkazib yuborish uchun /skip",
"text":"📝 Post matnini yuboring. Matn bo‘lmasa /skip",
"ready":"✅ Post tayyor. Amalni tanlang:","preview":"👁 Ko‘rib chiqish","buttons":"🔘 Knapkalar",
"publish":"📤 Yuborish","save_draft":"💾 Postni saqlash","cancel":"❌ Bekor qilish","addbtn":"➕ Knapka qo‘shish",
"clearbtn":"🗑 Barcha knapkalarni o‘chirish","btntext":"🔘 Knapka matnini yuboring:",
"btnurl":"🔗 Knapka URL manzilini yuboring:","btnrow":"↔️ Qaysi qatorga joylashsin? Raqam yuboring:",
"remove_attr":"⭐ Yozuvni olib tashlash","prem_info":"⭐ Premium — oyiga $1\n\n• Yozuvni olib tashlash\n• Yuborilgan postlarni tahrirlash\n• Cheksiz postlar",
"buy":"⭐ Premiumni yoqish","topup":"💳 Balansni to‘ldirish","need":"Balans yetarli emas. Avval kamida $2 to‘ldiring.",
"choose_net":"💰 Tarmoqni tanlang:","txid":"🧾 Muvaffaqiyatli to‘lovdan keyin TxID yuboring:",
"topup_ok":"✅ To‘lov tasdiqlandi. Balansingizga ${a:.2f} qo‘shildi.",
"txbad":"❌ Tranzaksiya topilmadi yoki talabga mos emas.","txused":"⚠️ Bu TxID allaqachon ishlatilgan.",
"no_dest":"📡 Avval kanal yoki guruh qo‘shing.","add_dest":"➕ Kanal/guruh qo‘shish",
"dest_hint":"@username yoki chat ID yuboring. Bot u yerda admin bo‘lishi kerak:",
"added":"✅ Qo‘shildi.","deleted":"🗑 O‘chirildi.","publish_choose":"📤 Qayerga yuborish?",
"published":"✅ Post yuborildi.","free_limit":"Bepul rejimda faqat 1 ta manzil tanlash mumkin.",
"attr":"Bu post Post Button 🔘 tomonidan tayyorlandi","users":"👥 Foydalanuvchilar",
"premusers":"⭐ Premium a'zolari","manual":"👑 O‘zim qo‘shganlar","required":"🔐 Majburiy a'zolik",
"chats":"📢 Kanal/guruhlar","attr_edit":"📝 Bepul foydalanuvchilar yozuvini yuboring:",
"support_edit":"💬 Support username yuboring (@siz ham bo‘ladi):","saved":"✅ Saqlandi.",
"manual_uid":"👤 Premium beriladigan User ID ni yuboring:","manual_done":"✅ Qo‘lda Premium berildi.",
"manual_off":"✅ Qo‘lda berilgan Premium bekor qilindi.","add_required":"➕ Majburiy kanal/guruh qo‘shish",
"required_hint":"@username yoki chat ID yuboring:","stats":"📊 Statistika","admin_only":"⛔ Admin uchun.",
"mydests":"📡 Mening kanallarim/guruhlarim","published_list":"📋 Yuborilgan postlar",
"edit":"✏️ Tahrirlash","edit_text":"📝 Yangi matnni yuboring:","edit_media":"🖼 Yangi rasm/video yuboring:",
"done":"✅ Tayyor","back":"⬅️ Orqaga","language":"🌐 Til"
},
"tr":{
"welcome":"👋 Post Button 🔘'a hoş geldiniz!","choose":"🌐 Dil seçin:","join":"🔐 Kullanmak için aşağıdakilere katılın:",
"check":"✅ Kontrol et","new":"📢 Yeni gönderi","saved_posts":"🗂 Kayıtlı gönderiler","dests":"📡 Kanallar ve gruplar","premium":"⭐ Premium","balance":"💰 Bakiye","support":"💬 Destek","admin":"👑 Yönetici paneli",
"media":"🖼 Fotoğraf veya video gönderin. Atlamak için /skip","text":"📝 Gönderi metnini gönderin. Metin yoksa /skip","ready":"✅ Gönderi hazır. İşlem seçin:",
"preview":"👁 Önizleme","buttons":"🔘 Butonlar","publish":"📤 Gönder","save_draft":"💾 Gönderiyi kaydet","cancel":"❌ İptal","addbtn":"➕ Buton ekle",
"clearbtn":"🗑 Tüm butonları sil","btntext":"🔘 Buton metnini gönderin:","btnurl":"🔗 Buton URL'sini gönderin:","btnrow":"↔️ Satır numarasını gönderin:",
"remove_attr":"⭐ İmzayı kaldır","prem_info":"⭐ Premium — ayda $1\n\n• İmzayı kaldır\n• Gönderileri düzenle\n• Sınırsız gönderi",
"buy":"⭐ Premium'u etkinleştir","topup":"💳 Bakiye yükle","need":"Bakiye yetersiz. Önce en az $2 yükleyin.",
"choose_net":"💰 Ağ seçin:","txid":"🧾 Başarılı ödeme sonrası TxID gönderin:","topup_ok":"✅ Ödeme onaylandı. ${a:.2f} bakiyeye eklendi.",
"txbad":"❌ İşlem bulunamadı veya şartlara uymuyor.","txused":"⚠️ Bu TxID daha önce kullanılmış.","no_dest":"📡 Önce kanal veya grup ekleyin.",
"add_dest":"➕ Kanal/grup ekle","dest_hint":"@username veya chat ID gönderin. Bot orada yönetici olmalı:","added":"✅ Eklendi.","deleted":"🗑 Silindi.",
"publish_choose":"📤 Nereye gönderilsin?","published":"✅ Gönderildi.","free_limit":"Ücretsiz modda sadece 1 hedef seçilebilir.","attr":"Bu gönderi Post Button 🔘 tarafından hazırlandı",
"users":"👥 Kullanıcılar","premusers":"⭐ Premium üyeler","manual":"👑 Manuel eklenenler","required":"🔐 Zorunlu üyelik","chats":"📢 Kanal/gruplar",
"attr_edit":"📝 Ücretsiz kullanıcı imzasını gönderin:","support_edit":"💬 Support username gönderin:","saved":"✅ Kaydedildi.",
"manual_uid":"👤 Premium verilecek User ID:","manual_done":"✅ Manuel Premium verildi.","manual_off":"✅ Manuel Premium iptal edildi.",
"add_required":"➕ Zorunlu kanal/grup ekle","required_hint":"@username veya chat ID gönderin:","stats":"📊 İstatistik","admin_only":"⛔ Sadece yönetici.",
"mydests":"📡 Kanallarım/gruplarım","published_list":"📋 Gönderilenler","edit":"✏️ Düzenle","edit_text":"📝 Yeni metni gönderin:","edit_media":"🖼 Yeni fotoğraf/video gönderin:","done":"✅ Tamam","back":"⬅️ Geri","language":"🌐 Dil"
},
"ru":{
"welcome":"👋 Добро пожаловать в Post Button 🔘!","choose":"🌐 Выберите язык:","join":"🔐 Чтобы пользоваться ботом, вступите в следующие:",
"check":"✅ Проверить","new":"📢 Новый пост","saved_posts":"🗂 Сохранённые посты","dests":"📡 Каналы и группы","premium":"⭐ Premium","balance":"💰 Баланс","support":"💬 Поддержка","admin":"👑 Админ-панель",
"media":"🖼 Отправьте фото или видео. Пропустить: /skip","text":"📝 Отправьте текст поста. Если текста нет: /skip","ready":"✅ Пост готов. Выберите действие:",
"preview":"👁 Предпросмотр","buttons":"🔘 Кнопки","publish":"📤 Отправить","save_draft":"💾 Сохранить пост","cancel":"❌ Отмена","addbtn":"➕ Добавить кнопку",
"clearbtn":"🗑 Удалить все кнопки","btntext":"🔘 Отправьте текст кнопки:","btnurl":"🔗 Отправьте URL кнопки:","btnrow":"↔️ Отправьте номер строки:",
"remove_attr":"⭐ Убрать подпись","prem_info":"⭐ Premium — $1 в месяц\n\n• Убрать подпись\n• Редактировать отправленные посты\n• Неограниченные посты",
"buy":"⭐ Подключить Premium","topup":"💳 Пополнить баланс","need":"Недостаточно средств. Сначала пополните минимум на $2.",
"choose_net":"💰 Выберите сеть:","txid":"🧾 После успешной оплаты отправьте TxID:","topup_ok":"✅ Платёж подтверждён. ${a:.2f} добавлено на баланс.",
"txbad":"❌ Транзакция не найдена или не соответствует требованиям.","txused":"⚠️ Этот TxID уже использован.","no_dest":"📡 Сначала добавьте канал или группу.",
"add_dest":"➕ Добавить канал/группу","dest_hint":"Отправьте @username или chat ID. Бот должен быть там администратором:","added":"✅ Добавлено.","deleted":"🗑 Удалено.",
"publish_choose":"📤 Куда отправить?","published":"✅ Отправлено.","free_limit":"В бесплатном режиме можно выбрать только 1 цель.","attr":"Этот пост подготовлен с помощью Post Button 🔘",
"users":"👥 Пользователи","premusers":"⭐ Premium","manual":"👑 Добавленные вручную","required":"🔐 Обязательная подписка","chats":"📢 Каналы/группы",
"attr_edit":"📝 Отправьте подпись для бесплатных пользователей:","support_edit":"💬 Отправьте username поддержки:","saved":"✅ Сохранено.",
"manual_uid":"👤 User ID для выдачи Premium:","manual_done":"✅ Premium выдан вручную.","manual_off":"✅ Ручной Premium отменён.",
"add_required":"➕ Добавить обязательный канал/группу","required_hint":"Отправьте @username или chat ID:","stats":"📊 Статистика","admin_only":"⛔ Только для администратора.",
"mydests":"📡 Мои каналы/группы","published_list":"📋 Отправленные посты","edit":"✏️ Редактировать","edit_text":"📝 Отправьте новый текст:","edit_media":"🖼 Отправьте новое фото/видео:","done":"✅ Готово","back":"⬅️ Назад","language":"🌐 Язык"
},
"ar":{
"welcome":"👋 أهلاً بك في Post Button 🔘!","choose":"🌐 اختر اللغة:","join":"🔐 لاستخدام البوت، انضم إلى:",
"check":"✅ تحقق","new":"📢 منشور جديد","saved_posts":"🗂 المنشورات المحفوظة","dests":"📡 القنوات والمجموعات","premium":"⭐ Premium","balance":"💰 الرصيد","support":"💬 الدعم","admin":"👑 لوحة الإدارة",
"media":"🖼 أرسل صورة أو فيديو. للتخطي: /skip","text":"📝 أرسل نص المنشور. إذا لم يوجد: /skip","ready":"✅ المنشور جاهز. اختر الإجراء:",
"preview":"👁 معاينة","buttons":"🔘 الأزرار","publish":"📤 إرسال","save_draft":"💾 حفظ المنشور","cancel":"❌ إلغاء","addbtn":"➕ إضافة زر",
"clearbtn":"🗑 حذف كل الأزرار","btntext":"🔘 أرسل نص الزر:","btnurl":"🔗 أرسل رابط الزر:","btnrow":"↔️ أرسل رقم الصف:",
"remove_attr":"⭐ إزالة التوقيع","prem_info":"⭐ Premium — $1 شهرياً\n\n• إزالة التوقيع\n• تعديل المنشورات المرسلة\n• منشورات غير محدودة",
"buy":"⭐ تفعيل Premium","topup":"💳 شحن الرصيد","need":"الرصيد غير كافٍ. اشحن $2 على الأقل أولاً.",
"choose_net":"💰 اختر الشبكة:","txid":"🧾 بعد نجاح الدفع أرسل TxID:","topup_ok":"✅ تم تأكيد الدفع. تمت إضافة ${a:.2f} إلى رصيدك.",
"txbad":"❌ لم يتم العثور على المعاملة أو لا تطابق الشروط.","txused":"⚠️ تم استخدام TxID هذا مسبقاً.","no_dest":"📡 أضف قناة أو مجموعة أولاً.",
"add_dest":"➕ إضافة قناة/مجموعة","dest_hint":"أرسل @username أو chat ID. يجب أن يكون البوت مشرفاً هناك:","added":"✅ تمت الإضافة.","deleted":"🗑 تم الحذف.",
"publish_choose":"📤 أين تريد الإرسال؟","published":"✅ تم الإرسال.","free_limit":"في الوضع المجاني يمكن اختيار وجهة واحدة فقط.","attr":"تم إعداد هذا المنشور بواسطة Post Button 🔘",
"users":"👥 المستخدمون","premusers":"⭐ أعضاء Premium","manual":"👑 المضافون يدوياً","required":"🔐 الاشتراك الإلزامي","chats":"📢 القنوات/المجموعات",
"attr_edit":"📝 أرسل توقيع المستخدمين المجانيين:","support_edit":"💬 أرسل username للدعم:","saved":"✅ تم الحفظ.",
"manual_uid":"👤 أرسل User ID لمنحه Premium:","manual_done":"✅ تم منح Premium يدوياً.","manual_off":"✅ تم إلغاء Premium اليدوي.",
"add_required":"➕ إضافة قناة/مجموعة إلزامية","required_hint":"أرسل @username أو chat ID:","stats":"📊 الإحصائيات","admin_only":"⛔ للإدارة فقط.",
"mydests":"📡 قنواتي/مجموعاتي","published_list":"📋 المنشورات المرسلة","edit":"✏️ تعديل","edit_text":"📝 أرسل النص الجديد:","edit_media":"🖼 أرسل الصورة/الفيديو الجديد:","done":"✅ تم","back":"⬅️ رجوع","language":"🌐 اللغة"
},
"en":{
"welcome":"👋 Welcome to Post Button 🔘!","choose":"🌐 Choose a language:","join":"🔐 To use the bot, join:",
"check":"✅ Check","new":"📢 New post","saved_posts":"🗂 Saved posts","dests":"📡 Channels & groups","premium":"⭐ Premium","balance":"💰 Balance","support":"💬 Support","admin":"👑 Admin panel",
"media":"🖼 Send a photo or video. Skip with /skip","text":"📝 Send the post text. If none: /skip","ready":"✅ Post is ready. Choose an action:",
"preview":"👁 Preview","buttons":"🔘 Buttons","publish":"📤 Publish","cancel":"❌ Cancel","addbtn":"➕ Add button",
"clearbtn":"🗑 Clear all buttons","btntext":"🔘 Send button text:","btnurl":"🔗 Send button URL:","btnrow":"↔️ Send row number:",
"remove_attr":"⭐ Remove attribution","prem_info":"⭐ Premium — $1/month\n\n• Remove attribution\n• Edit published posts\n• Unlimited posts",
"buy":"⭐ Enable Premium","topup":"💳 Top up balance","need":"Insufficient balance. Top up at least $2 first.",
"choose_net":"💰 Choose network:","txid":"🧾 After successful payment, send the TxID:","topup_ok":"✅ Payment confirmed. ${a:.2f} was added to your balance.",
"txbad":"❌ Transaction not found or does not meet the requirements.","txused":"⚠️ This TxID has already been used.","no_dest":"📡 Add a channel or group first.",
"add_dest":"➕ Add channel/group","dest_hint":"Send @username or chat ID. The bot must be an admin there:","added":"✅ Added.","deleted":"🗑 Deleted.",
"publish_choose":"📤 Where should it be published?","published":"✅ Published.","free_limit":"Free mode allows only 1 destination.","attr":"This post was prepared by Post Button 🔘",
"users":"👥 Users","premusers":"⭐ Premium members","manual":"👑 Manually added","required":"🔐 Mandatory membership","chats":"📢 Channels/groups",
"attr_edit":"📝 Send attribution text for free users:","support_edit":"💬 Send support username:","saved":"✅ Saved.",
"manual_uid":"👤 Send the User ID to grant Premium:","manual_done":"✅ Premium granted manually.","manual_off":"✅ Manual Premium revoked.",
"add_required":"➕ Add required channel/group","required_hint":"Send @username or chat ID:","stats":"📊 Statistics","admin_only":"⛔ Admin only.",
"mydests":"📡 My channels/groups","published_list":"📋 Published posts","edit":"✏️ Edit","edit_text":"📝 Send the new text:","edit_media":"🖼 Send the new photo/video:","done":"✅ Done","back":"⬅️ Back","language":"🌐 Language"
}}

def tr(lang,key,**kw):
    s=T.get(lang,T["uz"]).get(key,T["uz"].get(key,key))
    return s.format(**kw)

def kb_lang():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LANGS["uz"],callback_data="lang:uz"),InlineKeyboardButton(text=LANGS["tr"],callback_data="lang:tr")],
        [InlineKeyboardButton(text=LANGS["ru"],callback_data="lang:ru"),InlineKeyboardButton(text=LANGS["ar"],callback_data="lang:ar")],
        [InlineKeyboardButton(text=LANGS["en"],callback_data="lang:en")]
    ])

def kb_reply_menu(lang):
    labels={"uz":"☰ Menyu","ru":"☰ Меню","en":"☰ Menu","tr":"☰ Menü","ar":"☰ القائمة"}
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=labels.get(lang,labels["uz"]))]], resize_keyboard=True, is_persistent=True)

def kb_main(lang,admin=False):
    rows=[
        [InlineKeyboardButton(text=tr(lang,"new"),callback_data="post:new"),InlineKeyboardButton(text=tr(lang,"saved_posts"),callback_data="saved:list")],
        [InlineKeyboardButton(text=tr(lang,"dests"),callback_data="dest:list"),InlineKeyboardButton(text=tr(lang,"premium"),callback_data="prem:menu")],
        [InlineKeyboardButton(text=tr(lang,"balance"),callback_data="bal:menu"),InlineKeyboardButton(text=tr(lang,"support"),callback_data="support")],
    ]
    if admin: rows.append([InlineKeyboardButton(text=tr(lang,"admin"),callback_data="adm:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def kb_cancel():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌",callback_data="cancel")]])

def kb_draft(lang,premium):
    rows=[
        [InlineKeyboardButton(text=tr(lang,"preview"),callback_data="post:preview"),
         InlineKeyboardButton(text=tr(lang,"buttons"),callback_data="post:buttons")],
        [InlineKeyboardButton(text=tr(lang,"publish"),callback_data="post:choose")],
        [InlineKeyboardButton(text=tr(lang,"save_draft"),callback_data="saved:save")],
    ]
    if not premium: rows.append([InlineKeyboardButton(text=tr(lang,"remove_attr"),callback_data="prem:menu")])
    rows.append([InlineKeyboardButton(text=tr(lang,"cancel"),callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def kb_admin(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Пост жойлаш",callback_data="adm:post")],
        [InlineKeyboardButton(text="📊",callback_data="adm:stats"),InlineKeyboardButton(text=tr(lang,"users"),callback_data="adm:users")],
        [InlineKeyboardButton(text=tr(lang,"premusers"),callback_data="adm:prem"),InlineKeyboardButton(text=tr(lang,"manual"),callback_data="adm:manual:list")],
        [InlineKeyboardButton(text="📡 Пост каналлари",callback_data="adm:dests"),InlineKeyboardButton(text=tr(lang,"required"),callback_data="adm:req")],
        [InlineKeyboardButton(text=tr(lang,"chats"),callback_data="adm:chats"),InlineKeyboardButton(text="🌐 Тил",callback_data="adm:lang")],
        [InlineKeyboardButton(text=tr(lang,"attr_edit"),callback_data="adm:attr"),InlineKeyboardButton(text=tr(lang,"support_edit"),callback_data="adm:support")],
        [InlineKeyboardButton(text=tr(lang,"back"),callback_data="home")]
    ])

def kb_prem(lang,balance):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=tr(lang,"buy"),callback_data="prem:buy")],
        [InlineKeyboardButton(text=tr(lang,"topup"),callback_data="bal:menu")],
        [InlineKeyboardButton(text=tr(lang,"back"),callback_data="home")]
    ])

def kb_network(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟡 BEP20",callback_data="topup:bep20"),InlineKeyboardButton(text="🔴 TRC20",callback_data="topup:trc20")],
        [InlineKeyboardButton(text=tr(lang,"back"),callback_data="home")]
    ])

class DB:
    def __init__(self,path): self.path=path
    async def init(self):
        Path(self.path).parent.mkdir(parents=True,exist_ok=True)
        async with aiosqlite.connect(self.path) as d:
            await d.executescript("""
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS users(
              user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, lang TEXT DEFAULT '',
              balance REAL DEFAULT 0, premium_until TEXT, manual_premium INTEGER DEFAULT 0,
              created_at TEXT, updated_at TEXT);
            CREATE TABLE IF NOT EXISTS destinations(
              id INTEGER PRIMARY KEY AUTOINCREMENT, owner_id INTEGER, chat_id TEXT, title TEXT, kind TEXT, created_at TEXT,
              UNIQUE(owner_id,chat_id));
            CREATE TABLE IF NOT EXISTS required_chats(
              id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id TEXT UNIQUE, title TEXT, kind TEXT, enabled INTEGER DEFAULT 1, created_at TEXT);
            CREATE TABLE IF NOT EXISTS drafts(
              id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,title TEXT DEFAULT '',media_type TEXT,file_id TEXT,text TEXT,attribution INTEGER DEFAULT 1,created_at TEXT,updated_at TEXT);
            CREATE TABLE IF NOT EXISTS buttons(
              id INTEGER PRIMARY KEY AUTOINCREMENT,draft_id INTEGER,row_no INTEGER,position INTEGER,text TEXT,url TEXT,icon_custom_emoji_id TEXT DEFAULT '',style TEXT DEFAULT 'primary');
            CREATE TABLE IF NOT EXISTS published(
              id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,draft_id INTEGER,chat_id TEXT,message_id INTEGER,created_at TEXT);
            CREATE TABLE IF NOT EXISTS txs(
              txid TEXT PRIMARY KEY,network TEXT,user_id INTEGER,amount REAL,created_at TEXT);
            CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT);
            """)
            # Safe migrations for existing databases: never delete existing data.
            for sql in (
                "ALTER TABLE drafts ADD COLUMN title TEXT DEFAULT ''",
                "ALTER TABLE drafts ADD COLUMN saved INTEGER DEFAULT 0",
                "ALTER TABLE buttons ADD COLUMN icon_custom_emoji_id TEXT DEFAULT ''",
                "ALTER TABLE buttons ADD COLUMN style TEXT DEFAULT 'primary'",
            ):
                try:
                    await d.execute(sql)
                except Exception:
                    pass
            await d.commit()
    async def upsert(self,u):
        now=datetime.now(timezone.utc).isoformat()
        async with aiosqlite.connect(self.path) as d:
            await d.execute("""INSERT INTO users(user_id,username,first_name,created_at,updated_at)
            VALUES(?,?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET username=excluded.username,
            first_name=excluded.first_name,updated_at=excluded.updated_at""",
            (u.id,u.username or "",u.first_name or "",now,now)); await d.commit()
    async def user(self,uid):
        async with aiosqlite.connect(self.path) as d:
            d.row_factory=aiosqlite.Row
            c=await d.execute("SELECT * FROM users WHERE user_id=?",(uid,)); return await c.fetchone()
    async def lang(self,uid):
        u=await self.user(uid); return (u["lang"] if u else "") or "uz"
    async def setlang(self,uid,lang):
        async with aiosqlite.connect(self.path) as d:
            await d.execute("UPDATE users SET lang=? WHERE user_id=?",(lang,uid)); await d.commit()
    async def premium(self,uid):
        u=await self.user(uid)
        if not u:return False
        if u["manual_premium"]:return True
        if not u["premium_until"]:return False
        try:return datetime.fromisoformat(u["premium_until"])>datetime.now(timezone.utc)
        except:return False
    async def balance(self,uid):
        u=await self.user(uid); return float(u["balance"]) if u else 0
    async def add_balance(self,uid,a):
        async with aiosqlite.connect(self.path) as d:
            await d.execute("UPDATE users SET balance=balance+? WHERE user_id=?",(a,uid)); await d.commit()
    async def buy_premium(self,uid,price):
        async with aiosqlite.connect(self.path) as d:
            d.row_factory=aiosqlite.Row
            c=await d.execute("SELECT balance,premium_until,manual_premium FROM users WHERE user_id=?",(uid,));u=await c.fetchone()
            if not u or u["manual_premium"] or float(u["balance"])<price:return False
            base=datetime.now(timezone.utc)
            if u["premium_until"]:
                try:
                    old=datetime.fromisoformat(u["premium_until"])
                    if old>base:base=old
                except:pass
            until=(base+timedelta(days=30)).isoformat()
            await d.execute("UPDATE users SET balance=balance-?,premium_until=? WHERE user_id=?",(price,until,uid));await d.commit();return True
    async def manual(self,uid,on=True):
        async with aiosqlite.connect(self.path) as d:
            await d.execute("UPDATE users SET manual_premium=? WHERE user_id=?",(1 if on else 0,uid));await d.commit()
    async def users(self,limit=100):
        async with aiosqlite.connect(self.path) as d:
            d.row_factory=aiosqlite.Row;c=await d.execute("SELECT * FROM users ORDER BY created_at DESC LIMIT ?",(limit,));return await c.fetchall()
    async def reqs(self):
        async with aiosqlite.connect(self.path) as d:
            d.row_factory=aiosqlite.Row;c=await d.execute("SELECT * FROM required_chats ORDER BY id");return await c.fetchall()
    async def add_req(self,cid,title,kind):
        async with aiosqlite.connect(self.path) as d:
            await d.execute("INSERT OR REPLACE INTO required_chats(chat_id,title,kind,enabled,created_at) VALUES(?,?,?,?,?)",
                             (str(cid),title,kind,1,datetime.now(timezone.utc).isoformat()));await d.commit()
    async def del_req(self,i):
        async with aiosqlite.connect(self.path) as d:await d.execute("DELETE FROM required_chats WHERE id=?",(i,));await d.commit()
    async def dests(self,uid):
        async with aiosqlite.connect(self.path) as d:
            d.row_factory=aiosqlite.Row;c=await d.execute("SELECT * FROM destinations WHERE owner_id=? ORDER BY id",(uid,));return await c.fetchall()
    async def add_dest(self,uid,cid,title,kind):
        async with aiosqlite.connect(self.path) as d:
            await d.execute("INSERT OR IGNORE INTO destinations(owner_id,chat_id,title,kind,created_at) VALUES(?,?,?,?,?)",
                             (uid,str(cid),title,kind,datetime.now(timezone.utc).isoformat()));await d.commit()
    async def del_dest(self,uid,i):
        async with aiosqlite.connect(self.path) as d:await d.execute("DELETE FROM destinations WHERE owner_id=? AND id=?",(uid,i));await d.commit()
    async def draft(self,uid):
        async with aiosqlite.connect(self.path) as d:
            now=datetime.now(timezone.utc).isoformat();c=await d.execute("INSERT INTO drafts(user_id,title,created_at,updated_at) VALUES(?,?,?,?)",(uid,"",now,now));i=c.lastrowid;await d.commit();return i
    async def getdraft(self,i):
        async with aiosqlite.connect(self.path) as d:
            d.row_factory=aiosqlite.Row;c=await d.execute("SELECT * FROM drafts WHERE id=?",(i,));return await c.fetchone()
    async def save_draft_title(self,i,title):
        async with aiosqlite.connect(self.path) as d:
            await d.execute("UPDATE drafts SET title=?,saved=1,updated_at=? WHERE id=?",(title,datetime.now(timezone.utc).isoformat(),i));await d.commit()
    async def saved_drafts(self,uid,limit=100):
        async with aiosqlite.connect(self.path) as d:
            d.row_factory=aiosqlite.Row
            c=await d.execute("SELECT * FROM drafts WHERE user_id=? AND COALESCE(saved,0)=1 ORDER BY updated_at DESC,id DESC LIMIT ?",(uid,limit));return await c.fetchall()
    async def upd(self,i,**kw):
        allowed={"media_type","file_id","text","attribution"};kw={k:v for k,v in kw.items() if k in allowed}
        if not kw:return
        kw["updated_at"]=datetime.now(timezone.utc).isoformat()
        q=",".join(f"{k}=?" for k in kw)
        async with aiosqlite.connect(self.path) as d:await d.execute(f"UPDATE drafts SET {q} WHERE id=?",(*kw.values(),i));await d.commit()
    async def buttons(self,did):
        async with aiosqlite.connect(self.path) as d:
            d.row_factory=aiosqlite.Row;c=await d.execute("SELECT * FROM buttons WHERE draft_id=? ORDER BY row_no,position,id",(did,));return await c.fetchall()
    async def addbtn(self,did,row,text,url,icon_custom_emoji_id="",style="primary"):
        async with aiosqlite.connect(self.path) as d:
            c=await d.execute("SELECT COALESCE(MAX(position),0)+1 FROM buttons WHERE draft_id=? AND row_no=?",(did,row));pos=(await c.fetchone())[0]
            await d.execute("INSERT INTO buttons(draft_id,row_no,position,text,url,icon_custom_emoji_id,style) VALUES(?,?,?,?,?,?,?)",(did,row,pos,text,url,icon_custom_emoji_id or "",style or "primary"));await d.commit()
    async def delbtn(self,bid):
        async with aiosqlite.connect(self.path) as d:await d.execute("DELETE FROM buttons WHERE id=?",(bid,));await d.commit()
    async def clearbtn(self,did):
        async with aiosqlite.connect(self.path) as d:await d.execute("DELETE FROM buttons WHERE draft_id=?",(did,));await d.commit()
    async def savepub(self,uid,did,cid,mid):
        async with aiosqlite.connect(self.path) as d:
            await d.execute("INSERT INTO published(user_id,draft_id,chat_id,message_id,created_at) VALUES(?,?,?,?,?)",
                             (uid,did,str(cid),mid,datetime.now(timezone.utc).isoformat()));await d.commit()
    async def pubs(self,uid):
        async with aiosqlite.connect(self.path) as d:
            d.row_factory=aiosqlite.Row;c=await d.execute("SELECT * FROM published WHERE user_id=? ORDER BY id DESC LIMIT 30",(uid,));return await c.fetchall()
    async def txexists(self,tx):
        async with aiosqlite.connect(self.path) as d:c=await d.execute("SELECT 1 FROM txs WHERE txid=?",(tx,));return await c.fetchone() is not None
    async def addtx(self,tx,net,uid,a):
        async with aiosqlite.connect(self.path) as d:await d.execute("INSERT INTO txs(txid,network,user_id,amount,created_at) VALUES(?,?,?,?,?)",(tx,net,uid,a,datetime.now(timezone.utc).isoformat()));await d.commit()
    async def getset(self,k,default):
        async with aiosqlite.connect(self.path) as d:c=await d.execute("SELECT value FROM settings WHERE key=?",(k,));r=await c.fetchone();return r[0] if r else default
    async def setset(self,k,v):
        async with aiosqlite.connect(self.path) as d:await d.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)",(k,str(v)));await d.commit()

async def membership_ok(bot,db,uid):
    missing=[]
    for r in await db.reqs():
        if not r["enabled"]:continue
        try:
            m=await bot.get_chat_member(r["chat_id"],uid)
            if m.status in ("left","kicked"):missing.append(r)
        except:missing.append(r)
    return missing

async def build_markup(db,did):
    rows={}
    for b in await db.buttons(did):
        kwargs={"text":b["text"],"url":b["url"]}
        icon=b["icon_custom_emoji_id"] if "icon_custom_emoji_id" in b.keys() else ""
        style=b["style"] if "style" in b.keys() else "primary"
        # START is always the green Telegram button, including buttons created by older versions.
        if (b["text"] or "").strip().upper() == "START":
            style="success"
        if icon:
            kwargs["icon_custom_emoji_id"]=icon
        if style in ("primary","success","danger"):
            kwargs["style"]=style
        rows.setdefault(int(b["row_no"]),[]).append(InlineKeyboardButton(**kwargs))
    return InlineKeyboardMarkup(inline_keyboard=[rows[k] for k in sorted(rows)]) if rows else None

async def send_draft(bot,db,draft,cid,lang,premium):
    text=draft["text"] or ""
    if not premium and draft["attribution"]:
        attr=await db.getset(f"attr_{lang}",tr(lang,"attr"))
        text=(text+"\n\n"+attr).strip()
    markup=await build_markup(db,draft["id"])
    if draft["media_type"]=="photo":
        msg=await bot.send_photo(cid,draft["file_id"],caption=text[:1024],reply_markup=markup)
    elif draft["media_type"]=="video":
        msg=await bot.send_video(cid,draft["file_id"],caption=text[:1024],reply_markup=markup)
    else:
        msg=await bot.send_message(cid,text or " ",reply_markup=markup)
    await db.savepub(draft["user_id"],draft["id"],cid,msg.message_id)
    return msg

async def verify_tx(network,txid):
    if network=="bep20":
        if not ETHERSCAN_KEY or not BEP20_WALLET or not BEP20_USDT:return None,"not_configured"
        params={"chainid":"56","module":"account","action":"tokentx","contractaddress":BEP20_USDT,
                "address":BEP20_WALLET,"page":"1","offset":"100","sort":"desc","apikey":ETHERSCAN_KEY}
        async with aiohttp.ClientSession() as s:
            async with s.get("https://api.etherscan.io/v2/api",params=params,timeout=20) as r:data=await r.json()
        if data.get("status")!="1":return None,"not_found"
        for x in data.get("result",[]):
            if x.get("hash","").lower()==txid.lower():
                if x.get("to","").lower()!=BEP20_WALLET.lower():return None,"wrong_to"
                if x.get("contractAddress","").lower()!=BEP20_USDT.lower():return None,"wrong_token"
                dec=int(x.get("tokenDecimal") or 6)
                return float(Decimal(x.get("value","0"))/(Decimal(10)**dec)),"ok"
        return None,"not_found"
    if network=="trc20":
        if not TRONGRID_KEY or not TRC20_WALLET or not TRC20_USDT:return None,"not_configured"
        url=f"https://api.trongrid.io/v1/accounts/{TRC20_WALLET}/transactions/trc20"
        params={"limit":200,"contract_address":TRC20_USDT,"only_confirmed":"true","only_to":"true","order_by":"block_timestamp,desc"}
        async with aiohttp.ClientSession(headers={"TRON-PRO-API-KEY":TRONGRID_KEY}) as s:
            async with s.get(url,params=params,timeout=20) as r:data=await r.json()
        for x in data.get("data",[]):
            h=x.get("transaction_id","") or x.get("transactionId","")
            if h.lower()==txid.lower():
                to=x.get("to","")
                if to and to.lower()!=TRC20_WALLET.lower():return None,"wrong_to"
                contract=(x.get("token_info") or {}).get("address","") or x.get("contract_address","")
                if contract and contract.lower()!=TRC20_USDT.lower():return None,"wrong_token"
                dec=int((x.get("token_info") or {}).get("decimals",6))
                return float(Decimal(str(x.get("value","0")))/(Decimal(10)**dec)),"ok"
        return None,"not_found"
    return None,"network"

class S(StatesGroup):
    media=State(); text=State(); btntext=State(); btnurl=State(); btnrow=State()
    txid=State(); adddest=State(); addreq=State(); manual=State(); attr=State(); support=State()
    edittext=State(); editmedia=State(); btnedittext=State(); btnediturl=State(); btnemoji=State()

db=DB(DB_PATH)
dp=Dispatcher()

def lang_of(uid):
    return db.lang(uid)

@dp.message(Command("new"))
async def cmd_new(m:Message,state:FSMContext):
    await state.clear();did=await db.draft(m.from_user.id);await state.update_data(did=did);lang=await lang_of(m.from_user.id);await state.set_state(S.media);await m.answer(tr(lang,"media"),reply_markup=kb_cancel())

@dp.message(Command("saved"))
async def cmd_saved(m:Message):
    lang=await lang_of(m.from_user.id);rows=await db.saved_drafts(m.from_user.id);kb=[[InlineKeyboardButton(text="🗂 "+(r["title"] or r["text"] or "Post")[:45],callback_data=f"saved:open:{r['id']}")] for r in rows];kb.append([InlineKeyboardButton(text=tr(lang,"back"),callback_data="home")]);await m.answer(tr(lang,"saved_posts"),reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@dp.message(CommandStart())
async def start(m:Message,state:FSMContext):
    await db.upsert(m.from_user);await state.clear()
    u=await db.user(m.from_user.id)
    if not u["lang"]:
        await m.answer(tr("uz","choose"),reply_markup=kb_lang());return
    missing=await membership_ok(m.bot,db,m.from_user.id)
    if missing:
        rows=[]
        for r in missing:
            if str(r["chat_id"]).startswith("@"):
                rows.append([InlineKeyboardButton(text=("📢 " if r["kind"]=="channel" else "👥 ")+r["title"],url=f"https://t.me/{str(r['chat_id'])[1:]}")])
        rows.append([InlineKeyboardButton(text=tr(u["lang"],"check"),callback_data="gate:check")])
        await m.answer(tr(u["lang"],"join"),reply_markup=InlineKeyboardMarkup(inline_keyboard=rows));return
    await m.answer(tr(u["lang"],"welcome"),reply_markup=kb_main(u["lang"],m.from_user.id==ADMIN_ID))
    await m.answer("⁣",reply_markup=kb_reply_menu(u["lang"]))

@dp.callback_query(F.data.startswith("lang:"))
async def setlang(c:CallbackQuery):
    lang=c.data.split(":")[1]
    if lang not in LANGS: return await c.answer("❌",show_alert=True)
    await db.setlang(c.from_user.id,lang);await c.answer()
    missing=await membership_ok(c.bot,db,c.from_user.id)
    if missing:
        rows=[]
        for r in missing:
            cid=str(r["chat_id"])
            if cid.startswith("@"):
                rows.append([InlineKeyboardButton(text=("📢 " if r["kind"]=="channel" else "👥 ")+r["title"],url=f"https://t.me/{cid[1:]}")])
        rows.append([InlineKeyboardButton(text=tr(lang,"check"),callback_data="gate:check")])
        await c.message.edit_text(tr(lang,"join"),reply_markup=InlineKeyboardMarkup(inline_keyboard=rows));return
    await c.message.edit_text(tr(lang,"welcome"),reply_markup=kb_main(lang,c.from_user.id==ADMIN_ID))
    try: await c.message.answer("⁣",reply_markup=kb_reply_menu(lang))
    except Exception: pass

@dp.callback_query(F.data=="gate:check")
async def gate(c:CallbackQuery):
    lang=await lang_of(c.from_user.id);miss=await membership_ok(c.bot,db,c.from_user.id);await c.answer("✅" if not miss else "❌")
    if not miss:await c.message.edit_text(tr(lang,"welcome"),reply_markup=kb_main(lang,c.from_user.id==ADMIN_ID))

@dp.message(F.text.in_({"☰ Меню","☰ Menu","☰ Menü","☰ القائمة","☰ Menyu"}))
async def reply_menu(m:Message,state:FSMContext):
    await state.clear()
    lang=await lang_of(m.from_user.id)
    await m.answer(tr(lang,"welcome"),reply_markup=kb_main(lang,m.from_user.id==ADMIN_ID))

@dp.callback_query(F.data=="home")
async def home(c:CallbackQuery):
    lang=await lang_of(c.from_user.id);await c.message.edit_text(tr(lang,"welcome"),reply_markup=kb_main(lang,c.from_user.id==ADMIN_ID))

@dp.callback_query(F.data=="support")
async def support(c:CallbackQuery):
    lang=await lang_of(c.from_user.id);u=await db.getset("support",SUPPORT_USERNAME)
    await c.message.edit_text(tr(lang,"support").upper()+f"\n\n@{u}",reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"💬 @{u}",url=f"https://t.me/{u}")],
        [InlineKeyboardButton(text=tr(lang,"back"),callback_data="home")]]))

@dp.callback_query(F.data=="dest:list")
async def dest_list(c:CallbackQuery):
    lang=await lang_of(c.from_user.id);rows=await db.dests(c.from_user.id)
    kb=[[InlineKeyboardButton(text=f"🗑 {r['title'] or r['chat_id']}",callback_data=f"dest:del:{r['id']}")] for r in rows]
    kb.append([InlineKeyboardButton(text=tr(lang,"add_dest"),callback_data="dest:add")])
    kb.append([InlineKeyboardButton(text=tr(lang,"published_list"),callback_data="pub:list")])
    kb.append([InlineKeyboardButton(text=tr(lang,"back"),callback_data="home")])
    await c.message.edit_text(tr(lang,"mydests"),reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data=="dest:add")
async def dest_add(c:CallbackQuery,state:FSMContext):
    lang=await lang_of(c.from_user.id);await state.set_state(S.adddest);await c.message.answer(tr(lang,"dest_hint"),reply_markup=kb_cancel())

@dp.message(S.adddest)
async def dest_add_msg(m:Message,state:FSMContext):
    lang=await lang_of(m.from_user.id);cid=m.text.strip()
    try:
        chat=await m.bot.get_chat(cid)
        kind="channel" if chat.type=="channel" else "group"
        me=await m.bot.get_me()
        member=await m.bot.get_chat_member(chat.id,me.id)
        if member.status not in ("administrator","creator"):
            raise ValueError("Бот канал/группада администратор бўлиши керак.")
        await db.add_dest(m.from_user.id,str(chat.id),chat.title or cid,kind)
        await m.answer(tr(lang,"added"));await state.clear()
    except Exception as e:
        await m.answer("❌ "+str(e)[:300])

@dp.callback_query(F.data.startswith("dest:del:"))
async def dest_del(c:CallbackQuery):
    await db.del_dest(c.from_user.id,int(c.data.split(":")[-1]));await c.answer()
    await dest_list(c)

@dp.callback_query(F.data=="adm:post")
async def admin_post(c:CallbackQuery,state:FSMContext):
    if c.from_user.id!=ADMIN_ID:
        return await c.answer("⛔",show_alert=True)
    await state.clear()
    did=await db.draft(c.from_user.id)
    await state.update_data(did=did, admin_post=True)
    lang=await lang_of(c.from_user.id)
    await state.set_state(S.media)
    await c.message.answer(tr(lang,"media"),reply_markup=kb_cancel())
    await c.answer()

@dp.callback_query(F.data=="post:new")
async def new_post(c:CallbackQuery,state:FSMContext):
    await state.clear();did=await db.draft(c.from_user.id);await state.update_data(did=did)
    lang=await lang_of(c.from_user.id);await state.set_state(S.media)
    await c.message.answer(tr(lang,"media"),reply_markup=kb_cancel())

@dp.message(S.media)
async def media(m:Message,state:FSMContext):
    lang=await lang_of(m.from_user.id);data=await state.get_data();did=data["did"]
    if m.text and m.text.strip().lower()=="/skip":
        await db.upd(did,media_type=None,file_id=None)
    elif m.photo:
        await db.upd(did,media_type="photo",file_id=m.photo[-1].file_id)
    elif m.video:
        await db.upd(did,media_type="video",file_id=m.video.file_id)
    else:
        await m.answer(tr(lang,"media"));return
    await state.set_state(S.text);await m.answer(tr(lang,"text"),reply_markup=kb_cancel())

@dp.message(S.text)
async def post_text(m:Message,state:FSMContext):
    data=await state.get_data();did=data["did"];text="" if (m.text or "").strip().lower()=="/skip" else (m.text or "")
    await db.upd(did,text=text);await state.set_state(None);await state.update_data(did=did);lang=await lang_of(m.from_user.id)
    prem=await db.premium(m.from_user.id);await m.answer(tr(lang,"ready"),reply_markup=kb_draft(lang,prem))

@dp.callback_query(F.data=="saved:save")
async def saved_save(c:CallbackQuery,state:FSMContext):
    data=await state.get_data();did=data.get("did")
    if not did:
        return await c.answer("❌",show_alert=True)
    lang=await lang_of(c.from_user.id)
    d=await db.getdraft(did)
    title=(d["text"] or "").replace("\n"," ").strip()[:50] or "Post"
    await db.save_draft_title(did,title)
    await c.answer("✅")
    await c.message.edit_text("💾 "+title,reply_markup=kb_main(lang,c.from_user.id==ADMIN_ID))

def saved_action_text(lang,kind):
    if kind=="delete_all":
        return {"uz":"🗑 Барчасини ўчириш","ru":"🗑 Удалить всё","en":"🗑 Delete all","tr":"🗑 Tümünü sil","ar":"🗑 حذف الكل"}.get(lang,"🗑 Delete all")
    return {"uz":"🗂 Ҳозирча сақланган постлар йўқ.","ru":"🗂 Сохранённых постов пока нет.","en":"🗂 No saved posts yet.","tr":"🗂 Henüz kayıtlı gönderi yok.","ar":"🗂 لا توجد منشورات محفوظة بعد."}.get(lang,"🗂 No saved posts yet.")

@dp.callback_query(F.data=="saved:list")
async def saved_list(c:CallbackQuery):
    lang=await lang_of(c.from_user.id);rows=await db.saved_drafts(c.from_user.id)
    kb=[]
    if not rows:
        await c.message.edit_text(tr(lang,"saved_posts")+"\n\n"+saved_action_text(lang,"empty"),reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=tr(lang,"back"),callback_data="home")]]))
        return
    for r in rows:
        title=(r["title"] or r["text"] or "Post").replace("\n"," ").strip()[:42]
        kb.append([
            InlineKeyboardButton(text="📂 "+title,callback_data=f"saved:open:{r['id']}"),
            InlineKeyboardButton(text="🗑",callback_data=f"saved:del:{r['id']}")
        ])
    kb.append([InlineKeyboardButton(text=saved_action_text(lang,"delete_all"),callback_data="saved:clear")])
    kb.append([InlineKeyboardButton(text=tr(lang,"back"),callback_data="home")])
    await c.message.edit_text(tr(lang,"saved_posts"),reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data.startswith("saved:del:"))
async def saved_delete(c:CallbackQuery):
    did=int(c.data.split(":")[-1])
    await db.delete_draft(did,c.from_user.id)
    await c.answer("🗑 Ўчирилди")
    await saved_list(c)

@dp.callback_query(F.data=="saved:clear")
async def saved_clear(c:CallbackQuery):
    rows=await db.saved_drafts(c.from_user.id,1000)
    for r in rows:
        await db.delete_draft(r["id"],c.from_user.id)
    await c.answer("🗑 Барчаси ўчирилди")
    await saved_list(c)

@dp.callback_query(F.data.startswith("saved:open:"))
async def saved_open(c:CallbackQuery,state:FSMContext):
    did=int(c.data.split(":")[-1])
    d=await db.getdraft(did)
    if not d or d["user_id"]!=c.from_user.id:return await c.answer("❌",show_alert=True)
    await state.clear();await state.update_data(did=did)
    lang=await lang_of(c.from_user.id)
    await c.message.edit_text(tr(lang,"ready"),reply_markup=kb_draft(lang,await db.premium(c.from_user.id)))

@dp.callback_query(F.data=="post:preview")
async def preview(c:CallbackQuery):
    data=await c.message.bot.get_me();lang=await lang_of(c.from_user.id);s=dp.fsm.get_context(bot=c.bot,chat_id=c.from_user.id,user_id=c.from_user.id)
    st=await s.get_data();did=st.get("did")
    if not did: await c.answer("No draft");return
    d=await db.getdraft(did);prem=await db.premium(c.from_user.id)
    text=d["text"] or ""
    if not prem and d["attribution"]:text=(text+"\n\n"+await db.getset(f"attr_{lang}",tr(lang,"attr"))).strip()
    markup=await build_markup(db,did)
    if d["media_type"]=="photo":await c.message.answer_photo(d["file_id"],caption=text[:1024],reply_markup=markup)
    elif d["media_type"]=="video":await c.message.answer_video(d["file_id"],caption=text[:1024],reply_markup=markup)
    else:await c.message.answer(text or " ",reply_markup=markup)
    await c.answer()

@dp.callback_query(F.data=="post:buttons")
async def buttons_menu(c:CallbackQuery):
    lang=await lang_of(c.from_user.id);rows=[]
    s=dp.fsm.get_context(bot=c.bot,chat_id=c.from_user.id,user_id=c.from_user.id);did=(await s.get_data()).get("did")
    for b in await db.buttons(did):
        rows.append([
            InlineKeyboardButton(text=f"✏️ {b['text']}",callback_data=f"btn:edit:{b['id']}"),
            InlineKeyboardButton(text="🗑",callback_data=f"btn:del:{b['id']}")
        ])
    rows.append([InlineKeyboardButton(text=tr(lang,"addbtn"),callback_data="btn:add")])
    rows.append([InlineKeyboardButton(text="⭐ Premium emoji (icon)",callback_data="btn:emoji")])
    rows.append([InlineKeyboardButton(text=tr(lang,"clearbtn"),callback_data="btn:clear")])
    rows.append([InlineKeyboardButton(text=tr(lang,"back"),callback_data="post:back")])
    await c.message.edit_text(tr(lang,"buttons"),reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await c.answer()

@dp.callback_query(F.data=="btn:emoji")
async def btn_emoji_menu(c:CallbackQuery):
    lang=await lang_of(c.from_user.id);s=dp.fsm.get_context(bot=c.bot,chat_id=c.from_user.id,user_id=c.from_user.id);did=(await s.get_data()).get("did")
    rows=[[InlineKeyboardButton(text=f"{b['text']}",callback_data=f"btn:emoji:{b['id']}")] for b in await db.buttons(did)]
    rows.append([InlineKeyboardButton(text=tr(lang,"back"),callback_data="post:buttons")])
    await c.message.edit_text("⭐ Қайси кнопкага Premium emoji icon қўшилади?",reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))

@dp.callback_query(F.data.startswith("btn:emoji:"))
async def btn_emoji_choose(c:CallbackQuery,state:FSMContext):
    bid=int(c.data.split(":")[-1]);await state.update_data(bid=bid);await state.set_state(S.btnemoji)
    await c.message.answer("⭐ Энди Telegram Premium custom emoji'нинг ўзини хабар қилиб юборинг. Оддий emoji эмас.",reply_markup=kb_cancel())

@dp.message(S.btnemoji)
async def btn_emoji_receive(m:Message,state:FSMContext):
    entities=m.entities or []
    custom=None
    for e in entities:
        if e.type=="custom_emoji":
            custom=e.custom_emoji_id;break
    if not custom:
        return await m.answer("❌ Custom Premium emoji топилмади. Telegram'дан Premium emoji'ни хабар қилиб юборинг.")
    data=await state.get_data();bid=data["bid"]
    async with aiosqlite.connect(DB_PATH) as d:
        await d.execute("UPDATE buttons SET icon_custom_emoji_id=? WHERE id=?",(custom,bid));await d.commit()
    did=(await state.get_data()).get("did")
    await state.set_state(None)
    if did: await state.update_data(did=did)
    lang=await lang_of(m.from_user.id);await m.answer("✅ Premium emoji icon сақланди. Telegram уни кнопка матнининг ОЛДИДА кўрсатади.",reply_markup=kb_draft(lang,await db.premium(m.from_user.id)))

@dp.callback_query(F.data=="btn:add")
async def btn_add(c:CallbackQuery,state:FSMContext):
    data=await state.get_data()
    if not data.get("did"):
        did=await db.draft(c.from_user.id);await state.update_data(did=did)
    lang=await lang_of(c.from_user.id);await state.set_state(S.btntext);await c.message.answer(tr(lang,"btntext"),reply_markup=kb_cancel())

@dp.message(S.btntext)
async def btn_text(m:Message,state:FSMContext):
    lang=await lang_of(m.from_user.id);await state.update_data(btntext=m.text);await state.set_state(S.btnurl);await m.answer(tr(lang,"btnurl"),reply_markup=kb_cancel())

@dp.message(S.btnurl)
async def btn_url(m:Message,state:FSMContext):
    if not (m.text or "").startswith(("http://","https://")):
        await m.answer("URL must start with http:// or https://");return
    lang=await lang_of(m.from_user.id);await state.update_data(btnurl=m.text);await state.set_state(S.btnrow);await m.answer(tr(lang,"btnrow"),reply_markup=kb_cancel())

@dp.message(S.btnrow)
async def btn_row(m:Message,state:FSMContext):
    try:row=max(1,int(m.text))
    except:await m.answer("1");return
    data=await state.get_data()
    did=data.get("did")
    if not did:
        did=await db.draft(m.from_user.id);await state.update_data(did=did)
    style="success" if (data.get("btntext") or "").strip().upper()=="START" else "primary"
    await db.addbtn(did,row,data.get("btntext", "Button"),data.get("btnurl", ""),"",style)
    await state.set_state(None);await state.update_data(did=did)
    lang=await lang_of(m.from_user.id);await m.answer(tr(lang,"saved"),reply_markup=kb_draft(lang,await db.premium(m.from_user.id)))

@dp.callback_query(F.data.startswith("btn:edit:"))
async def btn_edit(c:CallbackQuery,state:FSMContext):
    lang=await lang_of(c.from_user.id)
    bid=int(c.data.split(":")[-1])
    async with aiosqlite.connect(DB_PATH) as d:
        d.row_factory=aiosqlite.Row
        cur=await d.execute("SELECT * FROM buttons WHERE id=?",(bid,)); b=await cur.fetchone()
    if not b: return await c.answer("❌",show_alert=True)
    await state.update_data(bid=bid,did=int(b["draft_id"]))
    await state.set_state(S.btnedittext)
    await c.message.answer(f"✏️ {b['text']}\n\n{tr(lang,'btntext')}",reply_markup=kb_cancel())

@dp.message(S.btnedittext)
async def btn_edit_text(m:Message,state:FSMContext):
    data=await state.get_data(); await state.update_data(btntext=m.text); await state.set_state(S.btnediturl)
    lang=await lang_of(m.from_user.id); await m.answer(tr(lang,"btnurl"),reply_markup=kb_cancel())

@dp.message(S.btnediturl)
async def btn_edit_url(m:Message,state:FSMContext):
    if not (m.text or "").startswith(("http://","https://")):
        return await m.answer("URL must start with http:// or https://")
    data=await state.get_data()
    async with aiosqlite.connect(DB_PATH) as d:
        await d.execute("UPDATE buttons SET text=?,url=? WHERE id=?",(data.get("btntext",""),m.text,data["bid"]))
        await d.commit()
    did=data.get("did")
    await state.set_state(None)
    if did: await state.update_data(did=did)
    lang=await lang_of(m.from_user.id); await m.answer(tr(lang,"saved"),reply_markup=kb_draft(lang,await db.premium(m.from_user.id)) if did else kb_main(lang,m.from_user.id==ADMIN_ID))

@dp.callback_query(F.data.startswith("btn:del:"))
async def btn_del(c:CallbackQuery):
    await db.delbtn(int(c.data.split(":")[-1]));await c.answer("✅")
    await buttons_menu(c)

@dp.callback_query(F.data=="btn:clear")
async def btn_clear(c:CallbackQuery):
    s=dp.fsm.get_context(bot=c.bot,chat_id=c.from_user.id,user_id=c.from_user.id);did=(await s.get_data()).get("did")
    await db.clearbtn(did);await c.answer("✅");await buttons_menu(c)

@dp.callback_query(F.data=="post:back")
async def post_back(c:CallbackQuery):
    s=dp.fsm.get_context(bot=c.bot,chat_id=c.from_user.id,user_id=c.from_user.id);did=(await s.get_data()).get("did")
    lang=await lang_of(c.from_user.id);await c.message.edit_text(tr(lang,"ready"),reply_markup=kb_draft(lang,await db.premium(c.from_user.id)))

@dp.callback_query(F.data=="post:choose")
async def choose_publish(c:CallbackQuery):
    lang=await lang_of(c.from_user.id);dests=await db.dests(c.from_user.id)
    if not dests:await c.answer(tr(lang,"no_dest"),show_alert=True);return
    prem=await db.premium(c.from_user.id)
    if not prem:dests=dests[:1]
    s=dp.fsm.get_context(bot=c.bot,chat_id=c.from_user.id,user_id=c.from_user.id);await s.update_data(selected=[])
    rows=[[InlineKeyboardButton(text=f"☐ {d['title']}",callback_data=f"sel:{d['id']}")] for d in dests]
    rows.append([InlineKeyboardButton(text=tr(lang,"publish"),callback_data="publish:go")])
    await c.message.edit_text(tr(lang,"publish_choose"),reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))

@dp.callback_query(F.data.startswith("sel:"))
async def select_dest(c:CallbackQuery):
    s=dp.fsm.get_context(bot=c.bot,chat_id=c.from_user.id,user_id=c.from_user.id);data=await s.get_data();sel=data.get("selected",[])
    i=int(c.data.split(":")[-1])
    if i in sel:sel.remove(i)
    else:
        if not await db.premium(c.from_user.id):sel=[i]
        else:sel.append(i)
    await s.update_data(selected=sel);await c.answer("☑️")

@dp.callback_query(F.data=="publish:go")
async def publish_go(c:CallbackQuery):
    lang=await lang_of(c.from_user.id);s=dp.fsm.get_context(bot=c.bot,chat_id=c.from_user.id,user_id=c.from_user.id);data=await s.get_data();sel=data.get("selected",[]);did=data.get("did")
    if not sel:await c.answer("❌",show_alert=True);return
    dests=await db.dests(c.from_user.id);chosen=[d for d in dests if d["id"] in sel]
    d=await db.getdraft(did);prem=await db.premium(c.from_user.id);ok=0
    for dest in chosen:
        try:await send_draft(c.bot,db,d,dest["chat_id"],lang,prem);ok+=1
        except Exception as e:await c.message.answer(f"❌ {dest['title']}: {str(e)[:200]}")
    await c.message.answer(f"{tr(lang,'published')} {ok}",reply_markup=kb_main(lang,c.from_user.id==ADMIN_ID));await s.clear()

@dp.callback_query(F.data=="prem:menu")
async def prem_menu(c:CallbackQuery):
    lang=await lang_of(c.from_user.id);u=await db.user(c.from_user.id)
    if u["manual_premium"]:
        await c.message.edit_text(tr(lang,"prem_info")+"\n\n"+tr(lang,"manual"),reply_markup=kb_prem(lang,u["balance"]));return
    if await db.premium(c.from_user.id):
        until=u["premium_until"] or "∞";await c.message.edit_text(tr(lang,"prem_info")+f"\n\n⏳ {until}",reply_markup=kb_prem(lang,u["balance"]));return
    await c.message.edit_text(tr(lang,"prem_info"),reply_markup=kb_prem(lang,u["balance"]))

@dp.callback_query(F.data=="prem:buy")
async def prem_buy(c:CallbackQuery):
    lang=await lang_of(c.from_user.id)
    if await db.buy_premium(c.from_user.id,PREMIUM_PRICE):await c.message.edit_text("⭐ Premium ✅",reply_markup=kb_main(lang,c.from_user.id==ADMIN_ID))
    else:await c.answer(tr(lang,"need"),show_alert=True)

@dp.callback_query(F.data=="bal:menu")
async def bal(c:CallbackQuery):
    lang=await lang_of(c.from_user.id);b=await db.balance(c.from_user.id)
    await c.message.edit_text(f"💰 {b:.2f} USDT",reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=tr(lang,"topup"),callback_data="topup:choose")],[InlineKeyboardButton(text=tr(lang,"back"),callback_data="home")]]))

@dp.callback_query(F.data=="topup:choose")
async def topup_choose(c:CallbackQuery):
    lang=await lang_of(c.from_user.id);await c.message.edit_text(tr(lang,"choose_net"),reply_markup=kb_network(lang))

@dp.callback_query(F.data.startswith("topup:") & ~F.data.endswith("choose"))
async def topup_network(c:CallbackQuery,state:FSMContext):
    net=c.data.split(":")[1];lang=await lang_of(c.from_user.id)
    addr=BEP20_WALLET if net=="bep20" else TRC20_WALLET
    await state.update_data(net=net);await state.set_state(S.txid)
    await c.message.answer(f"{'🟡 BEP20' if net=='bep20' else '🔴 TRC20'}\n\n💳 {addr}\n\n{tr(lang,'txid')}",reply_markup=kb_cancel())

@dp.message(S.txid)
async def txid(m:Message,state:FSMContext):
    lang=await lang_of(m.from_user.id);tx=(m.text or "").strip()
    if await db.txexists(tx):await m.answer(tr(lang,"txused"));return
    data=await state.get_data();amount,status=await verify_tx(data["net"],tx)
    if status=="ok" and amount is not None and amount>=MIN_TOPUP:
        await db.addtx(tx,data["net"],m.from_user.id,amount);await db.add_balance(m.from_user.id,amount);await state.clear()
        await m.answer(tr(lang,"topup_ok",a=amount),reply_markup=kb_main(lang,m.from_user.id==ADMIN_ID))
    else:await m.answer(tr(lang,"txbad"))

@dp.callback_query(F.data=="adm:menu")
async def adm_menu(c:CallbackQuery):
    if c.from_user.id!=ADMIN_ID:return await c.answer("⛔",show_alert=True)
    lang=await lang_of(c.from_user.id);await c.message.edit_text(tr(lang,"admin"),reply_markup=kb_admin(lang))

@dp.callback_query(F.data=="adm:lang")
async def adm_lang(c:CallbackQuery):
    if c.from_user.id!=ADMIN_ID:return
    await c.message.edit_text("🌐 Тилни танланг:",reply_markup=kb_lang())
    await c.answer()

@dp.callback_query(F.data=="adm:stats")
async def adm_stats(c:CallbackQuery):
    if c.from_user.id!=ADMIN_ID:return
    us=await db.users(10000);p=sum(1 for u in us if u["manual_premium"] or (u["premium_until"] and datetime.fromisoformat(u["premium_until"])>datetime.now(timezone.utc)))
    lang=await lang_of(c.from_user.id);await c.message.edit_text(f"{tr(lang,'stats')}\n\n👥 {len(us)}\n⭐ {p}",reply_markup=kb_admin(lang))

@dp.callback_query(F.data=="adm:users")
async def adm_users(c:CallbackQuery):
    if c.from_user.id!=ADMIN_ID:return
    lang=await lang_of(c.from_user.id);rows=await db.users(50);txt=tr(lang,"users")+"\n\n"
    for u in rows:txt+=f"• {u['user_id']} @{u['username'] or '-'}\n"
    await c.message.edit_text(txt[:4000],reply_markup=kb_admin(lang))

@dp.callback_query(F.data=="adm:prem")
async def adm_prem(c:CallbackQuery):
    if c.from_user.id!=ADMIN_ID:return
    lang=await lang_of(c.from_user.id);rows=await db.users(1000);txt=tr(lang,"premusers")+"\n\n"
    for u in rows:
        if u["manual_premium"] or (u["premium_until"] and datetime.fromisoformat(u["premium_until"])>datetime.now(timezone.utc)):
            txt+=f"• {u['user_id']} @{u['username'] or '-'} {'👑manual' if u['manual_premium'] else u['premium_until']}\n"
    await c.message.edit_text(txt[:4000],reply_markup=kb_admin(lang))

@dp.callback_query(F.data=="adm:manual:list")
async def adm_manual_list(c:CallbackQuery):
    if c.from_user.id!=ADMIN_ID:return
    lang=await lang_of(c.from_user.id); rows=await db.users(1000)
    manual_rows=[u for u in rows if u["manual_premium"]]
    kb=[[InlineKeyboardButton(text=f"🟢 {u['user_id']} @{u['username'] or '-'}",callback_data=f"adm:manual:off:{u['user_id']}")] for u in manual_rows]
    kb.append([InlineKeyboardButton(text="➕ Premium қўшиш",callback_data="adm:manual:add")])
    kb.append([InlineKeyboardButton(text=tr(lang,"back"),callback_data="adm:menu")])
    txt=tr(lang,"manual")+"\n\n"+("Ҳозирча бўш." if not manual_rows else "Керакли фойдаланувчини босиб Premium'ни бекор қилиш мумкин.")
    await c.message.edit_text(txt,reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data=="adm:manual:add")
async def adm_manual_add(c:CallbackQuery,state:FSMContext):
    if c.from_user.id!=ADMIN_ID:return
    lang=await lang_of(c.from_user.id);await state.set_state(S.manual);await c.message.answer(tr(lang,"manual_uid"),reply_markup=kb_cancel())

@dp.callback_query(F.data.startswith("adm:manual:off:"))
async def adm_manual_off(c:CallbackQuery):
    if c.from_user.id!=ADMIN_ID:return
    uid=int(c.data.split(":")[-1]);await db.manual(uid,False);await c.answer("✅");await adm_manual_list(c)

@dp.callback_query(F.data=="adm:manual")
async def adm_manual(c:CallbackQuery,state:FSMContext):
    if c.from_user.id!=ADMIN_ID:return
    lang=await lang_of(c.from_user.id);await state.set_state(S.manual);await c.message.answer(tr(lang,"manual_uid"),reply_markup=kb_cancel())

@dp.message(S.manual)
async def manual(m:Message,state:FSMContext):
    if m.from_user.id!=ADMIN_ID:return
    lang=await lang_of(m.from_user.id)
    try:uid=int(m.text.strip());await db.upsert(type("U",(),{"id":uid,"username":"","first_name":""})());await db.manual(uid,True);await state.clear();await m.answer(tr(lang,"manual_done"))
    except:await m.answer("User ID")

@dp.callback_query(F.data=="adm:dests")
async def adm_dests(c:CallbackQuery):
    if c.from_user.id!=ADMIN_ID:return
    lang=await lang_of(c.from_user.id); rows=await db.dests(ADMIN_ID)
    kb=[[InlineKeyboardButton(text=f"🗑 {r['title'] or r['chat_id']}",callback_data=f"adm:dest:del:{r['id']}")] for r in rows]
    kb.append([InlineKeyboardButton(text="➕ Канал/группа қўшиш",callback_data="adm:dest:add")])
    kb.append([InlineKeyboardButton(text=tr(lang,"back"),callback_data="adm:menu")])
    await c.message.edit_text("📡 Пост каналлари",reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data=="adm:dest:add")
async def adm_dest_add(c:CallbackQuery,state:FSMContext):
    if c.from_user.id!=ADMIN_ID:return
    lang=await lang_of(c.from_user.id);await state.set_state(S.adddest);await c.message.answer(tr(lang,"dest_hint"),reply_markup=kb_cancel())

@dp.callback_query(F.data.startswith("adm:dest:del:"))
async def adm_dest_del(c:CallbackQuery):
    if c.from_user.id!=ADMIN_ID:return
    await db.del_dest(ADMIN_ID,int(c.data.split(":")[-1]));await c.answer("✅");await adm_dests(c)

@dp.callback_query(F.data=="adm:req")
async def adm_req(c:CallbackQuery,state:FSMContext):
    if c.from_user.id!=ADMIN_ID:return
    lang=await lang_of(c.from_user.id);req=await db.reqs()
    rows=[[InlineKeyboardButton(text=f"🗑 {r['title']}",callback_data=f"req:del:{r['id']}")] for r in req]
    rows.append([InlineKeyboardButton(text=tr(lang,"add_required"),callback_data="req:add")])
    rows.append([InlineKeyboardButton(text=tr(lang,"back"),callback_data="adm:menu")])
    await c.message.edit_text(tr(lang,"required"),reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))

@dp.callback_query(F.data=="req:add")
async def req_add(c:CallbackQuery,state:FSMContext):
    if c.from_user.id!=ADMIN_ID:return
    lang=await lang_of(c.from_user.id);await state.set_state(S.addreq);await c.message.answer(tr(lang,"required_hint"),reply_markup=kb_cancel())

@dp.message(S.addreq)
async def req_add_msg(m:Message,state:FSMContext):
    if m.from_user.id!=ADMIN_ID:return
    cid=m.text.strip()
    try:
        chat=await m.bot.get_chat(cid);kind="channel" if chat.type=="channel" else "group";await db.add_req(str(chat.id),chat.title or cid,kind);await state.clear();await m.answer(tr("uz","added"))
    except Exception as e:await m.answer("❌ "+str(e)[:300])

@dp.callback_query(F.data.startswith("req:del:"))
async def req_del(c:CallbackQuery):
    if c.from_user.id!=ADMIN_ID:return
    await db.del_req(int(c.data.split(":")[-1]));await c.answer("✅");await adm_req(c, FSMContext)

@dp.callback_query(F.data=="adm:chats")
async def adm_chats(c:CallbackQuery):
    if c.from_user.id!=ADMIN_ID:return
    lang=await lang_of(c.from_user.id);req=await db.reqs();txt=tr(lang,"chats")+"\n\n"
    for r in req:txt+=f"• {r['id']} {r['title']} {r['chat_id']}\n"
    await c.message.edit_text(txt[:4000],reply_markup=kb_admin(lang))

@dp.callback_query(F.data=="adm:attr")
async def adm_attr(c:CallbackQuery,state:FSMContext):
    if c.from_user.id!=ADMIN_ID:return
    lang=await lang_of(c.from_user.id);await state.set_state(S.attr);await c.message.answer(tr(lang,"attr_edit"),reply_markup=kb_cancel())

@dp.message(S.attr)
async def attr(m:Message,state:FSMContext):
    if m.from_user.id!=ADMIN_ID:return
    lang=await lang_of(m.from_user.id);await db.setset(f"attr_{lang}",m.text);await state.clear();await m.answer(tr(lang,"saved"))

@dp.callback_query(F.data=="adm:support")
async def adm_support(c:CallbackQuery,state:FSMContext):
    if c.from_user.id!=ADMIN_ID:return
    lang=await lang_of(c.from_user.id);await state.set_state(S.support);await c.message.answer(tr(lang,"support_edit"),reply_markup=kb_cancel())

@dp.message(S.support)
async def support_save(m:Message,state:FSMContext):
    if m.from_user.id!=ADMIN_ID:return
    await db.setset("support",m.text.strip().lstrip("@"));await state.clear();await m.answer(tr("uz","saved"))

@dp.callback_query(F.data=="pub:list")
async def pub_list(c:CallbackQuery):
    lang=await lang_of(c.from_user.id);rows=await db.pubs(c.from_user.id)
    if not rows:await c.message.edit_text("📋 —",reply_markup=kb_main(lang,c.from_user.id==ADMIN_ID));return
    kb=[]
    for r in rows:
        kb.append([InlineKeyboardButton(text=f"✏️ {r['chat_id']} #{r['message_id']}",callback_data=f"pub:edit:{r['id']}")])
    kb.append([InlineKeyboardButton(text=tr(lang,"back"),callback_data="home")])
    await c.message.edit_text(tr(lang,"published_list"),reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data.startswith("pub:edit:"))
async def pub_edit(c:CallbackQuery,state:FSMContext):
    lang=await lang_of(c.from_user.id);prem=await db.premium(c.from_user.id)
    if not prem:await c.answer(tr(lang,"remove_attr"),show_alert=True);return
    # first build keeps edit UI simple: ask for new caption/text
    pid=int(c.data.split(":")[-1])
    async with aiosqlite.connect(DB_PATH) as d:
        d.row_factory=aiosqlite.Row;cur=await d.execute("SELECT * FROM published WHERE id=? AND user_id=?",(pid,c.from_user.id));r=await cur.fetchone()
    if not r:return
    await state.update_data(pub_id=pid,chat_id=r["chat_id"],message_id=r["message_id"])
    await state.set_state(S.edittext);await c.message.answer(tr(lang,"edit_text"),reply_markup=kb_cancel())

@dp.message(S.edittext)
async def edittext(m:Message,state:FSMContext):
    lang=await lang_of(m.from_user.id);data=await state.get_data()
    try:
        await m.bot.edit_message_caption(chat_id=data["chat_id"],message_id=data["message_id"],caption=m.text)
    except:
        try:await m.bot.edit_message_text(chat_id=data["chat_id"],message_id=data["message_id"],text=m.text)
        except Exception as e:await m.answer("❌ "+str(e)[:300]);return
    await state.clear();await m.answer(tr(lang,"saved"))

@dp.callback_query(F.data=="cancel")
async def cancel(c:CallbackQuery,state:FSMContext):
    await state.clear();lang=await lang_of(c.from_user.id);await c.message.answer(tr(lang,"welcome"),reply_markup=kb_main(lang,c.from_user.id==ADMIN_ID));await c.answer()

async def main():
    if not BOT_TOKEN: raise SystemExit("BOT_TOKEN is missing. Copy .env.example to .env and set it.")
    await db.init()
    bot=Bot(BOT_TOKEN)
    print("Post Button started")
    try:
        await bot.set_my_commands([BotCommand(command="start", description="Start"),BotCommand(command="new", description="New post"),BotCommand(command="saved", description="Saved posts")])
    except Exception:
        pass
    await dp.start_polling(bot)

if __name__=="__main__":
    asyncio.run(main())
