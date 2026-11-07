from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from app.schemas import LeadRequestSchema
from app.telegram import send_to_telegram
from database.db import create_request, update_request_telegram_status, get_bouquet_by_id, get_db_connection

router = APIRouter()


@router.get("/health", summary="Healthcheck")
async def health_check():
    """Проверка доступности сервиса и соединения с SQLite."""
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
        return {"status": "ok", "service": "love-flower-api", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database unreachable: {e}"
        )


@router.post("/api/requests", response_class=JSONResponse, summary="Создание заявки")
async def create_lead_request(payload: LeadRequestSchema):
    """
    1. Приём и валидация данных заявки (Pydantic).
    2. Сохранение заявки в SQLite (таблица requests).
    3. Отправка форматированного уведомления в Telegram Bot API.
    4. Обновление статуса отправки в БД.
    """
    data = payload.model_dump()

    # Получаем букет, если указан bouquet_id
    bouquet = None
    if payload.bouquet_id:
        bouquet = get_bouquet_by_id(payload.bouquet_id)
        if bouquet:
            data["budget_amount"] = data.get("budget_amount") or bouquet["price"]
            data["size_code"] = data.get("size_code") or bouquet["size_code"]

    try:
        # 1. Запись в БД
        request_id = create_request(data)

        # 2. Отправка в Telegram
        tg_res = await send_to_telegram(request_id, data, bouquet)

        # 3. Обновление статуса в БД
        update_request_telegram_status(
            request_id=request_id,
            status=tg_res.get("status", "pending"),
            message_id=tg_res.get("message_id")
        )

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "success": True,
                "request_id": request_id,
                "redirect_url": f"/order/success/{request_id}",
                "telegram": tg_res.get("status")
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании заявки: {e}"
        )
