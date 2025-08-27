import os
import re

class ConfigManager:
    def __init__(self, config_file='config.txt'):
        self.config_file = config_file
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """載入配置文件"""
        if not os.path.exists(self.config_file):
            self.create_default_config()
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # 嘗試轉換為適當的數據類型
                    if value.lower() in ['true', 'false']:
                        value = value.lower() == 'true'
                    elif value.isdigit():
                        value = int(value)
                    
                    self.config[key] = value
    
    def save_config(self):
        """保存配置到文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            f.write("# Telegram API 配置\n")
            f.write(f"api_id={self.config.get('api_id', 1234567)}\n")
            f.write(f"api_hash={self.config.get('api_hash', '967fc90f90ajfu1dd7fe0724jm5e28f8')}\n")
            f.write("\n# 默認設置\n")
            f.write(f"default_report_count={self.config.get('default_report_count', 100)}\n")
            f.write(f"default_target_channel={self.config.get('default_target_channel', '')}\n")
            f.write(f"default_report_mode={self.config.get('default_report_mode', 'spam')}\n")
            f.write("\n# UI 設置\n")
            f.write(f"theme={self.config.get('theme', 'dark')}\n")
            f.write(f"window_width={self.config.get('window_width', 800)}\n")
            f.write(f"window_height={self.config.get('window_height', 600)}\n")
            f.write("\n# 報告設置\n")
            f.write(f"auto_join_channel={self.config.get('auto_join_channel', True)}\n")
            f.write(f"delay_between_reports={self.config.get('delay_between_reports', 1)}\n")
            f.write("\n# 語言設置\n")
            f.write(f"language={self.config.get('language', 'zh-TW')}\n")
    
    def create_default_config(self):
        """創建默認配置文件"""
        self.config = {
            'api_id': 1234567,
            'api_hash': '967fc90f90ajfu1dd7fe0724jm5e28f8',
            'default_report_count': 100,
            'default_target_channel': '',
            'default_report_mode': 'spam',
            'theme': 'dark',
            'window_width': 800,
            'window_height': 600,
            'auto_join_channel': True,
            'delay_between_reports': 1,
            'language': 'zh-TW'
        }
        self.save_config()
    
    def get(self, key, default=None):
        """獲取配置值"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """設置配置值"""
        self.config[key] = value
        self.save_config() 