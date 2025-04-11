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
    *   Gerekli API anahtarları ve WordPress bilgileri **doğrudan uygulama arayüzünden** ayarlanabilir ve kaydedilebilir (`config.json` dosyasına yazılır).
*   **Esnek Prompt Seçenekleri:**
    *   Hazır **sistem SEO prompt'unu** kullanabilir veya içerik üretimi için tamamen **kendi özel prompt'unuzu** tanımlayabilirsiniz.
*   **Toplu İşlem:**
    *   Tek bir konu için **birden fazla makaleyi** tek seferde üretebilir ve yayınlayabilirsiniz.
*   **Detaylı Kayıt Tutma (Loglama):**
    *   Uygulamanın yaptığı tüm işlemleri (başarılı/başarısız API çağrıları, üretilen içerikler, hatalar vb.) takip etmek için **ayrı bir log penceresi** sunar.
*   **Yanıt Veren Tasarım:**
    *   Uzun sürebilecek API çağrıları sırasında arayüzün kilitlenmemesi için **threading** kullanılır.

---


## ⚙️ Kurulum ve Başlangıç Ayarları

### Gereksinimler

*   Python 3.8 veya üzeri
*   `pip` (Python paket yükleyici)
*   **Google Gemini API Anahtarı:** Uygulamanın makale üretebilmesi için gereklidir.
*   **WordPress Sitesi:** Erişilebilir, REST API'si aktif ve uygulama şifresi özelliğini destekleyen bir site.
*   **WordPress Kullanıcı Hesabı:** Sitede **yazı yayınlama yetkisine** (Administrator, Editor, Author rolleri) sahip bir kullanıcı.
*   **WordPress Uygulama Şifresi:** Yukarıdaki kullanıcı için WordPress üzerinden oluşturulmuş özel bir şifre.

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

### Başlangıç Ayarları ve Gerekli Bilgiler

Uygulamayı ilk kez çalıştırmadan önce veya çalıştırdıktan sonra Ayarlar bölümünden şu bilgilere ihtiyacınız olacak:

1.  **Google Gemini API Anahtarı:**
    *   Nasıl alınır? [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) adresine gidin, Google hesabınızla giriş yapın ve yeni bir API anahtarı oluşturun. Oluşturulan anahtarı kopyalayın.
    *   Bu anahtarı uygulamadaki "**Gemini API Key**" alanına yapıştırın.

2.  **WordPress Site Bilgileri:**
    *   `wp_url`: WordPress sitenizin tam adresi (örn: `https://siteniz.com`). Uygulamadaki "**WordPress URL**" alanına girin.
    *   `wp_username`: Sitenizdeki yazı yayınlama yetkisine sahip kullanıcının adı. Uygulamadaki "**WP Kullanıcı Adı**" alanına girin.
    *   `wp_app_password`: **WordPress Uygulama Şifresi**. Bu, normal giriş şifreniz *değildir*. Aşağıdaki adımlarla almanız gerekir:

#### WordPress Uygulama Şifresi Nasıl Alınır?

Bu şifre, uygulamanın sitenize API üzerinden güvenli bir şekilde bağlanmasını sağlar.

1.  WordPress yönetici panelinize (**wp-admin**) giriş yapın.
2.  Sol menüden **Kullanıcılar** (Users) -> **Profiliniz** (Your Profile) bölümüne gidin.
3.  Sayfayı aşağı kaydırın ve **Uygulama Şifreleri** (Application Passwords) bölümünü bulun. *(Eğer bu bölümü göremiyorsanız, sitenizde REST API'nin veya bu özelliğin bir eklenti tarafından engellenmediğinden emin olun.)*
4.  "**Yeni Uygulama Şifresi Adı**" alanına bu uygulama için hatırlatıcı bir isim verin (örn: `WPGeminiPublisher` veya `AI Makale Botu`).
5.  "**Yeni Uygulama Şifresi Ekle**" butonuna tıklayın.
6.  **❗ ÖNEMLİ:** WordPress size 16 veya 24 karakterlik, boşluklar içeren bir şifre gösterecektir (örn: `abcd efgh ijkl mnop qrst uvwx`). Bu şifreyi **hemen kopyalayın ve güvenli bir yere kaydedin**. Bu sayfadan ayrıldıktan sonra şifre **bir daha gösterilmeyecektir!**
7.  Kopyaladığınız bu **tam şifreyi (boşluklarıyla birlikte!)** uygulamadaki "**WP Uyg. Şifresi**" alanına yapıştırın.

**Tüm bu bilgileri girdikten sonra "Ayarları Kaydet" butonuna tıklayın.** Uygulama bu ayarları bilgisayarınızdaki `config.json` dosyasına kaydedecektir. Daha sonra "Bağlantıyı Test Et" butonu ile WordPress bağlantınızı kontrol edebilirsiniz.

---

## ▶️ Kullanım

1.  Terminal veya komut istemcisinde proje dizinine gidin (ve sanal ortamı aktifleştirdiğinizden emin olun).
2.  Uygulamayı başlatın:
    ```bash
    python main.py
    ```
3.  Arayüz açıldığında:
    *   Gerekli API ve site bilgilerini **Ayarlar** bölümüne girip kaydedin (daha önce yapmadıysanız).
    *   "**Bağlantıyı Test Et**" ile bağlantıyı doğrulayın.
    *   "**Makale Oluştur**" bölümünde:
        *   Bir **Konu/Anahtar Kelime** girin.
        *   "Yenile" ile WordPress **kategorilerini** çekip seçin.
        *   İstediğiniz **makale adedini** ve **karakter sayısını** belirtin.
    *   "**Prompt Ayarı**" bölümünde üretim talimatınızı seçin (Sistem veya Özel).
    *   Hazır olduğunuzda "**Makaleleri Oluştur ve Yayınla**" butonuna tıklayın.
    *   İşlem süresince ve bitiminde bilgilendirme mesajları alacaksınız.
    *   Detaylı işlem adımlarını ve olası hataları görmek için "**İşlem Kayıtlarını Göster**" butonuna tıklayın.

---

## 📄 Lisans

Bu proje **MIT Lisansı** altında lisanslanmıştır. Daha fazla bilgi için `LICENSE` dosyasına bakınız.

---

## 🤝 Katkıda Bulunma

Katkıda bulunmak isterseniz, lütfen bir "Issue" açarak sorunu veya önerinizi belirtin ya da bir "Pull Request" gönderin.

---

## 📞 İletişim

*   **Web Sitesi:** [https://siberotag.com](https://siberotag.com)
*   **GitHub:** [https://github.com/efemehmet1965](https://github.com/efemehmet1965)
