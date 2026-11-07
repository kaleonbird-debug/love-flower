"""
Генератор стильных SVG-иллюстраций букетов для LoveFlower.
Создаёт визуально гармоничные карточки букетов с цветовыми палитрами и ботанической графикой.
"""

from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent.parent / "static" / "images" / "bouquets"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ITEMS = [
    {
        "filename": "b1.svg",
        "title": "Белый комплимент",
        "palette_tag": "МОНОХРОМ / БЕЛАЯ",
        "bg_top": "#FBFBF9",
        "bg_bot": "#EFEFEA",
        "accent": "#5A7263",
        "accent_light": "#FFFFFF",
        "petal_stroke": "#3D483F",
        "glow": "rgba(255, 255, 255, 0.9)",
        "theme": "white"
    },
    {
        "filename": "b2.svg",
        "title": "Утренний рассвет",
        "palette_tag": "НЕЖНАЯ / ПАСТЕЛЬНАЯ",
        "bg_top": "#FFF7F2",
        "bg_bot": "#FBE6DC",
        "accent": "#DE8F75",
        "accent_light": "#FFEFE8",
        "petal_stroke": "#7E4937",
        "glow": "rgba(254, 230, 220, 0.9)",
        "theme": "peach"
    },
    {
        "filename": "b3.svg",
        "title": "Розовая карамель",
        "palette_tag": "НЕЖНАЯ / ПАСТЕЛЬНАЯ",
        "bg_top": "#FCF2F4",
        "bg_bot": "#F4D6DF",
        "accent": "#D17088",
        "accent_light": "#FFE4EB",
        "petal_stroke": "#7A3546",
        "glow": "rgba(253, 218, 227, 0.9)",
        "theme": "rose"
    },
    {
        "filename": "b4.svg",
        "title": "Ягодный сорбет",
        "palette_tag": "ЯРКАЯ / СОЧНАЯ",
        "bg_top": "#FFF0F4",
        "bg_bot": "#FDC5D4",
        "accent": "#E63964",
        "accent_light": "#FF8DA9",
        "petal_stroke": "#6E132A",
        "glow": "rgba(255, 180, 200, 0.9)",
        "theme": "berry"
    },
    {
        "filename": "b5.svg",
        "title": "Пыльная роза & Эвкалипт",
        "palette_tag": "ФИРМЕННАЯ НЕЖНАЯ",
        "bg_top": "#F6F0F2",
        "bg_bot": "#E5D4DA",
        "accent": "#9E6B7A",
        "accent_light": "#D8BAC3",
        "petal_stroke": "#522C38",
        "glow": "rgba(230, 210, 218, 0.9)",
        "theme": "dusty_rose"
    },
    {
        "filename": "b6.svg",
        "title": "Солнечный полдень",
        "palette_tag": "ЯРКАЯ / СОЧНАЯ",
        "bg_top": "#FFFBEB",
        "bg_bot": "#FEE685",
        "accent": "#D97706",
        "accent_light": "#FDE68A",
        "petal_stroke": "#78350F",
        "glow": "rgba(254, 240, 138, 0.9)",
        "theme": "sun"
    },
    {
        "filename": "b7.svg",
        "title": "Винный бархат",
        "palette_tag": "ТЁМНАЯ / ДРАМАТИЧНАЯ",
        "bg_top": "#2D1B22",
        "bg_bot": "#180C11",
        "accent": "#9E2A4B",
        "accent_light": "#D84A73",
        "petal_stroke": "#FF99B5",
        "glow": "rgba(158, 42, 75, 0.4)",
        "theme": "wine"
    },
    {
        "filename": "b8.svg",
        "title": "Сезонный ветивер",
        "palette_tag": "СЕЗОННАЯ / АВТОРСКАЯ",
        "bg_top": "#F7F8F4",
        "bg_bot": "#E1E6D8",
        "accent": "#657A57",
        "accent_light": "#CBD7C1",
        "petal_stroke": "#35422D",
        "glow": "rgba(215, 225, 205, 0.9)",
        "theme": "seasonal"
    },
    {
        "filename": "b9.svg",
        "title": "Королевский пион",
        "palette_tag": "ПРЕМИУМ ПАСТЕЛЬ",
        "bg_top": "#FBF3F6",
        "bg_bot": "#ECCFD9",
        "accent": "#C95F81",
        "accent_light": "#F8D4E2",
        "petal_stroke": "#69253B",
        "glow": "rgba(245, 205, 220, 0.9)",
        "theme": "peony"
    },
    {
        "filename": "b10.svg",
        "title": "Изумрудный монохром",
        "palette_tag": "МОНОХРОМ / АРХИТЕКТУРА",
        "bg_top": "#F4F7F5",
        "bg_bot": "#DCE6E0",
        "accent": "#2D5A46",
        "accent_light": "#FFFFFF",
        "petal_stroke": "#193629",
        "glow": "rgba(255, 255, 255, 0.95)",
        "theme": "emerald"
    },
    {
        "filename": "b11.svg",
        "title": "Гранд Гармония",
        "palette_tag": "ГРАНД / ЭКСКЛЮЗИВ",
        "bg_top": "#F9F4FA",
        "bg_bot": "#E6D4E8",
        "accent": "#8A5694",
        "accent_light": "#DFC5E6",
        "petal_stroke": "#4A2454",
        "glow": "rgba(235, 215, 240, 0.9)",
        "theme": "grand"
    },
    {
        "filename": "b12.svg",
        "title": "Драматичная полночь",
        "palette_tag": "ТЁМНАЯ / ДРАМАТИЧНАЯ",
        "bg_top": "#201B24",
        "bg_bot": "#0F0B12",
        "accent": "#734380",
        "accent_light": "#B884C6",
        "petal_stroke": "#E4C0F0",
        "glow": "rgba(115, 67, 128, 0.4)",
        "theme": "midnight"
    }
]

def make_svg(item):
    is_dark = "ДРАМАТИЧНАЯ" in item["palette_tag"] or item["theme"] in ("wine", "midnight")
    badge_bg = "rgba(255,255,255,0.15)" if is_dark else "rgba(0,0,0,0.06)"
    badge_text = "#FFFFFF" if is_dark else "#222222"
    sub_text = "#A098A5" if is_dark else "#777777"
    title_text = "#FFFFFF" if is_dark else "#111111"
    ribbon_color = item["accent"]

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 720" width="100%" height="100%">
  <defs>
    <linearGradient id="bg_grad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{item['bg_top']}"/>
      <stop offset="100%" stop-color="{item['bg_bot']}"/>
    </linearGradient>
    <radialGradient id="bloom_glow" cx="50%" cy="45%" r="45%">
      <stop offset="0%" stop-color="{item['accent_light']}" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="{item['accent_light']}" stop-opacity="0"/>
    </radialGradient>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="12" stdDeviation="18" flood-opacity="0.12"/>
    </filter>
  </defs>

  <!-- Canvas Background -->
  <rect width="600" height="720" fill="url(#bg_grad)"/>

  <!-- Subtle Floral Glow -->
  <circle cx="300" cy="330" r="230" fill="url(#bloom_glow)"/>

  <!-- Aesthetic Framing Border -->
  <rect x="24" y="24" width="552" height="672" fill="none" stroke="{title_text}" stroke-width="1" stroke-opacity="0.15"/>
  <rect x="30" y="30" width="540" height="660" fill="none" stroke="{title_text}" stroke-width="0.5" stroke-opacity="0.1"/>

  <!-- Botanical Bouquet Illustration -->
  <g id="bouquet" filter="url(#shadow)" transform="translate(300, 340)">
    <!-- Stems wrapping & Kraft wrap -->
    <path d="M-45 130 L-70 70 L70 70 L45 130 Z" fill="{badge_bg}" stroke="{item['petal_stroke']}" stroke-width="1.5" stroke-opacity="0.4"/>
    <path d="M-15 130 L-5 210 M15 130 L5 210 M0 130 L0 220" stroke="{item['petal_stroke']}" stroke-width="3" stroke-linecap="round" opacity="0.6"/>
    <!-- Wrap tie ribbon -->
    <rect x="-50" y="125" width="100" height="8" rx="4" fill="{ribbon_color}"/>

    <!-- Foliage / Leaves -->
    <path d="M-110 50 C-170 30 -160 -40 -100 -20 C-60 -5 -70 30 -110 50 Z" fill="{item['accent']}" opacity="0.75"/>
    <path d="M110 50 C170 30 160 -40 100 -20 C60 -5 70 30 110 50 Z" fill="{item['accent']}" opacity="0.75"/>
    <path d="M-70 -70 C-120 -120 -80 -170 -30 -130 C-10 -110 -30 -70 -70 -70 Z" fill="{item['accent']}" opacity="0.6"/>
    <path d="M70 -70 C120 -120 80 -170 30 -130 C10 -110 30 -70 70 -70 Z" fill="{item['accent']}" opacity="0.6"/>

    <!-- Left Floral Bloom -->
    <g transform="translate(-75, 10)">
      <circle cx="0" cy="0" r="54" fill="{item['accent_light']}" stroke="{item['petal_stroke']}" stroke-width="2"/>
      <circle cx="-10" cy="-6" r="38" fill="none" stroke="{item['petal_stroke']}" stroke-width="1.8"/>
      <circle cx="5" cy="5" r="24" fill="none" stroke="{item['petal_stroke']}" stroke-width="1.8"/>
      <circle cx="0" cy="0" r="10" fill="{item['accent']}"/>
    </g>

    <!-- Right Floral Bloom -->
    <g transform="translate(75, 10)">
      <circle cx="0" cy="0" r="54" fill="{item['accent_light']}" stroke="{item['petal_stroke']}" stroke-width="2"/>
      <circle cx="10" cy="-6" r="38" fill="none" stroke="{item['petal_stroke']}" stroke-width="1.8"/>
      <circle cx="-5" cy="5" r="24" fill="none" stroke="{item['petal_stroke']}" stroke-width="1.8"/>
      <circle cx="0" cy="0" r="10" fill="{item['accent']}"/>
    </g>

    <!-- Upper Center Bloom -->
    <g transform="translate(0, -65)">
      <circle cx="0" cy="0" r="62" fill="{item['accent_light']}" stroke="{item['petal_stroke']}" stroke-width="2"/>
      <!-- Multi-layered peony petals -->
      <path d="M-40 0 C-40 -35 40 -35 40 0 C30 30 -30 30 -40 0 Z" fill="none" stroke="{item['petal_stroke']}" stroke-width="1.8"/>
      <path d="M-25 -10 C-25 -25 25 -25 25 -10 C20 15 -20 15 -25 -10 Z" fill="none" stroke="{item['petal_stroke']}" stroke-width="1.8"/>
      <circle cx="0" cy="-6" r="8" fill="{item['accent']}"/>
    </g>

    <!-- Central Focal Big Bloom -->
    <g transform="translate(0, 15)">
      <circle cx="0" cy="0" r="70" fill="{item['accent_light']}" stroke="{item['petal_stroke']}" stroke-width="2.2"/>
      <path d="M-50 -10 C-50 -45 50 -45 50 -10 C40 38 -40 38 -50 -10 Z" fill="none" stroke="{item['petal_stroke']}" stroke-width="1.8"/>
      <path d="M-32 -5 C-32 -30 32 -30 32 -5 C25 25 -25 25 -32 -5 Z" fill="none" stroke="{item['petal_stroke']}" stroke-width="1.8"/>
      <circle cx="0" cy="-3" r="14" fill="{item['accent']}"/>
      <circle cx="0" cy="-3" r="6" fill="{item['accent_light']}"/>
    </g>

    <!-- Eucalyptus branchlets and sprigs -->
    <g stroke="{item['petal_stroke']}" stroke-width="1.5" stroke-linecap="round" fill="none">
      <path d="M-100 -20 Q-130 -60 -150 -110"/>
      <circle cx="-135" cy="-65" r="9" fill="{item['accent']}" opacity="0.8"/>
      <circle cx="-145" cy="-95" r="7" fill="{item['accent']}" opacity="0.8"/>

      <path d="M100 -20 Q130 -60 150 -110"/>
      <circle cx="135" cy="-65" r="9" fill="{item['accent']}" opacity="0.8"/>
      <circle cx="145" cy="-95" r="7" fill="{item['accent']}" opacity="0.8"/>
    </g>
  </g>

  <!-- Top Palette Tag Badge -->
  <g transform="translate(50, 52)">
    <rect width="180" height="26" rx="13" fill="{badge_bg}"/>
    <text x="90" y="17" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
          font-size="9" font-weight="700" letter-spacing="1.5" fill="{badge_text}" text-anchor="middle">
      {item['palette_tag']}
    </text>
  </g>

  <!-- Brand Signature Monogram -->
  <g transform="translate(515, 52)">
    <circle cx="18" cy="13" r="14" fill="none" stroke="{title_text}" stroke-width="1" stroke-opacity="0.3"/>
    <text x="18" y="17" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
          font-size="9" font-weight="700" letter-spacing="1" fill="{title_text}" text-anchor="middle" opacity="0.7">
      LF
    </text>
  </g>

  <!-- Lower Title Card -->
  <g transform="translate(50, 620)">
    <text x="0" y="24" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
          font-size="22" font-weight="700" letter-spacing="0.5" fill="{title_text}">
      {item['title']}
    </text>
    <text x="0" y="44" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
          font-size="11" font-weight="500" letter-spacing="1.5" fill="{sub_text}">
      ЛАВФЛОВЕР • АВТОРСКИЙ СБОРНЫЙ БУКЕТ
    </text>
  </g>
</svg>
"""

def main():
    for item in ITEMS:
        path = OUT_DIR / item["filename"]
        svg_content = make_svg(item)
        path.write_text(svg_content.strip(), encoding="utf-8")
        print(f"Generated {path.name}")

if __name__ == "__main__":
    main()
