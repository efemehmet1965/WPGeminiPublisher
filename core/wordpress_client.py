# ================================================================
#                       *** SIBER OTAG ***
#
#         This code is part of a project by Siber Otag.
#              Find more at: https://siberotag.com
#
# ================================================================
#           Copyright (c) 2025 Siber Otag - All Rights Reserved
# ================================================================

import requests
import json
from requests.auth import HTTPBasicAuth
import math
import time

class WordPressClient:
    def __init__(self, wp_url, username, app_password):
        if not wp_url or not username or not app_password:
            raise ValueError("WordPress URL, Kullanıcı Adı ve Uygulama Şifresi gerekli.")

        self.base_url = wp_url.rstrip('/') + '/wp-json/wp/v2'
        self.auth = HTTPBasicAuth(username, app_password)
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        print(f"WordPress istemcisi {self.base_url} için ayarlandı.")

    def test_connection(self):
         test_url_auth = self.base_url + '/users/me?context=edit'
         print(f"Bağlantı testi için istek gönderiliyor: {test_url_auth}")
         try:
             response = requests.get(test_url_auth, auth=self.auth, headers=self.headers, timeout=15)
             response.raise_for_status()

             user_data = response.json()
             user_id = user_data.get('id')
             user_name = user_data.get('name', self.auth.username)
             user_roles = user_data.get('roles', [])

             can_publish = any(role in ['administrator', 'editor', 'author'] for role in user_roles)

             print(f"WordPress bağlantısı başarılı! Kullanıcı: {user_name} (ID: {user_id}), Roller: {user_roles}")

             if not can_publish:
                  print("Uyarı: Kullanıcının rolleri arasında yazı yayınlama yetkisi (administrator, editor, author) bulunmuyor.")
                  return True, f"Bağlantı başarılı ({user_name}) ancak yazı yayınlama yetkiniz olmayabilir."
             else:
                  return True, f"Bağlantı başarılı! Kullanıcı: {user_name} (Yayınlama Yetkisi Var)"

         except requests.exceptions.Timeout:
            print("Hata: WordPress sitesine bağlanırken zaman aşımı.")
            return False, "Hata: Zaman aşımı."
         except requests.exceptions.ConnectionError as e:
             print(f"Hata: WordPress sitesine bağlanılamadı: {e}")
             suggestion = f" URL'yi ('http://' veya 'https://' ile) kontrol edin."
             return False, f"Hata: Bağlantı kurulamadı.{suggestion}"
         except requests.exceptions.HTTPError as e:
             status_code = response.status_code
             error_message = f"Hata ({status_code}). "
             try:
                 error_detail = response.json()
                 api_code = error_detail.get('code')
                 api_message = error_detail.get('message')
                 print(f"API Hata Kodu: {api_code}, Mesaj: {api_message}")
                 if status_code == 401:
                    if "incorrect_password" in api_code:
                        error_message += "Uygulama şifresi yanlış."
                    elif "invalid_username" in api_code:
                        error_message += "Kullanıcı adı geçersiz."
                    else:
                         error_message += "Kimlik doğrulama başarısız (Kullanıcı adı veya şifre yanlış)."
                 elif status_code == 403:
                     if "rest_cannot_edit_user" in api_code or "rest_forbidden" in api_code :
                         error_message += "Bu kullanıcı için yetki reddedildi (İzinleri kontrol edin)."
                     else:
                        error_message += "Yasaklandı (Yetki reddedildi)."
                 elif status_code == 404:
                     error_message += "API yolu bulunamadı (URL veya REST API etkinliğini kontrol edin)."
                 else:
                     error_message += api_message
             except (json.JSONDecodeError, AttributeError):
                 error_message += f"Sunucudan okunaksız yanıt: {response.text[:100]}"

             print(f"Hata: WordPress API Hatası: {status_code} - Detay: {response.text[:200]}")
             return False, error_message
         except Exception as e:
            print(f"Hata: WP bağlantı testi sırasında bilinmeyen hata: {e}")
            return False, f"Hata: Bilinmeyen sorun ({type(e).__name__})."


    def get_categories(self):
        all_categories = []
        page = 1
        per_page = 100
        categories_url = f"{self.base_url}/categories"

        while True:
            params = {'per_page': per_page, 'page': page, 'orderby': 'name', 'order': 'asc'}
            print(f"Kategoriler çekiliyor: Sayfa {page}")
            try:
                response = requests.get(categories_url, params=params, auth=self.auth, headers=self.headers, timeout=15)
                response.raise_for_status()

                categories = response.json()
                if not categories:
                    break

                for cat in categories:
                    all_categories.append({'id': cat['id'], 'name': cat['name'], 'parent': cat['parent']})

                total_categories = int(response.headers.get('X-WP-Total', 0))
                total_pages = int(response.headers.get('X-WP-TotalPages', 0))
                print(f"Toplam {total_categories} kategori, {total_pages} sayfa bulundu.")

                if page >= total_pages:
                    break

                page += 1

            except requests.exceptions.RequestException as e:
                print(f"Hata: WordPress kategorileri çekilirken: {e}")
                if page == 1:
                    return None, f"Hata: Kategoriler çekilemedi: {e}"
                else:
                     print("Uyarı: Tüm kategoriler çekilememiş olabilir.")
                     break
            except Exception as e:
                 print(f"Hata: Kategorileri işlerken bilinmeyen hata: {e}")
                 return None, f"Hata: Kategori işleme hatası: {e}"

        cat_map = {cat['id']: cat for cat in all_categories}
        for cat in all_categories:
             prefix = ""
             current = cat
             while current['parent'] != 0 and current['parent'] in cat_map:
                  prefix = cat_map[current['parent']]['name'] + " > " + prefix
                  current = cat_map[current['parent']]
             cat['hierarchical_name'] = prefix + cat['name']


        all_categories.sort(key=lambda x: x['hierarchical_name'])

        print(f"{len(all_categories)} kategori başarıyla çekildi.")
        return all_categories, None

    def _get_or_create_tag(self, tag_name):
        tags_url = f"{self.base_url}/tags"
        search_params = {'search': tag_name.lower(), 'per_page': 5, 'orderby':'count', 'order':'desc'}

        try:
            response = requests.get(tags_url, params=search_params, auth=self.auth, headers=self.headers, timeout=10)
            response.raise_for_status()
            results = response.json()

            exact_match = next((tag for tag in results if tag.get('name','').lower() == tag_name.lower()), None)
            if exact_match:
                  print(f"Varolan etiket bulundu: '{tag_name}' (ID: {exact_match['id']})")
                  return exact_match['id']

            print(f"'{tag_name}' etiketi bulunamadı, oluşturuluyor...")
            create_data = {'name': tag_name}
            response = requests.post(tags_url, json=create_data, auth=self.auth, headers=self.headers, timeout=15)

            if response.status_code == 400 and 'term_exists' in response.text:
                 print(f"Uyarı: '{tag_name}' etiketi zaten var (API 400 - term_exists). Tekrar aranıyor...")
                 time.sleep(1)
                 response_retry = requests.get(tags_url, params={'search': tag_name.lower(), 'per_page': 1}, auth=self.auth, headers=self.headers, timeout=10)
                 response_retry.raise_for_status()
                 results_retry = response_retry.json()
                 if results_retry and results_retry[0].get('name','').lower() == tag_name.lower():
                     print(f"Varolan etiket ikinci denemede bulundu: '{tag_name}' (ID: {results_retry[0]['id']})")
                     return results_retry[0]['id']
                 else:
                     print(f"Hata: '{tag_name}' etiketi oluşturulamadı veya bulunamadı.")
                     return None

            response.raise_for_status()
            new_tag = response.json()
            print(f"Yeni etiket oluşturuldu: '{tag_name}' (ID: {new_tag['id']})")
            return new_tag['id']

        except requests.exceptions.RequestException as e:
            print(f"Hata: Etiket işlenirken ('{tag_name}'): {e}")
            return None
        except Exception as e:
             print(f"Hata: Etiket işlenirken ('{tag_name}') bilinmeyen hata: {e}")
             return None


    def post_article(self, title, content, status='publish', tags=None, category_id=None, meta_description=None):
        posts_url = f"{self.base_url}/posts"

        post_data = {
            'title': title,
            'content': content,
            'status': status,
        }

        if tags:
            tag_ids = []
            print(f"Etiketler işleniyor: {tags}")
            for tag_name in tags:
                tag_id = self._get_or_create_tag(tag_name.strip())
                if tag_id:
                    tag_ids.append(tag_id)
            if tag_ids:
                print(f"Kullanılacak etiket ID'leri: {tag_ids}")
                post_data['tags'] = tag_ids
            else:
                 print("Hiçbir geçerli etiket ID'si bulunamadı/oluşturulamadı.")

        if category_id:
             try:
                cat_id_int = int(category_id)
                post_data['categories'] = [cat_id_int]
                print(f"Kategori ID'si eklendi: {cat_id_int}")
             except (ValueError, TypeError):
                 print(f"Uyarı: Geçersiz kategori ID'si ({category_id}). Kategori atanmayacak.")

        if meta_description:
             post_data['meta'] = {'rank_math_description': meta_description}
             print(f"Meta açıklaması eklendi (Plugin meta alanı: {list(post_data['meta'].keys())[0]})")


        try:
            print(f"Makale '{title}' gönderiliyor...")
            response = requests.post(posts_url, json=post_data, auth=self.auth, headers=self.headers, timeout=30)
            response.raise_for_status()

            posted_data = response.json()
            print(f"Makale BAŞARIYLA gönderildi! Başlık: '{title}', ID: {posted_data['id']}, Link: {posted_data.get('link')}")
            return True, f"Başarıyla gönderildi (ID: {posted_data['id']})"

        except requests.exceptions.Timeout:
             print(f"Hata: Makale gönderilirken ('{title}') zaman aşımı.")
             return False, "Hata: Gönderme zaman aşımı."
        except requests.exceptions.ConnectionError as e:
            print(f"Hata: Makale gönderilirken ('{title}') bağlantı hatası: {e}")
            return False, "Hata: WP'ye bağlanılamadı."
        except requests.exceptions.HTTPError as e:
             status_code = response.status_code
             error_msg = f"Hata: WP API Hatası ({status_code}). "
             try:
                 error_detail = response.json()
                 api_code = error_detail.get('code')
                 api_message = error_detail.get('message')
                 if status_code == 400:
                     error_msg += f"Geçersiz veri - {api_message}"
                 elif status_code == 403:
                     error_msg += f"Yetersiz yetki - {api_message}"
                 else:
                    error_msg += api_message if api_message else "Detay alınamadı."
             except Exception:
                 error_msg += f"Yanıt alınamadı: {response.text[:100]}"
             print(error_msg)
             return False, f"Hata ({status_code}). Detaylar için loglara bakın."
        except Exception as e:
            print(f"Hata: Makale gönderilirken ('{title}') bilinmeyen hata: {e}")
            return False, f"Hata: Bilinmeyen gönderim sorunu ({type(e).__name__})."