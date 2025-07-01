#!/usr/bin/env fontforge
import fontforge
import os

CHAR_DIR = "saved_chars"
OUTPUT_FONT = "output_font.ttf"

font = fontforge.font()
font.encoding = "UnicodeFull"
font.fontname = "CustomHandwritingFont"
font.familyname = "CustomHandwritingFont"
font.fullname = "Custom Handwriting Font"

for char_file in os.listdir(CHAR_DIR):
    if char_file.endswith(".png"):
        glyph_name = char_file[:-4]
        glyph = font.createChar(ord(glyph_name))
        glyph.importOutlines(os.path.join(CHAR_DIR, char_file))
        glyph.left_side_bearing = 10
        glyph.right_side_bearing = 10

font.generate(OUTPUT_FONT)
font.close()
