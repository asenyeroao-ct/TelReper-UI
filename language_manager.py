import json
import os
from typing import Dict, Any

class LanguageManager:
    """語言管理器，用於處理多語言支持"""
    
    def __init__(self, lang_dir='lang', default_language='zh-TW'):
        self.lang_dir = lang_dir
        self.default_language = default_language
        self.current_language = default_language
        self.translations = {}
        self.load_language(default_language)
    
    def get_available_languages(self) -> Dict[str, str]:
        """獲取可用的語言列表"""
        languages = {}
        if os.path.exists(self.lang_dir):
            for file in os.listdir(self.lang_dir):
                if file.endswith('.json'):
                    lang_code = file.replace('.json', '')
                    # 從語言文件中讀取語言名稱
                    try:
                        with open(os.path.join(self.lang_dir, file), 'r', encoding='utf-8') as f:
                            lang_data = json.load(f)
                            app_title = lang_data.get('app_title', lang_code)
                            languages[lang_code] = app_title
                    except:
                        languages[lang_code] = lang_code
        return languages
    
    def load_language(self, language_code: str) -> bool:
        """載入指定語言"""
        lang_file = os.path.join(self.lang_dir, f'{language_code}.json')
        
        if not os.path.exists(lang_file):
            # 如果指定的語言文件不存在，嘗試載入默認語言
            if language_code != self.default_language:
                return self.load_language(self.default_language)
            return False
        
        try:
            with open(lang_file, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
                self.current_language = language_code
                return True
        except Exception as e:
            print(f"Error loading language {language_code}: {e}")
            return False
    
    def get_text(self, key: str, **kwargs) -> str:
        """獲取翻譯文本，支持格式化參數"""
        # 支持嵌套鍵，如 'main_tab.target_channel'
        keys = key.split('.')
        value = self.translations
        
        try:
            for k in keys:
                value = value[k]
            
            # 如果是字符串，進行格式化
            if isinstance(value, str):
                return value.format(**kwargs) if kwargs else value
            else:
                return str(value)
        except (KeyError, TypeError):
            # 如果找不到翻譯，返回鍵名
            return key
    
    def get_current_language(self) -> str:
        """獲取當前語言代碼"""
        return self.current_language
    
    def get_language_info(self) -> Dict[str, Any]:
        """獲取當前語言信息"""
        return {
            'code': self.current_language,
            'app_title': self.get_text('app_title'),
            'version': self.get_text('version'),
            'author': self.get_text('author'),
            'github_link': self.get_text('github_link'),
            'supporter': self.get_text('supporter'),
            'supporter_link': self.get_text('supporter_link')
        }
    
    def format_message(self, message_key: str, **kwargs) -> str:
        """格式化消息文本"""
        return self.get_text(f'messages.{message_key}', **kwargs)
    
    def format_tooltip(self, tooltip_key: str) -> str:
        """格式化工具提示文本"""
        return self.get_text(f'tooltips.{tooltip_key}')
    
    def format_error(self, error_key: str) -> str:
        """格式化錯誤文本"""
        return self.get_text(f'errors.{error_key}')
    
    def format_confirmation(self, confirm_key: str, **kwargs) -> str:
        """格式化確認文本"""
        return self.get_text(f'confirmations.{confirm_key}', **kwargs) 