PRAGMA foreign_keys = ON;

-- 1. Справочник тегов (поводы, палитра, маркеры)
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_type TEXT NOT NULL CHECK (group_type IN ('occasion', 'palette', 'feature')),
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0
);

-- 2. Каталог букетов
CREATE TABLE IF NOT EXISTS bouquets (
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
CREATE TABLE IF NOT EXISTS bouquet_tags (
    bouquet_id INTEGER NOT NULL REFERENCES bouquets(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (bouquet_id, tag_id)
);

-- 4. Фотографии букетов (галерея)
CREATE TABLE IF NOT EXISTS bouquet_photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bouquet_id INTEGER NOT NULL REFERENCES bouquets(id) ON DELETE CASCADE,
    image_path TEXT NOT NULL,                         -- Относительный путь: /static/images/bouquets/b1.svg
    alt_text TEXT,
    is_cover BOOLEAN NOT NULL DEFAULT 0,              -- 1 = главное фото для каталога
    sort_order INTEGER NOT NULL DEFAULT 0
);

-- 5. Заявки клиентов (входящие лиды)
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bouquet_id INTEGER REFERENCES bouquets(id) ON DELETE SET NULL, -- NULL при заказе без букета
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
    customer_telegram TEXT,                                         -- Ник или телефон в Telegram клиента
    delivery_type TEXT NOT NULL DEFAULT 'delivery' CHECK (delivery_type IN ('delivery', 'pickup')),
    delivery_address TEXT,                                          -- Адрес доставки (если не самовывоз)
    comment TEXT,                                                   -- Текст для записки / пожелания флористу
    telegram_message_id INTEGER,                                    -- ID сообщения в TG
    telegram_status TEXT NOT NULL DEFAULT 'pending' CHECK (telegram_status IN ('pending', 'sent', 'failed')),
    status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'confirmed', 'in_work', 'done', 'cancelled')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для фильтрации и выборок
CREATE INDEX IF NOT EXISTS idx_bouquets_price ON bouquets(price);
CREATE INDEX IF NOT EXISTS idx_bouquets_size ON bouquets(size_code);
CREATE INDEX IF NOT EXISTS idx_bouquets_ready_active ON bouquets(is_active, is_ready_today);
CREATE INDEX IF NOT EXISTS idx_bouquet_tags_tag ON bouquet_tags(tag_id);
CREATE INDEX IF NOT EXISTS idx_bouquet_photos_bouquet ON bouquet_photos(bouquet_id, is_cover);
CREATE INDEX IF NOT EXISTS idx_requests_status_created ON requests(status, created_at DESC);
