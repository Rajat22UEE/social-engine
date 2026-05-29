from PIL import Image, ImageDraw, ImageFont
import os


# ── Font Loading ──────────────────────────────────────────────────────────────
_POPPINS_BOLD   = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
_POPPINS_MEDIUM = "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"
_POPPINS_REG    = "/usr/share/fonts/truetype/google-fonts/Poppins-Regular.ttf"
_LIB_BOLD       = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
_LIB_REG        = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


def _font(preferred: str, fallback: str, size: int) -> ImageFont.FreeTypeFont:
    for path in (preferred, fallback, _LIB_BOLD, _LIB_REG, "arial.ttf"):
        if path and os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


# ── Default Colors ──────────────────────────────────────────────────────────
C_NAVY      = (26,  42,  74)    # deep navy – headline
C_GREEN     = (29, 158, 117)    # green – hook card accent
C_DRK_GRN   = (15, 110,  86)    # dark green – hook text
C_LT_GREEN  = (225, 245, 238)   # soft green tint – hook card bg


# ── Template Configurations ───────────────────────────────────────────────────
TEMPLATE_CONFIG = {
    1: {
        "width": 1254, "height": 1254,
        "left_x": 64, "right_x": 1185, "top_y": 350, "footer_y": 1050,
        "headline_size": 90, "hook_size": 48,
        "headline_max_lines": 2, "hook_max_lines": 2,
        "line_spacing": 8, "hook_line_spacing": 18,
    },
    2: {
        "width": 941, "height": 1672,
        "left_x": 50, "right_x": 880, "top_y": 500, "footer_y": 1400,
        "headline_size": 72, "hook_size": 40,
        "headline_max_lines": 2, "hook_max_lines": 2,
        "line_spacing": 8, "hook_line_spacing": 15,
    },
    3: {
        "width": 1200, "height": 628,
        "left_x": 60, "right_x": 1140, "top_y": 100, "footer_y": 500,
        "headline_size": 64, "hook_size": 36,
        "headline_max_lines": 2, "hook_max_lines": 2,
        "line_spacing": 6, "hook_line_spacing": 12,
    },
    4: {
        "width": 1024, "height": 512,
        "left_x": 50, "right_x": 974, "top_y": 80, "footer_y": 420,
        "headline_size": 56, "hook_size": 32,
        "headline_max_lines": 2, "hook_max_lines": 2,
        "line_spacing": 6, "hook_line_spacing": 10,
    },
    5: {
        "width": 1000, "height": 1500,
        "left_x": 55, "right_x": 945, "top_y": 350, "footer_y": 1300,
        "headline_size": 68, "hook_size": 38,
        "headline_max_lines": 2, "hook_max_lines": 2,
        "line_spacing": 8, "hook_line_spacing": 14,
    },
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _wrap(draw, text, font, max_w):
    """Word-wrap text to fit within max_w pixels."""
    words = text.split()
    if not words:
        return []
    lines, cur = [], [words[0]]
    for word in words[1:]:
        candidate = " ".join(cur + [word])
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_w:
            cur.append(word)
        else:
            lines.append(" ".join(cur))
            cur = [word]
    lines.append(" ".join(cur))
    return lines


def _lh(draw, text, font):
    """Return pixel height of a single text line."""
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[3] - bb[1]


def _tw(draw, text, font):
    """Return pixel width of a text string."""
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0]


def _lighten_color(rgb, factor):
    """Lighten a color by blending with white."""
    return tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)


def _darken_color(rgb, factor):
    """Darken a color by blending with black."""
    return tuple(max(0, int(c * (1 - factor))) for c in rgb)


# ── TextOverlay ───────────────────────────────────────────────────────────────

class TextOverlay:
    """
    Renders headline + hook on the template with template-specific positioning.
    Caption, CTA, and hashtags are accepted for API/DB compatibility but
    NOT drawn on the image.
    """

    def __init__(self, template_path: str, template_id: int = 1, canvas_edits: dict = None):
        self.image = Image.open(template_path).convert("RGB")
        self.draw = ImageDraw.Draw(self.image)
        self.canvas_edits = canvas_edits or {}
        
        config = TEMPLATE_CONFIG.get(template_id, TEMPLATE_CONFIG[1])
        self.config = config
        self.content_w = config["right_x"] - config["left_x"]
        
        # Load fonts with optional override sizes from canvas_edits
        headline_size = self.canvas_edits.get('headline_size') or config["headline_size"]
        hook_size = self.canvas_edits.get('hook_size') or config["hook_size"]
        self.f_head = _font(_POPPINS_BOLD, _LIB_BOLD, headline_size)
        self.f_hook = _font(_POPPINS_MEDIUM, _LIB_REG, hook_size)
        
        # Default colors
        self.color_headline = C_NAVY
        self.color_hook_card_bg = _lighten_color(C_NAVY, 0.85)
        self.color_hook_accent = C_GREEN
        self.color_hook_text = _darken_color(C_GREEN, 0.5)
        self.color_accent = C_GREEN

    def _headline(self, text, x, y):
        """Brand-colored headline – single line, centre-aligned."""
        max_lines = self.config["headline_max_lines"]
        lines = _wrap(self.draw, text, self.f_head, self.content_w - 40)[:max_lines]
        if not lines:
            return y

        for ln in lines:
            lw = _tw(self.draw, ln, self.f_head)
            cx = x + (self.content_w - lw) // 2
            self.draw.text((cx, y), ln, font=self.f_head, fill=self.color_headline)
            y += _lh(self.draw, ln, self.f_head) + self.config["line_spacing"]
        return y + 40

    def _hook(self, text, x, y):
        """Hook in a card with accent stripe. Max 2 lines."""
        max_lines = self.config["hook_max_lines"]
        lines = _wrap(self.draw, text, self.f_hook, self.content_w - 60)[:max_lines]
        if not lines:
            return y

        line_h = _lh(self.draw, lines[0], self.f_hook)
        line_spacing = self.config["hook_line_spacing"]
        block_h = len(lines) * (line_h + line_spacing) - line_spacing + 40

        self.draw.rounded_rectangle(
            [x, y, self.config["right_x"], y + block_h],
            radius=12, fill=self.color_hook_card_bg
        )
        self.draw.rounded_rectangle(
            [x, y, x + 8, y + block_h],
            radius=4, fill=self.color_hook_accent
        )

        ty = y + 20
        for ln in lines:
            lw = _tw(self.draw, ln, self.f_hook)
            cx = x + (self.content_w - lw) // 2
            self.draw.text((cx, ty), ln, font=self.f_hook, fill=self.color_hook_text)
            ty += _lh(self.draw, ln, self.f_hook) + line_spacing

        return y + block_h

    def render(self, headline, hook):
        """Render headline + hook on the template image."""
        left_x = self.canvas_edits.get('headline_x') or self.config["left_x"]
        cy = self.canvas_edits.get('headline_y') or self.config["top_y"]

        cy = self._headline(headline, left_x, cy)

        hook_x = self.canvas_edits.get('hook_x') or self.config["left_x"]
        hook_y = self.canvas_edits.get('hook_y') or cy
        self._hook(hook, hook_x, hook_y)

    def save(self, output_path):
        os.makedirs(
            os.path.dirname(output_path) if os.path.dirname(output_path) else ".",
            exist_ok=True
        )
        self.image.save(output_path)


# ── generate_post_image() ─────────────────────────────────────────────────────

def generate_post_image(template_id: int, topic: str,
                        content_data: dict,
                        canvas_edits: dict = None) -> str:
    """
    Generate a post image and save to outputs/.
    Accepts optional canvas_edits for custom text positioning.

    Args:
        template_id  : int       – selects templates/template_{id}.png
        topic        : str       – used in filename
        content_data : dict      – keys: headline, hook, caption, cta, hashtags
        canvas_edits : dict, opt – keys: headline_x/y, hook_x/y, size overrides

    Returns:
        str – relative path to saved image, e.g. "outputs/gen_Topic_1.png"
    """
    template_file = f"templates/template_{template_id}.png"
    output_file = f"outputs/gen_{topic[:8].strip()}_{template_id}.png"

    if not os.path.exists(template_file):
        raise FileNotFoundError(
            f"Template not found: '{template_file}'. "
            f"Place your template PNG at that path."
        )

    overlay = TextOverlay(template_file, template_id, canvas_edits)
    overlay.render(
        headline=content_data.get("headline", ""),
        hook=content_data.get("hook", ""),
    )
    overlay.save(output_file)
    return output_file