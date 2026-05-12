import telebot
import random

# ===== Функции для работы с файлом фактов =====
def load_facts():
    try:
        with open("facts_tg.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        # Начальный список фактов
        return [
            "Осьминог имеет три сердца.",
            "У пчёл есть внутренние часы.",
            "Бамбук — это трава, а не дерево."
        ]

def save_facts(facts):
    with open("facts.txt", "w", encoding="utf-8") as f:
        for fact in facts:
            f.write(fact + "\n")

# ===== Загружаем факты при старте =====
facts = load_facts()

# ===== Создаём бота =====
TOKEN = "8256840542:AAEovc5kBr_IDqX-ecbD0jjjM2PER0E-uCY"
bot = telebot.TeleBot(TOKEN)

# ===== Команда /start =====
@bot.message_handler(commands=['start'])
def start(message):
    text = (
        "📚 Бот для управления списком фактов.\n\n"
        "Доступные команды:\n"
        "/random — случайный факт\n"
        "/add <текст> — добавить факт (после команды через пробел)\n"
        "/list — показать все факты с номерами\n"
        "/delete <номер> — удалить факт по номеру\n"
        "/search <слово> — найти факты по слову\n"
        "/help — повторить список команд"
    )
    bot.send_message(message.chat.id, text)

# ===== /help =====
@bot.message_handler(commands=['help'])
def help_cmd(message):
    start(message)  # просто повторяем то же сообщение

# ===== /random =====
@bot.message_handler(commands=['random'])
def random_fact(message):
    if not facts:
        bot.send_message(message.chat.id, "Список фактов пуст. Добавь через /add")
    else:
        bot.send_message(message.chat.id, random.choice(facts))

# ===== /add =====
@bot.message_handler(commands=['add'])
def add_fact(message):
    # Получаем текст после команды /add
    fact_text = message.text[len('/add '):].strip()
    if not fact_text:
        bot.reply_to(message, "Напиши факт после команды, например: /add Крокодилы умеют плакать")
        return
    facts.append(fact_text)
    save_facts(facts)
    bot.reply_to(message, f"✅ Факт добавлен:\n{fact_text}")

# ===== /list =====
@bot.message_handler(commands=['list'])
def list_facts(message):
    if not facts:
        bot.send_message(message.chat.id, "Список фактов пуст.")
        return
    # Формируем нумерованный список
    result = "📋 Список фактов:\n\n"
    for i, fact in enumerate(facts, 1):
        result += f"{i}. {fact}\n"
        # Telegram имеет ограничение 4096 символов, разобьём если длинно
        if len(result) > 3500:
            bot.send_message(message.chat.id, result)
            result = ""
    if result:
        bot.send_message(message.chat.id, result)

# ===== /delete =====
@bot.message_handler(commands=['delete'])
def delete_fact(message):
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        bot.reply_to(message, "Используй: /delete <номер> (номер из /list)")
        return
    num = int(parts[1])
    if 1 <= num <= len(facts):
        removed = facts.pop(num - 1)
        save_facts(facts)
        bot.reply_to(message, f"🗑 Удалён факт:\n{removed}")
    else:
        bot.reply_to(message, f"Неверный номер. Всего фактов: {len(facts)}")

# ===== /search =====
@bot.message_handler(commands=['search'])
def search_fact(message):
    keyword = message.text[len('/search '):].strip().lower()
    if not keyword:
        bot.reply_to(message, "Укажи слово для поиска, например: /search осьминог")
        return
    found = [fact for fact in facts if keyword in fact.lower()]
    if found:
        result = f"🔍 Найдено {len(found)} фактов:\n\n"
        for f in found:
            result += f"• {f}\n"
            if len(result) > 3500:
                bot.send_message(message.chat.id, result)
                result = ""
        if result:
            bot.send_message(message.chat.id, result)
    else:
        bot.send_message(message.chat.id, "Ничего не найдено.")

# ===== Запуск бота =====
print("Бот запущен...")
bot.infinity_polling()