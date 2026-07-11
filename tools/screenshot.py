#!/usr/bin/env python3
"""Convert LVGL raw ARGB8888 screenshot to PNG"""
import struct, sys, os

def convert(raw_path, out_path):
    try:
        from PIL import Image
    except ImportError:
        os.system("pip3 install Pillow")
        from PIL import Image

    with open(raw_path, 'rb') as f:
        w = struct.unpack('<i', f.read(4))[0]
        h = struct.unpack('<i', f.read(4))[0]
        stride = struct.unpack('<i', f.read(4))[0]
        img = Image.new('RGBA', (w, h))
        for y in range(h):
            row = f.read(w * 4)
            for x in range(w):
                b, g, r, a = row[x*4], row[x*4+1], row[x*4+2], row[x*4+3]
                img.putpixel((x, y), (r, g, b, a))
    img.save(out_path)
    print(f"Saved {out_path} ({w}x{h})")

if __name__ == '__main__':
    raw = sys.argv[1] if len(sys.argv) > 1 else 'screenshot.bin'
    out = sys.argv[2] if len(sys.argv) > 2 else 'screenshot.png'
    convert(raw, out)
