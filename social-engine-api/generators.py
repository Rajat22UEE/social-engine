from PIL import Image, ImageDraw, ImageFont
import os

class TextOverlay:
    def __init__(self, template_path):
        self.image = Image.open(template_path)
        self.draw = ImageDraw.Draw(self.image)
        # Point to a local TTF file
        self.font = ImageFont.truetype("arial.ttf", 40)

    def add_text(self, text, position=(50, 200), color=(255, 255, 255)):
        self.draw.text(position, text, font=self.font, fill=color)

    def save(self, output_path):
        self.image.save(output_path)

def generate_post_image(template_id, topic, caption):
    # Ensure directories exist
    os.makedirs("outputs", exist_ok=True)
    
    template_file = f"templates/template_{template_id}.png"
    output_file = f"outputs/gen_{topic[:5]}_{template_id}.png"
    
    if not os.path.exists(template_file):
        raise FileNotFoundError(f"Template {template_file} not found.")

    img = TextOverlay(template_file)
    # Simple overlay logic
    img.add_text(f"Topic: {topic}", (50, 50))
    img.add_text(f"Caption: {caption[:20]}...", (50, 300))
    
    img.save(output_file)
    return output_file