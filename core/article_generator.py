# ================================================================
#                       *** SIBER OTAG ***
#
#         This code is part of a project by Siber Otag.
#              Find more at: https://siberotag.com
#
# ================================================================
#           Copyright (c) 2025 Siber Otag - All Rights Reserved
# ================================================================

import os
import time
import markdown
from .gemini_client import GeminiClient
from .wordpress_client import WordPressClient
from .config_manager import load_config, save_config

class ArticleGenerator:
    def __init__(self):
        self.config = load_config()
        self.gemini_client = None
        self.wp_client = None
        self._initialize_clients()
        self.categories = []
        self.system_prompt_template = ""

    def _initialize_clients(self):
        api_key = self.config.get("gemini_api_key")
        if api_key:
            try:
                self.gemini_client = GeminiClient(api_key=api_key)
            except Exception as e:
                print(f"Uyarı: Gemini Client başlatılamadı: {e}")
                self.gemini_client = None
        else:
            print("Uyarı: Gemini API Anahtarı ayarlanmamış.")
            self.gemini_client = None

        wp_url, wp_user, wp_pass = self.config.get("wp_url"), self.config.get("wp_username"), self.config.get("wp_app_password")
        if wp_url and wp_user and wp_pass:
             try:
                 self.wp_client = WordPressClient(wp_url=wp_url, username=wp_user, app_password=wp_pass)
             except Exception as e:
                 print(f"Uyarı: WordPress Client başlatılamadı: {e}")
                 self.wp_client = None
        else:
            print("Uyarı: WordPress bilgileri eksik.")
            self.wp_client = None

    def update_config(self, new_config):
        save_config(new_config)
        self.config = new_config
        self.wp_client = None
        self.gemini_client = None
        self.categories = []
        self.system_prompt_template = ""
        self._initialize_clients()

    def get_config(self):
        return self.config

    def test_wp_connection(self):
         if not self.wp_client:
             return False, "WP istemcisi başlatılamadı."
         return self.wp_client.test_connection()

    def fetch_wp_categories(self):
         if not self.wp_client:
             return False, "WP istemcisi başlatılamadı.", None
         cats, err = self.wp_client.get_categories()
         if err:
             self.categories = []
             return False, err, None
         self.categories = cats
         return True, "Kategoriler çekildi.", cats

    def get_cached_categories(self):
        return self.categories

    def _load_system_prompt(self):
        if self.system_prompt_template:
            return True, None

        try:
            prompt_file = self.config.get("default_prompt_file", "prompts/system_seo_prompt.txt")
            if not os.path.exists(prompt_file):
                return False, f"Hata: Sistem prompt dosyası bulunamadı: {prompt_file}"
            with open(prompt_file, 'r', encoding='utf-8') as f:
                self.system_prompt_template = f.read()
            if not self.system_prompt_template:
                return False, "Hata: Sistem prompt dosyası boş."
            return True, None
        except IOError as e:
            return False, f"Hata: Sistem prompt dosyası okunamadı: {e}"
        except Exception as e:
            return False, f"Hata: Sistem prompt yüklenirken hata: {e}"


    def create_and_post_articles(self, topic, num_articles, length, use_system_prompt,
                                  custom_prompt_text, category_id=None, status_callback=None):

        if not self.gemini_client:
            return "Hata: Gemini başlatılmadı."
        if not self.wp_client:
            return "Hata: WordPress başlatılmadı."

        def log(message, level="info"):
             print(message)
             if status_callback:
                 status_callback(message, level)

        content_prompt_template = ""
        if use_system_prompt:
            loaded, error = self._load_system_prompt()
            if not loaded:
                log(error, "error")
                return error
            content_prompt_template = self.system_prompt_template
        else:
            if not custom_prompt_text:
                msg = "Hata: Özel prompt seçildi ancak metin boş."
                log(msg, "error")
                return msg
            content_prompt_template = custom_prompt_text
            if "{topic}" not in content_prompt_template:
                content_prompt_template += "\n\nKonu: {topic}"
            if "{title}" not in content_prompt_template:
                content_prompt_template += "\nBaşlık: {title}"
            if "{character_count}" not in content_prompt_template:
                content_prompt_template += f"\nKarakter Hedefi: {{character_count}}"

        results_summary = []
        total_start_time = time.time()

        for i in range(num_articles):
            log(f"\n===== Makale {i+1}/{num_articles} Başlatılıyor ({topic}) =====", "debug")
            article_start_time = time.time()

            current_topic_for_generation = topic

            generated_title = None
            generated_meta = None
            generated_content_md = None
            generated_content_html = None
            tags = []
            post_success = False
            post_message = "Bilinmeyen hata"

            try:
                 log(f"[{i+1}] Adım 1: Başlık üretiliyor...")
                 generated_title, title_error = self.gemini_client.generate_title(current_topic_for_generation)
                 if title_error:
                     raise ValueError(f"Başlık Üretilemedi: {title_error}")
                 log(f"   -> Üretilen Başlık: {generated_title}", "debug")

                 log(f"[{i+1}] Adım 2: Meta açıklama üretiliyor...")
                 generated_meta, meta_error = self.gemini_client.generate_meta_description(current_topic_for_generation, generated_title)
                 if meta_error:
                     log(f"   -> UYARI: Meta Açıklama Üretilemedi: {meta_error}", "warning")
                 else:
                     log(f"   -> Üretilen Meta: {generated_meta}", "debug")

                 log(f"[{i+1}] Adım 3: İçerik üretiliyor (Hedef: ~{length} karakter)...")
                 generated_content_md, content_error = self.gemini_client.generate_article_content(
                     current_topic_for_generation, generated_title, length, content_prompt_template
                 )

                 if content_error and not generated_content_md:
                     raise ValueError(f"İçerik Üretilemedi: {content_error}")
                 elif content_error and generated_content_md:
                     log(f"   -> UYARI: İçerik üretimi hatası ({content_error}), kısmi içerikle devam ediliyor.", "warning")
                     log(f"   -> İçerik Uzunluğu (Kısmi MD): {len(generated_content_md)} krktr", "debug")
                 elif not generated_content_md:
                     raise ValueError("İçerik Üretilemedi: API boş içerik döndürdü.")
                 else:
                     log(f"   -> İçerik Uzunluğu (MD): {len(generated_content_md)} karakter", "debug")

                 log(f"[{i+1}] Adım 3.5: İçerik Markdown'dan HTML'e dönüştürülüyor...")
                 if generated_content_md:
                      try:
                          generated_content_html = markdown.markdown(generated_content_md, extensions=['extra'])
                          log(f"   -> HTML dönüşümü tamamlandı. (HTML Uzunluğu: {len(generated_content_html)} karakter)", "debug")
                      except Exception as md_err:
                          log(f"   -> HATA: Markdown -> HTML dönüşümü başarısız: {md_err}. Ham içerik gönderilecek.", "error")
                          generated_content_html = generated_content_md
                 else:
                      generated_content_html = ""

                 log(f"[{i+1}] Adım 4: Etiketler üretiliyor...")
                 tags = self.gemini_client.generate_tags(generated_content_md if generated_content_md else "")
                 log(f"   -> Üretilen Etiketler: {tags}", "debug")

                 log(f"[{i+1}] Adım 5: '{generated_title}' WordPress'e gönderiliyor...")
                 post_success, post_message = self.wp_client.post_article(
                     title=generated_title,
                     content=generated_content_html,
                     tags=tags,
                     category_id=category_id,
                     meta_description=generated_meta
                 )
                 if not post_success:
                     log(f"   -> GÖNDERME BAŞARISIZ: {post_message}", "error")
                 else:
                     log(f"   -> BAŞARIYLA GÖNDERİLDİ: {post_message}", "success")

            except Exception as e:
                error_msg = f"Makale {i+1} işlenirken hata: {e}"
                log(error_msg, "error")
                post_message = str(e)
                post_success = False

            article_end_time = time.time()
            duration = article_end_time - article_start_time
            status_text = "BAŞARIYLA" if post_success else "BAŞARISIZ"
            title_for_summary = generated_title if generated_title else f"Başlıksız ({current_topic_for_generation})"
            summary_line = (f"Makale {i+1} [{title_for_summary[:30]}...]: {status_text} ({duration:.1f}sn). Mesaj: {post_message}")
            results_summary.append(summary_line)
            log(f"===== Makale {i+1} Tamamlandı ({status_text}) =====", "debug")

        total_end_time = time.time()
        total_duration = total_end_time - total_start_time
        final_message = (f"\nİşlem Tamamlandı! Toplam Süre: {total_duration:.1f}sn ({num_articles} makale denendi).\n--- ÖZET ---\n")
        final_message += "\n".join(results_summary)
        log(final_message, "info")

        return final_message