"""Generate a fictional PDF with text hidden by a rectangle."""
from pathlib import Path
import secrets
import pymupdf

OUT = Path(__file__).parent / "data"


def create_document():
    OUT.mkdir(exist_ok=True)
    code = "DEMO-" + secrets.token_hex(4).upper()
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((60, 70), "TRAINING DOCUMENT", fontsize=24)
    page.insert_text((60, 110), "Fictional data. No real secrets.", fontsize=13)
    page.insert_text((60, 165), "Access code:", fontsize=16)
    page.insert_text((60, 205), code, fontsize=22)
    secret_rect = pymupdf.Rect(55, 175, 400, 220)
    page.draw_rect(secret_rect, color=(0, 0, 0), fill=(0, 0, 0), overlay=True)
    page.insert_text((60, 270), "The code above has been covered before publication.", fontsize=13)
    doc.save(OUT / "document.pdf", garbage=4, deflate=True)
    doc.close()
    return OUT / "document.pdf"


if __name__ == "__main__":
    path = create_document()
    print("Created:", path)
