# -*- coding: utf-8 -*-
"""Sitedeki bütün iç bağlantıları ve sayfa temel etiketlerini denetler.

    python tools/link_kontrol.py

Her .html sayfasında href, src ve srcset değerlerinin dosyaya çözüldüğünü, #çapa hedeflerinin var olduğunu,
her sayfada tek <h1>, <title>, açıklama ve canonical bulunduğunu, hreflang eşlerinin karşılıklı olduğunu ve
JSON-LD bloklarının geçerli JSON olduğunu kontrol eder. Hata varsa çıkış kodu 1 olur.
"""
import glob, json, os, re, sys
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://hedefvinc.com"
ATLA = ("content/", "tools/", "taslak/", ".git/", ".github/")


class Ayristir(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.linkler, self.idler, self.h1, self.ld, self._ld = [], set(), 0, [], None
        self.title = self.desc = self.canon = None
        self.alt = {}
        self._t = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.idler.add(a["id"])
        for k in ("href", "src"):
            if a.get(k):
                self.linkler.append((tag, a[k]))
        if a.get("srcset") and not a["srcset"].startswith("data:"):
            for parca in a["srcset"].split(","):
                self.linkler.append((tag, parca.strip().split(" ")[0]))
        if tag == "h1":
            self.h1 += 1
        if tag == "title":
            self._t = True
        if tag == "meta" and a.get("name") == "description":
            self.desc = a.get("content")
        if tag == "link" and a.get("rel") == "canonical":
            self.canon = a.get("href")
        if tag == "link" and a.get("rel") == "alternate" and a.get("hreflang"):
            self.alt[a["hreflang"]] = a.get("href")
        if tag == "script" and a.get("type") == "application/ld+json":
            self._ld = ""

    def handle_endtag(self, tag):
        if tag == "title":
            self._t = False
        if tag == "script" and self._ld is not None:
            self.ld.append(self._ld)
            self._ld = None

    def handle_data(self, data):
        if self._t:
            self.title = (self.title or "") + data
        if self._ld is not None:
            self._ld += data


def sayfalar():
    for p in sorted(glob.glob(os.path.join(KOK, "**", "*.html"), recursive=True)):
        rel = os.path.relpath(p, KOK).replace(os.sep, "/")
        if not rel.startswith(ATLA):
            yield rel


def coz(rel_sayfa, url):
    """Bağlantıyı repo içi dosya yoluna çevirir; site dışıysa None."""
    if url.startswith(SITE):
        url = url[len(SITE):] or "/"
    u = urlsplit(url)
    if u.scheme or u.netloc or url.startswith(("mailto:", "tel:", "javascript:", "data:")):
        return None, None
    yol = unquote(u.path)
    if not yol:
        return rel_sayfa, u.fragment
    if yol.startswith("/"):
        hedef = yol[1:]
    else:
        hedef = os.path.normpath(os.path.join(os.path.dirname(rel_sayfa), yol)).replace(os.sep, "/")
    if hedef == "" or hedef.endswith("/"):
        hedef += "index.html"
    return hedef, u.fragment


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    bilgi = {}
    for rel in sayfalar():
        p = Ayristir()
        p.feed(open(os.path.join(KOK, rel), "rb").read().decode("utf-8"))
        bilgi[rel] = p
    hatalar = []
    toplam = 0
    for rel, p in bilgi.items():
        for tag, url in p.linkler:
            hedef, capa = coz(rel, url)
            if hedef is None:
                continue
            toplam += 1
            if not os.path.exists(os.path.join(KOK, hedef)):
                hatalar.append("%s: kırık bağlantı %s" % (rel, url))
            elif capa and hedef.endswith(".html") and hedef in bilgi and capa not in bilgi[hedef].idler:
                hatalar.append("%s: çapa yok %s" % (rel, url))
        if rel != "404.html" or True:
            if p.h1 != 1:
                hatalar.append("%s: %d adet h1" % (rel, p.h1))
            if not p.title or not p.desc:
                hatalar.append("%s: title ya da description eksik" % rel)
            if not p.canon and rel != "404.html":
                hatalar.append("%s: canonical eksik" % rel)
        for i, blok in enumerate(p.ld):
            try:
                json.loads(blok)
            except ValueError as e:
                hatalar.append("%s: JSON-LD %d geçersiz (%s)" % (rel, i, e))
        # hreflang karşılıklılığı
        for dil, href in p.alt.items():
            if dil == "x-default":
                continue
            hedef, _ = coz(rel, href)
            if hedef not in bilgi:
                hatalar.append("%s: hreflang %s hedefi yok (%s)" % (rel, dil, href))
                continue
            if p.canon and p.canon not in bilgi[hedef].alt.values():
                hatalar.append("%s: hreflang eşi %s geri bağlantı vermiyor" % (rel, hedef))
    for h in hatalar:
        print("HATA  " + h)
    print("%d sayfa, %d iç bağlantı denetlendi, %d hata." % (len(bilgi), toplam, len(hatalar)))
    return 1 if hatalar else 0


if __name__ == "__main__":
    sys.exit(main())
