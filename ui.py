import tkinter as tk
from tkinter import messagebox, scrolledtext
import customtkinter as ctk
import threading
import time
import webbrowser
from config_manager import ConfigManager
from telegram_reporter import TelegramReporter
from language_manager import LanguageManager

class ToolTip:
    """自定義Tooltip類"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        """顯示tooltip"""
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        
        # 創建tooltip窗口
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        # 設置tooltip樣式
        label = tk.Label(
            self.tooltip, 
            text=self.text, 
            justify=tk.LEFT,
            background="#2b2b2b",
            foreground="white",
            relief=tk.SOLID,
            borderwidth=1,
            font=("Segoe UI", 9)
        )
        label.pack(padx=5, pady=3)
        
        # 設置透明度
        self.tooltip.attributes('-alpha', 0.9)
    
    def hide_tooltip(self, event=None):
        """隱藏tooltip"""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class HyperlinkLabel:
    """超連結標籤類"""
    def __init__(self, parent, text, url, **kwargs):
        self.url = url
        self.label = ctk.CTkLabel(
            parent,
            text=text,
            text_color="#1976D2",
            cursor="hand2",
            **kwargs
        )
        self.label.bind("<Button-1>", self.open_url)
        self.label.bind("<Enter>", self.on_enter)
        self.label.bind("<Leave>", self.on_leave)
    
    def open_url(self, event=None):
        """打開URL"""
        try:
            webbrowser.open(self.url)
        except Exception as e:
            print(f"無法打開URL: {e}")
    
    def on_enter(self, event=None):
        """鼠標進入時改變顏色"""
        self.label.configure(text_color="#1565C0")
    
    def on_leave(self, event=None):
        """鼠標離開時恢復顏色"""
        self.label.configure(text_color="#1976D2")
    
    def pack(self, **kwargs):
        """包裝pack方法"""
        return self.label.pack(**kwargs)
    
    def configure(self, **kwargs):
        """包裝configure方法"""
        return self.label.configure(**kwargs)

class TelegramReporterUI:
    def __init__(self):
        # 設置主題
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # 初始化配置管理器
        self.config = ConfigManager()
        
        # 初始化語言管理器
        self.lang = LanguageManager()
        self.lang.load_language(self.config.get('language', 'zh-TW'))
        
        # 創建主窗口
        self.root = ctk.CTk()
        lang_info = self.lang.get_language_info()
        self.root.title(f"{lang_info['app_title']} - {lang_info['author']}")
        self.root.geometry(f"{self.config.get('window_width', 1000)}x{self.config.get('window_height', 700)}")
        self.root.resizable(True, True)
        
        # 設置窗口圖標和最小尺寸
        self.root.minsize(800, 600)
        
        # 初始化變量
        self.is_reporting = False
        self.reporting_thread = None
        
        # 初始化報告器
        self.reporter = TelegramReporter(self.config)
        
        # 創建UI元素
        self.create_widgets()
        
        # 更新帳戶列表
        self.update_account_list()
    
    def create_widgets(self):
        """創建UI元素"""
        # 主框架
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # 標題框架
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # 標題
        title_label = ctk.CTkLabel(
            title_frame, 
            text=f"📱 {self.lang.get_text('app_title')}", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(side="left")
        
        # 版本信息
        lang_info = self.lang.get_language_info()
        version_label = ctk.CTkLabel(
            title_frame,
            text=f"{lang_info['version']} - {lang_info['author']}",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        version_label.pack(side="right", pady=10)
        
        # 支持者信息（超連結）
        supporter_link = HyperlinkLabel(
            title_frame,
            text=f"🤝 {lang_info['supporter']}",
            url=lang_info['supporter_link'],
            font=ctk.CTkFont(size=10)
        )
        supporter_link.pack(side="right", padx=(0, 15), pady=10)
        
        # 為支持者鏈接添加tooltip
        ToolTip(supporter_link.label, f"點擊訪問支持者 {lang_info['supporter']} 的GitHub主頁")
        
        # 關於按鈕
        about_button = ctk.CTkButton(
            title_frame,
            text="ℹ️ 關於",
            command=self.show_about,
            width=60,
            height=25,
            font=ctk.CTkFont(size=10)
        )
        about_button.pack(side="right", padx=(0, 10), pady=10)
        
        # 創建筆記本（標籤頁）
        notebook = ctk.CTkTabview(main_frame)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 主頁標籤
        main_tab = notebook.add(self.lang.get_text('tabs.main'))
        self.create_main_tab(main_tab)
        
        # 帳戶管理標籤
        accounts_tab = notebook.add(self.lang.get_text('tabs.accounts'))
        self.create_accounts_tab(accounts_tab)
        
        # 設置標籤
        settings_tab = notebook.add(self.lang.get_text('tabs.settings'))
        self.create_settings_tab(settings_tab)
        
        # 日誌標籤
        log_tab = notebook.add(self.lang.get_text('tabs.log'))
        self.create_log_tab(log_tab)
    
    def create_main_tab(self, parent):
        """創建主頁標籤"""
        # 目標頻道框架
        target_frame = ctk.CTkFrame(parent)
        target_frame.pack(fill="x", padx=10, pady=8)
        
        # 目標頻道標題
        target_title = ctk.CTkLabel(
            target_frame, 
            text=self.lang.get_text('main_tab.target_channel'), 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        target_title.pack(anchor="w", padx=15, pady=(15, 8))
        
        # 輸入框架
        input_frame = ctk.CTkFrame(target_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkLabel(input_frame, text=self.lang.get_text('main_tab.channel_username'), font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 10))
        
        self.target_entry = ctk.CTkEntry(
            input_frame, 
            placeholder_text=self.lang.get_text('main_tab.channel_placeholder'),
            width=400,
            height=35
        )
        self.target_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.target_entry.insert(0, self.config.get('default_target_channel', ''))
        
        # 為目標頻道輸入框添加tooltip
        ToolTip(self.target_entry, self.lang.format_tooltip('target_channel'))
        
        # 清除按鈕
        clear_target_btn = ctk.CTkButton(
            input_frame,
            text=self.lang.get_text('main_tab.clear'),
            width=60,
            height=35,
            command=lambda: self.target_entry.delete(0, tk.END)
        )
        clear_target_btn.pack(side="right")
        
        # 為清除按鈕添加tooltip
        ToolTip(clear_target_btn, self.lang.format_tooltip('clear_target'))
        
        # 報告設置框架
        report_frame = ctk.CTkFrame(parent)
        report_frame.pack(fill="x", padx=10, pady=8)
        
        # 報告設置標題
        report_title = ctk.CTkLabel(
            report_frame, 
            text="⚙️ 報告設置", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        report_title.pack(anchor="w", padx=15, pady=(15, 12))
        
        # 設置選項框架
        settings_frame = ctk.CTkFrame(report_frame, fg_color="transparent")
        settings_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # 左側設置
        left_settings = ctk.CTkFrame(settings_frame, fg_color="transparent")
        left_settings.pack(side="left", fill="x", expand=True)
        
        # 報告數量
        count_frame = ctk.CTkFrame(left_settings, fg_color="transparent")
        count_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(count_frame, text="📊 報告數量:", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 10))
        self.count_entry = ctk.CTkEntry(count_frame, width=120, height=32)
        self.count_entry.pack(side="left")
        self.count_entry.insert(0, str(self.config.get('default_report_count', 100)))
        
        # 為報告數量輸入框添加tooltip
        ToolTip(self.count_entry, "設置每個帳戶要發送的報告數量\n建議設置在10-1000之間")
        
        # 右側設置
        right_settings = ctk.CTkFrame(settings_frame, fg_color="transparent")
        right_settings.pack(side="right", fill="x", expand=True)
        
        # 報告原因
        reason_frame = ctk.CTkFrame(right_settings, fg_color="transparent")
        reason_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(reason_frame, text="🚨 報告原因:", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 10))
        
        self.reason_var = tk.StringVar(value=self.config.get('default_report_mode', 'spam'))
        reasons = ['spam', 'fake_account', 'violence', 'child_abuse', 'pornography', 'geoirrelevant']
        
        self.reason_menu = ctk.CTkOptionMenu(
            reason_frame, 
            values=reasons,
            variable=self.reason_var,
            width=180,
            height=32
        )
        self.reason_menu.pack(side="left")
        
        # 為報告原因選擇框添加tooltip
        ToolTip(self.reason_menu, "選擇報告的原因類型\n• spam: 垃圾信息\n• fake_account: 虛假帳戶\n• violence: 暴力內容\n• child_abuse: 兒童虐待\n• pornography: 色情內容\n• geoirrelevant: 地理位置不相關")
        
        # 帳戶信息框架
        accounts_info_frame = ctk.CTkFrame(parent)
        accounts_info_frame.pack(fill="x", padx=10, pady=8)
        
        # 帳戶信息標題
        accounts_title = ctk.CTkLabel(
            accounts_info_frame, 
            text="👥 帳戶信息", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        accounts_title.pack(anchor="w", padx=15, pady=(15, 8))
        
        # 帳戶狀態框架
        status_frame = ctk.CTkFrame(accounts_info_frame, fg_color="transparent")
        status_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.accounts_label = ctk.CTkLabel(
            status_frame, 
            text="載入中...", 
            font=ctk.CTkFont(size=14)
        )
        self.accounts_label.pack(side="left")
        
        # 刷新按鈕
        refresh_btn = ctk.CTkButton(
            status_frame,
            text="🔄 刷新",
            width=80,
            height=30,
            command=self.update_account_list
        )
        refresh_btn.pack(side="right")
        
        # 為刷新按鈕添加tooltip
        ToolTip(refresh_btn, "刷新帳戶列表\n重新掃描sessions目錄中的帳戶文件")
        
        # 控制按鈕框架
        control_frame = ctk.CTkFrame(parent)
        control_frame.pack(fill="x", padx=10, pady=12)
        
        # 按鈕框架
        button_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=15, pady=15)
        
        self.start_button = ctk.CTkButton(
            button_frame,
            text="🚀 開始報告",
            command=self.start_reporting,
            fg_color="#2E7D32",
            hover_color="#1B5E20",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.start_button.pack(side="left", padx=(0, 10))
        
        # 為開始報告按鈕添加tooltip
        ToolTip(self.start_button, "開始執行報告操作\n確保已添加帳戶並設置目標頻道")
        
        self.stop_button = ctk.CTkButton(
            button_frame,
            text="⏹️ 停止報告",
            command=self.stop_reporting,
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=(0, 20))
        
        # 為停止報告按鈕添加tooltip
        ToolTip(self.stop_button, "停止當前的報告操作\n正在進行的報告將被中斷")
        
        # 進度框架
        progress_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        progress_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # 進度條
        self.progress_bar = ctk.CTkProgressBar(progress_frame, height=8)
        self.progress_bar.pack(fill="x", pady=(0, 8))
        self.progress_bar.set(0)
        
        # 狀態標籤
        self.status_label = ctk.CTkLabel(
            progress_frame, 
            text="✅ 就緒", 
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(anchor="w")
    
    def create_accounts_tab(self, parent):
        """創建帳戶管理標籤"""
        # 添加帳戶框架
        add_frame = ctk.CTkFrame(parent)
        add_frame.pack(fill="x", padx=10, pady=8)
        
        # 添加帳戶標題
        add_title = ctk.CTkLabel(
            add_frame, 
            text="➕ 添加新帳戶", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        add_title.pack(anchor="w", padx=15, pady=(15, 12))
        
        # 電話號碼輸入框架
        phone_frame = ctk.CTkFrame(add_frame, fg_color="transparent")
        phone_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkLabel(phone_frame, text="📞 電話號碼:", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 10))
        
        self.phone_entry = ctk.CTkEntry(
            phone_frame, 
            placeholder_text="+1234567890",
            height=35
        )
        self.phone_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # 為電話號碼輸入框添加tooltip
        ToolTip(self.phone_entry, "輸入Telegram帳戶的電話號碼\n格式：+國家代碼 電話號碼\n例如：+86 13800138000")
        
        self.add_account_button = ctk.CTkButton(
            phone_frame,
            text="➕ 添加帳戶",
            command=self.add_account,
            height=35,
            fg_color="#1976D2",
            hover_color="#1565C0"
        )
        self.add_account_button.pack(side="right")
        
        # 為添加帳戶按鈕添加tooltip
        ToolTip(self.add_account_button, "添加新的Telegram帳戶\n首次添加需要輸入驗證碼")
        
        # 帳戶列表框架
        list_frame = ctk.CTkFrame(parent)
        list_frame.pack(fill="both", expand=True, padx=10, pady=8)
        
        # 帳戶列表標題
        list_title = ctk.CTkLabel(
            list_frame, 
            text="📋 已添加的帳戶", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        list_title.pack(anchor="w", padx=15, pady=(15, 12))
        
        # 列表控制框架
        list_control_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        list_control_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        # 帳戶列表
        list_container = ctk.CTkFrame(list_frame)
        list_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.accounts_listbox = tk.Listbox(
            list_container,
            bg="#2b2b2b",
            fg="white",
            selectbackground="#1976D2",
            selectforeground="white",
            font=("Segoe UI", 11),
            borderwidth=0,
            highlightthickness=1,
            highlightcolor="#1976D2"
        )
        self.accounts_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 按鈕框架
        button_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # 刪除按鈕
        self.delete_account_button = ctk.CTkButton(
            button_frame,
            text="🗑️ 刪除選中帳戶",
            command=self.delete_account,
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            height=35
        )
        self.delete_account_button.pack(side="left")
        
        # 為刪除按鈕添加tooltip
        ToolTip(self.delete_account_button, "刪除選中的帳戶\n此操作會永久刪除帳戶session文件")
        
        # 全選按鈕
        select_all_btn = ctk.CTkButton(
            button_frame,
            text="☑️ 全選",
            command=lambda: self.accounts_listbox.select_set(0, tk.END),
            height=35,
            fg_color="#FF9800",
            hover_color="#F57C00"
        )
        select_all_btn.pack(side="right", padx=(10, 0))
        
        # 為全選按鈕添加tooltip
        ToolTip(select_all_btn, "選擇所有帳戶\n用於批量操作")
        
        # 取消選擇按鈕
        deselect_btn = ctk.CTkButton(
            button_frame,
            text="☐ 取消選擇",
            command=lambda: self.accounts_listbox.selection_clear(0, tk.END),
            height=35,
            fg_color="#757575",
            hover_color="#616161"
        )
        deselect_btn.pack(side="right")
        
        # 為取消選擇按鈕添加tooltip
        ToolTip(deselect_btn, "取消所有選擇\n清除當前選中的帳戶")
    
    def create_settings_tab(self, parent):
        """創建設置標籤"""
        # API設置框架
        api_frame = ctk.CTkFrame(parent)
        api_frame.pack(fill="x", padx=10, pady=8)
        
        # API設置標題
        api_title = ctk.CTkLabel(
            api_frame, 
            text="🔑 API設置", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        api_title.pack(anchor="w", padx=15, pady=(15, 12))
        
        # API ID
        api_id_frame = ctk.CTkFrame(api_frame, fg_color="transparent")
        api_id_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(api_id_frame, text="🔢 API ID:", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 10))
        self.api_id_entry = ctk.CTkEntry(api_id_frame, height=35)
        self.api_id_entry.pack(side="left", fill="x", expand=True)
        self.api_id_entry.insert(0, str(self.config.get('api_id', '')))
        
        # 為API ID輸入框添加tooltip
        ToolTip(self.api_id_entry, "輸入您的Telegram API ID\n可在 https://my.telegram.org 獲取")
        
        # API Hash
        api_hash_frame = ctk.CTkFrame(api_frame, fg_color="transparent")
        api_hash_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(api_hash_frame, text="🔐 API Hash:", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 10))
        self.api_hash_entry = ctk.CTkEntry(api_hash_frame, show="*", height=35)
        self.api_hash_entry.pack(side="left", fill="x", expand=True)
        self.api_hash_entry.insert(0, self.config.get('api_hash', ''))
        
        # 為API Hash輸入框添加tooltip
        ToolTip(self.api_hash_entry, "輸入您的Telegram API Hash\n可在 https://my.telegram.org 獲取")
        
        # 顯示/隱藏密碼按鈕
        self.show_hash_var = tk.BooleanVar()
        show_hash_check = ctk.CTkCheckBox(
            api_hash_frame,
            text="顯示",
            variable=self.show_hash_var,
            command=self.toggle_hash_visibility
        )
        show_hash_check.pack(side="right", padx=(10, 0))
        
        # 報告設置框架
        report_settings_frame = ctk.CTkFrame(parent)
        report_settings_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(report_settings_frame, text="報告設置:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        # 自動加入頻道
        self.auto_join_var = tk.BooleanVar(value=self.config.get('auto_join_channel', True))
        auto_join_check = ctk.CTkCheckBox(
            report_settings_frame,
            text="自動加入目標頻道",
            variable=self.auto_join_var
        )
        auto_join_check.pack(anchor="w", padx=10, pady=5)
        
        # 為自動加入頻道選項添加tooltip
        ToolTip(auto_join_check, "啟用後，程序會自動加入目標頻道\n如果已加入頻道，此選項不會重複加入")
        
        # 報告間隔
        delay_frame = ctk.CTkFrame(report_settings_frame)
        delay_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(delay_frame, text="報告間隔(秒):").pack(side="left", padx=10)
        self.delay_entry = ctk.CTkEntry(delay_frame, width=100)
        self.delay_entry.pack(side="left", padx=10)
        self.delay_entry.insert(0, str(self.config.get('delay_between_reports', 1)))
        
        # 為報告間隔輸入框添加tooltip
        ToolTip(self.delay_entry, "設置每次報告之間的延遲時間\n建議設置1-5秒，避免被限制")
        
        # 保存按鈕
        save_button = ctk.CTkButton(
            parent,
            text="💾 保存設置",
            command=self.save_settings,
            height=35,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        save_button.pack(pady=20)
        
        # 為保存設置按鈕添加tooltip
        ToolTip(save_button, "保存所有設置到配置文件\n設置將在下次啟動時自動載入")
        
        # 幫助鏈接框架
        help_frame = ctk.CTkFrame(parent, fg_color="transparent")
        help_frame.pack(fill="x", padx=10, pady=10)
        
        help_label = ctk.CTkLabel(
            help_frame,
            text="需要幫助？",
            font=ctk.CTkFont(size=12)
        )
        help_label.pack(side="left")
        
        # API幫助鏈接
        api_help_link = HyperlinkLabel(
            help_frame,
            text="獲取API憑證",
            url="https://my.telegram.org",
            font=ctk.CTkFont(size=12)
        )
        api_help_link.pack(side="left", padx=(10, 0))
        
        # 為API幫助鏈接添加tooltip
        ToolTip(api_help_link.label, "點擊前往Telegram API開發工具頁面\n獲取您的API ID和API Hash")
        
        # GitHub幫助鏈接
        github_help_link = HyperlinkLabel(
            help_frame,
            text="查看文檔",
            url="https://github.com/Mr3rf1/TelReper",
            font=ctk.CTkFont(size=12)
        )
        github_help_link.pack(side="left", padx=(10, 0))
        
        # 為GitHub幫助鏈接添加tooltip
        ToolTip(github_help_link.label, "點擊查看原版項目文檔\n了解更多使用方法和注意事項")
    
    def create_log_tab(self, parent):
        """創建日誌標籤"""
        # 日誌標題框架
        log_title_frame = ctk.CTkFrame(parent, fg_color="transparent")
        log_title_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # 日誌標題
        log_title = ctk.CTkLabel(
            log_title_frame,
            text="📝 運行日誌",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        log_title.pack(side="left")
        
        # 日誌控制按鈕
        log_control_frame = ctk.CTkFrame(parent, fg_color="transparent")
        log_control_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # 清除日誌按鈕
        clear_button = ctk.CTkButton(
            log_control_frame,
            text="🗑️ 清除日誌",
            command=self.clear_log,
            height=32,
            fg_color="#FF5722",
            hover_color="#E64A19"
        )
        clear_button.pack(side="left")
        
        # 為清除日誌按鈕添加tooltip
        ToolTip(clear_button, "清除所有日誌內容\n此操作不可撤銷")
        
        # 導出日誌按鈕
        export_button = ctk.CTkButton(
            log_control_frame,
            text="💾 導出日誌",
            command=self.export_log,
            height=32,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        export_button.pack(side="left", padx=(10, 0))
        
        # 為導出日誌按鈕添加tooltip
        ToolTip(export_button, "將當前日誌保存到文本文件\n可選擇保存位置和文件名")
        
        # 日誌文本框容器
        log_container = ctk.CTkFrame(parent)
        log_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # 日誌文本框
        self.log_text = scrolledtext.ScrolledText(
            log_container,
            bg="#1e1e1e",
            fg="#ffffff",
            font=("Consolas", 10),
            wrap=tk.WORD,
            insertbackground="white",
            selectbackground="#1976D2",
            selectforeground="white"
        )
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    def log_message(self, message):
        """添加日誌消息"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """清除日誌"""
        self.log_text.delete(1.0, tk.END)
    
    def toggle_hash_visibility(self):
        """切換API Hash的可見性"""
        if self.show_hash_var.get():
            self.api_hash_entry.configure(show="")
        else:
            self.api_hash_entry.configure(show="*")
    
    def export_log(self):
        """導出日誌到文件"""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="導出日誌"
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("成功", f"日誌已導出到: {filename}")
                self.log_message(f"✅ 日誌已導出到: {filename}")
        except Exception as e:
            messagebox.showerror("錯誤", f"導出日誌失敗: {str(e)}")
            self.log_message(f"❌ 導出日誌失敗: {str(e)}")
    
    def show_about(self):
        """顯示關於對話框"""
        lang_info = self.lang.get_language_info()
        
        about_window = ctk.CTkToplevel(self.root)
        about_window.title("關於")
        about_window.geometry("600x500")
        about_window.resizable(False, False)
        
        # 設置為模態窗口
        about_window.transient(self.root)
        about_window.grab_set()
        
        # 主框架
        main_frame = ctk.CTkFrame(about_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 標題
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"{self.lang.get_text('app_title')} {lang_info['version']}",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        # 信息框架
        info_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=20)
        
        # 原作者信息
        author_label = ctk.CTkLabel(
            info_frame,
            text="原作者:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        author_label.pack(anchor="w", pady=(0, 5))
        
        author_link = HyperlinkLabel(
            info_frame,
            text=lang_info['author'],
            url=f"https://{lang_info['author']}",
            font=ctk.CTkFont(size=12)
        )
        author_link.pack(anchor="w", pady=(0, 15))
        
        # 原版項目信息
        project_label = ctk.CTkLabel(
            info_frame,
            text="原版項目:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        project_label.pack(anchor="w", pady=(0, 5))
        
        project_link = HyperlinkLabel(
            info_frame,
            text="GitHub Repository",
            url=lang_info['github_link'],
            font=ctk.CTkFont(size=12)
        )
        project_link.pack(anchor="w", pady=(0, 15))
        
        # 支持者信息
        supporter_label = ctk.CTkLabel(
            info_frame,
            text="支持者:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        supporter_label.pack(anchor="w", pady=(0, 5))
        
        supporter_link = HyperlinkLabel(
            info_frame,
            text=lang_info['supporter'],
            url=lang_info['supporter_link'],
            font=ctk.CTkFont(size=12)
        )
        supporter_link.pack(anchor="w", pady=(0, 20))
        
        # 功能特點
        features_label = ctk.CTkLabel(
            info_frame,
            text="功能特點:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        features_label.pack(anchor="w", pady=(0, 10))
        
        features_text = """• 現代化圖形界面
• 多語言支持
• 多帳戶管理
• 批量報告功能
• 實時進度顯示
• 詳細日誌記錄
• 智能工具提示"""
        
        features_list = ctk.CTkLabel(
            info_frame,
            text=features_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        features_list.pack(anchor="w", pady=(0, 20))
        
        # 感謝信息
        thanks_label = ctk.CTkLabel(
            info_frame,
            text="感謝所有為此項目做出貢獻的開發者！",
            font=ctk.CTkFont(size=12),
            text_color="#4CAF50"
        )
        thanks_label.pack(anchor="w", pady=(0, 20))
        
        # 關閉按鈕
        close_button = ctk.CTkButton(
            main_frame,
            text="關閉",
            command=about_window.destroy,
            width=100
        )
        close_button.pack(pady=(0, 20))
    
    def update_account_list(self):
        """更新帳戶列表"""
        session_files = self.reporter.get_session_files()
        
        # 更新帳戶數量標籤
        if len(session_files) == 0:
            self.accounts_label.configure(text="❌ 未添加任何帳戶")
        elif len(session_files) == 1:
            self.accounts_label.configure(text=f"✅ 已添加 1 個帳戶")
        else:
            self.accounts_label.configure(text=f"✅ 已添加 {len(session_files)} 個帳戶")
        
        # 更新列表框
        self.accounts_listbox.delete(0, tk.END)
        for session_file in session_files:
            account_name = session_file.replace('.session', '')
            self.accounts_listbox.insert(tk.END, f"📱 {account_name}")
    
    def add_account(self):
        """添加帳戶"""
        phone_number = self.phone_entry.get().strip()
        if not phone_number:
            messagebox.showerror("錯誤", "請輸入電話號碼！")
            return
        
        self.add_account_button.configure(state="disabled", text="添加中...")
        self.log_message(f"正在添加帳戶: {phone_number}")
        
        def add_account_thread():
            success, message = self.reporter.add_account(phone_number)
            
            def update_ui():
                self.add_account_button.configure(state="normal", text="添加帳戶")
                self.phone_entry.delete(0, tk.END)
                self.update_account_list()
                
                if success:
                    messagebox.showinfo("成功", message)
                    self.log_message(f"✅ {message}")
                else:
                    messagebox.showerror("錯誤", message)
                    self.log_message(f"❌ {message}")
            
            self.root.after(0, update_ui)
        
        threading.Thread(target=add_account_thread, daemon=True).start()
    
    def delete_account(self):
        """刪除選中的帳戶"""
        selection = self.accounts_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "請選擇要刪除的帳戶！")
            return
        
        account_name = self.accounts_listbox.get(selection[0])
        if messagebox.askyesno("確認", f"確定要刪除帳戶 {account_name} 嗎？"):
            import os
            session_file = os.path.join('sessions', f'{account_name}.session')
            try:
                os.remove(session_file)
                self.update_account_list()
                self.log_message(f"已刪除帳戶: {account_name}")
                messagebox.showinfo("成功", f"已刪除帳戶 {account_name}")
            except Exception as e:
                messagebox.showerror("錯誤", f"刪除帳戶時發生錯誤: {str(e)}")
    
    def save_settings(self):
        """保存設置"""
        try:
            # 保存API設置
            self.config.set('api_id', int(self.api_id_entry.get()))
            self.config.set('api_hash', self.api_hash_entry.get())
            
            # 保存報告設置
            self.config.set('auto_join_channel', self.auto_join_var.get())
            self.config.set('delay_between_reports', int(self.delay_entry.get()))
            
            # 重新初始化報告器
            self.reporter = TelegramReporter(self.config)
            
            messagebox.showinfo("成功", "設置已保存！")
            self.log_message("設置已保存")
        except ValueError as e:
            messagebox.showerror("錯誤", f"設置格式錯誤: {str(e)}")
    
    def start_reporting(self):
        """開始報告"""
        # 獲取參數
        target_channel = self.target_entry.get().strip()
        if not target_channel:
            messagebox.showerror("錯誤", "請輸入目標頻道！")
            return
        
        try:
            report_count = int(self.count_entry.get())
            if report_count <= 0:
                raise ValueError("報告數量必須大於0")
        except ValueError:
            messagebox.showerror("錯誤", "請輸入有效的報告數量！")
            return
        
        report_mode = self.reason_var.get()
        
        # 檢查是否有帳戶
        session_files = self.reporter.get_session_files()
        if not session_files:
            messagebox.showerror("錯誤", "請先添加帳戶！")
            return
        
        # 更新UI狀態
        self.is_reporting = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.progress_bar.set(0)
        self.status_label.configure(text="🔄 報告中...")
        
        # 保存當前設置為默認值
        self.config.set('default_target_channel', target_channel)
        self.config.set('default_report_count', report_count)
        self.config.set('default_report_mode', report_mode)
        
        self.log_message(f"🚀 開始報告頻道: {target_channel}")
        self.log_message(f"📊 報告數量: {report_count}, 原因: {report_mode}")
        self.log_message(f"👥 使用帳戶數量: {len(session_files)}")
        
        # 在線程中運行報告
        def reporting_thread():
            def progress_callback(message, current, total):
                def update_progress():
                    progress = current / total if total > 0 else 0
                    self.progress_bar.set(progress)
                    self.status_label.configure(text=f"報告中... {current}/{total}")
                    self.log_message(message)
                
                self.root.after(0, update_progress)
            
            success, message = self.reporter.run_reports_sync(
                target_channel, report_count, report_mode, progress_callback
            )
            
            def finish_reporting():
                self.is_reporting = False
                self.start_button.configure(state="normal")
                self.stop_button.configure(state="disabled")
                self.progress_bar.set(1.0)
                self.status_label.configure(text="✅ 完成")
                self.log_message(f"🏁 報告完成: {message}")
                
                if success:
                    messagebox.showinfo("完成", message)
                else:
                    messagebox.showerror("錯誤", message)
            
            self.root.after(0, finish_reporting)
        
        self.reporting_thread = threading.Thread(target=reporting_thread, daemon=True)
        self.reporting_thread.start()
    
    def stop_reporting(self):
        """停止報告"""
        if self.is_reporting:
            self.is_reporting = False
            self.status_label.configure(text="⏹️ 停止中...")
            self.log_message("⏹️ 正在停止報告...")
            
            # 重置UI狀態
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.progress_bar.set(0)
            self.status_label.configure(text="✅ 已停止")
            self.log_message("✅ 報告已停止")
        else:
            self.log_message("⚠️ 當前沒有正在運行的報告任務")
    
    def run(self):
        """運行UI"""
        self.root.mainloop()

if __name__ == "__main__":
    app = TelegramReporterUI()
    app.run() 