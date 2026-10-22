# -*- coding: utf-8 -*-
"""Fotoğrafların web kopyalarını üretir (Pillow gerekir: pip install pillow).

    python tools/foto.py

assets/img altındaki her .jpg/.jpeg için assets/img/r/<aynı yol>-800.jpg ve
-1600.jpg kopyaları üretir (kaynak daha darsa kendi genişliğinde kalır) ve
boyutları assets/img/r/manifest.json dosyasına yazar. Dikey fotoğraflarda yükseklik de sınırlanır. Sayfa üreticisi
(tools/build_blog.py) srcset, width ve height değerlerini bu dosyadan okur.

Yeni fotoğraf eklediğinizde bu betiği bir kez çalıştırın. Var olan kopyalara
dokunmaz; kaynak dosya değişmişse yeniden üretir. Siyah ekran görüntüsü
bantları otomatik kırpılır.
"""
import glob, hashlib, json, os, sys
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "assets", "img")
OUT = os.path.join(IMG, "r")
WIDTHS = (800, 1600)
MAKS_YUKSEKLIK = {800: 1200, 1600: 1600}  # dikey fotoğraflar gereksiz büyümesin
ATLA = ("ekran-goruntusu", "logo", "favicon", "apple-touch", "icon-")


def kaynaklar():
    for p in sorted(glob.glob(os.path.join(IMG, "**", "*.*"), recursive=True)):
        rel = os.path.relpath(p, IMG).replace(os.sep, "/")
        if not rel.lower().endswith((".jpg", ".jpeg")):
            continue
        if rel.startswith(("r/", "brand/", "og/", "qr/")) or any(a in rel for a in ATLA):
            continue
        yield rel


def siyah_bant_kirp(im):
    g = im.convert("L")
    w, h = g.size
    px = g.load()

    def koyu(y):
        return max(px[x, y] for x in range(0, w, max(1, w // 64))) < 24

    top = 0
    while top < h // 3 and koyu(top):
        top += 1
    bot = h - 1
    while bot > h * 2 // 3 and koyu(bot):
        bot -= 1
    if top > 4 or bot < h - 5:
        return im.crop((0, top, w, bot + 1))
    return im


def main():
    man_yol = os.path.join(OUT, "manifest.json")
    man = json.load(open(man_yol, encoding="utf-8")) if os.path.exists(man_yol) else {}
    yeni = {}
    for rel in kaynaklar():
        src = os.path.join(IMG, rel)
        ozet = hashlib.sha1(open(src, "rb").read()).hexdigest()[:12]
        stem = os.path.splitext(rel)[0]
        hedefler = {w: os.path.join(OUT, "%s-%d.jpg" % (stem, w)) for w in WIDTHS}
        eski = man.get(rel)
        if eski and eski.get("sha1") == ozet and all(os.path.exists(h) for h in hedefler.values()):
            yeni[rel] = eski
            continue
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        im = siyah_bant_kirp(im)
        kayit = {"sha1": ozet, "w": im.width, "h": im.height, "v": []}
        for w in WIDTHS:
            hw = min(w, im.width, round(MAKS_YUKSEKLIK[w] * im.width / im.height))
            hh = round(im.height * hw / im.width)
            out = im if hw == im.width else im.resize((hw, hh), Image.LANCZOS)
            os.makedirs(os.path.dirname(hedefler[w]), exist_ok=True)
            out.save(hedefler[w], "JPEG", quality=74 if w <= 800 else 70,
                     optimize=True, progressive=True, subsampling=2)
            kayit["v"].append({"src": "r/%s-%d.jpg" % (stem, w), "w": hw, "h": hh})
        yeni[rel] = kayit
        print("  %-62s %dx%d" % (rel, im.width, im.height))
    with open(man_yol, "wb") as f:
        f.write((json.dumps(yeni, ensure_ascii=False, indent=1, sort_keys=True) + "\n").encode("utf-8"))
    print("manifest: %d fotoğraf" % len(yeni))


if __name__ == "__main__":
    sys.exit(main())
