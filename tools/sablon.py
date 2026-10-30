# -*- coding: utf-8 -*-
"""Hedef Vinç site şablonu: üst bölüm, alt bölüm, alt çubuk, görseller, head etiketleri ve yapılandırılmış veri.

Bu dosyayı tools/build_blog.py kullanır. Tek başına çalıştırılmaz.
Telefon, adres, e-posta gibi sabit bilgiler yalnızca burada durur.
"""
import html, json, os, re, struct
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://hedefvinc.com"

# ---------------------------------------------------------------- firma bilgileri (NAP: her yerde aynı)
TEL = "+905337089200"
TEL_YAZI = "0533 708 92 00"
TEL_INT = "+90 533 708 92 00"
TEL_EN = "+905322944863"
TEL_EN_YAZI = "0532 294 48 63"
TEL_EN_INT = "+90 532 294 48 63"
WA = "905337089200"
EPOSTA = "info@hedefvinc.com"
ADRES_SATIR = "Dörttepe Mah. 3. Bulvar No:128/2"
ADRES_TARIF = "Güllük–Güvercinlik arası, Tuzla Kavşağı, Shell arkası"
ADRES_TARIF_EN = "Between Güllük and Güvercinlik, at the Tuzla junction, behind the Shell station"
ADRES_IL = "48200 Milas / Muğla"
HARITA = "https://www.google.com/maps/search/?api=1&query=" + quote("Dörttepe Mah. 3. Bulvar No:128/2 Milas Muğla")
ISLETME_ID = SITE + "/#isletme"
WEBSITE_ID = SITE + "/#website"
LOGO_PNG = SITE + "/assets/img/brand/hedef-vinc-logo.png"
YAZARLAR = [("Ahmet Uğur", SITE + "/hakkimizda.html#ahmet-ugur"), ("Mehmet Uğur", SITE + "/hakkimizda.html#mehmet-ugur")]
SLOGAN = "Vinci kiralayan da tamir eden de biziz."

# ---------------------------------------------------------------- SAHİBİNİN VERECEĞİ BİLGİLER
# Boş bırakılan alanlar sayfalara yazılmaz. Doldurduktan sonra: python tools/build_blog.py
KONUM = None          # Google Haritalar'daki atölye iğnesi, örnek: (37.2391, 27.6012)  [enlem, boylam]
GOOGLE_PROFIL = "https://www.google.com/search?kgmid=/g/11nvf8yjyf"  # Google'daki adı: Hedef Vinç Hidrolik
SAME_AS = [GOOGLE_PROFIL]  # Google İşletme Profili; varsa Instagram, Facebook ... eklenir
DOGRULAMA = {
    "google-site-verification": "",   # Google Search Console > Ayarlar > Sahiplik doğrulama > HTML etiketi
    "msvalidate.01": "",              # Bing Webmaster Tools
    "yandex-verification": "",        # Yandex Webmaster
}

AYLAR = {"tr": [None, "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos",
                "Eylül", "Ekim", "Kasım", "Aralık"],
         "en": [None, "January", "February", "March", "April", "May", "June", "July", "August",
                "September", "October", "November", "December"]}

HIZMETLER = [  # (url, ad, tek satır açıklama) llms.txt, katalog ve OfferCatalog için
    ("/hizmetler/vinc-revizyon-tamir-bakim.html", "Vinç tamiri, revizyon ve bakım",
     "Arıza tespiti, revizyon, periyodik bakım. Atölyede ya da sahada."),
    ("/hizmetler/hiyap-vinc-tamiri.html", "Hiyap vinç tamiri",
     "Kamyon üstü katlanır ve teleskopik bomlu vinçlerde bom, ayak, kumanda ve hidrolik arızaları."),
    ("/hizmetler/vinc-hidrolik-tamiri.html", "Vinç hidrolik tamiri",
     "Pompa, kumanda valfi, silindir keçesi, hortum ve yağ kaçakları."),
    ("/hizmetler/vinc-kiralama.html", "Vinç kiralama",
     "Operatörlü vinç: Milas, Bodrum, Muğla ve çevresi."),
    ("/bolgeler/bodrum-vinc-kiralama.html", "Bodrum vinç kiralama",
     "Villa ve inşaat işleri, dar sokaklar, tekne kaldırma."),
    ("/bolgeler/gulluk-vinc-kiralama.html", "Güllük vinç kiralama",
     "Tekne karaya alma ve indirme, konteyner, yazlık ve yapı işleri."),
    ("/bolgeler/oren-vinc-kiralama.html", "Ören vinç kiralama",
     "Yazlık ve villa işleri, konteyner, otel ekipmanı, tekne."),
    ("/bolgeler/yatagan-vinc-kiralama.html", "Yatağan vinç kiralama",
     "Tesis ve sanayi işleri; ocak ve sahada hiyap ve iş makinası tamiri."),
    ("/bolgeler/didim-vinc-kiralama.html", "Didim vinç kiralama",
     "Villa ve site işleri, konteyner, tesis ekipmanı; Milas'tan planlı."),
    ("/bolgeler/mugla-vinc-tamiri.html", "Muğla vinç ve hiyap tamiri",
     "Muğla ilçeleri ve yakın Aydın'da vinç ve hiyap tamiri; atölyede ya da sahada."),
    ("/bolgeler/bodrum-vinc-tamiri.html", "Bodrum vinç ve hiyap tamiri",
     "Şantiyedeki hiyaplar ve tekne üstü vinçler; sahada ya da atölyede."),
    ("/hizmetler/is-makinasi-tamir-bakim.html", "İş makinası tamir ve bakım",
     "Ekskavatör, yükleyici, forklift; mekanik ve hidrolik onarım."),
    ("/hizmetler/pres-hortum.html", "Pres hortum",
     "Hidrolik hortum ölçüye göre kesilir, rekoru takılıp preslenir."),
    ("/hizmetler/hidrolik-yedek-parca.html", "Hidrolik yedek parça",
     "Pompa, valf, silindir, keçe takımı, rekor ve hortum temini."),
    ("/hizmetler/torna-isleri.html", "Torna işleri ve parça imalatı",
     "Pim, burç, mil, flanş; numuneden ya da ölçüden imalat."),
    ("/hizmetler/kaynak-isleri.html", "Kaynak işleri",
     "Bom ve şase kaynağı, çelik konstrüksiyon, sahada kaynak."),
    ("/hizmetler/kamyon-sase-giydirme.html", "Kamyon şase düzeltme ve giydirme",
     "Şase doğrultma, uzatma, kısaltma ve güçlendirme."),
    ("/hizmetler/konteyner-satis-kiralama.html", "Konteyner satış ve kiralama",
     "Sıfır ve 2. el konteyner; vinçle teslim ve yerleştirme."),
]
BILGI_ALANLARI = ["Vinç tamiri", "Vinç revizyonu", "Hiyap tamiri", "Vinç hidrolik sistemleri", "Pres hortum",
                  "Vinç kiralama", "Tekne kaldırma"]


def esc(t):
    """Öznitelik ve metin için kaçış; tek tırnak okunur kalsın diye dokunulmaz."""
    return html.escape(str(t), quote=False).replace('"', "&quot;")


def tarih_yazi(iso, dil="tr"):
    y, m, d = (int(x) for x in iso[:10].split("-"))
    return "%d %s %d" % (d, AYLAR["en" if dil == "en" else "tr"][m], y)


def wa_link(mesaj):
    return "https://wa.me/%s?text=%s" % (WA, quote(mesaj, safe=""))


# ---------------------------------------------------------------- görseller

_MANIFEST = None
BOS_GORSEL = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
MOBIL = "(max-width: 859.98px)"
MASAUSTU = "(min-width: 860px)"


def manifest():
    global _MANIFEST
    if _MANIFEST is None:
        p = os.path.join(ROOT, "assets", "img", "r", "manifest.json")
        _MANIFEST = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    return _MANIFEST


def gorsel_yolu(p):
    """'real_ones/x.jpg', 'assets/img/x.jpg' veya '/assets/img/x.jpg' -> 'real_ones/x.jpg'"""
    p = (p or "").strip().lstrip("/")
    if p.startswith("assets/img/"):
        p = p[len("assets/img/"):]
    return p


def jpeg_boyut(yol):
    """Pillow olmadan JPEG/PNG genişlik-yükseklik okur (CI ortamı için)."""
    with open(yol, "rb") as f:
        bas = f.read(26)
        if bas[:8] == b"\x89PNG\r\n\x1a\n":
            return struct.unpack(">II", bas[16:24])
        f.seek(2)
        while True:
            b = f.read(1)
            while b and b != b"\xff":
                b = f.read(1)
            while b == b"\xff":
                b = f.read(1)
            if not b:
                return None
            m = b[0]
            if m in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                f.read(3)
                h, w = struct.unpack(">HH", f.read(4))
                return w, h
            n = struct.unpack(">H", f.read(2))[0]
            f.seek(n - 2, 1)


def gorsel_var(p):
    p = gorsel_yolu(p)
    return p in manifest() or os.path.exists(os.path.join(ROOT, "assets", "img", p))


def gorsel_kaynak(p):
    """(src, srcset, w, h, buyuk_url, buyuk_w, buyuk_h) döndürür."""
    p = gorsel_yolu(p)
    m = manifest().get(p)
    if m:
        v = m["v"]
        src = "/assets/img/" + v[0]["src"]
        srcset = ", ".join("/assets/img/%s %dw" % (x["src"], x["w"]) for x in v)
        return src, srcset, v[0]["w"], v[0]["h"], "/assets/img/" + v[-1]["src"], v[-1]["w"], v[-1]["h"]
    yol = os.path.join(ROOT, "assets", "img", p)
    wh = jpeg_boyut(yol) if os.path.exists(yol) else None
    w, h = wh if wh else (1200, 800)
    return "/assets/img/" + p, None, w, h, "/assets/img/" + p, w, h


def img(p, alt, sizes="100vw", eager=False, cls=None, sadece=None):
    """sadece='mobil' ya da 'masaustu': görsel öbür ekranda hiç indirilmez (picture + boş kaynak)."""
    src, srcset, w, h, _, _, _ = gorsel_kaynak(p)
    a = ['src="%s"' % src]
    if srcset:
        a.append('srcset="%s" sizes="%s"' % (srcset, sizes))
    a.append('width="%d" height="%d"' % (w, h))
    a.append('alt="%s"' % esc(alt))
    if eager:
        a.append('fetchpriority="high"')
    else:
        a.append('loading="lazy" decoding="async"')
    if cls:
        a.append('class="%s"' % cls)
    etiket = "<img %s>" % " ".join(a)
    if sadece:
        medya = MASAUSTU if sadece == "mobil" else MOBIL
        return '<picture><source media="%s" srcset="%s">%s</picture>' % (medya, BOS_GORSEL, etiket)
    return etiket


def foto(p, alt, yazi=None, sizes="100vw", eager=False, cls="foto", sadece=None):
    cap = "<figcaption>%s</figcaption>" % yazi if yazi else ""
    return '<figure class="%s">%s%s</figure>' % (cls, img(p, alt, sizes, eager, sadece=sadece), cap)


def og_bilgi(p):
    """(mutlak url, genişlik, yükseklik)"""
    if p.startswith("http"):
        return p, None, None
    if p.startswith("/assets/img/og/"):
        return SITE + p, 1200, 630
    k = gorsel_kaynak(p)
    return SITE + k[4], k[5], k[6]


def og_url(p):
    return og_bilgi(p)[0]


# ---------------------------------------------------------------- simgeler

IKON_TEL = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 '
            '19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 '
            '1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.9.6 2.8.7a2 2 0 0 '
            '1 1.7 2z"/></svg>')
IKON_WA = ('<svg width="19" height="19" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.5 '
           '14.4c-.3-.1-1.8-.9-2-1-.3-.1-.5-.1-.7.2-.2.3-.8 1-.9 1.2-.2.2-.3.2-.6.1-.3-.1-1.3-.5-2.4-1.5-.9-.8-1.5-1.8'
           '-1.7-2.1-.2-.3 0-.5.1-.6l.4-.5c.1-.2.2-.3.3-.5.1-.2 0-.4 0-.5l-.9-2.2c-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8'
           '.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.1.2 2.1 3.2 5.1 4.5.7.3 1.3.5 1.7.6.7.2 1.4.2 1.9.1.6-.1 1.8-.7 2-1.4'
           '.2-.7.2-1.3.2-1.4-.1-.1-.3-.2-.6-.3M12 21.8a9.9 9.9 0 0 1-5-1.4l-.4-.2-3.7 1 1-3.6-.2-.4A9.9 9.9 0 1 1 12 '
           '21.8m8.4-18.3A11.8 11.8 0 0 0 12 0C5.5 0 .2 5.3.2 11.9c0 2.1.5 4.1 1.6 5.9L0 24l6.3-1.7a11.9 11.9 0 0 0 '
           '5.7 1.5c6.6 0 11.9-5.3 11.9-11.9 0-3.2-1.2-6.2-3.5-8.4"/></svg>')

# ---------------------------------------------------------------- metinler

T = {
    "tr": {
        "ana": "Ana sayfa", "menu": "Menü", "ara": "Ara", "hemen_ara": "Hemen ara",
        "wa": "WhatsApp", "wa_yaz": "WhatsApp'tan yazın", "dil_kisa": "EN", "dil_ad": "English",
        "atla": "İçeriğe geç", "ana_menu": "Ana menü", "hizli": "Hızlı iletişim",
        "wa_varsayilan": "Merhaba, Hedef Vinç'e web sitesinden yazıyorum.",
        "sss": "Sık sorulan sorular",
    },
    "en": {
        "ana": "Home", "menu": "Menu", "ara": "Call", "hemen_ara": "Call now",
        "wa": "WhatsApp", "wa_yaz": "Message on WhatsApp", "dil_kisa": "TR", "dil_ad": "Türkçe",
        "atla": "Skip to content", "ana_menu": "Main menu", "hizli": "Quick contact",
        "wa_varsayilan": "Hello, I'm contacting Hedef Vinç from your website.",
        "sss": "Frequently asked questions",
    },
}

NAV = {
    "tr": [("tamir", "Vinç tamiri", "/hizmetler/vinc-revizyon-tamir-bakim.html"),
           ("kiralama", "Vinç kiralama", "/hizmetler/vinc-kiralama.html"),
           ("hizmetler", "Tüm hizmetler", "/hizmetler/"),
           ("blog", "Blog", "/blog/index.html"),
           ("hakkimizda", "Hakkımızda", "/hakkimizda.html"),
           ("iletisim", "İletişim", "/iletisim.html")],
    "en": [("tamir", "Crane repair", "/en/services/crane-repair-maintenance.html"),
           ("kiralama", "Crane rental", "/en/services/crane-rental.html"),
           ("hizmetler", "All services", "/en/#services"),
           ("blog", "Blog", "/en/blog/index.html"),
           ("hakkimizda", "About", "/en/about.html"),
           ("iletisim", "Contact", "/en/contact.html")],
}

FONTS = ("https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@112,800"
         "&family=IBM+Plex+Mono:wght@500&family=IBM+Plex+Sans:wght@400;600&display=swap")


def btn_ara(dil="tr", cls="btn btn--sari", metin=None):
    if dil == "en":
        return '<a class="%s" href="tel:%s">%s%s</a>' % (cls, TEL_EN, IKON_TEL, metin or "Call %s" % TEL_EN_INT)
    return '<a class="%s" href="tel:%s">%s%s</a>' % (cls, TEL, IKON_TEL, metin or "Ara: %s" % TEL_YAZI)


def btn_wa(mesaj, dil="tr", cls="btn btn--wa", metin=None):
    return '<a class="%s" href="%s">%s%s</a>' % (cls, esc(wa_link(mesaj)), IKON_WA, metin or T[dil]["wa_yaz"])


def adres_html(dil="tr"):
    """Adres bloğu: her sayfada aynı üç satır (İngilizce sayfalarda ek bir yön tarifi satırı)."""
    ek = '<br><span lang="en">%s</span>' % ADRES_TARIF_EN if dil == "en" else ""
    il = ADRES_IL + (", Türkiye" if dil == "en" else "")
    return '<address class="adres">%s<br>%s<br>%s%s</address>' % (ADRES_SATIR, ADRES_TARIF, il, ek)


# ---------------------------------------------------------------- yapılandırılmış veri

ALAN = [("City", "Milas"), ("City", "Bodrum"), ("AdministrativeArea", "Muğla"),
        ("AdministrativeArea", "Aydın"), ("AdministrativeArea", "İzmir")]
ISLETME_TURU = ["HomeAndConstructionBusiness", "AutoRepair"]


def isletme_ref():
    return {"@type": ISLETME_TURU, "@id": ISLETME_ID, "name": "Hedef Vinç"}


def kisi_ref(ad, kimlik):
    return {"@type": "Person", "@id": kimlik, "name": ad, "url": SITE + "/hakkimizda.html"}


def kisi_schema():
    return [{"@type": "Person", "@id": kimlik, "name": ad, "jobTitle": "Kurucu ortak",
             "worksFor": {"@id": ISLETME_ID}, "url": SITE + "/hakkimizda.html"} for ad, kimlik in YAZARLAR]


def website_schema():
    return {"@type": "WebSite", "@id": WEBSITE_ID, "url": SITE + "/", "name": "Hedef Vinç",
            "alternateName": ["Retrofit Hedef Crane", "hedefvinc.com"], "inLanguage": "tr-TR",
            "publisher": {"@id": ISLETME_ID}}


def isletme_schema():
    gorseller = ["real_ones/atolye-revizyonu-biten-katlanir-bom-vinc.jpg", "hedef-vinc-kamyon.jpg",
                 "real_ones/retrofit-hedef-crane-tekne-uzeri-deniz-vinci.jpg", "atolye-torna.jpg"]
    d = {
        "@type": ISLETME_TURU,
        "@id": ISLETME_ID,
        "name": "Hedef Vinç",
        "alternateName": ["Retrofit Hedef Crane", "Hedef Vinç Hidrolik", "Hedef Vinç Retrofit Crane"],
        "slogan": SLOGAN,
        "description": ("Milas'ta 2005'ten beri vinç tamiri, revizyon ve bakım ile operatörlü vinç kiralama. "
                        "Tuzla Kavşağı'nda kendi atölyesi; Milas, Bodrum, Muğla, Aydın ve İzmir'e 7/24 hizmet."),
        "url": SITE + "/",
        "logo": {"@type": "ImageObject", "url": LOGO_PNG, "width": 1200, "height": 279},
        "image": [og_url(g) for g in gorseller],
        "telephone": TEL_INT,
        "email": EPOSTA,
        "contactPoint": [
            {"@type": "ContactPoint", "telephone": TEL_INT, "email": EPOSTA, "contactType": "customer service",
             "availableLanguage": ["Turkish"], "hoursAvailable": {
                 "@type": "OpeningHoursSpecification",
                 "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                 "opens": "00:00", "closes": "23:59"}},
            {"@type": "ContactPoint", "telephone": TEL_EN_INT, "email": EPOSTA, "contactType": "customer service",
             "availableLanguage": ["English", "Turkish"]},
        ],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": ADRES_SATIR,
            "description": ADRES_TARIF,
            "addressLocality": "Milas",
            "addressRegion": "Muğla",
            "postalCode": "48200",
            "addressCountry": "TR",
        },
        "hasMap": HARITA,
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "opens": "00:00", "closes": "23:59"}],
        "areaServed": [{"@type": t, "name": n} for t, n in ALAN],
        "founder": [{"@id": kimlik} for _, kimlik in YAZARLAR],
        "foundingDate": "2005",
        "knowsLanguage": ["tr", "en"],
        "knowsAbout": BILGI_ALANLARI,
        "hasOfferCatalog": {
            "@type": "OfferCatalog", "name": "Hedef Vinç hizmetleri",
            "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": ad, "url": SITE + u}}
                                for u, ad, _ in HIZMETLER]},
    }
    if KONUM:
        d["geo"] = {"@type": "GeoCoordinates", "latitude": KONUM[0], "longitude": KONUM[1]}
    if SAME_AS:
        d["sameAs"] = list(SAME_AS)
    return d


def graf(dugumler):
    return {"@context": "https://schema.org", "@graph": dugumler}


def hizmet_schema(h, url, dil):
    d = {"@context": "https://schema.org", "@type": "Service", "@id": url + "#hizmet", "name": h["ad"],
         "serviceType": h.get("tur", h["ad"]), "description": h.get("aciklama", ""), "url": url,
         "provider": isletme_ref(), "areaServed": [{"@type": t, "name": n} for t, n in ALAN], "inLanguage": dil}
    if h.get("gorsel"):
        d["image"] = og_url(h["gorsel"])
    return d


def kirinti_schema(kirinti, dil):
    items = [{"@type": "ListItem", "position": 1, "name": T[dil]["ana"],
              "item": SITE + ("/en/" if dil == "en" else "/")}]
    for i, (ad, yol) in enumerate(kirinti, 2):
        it = {"@type": "ListItem", "position": i, "name": ad}
        if yol:
            it["item"] = SITE + yol
        items.append(it)
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}


def metin_duz(t):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", t))).strip()


def sss_schema(sss):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": metin_duz(x["q"]),
                            "acceptedAnswer": {"@type": "Answer", "text": metin_duz(x["a"])}} for x in sss]}


def ld(obj):
    s = json.dumps(obj, ensure_ascii=False, indent=1)
    s = s.replace("</", "<\\/")
    return '<script type="application/ld+json">\n%s\n</script>' % s


# ---------------------------------------------------------------- parçalar

def kirinti_html(kirinti, dil):
    li = ['<li><a href="%s">%s</a></li>' % ("/en/" if dil == "en" else "/", T[dil]["ana"])]
    for ad, yol in kirinti:
        if yol:
            li.append('<li><a href="%s">%s</a></li>' % (yol, esc(ad)))
        else:
            li.append('<li aria-current="page">%s</li>' % esc(ad))
    return '<ol class="yol" aria-label="%s">%s</ol>' % ("Breadcrumb" if dil == "en" else "Sayfa yolu", "".join(li))


def ust(dil, aktif, es_yol):
    t = T[dil]
    ana = "/en/" if dil == "en" else "/"
    linkler = []
    for k, ad, yol in NAV[dil]:
        cur = ' aria-current="page"' if k == aktif else ""
        linkler.append('<a href="%s"%s>%s</a>' % (yol, cur, ad))
    hedef_dil = "tr" if dil == "en" else "en"
    if dil == "en":
        tel, tel_yazi, ara_etiket = TEL_EN, TEL_EN_INT, "Call the English line: " + TEL_EN_INT
        nav_alt = ('<div class="nav-alt"><a href="tel:%s">Turkish line, 24/7: %s</a>'
                   '<a href="%s" hreflang="tr" lang="tr">Türkçe site</a></div>' % (TEL, TEL_INT, es_yol))
        logo_alt = "Hedef Vinç, Retrofit Crane, since 2005"
    else:
        tel, tel_yazi, ara_etiket = TEL, TEL_YAZI, "Ara: " + TEL_YAZI
        nav_alt = ('<div class="nav-alt"><a href="tel:%s" lang="en">English line: %s</a>'
                   '<a href="%s" hreflang="en" lang="en">English site</a></div>' % (TEL_EN, TEL_EN_YAZI, es_yol))
        logo_alt = "Hedef Vinç, Retrofit Crane, 2005'ten beri"
    return """<a class="atla" href="#icerik">{atla}</a>
<header class="hdr">
 <div class="wrap hdr__in">
  <a class="hdr__logo" href="{ana}"><img class="uzun" src="/assets/img/brand/hedef-vinc-logo.svg" width="198" height="46" alt="{logo_alt}"><img class="kisa" src="/assets/img/brand/hedef-vinc-logo-kisa.svg" width="181" height="34" alt="{logo_alt}"></a>
  <nav class="hdr__nav" id="menu" aria-label="{ana_menu}">{linkler}{nav_alt}</nav>
  <div class="hdr__act">
   <a class="dil" href="{es}" hreflang="{hd}" lang="{hd}" title="{dil_ad}">{dil_kisa}</a>
   <a class="btn btn--sari hdr__tel" href="tel:{tel}">{ikon}<span>{tel_yazi}</span></a>
   <a class="hdr__ara" href="tel:{tel}" aria-label="{ara_etiket}">{ikon}</a>
   <button class="hdr__menu" type="button" aria-expanded="false" aria-controls="menu"><i></i>{menu}</button>
  </div>
 </div>
</header>""".format(atla=t["atla"], ana=ana, logo_alt=esc(logo_alt), ana_menu=t["ana_menu"],
                    linkler="".join(linkler), nav_alt=nav_alt, es=es_yol, hd=hedef_dil, dil_ad=t["dil_ad"],
                    dil_kisa=t["dil_kisa"], tel=tel, tel_yazi=tel_yazi, ara_etiket=esc(ara_etiket), ikon=IKON_TEL,
                    menu=t["menu"])


def alt_cubuk(dil, wa_mesaj=None):
    t = T[dil]
    ara_tel, ara = (TEL_EN, "Call") if dil == "en" else (TEL, "Ara")
    return ('<nav class="altbar" aria-label="%s"><a href="tel:%s">%s<span>%s</span></a>'
            '<a href="%s">%s<span>WhatsApp</span></a></nav>') % (
        t["hizli"], ara_tel, IKON_TEL, ara, esc(wa_link(wa_mesaj or t["wa_varsayilan"])), IKON_WA)


def _grup(baslik, linkler):
    li = "".join('<li><a href="%s"%s>%s</a></li>' % (u, (' ' + ek) if ek else "", ad) for u, ad, ek in linkler)
    return ('<details class="katla ftr__grup" open><summary><h2>%s</h2></summary><ul>%s</ul></details>'
            % (baslik, li))


def alt(dil):
    if dil == "en":
        gruplar = [
            _grup("Crane repair", [("/en/services/crane-repair-maintenance.html", "Crane repair &amp; maintenance", ""),
                                   ("/en/services/hydraulic-hose-pressing.html", "Hydraulic hose pressing", ""),
                                   ("/en/services/hydraulic-spare-parts.html", "Hydraulic spare parts", "")]),
            _grup("Crane rental", [("/en/services/crane-rental.html", "Crane rental", ""),
                                   ("/en/services/container-sales-rental.html", "Container sales &amp; rental", ""),
                                   ("/en/blog/boat-lifting-bodrum.html", "Boat lifting in Bodrum", "")]),
            _grup("Workshop", [("/en/services/heavy-equipment-repair.html", "Heavy equipment repair", ""),
                               ("/en/services/custom-machining.html", "Custom machining", ""),
                               ("/en/services/welding-services.html", "Welding", ""),
                               ("/en/services/truck-chassis-works.html", "Truck chassis works", "")]),
            _grup("Hedef Vinç", [("/en/about.html", "About us", ""), ("/en/contact.html", "Contact &amp; directions", ""),
                                 ("/en/blog/index.html", "Blog", ""), ("/", "Türkçe site", 'hreflang="tr" lang="tr"')]),
        ]
        kim = ('<p class="ftr__not">Crane repair and operated crane rental from our own workshop in Milas, run by '
               'Ahmet Uğur and Mehmet Uğur since 2005.</p>')
        telefon = ('<p class="ftr__tel"><a href="tel:%s">%s</a> English<br><a href="tel:%s">%s</a> Turkish, 24/7</p>'
                   % (TEL_EN, TEL_EN_INT, TEL, TEL_INT))
        harita, alt_satir = "Get directions", "Open 24/7, emergencies included"
        ana = "/en/"
    else:
        gruplar = [
            _grup("Vinç tamiri", [("/hizmetler/vinc-revizyon-tamir-bakim.html", "Vinç tamiri ve revizyon", ""),
                                  ("/hizmetler/hiyap-vinc-tamiri.html", "Hiyap vinç tamiri", ""),
                                  ("/hizmetler/vinc-hidrolik-tamiri.html", "Vinç hidrolik tamiri", "")]),
            _grup("Vinç kiralama", [("/hizmetler/vinc-kiralama.html", "Milas vinç kiralama", ""),
                                    ("/bolgeler/bodrum-vinc-kiralama.html", "Bodrum vinç kiralama", ""),
                                    ("/hizmetler/konteyner-satis-kiralama.html", "Konteyner satış ve kiralama", "")]),
            _grup("Atölye", [("/hizmetler/is-makinasi-tamir-bakim.html", "İş makinası tamir", ""),
                             ("/hizmetler/pres-hortum.html", "Pres hortum", ""),
                             ("/hizmetler/hidrolik-yedek-parca.html", "Hidrolik yedek parça", ""),
                             ("/hizmetler/torna-isleri.html", "Torna işleri", ""),
                             ("/hizmetler/kaynak-isleri.html", "Kaynak işleri", ""),
                             ("/hizmetler/kamyon-sase-giydirme.html", "Kamyon şase giydirme", "")]),
            _grup("Hedef Vinç", [("/hakkimizda.html", "Hakkımızda", ""), ("/iletisim.html", "İletişim ve adres", ""),
                                 ("/blog/index.html", "Blog", ""), ("/hizmetler/", "Tüm hizmetler", ""),
                                 ("/en/", "English", 'hreflang="en" lang="en"')]),
        ]
        kim = ('<p class="ftr__not">Ahmet Uğur ve Mehmet Uğur\'un işlettiği atölye. 2005\'ten beri Milas\'ta vinç '
               'tamiri ve vinç kiralama.</p>')
        telefon = ('<p class="ftr__tel"><a href="tel:%s">%s</a> 7/24<br><a href="tel:%s">%s</a> <span lang="en">English</span></p>'
                   % (TEL, TEL_YAZI, TEL_EN, TEL_EN_YAZI))
        harita, alt_satir = "Yol tarifi al", "7/24 açık, acil işler dahil"
        ana = "/"
    return """<footer class="ftr">
 <div class="wrap">
  <div class="ftr__in">
   <div class="ftr__kim">
    <a class="ftr__logo" href="{ana}"><img src="/assets/img/brand/hedef-vinc-logo-beyaz.svg" width="220" height="51" alt="Hedef Vinç, Retrofit Crane" loading="lazy"></a>
    {kim}
    {adres}
    {telefon}
    <p class="ftr__tel"><a href="mailto:{eposta}">{eposta}</a><br><a href="{harita_url}">{harita}</a> · <a href="{google}">{google_ad}</a></p>
   </div>
   <div class="ftr__kol">{g0}{g1}</div>
   <div class="ftr__kol">{g2}</div>
   <div class="ftr__kol">{g3}</div>
  </div>
  <div class="ftr__alt"><span>Hedef Vinç · Retrofit Hedef Crane · 2005</span><span>{alt_satir}</span></div>
 </div>
</footer>""".format(ana=ana, kim=kim, adres=adres_html(dil), telefon=telefon, eposta=EPOSTA, harita_url=esc(HARITA),
                    google=esc(GOOGLE_PROFIL), google_ad="Google profile" if dil == "en" else "Google profilimiz",
                    harita=harita, g0=gruplar[0], g1=gruplar[1], g2=gruplar[2], g3=gruplar[3], alt_satir=alt_satir)


def son_bant(dil, tur="genel", wa_mesaj=None, baslik=None, metin=None):
    """Sayfa sonundaki çağrı bandı. baslik/metin verilirse türün varsayılan metinlerinin yerine geçer."""
    if dil == "en":
        h2 = {"tamir": "Crane out of action? Send us a photo or a short video.",
              "kiralama": "Need a crane? Tell us the load, the address and the day.",
              "genel": "Crane repair or crane rental: one call."}[tur]
        p = "Our English line is there for foreign customers. For photos and videos, WhatsApp is the quickest way."
        hat = ('<a href="tel:%s"><span class="ne">English line</span><span class="no">%s</span></a>'
               '<a href="tel:%s"><span class="ne">Turkish line · 24/7</span><span class="no">%s</span></a>'
               % (TEL_EN, TEL_EN_INT, TEL, TEL_INT))
        btn = btn_ara("en") + btn_wa(wa_mesaj or T["en"]["wa_varsayilan"], "en")
    else:
        h2 = {"tamir": "Vinciniz arızalı mı? Fotoğrafını ya da kısa bir videosunu gönderin.",
              "kiralama": "Vinç mi lazım? Yükü, adresi ve günü söyleyin.",
              "genel": "Vinç tamiri ya da vinç kiralama: tek telefon."}[tur]
        p = {"tamir": "Arızayı telefonda dinler, gerekirse sahaya geliriz. Kapsamlı işleri Tuzla Kavşağı'ndaki atölyede yaparız.",
             "kiralama": "Uygun vinci ve operatörü planlarız. Gerekiyorsa önce yerinde bakarız. Fiyatı işi gördükten sonra net söyleriz.",
             "genel": "Telefonlarımız gece gündüz açık. Yabancı müşterilerimiz için İngilizce hattımız var."}[tur]
        hat = ('<a href="tel:%s"><span class="ne">Türkçe hat · 7/24</span><span class="no">%s</span></a>'
               '<a href="tel:%s"><span class="ne" lang="en">English line</span><span class="no">%s</span></a>'
               % (TEL, TEL_YAZI, TEL_EN, TEL_EN_YAZI))
        btn = btn_ara("tr") + btn_wa(wa_mesaj or T["tr"]["wa_varsayilan"], "tr")
    h2 = baslik or h2
    p = metin or p
    return """<section class="son" aria-labelledby="son-baslik">
 <div class="wrap son__in">
  <div>
   <h2 id="son-baslik">{h2}</h2>
   <p>{p}</p>
   <div class="btnlar">{btn}</div>
  </div>
  <div class="hatlar">{hat}</div>
 </div>
</section>""".format(h2=h2, p=p, btn=btn, hat=hat)


def sss_html(sss, baslik, dil="tr"):
    ic = "\n".join('<details><summary>%s</summary><div class="cevap">%s</div></details>' % (x["q"], x["a"]) for x in sss)
    return """<section class="bant bant--beyaz" aria-labelledby="sss-baslik">
 <div class="wrap">
  <div class="bant__bas"><h2 id="sss-baslik">{b}</h2></div>
  <div class="sss">
{ic}
  </div>
 </div>
</section>""".format(b=baslik or T[dil]["sss"], ic=ic)


def sayfa(meta, govde):
    """Tam HTML belgesi. meta: baslik, aciklama, dil, kanonik, es (hreflang eşi), nav, gorsel, gorsel_alt,
    ld (liste), tur ('website'/'article'), noindex, wa."""
    dil = meta.get("dil", "tr")
    kanonik = meta["kanonik"]
    alt_link = []
    if meta.get("es"):
        tr_url, en_url = (kanonik, SITE + meta["es"]) if dil == "tr" else (SITE + meta["es"], kanonik)
        alt_link = ['<link rel="alternate" hreflang="tr" href="%s">' % tr_url,
                    '<link rel="alternate" hreflang="en" href="%s">' % en_url,
                    '<link rel="alternate" hreflang="x-default" href="%s">' % tr_url]
    es_yol = meta.get("es") or ("/" if dil == "en" else "/en/")
    robots = "noindex" if meta.get("noindex") else "index, follow, max-image-preview:large"
    og, og_w, og_h = og_bilgi(meta.get("gorsel") or ("/assets/img/og/hedef-vinc-og-en.jpg" if dil == "en"
                                                       else "/assets/img/og/hedef-vinc-og.jpg"))
    og_alt = meta.get("gorsel_alt") or meta.get("og_baslik") or meta["baslik"]
    ogb = esc(meta.get("og_baslik") or meta["baslik"])
    ek = ['<meta property="og:image:width" content="%d">' % og_w,
          '<meta property="og:image:height" content="%d">' % og_h] if og_w else []
    ek.append('<meta property="og:image:alt" content="%s">' % esc(og_alt))
    dogrula = "".join('<meta name="%s" content="%s">\n' % (k, esc(v)) for k, v in DOGRULAMA.items() if v)
    lds = "\n".join(ld(x) for x in meta.get("ld", []))
    return """<!DOCTYPE html>
<html lang="{dil}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{baslik}</title>
<meta name="description" content="{aciklama}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{kanonik}">
{alt_link}
{dogrula}<meta property="og:type" content="{ogtur}">
<meta property="og:site_name" content="Hedef Vinç">
<meta property="og:locale" content="{loc}">
<meta property="og:locale:alternate" content="{loc_alt}">
<meta property="og:title" content="{ogbaslik}">
<meta property="og:description" content="{aciklama}">
<meta property="og:url" content="{kanonik}">
<meta property="og:image" content="{og}">
{og_ek}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{ogbaslik}">
<meta name="twitter:description" content="{aciklama}">
<meta name="twitter:image" content="{og}">
<meta name="twitter:image:alt" content="{og_alt}">
<meta name="theme-color" content="#06183A">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/svg+xml" href="/assets/img/brand/hedef-vinc-ikon.svg">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{fonts}">
<link rel="stylesheet" href="/assets/css/style.css">
{lds}
</head>
<body>
{ust}
<main id="icerik">
{govde}
</main>
{alt}
{altbar}
<script src="/assets/js/main.js" defer></script>
</body>
</html>
""".format(dil=dil, baslik=esc(meta["baslik"]), aciklama=esc(meta["aciklama"]), robots=robots, kanonik=kanonik,
           alt_link="\n".join(alt_link), dogrula=dogrula, ogtur=meta.get("tur", "website"),
           loc="en_GB" if dil == "en" else "tr_TR", loc_alt="tr_TR" if dil == "en" else "en_GB",
           ogbaslik=ogb, og=og, og_ek="\n".join(ek), og_alt=esc(og_alt), fonts=esc(FONTS), lds=lds,
           ust=ust(dil, meta.get("nav"), es_yol), govde=govde.strip(), alt=alt(dil),
           altbar=alt_cubuk(dil, meta.get("wa")))
