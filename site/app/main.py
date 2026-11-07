from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.routes.pages import router as pages_router
from app.routes.api import router as api_router
from database.db import init_db

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # При старте приложения инициализируем БД и проверяем наличие данных
    try:
        init_db()
    except Exception as e:
        print(f"[WARN] init_db failed: {e}", flush=True)
    yield


app = FastAPI(
    title="ЛавФловер — Цветочный салон",
    description="Черновой MVP сайта цветочного салона «ЛавФловер» (LoveFlower)",
    version="1.0.0",
    lifespan=lifespan,
)

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Подключаем роуты
app.include_router(pages_router)
app.include_router(api_router)


# Обработчик ошибки 404
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    return HTMLResponse(
        content=f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Страница не найдена — ЛавФловер</title>
            <link rel="stylesheet" href="/static/css/style.css">
        </head>
        <body>
            <div class="empty-state" style="padding: 100px 20px; text-align: center;">
                <h1 style="font-size: 4rem; margin-bottom: 10px; font-weight: 300;">404</h1>
                <p style="font-size: 1.2rem; color: #666; margin-bottom: 25px;">Запрашиваемая страница не найдена</p>
                <a href="/" class="btn btn-primary">Вернуться на главную</a>
            </div>
        </body>
        </html>
        """,
        status_code=404,
    )
