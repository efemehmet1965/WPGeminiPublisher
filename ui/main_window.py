# ================================================================
#                       *** SIBER OTAG ***
#
#         This code is part of a project by Siber Otag.
#              Find more at: https://siberotag.com
#
# ================================================================
#           Copyright (c) 2025 Siber Otag - All Rights Reserved
# ================================================================

import customtkinter as ctk
from tkinter import messagebox
from core.article_generator import ArticleGenerator
import threading
import os
import webbrowser

class LogWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("İşlem Kayıtları")
        self.geometry("750x500")
        self.log_storage_ref = master.log_storage
        self.after(250, self.lift)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.textbox = ctk.CTkTextbox(self, wrap="word", state="disabled", activate_scrollbars=True, font=ctk.CTkFont(family="Consolas", size=11))
        self.textbox.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=(10, 5))

        self.textbox.tag_config("error", foreground="red")
        self.textbox.tag_config("warning", foreground="orange")
        self.textbox.tag_config("success", foreground="lightgreen")
        self.textbox.tag_config("info", foreground="#A0A0A0")
        self.textbox.tag_config("debug", foreground="#7777CC")

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky="e")

        self.clear_button = ctk.CTkButton(button_frame, text="Logları Temizle", command=self.clear_logs, width=120)
        self.clear_button.pack(side=ctk.RIGHT, padx=(10,10))

        self.refresh_button = ctk.CTkButton(button_frame, text="Yenile", command=self.load_logs, width=100)
        self.refresh_button.pack(side=ctk.RIGHT, padx=(0, 5))

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.load_logs()

    def load_logs(self):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        for message, level in self.log_storage_ref:
            self.textbox.insert("end", f"{message}\n", level)
        self.textbox.configure(state="disabled")
        self.textbox.see("end")

    def clear_logs(self):
        if messagebox.askyesno("Logları Temizle", "Tüm işlem kayıtlarını kalıcı olarak silmek istediğinizden emin misiniz?"):
            self.master.clear_log_storage()
            self.load_logs()

    def on_close(self):
        self.master.log_window = None
        self.destroy()


class AppUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("WP Gemini Publisher")
        self.geometry("900x720")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.generator = ArticleGenerator()
        self.config = self.generator.get_config()
        self.categories_map = {}
        self.log_storage = []
        self.log_window = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)
        self.grid_rowconfigure(4, weight=0)

        settings_frame = ctk.CTkFrame(self, corner_radius=10)
        settings_frame.grid(row=0, column=0, padx=15, pady=(15, 7), sticky="ew")
        settings_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(settings_frame, text="Ayarlar", font=ctk.CTkFont(weight="bold", size=14)).grid(row=0, column=0, columnspan=3, padx=10, pady=(5,10), sticky="w")
        ctk.CTkLabel(settings_frame, text="Gemini API Key:").grid(row=1, column=0, padx=(15,5), pady=5, sticky="w")
        self.gemini_api_key_var = ctk.StringVar(value=self.config.get('gemini_api_key', ''))
        self.gemini_api_key_entry = ctk.CTkEntry(settings_frame, textvariable=self.gemini_api_key_var, width=400, show='*')
        self.gemini_api_key_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(settings_frame, text="WordPress URL:").grid(row=2, column=0, padx=(15,5), pady=5, sticky="w")
        self.wp_url_var = ctk.StringVar(value=self.config.get('wp_url', ''))
        self.wp_url_entry = ctk.CTkEntry(settings_frame, textvariable=self.wp_url_var, placeholder_text="https://siteniz.com")
        self.wp_url_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(settings_frame, text="WP Kullanıcı Adı:").grid(row=3, column=0, padx=(15,5), pady=5, sticky="w")
        self.wp_username_var = ctk.StringVar(value=self.config.get('wp_username', ''))
        self.wp_username_entry = ctk.CTkEntry(settings_frame, textvariable=self.wp_username_var)
        self.wp_username_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w", ipadx=30)
        ctk.CTkLabel(settings_frame, text="WP Uyg. Şifresi:").grid(row=4, column=0, padx=(15,5), pady=5, sticky="w")
        self.wp_app_password_var = ctk.StringVar(value=self.config.get('wp_app_password', ''))
        self.wp_app_password_entry = ctk.CTkEntry(settings_frame, textvariable=self.wp_app_password_var, show='*')
        self.wp_app_password_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w", ipadx=30)
        button_frame_settings = ctk.CTkFrame(settings_frame, fg_color="transparent")
        button_frame_settings.grid(row=5, column=1, columnspan=2, pady=10, padx=5, sticky="e")
        self.test_status_label = ctk.CTkLabel(button_frame_settings, text="", text_color="gray", font=ctk.CTkFont(size=11))
        self.test_status_label.pack(side=ctk.LEFT, padx=(0, 10))
        self.test_wp_button = ctk.CTkButton(button_frame_settings, text="Bağlantıyı Test Et", command=self.test_wp_connection_threaded, width=140)
        self.test_wp_button.pack(side=ctk.RIGHT, padx=(5, 0))
        self.save_button = ctk.CTkButton(button_frame_settings, text="Ayarları Kaydet", command=self.save_settings, width=140, fg_color="green", hover_color="darkgreen")
        self.save_button.pack(side=ctk.RIGHT, padx=(0, 5))

        generator_frame = ctk.CTkFrame(self, corner_radius=10)
        generator_frame.grid(row=1, column=0, padx=15, pady=7, sticky="ew")
        generator_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(generator_frame, text="Makale Oluştur", font=ctk.CTkFont(weight="bold", size=14)).grid(row=0, column=0, columnspan=3, padx=10, pady=(5,10), sticky="w")
        ctk.CTkLabel(generator_frame, text="Konu/Anahtar Kelime:").grid(row=1, column=0, padx=(15,5), pady=5, sticky="w")
        self.topic_var = ctk.StringVar()
        self.topic_entry = ctk.CTkEntry(generator_frame, textvariable=self.topic_var, placeholder_text="Örn: Python ile web geliştirme")
        self.topic_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(generator_frame, text="WordPress Kategori:").grid(row=2, column=0, padx=(15,5), pady=5, sticky="w")
        self.category_combobox = ctk.CTkComboBox(generator_frame, values=["Kategorileri Yenile..."], state="readonly", command=self.on_category_select)
        self.category_combobox.set("Kategori Seçin...")
        self.category_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.refresh_cat_button = ctk.CTkButton(generator_frame, text="Yenile", command=self.fetch_categories_threaded, width=60)
        self.refresh_cat_button.grid(row=2, column=2, padx=(5,15), pady=5)
        options_frame = ctk.CTkFrame(generator_frame, fg_color="transparent")
        options_frame.grid(row=3, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        ctk.CTkLabel(generator_frame, text="Ayarlar:").grid(row=3, column=0, padx=(15,5), pady=5, sticky="w")
        ctk.CTkLabel(options_frame, text="Adet:").pack(side=ctk.LEFT, padx=(0, 5))
        self.article_count_var = ctk.IntVar(value=self.config.get('article_count', 1))
        self.article_count_entry = ctk.CTkEntry(options_frame, textvariable=self.article_count_var, width=60, justify='center')
        self.article_count_entry.pack(side=ctk.LEFT, padx=(0, 15))
        ctk.CTkLabel(options_frame, text="~Karakter:").pack(side=ctk.LEFT, padx=(0, 5))
        self.article_length_var = ctk.IntVar(value=self.config.get('article_length', 1500))
        self.article_length_entry = ctk.CTkEntry(options_frame, textvariable=self.article_length_var, width=80, justify='center')
        self.article_length_entry.pack(side=ctk.LEFT, padx=(0, 5))

        prompt_frame = ctk.CTkFrame(self, corner_radius=10)
        prompt_frame.grid(row=2, column=0, padx=15, pady=7, sticky="ew")
        prompt_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(prompt_frame, text="Prompt Ayarı", font=ctk.CTkFont(weight="bold", size=14)).grid(row=0, column=0, columnspan=2, padx=10, pady=(5,10), sticky="w")
        self.prompt_choice_var = ctk.BooleanVar(value=self.config.get('use_system_prompt', True))
        self.system_prompt_radio = ctk.CTkRadioButton(prompt_frame, text="Sistem SEO Prompt'u Kullan", variable=self.prompt_choice_var, value=True, command=self.toggle_custom_prompt)
        self.system_prompt_radio.grid(row=1, column=0, padx=15, pady=(0,0), sticky="w")
        default_prompt_file = self.config.get('default_prompt_file', 'prompts/system_seo_prompt.txt')
        prompt_file_exists = os.path.exists(default_prompt_file)
        prompt_label_text = f"({os.path.basename(default_prompt_file)}{'' if prompt_file_exists else ' - Bulunamadı!'})"
        prompt_label_color = "gray" if prompt_file_exists else "orange"
        self.system_prompt_label = ctk.CTkLabel(prompt_frame, text=prompt_label_text, text_color=prompt_label_color, font=ctk.CTkFont(size=11))
        self.system_prompt_label.grid(row=1, column=1, padx=5, pady=(0,0), sticky="w")
        self.custom_prompt_radio = ctk.CTkRadioButton(prompt_frame, text="Özel Prompt Kullan:", variable=self.prompt_choice_var, value=False, command=self.toggle_custom_prompt)
        self.custom_prompt_radio.grid(row=2, column=0, columnspan=2, padx=15, pady=(10, 5), sticky="w")
        self.custom_prompt_text = ctk.CTkTextbox(prompt_frame, wrap="word", height=100, activate_scrollbars=True)
        self.custom_prompt_text.grid(row=3, column=0, columnspan=2, sticky="ew", padx=15, pady=(0, 10))
        self.custom_prompt_text.insert("1.0", self.config.get('custom_prompt', ''))
        self.toggle_custom_prompt()

        action_button_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_button_frame.grid(row=3, column=0, padx=15, pady=10, sticky="ew")
        action_button_frame.grid_columnconfigure(0, weight=1)
        action_button_frame.grid_columnconfigure(1, weight=1)

        self.generate_button = ctk.CTkButton(action_button_frame, text="Makaleleri Oluştur ve Yayınla", command=self.start_generation_threaded, height=40, font=ctk.CTkFont(size=14, weight="bold"))
        self.generate_button.grid(row=0, column=0, padx=(0,5), pady=5, sticky="w")

        self.show_log_button = ctk.CTkButton(action_button_frame, text="İşlem Kayıtlarını Göster", command=self.show_logs_window, width=180)
        self.show_log_button.grid(row=0, column=1, padx=(5,0), pady=5, sticky="e")

        footer_frame = ctk.CTkFrame(self, height=25, corner_radius=0)
        footer_frame.grid(row=4, column=0, padx=0, pady=(5,0), sticky="sew")
        footer_frame.grid_columnconfigure(0, weight=1)
        footer_frame.grid_columnconfigure(1, weight=1)
        website_url = "https://siberotag.com"
        github_url = "https://github.com/efemehmet1965/"
        website_label = ctk.CTkLabel(footer_frame, text=website_url, text_color="gray", font=ctk.CTkFont(size=10), cursor="hand2")
        website_label.grid(row=0, column=0, padx=(15, 5), pady=3, sticky="w")
        website_label.bind("<Button-1>", lambda e, url=website_url: webbrowser.open_new(url))
        github_label = ctk.CTkLabel(footer_frame, text=github_url, text_color="gray", font=ctk.CTkFont(size=10), cursor="hand2")
        github_label.grid(row=0, column=1, padx=(5, 15), pady=3, sticky="e")
        github_label.bind("<Button-1>", lambda e, url=github_url: webbrowser.open_new(url))

        self.fetch_categories_threaded()

    def add_log(self, message, level="info"):
        self.log_storage.append((message, level))
        print(f"LOG [{level.upper()}]: {message}")

    def clear_log_storage(self):
        self.log_storage = []
        if self.log_window:
            self.log_window.load_logs()

    def show_logs_window(self):
        if self.log_window is None or not self.log_window.winfo_exists():
            self.log_window = LogWindow(master=self)
        else:
            self.log_window.lift()
            self.log_window.load_logs()

    def save_settings(self):
        self.config['gemini_api_key'] = self.gemini_api_key_var.get()
        self.config['wp_url'] = self.wp_url_var.get().strip().rstrip('/')
        self.config['wp_username'] = self.wp_username_var.get().strip()
        self.config['wp_app_password'] = self.wp_app_password_var.get()
        self.config['use_system_prompt'] = self.prompt_choice_var.get()
        self.config['custom_prompt'] = self.custom_prompt_text.get("1.0", "end-1c").strip()
        self.config['article_count'] = self.article_count_var.get()
        self.config['article_length'] = self.article_length_var.get()
        try:
             self.generator.update_config(self.config)
             messagebox.showinfo("Başarılı", "Ayarlar başarıyla kaydedildi!")
             self.test_status_label.configure(text="")
             self.category_combobox.configure(values=["Kategorileri Yenile..."])
             self.category_combobox.set("Kategori Seçin...")
             self.categories_map = {}
             self.fetch_categories_threaded()
             self.update_prompt_label_status()
        except Exception as e:
             error_msg = f"Ayarlar kaydedilirken hata: {e}"
             self.add_log(error_msg, "error")
             messagebox.showerror("Hata", error_msg)

    def _run_generation(self, topic, num_articles, length, use_system_prompt, custom_prompt_text, category_id):
        final_message = "Hata: Üretim sırasında bilinmeyen bir sorun oluştu."
        try:
            if category_id is not None:
                try: cat_id_int = int(category_id)
                except (ValueError, TypeError): self.add_log(f"Uyarı: Geçersiz kategori ID ({category_id}) algılandı, varsayılan kullanılacak.", "warning"); cat_id_int = None
            else: cat_id_int = None
            final_message = self.generator.create_and_post_articles(
                topic, num_articles, length, use_system_prompt, custom_prompt_text,
                category_id=cat_id_int, status_callback=self.add_log)
        except Exception as e:
            import traceback
            error_msg = f"Makale oluşturma sırasında kritik hata: {e}\n{traceback.format_exc()}"
            self.add_log(f"Beklenmedik KRİTİK HATA: {e}. Detaylar konsolda.", "error")
            final_message = f"Beklenmedik KRİTİK HATA: {e}"
        finally:
            self.after(0, self._generation_complete, final_message)

    def _generation_complete(self, final_message):
         self.generate_button.configure(text="Makaleleri Oluştur ve Yayınla")
         self.set_buttons_state("normal")
         if "İşlem Tamamlandı!" in final_message and "BAŞARISIZ" not in final_message:
              summary = final_message.split("--- ÖZET ---")[-1].strip()
              num_articles_tried = self.article_count_var.get()
              success_count = summary.count("BAŞARIYLA")
              fail_count = summary.count("BAŞARISIZ")
              msg_title = "İşlem Tamamlandı"
              msg_details = f"{success_count}/{num_articles_tried} makale başarıyla oluşturuldu/gönderildi."
              if fail_count > 0:
                   msg_details += f"\n{fail_count} makalede hata oluştu."
                   messagebox.showwarning(msg_title, msg_details + "\nDetaylar için işlem kayıtlarına bakın.")
              else: messagebox.showinfo(msg_title, msg_details)
         elif "BAŞARISIZ" in final_message:
              messagebox.showwarning("İşlem Tamamlandı (Hatalarla)", "Bazı makaleler oluşturulurken veya gönderilirken hata oluştu.\nDetaylar için işlem kayıtlarına bakın.")
         else: messagebox.showerror("Kritik Hata", f"İşlem sırasında beklenmedik bir hata oluştu:\n{final_message}\nDetaylar için işlem kayıtlarına bakın.")
         self.add_log("=== Tüm İşlemler Bitti ===", "info")
         if self.log_window and self.log_window.winfo_exists(): self.log_window.load_logs()

    def update_prompt_label_status(self):
        default_prompt_file = self.config.get('default_prompt_file', 'prompts/system_seo_prompt.txt')
        prompt_file_exists = os.path.exists(default_prompt_file)
        prompt_label_text = f"({os.path.basename(default_prompt_file)}{'' if prompt_file_exists else ' - Bulunamadı!'})"
        prompt_label_color = "gray" if prompt_file_exists else "orange"
        self.system_prompt_label.configure(text=prompt_label_text, text_color=prompt_label_color)

    def toggle_custom_prompt(self):
        if self.prompt_choice_var.get():
            self.custom_prompt_text.configure(state="disabled", fg_color="transparent")
        else:
            default_color = self.custom_prompt_text.cget("fg_color")
            if isinstance(default_color, (list, tuple)) and len(default_color) > 1:
                current_mode = ctk.get_appearance_mode(); color_index = 0 if current_mode == "Light" else 1; actual_color = default_color[color_index]
            else: actual_color = default_color if default_color else ("#FFFFFF" if ctk.get_appearance_mode() == "Light" else "#404040")
            self.custom_prompt_text.configure(state="normal", fg_color=actual_color)
        self.update_prompt_label_status()

    def test_wp_connection_threaded(self):
        self.test_status_label.configure(text="Test ediliyor...", text_color="orange"); self.set_buttons_state("disabled")
        thread = threading.Thread(target=self._run_wp_test, daemon=True); thread.start()

    def _run_wp_test(self):
         self.add_log("WordPress bağlantısı test ediliyor...", "debug"); success, message = self.generator.test_wp_connection()
         self.after(0, self._update_test_status, success, message)

    def _update_test_status(self, success, message):
        if success:
             self.test_status_label.configure(text=f"✓ {message.split('!')[0]}", text_color="lightgreen")
             self.add_log(f"WordPress Bağlantı Testi: Başarılı - {message}", "success");
             if not self.categories_map: self.fetch_categories_threaded()
        else: self.test_status_label.configure(text=f"✗ {message}", text_color="red"); self.add_log(f"WordPress Bağlantı Testi Başarısız: {message}", "error")
        self.set_buttons_state("normal")

    def fetch_categories_threaded(self):
        if hasattr(self, "_fetch_thread") and self._fetch_thread and self._fetch_thread.is_alive(): self.add_log("Kategori çekme işlemi zaten devam ediyor.", "warning"); return
        self.add_log("WordPress kategorileri çekiliyor...", "debug"); self.refresh_cat_button.configure(state="disabled", text="..."); self.category_combobox.configure(state="disabled")
        self.set_buttons_state("disabled", exclude=[self.refresh_cat_button])
        self._fetch_thread = threading.Thread(target=self._run_category_fetch, daemon=True); self._fetch_thread.start()

    def _run_category_fetch(self):
        success, message, categories = self.generator.fetch_wp_categories()
        self.after(0, self._update_category_list, success, message, categories)

    def _update_category_list(self, success, message, categories):
        self.refresh_cat_button.configure(state="normal", text="Yenile"); self.set_buttons_state("normal")
        if success and categories:
            self.categories_map = {cat['hierarchical_name']: cat['id'] for cat in categories}; self.categories_map["[Varsayılan Kategori]"] = None
            category_names = sorted(self.categories_map.keys()); self.category_combobox.configure(values=category_names, state="readonly")
            current_selection = self.category_combobox.get()
            if current_selection not in category_names: self.category_combobox.set("[Varsayılan Kategori]")
            else: self.category_combobox.set(current_selection)
            self.add_log(f"{len(categories)} kategori yüklendi.", "success")
        else:
             self.category_combobox.configure(values=["Kategori Çekilemedi!"], state="disabled"); self.category_combobox.set("Kategori Çekilemedi!")
             self.categories_map = {}; self.add_log(f"Kategoriler çekilemedi: {message}", "error")
        self._fetch_thread = None

    def on_category_select(self, selected_name):
         category_id = self.categories_map.get(selected_name); self.add_log(f"Kategori seçildi: '{selected_name}' (ID: {category_id})", "debug")

    def start_generation_threaded(self):
        topic = self.topic_var.get().strip();
        if not topic: messagebox.showerror("Hata", "Lütfen bir konu veya anahtar kelime girin."); return
        try:
            num_articles = self.article_count_var.get(); length = self.article_length_var.get()
            if num_articles <= 0 or length < 100: messagebox.showwarning("Geçersiz Değer", "Lütfen geçerli bir makale sayısı (en az 1) ve karakter sayısı (en az 100) girin."); return
            self.config['article_count'] = num_articles; self.config['article_length'] = length
        except Exception: messagebox.showerror("Hata", "Makale sayısı ve karakter sayısı geçerli bir sayı olmalıdır."); return
        use_system_prompt = self.prompt_choice_var.get()
        if use_system_prompt and not os.path.exists(self.config.get('default_prompt_file', '')): messagebox.showerror("Hata", f"Sistem prompt dosyası bulunamadı:\n{self.config.get('default_prompt_file', '')}\nLütfen ayarları kontrol edin veya özel prompt kullanın."); return
        custom_prompt_text = self.custom_prompt_text.get("1.0", "end-1c").strip() if not use_system_prompt else ""
        if not use_system_prompt and not custom_prompt_text: messagebox.showerror("Hata", "Özel prompt seçili ancak prompt alanı boş."); return
        selected_category_name = self.category_combobox.get()
        if selected_category_name in ["Kategori Seçin...", "Kategorileri Yenile...", "Kategori Çekilemedi!"]: category_id = None; self.add_log("Uyarı: Geçerli bir kategori seçilmedi. Makale varsayılan kategoriye gönderilecek.", "warning")
        else: category_id = self.categories_map.get(selected_category_name)
        self.add_log("-" * 30, "debug"); self.add_log(f"Makale Oluşturma Başlatılıyor...", "info")
        log_details = (f"  Konu: {topic} | Adet: {num_articles} | Karakter: ~{length} | Prompt: {'Sistem' if use_system_prompt else 'Özel'} | Kategori: '{selected_category_name}' (ID: {category_id})"); self.add_log(log_details, "debug")
        self.set_buttons_state("disabled"); self.generate_button.configure(text="Çalışıyor...")
        thread = threading.Thread(target=self._run_generation, args=(topic, num_articles, length, use_system_prompt, custom_prompt_text, category_id), daemon=True); thread.start()

    def set_buttons_state(self, state="normal", exclude=None):
         if exclude is None: exclude = []
         buttons = [self.save_button, self.test_wp_button, self.refresh_cat_button, self.generate_button, self.show_log_button]
         entries_and_text = [self.gemini_api_key_entry, self.wp_url_entry, self.wp_username_entry, self.wp_app_password_entry, self.topic_entry, self.article_count_entry, self.article_length_entry, self.custom_prompt_text, self.category_combobox]
         radios = [self.system_prompt_radio, self.custom_prompt_radio]
         all_widgets = buttons + entries_and_text + radios
         for widget in all_widgets:
             if widget not in exclude:
                 try:
                     current_state = "normal" if state == "normal" else "disabled"
                     if isinstance(widget, ctk.CTkComboBox): current_state = "readonly" if state == "normal" else "disabled"
                     elif isinstance(widget, ctk.CTkTextbox) and widget == self.custom_prompt_text: pass
                     widget.configure(state=current_state)
                 except Exception as e: print(f"Widget state ayarlama hatası ({widget.__class__.__name__}): {e}")
         if state == "normal":
             try: self.toggle_custom_prompt()
             except Exception as e: print(f"Toggle custom prompt çağrı hatası: {e}")