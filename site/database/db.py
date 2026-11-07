import os
import sqlite3
from typing import Any, Dict, List, Optional
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.environ.get("DATABASE_PATH", str(BASE_DIR / "database" / "love_flower.db"))
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(force: bool = False):
    """Инициализирует структуру БД и накатывает сиды при первом запуске."""
    db_file = Path(DB_PATH)
    needs_seed = not db_file.exists() or force or db_file.stat().st_size == 0

    db_file.parent.mkdir(parents=True, exist_ok=True)
    conn = get_db_connection()
    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()

        # Проверим, есть ли уже данные в tags и bouquets
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM bouquets")
        count = cur.fetchone()[0]
        if count == 0:
            try:
                from .seed import seed_data
            except ImportError:
                from database.seed import seed_data
            seed_data(conn)
    finally:
        conn.close()


def get_all_tags() -> Dict[str, List[Dict[str, Any]]]:
    """Возвращает теги, сгруппированные по group_type."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, group_type, slug, name, sort_order FROM tags ORDER BY sort_order ASC")
        rows = cur.fetchall()
        tags_by_group: Dict[str, List[Dict[str, Any]]] = {}
        for r in rows:
            gt = r["group_type"]
            if gt not in tags_by_group:
                tags_by_group[gt] = []
            tags_by_group[gt].append(dict(r))
        return tags_by_group
    finally:
        conn.close()


def get_bouquets(
    budget: Optional[str] = None,
    size: Optional[str] = None,
    palette: Optional[str] = None,
    occasion: Optional[str] = None,
    ready_today: Optional[bool] = False,
    sort: Optional[str] = "popular",
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Фильтрует и возвращает букеты с их обложками и тегами."""
    conn = get_db_connection()
    try:
        query = """
            SELECT DISTINCT
                b.id, b.slug, b.title, b.description, b.price, b.is_price_from,
                b.size_code, b.dimensions, b.lead_time_hours, b.is_ready_today,
                b.is_active, b.sort_order, b.created_at,
                bp.image_path as cover_image, bp.alt_text as cover_alt
            FROM bouquets b
            LEFT JOIN bouquet_photos bp ON b.id = bp.bouquet_id AND bp.is_cover = 1
            LEFT JOIN bouquet_tags bt ON b.id = bt.bouquet_id
            LEFT JOIN tags t ON bt.tag_id = t.id
            WHERE b.is_active = 1
        """
        params: List[Any] = []

        if budget:
            if budget == "0-3500":
                query += " AND b.price <= 3500"
            elif budget == "3500-5500":
                query += " AND b.price >= 3500 AND b.price <= 5500"
            elif budget == "5500-10000":
                query += " AND b.price >= 5500 AND b.price <= 10000"
            elif budget == "10000-15000":
                query += " AND b.price >= 10000 AND b.price <= 15000"
            elif budget == "15000-plus":
                query += " AND b.price >= 15000"

        if size and size in ("compact", "standard", "large"):
            query += " AND b.size_code = ?"
            params.append(size)

        if ready_today:
            query += " AND b.is_ready_today = 1"

        if palette:
            query += " AND b.id IN (SELECT bt2.bouquet_id FROM bouquet_tags bt2 JOIN tags t2 ON bt2.tag_id = t2.id WHERE t2.group_type = 'palette' AND t2.slug = ?)"
            params.append(palette)

        if occasion:
            query += " AND b.id IN (SELECT bt3.bouquet_id FROM bouquet_tags bt3 JOIN tags t3 ON bt3.tag_id = t3.id WHERE t3.group_type = 'occasion' AND t3.slug = ?)"
            params.append(occasion)

        # Сортировка
        if sort == "price_asc":
            query += " ORDER BY b.price ASC, b.id ASC"
        elif sort == "price_desc":
            query += " ORDER BY b.price DESC, b.id ASC"
        else:  # popular
            query += " ORDER BY b.sort_order ASC, b.id ASC"

        if limit:
            query += f" LIMIT {int(limit)}"

        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()

        results = []
        for r in rows:
            item = dict(r)
            # Добавим названия тегов палитры и размера для удобного отображения
            cur.execute("""
                SELECT t.slug, t.name, t.group_type
                FROM tags t
                JOIN bouquet_tags bt ON t.id = bt.tag_id
                WHERE bt.bouquet_id = ?
            """, (item["id"],))
            tags = cur.fetchall()
            item["tags"] = [dict(t) for t in tags]
            item["palette_names"] = [t["name"] for t in tags if t["group_type"] == "palette"]
            item["occasion_names"] = [t["name"] for t in tags if t["group_type"] == "occasion"]
            results.append(item)

        return results
    finally:
        conn.close()


def get_bouquet_by_slug(slug: str) -> Optional[Dict[str, Any]]:
    """Возвращает детальную карточку букета со всеми фото и тегами."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, slug, title, description, price, is_price_from,
                   size_code, dimensions, lead_time_hours, is_ready_today,
                   is_active, sort_order, created_at, updated_at
            FROM bouquets
            WHERE slug = ? AND is_active = 1
        """, (slug,))
        row = cur.fetchone()
        if not row:
            return None

        bouquet = dict(row)

        # Фотографии
        cur.execute("""
            SELECT id, image_path, alt_text, is_cover, sort_order
            FROM bouquet_photos
            WHERE bouquet_id = ?
            ORDER BY is_cover DESC, sort_order ASC
        """, (bouquet["id"],))
        bouquet["photos"] = [dict(p) for p in cur.fetchall()]
        bouquet["cover_image"] = bouquet["photos"][0]["image_path"] if bouquet["photos"] else "/static/images/bouquets/b1.svg"

        # Теги
        cur.execute("""
            SELECT t.id, t.group_type, t.slug, t.name
            FROM tags t
            JOIN bouquet_tags bt ON t.id = bt.tag_id
            WHERE bt.bouquet_id = ?
            ORDER BY t.sort_order ASC
        """, (bouquet["id"],))
        tags = [dict(t) for t in cur.fetchall()]
        bouquet["tags"] = tags
        bouquet["palette_names"] = [t["name"] for t in tags if t["group_type"] == "palette"]
        bouquet["occasion_names"] = [t["name"] for t in tags if t["group_type"] == "occasion"]

        return bouquet
    finally:
        conn.close()


def get_bouquet_by_id(bouquet_id: int) -> Optional[Dict[str, Any]]:
    """Возвращает букет по id."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT slug FROM bouquets WHERE id = ?", (bouquet_id,))
        row = cur.fetchone()
        if not row:
            return None
        return get_bouquet_by_slug(row["slug"])
    finally:
        conn.close()


def create_request(payload: Dict[str, Any]) -> int:
    """Сохраняет новую клиентскую заявку в таблице requests."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO requests (
                bouquet_id, custom_reference_info, budget_amount, budget_range,
                size_code, palette, occasion, delivery_date, delivery_time_slot,
                customer_name, customer_phone, delivery_type, delivery_address,
                comment, telegram_status, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', 'new')
        """, (
            payload.get("bouquet_id"),
            payload.get("custom_reference_info"),
            payload.get("budget_amount"),
            payload.get("budget_range"),
            payload.get("size_code"),
            payload.get("palette"),
            payload.get("occasion"),
            payload.get("delivery_date"),
            payload.get("delivery_time_slot"),
            payload.get("customer_name"),
            payload.get("customer_phone"),
            payload.get("delivery_type", "delivery"),
            payload.get("delivery_address"),
            payload.get("comment"),
        ))
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def update_request_telegram_status(
    request_id: int,
    status: str,
    message_id: Optional[int] = None
) -> None:
    """Обновляет статус отправки в Telegram."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE requests
            SET telegram_status = ?, telegram_message_id = ?
            WHERE id = ?
        """, (status, message_id, request_id))
        conn.commit()
    finally:
        conn.close()


def get_request_by_id(request_id: int) -> Optional[Dict[str, Any]]:
    """Возвращает заявку по id."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT r.*, b.title as bouquet_title, b.slug as bouquet_slug, b.price as bouquet_price
            FROM requests r
            LEFT JOIN bouquets b ON r.bouquet_id = b.id
            WHERE r.id = ?
        """, (request_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
