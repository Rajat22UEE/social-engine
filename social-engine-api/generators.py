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


# ── Brand Colors ──────────────────────────────────────────────────────────────
C_NAVY      = (26,  42,  74)    # deep navy – headline
C_GREEN     = (29, 158, 117)    # kyma-AI brand green – hook card accent
C_DRK_GRN   = (15, 110,  86)    # dark green – hook text
C_LT_GREEN  = (225, 245, 238)   # soft green tint – hook card bg


# ── Template Configurations ───────────────────────────────────────────────────
# Each template has its own layout parameters to fit content perfectly
TEMPLATE_CONFIG = {
    # Template 1: Square (1254×1254) - kyma-AI style
    1: {
        "width": 1254,
        "height": 1254,
        "left_x": 64,
        "right_x": 1185,
        "top_y": 350,          # Start lower - more breathing room from top
        "footer_y": 1050,      # Stop before footer
        "headline_size": 90,   # Slightly smaller to fit in one line
        "hook_size": 48,       # Smaller font for better fit
        "headline_max_lines": 1,
        "hook_max_lines": 2,
        "line_spacing": 8,
        "hook_line_spacing": 18,
    },
    # Template 2: Portrait/Stories (941×1672)
    2: {
        "width": 941,
        "height": 1672,
        "left_x": 50,
        "right_x": 880,
        "top_y": 500,          # Start much lower - centered vertically
        "footer_y": 1400,      # Stop well before bottom
        "headline_size": 72,   # Smaller for narrower canvas
        "hook_size": 40,       # Proportionally smaller
        "headline_max_lines": 1,
        "hook_max_lines": 2,
        "line_spacing": 8,
        "hook_line_spacing": 15,
    },
}


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
    Renders headline + hook on the template with template-specific positioning.
    Caption, CTA, and hashtags are accepted for API/DB compatibility but
    NOT drawn on the image.
    """

    def __init__(self, template_path: str, template_id: int = 1):
        self.image = Image.open(template_path).convert("RGB")
        self.draw = ImageDraw.Draw(self.image)
        self.template_id = template_id
        
        # Load template-specific config
        config = TEMPLATE_CONFIG.get(template_id, TEMPLATE_CONFIG[1])
        self.config = config
        
        # Calculate content width
        self.content_w = config["right_x"] - config["left_x"]
        
        # Load fonts sized for this template
        self.f_head = _font(_POPPINS_BOLD, _LIB_BOLD, config["headline_size"])
        self.f_hook = _font(_POPPINS_MEDIUM, _LIB_REG, config["hook_size"])

    def _headline(self, text: str, x: int, y: int) -> int:
        """
        Navy headline – single line, centre-aligned.
        Returns Y below the last line.
        """
        max_lines = self.config["headline_max_lines"]
        lines = _wrap(self.draw, text, self.f_head, self.content_w - 40)[:max_lines]
        if not lines:
            return y

        for ln in lines:
            # Centre this line horizontally
            lw = _tw(self.draw, ln, self.f_head)
            cx = x + (self.content_w - lw) // 2
            self.draw.text((cx, y), ln, font=self.f_head, fill=C_NAVY)
            y += _lh(self.draw, ln, self.f_head) + self.config["line_spacing"]
        
        # Add spacing after headline
        return y + 40

    def _hook(self, text: str, x: int, y: int) -> int:
        """
        Hook in a soft-green card with a bold green left stripe.
        Max 2 lines for punchy, focused messaging.
        Returns Y below the block.
        """
        max_lines = self.config["hook_max_lines"]
        lines = _wrap(self.draw, text, self.f_hook, self.content_w - 60)[:max_lines]
        if not lines:
            return y

        line_h = _lh(self.draw, lines[0], self.f_hook)
        line_spacing = self.config["hook_line_spacing"]
        block_h = len(lines) * (line_h + line_spacing) - line_spacing + 40  # padding top+bottom

        # Full-width card
        self.draw.rounded_rectangle(
            [x, y, self.config["right_x"], y + block_h],
            radius=12, fill=C_LT_GREEN
        )
        # Bold left accent stripe
        self.draw.rounded_rectangle(
            [x, y, x + 8, y + block_h],
            radius=4, fill=C_GREEN
        )

        ty = y + 20
        for ln in lines:
            # Centre each line within the card
            lw = _tw(self.draw, ln, self.f_hook)
            cx = x + (self.content_w - lw) // 2
            self.draw.text((cx, ty), ln, font=self.f_hook, fill=C_DRK_GRN)
            ty += _lh(self.draw, ln, self.f_hook) + line_spacing

        return y + block_h

    # ── Public API ────────────────────────────────────────────────────────────

    def render(self, topic: str, headline: str, hook: str,
               caption: str, cta: str, hashtags: list[str]) -> None:
        """
        Only headline + hook are rendered. All other params are accepted
        for API/DB compatibility but NOT drawn on the image.
        """
        cy = self.config["top_y"]

        # ── Headline (big, bold, centred) ─────────────────────────────────
        cy = self._headline(headline, self.config["left_x"], cy)

        # ── Hook (card with accent stripe) ────────────────────────────────
        self._hook(hook, self.config["left_x"], cy)

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
    output_file = f"outputs/gen_{topic[:8].strip()}_{template_id}.png"

    if not os.path.exists(template_file):
        raise FileNotFoundError(
            f"Template not found: '{template_file}'. "
            f"Place your template PNG at that path."
        )

    overlay = TextOverlay(template_file, template_id)
    overlay.render(
        topic=topic,
        headline=content_data.get("headline", ""),
        hook=content_data.get("hook", ""),
        caption=content_data.get("caption", ""),
        cta=content_data.get("cta", ""),
        hashtags=content_data.get("hashtags", []),
    )
    overlay.save(output_file)
    return output_file