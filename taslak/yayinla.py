# -*- coding: utf-8 -*-
"""Kuyruktaki blog taslaklarını yayına alır.

    python taslak/yayinla.py --list    -> bekleyen taslakları sırasıyla listeler
    python taslak/yayinla.py           -> sıradaki 1 taslağı bugünün tarihiyle yayınlar
    python taslak/yayinla.py 3         -> sıradaki 3 taslağı yayınlar
    python taslak/yayinla.py --gunluk  -> bugün henüz yayın yapılmadıysa sıradaki 1 taslağı yayınlar
                                          (GitHub Actions her gün bunu çalıştırır)

Repo kökünden çalıştırın. Tarih her zaman bugündür (Türkiye saati, UTC+3); ileri tarihli yazı oluşmaz.
Yayınlanan taslak content/blog/<slug>.json olarak taşınır, datePublished ve dateModified bugüne ayarlanır,
taslak/yayin-gunlugu.txt dosyasına "YYYY-AA-GG slug" satırı eklenir ve tools/build_blog.py çalıştırılır
(yazı sayfası, blog listesi, ilgili hizmet sayfaları, sitemap.xml, llms.txt). Sonra commit + push yeterli.

Taslaklar numara sırasıyla yayınlanır; bir taslak yalnızca kendinden önceki numaralara bağlantı verebilir,
bu yüzden sırayı değiştirmeyin. Taslak doğrulamadan geçmezse yayınlanmaz.
"""
import datetime, glob, json, os, subprocess, sys

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KUYRUK = os.path.join(KOK, "taslak", "kuyruk")
YAZILAR = os.path.join(KOK, "content", "blog")
GUNLUK = os.path.join(KOK, "taslak", "yayin-gunlugu.txt")
TR_SAAT = datetime.timezone(datetime.timedelta(hours=3))  # Türkiye 2016'dan beri sabit UTC+3

sys.path.insert(0, os.path.join(KOK, "taslak"))
import kontrol  # noqa: E402


def bugun():
    zorla = os.environ.get("YAYIN_TARIHI")  # yalnızca deneme için: YAYIN_TARIHI=2026-10-23
    if zorla:
        return datetime.date.fromisoformat(zorla)
    return datetime.datetime.now(TR_SAAT).date()


def bekleyenler():
    return sorted(glob.glob(os.path.join(KUYRUK, "*.json")),
                  key=lambda p: (int(os.path.basename(p).split("-", 1)[0]), p))


def oku(p):
    with open(p, "rb") as f:
        return json.loads(f.read().decode("utf-8"))


def yaz_json(p, d):
    veri = (json.dumps(d, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    with open(p, "wb") as f:
        f.write(veri)


def tarihli(d, iso):
    """Alan sırasını koruyarak tarihleri 'category' alanının arkasına yerleştirir."""
    out = {}
    for k, v in d.items():
        if k in ("datePublished", "dateModified"):
            continue
        out[k] = v
        if k == "category":
            out["datePublished"] = iso
            out["dateModified"] = iso
    out.setdefault("datePublished", iso)
    out.setdefault("dateModified", iso)
    return out


def gunluk_oku():
    if not os.path.exists(GUNLUK):
        return []
    with open(GUNLUK, "rb") as f:
        return [l.split() for l in f.read().decode("utf-8").splitlines() if l.strip()]


def main(arg):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    dosyalar = bekleyenler()
    if arg == "--list":
        print("Bekleyen %d taslak:" % len(dosyalar))
        for p in dosyalar:
            d = oku(p)
            print("  %-48s hedef: %s" % (os.path.basename(p)[:-5], d.get("_hedef", "")))
        return 0

    iso = bugun().isoformat()
    if arg == "--gunluk":
        if any(s and s[0] == iso for s in gunluk_oku()):
            print("Bugün (%s) zaten yayın yapıldı." % iso)
            return 0
        arg = "1"
    try:
        n = int(arg)
    except ValueError:
        print(__doc__)
        return 2
    if not dosyalar:
        print("Bekleyen taslak yok.")
        return 0

    yayinlanan = []
    for p in dosyalar[:n]:
        hata, _ = kontrol.kontrol([p], sessiz=True)
        if hata:
            print("DURDU  %s doğrulamadan geçmedi; yayınlanmadı." % os.path.basename(p))
            break
        d = oku(p)
        hedef = os.path.join(YAZILAR, d["slug"] + ".json")
        if os.path.exists(hedef):
            print("DURDU  content/blog/%s.json zaten var." % d["slug"])
            break
        os.makedirs(YAZILAR, exist_ok=True)
        yaz_json(hedef, tarihli(d, iso))
        os.remove(p)
        with open(GUNLUK, "ab") as f:
            f.write(("%s %s\n" % (iso, d["slug"])).encode("utf-8"))
        yayinlanan.append(d["slug"])
        print("  yayınlandı  %s  (%s)" % (d["slug"], iso))

    if yayinlanan:
        r = subprocess.run([sys.executable, os.path.join(KOK, "tools", "build_blog.py")], cwd=KOK)
        if r.returncode:
            return r.returncode
    print("Kalan taslak: %d" % len(bekleyenler()))
    if yayinlanan:
        print('Şimdi: git add -A && git commit -m "Blog: yeni yazı" && git push')
    return 0 if yayinlanan or not dosyalar[:n] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "1"))
