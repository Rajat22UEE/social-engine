from PIL import Image, ImageDraw, ImageFont
import os

# ── Canvas & Template Constants ───────────────────────────────────────────────
CANVAS_SIZE = 1254          # Template is 1254×1254 px (square)

# ── Content Zone ──────────────────────────────────────────────────────────────
# Template safe zones (from kyma-AI template):
#   Top section full width (x:64→1185) from y:228 onward
#   Footer starts at y:930 - don't draw below this
LEFT_X      = 64
RIGHT_X     = 1185
TOP_Y       = 228
FOOTER_Y    = 930
CONTENT_W   = RIGHT_X - LEFT_X    # 1121 px

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


# ── Brand Colors ──────────────────────────────────────────────────────────────
C_NAVY      = (26,  42,  74)    # deep navy – headline
C_GREEN     = (29, 158, 117)    # kyma-AI brand green – hook card accent
C_DRK_GRN  = (15, 110,  86)    # dark green – hook text
C_LT_GREEN  = (225, 245, 238)   # soft green tint – hook card bg


# ── Helpers ───────────────────────────────────────────────────────────────────

def _wrap(draw: ImageDraw.ImageDraw, text: str,
          font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
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


def _lh(draw: ImageDraw.ImageDraw, text: str,
        font: ImageFont.FreeTypeFont) -> int:
    """Return pixel height of a single text line."""
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[3] - bb[1]


def _tw(draw: ImageDraw.ImageDraw, text: str,
        font: ImageFont.FreeTypeFont) -> int:
    """Return pixel width of a text string."""
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0]


# ── TextOverlay ───────────────────────────────────────────────────────────────

class TextOverlay:
    """
    Renders ONLY headline + hook on the template – big, bold, eye-catching.
    Caption, CTA, and hashtags are accepted for API/DB compatibility but
    NOT drawn on the image.
    """

    def __init__(self, template_path: str):
        self.image = Image.open(template_path).convert("RGB")
        self.draw  = ImageDraw.Draw(self.image)
        
        # Large fonts – headline dominates, hook is bold but slightly smaller
        self.f_head = _font(_POPPINS_BOLD,   _LIB_BOLD,  112)  # massive headline
        self.f_hook = _font(_POPPINS_MEDIUM, _LIB_REG,    56)  # bold hook

    def _headline(self, text: str, x: int, y: int) -> int:
        """
        Huge navy headline (112pt) – max 2 lines, centre-aligned.
        Returns Y below the last line.
        """
        lines = _wrap(self.draw, text, self.f_head, CONTENT_W - 80)[:2]
        if not lines:
            return y

        for ln in lines:
            # Centre this line horizontally
            lw = _tw(self.draw, ln, self.f_head)
            cx = x + (CONTENT_W - lw) // 2
            self.draw.text((cx, y), ln, font=self.f_head, fill=C_NAVY)
            y += _lh(self.draw, ln, self.f_head) + 10
        return y + 60

    def _hook(self, text: str, x: int, y: int) -> int:
        """
        Hook (56pt) in a soft-green full-width card with a bold green left stripe.
        Max 4 lines to fill vertical space.
        Returns Y below the block.
        """
        lines = _wrap(self.draw, text, self.f_hook, CONTENT_W - 100)[:4]
        if not lines:
            return y

        line_h  = _lh(self.draw, lines[0], self.f_hook)
        block_h = len(lines) * (line_h + 20) - 20 + 50   # padding top+bottom

        # Full-width card
        self.draw.rounded_rectangle(
            [x, y, RIGHT_X, y + block_h],
            radius=16, fill=C_LT_GREEN
        )
        # Bold left accent stripe
        self.draw.rounded_rectangle(
            [x, y, x + 10, y + block_h],
            radius=6, fill=C_GREEN
        )

        ty = y + 25
        for ln in lines:
            # Centre each line within the card
            lw = _tw(self.draw, ln, self.f_hook)
            cx = x + (CONTENT_W - lw) // 2
            self.draw.text((cx, ty), ln, font=self.f_hook, fill=C_DRK_GRN)
            ty += _lh(self.draw, ln, self.f_hook) + 20

        return y + block_h

    # ── Public API ────────────────────────────────────────────────────────────

    def render(self, topic: str, headline: str, hook: str,
               caption: str, cta: str, hashtags: list[str]) -> None:
        """
        Only headline + hook are rendered. All other params are accepted
        for API/DB compatibility but NOT drawn on the image.
        """
        cy = TOP_Y

        # ── Headline (big, bold, centred) ─────────────────────────────────
        cy = self._headline(headline, LEFT_X, cy)

        # ── Hook (card with accent stripe – fills remaining space) ────────
        self._hook(hook, LEFT_X, cy)

    def save(self, output_path: str) -> None:
        os.makedirs(
            os.path.dirname(output_path) if os.path.dirname(output_path) else ".",
            exist_ok=True
        )
        self.image.save(output_path)


# ── generate_post_image() ─────────────────────────────────────────────────────

def generate_post_image(template_id: int, topic: str,
                        content_data: dict) -> str:
    """
    Generate a post image and save to outputs/.
    Signature identical to original – main.py needs no changes.

    Args:
        template_id  : int  – selects templates/template_{id}.png
        topic        : str  – used in filename
        content_data : dict – keys: headline, hook, caption, cta, hashtags

    Returns:
        str – relative path to saved image, e.g. "outputs/gen_Topic_1.png"
    """
    template_file = f"templates/template_{template_id}.png"
    output_file   = f"outputs/gen_{topic[:8].strip()}_{template_id}.png"

    if not os.path.exists(template_file):
        raise FileNotFoundError(
            f"Template not found: '{template_file}'. "
            f"Place your template PNG at that path."
        )

    overlay = TextOverlay(template_file)
    overlay.render(
        topic    = topic,
        headline = content_data.get("headline", ""),
        hook     = content_data.get("hook",     ""),
        caption  = content_data.get("caption",  ""),
        cta      = content_data.get("cta",      ""),
        hashtags = content_data.get("hashtags", []),
    )
    overlay.save(output_file)
    return output_file