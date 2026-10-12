#!/usr/bin/env python3
"""Create independently designed Android launcher icons (stdlib only).

The upstream ArtCraft marks are trademarks and cannot be reused on modified forks.
"""
import struct
import sys
import zlib
from pathlib import Path


def png(path: Path, n: int) -> None:
    rows = []
    for y in range(n):
        row = bytearray([0])
        for x in range(n):
            xx, yy = (x + .5) / n, (y + .5) / n
            rx = max(abs(xx - .5) - .405, 0)
            ry = max(abs(yy - .5) - .405, 0)
            inside = rx * rx + ry * ry < .075 * .075
            c = (14, 48, 59, 255) if inside else (0, 0, 0, 0)
            if .285 < xx < .705 and .19 < yy < .805 and not (.605 < xx and yy < .29 and yy < -xx + .895):
                c = (246, 250, 247, 255)
            if .605 <= xx <= .705 and .19 <= yy <= .29 and xx + yy > .895:
                c = (150, 202, 191, 255)
            if .35 < xx < .64 and (.44 < yy < .48 or .545 < yy < .585 or .65 < yy < .69):
                c = (29, 105, 112, 255)
            row.extend(c)
        rows.append(bytes(row))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = b"".join(rows)
    data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", n, n, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: make_icon.py APP_DIR")
    root = Path(sys.argv[1])
    for density, n in [("mdpi", 48), ("hdpi", 72), ("xhdpi", 96), ("xxhdpi", 144), ("xxxhdpi", 192)]:
        png(root / f"res/mipmap-{density}/ic_launcher.png", n)
