"""Read the actual text content of our generated PDF."""
from pathlib import Path
import pymupdf

path = Path(__file__).parent / "data" / "document.pdf"
if not path.exists():
    raise SystemExit("Run start.cmd first.")
with pymupdf.open(path) as doc:
    text = "\n".join(page.get_text() for page in doc)
print(text)
if "DEMO-" in text:
    print("The hidden code is still in the document!")
else:
    print("No DEMO code found in the extracted text.")
