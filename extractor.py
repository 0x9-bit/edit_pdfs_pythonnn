import fitz  # PyMuPDF

pdf_path = "Sales_Contract_10004048_20250619032751 (2).pdf"  # change to your PDF path

doc = fitz.open(pdf_path)
page = doc[1]  # page index starts at 0, so 1 = second page

print("--- PAGE 2 TEXT ---")
blocks = page.get_text("blocks")
for block in blocks:
    print(repr(block[4]))  # repr shows spaces/newlines
doc.close()
