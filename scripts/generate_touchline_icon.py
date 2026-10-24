import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_touchline_icon():
    S = 2048  # High-definition master canvas
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    
    # -------------------------------------------------------------
    # 1. DROP SHADOW for outer squircle (Depth / 3D floating effect)
    # -------------------------------------------------------------
    pad = 120
    sq_box = [pad, pad, S - pad, S - pad]
    sq_r = 440
    
    s_img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(s_img)
    # Downward offset + soft blur matching modern OS iconography
    s_draw.rounded_rectangle([sq_box[0], sq_box[1] + 55, sq_box[2], sq_box[3] + 55], radius=sq_r, fill=(0, 0, 0, 160))
    s_img = s_img.filter(ImageFilter.GaussianBlur(radius=45))
    img.alpha_composite(s_img)
    
    # -------------------------------------------------------------
    # 2. OUTER SQUIRCLE: Football Manager Signature Royal Violet
    # Vibrant, deep, luxurious gradient: #8b5cf6 -> #6366f1 -> #4338ca
    # -------------------------------------------------------------
    sq_img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    grad = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(grad)
    
    top_col = (139, 92, 246)   # #8b5cf6 Vibrant FM Violet
    mid_col = (99, 102, 241)   # #6366f1 Electric Indigo
    bot_col = (67, 56, 202)    # #4338ca Deep Tactical Violet
    
    for y in range(S):
        t = y / S
        if t < 0.5:
            f = t / 0.5
            r = int(top_col[0] * (1 - f) + mid_col[0] * f)
            g = int(top_col[1] * (1 - f) + mid_col[1] * f)
            b = int(top_col[2] * (1 - f) + mid_col[2] * f)
        else:
            f = (t - 0.5) / 0.5
            r = int(mid_col[0] * (1 - f) + bot_col[0] * f)
            g = int(mid_col[1] * (1 - f) + bot_col[1] * f)
            b = int(mid_col[2] * (1 - f) + bot_col[2] * f)
        g_draw.line([(0, y), (S, y)], fill=(r, g, b, 255))
        
    # Stadium illumination sheen (top-center glassmorphism lighting)
    sheen = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    shd = ImageDraw.Draw(sheen)
    cx, cy = S // 2, int(S * 0.22)
    max_d = 950
    for r in range(max_d, 0, -30):
        alpha = int(48 * (1 - r / max_d)**1.5)
        shd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, alpha))
    grad.alpha_composite(sheen)
    
    sq_mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(sq_mask).rounded_rectangle(sq_box, radius=sq_r, fill=255)
    sq_img.paste(grad, (0, 0), sq_mask)
    
    # Premium glass rim highlight (inner 12px bevel)
    rim = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(rim).rounded_rectangle(sq_box, radius=sq_r, outline=(255, 255, 255, 110), width=12)
    sq_img.alpha_composite(rim)
    img.alpha_composite(sq_img)
    
    # -------------------------------------------------------------
    # 3. WHITE DOCUMENT CARD (Dog-ear folded corner, clean contrast)
    # -------------------------------------------------------------
    doc_w = 1180
    doc_h = 1440
    dx0 = (S - doc_w) // 2
    dy0 = (S - doc_h) // 2 - 20
    dx1 = dx0 + doc_w
    dy1 = dy0 + doc_h
    doc_r = 80
    fold_s = 200
    
    # Card drop shadow
    c_sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(c_sh).rounded_rectangle([dx0, dy0 + 35, dx1, dy1 + 35], radius=doc_r, fill=(0, 0, 0, 160))
    c_sh = c_sh.filter(ImageFilter.GaussianBlur(radius=38))
    img.alpha_composite(c_sh)
    
    doc_img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    c_mask = Image.new("L", (S, S), 0)
    cm_draw = ImageDraw.Draw(c_mask)
    cm_draw.rounded_rectangle([dx0, dy0, dx1, dy1], radius=doc_r, fill=255)
    cm_draw.polygon([(dx1 - fold_s, dy0 - 5), (dx1 + 5, dy0 - 5), (dx1 + 5, dy0 + fold_s)], fill=0)
    
    c_fill = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cfd = ImageDraw.Draw(c_fill)
    for y in range(dy0, dy1 + 1):
        prog = (y - dy0) / doc_h
        val = int(255 - prog * 8)
        cfd.line([(dx0, y), (dx1, y)], fill=(val, val, val, 255))
    doc_img.paste(c_fill, (0, 0), c_mask)
    
    # Dog-ear flap
    fl_img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    fld = ImageDraw.Draw(fl_img)
    fld.polygon([(dx1 - fold_s, dy0), (dx1 - fold_s, dy0 + fold_s), (dx1, dy0 + fold_s)], fill=(225, 230, 236, 255))
    fld.line([(dx1 - fold_s, dy0), (dx1, dy0 + fold_s)], fill=(195, 200, 208, 255), width=8)
    
    f_sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(f_sh).polygon([(dx1 - fold_s, dy0 + fold_s), (dx1 - fold_s - 45, dy0 + fold_s + 45), (dx1, dy0 + fold_s + 45)], fill=(0, 0, 0, 70))
    f_sh = f_sh.filter(ImageFilter.GaussianBlur(radius=15))
    doc_img.alpha_composite(f_sh)
    doc_img.alpha_composite(fl_img)
    
    # -------------------------------------------------------------
    # 4. MINI TACTICAL PITCH (Generous white border for maximum contrast)
    # -------------------------------------------------------------
    px_pad = int(doc_w * 0.10)
    px0 = dx0 + px_pad
    px1 = dx1 - px_pad
    py0 = dy0 + 130
    py1 = dy1 - 380
    pr = 35
    
    p_mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(p_mask).rounded_rectangle([px0, py0, px1, py1], radius=pr, fill=255)
    
    p_surf = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    psd = ImageDraw.Draw(p_surf)
    
    # Alternating grass stripes (7 stripes, fresh lawn emerald)
    n_stripes = 7
    s_h = (py1 - py0) / n_stripes
    for i in range(n_stripes):
        sy0 = int(py0 + i * s_h)
        sy1 = int(py0 + (i + 1) * s_h)
        col = (16, 140, 85, 255) if i % 2 == 0 else (10, 115, 68, 255)
        psd.rectangle([px0, sy0, px1, sy1], fill=col)
        
    # Pitch boundary & tactical markings (crisp bold white lines)
    lw = 14
    lcol = (255, 255, 255, 245)
    margin = 35
    bx0, bx1 = px0 + margin, px1 - margin
    by0, by1 = py0 + margin, py1 - margin
    
    psd.rectangle([bx0, by0, bx1, by1], outline=lcol, width=lw)
    mid_y = (by0 + by1) // 2
    mid_x = (bx0 + bx1) // 2
    psd.line([(bx0, mid_y), (bx1, mid_y)], fill=lcol, width=lw)
    
    cc_r = 135
    psd.ellipse([mid_x - cc_r, mid_y - cc_r, mid_x + cc_r, mid_y + cc_r], outline=lcol, width=lw)
    psd.ellipse([mid_x - 18, mid_y - 18, mid_x + 18, mid_y + 18], fill=lcol)
    
    box_w, box_h = 380, 170
    psd.rectangle([mid_x - box_w // 2, by0, mid_x + box_w // 2, by0 + box_h], outline=lcol, width=lw)
    psd.ellipse([mid_x - 14, by0 + 120 - 14, mid_x + 14, by0 + 120 + 14], fill=lcol)
    psd.arc([mid_x - 85, by0 + 120 - 85, mid_x + 85, by0 + 120 + 85], start=30, end=150, fill=lcol, width=lw)
    
    psd.rectangle([mid_x - box_w // 2, by1 - box_h, mid_x + box_w // 2, by1], outline=lcol, width=lw)
    psd.ellipse([mid_x - 14, by1 - 120 - 14, mid_x + 14, by1 - 120 + 14], fill=lcol)
    psd.arc([mid_x - 85, by1 - 120 - 85, mid_x + 85, by1 - 120 + 85], start=210, end=330, fill=lcol, width=lw)
    
    # Attacking tactical arrow
    arrow_pts = []
    for s in range(25):
        u = s / 24.0
        p0 = (mid_x - 200, mid_y + 110)
        p1 = (mid_x - 220, mid_y - 80)
        p2 = (mid_x - 40, by0 + 110)
        ax = (1-u)**2 * p0[0] + 2*(1-u)*u * p1[0] + u**2 * p2[0]
        ay = (1-u)**2 * p0[1] + 2*(1-u)*u * p1[1] + u**2 * p2[1]
        arrow_pts.append((ax, ay))
    for i in range(len(arrow_pts) - 1):
        if (i // 2) % 2 == 0:
            psd.line([arrow_pts[i], arrow_pts[i+1]], fill=(56, 189, 248, 255), width=18)
    htip = arrow_pts[-1]
    psd.polygon([htip, (htip[0] - 44, htip[1] + 38), (htip[0] + 18, htip[1] + 44)], fill=(56, 189, 248, 255))
    
    # Player nodes
    def draw_node(nx, ny, col_ring, col_core, r=42):
        psd.ellipse([nx - r - 8, ny - r - 8, nx + r + 8, ny + r + 8], fill=(0, 0, 0, 80))
        psd.ellipse([nx - r, ny - r, nx + r, ny + r], fill=col_ring, outline=(255, 255, 255, 255), width=9)
        psd.ellipse([nx - r // 2, ny - r // 2, nx + r // 2, ny + r // 2], fill=col_core)

    c_cyan = (14, 165, 233)
    c_gold = (245, 158, 11)
    c_white = (255, 255, 255)
    draw_node(mid_x - 190, by1 - 150, c_cyan, c_white, 38)
    draw_node(mid_x + 190, by1 - 150, c_cyan, c_white, 38)
    draw_node(mid_x - 120, mid_y + 40, c_cyan, c_white, 42)
    draw_node(mid_x + 120, mid_y + 40, c_cyan, c_white, 42)
    draw_node(mid_x - 30, by0 + 110, c_gold, c_white, 48)
    
    doc_img.paste(p_surf, (0, 0), p_mask)
    
    # -------------------------------------------------------------
    # 5. BOTTOM BANNER ("FM 26")
    # Matching the FM signature violet with clean white bold text
    # -------------------------------------------------------------
    b_h = 320
    b_y0 = dy1 - b_h
    b_y1 = dy1
    b_mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(b_mask).rounded_rectangle([dx0, b_y0, dx1, b_y1], radius=doc_r, fill=255)
    b_fill = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    bfd = ImageDraw.Draw(b_fill)
    for y in range(b_y0, b_y1 + 1):
        t = (y - b_y0) / b_h
        r = int(top_col[0] * (1 - t) + bot_col[0] * t)
        g = int(top_col[1] * (1 - t) + bot_col[1] * t)
        b = int(top_col[2] * (1 - t) + bot_col[2] * t)
        bfd.line([(dx0, y), (dx1, y)], fill=(r, g, b, 255))
    bfd.line([(dx0, b_y0), (dx1, b_y0)], fill=(255, 255, 255, 120), width=6)
    doc_img.paste(b_fill, (0, 0), b_mask)
    
    # Typography: "FM 26" in Segoe UI Bold
    font_path = "C:\\Windows\\Fonts\\segoeuib.ttf"
    if not os.path.exists(font_path):
        font_path = "C:\\Windows\\Fonts\\arialbd.ttf"
    font = ImageFont.truetype(font_path, 220)
    text = "FM 26"
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (dx0 + dx1 - tw) // 2
    ty = b_y0 + (b_h - th) // 2 - bbox[1] - 8
    tdd = ImageDraw.Draw(doc_img)
    tdd.text((tx, ty + 8), text, font=font, fill=(0, 0, 0, 110))
    tdd.text((tx, ty), text, font=font, fill=(255, 255, 255, 255))
    
    img.alpha_composite(doc_img)
    return img

if __name__ == "__main__":
    print("Generating Touchline FM26 Master Icon...")
    master = create_touchline_icon()
    
    # Target directory: web
    os.makedirs("web", exist_ok=True)
    
    # 1. Save 1024x1024 and 512x512 high-res PNGs
    img_1024 = master.resize((1024, 1024), Image.Resampling.LANCZOS)
    img_1024.save("web/touchline_1024.png", format="PNG", optimize=True)
    img_1024.save("web/app_icon_1024.png", format="PNG", optimize=True)
    
    img_512 = master.resize((512, 512), Image.Resampling.LANCZOS)
    img_512.save("web/touchline_512.png", format="PNG", optimize=True)
    img_512.save("web/app_icon.png", format="PNG", optimize=True)
    
    # 2. Build multi-resolution ICO with all 10 standard Windows icon sizes
    sizes = [
        (256, 256),
        (128, 128),
        (96, 96),
        (64, 64),
        (48, 48),
        (40, 40),
        (32, 32),
        (24, 24),
        (20, 20),
        (16, 16)
    ]
    
    # Save both touchline.ico and app_icon.ico and favicon.ico
    for target in ["web/touchline.ico", "web/app_icon.ico", "web/favicon.ico"]:
        img_512.save(target, format="ICO", sizes=sizes)
        print(f"Saved: {target} (contains {len(sizes)} resolutions)")
        
    print("Icon generation completed successfully!")
