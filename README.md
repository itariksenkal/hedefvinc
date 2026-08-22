# Hedef Vinç — hedefvinc.com

Hedef Vinç (Retrofit Hedef Crane) için iki dilli (TR + EN) statik tanıtım sitesi.
Milas / Muğla merkezli vinç kiralama, vinç servisi, iş makinası bakımı ve konteyner
satış-kiralama firması.

Saf HTML + CSS + JS — framework yok, derleme adımı yok. GitHub Pages'e olduğu gibi
yüklenip yayınlanır.

## Klasör Yapısı

```
├── index.html                  Ana sayfa (Türkçe)
├── hakkimizda.html             Hakkımızda
├── iletisim.html               İletişim
├── 404.html                    Bulunamayan sayfa (GitHub Pages otomatik kullanır)
├── hizmetler/                  9 hizmet detay sayfası (Türkçe)
├── blog/                       Blog: index.html + 8 yazı (Türkçe)
├── en/                         İngilizce site
│   ├── index.html              Home
│   ├── about.html, contact.html
│   ├── services/               9 hizmet sayfası (İngilizce)
│   └── blog/                   Blog index + 8 yazı (İngilizce)
├── assets/
│   ├── css/style.css           Tüm site stili (tek dosya)
│   ├── js/main.js              Menü, SSS, sayaçlar, animasyonlar
│   └── img/                    Firma fotoğrafları + logo + stok/ (Pexels, telifsiz)
├── sitemap.xml                 TR+EN tüm sayfalar, hreflang alternates ile
├── robots.txt
├── llms.txt                    Yapay zeka arama motorları için site özeti
├── CNAME                       Özel alan adı: hedefvinc.com
└── _private/                   YAYINLANMAZ (.gitignore'da) — kaşe fotoğrafı, orijinaller
```

## ÖNEMLİ — _private klasörü

`_private/` içinde **vergi numarası içeren kaşe fotoğrafı** ve fotoğrafların
orijinalleri var. Bu klasör `.gitignore`'da olduğu için GitHub'a gitmez —
**`.gitignore` dosyasını silmeyin** ve bu klasördekileri siteye koymayın.

## GitHub Pages'te Yayınlama

1. GitHub'da yeni bir repo oluşturun (ör. `hedefvinc`).
2. Bu klasörü repoya push edin:
   ```
   git init
   git add .
   git commit -m "Hedef Vinç sitesi"
   git branch -M main
   git remote add origin https://github.com/KULLANICI/hedefvinc.git
   git push -u origin main
   ```
3. Repo → **Settings → Pages** → Source: `main` branch, `/ (root)` seçin.
4. Alan adı: **Settings → Pages → Custom domain** alanına `hedefvinc.com` yazın
   (CNAME dosyası repoda hazır). DNS'te:
   - `A` kayıtları: 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153
   - `www` için CNAME: `KULLANICI.github.io`
5. "Enforce HTTPS" kutusunu işaretleyin.
6. Yayın sonrası [Google Search Console](https://search.google.com/search-console)'a
   siteyi ekleyip `sitemap.xml`'i gönderin — Google Ads kalite puanı ve organik
   trafik için önemli.

## Fotoğraflar

- Firma fotoğrafları `assets/img/` altında (siyah bantları kırpılmış, optimize edilmiş).
- `assets/img/stok/` altındakiler Pexels'ten indirilmiş **telifsiz** stok fotoğraflar
  (Pexels lisansı: ticari kullanım serbest, atıf gerekmez).
- Yeni fotoğraf eklemek için: dosyayı `assets/img/` içine koyun (Türkçe karaktersiz,
  boşluksuz isimle), ana sayfadaki `gallery-grid` bölümüne bir `<figure>` ekleyin.

## Blog'a Yeni Yazı Ekleme

1. `blog/` içindeki bir yazıyı kopyalayıp yeni dosya adı verin.
2. Başlık, tarih, içerik, canonical/og/hreflang URL'lerini güncelleyin.
3. `blog/index.html`'e ve ana sayfadaki "Blog" bölümüne kart ekleyin.
4. `sitemap.xml`'e URL ekleyin. (İngilizcesi için aynısını `en/blog/` altında yapın.)

## Düzenleme Notları

- Telefonlar: 0533 708 92 00 (ana) ve 0532 294 48 63 (İngilizce destek).
  Değişirse tüm sayfalarda `tel:+90...` ve `wa.me/90...` linklerini birlikte güncelleyin.
- E-posta adresi kasıtlı eklenmedi (info@hedefvinc.com açılınca footer'a eklenebilir).
- Google Ads için her hizmetin kendi açılış sayfası `hizmetler/` (TR) ve
  `en/services/` (EN) altındadır.
