# Технический каркас сайта и структура каталога Love Flower

Документ описывает структуру каталога, реляционную модель данных, схему приёма заявок в Telegram, архитектуру серверных роутов на FastAPI и открытые технические риски для салона цветов **Love Flower** (владелец — Евгения Кучерявая).

Стек первого релиза: **Python 3.11+ / FastAPI + SQLite + Jinja2 + Telegram Bot API**.  
Концепция UI: **Минималистичный чёрно-белый дизайн**, где цветовыми акцентами являются исключительно фотографии букетов.

---

## 1. Дерево категорий и фильтров

Главный пользовательский сценарий — быстрый подбор букета под выделенный бюджет без перегрузки интерфейса лишними шагами. Поиск строится по принципу: **«Сначала бюджет → затем калибровка по размеру, гамме, поводу и срочности»**.

```
[Главная: Выбор бюджета]
   ├── До 3 500 ₽         (комплименты, моно-букеты мини)
   ├── 3 500 – 5 500 ₽    (базовые популярные букеты)
   ├── 5 500 – 10 000 ₽   (авторские сборные букеты среднего объема)
   ├── 10 000 – 15 000 ₽  (пышные премиальные композиции)
   └── От 15 000 ₽        (гигантские букеты, эксклюзивные сорта)
         │
         ▼
[Каталог с фасетными фильтрами поверх выборки]
   ├── Размер:        [ Компактный (S) | Стандартный (M) | Большой (L/XL) ]
   ├── Палитра:       [ Нежная / Пастельная | Яркая / Сочная | Монохром / Белая | Тёмная / Драматичная | Сезонная ]
   ├── Повод:         [ «Маме» | «Подруге» | «Жене» | «День рождения» | «Свидание» | «Без повода» ]
   └── Срочность:     [ [x] Можно сегодня (в наличии / сборка до 2 часов) ]
```

### 1.1. Вход по бюджету (базовые сегменты)
Входные категории оформляются крупными карточками на первом экране главной страницы и закреплёнными табами/чипсами в шапке каталога:
1. **`budget=0-3500` («До 3 500 ₽»)**: букеты-комплименты, моно-составы в лаконичной бумаге, сухоцветы, мини-коробки.
2. **`budget=3500-5500` («3 500 – 5 500 ₽»)**: самый ходовой массовый сегмент; стильные сборные композиции среднего формата.
3. **`budget=5500-10000` («5 500 – 10 000 ₽»)**: авторская флористика, ранункулюсы, садовые розы, гортензии, пышная фактура.
4. **`budget=10000-15000` («10 000 – 15 000 ₽»)**: эффектные объемные подарки, редкие сорта, премиальная упаковка.
5. **`budget=15000-plus` («От 15 000 ₽»)**: вау-композиции от 50–101 стебля, гигантские корзины и шляпные коробки.

### 1.2. Дополнительные фасетные фильтры
Фильтры накладываются поверх выбранного бюджета (или применяются ко всему каталогу при сбросе ценового диапазона):

* **Размер (габариты композиции)**:
  * `compact` — Компактный (диаметр до 25 см; удобно нести в руках, подходит для ресторанов и свиданий).
  * `standard` — Стандартный (диаметр 30–45 см; классический универсальный формат).
  * `large` — Большой (диаметр от 50 см; объёмный, выразительный букет).
* **Цветовая палитра**:
  * `tender` — Нежная / пастельная (пудровый, персиковый, кремовый, пыльно-розовый).
  * `vibrant` — Яркая / контрастная (фуксия, коралл, терракот, солнечный желтый, ягодный).
  * `white` — Монохром / белая (чистый белый, молочный, зелень эвкалипта).
  * `deep` — Тёмная / драматичная (бордо, марсала, сливовый, графитовый акцент).
  * `seasonal` — Сезонная (актуальные акценты текущего времени года).
* **Повод**:
  * `mom` — «Маме» (уютные, стойкие, теплые и душевные сочетания).
  * `friend` — «Подруге» (стильные, трендовые, легкие, воздушные формы).
  * `wife` — «Жене» (чувственные, романтичные, премиальные сорта роз/пионов).
  * `birthday` — «День рождения» (праздничные, заметные, универсальные).
  * `just_because` — «Без повода / Просто так» (ненавязчивые интерьерные композиции).
* **Быстрая готовность**:
  * `ready_today=1` («Можно сегодня») — фильтрует позиции, доступные к сборке и передаче курьеру в течение 30–90 минут из цветов в текущей витрине/холодильнике.

### 1.3. Логика комбинирования и URL
* Фильтры сериализуются в чистые Query-параметры:  
  `GET /catalog?budget=3500-5500&size=standard&palette=tender&occasion=mom&ready_today=1`
* **Правило связки**:
  * Разные группы параметров соединяются через логическое **`AND`** (бюджет 3500–5500 И размер «стандартный» И повод «маме»).
  * Внутри групп `palette` и `occasion` поддерживается множественный выбор через `IN` (логическое **`OR`**), например: `?palette=tender&palette=white`.
* **Сортировка**: по умолчанию — сначала рекомендуемые / хиты (`sort=popular`), опционально — по возрастанию/убыванию цены (`sort=price_asc`, `sort=price_desc`).

---

## 2. Модель данных SQLite

Схема нормализована для разделения сущностей букетов, тегов (поводы, палитры, размеры) и входящих клиентских заявок. Используется целостность внешних ключей (`PRAGMA foreign_keys = ON;`).

### 2.1. Диаграмма сущностей (ERD)

```
┌────────────────────────┐         ┌────────────────────────┐
│        bouquets        │         │          tags          │
├────────────────────────┤         ├────────────────────────┤
│ id (PK)                │         │ id (PK)                │
│ slug (UNIQUE)          │         │ group_type             │
│ title                  │         │ slug (UNIQUE)          │
│ description            │         │ name                   │
│ price                  │         │ sort_order             │
│ is_price_from          │         └───────────┬────────────┘
│ size_code              │                     │
│ dimensions             │                     │
│ lead_time_hours        │                     │
│ is_ready_today         │                     │
│ is_active              │                     │
│ sort_order             │                     │
│ created_at             │                     │
└───────────┬────────────┘                     │
            │ 1                                │ 1
            │                                  │
            │ N                                │ N
┌───────────┴────────────┐         ┌───────────┴────────────┐
│     bouquet_photos     │         │      bouquet_tags      │
├────────────────────────┤         ├────────────────────────┤
│ id (PK)                │         │ bouquet_id (FK, PK)    │
│ bouquet_id (FK)        │         │ tag_id (FK, PK)        │
│ image_path             │         └────────────────────────┘
│ alt_text               │
│ is_cover               │
│ sort_order             │
└────────────────────────┘
            │ 1
            │
            │ 0..N
┌───────────┴────────────┐
│        requests        │
├────────────────────────┤
│ id (PK)                │
│ bouquet_id (FK, NULL)  │
│ custom_reference_info  │
│ budget_amount          │
│ budget_range           │
│ size_code              │
│ palette                │
│ occasion               │
│ delivery_date          │
│ delivery_time_slot     │
│ customer_name          │
│ customer_phone         │
│ delivery_type          │
│ delivery_address       │
│ comment                │
│ telegram_message_id    │
│ telegram_status        │
│ status                 │
│ created_at             │
└────────────────────────┘
```

### 2.2. DDL-описание таблиц на SQLite Dialect

```sql
PRAGMA foreign_keys = ON;

-- 1. Справочник тегов (поводы, палитра, маркеры)
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_type TEXT NOT NULL CHECK (group_type IN ('occasion', 'palette', 'feature')),
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0
);

-- 2. Каталог букетов
CREATE TABLE bouquets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    price INTEGER NOT NULL CHECK (price >= 0),         -- Базовая цена в рублях
    is_price_from BOOLEAN NOT NULL DEFAULT 0,         -- 1 = "цена от", 0 = фиксированная цена
    size_code TEXT NOT NULL CHECK (size_code IN ('compact', 'standard', 'large')),
    dimensions TEXT,                                  -- Пример: "35x45 см"
    lead_time_hours INTEGER NOT NULL DEFAULT 2,       -- Срок подготовки/сборки в часах
    is_ready_today BOOLEAN NOT NULL DEFAULT 1,        -- 1 = доступен сегодня, 0 = предзаказ
    is_active BOOLEAN NOT NULL DEFAULT 1,             -- Видимость на сайте
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 3. Связка букетов с тегами (Many-to-Many)
CREATE TABLE bouquet_tags (
    bouquet_id INTEGER NOT NULL REFERENCES bouquets(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (bouquet_id, tag_id)
);

-- 4. Фотографии букетов (галерея)
CREATE TABLE bouquet_photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bouquet_id INTEGER NOT NULL REFERENCES bouquets(id) ON DELETE CASCADE,
    image_path TEXT NOT NULL,                         -- Относительный путь: /static/uploads/bouquets/b1_01.webp
    alt_text TEXT,
    is_cover BOOLEAN NOT NULL DEFAULT 0,              -- 1 = главное фото для каталога
    sort_order INTEGER NOT NULL DEFAULT 0
);

-- 5. Заявки клиентов (входящие лиды)
CREATE TABLE requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bouquet_id INTEGER REFERENCES bouquets(id) ON DELETE SET NULL, -- NULL при сборке "Свой букет"
    custom_reference_info TEXT,                                     -- Пожелания, если заказ не из каталога
    budget_amount INTEGER,                                          -- Точная сумма (руб.), если выбрана
    budget_range TEXT,                                              -- Диапазон бюджета ("3500-5500")
    size_code TEXT CHECK (size_code IN ('compact', 'standard', 'large') OR size_code IS NULL),
    palette TEXT,                                                   -- Название выбранной палитры
    occasion TEXT,                                                  -- Повод заказа
    delivery_date TEXT NOT NULL,                                    -- Дата: YYYY-MM-DD
    delivery_time_slot TEXT NOT NULL,                               -- Пример: "10:00-12:00" или "Как можно скорее"
    customer_name TEXT,                                             -- Имя заказчика
    customer_phone TEXT NOT NULL,                                   -- Номер в формате +7XXXXXXXXXX
    delivery_type TEXT NOT NULL DEFAULT 'delivery' CHECK (delivery_type IN ('delivery', 'pickup')),
    delivery_address TEXT,                                          -- Адрес доставки (если не самовывоз)
    comment TEXT,                                                   -- Текст для записки / пожелания флористу
    telegram_message_id INTEGER,                                    -- ID сообщения в TG (для ответа и трекинга)
    telegram_status TEXT NOT NULL DEFAULT 'pending' CHECK (telegram_status IN ('pending', 'sent', 'failed')),
    status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'confirmed', 'in_work', 'done', 'cancelled')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для фильтрации и выборок
CREATE INDEX idx_bouquets_price ON bouquets(price);
CREATE INDEX idx_bouquets_size ON bouquets(size_code);
CREATE INDEX idx_bouquets_ready_active ON bouquets(is_active, is_ready_today);
CREATE INDEX idx_bouquet_tags_tag ON bouquet_tags(tag_id);
CREATE INDEX idx_bouquet_photos_bouquet ON bouquet_photos(bouquet_id, is_cover);
CREATE INDEX idx_requests_status_created ON requests(status, created_at DESC);
```

---

## 3. Поля формы заявки → Telegram

Форма заявки решает две задачи:
1. Заказ конкретного букета из карточки каталога (параметры букета подставляются автоматически).
2. Заказ через мастер «Собрать свой букет» (клиент задаёт параметры с нуля).

### 3.1. Таблица сопоставления полей формы, БД и Telegram-сообщения

| № | Поле в веб-форме | HTML Input / Валидация | Колонка таблицы `requests` | Тип в SQLite | Вывод в сообщении Telegram |
|---|---|---|---|---|---|
| 1 | **Букет / Референс** | Скрытый `bouquet_id` (INT) или текстовое описание референса при сборке | `bouquet_id` + `custom_reference_info` | `INTEGER` (FK) / `TEXT` | `💐 Букет:` Название + ссылка на сайт **или** `Сборка по параметрам` |
| 2 | **Бюджет** | Числовое поле или выбор диапазона (`radio`/`select`) | `budget_amount` / `budget_range` | `INTEGER` / `TEXT` | `💰 Бюджет:` Фиксированная цена букета или выбранная вилка (напр. *5 500 – 10 000 ₽*) |
| 3 | **Размер** | Переключатель `compact` / `standard` / `large` | `size_code` | `TEXT` | `📏 Размер:` *Компактный (S)* / *Стандартный (M)* / *Большой (L)* |
| 4 | **Палитра** | Выпадающий список / чипсы палитр | `palette` | `TEXT` | `🎨 Палитра:` *Нежная / пастельная* |
| 5 | **Повод** | Выбор повода (`mom`, `wife`, `friend` и др.) | `occasion` | `TEXT` | `🎉 Повод:` *Маме* / *Жене* / *Без повода* |
| 6 | **Дата и время** | `input type="date"` + `select` временного интервала | `delivery_date` + `delivery_time_slot` | `TEXT` + `TEXT` | `📅 Дата и время:` *24.10.2026, 14:00–16:00* (или *Сегодня к 18:00*) |
| 7 | **Телефон клиента** | `input type="tel"` с маской `+7 (999) 999-99-99` (E.164) | `customer_phone` | `TEXT NOT NULL` | `📞 Телефон:` `+79991234567` (кликабельная ссылка `tel:`) |
| 8 | **Имя клиента** | `input type="text"` (опционально) | `customer_name` | `TEXT` | `👤 Клиент:` *Иван* |
| 9 | **Тип получения** | `radio`: Доставка / Самовывоз | `delivery_type` + `delivery_address` | `TEXT` + `TEXT` | `🚗 Доставка:` *ул. Ленина, д. 12, кв. 45* **или** `Самовывоз из салона` |
| 10| **Комментарий** | `textarea` (текст записки, пожелания по составу) | `comment` | `TEXT` | `📝 Записка / Комментарий:` *«С днем рождения, любимая мамочка!»* |

---

### 3.2. Шаблон сообщения для Telegram-бота

Сообщение отправляется менеджеру салона в HTML-разметке сразу после успешной транзакции в SQLite:

```html
🌸 <b>НОВАЯ ЗАЯВКА #LF-{{ request_id }}</b>
───────────────
{% if bouquet_title %}
💐 <b>Букет:</b> <a href="{{ base_url }}/catalog/{{ bouquet_slug }}">{{ bouquet_title }}</a>
{% else %}
💐 <b>Тип:</b> Индивидуальная сборка («Собрать свой»)
{% endif %}
💰 <b>Бюджет:</b> {{ budget_display }} ₽
📏 <b>Размер:</b> {{ size_display }}
🎨 <b>Палитра:</b> {{ palette_display }}
🎉 <b>Повод:</b> {{ occasion_display }}
───────────────
📅 <b>Когда:</b> {{ delivery_date }} (интервал: {{ delivery_time_slot }})
🚗 <b>Получение:</b> {{ delivery_type_display }}{% if delivery_address %}: {{ delivery_address }}{% endif %}
───────────────
👤 <b>Клиент:</b> {{ customer_name | default("Не указано", true) }}
📞 <b>Телефон:</b> <a href="tel:{{ customer_phone }}">{{ customer_phone }}</a>
{% if comment %}
💬 <b>Комментарий / Записка:</b>
<i>«{{ comment }}»</i>
{% endif %}
───────────────
⏰ <i>Создано: {{ created_at_formatted }}</i>
```

#### Пример реального сообщения в Telegram:
```
🌸 НОВАЯ ЗАЯВКА #LF-1048
───────────────
💐 Букет: Пыльная роза & Эвкалипт (M)
💰 Бюджет: 6 800 ₽
📏 Размер: Стандартный (M)
🎨 Палитра: Нежная / пастельная
🎉 Повод: Маме
───────────────
📅 Когда: 24.10.2026 (интервал: 12:00–14:00)
🚗 Доставка: г. Москва, ул. Арбат, д. 15, кв. 22
───────────────
👤 Клиент: Евгения
📞 Телефон: +7 (916) 123-45-67
💬 Комментарий / Записка:
«Мамуля, спасибо за тепло! С твоим днем!»
───────────────
⏰ Создано: 23.10.2026 18:45
```

---

## 4. Каркас FastAPI-роутов

Архитектура построена на серверном рендеринге шаблонов Jinja2 для SEO и мгновенной загрузки каталога, а отправка формы заявки реализована через асинхронный POST-эндпоинт с Pydantic-валидацией.

### 4.1. Карта эндпоинтов

| HTTP Метод | URL Путь | Функция-обработчик | Назначение и возвращаемый результат |
|---|---|---|---|
| `GET` | `/` | `route_home` | **Главная страница**: входные карточки выбора бюджета, блок «Можно сегодня», преимущества салона. Возвращает `index.html`. |
| `GET` | `/catalog` | `route_catalog` | **Каталог с фасетными фильтрами**: фильтрация по `budget`, `size`, `palette`, `occasion`, `ready_today`, пагинация. Возвращает `catalog.html`. |
| `GET` | `/catalog/{slug}` | `route_bouquet_detail` | **Детальная карточка букета**: галерея фотографий, состав, срок сборки, быстрая кнопка «Заказать в 1 клик». Возвращает `bouquet_detail.html`. |
| `GET` | `/builder` (или `/custom`) | `route_custom_builder` | **Интерактивный подборщик «Собрать свой»**: пошаговый выбор бюджета, палитры, размера и повода без привязки к конкретному фото. Возвращает `builder.html`. |
| `POST` | `/api/requests` | `route_create_request` | **Приём заявки**: валидация Pydantic-модели, сохранение в таблицу `requests`, неблокирующая отправка в Telegram Bot API. Возвращает JSON `{"status": "ok", "request_id": 1048}`. |
| `GET` | `/order/success/{request_id}` | `route_order_success` | **Экран благодарности**: статус заявки, напоминание о звонке/сообщении флориста в течение 10–15 минут. Возвращает `success.html`. |
| `GET` | `/health` | `route_health` | **Служебный healthcheck**: проверка доступности SQLite и статуса сервиса. Возвращает JSON `{"status": "healthy"}`. |

---

### 4.2. Спецификация серверного кода (`app/main.py`)

```python
from datetime import date
from typing import Optional
from fastapi import FastAPI, Depends, Request, Form, HTTPException, Query, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator
import re

app = FastAPI(title="Love Flower Website API", version="1.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ─── PYDANTIC СХЕМЫ ВАЛИДАЦИИ ────────────────────────────────────────────────

class BouquetFilterParams(BaseModel):
    budget: Optional[str] = None          # '0-3500', '3500-5500', '5500-10000', '10000-15000', '15000-plus'
    size: Optional[str] = None            # 'compact', 'standard', 'large'
    palette: Optional[str] = None         # 'tender', 'vibrant', 'white', 'deep', 'seasonal'
    occasion: Optional[str] = None        # 'mom', 'friend', 'wife', 'birthday', 'just_because'
    ready_today: Optional[bool] = False   # True = только в наличии сегодня
    sort: Optional[str] = "popular"       # 'popular', 'price_asc', 'price_desc'


class LeadRequestSchema(BaseModel):
    bouquet_id: Optional[int] = None
    custom_reference_info: Optional[str] = None
    budget_range: Optional[str] = None
    budget_amount: Optional[int] = None
    size_code: Optional[str] = None
    palette: Optional[str] = None
    occasion: Optional[str] = None
    delivery_date: str = Field(..., description="Формат YYYY-MM-DD")
    delivery_time_slot: str = Field(..., example="14:00-16:00")
    customer_name: Optional[str] = Field(None, max_length=100)
    customer_phone: str = Field(..., example="+79161234567")
    delivery_type: str = Field("delivery", pattern="^(delivery|pickup)$")
    delivery_address: Optional[str] = None
    comment: Optional[str] = Field(None, max_length=1000)

    @field_validator("customer_phone")
    @classmethod
    def clean_and_validate_phone(cls, v: str) -> str:
        digits = re.sub(r"\D", "", v)
        if len(digits) == 11 and digits[0] in ("7", "8"):
            digits = "7" + digits[1:]
        elif len(digits) == 10:
            digits = "7" + digits
        else:
            raise ValueError("Некорректный формат телефона РФ")
        return f"+{digits}"


# ─── РОУТЫ СТРАНИЦ (JINJA2 HTML) ─────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse, summary="Главная страница")
async def get_home_page(request: Request):
    """Отображает вход по бюджету и витрину экспресс-доставки."""
    # Получение подборки хитов и категорий бюджетов из SQLite
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/catalog", response_class=HTMLResponse, summary="Каталог букетов")
async def get_catalog_page(
    request: Request,
    budget: Optional[str] = Query(None),
    size: Optional[str] = Query(None),
    palette: Optional[str] = Query(None),
    occasion: Optional[str] = Query(None),
    ready_today: Optional[bool] = Query(False),
    sort: Optional[str] = Query("popular"),
):
    """Каталог с фильтрами по бюджету, размеру, палитре, поводу и срочности."""
    filters = BouquetFilterParams(
        budget=budget, size=size, palette=palette,
        occasion=occasion, ready_today=ready_today, sort=sort
    )
    # Запрос в SQLite: SELECT * FROM bouquets WHERE ... с джойнами тегов
    return templates.TemplateResponse("catalog.html", {"request": request, "filters": filters})


@app.get("/catalog/{slug}", response_class=HTMLResponse, summary="Карточка букета")
async def get_bouquet_detail(request: Request, slug: str):
    """Карточка отдельного букета с фотогалереей и формой заказа."""
    # SELECT * FROM bouquets WHERE slug = :slug AND is_active = 1
    return templates.TemplateResponse("bouquet_detail.html", {"request": request, "slug": slug})


@app.get("/builder", response_class=HTMLResponse, summary="Подборщик 'Собрать свой'")
async def get_custom_builder(request: Request):
    """Пошаговый подбор букета по бюджету, палитре и поводу под индивидуальный заказ."""
    return templates.TemplateResponse("custom_builder.html", {"request": request})


@app.get("/order/success/{request_id}", response_class=HTMLResponse, summary="Страница подтверждения")
async def get_order_success(request: Request, request_id: int):
    """Экран с подтверждением приёма заказа и таймером ожидания звонка."""
    return templates.TemplateResponse("success.html", {"request": request, "request_id": request_id})


# ─── РОУТЫ ПРИЁМА ДАННЫХ И TELEGRAM API ──────────────────────────────────────

@app.post("/api/requests", response_class=JSONResponse, summary="Создание заявки")
async def create_lead_request(payload: LeadRequestSchema):
    """
    1. Валидация входных данных.
    2. Сохранение заявки в SQLite (requests).
    3. Асинхронная отправка форматированного уведомления в Telegram Bot API.
    4. Обновление статуса отправки в базе данных.
    """
    # 1. Запись в SQLite -> request_id
    request_id = 1048  # db.insert_request(payload)

    # 2. Асинхронный вызов Telegram Bot API (httpx.AsyncClient -> sendMessage)
    # telegram_status = await send_telegram_notification(request_id, payload)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"success": True, "request_id": request_id, "redirect_url": f"/order/success/{request_id}"}
    )


@app.get("/health", summary="Healthcheck")
async def health_check():
    """Проверка доступности сервиса и соединения с SQLite."""
    return {"status": "ok", "service": "love-flower-api"}
```

---

## 5. Открытые технические вопросы и риски

Краткий перечень вопросов, требующих согласования с владелицей салона (Евгенией Кучерявой) до начала вёрстки и интеграции:

1. **Режим доставки и географические зоны**:
   * *Вопрос:* Доставка осуществляется только по фиксированному городу или включая пригород/область?
   * *Риск:* Если клиент вводит адрес за пределами стандартной зоны доставки, менеджеру придётся вручную пересогласовывать стоимость курьера.
   * *Решение для MVP:* Добавить в форме выбор: «Доставка по городу (рассчитает менеджер)» / «Самовывоз из салона (бесплатно)».

2. **Отказоустойчивость Telegram-уведомлений**:
   * *Риск:* При блокировках, сетевых тайм-аутах или сбоях на стороне Telegram Bot API заявка клиента может не дойти до флориста вовремя, а сайт без корзины зависит от скорости реакции на 100%.
   * *Решение:* Заявка **всегда** сначала гарантированно фиксируется в SQLite со статусом `telegram_status = 'pending'`. Фоновая задача (FastAPI BackgroundTasks / лёгкий retry-механизм) повторяет отправку при ошибке 3 раза с интервалом в 10 секунд. Дополнительно — логирование всех лидов в локальный файл журнала.

3. **Маршрутизация Telegram-сообщений**:
   * *Вопрос:* Уведомления должны приходить в личные сообщения Евгении или в групповой рабочий чат флористов/курьеров?
   * *Рекомендация:* Использовать закрытую группу Telegram с ботом. Менеджер, забирающий букет в работу, нажимает inline-кнопку «Взял в работу @username», чтобы избежать дублирования звонков клиенту.

4. **Актуализация каталога и статуса «Можно сегодня»**:
   * *Риск:* В салоне постоянно меняется фактический остаток срезки в холодильнике. Если букет помечен как «Можно сегодня», а цветка нет, возникает негатив клиента при звонке.
   * *Решение для MVP:* На первом этапе без полноценной админки предусмотреть минимальную веб-страницу или Telegram-команду для бота, позволяющую одной кнопкой переключать флаг `is_ready_today` для популярных артикулов.

5. **Сезонность сортов и дисклеймер соответствия**:
   * *Риск:* Клиент ожидает 100% совпадение букета с фотографией на сайте, однако живой цветок зависит от партии и сезона.
   * *Решение:* Обязательный лаконичный дисклеймер под кнопкой отправки заявки: *«Цветы — живой материал. Авторский состав может незначительно отличаться по оттенку и фактуре при сохранении общей цветовой гаммы, объема и настроения букета»*.

6. **Соответствие 152-ФЗ (Персональные данные)**:
   * *Требование:* Форма собирает имя, телефон и адрес доставки.
   * *Решение:* Под формой обязательно размещается чекбокс (или надпись под кнопкой) со ссылкой: *«Нажимая кнопку, вы соглашаетесь с Политикой обработки персональных данных»*. Текст базовой оферты/политики должен быть доступен по адресу `/privacy`.
