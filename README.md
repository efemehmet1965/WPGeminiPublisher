# WPGeminiPublisher 🚀

**WordPress için Yapay Zeka İçerik Üretici & Yayınlayıcı**

Google Gemini API kullanarak SEO uyumlu makaleler oluşturun ve bunları doğrudan WordPress sitenizde yayınlayın!

[![Lisans: MIT](https://img.shields.io/badge/Lisans-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📖 Proje Hakkında

WPGeminiPublisher, WordPress siteleri için içerik oluşturma sürecini otomatikleştirmek amacıyla geliştirilmiş bir Python masaüstü uygulamasıdır. Google Gemini API'nin gücünden faydalanarak belirlediğiniz konularda SEO odaklı makaleler üretir (başlık, meta açıklama, içerik, etiketler) ve bu içerikleri WordPress REST API aracılığıyla sitenize otomatik olarak gönderir.

Bu araç, özellikle düzenli içerik girişi yapması gereken blog yazarları, SEO uzmanları ve web geliştiricileri için zaman kazandırmak üzere tasarlanmıştır.

---

## ✨ Özellikler

*   **Yapay Zeka ile İçerik Üretimi:**
    *   **Google Gemini** (`gemini-1.5-flash-latest` modeli) kullanılır.
    *   Konuya özel, **SEO uyumlu başlıklar** üretir.
    *   Tıklama oranını artırmaya yönelik **meta açıklamalar** oluşturur.
    *   Belirtilen karakter hedefine uygun, **yapılandırılmış makale içeriği** (Markdown) hazırlar ve HTML'e dönüştürür.
    *   İçeriğe uygun **yazı etiketleri** önerir.
*   **Doğrudan WordPress Entegrasyonu:**
    *   Üretilen makaleleri seçilen **WordPress kategorisi** ile yayınlar.
    *   Sitenizdeki mevcut **kategorileri otomatik olarak çeker**.
    *   WordPress sitenizle olan **API bağlantısını ve kullanıcı yetkilerini test eder**.
    *   Eğer yoksa, gerekli **etiketleri WordPress'te otomatik oluşturur**.
*   **Kullanıcı Dostu Arayüz:**
    *   Modern ve kullanımı kolay arayüz için **CustomTkinter** kullanılmıştır.
    *   **Koyu/Açık tema** desteği sunar.
*   **Kolay Yapılandırma:**
    *   Gerekli API anahtarları ve WordPress bilgileri `config.json` dosyası üzerinden veya doğrudan arayüzden ayarlanabilir.
*   **Esnek Prompt Seçenekleri:**
    *   Hazır **sistem SEO prompt'unu** kullanabilir veya içerik üretimi için tamamen **kendi özel prompt'unuzu** tanımlayabilirsiniz.
*   **Toplu İşlem:**
    *   Tek bir konu için **birden fazla makaleyi** tek seferde üretebilir ve yayınlayabilirsiniz.
*   **Detaylı Kayıt Tutma (Loglama):**
    *   Uygulamanın yaptığı tüm işlemleri (başarılı/başarısız API çağrıları, üretilen içerikler, hatalar vb.) takip etmek için **ayrı bir log penceresi** sunar.
*   **Yanıt Veren Tasarım:**
    *   Uzun sürebilecek API çağrıları sırasında arayüzün kilitlenmemesi için **threading** kullanılır.


---

## ⚙️ Kurulum ve Ayarlar

### Gereksinimler

*   Python 3.8 veya üzeri
*   `pip` (Python paket yükleyici)
*   Google Gemini API Anahtarı
*   WordPress kurulu ve erişilebilir bir web sitesi (REST API aktif olmalı)
*   WordPress sitenizde **yazı yayınlama yetkisine sahip** bir kullanıcı hesabı (Administrator, Editor, Author rolleri)
*   Bu kullanıcı için oluşturulmuş bir **WordPress Uygulama Şifresi** (Application Password)

### Kurulum Adımları

1.  **Projeyi İndirin veya Klonlayın:**
    ```bash
    git clone https://github.com/efemehmet1965/WPGeminiPublisher.git
    cd WPGeminiPublisher
    ```
2.  **(Önerilen) Sanal Ortam Oluşturun:**
    *   **Windows:**
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    *   **Linux/macOS:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
3.  **Gerekli Kütüphaneleri Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```

### Yapılandırma (`config.json`)

Proje kök dizininde bulunan `config.json` dosyasını bir metin düzenleyici ile açın ve aşağıdaki alanları kendi bilgilerinizle doldurun:

*   `gemini_api_key`: Google AI Studio üzerinden aldığınız API anahtarınız.
    *   Nasıl alınır? [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) adresine gidin ve yeni bir anahtar oluşturun.
*   `wp_url`: WordPress sitenizin tam adresi (örneğin: `https://siteniz.com`). Sonunda `/` olmamalıdır.
*   `wp_username`: WordPress yönetici panelinize giriş yaparken kullandığınız kullanıcı adı.
*   `wp_app_password`: WordPress sitenizden bu uygulama için özel olarak oluşturduğunuz **Uygulama Şifresi**. **Normal giriş şifreniz DEĞİLDİR!** (Aşağıdaki adıma bakın).
*   `article_count`: Tek seferde üretilecek varsayılan makale sayısı.
*   `article_length`: Makalelerin hedeflenen yaklaşık karakter sayısı.
*   `use_system_prompt`: `true` ise dahili SEO prompt'u kullanılır, `false` ise aşağıdaki özel prompt kullanılır.
*   `custom_prompt`: `use_system_prompt` `false` ise kullanılacak kendi özel prompt metniniz.
*   `default_prompt_file`: Sistem prompt'unun okunacağı dosya yolu (genellikle değiştirmenize gerek yoktur).

#### WordPress Uygulama Şifresi Nasıl Alınır?

Bu, uygulamanın sitenize güvenli bir şekilde bağlanabilmesi için kritik öneme sahiptir.

1.  WordPress yönetici panelinize (**wp-admin**) giriş yapın.
2.  Sol menüden **Kullanıcılar** (Users) -> **Profiliniz** (Your Profile) bölümüne gidin.
3.  Sayfayı aşağı kaydırın ve **Uygulama Şifreleri** (Application Passwords) bölümünü bulun. *(Eğer bu bölümü göremiyorsanız, sitenizde REST API'nin veya bu özelliğin bir güvenlik eklentisi tarafından engellenmediğinden emin olun.)*
4.  "**Yeni Uygulama Şifresi Adı**" (New Application Password Name) alanına bu uygulama için hatırlatıcı bir isim verin (örneğin: `WPGeminiPublisher` veya `AI Makale Botu`).
5.  "**Yeni Uygulama Şifresi Ekle**" (Add New Application Password) butonuna tıklayın.
6.  **❗ ÖNEMLİ:** WordPress size 16 veya 24 karakterlik, boşluklar içeren bir şifre gösterecektir (örn: `abcd efgh ijkl mnop qrst uvwx`). Bu şifreyi **hemen kopyalayın ve güvenli bir yere kaydedin**. Sayfadan ayrıldıktan veya sayfayı yeniledikten sonra bu şifre **bir daha gösterilmeyecektir!**
7.  Kopyaladığınız bu **tam şifreyi (boşluklarıyla birlikte!)** `config.json` dosyasındaki `wp_app_password` alanına yapıştırın.

---

## ▶️ Kullanım

1.  Terminal veya komut istemcisinde proje dizinine gidin (ve sanal ortamı aktifleştirdiğinizden emin olun).
2.  Uygulamayı başlatın:
    ```bash
    python main.py
    ```
3.  Arayüz açıldığında:
    *   İlk olarak **Ayarlar** bölümündeki bilgilerin doğru olduğundan emin olun veya doğrudan arayüzden girip "Ayarları Kaydet" butonuna tıklayın.
    *   "**Bağlantıyı Test Et**" butonu ile WordPress sitenizle bağlantının ve kimlik doğrulamanın başarılı olup olmadığını kontrol edin.
    *   "**Makale Oluştur**" bölümünde:
        *   Bir **Konu/Anahtar Kelime** girin.
        *   "Yenile" butonu ile WordPress kategorilerinizi çekin ve listeden bir **kategori seçin** (veya varsayılanı kullanın).
        *   İstediğiniz **makale adedini** ve yaklaşık **karakter sayısını** belirtin.
    *   "**Prompt Ayarı**" bölümünde sistem prompt'unu mu yoksa kendi özel prompt'unuzu mu kullanacağınızı seçin.
    *   Hazır olduğunuzda "**Makaleleri Oluştur ve Yayınla**" butonuna tıklayın.
    *   İşlem bittiğinde bir bildirim alacaksınız.
    *   Detayları görmek için "**İşlem Kayıtlarını Göster**" butonuna tıklayarak log penceresini açabilirsiniz.

---

## 📄 Lisans

Bu proje **MIT Lisansı** altında lisanslanmıştır. Daha fazla bilgi için `LICENSE` dosyasına bakınız.

---

## 🤝 Katkıda Bulunma

Katkıda bulunmak isterseniz, lütfen bir "Issue" açarak sorunu veya önerinizi belirtin ya da bir "Pull Request" gönderin.

---

## 📞 İletişim

*   **Geliştirici:** Efe Mehmet (Siber Otag)
*   **Web Sitesi:** [https://siberotag.com](https://siberotag.com)
*   **GitHub:** [https://github.com/efemehmet1965](https://github.com/efemehmet1965)
