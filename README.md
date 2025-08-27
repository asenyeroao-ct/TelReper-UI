# Telegram 頻道報告工具

一個帶有現代化UI的Telegram頻道報告工具，基於原來的命令行版本改進。

## 🔗 原版項目

本項目基於 [Mr3rf1/TelReper](https://github.com/Mr3rf1/TelReper) 開發，添加了圖形界面和多語言支持。

**原版項目特點：**
- 命令行界面
- 多帳戶支持
- 批量報告功能
- 多種報告原因
- 會話管理

## 功能特點

- 🎨 現代化圖形界面，使用CustomTkinter
- 🌍 多語言支持（英文、繁體中文、俄文）
- 📱 多帳戶管理
- ⚙️ 可配置的API設置
- 📊 實時進度顯示
- 📝 詳細的日誌記錄
- 🔧 靈活的報告設置
- 💡 智能工具提示
- 🔗 超連結支持（可點擊跳轉）

## 安裝步驟

### 1. 環境設置
```bash
# 運行環境設置腳本
setup.bat
```

### 2. 啟動程序
```bash
# 運行啟動腳本
start.bat
```

## 使用說明

### 主頁
- **目標頻道**: 輸入要報告的頻道用戶名（不含@）
- **報告數量**: 設置每個帳戶的報告次數
- **報告原因**: 選擇報告的原因類型
- **開始報告**: 點擊開始執行報告操作

### 帳戶管理
- **添加帳戶**: 輸入電話號碼添加新的Telegram帳戶
- **帳戶列表**: 查看和管理已添加的帳戶
- **刪除帳戶**: 選擇並刪除不需要的帳戶

### 設置
- **API設置**: 配置Telegram API ID和Hash
- **報告設置**: 調整自動加入頻道和報告間隔等選項
- **保存設置**: 保存所有配置到config.txt文件

### 日誌
- **實時日誌**: 查看程序運行的詳細日誌
- **清除日誌**: 清空日誌內容

## 配置文件

程序使用`config.txt`文件保存設置：

```ini
# Telegram API 配置
api_id=1234567
api_hash=your_api_hash_here

# 默認設置
default_report_count=100
default_target_channel=
default_report_mode=spam

# UI 設置
theme=dark
window_width=800
window_height=600

# 報告設置
auto_join_channel=true
delay_between_reports=1
```

## 報告原因類型

- `spam` - 垃圾信息
- `fake_account` - 虛假帳戶
- `violence` - 暴力內容
- `child_abuse` - 兒童虐待
- `pornography` - 色情內容
- `geoirrelevant` - 地理位置不相關

## 注意事項

1. **API設置**: 請確保在設置中配置正確的Telegram API ID和Hash
2. **帳戶安全**: 請妥善保管帳戶session文件
3. **使用限制**: 請遵守Telegram的使用條款和當地法律法規
4. **頻率控制**: 建議設置適當的報告間隔，避免被限制

## 文件結構

```
tg/
├── main.py              # 原始命令行版本
├── ui.py                # 主UI程序
├── config_manager.py    # 配置管理器
├── telegram_reporter.py # 報告器核心功能
├── language_manager.py  # 語言管理器
├── lang/                # 語言文件目錄
│   ├── en.json         # 英文語言文件
│   ├── zh-TW.json      # 繁體中文語言文件
│   └── ru.json         # 俄文語言文件
├── config.txt           # 配置文件
├── requirements.txt     # 依賴項列表
├── setup.bat           # 環境設置腳本
├── start.bat           # 啟動腳本
└── README.md           # 說明文檔
```

## 開發者

- 原作者: [t.me/Mr3rf1](https://t.me/Mr3rf1)
- 原版項目: [Mr3rf1/TelReper](https://github.com/Mr3rf1/TelReper)
- UI改進: 基於原版本開發，添加圖形界面和多語言支持

## 🤝 支持

- 支持者: [@asenyeroao-ct](https://github.com/asenyeroao-ct)
- 感謝所有為此項目做出貢獻的開發者

## 免責聲明

本工具僅供學習和研究使用。使用者需要對自己的行為負責，並遵守相關法律法規。開發者不對任何濫用行為承擔責任。 