# -*- coding: utf-8 -*-
"""Değişen sayfaları IndexNow ile Bing ve Yandex'e bildirir (Bing, ChatGPT ve Copilot aramasını besler).

    python tools/indexnow.py --degisen          # son commit'te değişen HTML sayfaları
    python tools/indexnow.py --degisen --kuru   # gönderilecek isteği yalnızca yazdırır
    python tools/indexnow.py https://hedefvinc.com/ https://hedefvinc.com/blog/index.html

Anahtar dosyası site kökündedir (<anahtar>.txt) ve GitHub Pages ile yayınlanır. Bir hata olursa yalnızca
uyarı yazar ve 0 ile çıkar; otomatik yayını hiçbir zaman durdurmaz. Python standart kütüphanesi yeterlidir.
"""
import glob, json, os, subprocess, sys, urllib.request

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://hedefvinc.com"
HOST = "hedefvinc.com"
UC = "https://api.indexnow.org/indexnow"
ATLA = ("content/", "tools/", "taslak/", ".github/")


def anahtar():
    for p in glob.glob(os.path.join(KOK, "*.txt")):
        ad = os.path.basename(p)[:-4]
        if len(ad) == 32 and all(c in "0123456789abcdef" for c in ad):
            if open(p, encoding="utf-8").read().strip() == ad:
                return ad
    return None


def url_yolu(rel):
    if rel == "index.html":
        return SITE + "/"
    if rel.endswith("/index.html") and rel.count("/") == 1 and rel.split("/")[0] in ("en", "hizmetler"):
        return SITE + "/" + rel[: -len("index.html")]
    return SITE + "/" + rel


def degisenler():
    try:
        cikti = subprocess.run(["git", "-C", KOK, "diff", "--name-only", "HEAD~1", "HEAD"],
                               capture_output=True, text=True, check=True).stdout
    except Exception as e:  # ilk commit ya da git yok
        print("UYARI  değişen dosyalar okunamadı: %s" % e)
        return []
    urller = []
    for rel in cikti.split():
        rel = rel.strip()
        if rel.endswith(".html") and not rel.startswith(ATLA) and rel != "404.html" \
                and os.path.exists(os.path.join(KOK, rel)):
            urller.append(url_yolu(rel))
    return sorted(set(urller))


def gonder(urller, kuru=False):
    a = anahtar()
    if not a:
        print("UYARI  anahtar dosyası bulunamadı; gönderilmedi.")
        return
    if not urller:
        print("Bildirilecek değişen sayfa yok.")
        return
    veri = {"host": HOST, "key": a, "keyLocation": "%s/%s.txt" % (SITE, a), "urlList": urller[:10000]}
    if kuru:
        print(json.dumps(veri, ensure_ascii=False, indent=1))
        return
    istek = urllib.request.Request(UC, data=json.dumps(veri).encode("utf-8"), method="POST",
                                   headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(istek, timeout=30) as yanit:
            print("IndexNow: %d sayfa bildirildi (HTTP %d)." % (len(urller), yanit.status))
    except Exception as e:
        print("UYARI  IndexNow isteği başarısız: %s" % e)


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    kuru = "--kuru" in argv
    argv = [x for x in argv if x != "--kuru"]
    if "--degisen" in argv:
        urller = degisenler()
    else:
        urller = [u for u in argv if u.startswith(SITE)]
    gonder(urller, kuru)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
