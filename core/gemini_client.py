# ================================================================
#                       *** SIBER OTAG ***
#
#         This code is part of a project by Siber Otag.
#              Find more at: https://siberotag.com
#
# ================================================================
#           Copyright (c) 2025 Siber Otag - All Rights Reserved
# ================================================================

import google.generativeai as genai
import time
import os

MODEL_NAME = 'gemini-1.5-flash-latest'
MAX_OUTPUT_TOKENS_CONFIG = 8192
TEMPERATURE_CONTENT = 0.6
TEMPERATURE_CREATIVE = 0.7
RETRY_DELAY = 5
MAX_RETRIES = 3

DEFAULT_SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

class GeminiClient:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("Gemini API anahtarı gerekli.")
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(MODEL_NAME)
            print(f"Gemini AI istemcisi ({MODEL_NAME}) başarıyla başlatıldı.")
        except Exception as e:
            print(f"HATA: Gemini AI istemcisi başlatılamadı ({type(e).__name__}): {e}")
            raise

    def _generate_with_retries(self, prompt_text, temperature, max_tokens=None):
        if not self.model:
            return "Hata: Gemini modeli düzgün başlatılamamış.", None

        effective_max_tokens = max_tokens if max_tokens else MAX_OUTPUT_TOKENS_CONFIG

        generation_config = genai.types.GenerationConfig(
            max_output_tokens=effective_max_tokens,
            temperature=temperature,
        )

        print(f"  -> API İsteği Gönderiliyor (MaxTokens: {effective_max_tokens}, Temp: {temperature})...")

        response = None
        for attempt in range(MAX_RETRIES):
            try:
                response = self.model.generate_content(
                    prompt_text,
                    generation_config=generation_config,
                    safety_settings=DEFAULT_SAFETY_SETTINGS
                )

                if response.prompt_feedback and response.prompt_feedback.block_reason:
                    reason = response.prompt_feedback.block_reason.name if hasattr(response.prompt_feedback.block_reason, 'name') else str(response.prompt_feedback.block_reason)
                    print(f"  -> UYARI: Prompt engellendi: {reason}")
                    return f"Hata: Prompt güvenlik filtresine takıldı ({reason}).", None

                if not response.candidates:
                    print(f"  -> UYARI: Yanıtta 'candidates' boş!")
                    if response.prompt_feedback and response.prompt_feedback.block_reason:
                         reason = response.prompt_feedback.block_reason.name if hasattr(response.prompt_feedback.block_reason, 'name') else str(response.prompt_feedback.block_reason)
                         return f"Hata: Prompt güvenlik filtresine takıldı ({reason}).", None
                    return "Hata: API'den boş 'candidates' yanıtı alındı.", None

                candidate = response.candidates[0]
                finish_reason = candidate.finish_reason
                finish_reason_name = finish_reason.name if hasattr(finish_reason, 'name') else str(finish_reason) if finish_reason else 'UNKNOWN'

                if finish_reason_name == 'SAFETY':
                    ratings = candidate.safety_ratings
                    print(f"  -> UYARI: İçerik güvenliği engeli: {ratings}")
                    return f"Hata: Üretilen içerik güvenlik filtresine takıldı ({ratings}).", None

                if finish_reason_name not in ['STOP', 'MAX_TOKENS']:
                    print(f"  -> UYARI: Beklenmedik bitiş nedeni: {finish_reason_name}")
                    text_content = "".join(part.text for part in candidate.content.parts if hasattr(part, 'text')).strip() if candidate.content and candidate.content.parts else response.text if hasattr(response, 'text') else None
                    return f"Hata: İçerik üretimi tamamlanamadı (Sebep: {finish_reason_name}).", text_content

                text_content = None
                if candidate.content and candidate.content.parts:
                     text_content = "".join(part.text for part in candidate.content.parts if hasattr(part, 'text')).strip()
                elif hasattr(response, 'text') and response.text:
                     text_content = response.text.strip()

                if text_content:
                    if finish_reason_name == 'MAX_TOKENS':
                         print(f"  -> UYARI: MAX_TOKENS limitine ulaşıldı ({effective_max_tokens}). Kısmi içerik döndürülüyor.")
                         return None, text_content
                    else:
                         print(f"  -> Başarılı yanıt alındı ({len(text_content)} karakter).")
                         return None, text_content
                else:
                    print(f"  -> UYARI: Başarılı yanıt (FinishReason: {finish_reason_name}) ancak metin içeriği boş.")
                    return "Hata: Başarılı yanıt alındı ancak metin içeriği boş.", None


            except Exception as e:
                print(f"HATA: API İletişim Hatası (Deneme {attempt + 1}/{MAX_RETRIES}) - {type(e).__name__}: {e}")

                if "API key not valid" in str(e) or "APIキーが有効ではありません" in str(e):
                    return "Hata: Gemini API anahtarı geçersiz.", None

                status_code = getattr(e, 'status_code', None)
                is_rate_limit = status_code == 429 or 'ResourceExhausted' in type(e).__name__

                if is_rate_limit:
                    wait_time = RETRY_DELAY * (2 ** attempt)
                    print(f"    --> Rate limit. {wait_time:.1f}sn bekleniyor...")
                    time.sleep(wait_time)
                    continue
                elif attempt < MAX_RETRIES - 1:
                    print(f"    --> {RETRY_DELAY}sn bekleniyor...")
                    time.sleep(RETRY_DELAY)
                    continue
                else:
                    return f"Hata: API'ye ulaşılamadı ({type(e).__name__}): {e}", None

        return f"Hata: Maksimum deneme sayısına ({MAX_RETRIES}) ulaşıldı.", None


    def generate_title(self, topic):
        print("Başlık üretiliyor...")
        prompt = (f'"{topic}" konusu/anahtar kelimesi için kısa (maksimum 60-70 karakter), '
                  f'SEO uyumlu ve ilgi çekici bir Türkçe makale başlığı oluştur. '
                  f'Başka hiçbir şey yazma, SADECE başlığı yaz.')
        error, title = self._generate_with_retries(prompt, TEMPERATURE_CREATIVE, max_tokens=100)
        if error:
            print(f"Başlık üretme hatası: {error}")
            return None, error
        cleaned_title = title.strip().strip('"\'').strip()
        return cleaned_title, None

    def generate_meta_description(self, topic, title=None):
        print("Meta açıklama üretiliyor...")
        title_context = f' "{title}" başlıklı' if title else ""
        prompt = (f'"{topic}" konulu{title_context} Türkçe makale için, yaklaşık 155 karakter '
                  f'uzunluğunda, anahtar kelimeyi içeren, arama sonuçlarında tıklanmayı '
                  f'teşvik edecek bir meta açıklama yaz. SADECE meta açıklamayı yaz.')
        error, meta_desc = self._generate_with_retries(prompt, TEMPERATURE_CREATIVE, max_tokens=300)
        if error:
            print(f"Meta açıklama üretme hatası: {error}")
            return None, error
        cleaned_meta = meta_desc.strip().strip('"\'').strip()
        return cleaned_meta, None


    def generate_article_content(self, topic, title, character_count, system_prompt_template):
        print(f"Makale içeriği üretiliyor (Hedef: ~{character_count} karakter)...")
        try:
            final_prompt = system_prompt_template.format(
                topic=topic,
                title=title,
                character_count=character_count
            )
        except KeyError as e:
            error_msg = f"Hata: Sistem prompt'unda eksik yer tutucu: {e}. Prompt dosyasını kontrol edin."
            print(error_msg)
            return None, error_msg
        except Exception as e:
            error_msg = f"Hata: İçerik prompt'u formatlanırken sorun: {e}"
            print(error_msg)
            return None, error_msg

        error, content = self._generate_with_retries(final_prompt, TEMPERATURE_CONTENT)

        if error:
            print(f"İçerik üretme hatası: {error}")
            return content if content else None, error
        return content, None


    def generate_tags(self, article_content, num_tags=5):
        if not article_content:
             print("UYARI: Etiket oluşturmak için boş içerik verildi.")
             return []

        print("Etiketler üretiliyor...")
        content_snippet = article_content[:2000]

        prompt = f"""Aşağıdaki makale içeriğini analiz et ve en alakalı {num_tags} adet SEO dostu etiket öner. Etiketler kısa (1-3 kelime), küçük harf ve virgülle ayrılmış olmalı. Sadece virgülle ayrılmış etiket listesini yaz, başka hiçbir metin veya açıklama ekleme.

Makale Özeti:
{content_snippet}...

Etiketler:"""

        error, tags_response = self._generate_with_retries(prompt, TEMPERATURE_CREATIVE, max_tokens=150)

        if error:
            print(f"Etiket oluşturulamadı: {error}")
            return []

        if not tags_response:
             print(f"UYARI: Etiket yanıtı boş geldi.")
             return []

        tags_string = tags_response.lower().replace("etiketler:", "").strip()
        tags = [tag.strip() for tag in tags_string.split(',') if tag.strip()]
        tags = tags[:num_tags]

        print(f"Oluşturulan etiketler ({len(tags)} adet): {tags}")
        return tags