# -*- coding: utf-8 -*-
"""Blog yazılarını ve kuyruktaki taslakları doğrular.

    python taslak/kontrol.py            # content/blog/*.json + taslak/kuyruk/*.json
    python taslak/kontrol.py dosya.json # yalnızca verilen dosyalar

Repo kökünden çalıştırın. Hata varsa çıkış kodu 1 olur ve otomatik yayın durur;
böylece bozuk bir taslak siteye hiç girmez. UYARI satırları yayını durdurmaz.

Denetlenenler: zorunlu alanlar, başlık/açıklama uzunluğu, kategori, slug ve dosya adı,
görselin varlığı, blok yapısı, SSS sayısı, iç bağlantıların çözülmesi, metinde izin verilmeyen HTML
(yalnızca <a href>, <strong>, <em> serbest), telefon numarası ve GEO alanları:
  kisaCevap   45-75 kelime
  cikarimlar  3-5 madde
  kaynaklar   en az 1; her biri title, publisher ve https:// ile başlayan url
  uzunluk     giriş + gövde + SSS: yayındaki yazı en az 1.000, taslak en az 1.150 kelime
              (kısa cevap, çıkarımlar ve kaynaklar sayılmaz)
"""
import glob, json, os, re, sys

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(KOK, "tools"))
import sablon  # noqa: E402

YAZILAR = os.path.join(KOK, "content", "blog")
KUYRUK = os.path.join(KOK, "taslak", "kuyruk")
SAYFALAR = os.path.join(KOK, "content", "sayfalar")

KATEGORILER = ("Vinç Tamiri", "Vinç Kiralama", "Hidrolik", "Atölye", "Rehber")
ALANLAR = ("slug", "_hedef", "title", "h1", "desc", "category", "image", "imageAlt", "intro", "body", "faqs", "related",
           "kisaCevap", "cikarimlar", "kaynaklar")
ALT_SINIR = {False: 1000, True: 1150}   # yayında / taslak
TARIHLER = ("datePublished", "dateModified")
BLOKLAR = {"h2": "text", "h3": "text", "p": "text", "ul": "items", "ol": "items", "table": "rows", "callout": "text"}
CTA_DEGERLERI = ("tamir", "kiralama", "hortum", "atolye", "konteyner", "hiyap", "hidrolik", "yedek",
                 "is-makinasi", "torna", "kaynak", "sase", "bodrum")
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
KUYRUK_ADI = re.compile(r"(\d{2,3})-([a-z0-9]+(?:-[a-z0-9]+)*)\.json\Z")
TARIH = re.compile(r"\d{4}-\d{2}-\d{2}\Z")
ETIKET = re.compile(r"<\s*(/?)\s*([a-zA-Z0-9]+)([^>]*)>")
HREF = re.compile(r'\Ahref="((?:/|https://)[^"<>\s]*)"\Z')
LINK = re.compile(r'href="(/[^"#?]*)')
TELEFON = re.compile(r"(?:\+90|\b0)\s?5\d{2}[\s.]?\d{3}[\s.]?\d{2}[\s.]?\d{2}")


def sayfa_yollari():
    """Sitede var olan (ya da üretici tarafından üretilecek) sayfa yolları."""
    yollar = set()
    for p in glob.glob(os.path.join(KOK, "**", "*.html"), recursive=True):
        rel = os.path.relpath(p, KOK).replace(os.sep, "/")
        if rel.startswith(("content/", "tools/", "taslak/", ".git/")):
            continue
        yollar.add("/" + rel)
    for p in glob.glob(os.path.join(SAYFALAR, "**", "*.html"), recursive=True):
        yollar.add("/" + os.path.relpath(p, SAYFALAR).replace(os.sep, "/"))
    for y in list(yollar):
        if y.endswith("/index.html"):
            yollar.add(y[: -len("index.html")])
    return yollar


def metinler(d):
    yield "intro", d.get("intro", "")
    yield "h1", d.get("h1", "")
    for i, b in enumerate(d.get("body", [])):
        if isinstance(b.get("text"), str):
            yield "body[%d]" % i, b["text"]
        for x in b.get("items", []) or []:
            yield "body[%d]" % i, x
        for x in b.get("head", []) or []:
            yield "body[%d]" % i, x
        for r in b.get("rows", []) or []:
            for c in r:
                yield "body[%d]" % i, c
    for i, f in enumerate(d.get("faqs", [])):
        yield "faqs[%d]" % i, f.get("q", "")
        yield "faqs[%d]" % i, f.get("a", "")


def tum_metinler(d):
    yield from metinler(d)
    if isinstance(d.get("kisaCevap"), str):
        yield "kisaCevap", d["kisaCevap"]
    for i, x in enumerate(d.get("cikarimlar") or []):
        yield "cikarimlar[%d]" % i, x


def say(t):
    return len(re.sub(r"<[^>]+>", " ", str(t)).split())


def kelime(d):
    """Giriş + gövde + SSS (başlık, kısa cevap, çıkarımlar ve kaynaklar hariç)."""
    return sum(say(t) for yer, t in metinler(d) if yer != "h1")


def denetle(yol, d, taslak, yollar, bilinen_yazilar):
    """(hatalar, uyarilar) döndürür."""
    H, U = [], []
    ad = os.path.basename(yol)
    eksik = [k for k in ALANLAR if not d.get(k)]
    if eksik:
        H.append("eksik alan: " + ", ".join(eksik))
    if taslak:
        m = KUYRUK_ADI.fullmatch(ad)
        if not m:
            H.append("dosya adı NN-slug.json olmalı")
        elif d.get("slug") != m.group(2):
            H.append("slug dosya adıyla aynı olmalı")
        for k in TARIHLER:
            if k in d:
                U.append("taslakta %s var; yayınlanırken bugünün tarihiyle değiştirilecek" % k)
    else:
        if d.get("slug") and ad != d["slug"] + ".json":
            H.append("dosya adı <slug>.json olmalı")
        for k in TARIHLER:
            if not TARIH.fullmatch(str(d.get(k, ""))):
                H.append("%s YYYY-AA-GG olmalı" % k)
        if d.get("datePublished", "") > d.get("dateModified", "9"):
            H.append("dateModified, datePublished'tan önce olamaz")
    s = d.get("slug", "")
    if s and not SLUG.fullmatch(s):
        H.append("slug yalnızca küçük harf, rakam ve tire içermeli: %r" % s)
    if len(d.get("title", "")) > 62:
        H.append("title %d karakter (en fazla 62)" % len(d["title"]))
    if len(d.get("desc", "")) > 160:
        H.append("desc %d karakter (en fazla 160)" % len(d["desc"]))
    if d.get("category") and d["category"] not in KATEGORILER:
        H.append("kategori %r geçersiz (%s)" % (d["category"], ", ".join(KATEGORILER)))
    if d.get("cta") and d["cta"] not in CTA_DEGERLERI:
        H.append("cta %r geçersiz (%s)" % (d["cta"], ", ".join(CTA_DEGERLERI)))
    if d.get("image") and not sablon.gorsel_var(d["image"]):
        H.append("görsel yok: assets/img/%s" % sablon.gorsel_yolu(d["image"]))
    elif d.get("image") and sablon.gorsel_yolu(d["image"]) not in sablon.manifest():
        U.append("görselin küçültülmüş kopyası yok; 'python tools/foto.py' çalıştırın (%s)" % d["image"])
    if d.get("image", "").startswith("stok/"):
        U.append("stok fotoğraf kullanılıyor (%s); uygun gerçek fotoğraf varsa onu seçin" % d["image"])

    for i, b in enumerate(d.get("body", []) if isinstance(d.get("body"), list) else []):
        alan = BLOKLAR.get(b.get("type"))
        if not alan:
            H.append("body[%d]: bilinmeyen blok türü %r" % (i, b.get("type")))
            continue
        deger = b.get(alan)
        if not deger:
            H.append("body[%d] (%s): '%s' boş" % (i, b["type"], alan))
        if b["type"] == "table":
            if not b.get("head"):
                H.append("body[%d] (table): 'head' boş" % i)
            elif any(len(r) != len(b["head"]) for r in b.get("rows", [])):
                H.append("body[%d] (table): satırların sütun sayısı başlıkla aynı değil" % i)
    if d.get("body") and not any(b.get("type") == "h2" for b in d["body"]):
        U.append("hiç h2 yok; yazı içi çağrı kutusu yazının sonuna konacak")

    faqs = d.get("faqs", [])
    if any(not f.get("q") or not f.get("a") for f in faqs):
        H.append("SSS'de boş soru ya da cevap var")
    if len(faqs) < 3:
        H.append("en az 3 SSS gerekli (%d var)" % len(faqs))
    elif not 4 <= len(faqs) <= 6:
        U.append("SSS sayısı %d (önerilen 4-6)" % len(faqs))

    n = kelime(d)
    if n < ALT_SINIR[taslak]:
        H.append("%d kelime (en az %d; giriş + gövde + SSS)" % (n, ALT_SINIR[taslak]))

    kc = d.get("kisaCevap")
    if kc is not None:
        if not isinstance(kc, str):
            H.append("kisaCevap metin olmalı")
        elif not 45 <= say(kc) <= 75:
            H.append("kisaCevap %d kelime (45-75 olmalı)" % say(kc))
    ck = d.get("cikarimlar")
    if ck is not None:
        if not isinstance(ck, list) or not 3 <= len(ck) <= 5 or any(not str(x).strip() for x in ck):
            H.append("cikarimlar 3-5 dolu madde olmalı (%s)" % (len(ck) if isinstance(ck, list) else "liste değil"))
        else:
            for i, x in enumerate(ck):
                if say(x) > 20:
                    U.append("cikarimlar[%d] %d kelime (en fazla 20 önerilir)" % (i, say(x)))
    ky = d.get("kaynaklar")
    if ky is not None:
        if not isinstance(ky, list) or not ky:
            H.append("kaynaklar en az 1 kaynak içermeli")
        else:
            for i, k in enumerate(ky):
                if not isinstance(k, dict):
                    H.append("kaynaklar[%d] {title, publisher, url} olmalı" % i)
                    continue
                eksik = [a for a in ("title", "publisher", "url") if not str(k.get(a, "")).strip()]
                if eksik:
                    H.append("kaynaklar[%d]: eksik %s" % (i, ", ".join(eksik)))
                if k.get("url") and not str(k["url"]).startswith("https://"):
                    H.append("kaynaklar[%d]: url https:// ile başlamalı (%s)" % (i, k["url"]))

    def yol_var(y):
        y = y.split("#")[0]
        if y in yollar:
            return True
        if y.startswith("/blog/") and y.endswith(".html") and y[6:-5] in bilinen_yazilar:
            return True
        return False

    for yer, t in tum_metinler(d):
        t = str(t)
        for m in ETIKET.finditer(t):
            kapanis, etiket, attr = m.group(1), m.group(2).lower(), m.group(3).strip()
            if etiket in ("strong", "em") and not attr:
                continue
            if etiket == "a" and (kapanis or HREF.match(attr)):
                continue
            H.append("%s: izin verilmeyen HTML %r" % (yer, m.group(0)[:60]))
        if "javascript:" in t.lower() or "<script" in t.lower():
            H.append("%s: metinde script olamaz" % yer)
        if TELEFON.search(re.sub(r"<[^>]+>", " ", t)):
            U.append("%s: metinde telefon numarası var (çağrı kutularını şablon ekliyor)" % yer)
        for y in LINK.findall(t):
            if not yol_var(y):
                H.append("%s: kırık iç bağlantı %s" % (yer, y))
    for y in d.get("related", []):
        if not y.startswith("/"):
            H.append("related: kök göreli yol olmalı (%s)" % y)
        elif not yol_var(y):
            H.append("related: kırık bağlantı %s" % y)
    if d.get("related") and not any(r.startswith(("/hizmetler/", "/bolgeler/")) for r in d["related"]):
        U.append("related içinde hizmet sayfası yok")
    return H, U


def oku(yol):
    try:
        with open(yol, "rb") as f:
            return json.loads(f.read().decode("utf-8")), None
    except ValueError as e:
        return None, "JSON okunamadı: %s" % e


def kontrol(dosyalar=None, sessiz=False):
    yollar = sayfa_yollari()
    yayinda = sorted(glob.glob(os.path.join(YAZILAR, "*.json")))
    kuyruk = sorted(glob.glob(os.path.join(KUYRUK, "*.json")))
    bilinen = set()
    for p in yayinda:
        d, _ = oku(p)
        if d and d.get("slug"):
            bilinen.add(d["slug"])
    hedef = [os.path.abspath(x) for x in dosyalar] if dosyalar else None
    toplam_h, sayac, gorulen = 0, 0, {}
    for p in yayinda + kuyruk:
        taslak = os.path.dirname(os.path.abspath(p)) == os.path.abspath(KUYRUK)
        d, err = oku(p)
        H, U = ([err], []) if err else denetle(p, d, taslak, yollar, bilinen)
        if d and d.get("slug"):
            if d["slug"] in gorulen:
                H.append("slug %r iki kez kullanılmış (%s)" % (d["slug"], gorulen[d["slug"]]))
            gorulen[d["slug"]] = os.path.basename(p)
            if taslak:
                bilinen.add(d["slug"])  # sonraki taslaklar bu yazıya bağlantı verebilir
        if hedef and os.path.abspath(p) not in hedef:
            continue
        sayac += 1
        rel = os.path.relpath(p, KOK).replace(os.sep, "/")
        if d and not err:
            ozet = "%d kelime, kısa cevap %s, %s çıkarım, %s kaynak" % (
                kelime(d), say(d["kisaCevap"]) if isinstance(d.get("kisaCevap"), str) else "yok",
                len(d["cikarimlar"]) if isinstance(d.get("cikarimlar"), list) else "yok",
                len(d["kaynaklar"]) if isinstance(d.get("kaynaklar"), list) else "yok")
        else:
            ozet = "okunamadı"
        if H:
            print("HATA   %s  (%s)" % (rel, ozet))
            for h in H:
                print("         - %s" % h)
        elif not sessiz:
            print("TAMAM  %s  (%s)" % (rel, ozet))
        if not sessiz:
            for u in U:
                print("         uyarı: %s" % u)
        toplam_h += len(H)
    return toplam_h, sayac


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    hata, adet = kontrol(sys.argv[1:] or None)
    if hata:
        print("\n%d hata, %d dosya denetlendi." % (hata, adet))
        sys.exit(1)
    print("Tamam: %d dosya geçerli." % adet)
