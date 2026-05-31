from PIL import Image, ImageDraw, ImageFont
import os

# ── Font Loading ──────────────────────────────────────────────────────────────
_FONT_PATHS = [
    "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
    "/usr/share/fonts/truetype/google-fonts/Poppins-Regular.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "arial.ttf",
]


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in _FONT_PATHS:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


# ── Color Palette ─────────────────────────────────────────────────────────────
C_NAVY       = (26,  42,  74)   # headlines
C_GREEN      = (29, 158, 117)  # hook accent bar
C_DARK_GREEN = (15, 110,  86)  # hook text


# ── Template Configs (Headline + Hook only, full-width layout) ────────────────
TEMPLATE_CONFIGS = {
    # Feed (4:5, 1080x1350)
    1: {
        "width": 1080, "height": 1350,
        "elements": {
            "headline": {
                "x_pct": 0.04, "y_pct": 0.25,       # 4% left, 25% top
                "font_size": 76, "color": C_NAVY,
                "max_lines": 4, "text_width_pct": 0.92,
            },
            "hook": {
                "x_pct": 0.04, "y_pct": 0.38,       # 4% left, 38% top
                "font_size": 44, "color": C_DARK_GREEN,
                "max_lines": 3, "text_width_pct": 0.92,
            },
        }
    },
    # Story (9:16, 1080x1920)
    2: {
        "width": 1080, "height": 1920,
        "elements": {
            "headline": {
                "x_pct": 0.05, "y_pct": 0.25,       # 5% left, 25% top
                "font_size": 60, "color": C_NAVY,
                "max_lines": 3, "text_width_pct": 0.75,
            },
            "hook": {
                "x_pct": 0.05, "y_pct": 0.35,       # 5% left, 35% top
                "font_size": 40, "color": C_DARK_GREEN,
                "max_lines": 4, "text_width_pct": 0.75,
            },
        }
    }
}


# ── Text Helpers ──────────────────────────────────────────────────────────────

def _wrap(draw, text, font, max_w_px):
    """Word-wrap text to fit within max_w_px pixels."""
    words = text.split()
    if not words:
        return []
    lines, cur = [], [words[0]]
    for word in words[1:]:
        candidate = " ".join(cur + [word])
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_w_px:
            cur.append(word)
        else:
            lines.append(" ".join(cur))
            cur = [word]
    lines.append(" ".join(cur))
    return lines


def _text_h(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[3] - bb[1]


def _text_w(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0]


def _lighten(rgb, factor):
    return tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)


# ── TextOverlay (Headline + Hook only, full-width coverage) ───────────────────

class TextOverlay:
    def __init__(self, template_path: str, template_id: int = 1):
        self.image = Image.open(template_path).convert("RGB")
        self.draw = ImageDraw.Draw(self.image)
        self.config = TEMPLATE_CONFIGS.get(template_id, TEMPLATE_CONFIGS[1])
        self.w = self.config["width"]
        self.h = self.config["height"]

    def render(self, headline: str, hook: str):
        """
        Render headline and hook with full-width text layout.
        Each element position is defined as percentage of image dimensions,
        and text fills the available width proportionally.
        """
        cfg = self.config["elements"]

        # ── Headline (full-width, left-aligned, multi-line) ─────────────────
        hl_cfg = cfg.get("headline")
        if headline and hl_cfg:
            x = int(self.w * hl_cfg["x_pct"])
            y = int(self.h * hl_cfg["y_pct"])
            max_w = int(self.w * hl_cfg["text_width_pct"])
            font = _load_font(hl_cfg["font_size"])
            lines = _wrap(self.draw, headline, font, max_w)[:hl_cfg["max_lines"]]
            if lines:
                for ln in lines:
                    self.draw.text((x, y), ln, font=font, fill=hl_cfg["color"])
                    y += _text_h(self.draw, ln, font) + 8
                h_end = y + 20
            else:
                h_end = y

        # ── Hook (full-width, card background with accent bar) ──────────────
        hk_cfg = cfg.get("hook")
        if hook and hk_cfg:
            x = int(self.w * hk_cfg["x_pct"])
            y = max(h_end, int(self.h * hk_cfg["y_pct"]))
            max_w = int(self.w * hk_cfg["text_width_pct"])
            font = _load_font(hk_cfg["font_size"])
            lines = _wrap(self.draw, hook, font, max_w)[:hk_cfg["max_lines"]]
            if lines:
                line_h = _text_h(self.draw, lines[0], font)
                spacing = 10
                block_h = len(lines) * (line_h + spacing) - spacing + 28
                block_w = int(self.w * hk_cfg["text_width_pct"]) + 20

                # Background card
                bg_color = _lighten(C_GREEN, 0.85)
                self.draw.rounded_rectangle(
                    [x, y, x + block_w, y + block_h],
                    radius=12, fill=bg_color
                )
                # Accent bar on left
                self.draw.rounded_rectangle(
                    [x, y, x + 8, y + block_h],
                    radius=4, fill=C_GREEN
                )

                y += 14
                for ln in lines:
                    lw = _text_w(self.draw, ln, font)
                    cx = x + 14 + (block_w - 28 - lw) // 2
                    self.draw.text((cx, y), ln, font=font, fill=hk_cfg["color"])
                    y += _text_h(self.draw, ln, font) + spacing

    def save(self, output_path: str):
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        self.image.save(output_path)


# ── generate_post_image ───────────────────────────────────────────────────────

def generate_post_image(template_id: int, topic: str, content_data: dict) -> str:
    """
    Generate an Instagram post image with headline + hook overlay.

    Args:
        template_id: 1 = Feed (4:5), 2 = Story (9:16)
        topic: used in filename
        content_data: keys: headline, hook (caption and cta are ignored)
    Returns:
        relative path like "outputs/gen_Topic_1.png"
    """
    template_file = f"templates/template_{template_id}.png"
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/gen_{topic[:10].strip()}_{template_id}.png"

    if not os.path.exists(template_file):
        raise FileNotFoundError(f"Template not found: '{template_file}'")

    overlay = TextOverlay(template_file, template_id)
    overlay.render(
        headline=content_data.get("headline", ""),
        hook=content_data.get("hook", ""),
    )
    overlay.save(output_file)
    return output_file