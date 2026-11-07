import sqlite3

def seed_data(conn: sqlite3.Connection):
    cur = conn.cursor()

    # 1. Tags
    tags = [
        # group_type, slug, name, sort_order
        ('palette', 'tender', 'Нежная / пастельная', 10),
        ('palette', 'vibrant', 'Яркая / сочная', 20),
        ('palette', 'white', 'Монохром / белая', 30),
        ('palette', 'deep', 'Тёмная / драматичная', 40),
        ('palette', 'seasonal', 'Сезонная', 50),

        ('occasion', 'mom', 'Маме', 10),
        ('occasion', 'wife', 'Жене', 20),
        ('occasion', 'friend', 'Подруге', 30),
        ('occasion', 'birthday', 'День рождения', 40),
        ('occasion', 'just_because', 'Без повода', 50),
    ]

    cur.executemany(
        "INSERT OR IGNORE INTO tags (group_type, slug, name, sort_order) VALUES (?, ?, ?, ?)",
        tags
    )

    # Dictionary tag_slug -> tag_id
    cur.execute("SELECT slug, id FROM tags")
    tag_map = dict(cur.fetchall())

    # 2. Bouquets
    bouquets = [
        {
            "slug": "belyj-kompliment",
            "title": "Белый комплимент",
            "description": "Элегантный моно-букет из стойких белоснежных диантусов и ароматного эвкалипта Cinerea в дизайнерской матовой бумаге. Идеально для утончённого знака внимания.",
            "price": 2900,
            "is_price_from": 0,
            "size_code": "compact",
            "dimensions": "диаметр 22 см, высота 35 см",
            "lead_time_hours": 1,
            "is_ready_today": 1,
            "is_active": 1,
            "sort_order": 1,
            "image": "/static/images/bouquets/b1.svg",
            "tags": ["white", "just_because", "friend"]
        },
        {
            "slug": "utrennij-rassvet",
            "title": "Утренний рассвет",
            "description": "Компактная воздушная композиция с кустовыми персиковыми розами, нежной маттиолой и веточками оксипеталума. Удобно держать в руках на прогулке или свидании.",
            "price": 3400,
            "is_price_from": 0,
            "size_code": "compact",
            "dimensions": "диаметр 24 см, высота 38 см",
            "lead_time_hours": 1,
            "is_ready_today": 1,
            "is_active": 1,
            "sort_order": 2,
            "image": "/static/images/bouquets/b2.svg",
            "tags": ["tender", "friend", "just_because"]
        },
        {
            "slug": "rozovaya-karamel",
            "title": "Розовая карамель",
            "description": "Уютный и тёплый сборный букет из пионовидных роз Candy X-Pression, кремовой эустомы и эвкалипта. Универсальный хит для поздравления мамы или коллеги.",
            "price": 4200,
            "is_price_from": 0,
            "size_code": "standard",
            "dimensions": "диаметр 35 см, высота 45 см",
            "lead_time_hours": 2,
            "is_ready_today": 1,
            "is_active": 1,
            "sort_order": 3,
            "image": "/static/images/bouquets/b3.svg",
            "tags": ["tender", "mom", "birthday"]
        },
        {
            "slug": "yagodnyj-sorbet",
            "title": "Ягодный сорбет",
            "description": "Энергичный букет с сочными коралловыми розами, малиновым гиперикумом и лесной зеленью. Дарит улыбку и праздничное настроение с первого взгляда.",
            "price": 4800,
            "is_price_from": 0,
            "size_code": "standard",
            "dimensions": "диаметр 38 см, высота 45 см",
            "lead_time_hours": 2,
            "is_ready_today": 1,
            "is_active": 1,
            "sort_order": 4,
            "image": "/static/images/bouquets/b4.svg",
            "tags": ["vibrant", "birthday", "friend"]
        },
        {
            "slug": "pylnaya-roza-evkalipt",
            "title": "Пыльная роза & Эвкалипт",
            "description": "Фирменный фаворит салона: французские садовые розы пыльно-пудрового оттенка, фактурная гортензия и серебристый эвкалипт. Роскошная фактура и тонкий аромат.",
            "price": 6800,
            "is_price_from": 0,
            "size_code": "standard",
            "dimensions": "диаметр 42 см, высота 50 см",
            "lead_time_hours": 2,
            "is_ready_today": 1,
            "is_active": 1,
            "sort_order": 5,
            "image": "/static/images/bouquets/b5.svg",
            "tags": ["tender", "mom", "wife"]
        },
        {
            "slug": "solnechnyj-polden",
            "title": "Солнечный полдень",
            "description": "Яркий букет в солнечной гамме: садовые подсолнухи, оранжевые кустовые розы и ветвистый рускус в минималистичной крафтовой упаковке.",
            "price": 7200,
            "is_price_from": 0,
            "size_code": "standard",
            "dimensions": "диаметр 40 см, высота 50 см",
            "lead_time_hours": 2,
            "is_ready_today": 1,
            "is_active": 1,
            "sort_order": 6,
            "image": "/static/images/bouquets/b6.svg",
            "tags": ["vibrant", "birthday", "mom"]
        },
        {
            "slug": "vinnyj-barhat",
            "title": "Винный бархат",
            "description": "Глубокая драматичная гамма: темные розы сорта Red Naomi, бордовые каллы и декоративные ягоды. Смелый, чувственный букет для особых признаний.",
            "price": 8900,
            "is_price_from": 0,
            "size_code": "large",
            "dimensions": "диаметр 50 см, высота 60 см",
            "lead_time_hours": 3,
            "is_ready_today": 1,
            "is_active": 1,
            "sort_order": 7,
            "image": "/static/images/bouquets/b7.svg",
            "tags": ["deep", "wife", "birthday"]
        },
        {
            "slug": "sezonnyj-vetiver",
            "title": "Сезонный ветивер",
            "description": "Авторская сезонная подборка флориста: редкие текстуры, сезонные полевые акценты и свежесрезанные ветки. Каждый букет собирается индивидуально под настроение дня.",
            "price": 6200,
            "is_price_from": 1,
            "size_code": "standard",
            "dimensions": "диаметр 38 см, высота 48 см",
            "lead_time_hours": 3,
            "is_ready_today": 0,
            "is_active": 1,
            "sort_order": 8,
            "image": "/static/images/bouquets/b8.svg",
            "tags": ["seasonal", "friend", "just_because"]
        },
        {
            "slug": "korolevskij-pion",
            "title": "Королевский пион",
            "description": "Пышное облако отборных пионов сорта Сара Бернар в сочетании с белыми садовыми розами. Премиальный объем и восхитительное раскрытие каждого бутона.",
            "price": 12500,
            "is_price_from": 0,
            "size_code": "large",
            "dimensions": "диаметр 55 см, высота 60 см",
            "lead_time_hours": 2,
            "is_ready_today": 1,
            "is_active": 1,
            "sort_order": 9,
            "image": "/static/images/bouquets/b9.svg",
            "tags": ["tender", "wife", "birthday"]
        },
        {
            "slug": "izumrudnyj-monohrom",
            "title": "Изумрудный монохром",
            "description": "Строгая графичная эстетика белого и глубокого зелёного: белые антуриумы, розы Мондиаль, аспарагус и эвкалипт парвифолия. Архитектурный стиль для ценителей минимализма.",
            "price": 13800,
            "is_price_from": 0,
            "size_code": "large",
            "dimensions": "диаметр 52 см, высота 65 см",
            "lead_time_hours": 3,
            "is_ready_today": 1,
            "is_active": 1,
            "sort_order": 10,
            "image": "/static/images/bouquets/b10.svg",
            "tags": ["white", "wife", "birthday"]
        },
        {
            "slug": "grand-garmoniya",
            "title": "Гранд Гармония",
            "description": "Впечатляющая авторская корзина из 55+ отборных цветов пастельной палитры: гортензии, пионовидные розы, озотамнус и ланугиноза. Настоящий вау-эффект для ключевых событий.",
            "price": 18500,
            "is_price_from": 1,
            "size_code": "large",
            "dimensions": "диаметр 65 см, высота 70 см",
            "lead_time_hours": 4,
            "is_ready_today": 1,
            "is_active": 1,
            "sort_order": 11,
            "image": "/static/images/bouquets/b11.svg",
            "tags": ["tender", "wife", "birthday", "mom"]
        },
        {
            "slug": "dramatichnaya-polnoch",
            "title": "Драматичная полночь",
            "description": "Эксклюзивная композиция в тёмных тонах: чёрные каллы, бархатные темно-красные пионы и графитовая зелень в дизайнерской шляпной коробке ручной работы.",
            "price": 16500,
            "is_price_from": 0,
            "size_code": "large",
            "dimensions": "диаметр 60 см, высота 65 см",
            "lead_time_hours": 4,
            "is_ready_today": 0,
            "is_active": 1,
            "sort_order": 12,
            "image": "/static/images/bouquets/b12.svg",
            "tags": ["deep", "wife"]
        }
    ]

    for b in bouquets:
        cur.execute("""
            INSERT OR REPLACE INTO bouquets (
                slug, title, description, price, is_price_from,
                size_code, dimensions, lead_time_hours, is_ready_today,
                is_active, sort_order
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            b["slug"], b["title"], b["description"], b["price"], b["is_price_from"],
            b["size_code"], b["dimensions"], b["lead_time_hours"], b["is_ready_today"],
            b["is_active"], b["sort_order"]
        ))
        bouquet_id = cur.lastrowid

        # Фото
        cur.execute("""
            INSERT OR REPLACE INTO bouquet_photos (
                bouquet_id, image_path, alt_text, is_cover, sort_order
            ) VALUES (?, ?, ?, 1, 0)
        """, (bouquet_id, b["image"], b["title"]))

        # Теги
        for tag_slug in b["tags"]:
            tag_id = tag_map.get(tag_slug)
            if tag_id:
                cur.execute("""
                    INSERT OR IGNORE INTO bouquet_tags (bouquet_id, tag_id)
                    VALUES (?, ?)
                """, (bouquet_id, tag_id))

    conn.commit()
    print("Database successfully seeded with 12 bouquets and tags!")


if __name__ == "__main__":
    try:
        from database.db import get_db_connection, init_db
    except ImportError:
        from db import get_db_connection, init_db
    init_db(force=True)
