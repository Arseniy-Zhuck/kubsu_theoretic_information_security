import tempfile
import unittest
from pathlib import Path
import pymupdf
import create_pdf


class PdfTests(unittest.TestCase):
    def test_hidden_text_exists(self):
        old = create_pdf.OUT
        with tempfile.TemporaryDirectory() as temp:
            try:
                create_pdf.OUT = Path(temp)
                path = create_pdf.create_document()
                with pymupdf.open(path) as doc:
                    self.assertIn("DEMO-", doc[0].get_text())
                    # Pixel inside the covering rectangle is black.
                    pix = doc[0].get_pixmap()
                    self.assertEqual(pix.pixel(100, 190)[:3], (0, 0, 0))
            finally:
                create_pdf.OUT = old


if __name__ == "__main__":
    unittest.main()
