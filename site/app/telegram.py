import logging
from datetime import datetime
from typing import Any, Dict, Optional
import httpx
from app.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, BASE_URL

logger = logging.getLogger("love_flower.telegram")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [telegram] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

SIZE_MAP = {
    "compact": "Компактный (S)",
    "standard": "Стандартный (M)",
    "large": "Большой (L/XL)",
}

BUDGET_MAP = {
    "0-3500": "до 3 500",
    "3500-5500": "3 500 – 5 500",
    "5500-10000": "5 500 – 10 000",
    "10000-15000": "10 000 – 15 000",
    "15000-plus": "от 15 000",
}

PALETTE_MAP = {
    "tender": "Нежная / пастельная",
    "vibrant": "Яркая / сочная",
    "white": "Монохром / белая",
    "deep": "Тёмная / драматичная",
    "seasonal": "Сезонная",
}

OCCASION_MAP = {
    "mom": "Маме",
    "wife": "Жене",
    "friend": "Подруге",
    "birthday": "День рождения",
    "just_because": "Без повода / Просто так",
}


def format_telegram_message(
    request_id: int,
    data: Dict[str, Any],
    bouquet: Optional[Dict[str, Any]] = None
) -> str:
    """Форматирует красивое HTML-сообщение для Telegram Bot API согласно спецификации."""
    created_at = datetime.now().strftime("%d.%m.%Y %H:%M")

    # Букет
    if bouquet:
        bouquet_title = bouquet.get("title", "Букет")
        bouquet_slug = bouquet.get("slug", "")
        bouquet_line = f'💐 <b>Букет:</b> <a href="{BASE_URL}/catalog/{bouquet_slug}">{bouquet_title}</a>'
        price = bouquet.get("price")
        is_from = bouquet.get("is_price_from")
        budget_display = f"{'от ' if is_from else ''}{price:,}".replace(",", " ")
    else:
        bouquet_line = '💐 <b>Тип:</b> Индивидуальный подбор по параметрам'
        if data.get("budget_amount"):
            budget_display = f"{data['budget_amount']:,}".replace(",", " ")
        elif data.get("budget_range"):
            budget_display = BUDGET_MAP.get(data["budget_range"], data["budget_range"])
        else:
            budget_display = "Уточнить у клиента"

    # Размер
    size_code = data.get("size_code") or (bouquet.get("size_code") if bouquet else None)
    size_display = SIZE_MAP.get(size_code, "По согласованию")

    # Палитра
    palette = data.get("palette")
    if not palette and bouquet and bouquet.get("palette_names"):
        palette_display = ", ".join(bouquet["palette_names"])
    else:
        palette_display = PALETTE_MAP.get(palette, palette or "Любая / на вкус флориста")

    # Доставка
    deliv_type = data.get("delivery_type", "delivery")
    deliv_type_display = "Самовывоз из салона" if deliv_type == "pickup" else "Доставка по городу (такси)"
    address = data.get("delivery_address")
    address_line = f": <i>{address}</i>" if (address and deliv_type == "delivery") else ""

    customer_name = data.get("customer_name") or "Не указано"
    customer_phone = data.get("customer_phone", "")
    delivery_date = data.get("delivery_date", "Сегодня")
    delivery_time = data.get("delivery_time_slot", "Как можно скорее")
    comment = data.get("comment", "").strip()

    comment_block = ""
    if comment:
        comment_block = f"""
💬 <b>Комментарий / Записка:</b>
<i>«{comment}»</i>"""

    msg = f"""🌸 <b>НОВАЯ ЗАЯВКА #LF-{request_id}</b>
───────────────
{bouquet_line}
💰 <b>Бюджет:</b> {budget_display} ₽
📏 <b>Размер:</b> {size_display}
🎨 <b>Палитра:</b> {palette_display}
───────────────
📅 <b>Когда:</b> {delivery_date} (интервал: {delivery_time})
🚗 <b>Получение:</b> {deliv_type_display}{address_line}
───────────────
👤 <b>Клиент:</b> {customer_name}
📞 <b>Телефон:</b> <a href="tel:{customer_phone}">{customer_phone}</a>{comment_block}
───────────────
⏰ <i>Создано: {created_at}</i>"""

    return msg.strip()


async def send_to_telegram(
    request_id: int,
    data: Dict[str, Any],
    bouquet: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Отправляет уведомление в Telegram Bot API.
    Если токены не заданы (MVP заглушка) — логирует заявку и не падает.
    """
    html_text = format_telegram_message(request_id, data, bouquet)

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        sep_eq = "=" * 60
        sep_dash = "-" * 60
        log_msg = (
            f"\n{sep_eq}\n"
            f"[TELEGRAM STUB] Токен бота или ID чата не настроены в .env.\n"
            f"Заявка #LF-{request_id} успешно записана в БД и выведена в консоль:\n"
            f"{sep_dash}\n"
            f"{html_text}\n"
            f"{sep_eq}"
        )
        logger.info(log_msg)
        return {
            "status": "pending",
            "message_id": None,
            "stub": True,
            "note": "Telegram bot token or chat ID not set. Logged to console."
        }

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": html_text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                res_data = resp.json()
                message_id = res_data.get("result", {}).get("message_id")
                logger.info(f"Заявка #LF-{request_id} успешно отправлена в Telegram (message_id: {message_id})")
                return {"status": "sent", "message_id": message_id}
            else:
                logger.error(f"Ошибка Telegram API ({resp.status_code}): {resp.text}")
                return {"status": "failed", "error": f"HTTP {resp.status_code}: {resp.text}"}
    except Exception as e:
        logger.error(f"Сбой отправки сообщения в Telegram для заявки #{request_id}: {e}")
        return {"status": "failed", "error": str(e)}
