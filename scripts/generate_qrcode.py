#!/usr/bin/env python3
"""生成桜探記推广用二维码（高容错 + 中心 LOGO + 装饰边框）。"""
from __future__ import annotations

import math
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFilter, ImageFont

URL = "https://www.kudou-shinichi.cn/Sakura/"
ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "frontend" / "public"
OUT = PUBLIC / "sakura-site-qrcode.png"
FAVICON_ICO = PUBLIC / "favicon.ico"
FAVICON_SVG = PUBLIC / "favicon.svg"

INK = (61, 44, 54, 255)


def _point_in_rotated_petal(px: float, py: float, theta_deg: float) -> bool:
    """与 favicon.svg 一致：椭圆心在 (12,5.5)、rx=2.6、ry=4.5，绕 (12,12) 旋转 theta_deg（度，SVG 顺时针为正）。"""
    rad = math.radians(theta_deg)
    vx, vy = px - 12.0, py - 12.0
    # 逆变换：把用户坐标变回旋转前的局部坐标
    a = vx * math.cos(rad) - vy * math.sin(rad)
    b = vx * math.sin(rad) + vy * math.cos(rad)
    return (a / 2.6) ** 2 + ((6.5 + b) / 4.5) ** 2 <= 1.0


def render_favicon_raster(out_px: int, supersample: int = 8) -> Image.Image:
    """按 favicon.svg 几何光栅化（与 index.html 引用的图标一致）。"""
    s = supersample
    w = h = out_px * s
    scale = w / 24.0
    pink = (217, 80, 111, 255)
    cream = (250, 247, 242, 255)
    pink_center = (217, 80, 111, int(255 * 0.6))

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    pix = img.load()
    thetas = (0.0, 72.0, 144.0, 216.0, 288.0)

    for iy in range(h):
        py = (iy + 0.5) / scale
        for ix in range(w):
            px = (ix + 0.5) / scale
            if any(_point_in_rotated_petal(px, py, t) for t in thetas):
                pix[ix, iy] = pink

    # 花心圆（后绘，盖住花瓣交界）
    cx, cy = int(12 * scale), int(12 * scale)
    r2 = int(2.5 * scale)
    r1 = max(1, int(1.2 * scale))
    draw = ImageDraw.Draw(img)
    draw.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=cream)
    inner = Image.new("RGBA", (2 * r1 + 2, 2 * r1 + 2), (0, 0, 0, 0))
    ImageDraw.Draw(inner).ellipse([0, 0, 2 * r1 + 1, 2 * r1 + 1], fill=pink_center)
    img.alpha_composite(inner, (cx - r1 - 1, cy - r1 - 1))

    return img.resize((out_px, out_px), Image.Resampling.LANCZOS)


def load_center_logo(size: int) -> Image.Image:
    if FAVICON_ICO.is_file():
        im = Image.open(FAVICON_ICO).convert("RGBA")
        return im.resize((size, size), Image.Resampling.LANCZOS)
    if not FAVICON_SVG.is_file():
        raise FileNotFoundError(f"缺少 {FAVICON_SVG} 或 {FAVICON_ICO}")
    return render_favicon_raster(size)


def gradient_background(w: int, h: int) -> Image.Image:
    top = (255, 228, 236)
    bottom = (250, 247, 242)
    img = Image.new("RGB", (w, h), bottom)
    px = img.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        c = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        for x in range(w):
            px[x, y] = c
    return img


def main() -> None:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=14,
        border=2,
    )
    qr.add_data(URL)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#3D2C36", back_color="#FFFFFF").convert("RGBA")

    logo_max = int(qr_img.width * 0.22)
    logo = load_center_logo(logo_max)
    pad = int(logo_max * 0.18)
    plate = Image.new("RGBA", (logo.width + 2 * pad, logo.height + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(plate)
    d.rounded_rectangle(
        [0, 0, plate.width - 1, plate.height - 1],
        radius=max(6, pad // 2),
        fill=(255, 255, 255, 255),
    )
    plate.alpha_composite(logo, (pad, pad))
    lx = (qr_img.width - plate.width) // 2
    ly = (qr_img.height - plate.height) // 2
    qr_img.alpha_composite(plate, (lx, ly))

    margin = 72
    title_h = 44
    foot_h = 42
    cw = qr_img.width + 2 * margin
    ch = qr_img.height + 2 * margin + title_h + foot_h
    canvas = gradient_background(cw, ch)
    card = Image.new("RGBA", (cw, ch - title_h - foot_h + 20), (0, 0, 0, 0))
    shadow = Image.new("RGBA", card.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    cr = 28
    sd.rounded_rectangle([8, 12, card.width - 1 + 8, card.height - 1 + 12], radius=cr, fill=(60, 40, 50, 55))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    card.alpha_composite(shadow, (0, 0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([0, 0, card.width - 1, card.height - 1], radius=cr, fill=(255, 255, 255, 255))
    ox = (card.width - qr_img.width) // 2
    oy = margin // 2 + 8
    card.alpha_composite(qr_img, (ox, oy))

    canvas_rgba = canvas.convert("RGBA")
    paste_y = title_h - 10
    canvas_rgba.alpha_composite(card, (0, paste_y))

    draw = ImageDraw.Draw(canvas_rgba)
    title = "桜探記"
    _font_paths = [
        ("/System/Library/Fonts/Hiragino Sans GB.ttc", 0),
        ("/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc", 0),
    ]

    def _load(sz: int) -> ImageFont.FreeTypeFont:
        for path, idx in _font_paths:
            try:
                return ImageFont.truetype(path, sz, index=idx)
            except OSError:
                continue
        return ImageFont.load_default()

    font_title = _load(34)
    font_foot = _load(16)
    tw, _ = draw.textbbox((0, 0), title, font=font_title)[2:]
    draw.text(((cw - tw) / 2, 18), title, fill=INK[:3], font=font_title)

    foot = "kudou-shinichi.cn/Sakura"
    fw, _ = draw.textbbox((0, 0), foot, font=font_foot)[2:]
    draw.text(((cw - fw) / 2, paste_y + card.height + 12), foot, fill=(150, 130, 140), font=font_foot)

    final = canvas_rgba.convert("RGB")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    final.save(OUT, "PNG", optimize=True)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
