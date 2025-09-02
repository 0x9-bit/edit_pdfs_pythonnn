import fitz
import os

doc = fitz.open()

# حمّل الخط
# font_path = os.path.join("fonts", "DejaVuSans-Bold.ttf")
# font = fitz.Font(fontfile=font_path)
font = fitz.Font(fontname="symbol")
# اطبع نص مع اليورو
font = fitz.Font("symbol")
vuc = font.valid_codepoints()
page = doc.new_page()
page.insert_text((72, 72), "\u00A0", fontname="symbol", fontsize=20)
# for i in vuc:
#     page.insert_text((72, 72), "%s %s (%s)\n" % (i, chr(i), font.unicode_to_glyph_name(i)), fontname="symbol", fontsize=20)
#     print("%s %s (%s)" % (i, chr(i), font.unicode_to_glyph_name(i)))
doc.save("test.pdf")
doc.close()
