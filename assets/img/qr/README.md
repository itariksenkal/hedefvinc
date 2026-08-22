# Hedef Vinç — QR Kodlar

Tüm kodlar **2000 px** (300 DPI'da ~17 cm) PNG'dir; ortasında firma logosu vardır ve
**H seviyesi (%30) hata düzeltme** ile üretilmiştir — logo kapatsa bile okunur.

Hepsi test edildi: **220 px'e kadar küçültüldüğünde bile doğru adresi veriyor.**

## Web sitesi kodları → `https://hedefvinc.com`

| Dosya | Görünüm | Nerede kullanılır |
|---|---|---|
| `web-qr-1-klasik.png` | Lacivert, beyaz zemin, logo | Genel kullanım — kartvizit, broşür, teklif |
| `web-qr-2-sari-zemin.png` | Lacivert kod, sarı zemin | Dikkat çekmesi gereken yerler — afiş, tabela |
| `web-qr-3-yuvarlak.png` | Yumuşak köşeli moduller | Modern görünüm — sosyal medya, dijital |
| `web-qr-4-cerceve-lacivert.png` | Lacivert kart + "hedefvinc.com" | **Araç giydirme, tabela, pano** (yazılı çerçeveli) |
| `web-qr-5-cerceve-sari.png` | Sarı kart + lacivert yazı | Aynısının sarı versiyonu |
| `web-qr-6-sade-siyah.png` | Düz siyah, logosuz | **En güvenli** — küçük baskı, gazete, faks, fotokopi |

## WhatsApp kodları → `https://wa.me/905337089200`

Okutan kişinin WhatsApp'ı doğrudan **0533 708 92 00** ile sohbet ekranında açılır.

| Dosya | Görünüm | Nerede kullanılır |
|---|---|---|
| `wa-qr-1-klasik.png` | Yeşil, beyaz zemin, logo | Genel kullanım |
| `wa-qr-2-lacivert.png` | Lacivert kod + yeşil göz | Marka renkleriyle uyumlu |
| `wa-qr-3-yuvarlak.png` | Yumuşak köşeli yeşil | Dijital / sosyal medya |
| `wa-qr-4-cerceve-yesil.png` | Yeşil kart + "WhatsApp'tan Yazın" | **Araç, tabela, vitrin** |
| `wa-qr-5-cerceve-lacivert.png` | Lacivert kart + yeşil yazı | Marka ağırlıklı baskılar |
| `wa-qr-6-sade-siyah.png` | Düz siyah, logosuz | En güvenli, küçük baskı |

## Baskı kuralları

- **En küçük baskı boyutu: 2,5 x 2,5 cm.** Daha küçüğünde okutma zorlaşır.
  Araç veya tabelada uzaktan okutulacaksa **en az 10 cm** yapın
  (kural: okuma mesafesi ÷ 10 = kod kenarı; 2 metreden okunacaksa 20 cm).
- Kodun etrafındaki **beyaz boşluğu kırpmayın** — tarayıcı o boşluğa göre kodu bulur.
- Kodu **germeyin/eğmeyin**; sadece orantılı büyütüp küçültün.
- Koyu zemin üzerine basacaksanız çerçeveli (`cerceve`) versiyonları kullanın.
- Baskı öncesi **kendi telefonunuzla mutlaka bir kez okutun.**

## Not

Web sitesi kodları `hedefvinc.com` adresine gider. Alan adının DNS ayarı
tamamlanıp site yayına girmeden önce basılan kodlar açılmaz — önce siteyi
yayına alın, sonra bastırın.

Kodlar `assets/img/qr/` klasöründe üretilmiştir; yeniden üretmek gerekirse
QR verisi kısa tutulmalıdır (uzun adres = sık modül = zor okuma).
