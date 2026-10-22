# -*- coding: utf-8 -*-
"""Hedef Vinç site üreticisi.

    python tools/build_blog.py          # her şeyi üretir
    python tools/build_blog.py --kontrol  # yazmadan, nelerin değişeceğini söyler

Ne üretir:
  - content/blog/<slug>.json      -> blog/<slug>.html        (Türkçe yazılar)
  - content/sayfalar/**/<ad>.html -> aynı yoldaki sayfa       (ana sayfa, hizmetler, İngilizce sayfalar ...)
  - blog/index.html, en/blog/index.html (kategori süzgeçli liste)
  - sitemap.xml (TR + EN, hreflang eşleri), llms.txt, robots.txt

Aynı girdiyle iki kez çalıştırıldığında hiçbir dosya değişmez. Dosyalar UTF-8 ve LF satır sonuyla yazılır.
Python 3.8+ yeterli, ek paket gerekmez.
"""
import glob, html, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sablon as S  # noqa: E402

ROOT = S.ROOT
SITE = S.SITE
KATEGORILER = ["Vinç Tamiri", "Vinç Kiralama", "Hidrolik", "Atölye", "Rehber"]
TAMIR_HUB = "/hizmetler/vinc-revizyon-tamir-bakim.html"
KIRA_HUB = "/hizmetler/vinc-kiralama.html"

HIZMETLER_TR = S.HIZMETLER

# ---------------------------------------------------------------- yardımcılar


def oku(p):
    return open(p, "rb").read().decode("utf-8").replace("\r\n", "\n")


DEGISEN = []
KURU = "--kontrol" in sys.argv


def yaz(rel, icerik):
    p = os.path.join(ROOT, rel)
    veri = icerik.replace("\r\n", "\n").encode("utf-8")
    if os.path.exists(p) and open(p, "rb").read() == veri:
        return
    DEGISEN.append(rel)
    if KURU:
        return
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(veri)


def url_yolu(rel):
    """'hizmetler/index.html' -> '/hizmetler/', 'index.html' -> '/'"""
    rel = rel.replace(os.sep, "/")
    if rel == "index.html":
        return "/"
    if rel == "en/index.html":
        return "/en/"
    if rel == "hizmetler/index.html":
        return "/hizmetler/"
    return "/" + rel


IZINLI = re.compile(r"&lt;(/?)(strong|em)&gt;")
A_AC = re.compile(r'&lt;a href="((?:/|https://)[^"<>\s]*)"&gt;')


def temiz(t):
    """Yazı metninde yalnızca <a href>, <strong>, <em> kalır; geri kalan her şey metne çevrilir."""
    t = html.escape(html.unescape(str(t)), quote=False)
    t = IZINLI.sub(r"<\1\2>", t)

    def a(m):
        href = m.group(1)
        if href.startswith("https://"):
            return '<a href="%s" rel="noopener">' % href
        return '<a href="%s">' % href
    t = A_AC.sub(a, t)
    t = t.replace("&lt;/a&gt;", "</a>")
    return t


def kelime_say(*parcalar):
    return sum(len(re.sub(r"<[^>]+>", " ", html.unescape(str(x))).split()) for x in parcalar)


# ---------------------------------------------------------------- kaynakları oku

def on_bilgi(kaynak):
    m = re.match(r"\s*<!--(.*?)-->\s*", kaynak, re.S)
    if not m:
        raise ValueError("sayfa kaynağının başında <!-- {json} --> yok")
    return json.loads(m.group(1)), kaynak[m.end():]


def sayfalari_oku():
    out = []
    taban = os.path.join(ROOT, "content", "sayfalar")
    for p in sorted(glob.glob(os.path.join(taban, "**", "*.html"), recursive=True)):
        rel = os.path.relpath(p, taban).replace(os.sep, "/")
        meta, govde = on_bilgi(oku(p))
        meta["_rel"] = rel
        meta["_url"] = meta.get("kanonik_yol") or url_yolu(rel)
        meta.setdefault("dil", "en" if rel.startswith("en/") else "tr")
        out.append((meta, govde))
    return out


def yazilari_oku():
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, "content", "blog", "*.json"))):
        try:
            d = json.loads(oku(p))
        except ValueError as e:
            print("UYARI  %s okunamadı: %s" % (os.path.basename(p), e))
            continue
        eksik = [k for k in ("slug", "title", "h1", "desc", "category", "datePublished", "image", "intro", "body")
                 if not d.get(k)]
        if eksik:
            print("UYARI  %s atlandı, eksik alan: %s" % (os.path.basename(p), ", ".join(eksik)))
            continue
        d.setdefault("dateModified", d["datePublished"])
        d.setdefault("faqs", [])
        d.setdefault("related", [])
        d.setdefault("imageAlt", d["h1"])
        d["_url"] = "/blog/%s.html" % d["slug"]
        out.append(d)
    out.sort(key=lambda d: (d["datePublished"], d["dateModified"], d["slug"]), reverse=True)
    return out


# ---------------------------------------------------------------- yazı kartları

def kart(url, foto, alt, kat, baslik, ozet, tarih, dil, hn="h3"):
    return ('<article class="kart" data-kat="{k}">'
            '<a class="kart__foto" href="{u}" tabindex="-1" aria-hidden="true">{img}</a>'
            '<div class="kart__ic"><p class="etiket">{k} · <time datetime="{t}">{ty}</time></p>'
            '<{hn}><a href="{u}">{b}</a></{hn}><p>{o}</p></div></article>').format(
        k=S.esc(kat), u=url, img=S.img(foto, alt, "(min-width: 1040px) 380px, (min-width: 700px) 50vw, 100vw"),
        t=tarih, ty=S.tarih_yazi(tarih, dil), b=S.esc(baslik), o=S.esc(ozet), hn=hn)


def yazi_karti(d, hn="h3"):
    return kart(d["_url"], d["image"], d.get("imageAlt", ""), d["category"], d["h1"], d["desc"],
                d["datePublished"], "tr", hn)


def en_yazi_karti(m, hn="h3"):
    return kart(m["_url"], m["kapak"], m.get("kapakAlt", ""), m.get("kategori", "Blog"), m["h1"], m["aciklama"],
                m["tarih"], "en", hn)


def yazi_sec(yazilar, kategoriler=(), anahtarlar=(), n=3, haric=()):
    once = [d for d in yazilar if any(a in d["slug"] for a in anahtarlar) and d["_url"] not in haric]
    sonra = [d for d in yazilar if d["category"] in kategoriler and d not in once and d["_url"] not in haric]
    return (once + sonra)[:n]


ILK_GORSEL = re.compile(r"\{\{(?:foto|img):([^|}]+)\|([^|}]*)")


def ilk_gorsel(govde, tercih):
    """Sayfadaki ilk {{foto}}/{{img}}: (yol, alt). tercih verilirse o görselin alt metni aranır."""
    bulunan = ILK_GORSEL.findall(govde)
    for yol, alt in bulunan:
        if tercih and S.gorsel_yolu(yol) == S.gorsel_yolu(tercih):
            return yol, alt
    return bulunan[0] if bulunan else (None, None)


# ---------------------------------------------------------------- yer tutucular

class Baglam:
    def __init__(self, meta, yazilar, en_yazilar, basliklar):
        self.meta, self.yazilar, self.en_yazilar, self.basliklar = meta, yazilar, en_yazilar, basliklar
        self.dil = meta.get("dil", "tr")


def yt_foto(b, a):
    """{{foto:yol|alt|altyazı|sizes|sınıf|eager|sadece}}  sadece: mobil / masaustu"""
    a += [""] * 7
    return S.foto(a[0], a[1], a[2] or None, a[3] or "100vw", bool(a[5]), a[4] or "foto", a[6] or None)


def yt_img(b, a):
    """{{img:yol|alt|sizes|eager|sadece}}"""
    a += [""] * 5
    return S.img(a[0], a[1], a[2] or "100vw", bool(a[3]), sadece=a[4] or None)


def yt_ara(b, a):
    return S.btn_ara(b.dil, metin=a[0] if a and a[0] else None)


def yt_ara_en(b, a):
    return S.btn_ara("en", cls="btn btn--cizgi", metin=a[0] if a and a[0] else "English: %s" % S.TEL_EN_INT)


def yt_wa(b, a):
    return S.btn_wa(a[0] if a and a[0] else (b.meta.get("wa") or S.T[b.dil]["wa_varsayilan"]), b.dil,
                    metin=a[1] if len(a) > 1 and a[1] else None)


def yt_sss(b, a):
    if not b.meta.get("sss"):
        return ""
    return S.sss_html(b.meta["sss"], b.meta.get("sss_baslik"), b.dil)


def yt_son(b, a):
    return S.son_bant(b.dil, b.meta.get("cta", "genel"), b.meta.get("wa"), b.meta.get("cta_baslik"),
                      b.meta.get("cta_metin"))


def yt_kirinti(b, a):
    return S.kirinti_html([tuple(x) for x in b.meta.get("kirinti", [])], b.dil)


def yt_yazilar(b, a):
    """{{yazilar:Başlık|kat1,kat2|3|anahtar1,anahtar2}} -> bant; uygun yazı yoksa hiçbir şey."""
    a += [""] * 4
    kats = [x.strip() for x in a[1].split(",") if x.strip()]
    anah = [x.strip() for x in a[3].split(",") if x.strip()]
    sec = yazi_sec(b.yazilar, kats, anah, int(a[2] or 3), (b.meta["_url"],))
    if not sec:
        return ""
    return ('<section class="bant bant--koyu" aria-labelledby="yazilar-baslik"><div class="wrap">'
            '<div class="bant__bas"><h2 id="yazilar-baslik">%s</h2></div>'
            '<div class="kartlar">%s</div>'
            '<p style="margin-top:24px"><a class="lnk" href="/blog/index.html">Tüm yazılar</a></p>'
            '</div></section>') % (a[0] or "İlgili yazılar", "".join(yazi_karti(d) for d in sec))


def yt_son_yazilar(b, a):
    n = int(a[0]) if a and a[0] else 3
    if b.dil == "en":
        sec = b.en_yazilar[:n]
        return "".join(en_yazi_karti(m) for m in sec)
    return "".join(yazi_karti(d) for d in b.yazilar[:n])


def yt_blogdan(b, a):
    """{{blogdan:Başlık|açıklama|n}} -> son yazılar bandı; yazı yoksa hiçbir şey."""
    a += [""] * 3
    n = int(a[2] or 3)
    if b.dil == "en":
        kartlar = "".join(en_yazi_karti(m) for m in b.en_yazilar[:n])
        tum = '<a class="lnk" href="/en/blog/index.html">All articles</a>'
    else:
        kartlar = "".join(yazi_karti(d) for d in b.yazilar[:n])
        tum = '<a class="lnk" href="/blog/index.html">Tüm yazılar</a>'
    if not kartlar:
        return ""
    return ('<section class="bant bant--koyu" aria-labelledby="blog-baslik"><div class="wrap">'
            '<div class="bant__bas"><h2 id="blog-baslik">%s</h2>%s</div>'
            '<div class="kartlar">%s</div><p style="margin-top:24px">%s</p></div></section>') % (
        a[0] or "Blog", ('<p class="lead">%s</p>' % a[1]) if a[1] else "", kartlar, tum)


def yt_katalog(b, a):
    haric = set(x for x in (a or []) if x) | {b.meta["_url"]}
    li = ['<li><a href="%s"><span class="ad">%s</span><span class="ne">%s</span></a></li>' % (u, S.esc(ad), S.esc(ne))
          for u, ad, ne in HIZMETLER_TR if u not in haric]
    return '<ul class="katalog katalog--iki">%s</ul>' % "".join(li)


def yt_en_yazilar(b, a):
    return "".join(en_yazi_karti(m, "h2") for m in b.en_yazilar)


def yt_harita(b, a):
    return S.esc(S.HARITA)


def yt_adres(b, a):
    return S.adres_html(b.dil)


YER = {"foto": yt_foto, "img": yt_img, "ara": yt_ara, "ara-en": yt_ara_en, "wa": yt_wa, "sss": yt_sss,
       "son": yt_son, "kirinti": yt_kirinti, "yazilar": yt_yazilar, "son-yazilar": yt_son_yazilar,
       "katalog": yt_katalog, "blogdan": yt_blogdan, "en-yazilar": yt_en_yazilar, "harita": yt_harita, "adres": yt_adres, "eposta": lambda b, a: S.EPOSTA,
       "google": lambda b, a: S.esc(S.GOOGLE_PROFIL),
       "tel": lambda b, a: S.TEL, "tel-en": lambda b, a: S.TEL_EN}
YT = re.compile(r"\{\{([a-z-]+)(?::(.*?))?\}\}")


def yer_tut(govde, b):
    def r(m):
        ad = m.group(1)
        if ad not in YER:
            raise ValueError("bilinmeyen yer tutucu {{%s}} (%s)" % (ad, b.meta["_rel"]))
        args = m.group(2).split("|") if m.group(2) is not None else []
        return YER[ad](b, args)
    return YT.sub(r, govde)


# ---------------------------------------------------------------- yazı sayfası

# Yazı içi çağrı kutusu: her yazıya konusuna uyan hizmet sayfası.
# Seçim sırası: yazıdaki "cta" alanı -> "related" içindeki ilk hizmet sayfası -> metindeki ilk hizmet
# bağlantısı -> kategori. Değer: (ad, url, kutu başlığı, kutu metni, WhatsApp mesajı, son bant türü, ikinci bağlantı)
CTA = {
    "tamir": ("Vinç tamiri ve revizyon", TAMIR_HUB, "Vinciniz bu durumda mı?",
              "2005'ten beri Milas Tuzla Kavşağı'ndaki atölyemizde vinç tamir ediyoruz. Arızanın fotoğrafını ya da "
              "kısa bir videosunu gönderin; telefonda dinler, gerekirse sahaya geliriz.",
              "Merhaba, vinç arızası için yazıyorum.", "tamir", "/hizmetler/vinc-hidrolik-tamiri.html"),
    "hiyap": ("Hiyap vinç tamiri", "/hizmetler/hiyap-vinc-tamiri.html", "Hiyabınız bu durumda mı?",
              "Kamyon üstü vinçlerin bom, ayak, kumanda ve hidrolik arızalarına Milas'taki atölyemizde ya da sahada "
              "bakıyoruz. Arızalı hareketin kısa bir videosunu gönderin.",
              "Merhaba, hiyap vinç arızası için yazıyorum.", "tamir", TAMIR_HUB),
    "hidrolik": ("Vinç hidrolik tamiri", "/hizmetler/vinc-hidrolik-tamiri.html", "Vincinizin hidroliğinde sorun mu var?",
                 "Pompa, kumanda valfi, silindir keçesi ve kaçaklar için atölyemizde teşhis, onarım ve deneme yapıyoruz. "
                 "Kaçağın fotoğrafını ya da videosunu gönderin.",
                 "Merhaba, vinç hidrolik arızası için yazıyorum.", "tamir", "/hizmetler/pres-hortum.html"),
    "hortum": ("Pres hortum", "/hizmetler/pres-hortum.html", "Hortum mu patladı?",
               "Eski hortumu getirin ya da rekorların fotoğrafını gönderin; ölçüsüne göre kesip presliyoruz. "
               "Yaygın ölçülerde çoğu hortum aynı gün hazır.",
               "Merhaba, pres hortum yaptırmak istiyorum.", "hortum", "/hizmetler/vinc-hidrolik-tamiri.html"),
    "yedek": ("Hidrolik yedek parça", "/hizmetler/hidrolik-yedek-parca.html", "Parça mı arıyorsunuz?",
              "Parçanın etiketini ya da fotoğrafını gönderin; doğru parçayı bulalım, bulunmayan işlenebilir parçayı "
              "tornada yapalım.", "Merhaba, hidrolik yedek parça arıyorum.", "atolye", "/hizmetler/torna-isleri.html"),
    "is-makinasi": ("İş makinası tamir ve bakım", "/hizmetler/is-makinasi-tamir-bakim.html", "Makineniz mi durdu?",
                    "Ekskavatör, yükleyici ve beko loderin mekanik ve hidrolik arızalarına atölyede ya da sahada "
                    "bakıyoruz. Arızayı anlatın, gereken parçayla gelelim.",
                    "Merhaba, iş makinası arızası için yazıyorum.", "atolye", "/hizmetler/pres-hortum.html"),
    "torna": ("Torna işleri", "/hizmetler/torna-isleri.html", "Parçanız yok mu?",
              "Pim, burç, mil ve flanşı numuneden ya da ölçüden atölyemizde imal ediyoruz. Parçanın fotoğrafını ya da "
              "ölçüsünü gönderin.", "Merhaba, torna ile parça yaptırmak istiyorum.", "atolye", TAMIR_HUB),
    "kaynak": ("Kaynak işleri", "/hizmetler/kaynak-isleri.html", "Kaynak işiniz mi var?",
               "Bom ve şase çatlakları, kova onarımı, çelik konstrüksiyon. Fotoğrafa bakıp yöntemi ve fiyatı "
               "söyleyelim; atölyede ya da sahada.", "Merhaba, kaynak işi için yazıyorum.", "atolye",
               "/hizmetler/kamyon-sase-giydirme.html"),
    "sase": ("Kamyon şase düzeltme ve giydirme", "/hizmetler/kamyon-sase-giydirme.html", "Şase işiniz mi var?",
             "Kamyon şasesini ölçüp doğrultuyor, uzatıyor, kısaltıyor ve güçlendiriyoruz. Aracı ve yapılacak işi "
             "anlatın.", "Merhaba, kamyon şase işi için yazıyorum.", "atolye", "/hizmetler/kaynak-isleri.html"),
    "konteyner": ("Konteyner satış ve kiralama", "/hizmetler/konteyner-satis-kiralama.html", "Konteyner mi lazım?",
                  "Sıfır ve 2. el konteyner satıyor ve kiralıyoruz; vinçli aracımızla getirip istediğiniz yere "
                  "indiriyoruz.", "Merhaba, konteyner için bilgi almak istiyorum.", "konteyner", KIRA_HUB),
    "kiralama": ("Vinç kiralama", KIRA_HUB, "Milas, Bodrum ve çevresinde operatörlü vinç",
                 "Yükün ağırlığını, adresi ve günü söyleyin; uygun vinci ve operatörü planlayalım. Fiyatı işi "
                 "gördükten sonra net söyleriz.", "Merhaba, vinç kiralama için yazıyorum.", "kiralama",
                 "/bolgeler/bodrum-vinc-kiralama.html"),
    "bodrum": ("Bodrum vinç kiralama", "/bolgeler/bodrum-vinc-kiralama.html", "Bodrum'da vinç mi lazım?",
               "Villa, inşaat ve tekne işleri için operatörlü vinç gönderiyoruz. Dar sokaklarda önce yerinde "
               "bakıyoruz. İngilizce hattımız: 0532 294 48 63.", "Merhaba, Bodrum'da vinç kiralamak istiyorum.",
               "kiralama", KIRA_HUB),
    "atolye": ("Tüm hizmetler", "/hizmetler/", "Atölyede işiniz mi var?",
               "Hidrolik, torna, kaynak ve şase işlerini Milas Tuzla Kavşağı'ndaki atölyemizde yapıyoruz. İşin "
               "fotoğrafını gönderin.", "Merhaba, atölye işi için yazıyorum.", "atolye", "/iletisim.html"),
}
URL_CTA = {v[1]: k for k, v in CTA.items() if k != "atolye"}
IKINCI_AD = {v[1]: v[0] for v in CTA.values()}
IKINCI_AD.update({TAMIR_HUB: "Vinç tamiri ve revizyon", "/iletisim.html": "Adres ve yol tarifi"})
SON_METIN = {  # son bant (başlık, metin); listede olmayan türlerde şablonun varsayılanı kullanılır
    "hortum": ("Hortum mu patladı? Ölçüsünü ya da fotoğrafını gönderin.",
               "Eski hortumu getirin ya da rekorların fotoğrafını gönderin; çoğu hortumu aynı gün presliyoruz."),
    "atolye": ("Atölyede işiniz mi var? Fotoğrafını gönderin.",
               "İşin fotoğrafına bakıp ne yapılacağını ve fiyatı söyleriz. Atölyemiz Tuzla Kavşağı'nda, "
               "telefonlarımız 7/24 açık."),
    "konteyner": ("Konteyner mi lazım? Ölçüyü ve adresi söyleyin.",
                  "Seçenekleri ve fiyatı söyleyelim; konteyneri vinçle getirip yerine koyalım."),
}
HIZMET_LINK = re.compile(r'href="(/(?:hizmetler|bolgeler)/[^"#]+)')
ATOLYE_TURLERI = ("atolye", "hortum")


def cta_sec(d):
    acik = (d.get("cta") or "").strip()
    if acik in CTA and acik != "atolye":
        return acik
    adaylar = [r.split("#")[0] for r in d.get("related", []) if r.startswith(("/hizmetler/", "/bolgeler/"))]
    metin = " ".join([d.get("intro", "")] + [b.get("text", "") + " " + " ".join(b.get("items", [])) for b in d["body"]])
    adaylar += HIZMET_LINK.findall(metin)
    for u in adaylar:
        if u in URL_CTA:
            if acik == "atolye" and CTA[URL_CTA[u]][5] not in ATOLYE_TURLERI:
                continue
            return URL_CTA[u]
    if acik == "atolye":
        return "atolye"
    k = d["category"]
    if k == "Vinç Kiralama":
        return "kiralama"
    if k == "Hidrolik":
        return "hidrolik"
    if k == "Atölye":
        return "atolye"
    return "kiralama" if "kiralama" in d["slug"] else "tamir"


def kutu_cta(anahtar):
    ad, url, baslik, metin, wa, _, ikinci = CTA[anahtar]
    return ('<aside class="kutu-cta" aria-label="%s"><h3>%s</h3><p>%s</p><div class="btnlar">%s%s</div>'
            '<p><a class="lnk" href="%s">%s</a> · <a class="lnk" href="%s">%s</a></p></aside>') % (
        S.esc(ad), baslik, metin, S.btn_ara("tr"), S.btn_wa(wa, "tr"), url, ad, ikinci, IKINCI_AD.get(ikinci, ikinci))


def son_bant_yazi(anahtar):
    tur = CTA[anahtar][5]
    if tur in SON_METIN:
        b, m = SON_METIN[tur]
        return S.son_bant("tr", "tamir", CTA[anahtar][4], b, m)
    return S.son_bant("tr", "kiralama" if tur == "kiralama" else "tamir", CTA[anahtar][4])


TR_ASCII = str.maketrans("çğıöşüâîûÇĞİÖŞÜ", "cgiosuaiucgiosu")


def capa(metin, gorulen):
    s = re.sub(r"[^a-z0-9]+", "-", S.metin_duz(metin).translate(TR_ASCII).lower()).strip("-")[:60] or "bolum"
    aday, i = s, 2
    while aday in gorulen:
        aday, i = "%s-%d" % (s, i), i + 1
    gorulen.add(aday)
    return aday


def icindekiler(bloklar, ekler=()):
    """ekler: [(çapa, başlık)] yazı gövdesinden sonra gelen bölümler (çıkarımlar, SSS, kaynaklar)."""
    gorulen, li = set(), []
    for b in bloklar:
        if b.get("type") == "h2":
            li.append('<li><a href="#%s">%s</a></li>' % (capa(b["text"], gorulen), temiz(b["text"])))
    if len(li) < 3:
        return ""
    li += ['<li><a href="#%s">%s</a></li>' % (c, b) for c, b in ekler]
    return ('<details class="katla icindekiler" open><summary><span>İçindekiler</span></summary>'
            '<ol>%s</ol></details>' % "".join(li))


def kisa_cevap_html(d):
    if not d.get("kisaCevap"):
        return ""
    return ('<div class="kisa-cevap"><p class="kisa-cevap__etiket">Kısa cevap</p><p>%s</p></div>'
            % temiz(d["kisaCevap"]))


def cikarimlar_html(d):
    if not d.get("cikarimlar"):
        return ""
    return ('<section class="cikarim" aria-labelledby="cikarimlar"><h2 id="cikarimlar">Önemli çıkarımlar</h2>'
            '<ul>%s</ul></section>' % "".join("<li>%s</li>" % temiz(x) for x in d["cikarimlar"]))


def kaynak_gecerli(k):
    return isinstance(k, dict) and k.get("title") and str(k.get("url", "")).startswith("https://")


def kaynaklar_html(d):
    ks = [k for k in d.get("kaynaklar") or [] if kaynak_gecerli(k)]
    if not ks:
        return ""
    li = "".join('<li><a href="%s" rel="noopener">%s</a>%s</li>' % (
        S.esc(k["url"]), S.esc(k["title"]),
        ('<span class="kaynak__yayinci">%s</span>' % S.esc(k["publisher"])) if k.get("publisher") else "") for k in ks)
    return ('<section class="kaynaklar" aria-labelledby="kaynaklar"><h2 id="kaynaklar">Kaynaklar</h2>'
            '<ol>%s</ol></section>' % li)


def govde_bloklari(bloklar, cta_html):
    out, h2_sayisi, cta_kondu, gorulen = [], 0, False, set()
    for b in bloklar:
        t = b.get("type")
        if t == "h2":
            h2_sayisi += 1
            if h2_sayisi == 2 and not cta_kondu:
                out.append(cta_html)
                cta_kondu = True
            out.append('<h2 id="%s">%s</h2>' % (capa(b["text"], gorulen), temiz(b["text"])))
        elif t == "h3":
            out.append("<h3>%s</h3>" % temiz(b["text"]))
        elif t == "p":
            out.append("<p>%s</p>" % temiz(b["text"]))
        elif t in ("ul", "ol"):
            out.append("<%s>%s</%s>" % (t, "".join("<li>%s</li>" % temiz(x) for x in b["items"]), t))
        elif t == "table":
            head = "".join("<th scope=\"col\">%s</th>" % temiz(c) for c in b.get("head", []))
            rows = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % temiz(c) for c in r) for r in b["rows"])
            out.append('<div class="tablo-kap"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
                       % (head, rows))
        elif t == "callout":
            out.append('<div class="not"><p>%s</p></div>' % temiz(b["text"]))
        else:
            print("UYARI  bilinmeyen blok türü: %r" % t)
    if not cta_kondu:
        out.append(cta_html)
    return "\n".join(out)


def ilgili_listesi(yollar, basliklar, dil="tr"):
    li = []
    for y in yollar:
        y = y.split("#")[0]
        if y not in basliklar:
            continue
        tur = ("Yazı" if dil == "tr" else "Article") if "/blog/" in y else ("Hizmet" if dil == "tr" else "Service")
        li.append('<li><a href="%s"><span class="tur">%s</span>%s</a></li>' % (y, tur, S.esc(basliklar[y])))
    return '<ul class="ilgili">%s</ul>' % "".join(li) if li else ""


def yazar_kutusu(dil="tr"):
    if dil == "en":
        return ('<div class="yazar"><span class="etiket" style="margin:0">Written by</span>'
                '<span class="yazar__ad">Ahmet Uğur &amp; Mehmet Uğur</span>'
                '<p>Owners of Hedef Vinç (Retrofit Hedef Crane). Repairing and renting out cranes from their own '
                'workshop in Milas since 2005. <a class="lnk" href="/en/about.html">About us</a></p></div>')
    return ('<div class="yazar"><span class="etiket" style="margin:0">Yazan</span>'
            '<span class="yazar__ad">Ahmet Uğur &amp; Mehmet Uğur</span>'
            '<p>Hedef Vinç\'in (Retrofit Hedef Crane) sahipleri. 2005\'ten beri Milas Tuzla Kavşağı\'ndaki atölyede '
            'vinç tamiri ve vinç kiralama yapıyorlar. <a class="lnk" href="/hakkimizda.html">Hakkımızda</a></p></div>')


def kisiler():
    return [S.kisi_ref(ad, kimlik) for ad, kimlik in S.YAZARLAR]


def yazi_schema(url, baslik, aciklama, gorsel, yayin, guncel, dil, kategori, kelime, ozet=None, kaynaklar=()):
    d = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": baslik[:110],
            "description": aciklama, "image": [S.og_url(gorsel)], "datePublished": yayin, "dateModified": guncel,
            "author": kisiler(),
            "publisher": {"@type": "Organization", "@id": S.ISLETME_ID, "name": "Hedef Vinç",
                          "logo": {"@type": "ImageObject", "url": S.LOGO_PNG}},
            "isPartOf": {"@id": S.WEBSITE_ID},
            "mainEntityOfPage": {"@type": "WebPage", "@id": url}, "inLanguage": dil,
            "articleSection": kategori, "wordCount": kelime}
    if ozet:
        d["abstract"] = S.metin_duz(ozet)
    if kaynaklar:
        d["citation"] = [{"@type": "CreativeWork", "name": k["title"], "url": k["url"],
                          **({"publisher": {"@type": "Organization", "name": k["publisher"]}} if k.get("publisher") else {})}
                         for k in kaynaklar]
    return d


def yazi_sayfasi(d, basliklar, es_haritasi):
    url = SITE + d["_url"]
    tur = cta_sec(d)
    kelime = kelime_say(d["intro"], *[b.get("text", "") for b in d["body"]],
                        *[x for b in d["body"] for x in b.get("items", [])],
                        *[c for b in d["body"] for r in b.get("rows", []) for c in r],
                        *[f["q"] + " " + f["a"] for f in d["faqs"]])
    dk = max(2, round(kelime / 200))
    kirinti = [("Blog", "/blog/index.html"), (d["h1"], None)]
    sss = ""
    if d["faqs"]:
        sss = ('<h2 id="sss">Sık sorulan sorular</h2><div class="sss">%s</div>'
               % "".join('<details><summary>%s</summary><div class="cevap"><p>%s</p></div></details>'
                         % (temiz(f["q"]), temiz(f["a"])) for f in d["faqs"]))
    ilgili = ilgili_listesi(d["related"], basliklar)
    hub, hub_ad = CTA[tur][1], CTA[tur][0]
    hub_li = "" if hub in d["related"] else ('<li><a href="%s"><span class="tur">Hedef Vinç</span>%s</a></li>' % (hub, hub_ad))
    yan = ('<aside class="yan">%s<div><h2>Hedef Vinç</h2><ul class="ilgili">%s'
           '<li><a href="/iletisim.html"><span class="tur">Atölye</span>Adres ve yol tarifi</a></li></ul></div></aside>') % (
        ('<div><h2>Bu konuyla ilgili</h2>%s</div>' % ilgili) if ilgili else "", hub_li)
    guncel = d["dateModified"]
    cikarim, kaynak = cikarimlar_html(d), kaynaklar_html(d)
    ek = ([("cikarimlar", "Önemli çıkarımlar")] if cikarim else []) + ([("sss", "Sık sorulan sorular")] if sss else []) \
        + ([("kaynaklar", "Kaynaklar")] if kaynak else [])
    govde = """<article>
<header class="yazi-bas"><div class="wrap">
{kirinti}
<p class="etiket">{kat}</p>
<h1>{h1}</h1>
<div class="kunye"><span>Yayın: <b><time datetime="{y}">{yy}</time></b></span><span>Güncelleme: <b><time datetime="{g}">{gy}</time></b></span><span>Yazan: <b>Ahmet Uğur &amp; Mehmet Uğur</b></span><span>{dk} dk okuma</span></div>
{kisa}
</div></header>
<div class="wrap"><figure class="kapak">{img}<figcaption>{alt}</figcaption></figure></div>
<div class="wrap yazi-govde">
<div class="metin">
<p class="giris-p">{giris}</p>
{icindekiler}
{govde}
{cikarim}
{sss}
{kaynak}
{yazar}
</div>
{yan}
</div>
</article>
{son}""".format(kirinti=S.kirinti_html(kirinti, "tr"), kat=S.esc(d["category"]), h1=temiz(d["h1"]),
                y=d["datePublished"], yy=S.tarih_yazi(d["datePublished"]), g=guncel, gy=S.tarih_yazi(guncel),
                dk=dk, img=S.img(d["image"], d.get("imageAlt", ""), "(min-width: 1232px) 1200px, 100vw", True),
                alt=S.esc(d.get("imageAlt", "")), giris=temiz(d["intro"]),
                govde=govde_bloklari(d["body"], kutu_cta(tur)), sss=sss, yazar=yazar_kutusu(),
                icindekiler=icindekiler(d["body"], ek), kisa=kisa_cevap_html(d), cikarim=cikarim, kaynak=kaynak,
                yan=yan, son=son_bant_yazi(tur))
    lds = [yazi_schema(url, d["h1"], d["desc"], d["image"], d["datePublished"], guncel, "tr", d["category"], kelime,
                       d.get("kisaCevap"), [k for k in d.get("kaynaklar") or [] if kaynak_gecerli(k)]),
           S.kirinti_schema(kirinti, "tr")]
    if d["faqs"]:
        lds.append(S.sss_schema(d["faqs"]))
    meta = {"baslik": d["title"], "aciklama": d["desc"], "dil": "tr", "kanonik": url, "es": es_haritasi.get(d["_url"]),
            "nav": "blog", "gorsel": d["image"], "gorsel_alt": d.get("imageAlt"), "ld": lds, "tur": "article",
            "og_baslik": d["h1"],
            "wa": "Merhaba, \"%s\" yazınızı okudum, bilgi almak istiyorum." % S.metin_duz(d["h1"])}
    return S.sayfa(meta, govde)


def en_yazi_sayfasi(m, govde_html, basliklar, es_haritasi):
    url = SITE + m["_url"]
    kirinti = [("Blog", "/en/blog/index.html"), (m["h1"], None)]
    tur = m.get("cta", "genel")
    kelime = kelime_say(govde_html)
    ilgili = ilgili_listesi(m.get("ilgili", []), basliklar, "en")
    yan = ('<aside class="yan">%s<div><h2>Services</h2><ul class="ilgili">'
           '<li><a href="/en/services/crane-repair-maintenance.html"><span class="tur">Hedef Vinç</span>Crane repair &amp; maintenance</a></li>'
           '<li><a href="/en/services/crane-rental.html"><span class="tur">Hedef Vinç</span>Crane rental</a></li>'
           '<li><a href="/en/contact.html"><span class="tur">Workshop</span>Address and directions</a></li></ul></div></aside>') % (
        ('<div><h2>Related</h2>%s</div>' % ilgili) if ilgili else "")
    govde = """<article>
<header class="yazi-bas"><div class="wrap">
{kirinti}
<p class="etiket">{kat}</p>
<h1>{h1}</h1>
<div class="kunye"><span>Published: <b><time datetime="{y}">{yy}</time></b></span><span>Updated: <b><time datetime="{g}">{gy}</time></b></span><span>By <b>Ahmet Uğur &amp; Mehmet Uğur</b></span></div>
</div></header>
<div class="wrap"><figure class="kapak">{img}{cap}</figure></div>
<div class="wrap yazi-govde">
<div class="metin">
{govde}
{yazar}
</div>
{yan}
</div>
</article>
{son}""".format(kirinti=S.kirinti_html(kirinti, "en"), kat=S.esc(m.get("kategori", "Blog")), h1=S.esc(m["h1"]),
                y=m["tarih"], yy=S.tarih_yazi(m["tarih"], "en"), g=m.get("degisim", m["tarih"]),
                gy=S.tarih_yazi(m.get("degisim", m["tarih"]), "en"),
                img=S.img(m["kapak"], m.get("kapakAlt", ""), "(min-width: 1232px) 1200px, 100vw", True),
                cap=("<figcaption>%s</figcaption>" % m["kapakYazi"]) if m.get("kapakYazi") else "",
                govde=govde_html.strip(), yazar=yazar_kutusu("en"), yan=yan, son=S.son_bant("en", tur))
    lds = [yazi_schema(url, m["h1"], m["aciklama"], m["kapak"], m["tarih"], m.get("degisim", m["tarih"]), "en",
                       m.get("kategori", "Blog"), kelime), S.kirinti_schema(kirinti, "en")]
    meta = {"baslik": m["baslik"], "aciklama": m["aciklama"], "dil": "en", "kanonik": url,
            "es": es_haritasi.get(m["_url"]), "nav": "blog", "gorsel": m["kapak"], "gorsel_alt": m.get("kapakAlt"),
            "ld": lds, "tur": "article",
            "og_baslik": m["h1"], "wa": S.T["en"]["wa_varsayilan"]}
    return S.sayfa(meta, govde)


# ---------------------------------------------------------------- blog listesi

def blog_listesi(yazilar, es_haritasi):
    kats = [k for k in KATEGORILER if any(d["category"] == k for d in yazilar)]
    kats += sorted(set(d["category"] for d in yazilar) - set(kats))
    cipler = ('<div class="cipler" role="group" aria-label="Kategoriye göre süz" hidden>'
              '<button class="cip" type="button" data-kat="*" aria-pressed="true">Tümü (%d)</button>%s</div>') % (
        len(yazilar), "".join('<button class="cip" type="button" data-kat="%s" aria-pressed="false">%s (%d)</button>'
                              % (S.esc(k), S.esc(k), sum(d["category"] == k for d in yazilar)) for k in kats))
    kartlar = "".join(yazi_karti(d, "h2") for d in yazilar)
    kirinti = [("Blog", None)]
    govde = """<section class="sb"><div class="wrap">
{kirinti}
<h1>Vinç tamiri ve vinç kiralama üzerine yazılar</h1>
<p class="sb__giris">Atölyede ve sahada en sık sorulan soruları yazıya döküyoruz: arıza belirtileri, hidrolik, bakım, kiralama öncesi hazırlık ve iş güvenliği. Yazıları Ahmet Uğur ve Mehmet Uğur yazıyor.</p>
</div></section>
<section class="bant bant--koyu" aria-label="Yazılar"><div class="wrap">
{cipler}
<div class="kartlar kartlar--liste">{kartlar}</div>
</div></section>
{son}""".format(kirinti=S.kirinti_html(kirinti, "tr"), cipler=cipler, kartlar=kartlar or "<p>Henüz yazı yok.</p>",
                son=S.son_bant("tr", "genel"))
    lds = [S.kirinti_schema(kirinti, "tr"),
           {"@context": "https://schema.org", "@type": "Blog", "name": "Hedef Vinç Blog", "url": SITE + "/blog/index.html",
            "inLanguage": "tr", "publisher": {"@id": S.ISLETME_ID},
            "blogPost": [{"@type": "BlogPosting", "headline": d["h1"], "url": SITE + d["_url"],
                          "datePublished": d["datePublished"]} for d in yazilar[:20]]}]
    meta = {"baslik": "Blog: Vinç Tamiri, Hidrolik ve Vinç Kiralama | Hedef Vinç",
            "aciklama": "Vinç tamiri, hidrolik arızalar, bakım ve vinç kiralama üzerine Milas'taki atölyemizden pratik yazılar. Yazanlar: Ahmet Uğur ve Mehmet Uğur.",
            "dil": "tr", "kanonik": SITE + "/blog/index.html", "es": es_haritasi.get("/blog/index.html"),
            "nav": "blog", "gorsel": yazilar[0]["image"] if yazilar else None, "ld": lds}
    return S.sayfa(meta, govde)


# ---------------------------------------------------------------- site haritası, llms, robots

def site_haritasi(girdiler):
    """girdiler: [(url_yolu, lastmod, es_yolu_veya_None, dil, ana_gorsel_veya_None)]"""
    satir = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml"'
             ' xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
    for yol, lastmod, es, dil, gorsel in girdiler:
        satir.append("  <url>")
        satir.append("    <loc>%s%s</loc>" % (SITE, yol))
        if lastmod:
            satir.append("    <lastmod>%s</lastmod>" % lastmod)
        if es:
            tr, en = (yol, es) if dil == "tr" else (es, yol)
            satir.append('    <xhtml:link rel="alternate" hreflang="tr" href="%s%s"/>' % (SITE, tr))
            satir.append('    <xhtml:link rel="alternate" hreflang="en" href="%s%s"/>' % (SITE, en))
            satir.append('    <xhtml:link rel="alternate" hreflang="x-default" href="%s%s"/>' % (SITE, tr))
        if gorsel:
            satir.append("    <image:image><image:loc>%s</image:loc></image:image>" % S.esc(S.og_url(gorsel)))
        satir.append("  </url>")
    satir.append("</urlset>")
    return "\n".join(satir) + "\n"


KISA_SSS = [  # llms.txt için doğrudan, tek satırlık cevaplar (yalnızca sitede yazan bilgiler)
    ("Hedef Vinç nerede?", "Milas'ta, Güllük ile Güvercinlik arasındaki Tuzla Kavşağı'nda, Shell'in arkasında: "
                           "Dörttepe Mah. 3. Bulvar No:128/2, 48200 Milas / Muğla."),
    ("Kaç yıldır çalışıyorlar?", "2005'ten beri; sahipleri Ahmet Uğur ve Mehmet Uğur."),
    ("Hangi saatlerde açık?", "7 gün 24 saat, acil işler dahil."),
    ("Ana işleri ne?", "Vinç tamiri (revizyon, bakım, hiyap ve hidrolik tamiri) ve operatörlü vinç kiralama."),
    ("Vinç operatörüyle mi geliyor?", "Evet, kiralanan vinçler kendi operatörleriyle gelir."),
    ("Arızalı vinç için sahaya geliyorlar mı?", "Evet; hortum, rekor, kumanda ve ayak arızalarının çoğu sahada, "
                                                 "söküm ve revizyon gerektiren işler atölyede yapılır."),
    ("Hangi bölgelere hizmet veriyorlar?", "Milas, Bodrum, Muğla, Aydın, İzmir ve çevresi."),
    ("Bodrum'da tekne kaldırıyorlar mı?", "Evet, vinçle tekne kaldırma ve denize indirme yapıyorlar."),
    ("İngilizce konuşan biri var mı?", "Evet, İngilizce hat: %s." % S.TEL_EN_INT),
    ("Fiyat listesi var mı?", "Hayır; fiyat işi gördükten sonra yük, mesafe, süre, adres ve saha koşullarına "
                              "(tamirde arızanın kapsamı ve parçaya) göre verilir."),
    ("Nasıl ulaşılır?", "Telefon %s (7/24), WhatsApp https://wa.me/%s, e-posta %s." % (S.TEL_INT, S.WA, S.EPOSTA)),
]


def llms(sayfalar, yazilar, en_yazilar):
    tr = {m["_url"]: m for m, _ in sayfalar if m.get("dil") == "tr" and m.get("tur") != "yazi" and not m.get("noindex")}
    en = {m["_url"]: m for m, _ in sayfalar if m.get("dil") == "en" and m.get("tur") != "yazi" and not m.get("noindex")}
    L = ["# Hedef Vinç (Retrofit Hedef Crane)", "",
         "> Milas (Muğla) merkezli vinç tamiri ve vinç kiralama firması. 2005'ten beri Ahmet Uğur ve Mehmet Uğur "
         "tarafından işletiliyor. Tuzla Kavşağı'ndaki kendi atölyesinde vinç tamiri, revizyon, bakım, hiyap tamiri ve "
         "vinç hidrolik tamiri yapıyor; Milas, Bodrum, Muğla, Aydın ve İzmir çevresinde operatörlü vinç kiralıyor. "
         "7/24 açık. Yabancı müşteriler için İngilizce telefon hattı var.", "",
         "## Temel bilgiler", "",
         "- Firma: Hedef Vinç (Retrofit Hedef Crane). Google İşletme Profili'ndeki adı: Hedef Vinç Hidrolik (%s)" % S.GOOGLE_PROFIL,
         "- Sahipler: Ahmet Uğur, Mehmet Uğur (kurucu ortaklar)",
         "- Faaliyet: 2005'ten beri",
         "- Adres: %s, %s, %s, Türkiye" % (S.ADRES_SATIR, S.ADRES_TARIF, S.ADRES_IL),
         "- Telefon (Türkçe, 7/24): %s" % S.TEL_INT,
         "- English line / İngilizce hat: %s" % S.TEL_EN_INT,
         "- WhatsApp: https://wa.me/%s" % S.WA,
         "- E-posta: %s" % S.EPOSTA,
         "- Çalışma saatleri: 7 gün 24 saat, acil işler dahil",
         "- Hizmet bölgesi: Milas, Bodrum, Muğla, Aydın, İzmir ve çevresi (Güllük, Güvercinlik, Ören, Yatağan, Didim, Söke)",
         "- Ana işler: vinç tamiri (revizyon, bakım, hiyap, hidrolik) ve vinç kiralama (operatörlü)",
         "- Diğer işler: iş makinası tamir-bakım, pres hortum, hidrolik yedek parça, torna, kaynak, kamyon şase giydirme, konteyner satış-kiralama",
         "- Fiyat: Sabit fiyat listesi yok. Vinç kiralamada yükün ağırlığı, yükseklik ve mesafe, süre, adres ve saha koşulları; "
         "tamirde arızanın kapsamı, parça ve işin atölyede mi sahada mı yapılacağı fiyatı belirler.",
         "- Site dili: Türkçe (ana), İngilizce (/en/)", ""]

    L += ["## Hizmet sayfaları", ""]
    for u, ad, ne in S.HIZMETLER:
        L.append("- [%s](%s%s): %s" % (ad, SITE, u, ne))
    L.append("- [Tüm hizmetler](%s/hizmetler/): Hizmetlerin tamamı tek sayfada." % SITE)
    L.append("")

    L += ["## Sık sorulan sorular (kısa cevaplar)", ""]
    for q, a in KISA_SSS:
        L.append("- %s %s" % (q, a))
    L.append("")

    L += ["## Kurumsal sayfalar", ""]
    for y in ["/", "/hakkimizda.html", "/iletisim.html", "/blog/index.html"]:
        if y in tr:
            m = tr[y]
            L.append("- [%s](%s%s): %s" % (m.get("kisa_ad") or m["baslik"], SITE, y, m["aciklama"]))
    L.append("")

    L += ["## Sayfalardaki sorular ve cevaplar", ""]
    goruldu = set()
    for y in ["/", "/hizmetler/vinc-revizyon-tamir-bakim.html", "/hizmetler/vinc-kiralama.html",
              "/hizmetler/hiyap-vinc-tamiri.html", "/hizmetler/vinc-hidrolik-tamiri.html",
              "/bolgeler/bodrum-vinc-kiralama.html", "/iletisim.html"]:
        for x in tr.get(y, {}).get("sss", []):
            q = S.metin_duz(x["q"])
            if q in goruldu:
                continue
            goruldu.add(q)
            L.append("- S: %s" % q)
            L.append("  C: %s" % S.metin_duz(x["a"]))
    L.append("")

    if yazilar:
        L += ["## Blog yazıları (Türkçe)", ""]
        for d in yazilar:
            L.append("- [%s](%s%s) (%s, %s): %s" % (S.metin_duz(d["h1"]), SITE, d["_url"], d["category"],
                                                    d["datePublished"], d["desc"]))
            if d.get("kisaCevap"):
                L.append("  Kısa cevap: %s" % S.metin_duz(d["kisaCevap"]))
        L.append("")

    L += ["## English", "",
          "Hedef Vinç repairs cranes (overhaul, loader/knuckle-boom crane repair, hydraulics) in its own workshop at the "
          "Tuzla junction in Milas, and rents out cranes with operators around Milas and Bodrum, including villa and "
          "construction lifts and boat lifting. Open 24/7. English line: %s. Email: %s." % (S.TEL_EN_INT, S.EPOSTA), ""]
    for y, m in sorted(en.items()):
        L.append("- [%s](%s%s): %s" % (m.get("kisa_ad") or m["baslik"], SITE, y, m["aciklama"]))
    for m in en_yazilar:
        L.append("- [%s](%s%s) (%s): %s" % (m["h1"], SITE, m["_url"], m["tarih"], m["aciklama"]))
    L.append("")
    return "\n".join(L)


ROBOTS = """User-agent: *
Allow: /
Disallow: /content/
Disallow: /tools/
Disallow: /taslak/

Sitemap: https://hedefvinc.com/sitemap.xml
"""

# ---------------------------------------------------------------- ana akış


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sayfalar = sayfalari_oku()
    yazilar = yazilari_oku()
    tr_yazi_slug = {d["slug"] for d in yazilar}

    en_yazilar = sorted([m for m, _ in sayfalar if m.get("tur") == "yazi" and m["dil"] == "en"],
                        key=lambda m: (m["tarih"], m["_url"]), reverse=True)

    # hreflang eşleri: iki yönlü
    es = {}
    for m, _ in sayfalar:
        if m.get("es"):
            hedef = m["es"]
            if hedef.startswith("/blog/") and hedef != "/blog/index.html":
                slug = hedef[len("/blog/"):-len(".html")]
                if slug not in tr_yazi_slug and not os.path.exists(os.path.join(ROOT, "blog", slug + ".html")):
                    continue
            es[m["_url"]] = hedef
            es[hedef] = m["_url"]

    # başlık haritası (ilgili bağlantılar için)
    basliklar = {}
    for m, _ in sayfalar:
        basliklar[m["_url"]] = m.get("kisa_ad") or m.get("h1") or m["baslik"]
    for d in yazilar:
        basliklar[d["_url"]] = S.metin_duz(d["h1"])

    harita = []

    for d in yazilar:
        yaz("blog/%s.html" % d["slug"], yazi_sayfasi(d, basliklar, es))
        harita.append((d["_url"], d["dateModified"], es.get(d["_url"]), "tr", d["image"]))

    if yazilar or os.path.exists(os.path.join(ROOT, "content", "blog")):
        yaz("blog/index.html", blog_listesi(yazilar, es))
        son = max([d["dateModified"] for d in yazilar] or [None]) if yazilar else None
        harita.append(("/blog/index.html", son, es.get("/blog/index.html"), "tr",
                       yazilar[0]["image"] if yazilar else None))

    for meta, govde in sayfalar:
        b = Baglam(meta, yazilar, en_yazilar, basliklar)
        icerik = yer_tut(govde, b)
        if meta.get("tur") == "yazi":
            html_out = en_yazi_sayfasi(meta, icerik, basliklar, es)
        else:
            kanonik = SITE + meta["_url"]
            lds = []
            dugum = []
            if meta.get("isletme"):
                dugum.append(S.isletme_schema())
            if meta.get("website"):
                dugum.append(S.website_schema())
            if meta.get("kisiler"):
                dugum.extend(S.kisi_schema())
            if dugum:
                lds.append(S.graf(dugum))
            if meta.get("hizmet"):
                lds.append(S.hizmet_schema(meta["hizmet"], kanonik, meta["dil"]))
            if meta.get("kirinti"):
                lds.append(S.kirinti_schema([tuple(x) for x in meta["kirinti"]], meta["dil"]))
            if meta.get("sss"):
                lds.append(S.sss_schema(meta["sss"]))
            m2 = dict(meta)
            m2.update({"kanonik": kanonik, "es": es.get(meta["_url"]), "ld": lds,
                       "gorsel_alt": meta.get("gorsel_alt") or ilk_gorsel(govde, meta.get("gorsel"))[1]})
            html_out = S.sayfa(m2, icerik)
        yaz(meta["_rel"], html_out)
        if not meta.get("noindex"):
            gorsel = meta.get("kapak") if meta.get("tur") == "yazi" else ilk_gorsel(govde, None)[0]
            harita.append((meta["_url"], meta.get("degisim") or meta.get("guncelleme"), es.get(meta["_url"]),
                           meta["dil"], gorsel))

    # eski (henüz JSON'a taşınmamış) Türkçe yazılar haritada kalsın
    for p in sorted(glob.glob(os.path.join(ROOT, "blog", "*.html"))):
        slug = os.path.basename(p)[:-5]
        if slug != "index" and slug not in tr_yazi_slug:
            harita.append(("/blog/%s.html" % slug, None, es.get("/blog/%s.html" % slug), "tr", None))

    sira = {"/": 0, "/en/": 1}
    harita.sort(key=lambda x: (x[3] != "tr", sira.get(x[0], 2), x[0]))
    yaz("sitemap.xml", site_haritasi(harita))
    yaz("llms.txt", llms(sayfalar, yazilar, en_yazilar))
    yaz("robots.txt", ROBOTS)

    print("%d sayfa, %d Türkçe yazı, %d İngilizce yazı. %s %d dosya." % (
        len([1 for m, _ in sayfalar if m.get("tur") != "yazi"]), len(yazilar), len(en_yazilar),
        "Değişecek:" if KURU else "Değişen:", len(DEGISEN)))
    for d in DEGISEN:
        print("  " + d)


if __name__ == "__main__":
    main()
