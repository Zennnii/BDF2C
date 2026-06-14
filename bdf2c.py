#!/usr/bin/env python3
import sys

def parse_bdf(path):
    glyphs = {}
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    current_enc = None
    bitmap = []
    width = height = 0

    for line in lines:
        parts = line.strip().split()
        if not parts:
            continue

        if parts[0] == "ENCODING":
            current_enc = int(parts[1])
            bitmap = []
        elif parts[0] == "BBX":
            width, height = int(parts[1]), int(parts[2])
        elif parts[0] == "BITMAP":
            bitmap = []
        elif parts[0] == "ENDCHAR":
            if current_enc is not None and len(bitmap) == height:
                glyphs[current_enc] = bitmap
            current_enc = None
        elif current_enc is not None and all(c in "0123456789ABCDEF" for c in parts[0]):
            row = int(parts[0], 16)
            row = row & ((1 << width) - 1)
            bitmap.append(row)

    return glyphs, width, height


def export_c(glyphs, width, height, name="font10x20"):
    print(f"#include <stdint.h>")
    print(f"// ASCII 32-126 from BDF {width}x{height}")
    print(f"const uint16_t {name}[95][{height}] = {{")

    for code in range(32, 127):
        print(f"  /* {chr(code)} (0x{code:02X}) */ {{")
        if code in glyphs:
            bitmap = glyphs[code]
            for row in bitmap:
                print(f"    0x{row:04X},")
        else:
            for _ in range(height):
                print("    0x0000,")
        print("  },")
    print("};")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: bdf2c.py font.bdf > font.h")
        sys.exit(1)

    glyphs, w, h = parse_bdf(sys.argv[1])
    export_c(glyphs, w, h)