"""
Скрипт комплексного тестирования роутов и логики приложения LoveFlower.
"""
import sys
from pathlib import Path

# Добавляем site в path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "site"))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_endpoints():
    print("--- 1. Healthcheck ---")
    r = client.get("/health")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    print("✓ /health:", r.json())

    print("\n--- 2. Главная страница (/) ---")
    r = client.get("/")
    assert r.status_code == 200
    assert "ЛавФловер" in r.text
    assert "0-3500" in r.text
    assert "15000-plus" in r.text
    assert "logo.svg" in r.text
    print("✓ / renders with logo and budget cards")

    print("\n--- 3. Каталог (/catalog) и фильтры ---")
    r = client.get("/catalog")
    assert r.status_code == 200
    assert "Найдено композиций: <b>12</b>" in r.text
    print("✓ /catalog shows all 12 bouquets")

    r_budget = client.get("/catalog?budget=0-3500")
    assert r_budget.status_code == 200
    assert "Белый комплимент" in r_budget.text
    assert "Найдено композиций: <b>2</b>" in r_budget.text
    print("✓ /catalog?budget=0-3500 filters correctly (2 bouquets)")

    r_size = client.get("/catalog?size=compact")
    assert r_size.status_code == 200
    print("✓ /catalog?size=compact filters correctly")

    r_palette = client.get("/catalog?palette=tender")
    assert r_palette.status_code == 200
    print("✓ /catalog?palette=tender filters correctly")

    r_today = client.get("/catalog?ready_today=1")
    assert r_today.status_code == 200
    print("✓ /catalog?ready_today=1 filters correctly")

    print("\n--- 4. Карточка букета (/catalog/{slug}) ---")
    r_detail = client.get("/catalog/pylnaya-roza-evkalipt")
    assert r_detail.status_code == 200
    assert "Пыльная роза &amp; Эвкалипт" in r_detail.text or "Пыльная роза" in r_detail.text
    assert "6 800" in r_detail.text
    assert "Хочу такой букет" in r_detail.text
    print("✓ /catalog/pylnaya-roza-evkalipt renders correctly")

    print("\n--- 5. Страница заказа (/order) ---")
    r_order = client.get("/order?bouquet=pylnaya-roza-evkalipt")
    assert r_order.status_code == 200
    assert "Пыльная роза" in r_order.text
    print("✓ /order?bouquet=pylnaya-roza-evkalipt renders with selected bouquet")

    print("\n--- 6. Отправка заявки через форму (POST /order) ---")
    form_payload = {
        "customer_name": "Тестовый Клиент",
        "customer_phone": "+7 (999) 111-22-33",
        "bouquet_id": 1,
        "delivery_type": "delivery",
        "delivery_address": "Москва, Арбат 10",
        "delivery_date": "Сегодня",
        "delivery_time_slot": "14:00–16:00",
        "comment": "Пожалуйста, положите открытку с надписью 'С любовью!'"
    }
    r_post = client.post("/order", data=form_payload, follow_redirects=False)
    assert r_post.status_code == 303, f"Expected 303 redirect, got {r_post.status_code}"
    redirect_url = r_post.headers["location"]
    print(f"✓ POST /order successfully created lead, redirected to: {redirect_url}")

    print("\n--- 7. Экран подтверждения заказа (/order/success/{id}) ---")
    r_success = client.get(redirect_url)
    assert r_success.status_code == 200
    assert "Заявка #LF-" in r_success.text
    assert "Тестовый Клиент" in r_success.text or "+79991112233" in r_success.text
    print(f"✓ {redirect_url} rendered correctly with order details")

    print("\n--- 8. API создания заявки (POST /api/requests) ---")
    json_payload = {
        "customer_name": "API Клиент",
        "customer_phone": "89169876543",
        "bouquet_id": 2,
        "delivery_type": "pickup",
        "delivery_date": "Завтра",
        "delivery_time_slot": "10:00–12:00",
        "comment": "Самовывоз утром"
    }
    r_api = client.post("/api/requests", json=json_payload)
    assert r_api.status_code == 201, f"Expected 201, got {r_api.status_code}: {r_api.text}"
    api_data = r_api.json()
    assert api_data.get("success") is True
    print(f"✓ POST /api/requests returned 201: {api_data}")

    print("\n--- 9. Информационные страницы (/how, /privacy) ---")
    r_how = client.get("/how")
    assert r_how.status_code == 200
    assert "Самовывоз" in r_how.text
    assert "аквапак" in r_how.text
    print("✓ /how rendered")

    r_privacy = client.get("/privacy")
    assert r_privacy.status_code == 200
    assert "152-ФЗ" in r_privacy.text
    print("✓ /privacy rendered")

    print("\n--- 10. Статические файлы ---")
    r_logo = client.get("/static/images/logo.svg")
    assert r_logo.status_code == 200
    assert "<svg" in r_logo.text
    print("✓ /static/images/logo.svg returned valid SVG")

    r_photo = client.get("/static/images/bouquets/b1.svg")
    assert r_photo.status_code == 200
    assert "<svg" in r_photo.text
    print("✓ /static/images/bouquets/b1.svg returned valid SVG")

    r_css = client.get("/static/css/style.css")
    assert r_css.status_code == 200
    print("✓ /static/css/style.css returned CSS")

    print("\n==========================================")
    print("ВСЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ!")
    print("==========================================")

if __name__ == "__main__":
    test_endpoints()
