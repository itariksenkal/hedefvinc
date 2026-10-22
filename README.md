# Hedef Vinç · hedefvinc.com

Hedef Vinç (Retrofit Hedef Crane) için iki dilli (TR + EN) statik site. Ana işler: Milas'ta
vinç tamiri ve vinç kiralama. Sahipler: Ahmet Uğur ve Mehmet Uğur, 2005'ten beri.

Saf HTML + tek CSS + küçük bir JS. Sayfalar `tools/build_blog.py` ile önceden üretilir ve
repoya üretilmiş hâlleriyle girer; GitHub Pages hiçbir derleme yapmadan yayınlar.

## Klasörler

```
content/sayfalar/   Sayfa kaynakları (ana sayfa, hizmetler, bölgeler, hakkımızda, iletişim, 404, en/...)
content/blog/       Türkçe blog yazıları, yazı başına bir JSON
taslak/kuyruk/      Sırada bekleyen yazı taslakları (NN-slug.json)
taslak/kontrol.py   Yazı ve taslak doğrulayıcı
taslak/yayinla.py   Kuyruktan yazı yayınlayıcı
tools/build_blog.py Site üreticisi (sayfalar, blog, sitemap.xml, llms.txt, robots.txt)
tools/sablon.py     Ortak şablon: üst/alt bölüm, telefonlar, adres, yapılandırılmış veri
tools/foto.py       Fotoğrafların 800/1600 piksel web kopyalarını üretir (Pillow gerekir)
tools/link_kontrol.py  İç bağlantı denetimi
tools/denetim.py    SEO denetimi (başlık, açıklama, h1, hreflang, görsel, JSON-LD)
tools/indexnow.py   Değişen sayfaları IndexNow'a bildirir
assets/css/style.css, assets/js/main.js
assets/img/brand/   Logo ve işaret (SVG); favicon ve uygulama simgeleri bunlardan üretildi
assets/img/r/       Fotoğrafların küçültülmüş kopyaları ve manifest.json
assets/img/og/      Paylaşım görselleri (1200×630)
assets/img/real_ones/  Sahibin gönderdiği orijinal fotoğraflar
```

Kök dizindeki `index.html`, `hizmetler/`, `bolgeler/`, `blog/`, `en/` gibi dosyalar **üretilmiş**
dosyalardır. Elle değiştirmeyin; bir sonraki üretimde üzerine yazılır. Değişikliği
`content/sayfalar/` ya da `content/blog/` içinde yapıp üreticiyi çalıştırın.

## Sık yapılan işler

Sayfa metnini değiştirmek: `content/sayfalar/<yol>.html` dosyasını düzenleyin. Dosyanın başındaki
`<!-- { ... } -->` bloğu başlık, açıklama, SSS ve şema bilgisidir. Sonra:

```
python tools/build_blog.py
python tools/link_kontrol.py
```

Telefon ya da adres değişirse: `tools/sablon.py` başındaki sabitleri ve sayfa kaynaklarındaki
`tel:` bağlantılarını güncelleyip üreticiyi çalıştırın.

Yeni fotoğraf: dosyayı `assets/img/` altına (Türkçe karaktersiz, boşluksuz adla) koyun ve
`python tools/foto.py` çalıştırın. Sayfalarda `{{foto:yol|alt metin|altyazı|sizes}}` ile kullanılır.

Yeni blog yazısı: `taslak/kuyruk/NN-slug.json` olarak ekleyin (alanlar için var olan bir taslağa
bakın), `python taslak/kontrol.py` ile doğrulayın.

## Denetim ve arama motorları

```
python tools/denetim.py       # tek h1, başlık ≤ 62, açıklama 120-160, canonical, hreflang, img alt/boyut, JSON-LD
python tools/link_kontrol.py  # iç bağlantılar
python tools/indexnow.py --degisen --kuru   # son commit'te değişen sayfaları IndexNow'a bildirmeden önce gösterir
```

IndexNow anahtarı kökteki `2ef09e7e305fb7d69e83939822a4a8e3.txt` dosyasıdır; silmeyin. Günlük yayından
sonra iş akışı değişen sayfaları Bing ve Yandex'e bildirir (hata olursa yayını durdurmaz).

Sahibinin vereceği bilgiler `tools/sablon.py` başındadır ve boşken sayfaya yazılmaz:
`KONUM` (Google Haritalar iğnesinin enlem/boylamı), `SAME_AS` (Google İşletme Profili dolu; varsa Instagram,
Facebook eklenir), `DOGRULAMA` (Google Search Console, Bing, Yandex doğrulama kodları). Doldurduktan sonra
`python tools/build_blog.py` çalıştırın.

## Blog kuyruğu

```
python taslak/yayinla.py --list    # bekleyenler
python taslak/yayinla.py           # sıradaki taslağı bugünün tarihiyle yayınla
python taslak/yayinla.py --gunluk  # bugün yayın yoksa bir tane yayınla
```

`.github/workflows/blog-kuyrugu.yml` her gün 09:37'de (yedek 21:37, İstanbul saati) `--gunluk`
çalıştırır, değişiklikleri commit edip gönderir. Yayın kaydı `taslak/yayin-gunlugu.txt` içindedir.

## Yayın

GitHub Pages, `main` dalı, kök dizin. Alan adı `CNAME` içinde. `_config.yml` kaynak klasörlerini
(`content/`, `tools/`, `taslak/`) yayından çıkarır; `robots.txt` da bunları taramaya kapatır.

## ÖNEMLİ: _private klasörü

`_private/` içinde vergi numarası içeren kaşe fotoğrafı ve fotoğraf orijinalleri var. Klasör
`.gitignore`'da olduğu için GitHub'a gitmez. `.gitignore` dosyasını silmeyin.
