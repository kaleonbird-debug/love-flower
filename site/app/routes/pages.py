import re
import os
from typing import Optional
from pathlib import Path
from urllib.parse import quote
from fastapi import APIRouter, Request, Form, HTTPException, Query, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.schemas import BouquetFilterParams
from app.telegram import send_to_telegram, SIZE_MAP, BUDGET_MAP, PALETTE_MAP, OCCASION_MAP
from database.db import (
    get_bouquets,
    get_bouquet_by_slug,
    get_bouquet_by_id,
    get_all_tags,
    create_request,
    update_request_telegram_status,
    get_request_by_id,
)

TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Регистрируем кастомные Jinja-фильтры
def format_price(value: Optional[int]) -> str:
    if value is None:
        return ""
    return f"{value:,}".replace(",", " ")

templates.env.filters["format_price"] = format_price

router = APIRouter()


@router.get("/", response_class=HTMLResponse, summary="Главная страница")
async def route_home(request: Request):
    """Главная страница: выбор бюджета, витрина букетов в наличии сегодня, преимущества."""
    ready_bouquets = get_bouquets(ready_today=True, limit=4)
    budget_ranges = [
        {"code": "0-3500", "label": "до 3 500 ₽", "desc": "Мини-комплименты и лаконичные моно-составы", "count": 2},
        {"code": "3500-5500", "label": "3 500 – 5 500 ₽", "desc": "Самый популярный формат стильных букетов", "count": 2},
        {"code": "5500-10000", "label": "5 500 – 10 000 ₽", "desc": "Пышная авторская флористика и садовые розы", "count": 4},
        {"code": "10000-15000", "label": "10 000 – 15 000 ₽", "desc": "Премиальные объемные композиции и пионы", "count": 2},
        {"code": "15000-plus", "label": "от 15 000 ₽", "desc": "Гранд-композиции и эксклюзивные сорта", "count": 2},
    ]
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "budget_ranges": budget_ranges,
            "ready_bouquets": ready_bouquets,
        }
    )


@router.get("/catalog", response_class=HTMLResponse, summary="Каталог букетов")
async def route_catalog(
    request: Request,
    budget: Optional[str] = Query(None),
    size: Optional[str] = Query(None),
    palette: Optional[str] = Query(None),
    occasion: Optional[str] = Query(None),
    ready_today: Optional[bool] = Query(False),
    sort: Optional[str] = Query("popular"),
):
    """Каталог с фасетной фильтрацией по бюджету, размеру, палитре и готовности."""
    filters = BouquetFilterParams(
        budget=budget,
        size=size,
        palette=palette,
        occasion=occasion,
        ready_today=ready_today,
        sort=sort,
    )
    bouquets = get_bouquets(
        budget=budget,
        size=size,
        palette=palette,
        occasion=occasion,
        ready_today=ready_today,
        sort=sort,
    )
    all_tags = get_all_tags()

    # Проверяем, есть ли активные фильтры
    has_active_filters = bool(budget or size or palette or occasion or ready_today)

    return templates.TemplateResponse(
        request=request,
        name="catalog.html",
        context={
            "bouquets": bouquets,
            "filters": filters,
            "has_active_filters": has_active_filters,
            "all_tags": all_tags,
            "size_map": SIZE_MAP,
            "budget_map": BUDGET_MAP,
            "palette_map": PALETTE_MAP,
            "occasion_map": OCCASION_MAP,
        }
    )


@router.get("/catalog/{slug}", response_class=HTMLResponse, summary="Карточка букета")
async def route_bouquet_detail(request: Request, slug: str):
    """Детальная карточка букета с фотогалереей, описанием и быстрым переходом в заказ."""
    bouquet = get_bouquet_by_slug(slug)
    if not bouquet:
        raise HTTPException(status_code=404, detail="Букет не найден")

    # Похожие букеты
    similar_bouquets = [b for b in get_bouquets(limit=4) if b["slug"] != slug][:3]

    return templates.TemplateResponse(
        request=request,
        name="bouquet_detail.html",
        context={
            "bouquet": bouquet,
            "similar_bouquets": similar_bouquets,
            "size_map": SIZE_MAP,
        }
    )


@router.get("/order", response_class=HTMLResponse, summary="Форма заявки")
async def route_order_page(
    request: Request,
    bouquet: Optional[str] = Query(None),
    budget: Optional[str] = Query(None),
    size: Optional[str] = Query(None),
    palette: Optional[str] = Query(None),
):
    """Страница оформления заказа с автоподстановкой выбранного букета или параметров."""
    selected_bouquet = None
    if bouquet:
        selected_bouquet = get_bouquet_by_slug(bouquet)

    all_tags = get_all_tags()

    return templates.TemplateResponse(
        request=request,
        name="order.html",
        context={
            "selected_bouquet": selected_bouquet,
            "initial_budget": budget or (selected_bouquet["price"] if selected_bouquet else None),
            "initial_size": size or (selected_bouquet["size_code"] if selected_bouquet else "standard"),
            "initial_palette": palette or (selected_bouquet["tags"][0]["slug"] if selected_bouquet and selected_bouquet.get("tags") else None),
            "all_tags": all_tags,
            "size_map": SIZE_MAP,
            "budget_map": BUDGET_MAP,
            "palette_map": PALETTE_MAP,
        }
    )


@router.post("/order", response_class=RedirectResponse, summary="Отправка заявки из формы")
async def route_submit_order_form(
    request: Request,
    customer_phone: str = Form(...),
    customer_name: Optional[str] = Form(None),
    bouquet_id: Optional[int] = Form(None),
    budget_range: Optional[str] = Form(None),
    budget_amount: Optional[int] = Form(None),
    size_code: Optional[str] = Form(None),
    palette: Optional[str] = Form(None),
    occasion: Optional[str] = Form(None),
    delivery_date: Optional[str] = Form("Сегодня"),
    delivery_time_slot: Optional[str] = Form("Как можно скорее"),
    delivery_type: str = Form("delivery"),
    delivery_address: Optional[str] = Form(None),
    comment: Optional[str] = Form(None),
):
    """Обрабатывает стандартную HTML-форму заявки и перенаправляет на экран благодарности."""
    # Очистка и валидация телефона
    digits = re.sub(r"\D", "", customer_phone)
    if len(digits) == 11 and digits[0] in ("7", "8"):
        clean_phone = f"+7{digits[1:]}"
    elif len(digits) == 10:
        clean_phone = f"+7{digits}"
    elif len(digits) >= 11:
        clean_phone = f"+{digits}"
    else:
        clean_phone = customer_phone.strip()

    data = {
        "bouquet_id": bouquet_id,
        "custom_reference_info": None,
        "budget_range": budget_range,
        "budget_amount": budget_amount,
        "size_code": size_code,
        "palette": palette,
        "occasion": occasion,
        "delivery_date": delivery_date or "Сегодня",
        "delivery_time_slot": delivery_time_slot or "Как можно скорее",
        "customer_name": customer_name.strip() if customer_name else None,
        "customer_phone": clean_phone,
        "delivery_type": delivery_type,
        "delivery_address": delivery_address.strip() if delivery_address else None,
        "comment": comment.strip() if comment else None,
    }

    # Подтягиваем данные букета, если передан bouquet_id
    bouquet = None
    if bouquet_id:
        bouquet = get_bouquet_by_id(bouquet_id)
        if bouquet:
            if not data["budget_amount"]:
                data["budget_amount"] = bouquet["price"]
            if not data["size_code"]:
                data["size_code"] = bouquet["size_code"]

    # 1. Сохранение в БД
    request_id = create_request(data)

    # 2. Отправка в Telegram
    tg_res = await send_to_telegram(request_id, data, bouquet)

    # 3. Обновление статуса
    update_request_telegram_status(
        request_id=request_id,
        status=tg_res.get("status", "pending"),
        message_id=tg_res.get("message_id")
    )

    # Переход на экран благодарности
    return RedirectResponse(
        url=f"/order/success/{request_id}",
        status_code=status.HTTP_303_SEE_OTHER
    )


def _build_telegram_link(lead: dict) -> str:
    """Ссылка на чат с флористом в Telegram (если настроен бот компании)."""
    username = (os.getenv("TELEGRAM_BOT_USERNAME") or "").strip().lstrip("@")
    if not username:
        return ""
    request_id = lead.get("id", "")
    lead_text = (
        f"Вопрос по заявке LF-{request_id}"
        if request_id else "Вопрос по заявке с сайта"
    )
    return f"https://t.me/{username}?text={quote(lead_text)}"


@router.get("/order/success/{request_id}", response_class=HTMLResponse, summary="Экран подтверждения")
async def route_order_success(request: Request, request_id: int):
    """Экран подтверждения успешного приёма заявки."""
    lead = get_request_by_id(request_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    return templates.TemplateResponse(
        request=request,
        name="success.html",
        context={
            "lead": lead,
            "size_map": SIZE_MAP,
            "budget_map": BUDGET_MAP,
            "telegram_link": _build_telegram_link(lead),
        }
    )


@router.get("/how", response_class=HTMLResponse, summary="Доставка и получение")
async def route_how(request: Request):
    """Страница с информацией о доставке, самовывозе и бережной упаковке."""
    return templates.TemplateResponse(request=request, name="how.html", context={})


@router.get("/privacy", response_class=HTMLResponse, summary="Политика конфиденциальности")
async def route_privacy(request: Request):
    """Политика конфиденциальности персональных данных (152-ФЗ)."""
    return templates.TemplateResponse(request=request, name="privacy.html", context={})
