# ================================================================
#                       *** SIBER OTAG ***
#
#         This code is part of a project by Siber Otag.
#              Find more at: https://siberotag.com
#
# ================================================================
#           Copyright (c) 2025 Siber Otag - All Rights Reserved
# ================================================================

import json
import os

CONFIG_FILE = 'config.json'

DEFAULT_CONFIG = {
    "gemini_api_key": "",
    "wp_url": "",
    "wp_username": "",
    "wp_app_password": "",
    "article_count": 1,
    "article_length": 1500,
    "use_system_prompt": True,
    "custom_prompt": "",
    "default_prompt_file": "prompts/system_seo_prompt.txt"
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            updated_config = DEFAULT_CONFIG.copy()
            updated_config.update(config_data)
            return updated_config
    except (json.JSONDecodeError, IOError) as e:
        print(f"Hata: Ayar dosyası ({CONFIG_FILE}) okunamadı veya bozuk: {e}")
        print("Varsayılan ayarlarla devam ediliyor.")
        return DEFAULT_CONFIG.copy()

def save_config(config_data):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        print("Ayarlar kaydedildi.")
    except IOError as e:
        print(f"Hata: Ayarlar kaydedilemedi: {e}")

if __name__ == '__main__':
    load_config()