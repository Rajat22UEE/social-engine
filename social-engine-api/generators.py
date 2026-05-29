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
    # Template 3: LinkedIn Landscape (1200×628)
    3: {
        "width": 1200,
        "height": 628,
        "left_x": 60,
        "right_x": 1140,
        "top_y": 100,          # Start near top for landscape
        "footer_y": 500,       # Stop before bottom
        "headline_size": 64,   # Smaller for compact canvas
        "hook_size": 36,       # Smaller hook
        "headline_max_lines": 1,
        "hook_max_lines": 2,
        "line_spacing": 6,
        "hook_line_spacing": 12,
    },
    # Template 4: Twitter / X Post (1024×512)
    4: {
        "width": 1024,
        "height": 512,
        "left_x": 50,
        "right_x": 974,
        "top_y": 80,
        "footer_y": 420,
        "headline_size": 56,
        "hook_size": 32,
        "headline_max_lines": 1,
        "hook_max_lines": 2,
        "line_spacing": 6,
        "hook_line_spacing": 10,
    },
    # Template 5: Pinterest Tall (1000×1500)
    5: {
        "width": 1000,
        "height": 1500,
        "left_x": 55,
        "right_x": 945,
        "top_y": 350,
        "footer_y": 1300,
        "headline_size": 68,
        "hook_size": 38,
        "headline_max_lines": 1,
        "hook_max_lines": 2,
        "line_spacing": 8,
        "hook_line_spacing": 14,
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
    Accepts optional brand_colors dict to override default colors.
    Caption, CTA, and hashtags are accepted for API/DB compatibility but
    NOT drawn on the image.
    """

    def __init__(self, template_path: str, template_id: int = 1, brand_colors: dict = None, canvas_edits: dict = None):
        self.image = Image.open(template_path).convert("RGB")
        self.draw = ImageDraw.Draw(self.image)
        self.template_id = template_id
        self.brand_colors = brand_colors or {}
        self.canvas_edits = canvas_edits or {}
        
        # Load template-specific config
        config = TEMPLATE_CONFIG.get(template_id, TEMPLATE_CONFIG[1])
        self.config = config
        
        # Calculate content width
        self.content_w = config["right_x"] - config["left_x"]
        
        # Load fonts with optional override sizes from canvas_edits
        headline_size = (self.canvas_edits.get('headline_size') or config["headline_size"])
        hook_size = (self.canvas_edits.get('hook_size') or config["hook_size"])
        self.f_head = _font(_POPPINS_BOLD, _LIB_BOLD, headline_size)
        self.f_hook = _font(_POPPINS_MEDIUM, _LIB_REG, hook_size)
        
        # ── Brand Colors (with defaults + canvas overrides) ────────────────
        self._parse_brand_colors()

    def _parse_brand_colors(self):
        """Parse brand colors from hex strings to RGB tuples, with defaults."""
        def hex_to_rgb(hex_str: str, default: tuple) -> tuple:
            if not hex_str or not isinstance(hex_str, str):
                return default
            hex_str = hex_str.lstrip('#')
            try:
                return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
            except (ValueError, IndexError):
                return default
        
        self.color_headline = hex_to_rgb(
            self.brand_colors.get('primary_color'), C_NAVY
        )
        self.color_hook_card_bg = self._lighten_color(self.color_headline, 0.85)
        self.color_hook_accent = hex_to_rgb(
            self.brand_colors.get('secondary_color'), C_GREEN
        )
        self.color_hook_text = self._darken_color(self.color_hook_accent, 0.5)
        self.color_accent = hex_to_rgb(
            self.brand_colors.get('accent_color'), C_GREEN
        )

    @staticmethod
    def _lighten_color(rgb: tuple, factor: float) -> tuple:
        """Lighten a color by blending with white."""
        return tuple(
            min(255, int(c + (255 - c) * factor)) for c in rgb
        )

    @staticmethod
    def _darken_color(rgb: tuple, factor: float) -> tuple:
        """Darken a color by blending with black."""
        return tuple(
            max(0, int(c * (1 - factor))) for c in rgb
        )

    def _headline(self, text: str, x: int, y: int) -> int:
        """
        Brand-colored headline – single line, centre-aligned.
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
            self.draw.text((cx, y), ln, font=self.f_head, fill=self.color_headline)
            y += _lh(self.draw, ln, self.f_head) + self.config["line_spacing"]
        
        # Add spacing after headline
        return y + 40

    def _hook(self, text: str, x: int, y: int) -> int:
        """
        Hook in a brand-colored card with accent stripe.
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

        # Full-width card (lightened primary color)
        self.draw.rounded_rectangle(
            [x, y, self.config["right_x"], y + block_h],
            radius=12, fill=self.color_hook_card_bg
        )
        # Bold left accent stripe (secondary color)
        self.draw.rounded_rectangle(
            [x, y, x + 8, y + block_h],
            radius=4, fill=self.color_hook_accent
        )

        ty = y + 20
        for ln in lines:
            # Centre each line within the card
            lw = _tw(self.draw, ln, self.f_hook)
            cx = x + (self.content_w - lw) // 2
            self.draw.text((cx, ty), ln, font=self.f_hook, fill=self.color_hook_text)
            ty += _lh(self.draw, ln, self.f_hook) + line_spacing

        return y + block_h

    def _place_logo(self) -> None:
        """Place brand logo in the top-left corner if logo_path is provided."""
        logo_path = self.brand_colors.get('logo_path')
        if not logo_path or not os.path.exists(logo_path):
            return
        
        try:
            logo = Image.open(logo_path).convert("RGBA")
            # Resize logo to fit within 150px width while maintaining aspect ratio
            max_logo_w = 150
            max_logo_h = 150
            logo_w, logo_h = logo.size
            ratio = min(max_logo_w / logo_w, max_logo_h / logo_h)
            if ratio < 1:
                new_w = int(logo_w * ratio)
                new_h = int(logo_h * ratio)
                logo = logo.resize((new_w, new_h), Image.LANCZOS)
            
            # Position: top-right corner with padding
            logo_x = self.config["right_x"] - logo.width - 20
            logo_y = 20
            
            # Paste logo with alpha mask for transparency
            if logo.mode == 'RGBA':
                self.image.paste(logo, (logo_x, logo_y), logo)
            else:
                self.image.paste(logo, (logo_x, logo_y))
        except Exception as e:
            print(f"Warning: Could not place logo: {e}")

    # ── Public API ────────────────────────────────────────────────────────────

    def render(self, topic: str, headline: str, hook: str,
               caption: str, cta: str, hashtags: list[str]) -> None:
        """
        Only headline + hook are rendered. All other params are accepted
        for API/DB compatibility but NOT drawn on the image.
        
        If brand_colors contains a logo_path, the logo is placed in the
        top-right corner.
        If canvas_edits contains custom positions, they override defaults.
        """
        # ── Logo (top-right corner, if provided) ──────────────────────────
        self._place_logo()

        # Use template defaults, override with canvas_edits if provided
        left_x = self.canvas_edits.get('headline_x') or self.config["left_x"]
        cy = self.canvas_edits.get('headline_y') or self.config["top_y"]

        # ── Headline (big, bold, centred) ─────────────────────────────────
        cy = self._headline(headline, left_x, cy)

        # ── Hook (card with accent stripe) ────────────────────────────────
        hook_x = self.canvas_edits.get('hook_x') or self.config["left_x"]
        hook_y = self.canvas_edits.get('hook_y') or cy
        self._hook(hook, hook_x, hook_y)

    def save(self, output_path: str) -> None:
        os.makedirs(
            os.path.dirname(output_path) if os.path.dirname(output_path) else ".",
            exist_ok=True
        )
        self.image.save(output_path)


# ── generate_post_image() ─────────────────────────────────────────────────────

def generate_post_image(template_id: int, topic: str,
                        content_data: dict, brand_colors: dict = None,
                        canvas_edits: dict = None) -> str:
    """
    Generate a post image and save to outputs/.
    Accepts optional brand_colors for branded image generation
    and optional canvas_edits for custom text positioning.

    Args:
        template_id  : int       – selects templates/template_{id}.png
        topic        : str       – used in filename
        content_data : dict      – keys: headline, hook, caption, cta, hashtags
        brand_colors : dict, opt – keys: primary_color, secondary_color, accent_color (hex)
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

    overlay = TextOverlay(template_file, template_id, brand_colors, canvas_edits)
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
