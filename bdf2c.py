#!/usr/bin/env python3
import sys

def parse_bdf(path):
    glyphs = {}

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    current_enc = None
    bitmap = []
    in_bitmap = False
    width = height = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue

        parts = line.split()

        if parts[0] == "ENCODING":
            current_enc = int(parts[1])
            bitmap = []
            in_bitmap = False

        elif parts[0] == "BBX":
            width, height = int(parts[1]), int(parts[2])

        elif parts[0] == "BITMAP":
            in_bitmap = True
            bitmap = []

        elif parts[0] == "ENDCHAR":
            if current_enc is not None and bitmap:
                glyphs[current_enc] = bitmap
            current_enc = None
            in_bitmap = False

        elif in_bitmap and current_enc is not None:
            # hex row
            try:
                row = int(line, 16)

                # normalize to width (shift excess left bits away if needed)
                max_bits = (1 << width) - 1
                row &= max_bits

                bitmap.append(row)
            except ValueError:
                pass

    return glyphs, width, height


def export_c(glyphs, width, height, name="font10x20"):
    print("#include <stdint.h>")
    print(f"// ASCII 32-126 from BDF {width}x{height}")
    print(f"const uint16_t {name}[95][{height}] = {{")

    for code in range(32, 127):
        print(f"  /* {chr(code)} (0x{code:02X}) */ {{")

        if code in glyphs:
            bitmap = glyphs[code]

            # pad or trim to height
            for i in range(height):
                if i < len(bitmap):
                    print(f"    0x{bitmap[i]:04X},")
                else:
                    print("    0x0000,")
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