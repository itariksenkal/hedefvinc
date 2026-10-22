# -*- coding: utf-8 -*-
"""Sayfa düzeyinde SEO denetimi.

    python tools/denetim.py

Her yayınlanan .html sayfasında: tek <h1>, <title> en fazla 62 karakter, açıklama 120-160 karakter,
canonical (404 hariç), karşılıklı hreflang eşleri, her <img> için alt + width + height, geçerli JSON-LD,
og:image ve twitter etiketleri; site genelinde tekrar eden başlık ya da açıklama olmaması.
Hata varsa çıkış kodu 1 olur.
"""
import glob, html, json, os, re, sys
from collections import defaultdict
from html.parser import HTMLParser

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://hedefvinc.com"
ATLA = ("content/", "tools/", "taslak/", ".git/", ".github/")


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.h1 = 0
        self.title, self.desc, self.canon, self.robots = None, None, None, ""
        self.alt, self.meta = {}, {}
        self.imgs, self.ld = [], []
        self._t, self._ld = False, None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "h1":
            self.h1 += 1
        elif tag == "title":
            self._t, self.title = True, ""
        elif tag == "meta":
            k = a.get("name") or a.get("property")
            if k:
                self.meta[k] = a.get("content", "")
        elif tag == "link" and a.get("rel") == "canonical":
            self.canon = a.get("href")
        elif tag == "link" and a.get("rel") == "alternate" and a.get("hreflang"):
            self.alt[a["hreflang"]] = a.get("href")
        elif tag == "img":
            self.imgs.append(a)
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._ld = ""

    def handle_endtag(self, tag):
        if tag == "title":
            self._t = False
        if tag == "script" and self._ld is not None:
            self.ld.append(self._ld)
            self._ld = None

    def handle_data(self, d):
        if self._t:
            self.title += d
        if self._ld is not None:
            self._ld += d


def sayfalar():
    for p in sorted(glob.glob(os.path.join(KOK, "**", "*.html"), recursive=True)):
        rel = os.path.relpath(p, KOK).replace(os.sep, "/")
        if not rel.startswith(ATLA):
            yield rel


def url_to_rel(u):
    yol = u[len(SITE):] if u.startswith(SITE) else u
    yol = yol.lstrip("/")
    if yol == "" or yol.endswith("/"):
        yol += "index.html"
    return yol


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    bilgi = {}
    for rel in sayfalar():
        p = P()
        p.feed(open(os.path.join(KOK, rel), "rb").read().decode("utf-8"))
        bilgi[rel] = p
    H = []
    basliklar, aciklamalar = defaultdict(list), defaultdict(list)
    for rel, p in bilgi.items():
        noindex = "noindex" in p.meta.get("robots", "")
        t = html.unescape(p.title or "").strip()
        d = html.unescape(p.meta.get("description", "")).strip()
        if p.h1 != 1:
            H.append("%s: %d adet h1" % (rel, p.h1))
        if not t:
            H.append("%s: title yok" % rel)
        elif len(t) > 62:
            H.append("%s: title %d karakter (en fazla 62)" % (rel, len(t)))
        if not noindex and not 120 <= len(d) <= 160:
            H.append("%s: açıklama %d karakter (120-160 olmalı)" % (rel, len(d)))
        if not noindex and not p.canon:
            H.append("%s: canonical yok" % rel)
        if not noindex:
            basliklar[t].append(rel)
            aciklamalar[d].append(rel)
        for k in ("og:title", "og:description", "og:image", "og:image:alt", "twitter:card", "twitter:title",
                  "twitter:description", "twitter:image"):
            if not p.meta.get(k):
                H.append("%s: %s eksik" % (rel, k))
        for i, im in enumerate(p.imgs):
            eksik = [k for k in ("alt", "width", "height") if k not in im]
            if eksik:
                H.append("%s: img %s için %s eksik" % (rel, im.get("src", "?")[:50], ", ".join(eksik)))
            elif not im["alt"].strip() and "aria-hidden" not in im:
                H.append("%s: img %s alt metni boş" % (rel, im.get("src", "?")[:50]))
        for i, b in enumerate(p.ld):
            try:
                json.loads(b)
            except ValueError as e:
                H.append("%s: JSON-LD %d geçersiz (%s)" % (rel, i, e))
                continue
            for u in re.findall(r'"(https://hedefvinc\.com/[^"#?]*)', b):
                hedef = url_to_rel(u)
                if not os.path.exists(os.path.join(KOK, hedef)):
                    H.append("%s: JSON-LD içindeki adres yok: %s" % (rel, u))
        for k in ("og:image", "twitter:image"):
            u = p.meta.get(k, "")
            if u.startswith(SITE) and not os.path.exists(os.path.join(KOK, url_to_rel(u))):
                H.append("%s: %s dosyası yok: %s" % (rel, k, u))
        for dil, href in p.alt.items():
            hedef = url_to_rel(href)
            if hedef not in bilgi:
                H.append("%s: hreflang %s hedefi yok (%s)" % (rel, dil, href))
            elif dil != "x-default" and p.canon and p.canon not in bilgi[hedef].alt.values():
                H.append("%s: hreflang eşi %s geri bağlantı vermiyor" % (rel, hedef))
        if p.alt and p.canon and p.canon not in p.alt.values():
            H.append("%s: hreflang listesinde sayfanın kendisi yok" % rel)
    for t, l in basliklar.items():
        if len(l) > 1:
            H.append("aynı title (%s): %s" % (t[:40], ", ".join(l)))
    for d, l in aciklamalar.items():
        if len(l) > 1:
            H.append("aynı açıklama: %s" % ", ".join(l))
    for h in H:
        print("HATA  " + h)
    print("%d sayfa denetlendi, %d hata." % (len(bilgi), len(H)))
    return 1 if H else 0


if __name__ == "__main__":
    sys.exit(main())
