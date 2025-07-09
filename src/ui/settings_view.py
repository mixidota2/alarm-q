# -*- coding: utf-8 -*-
import flet as ft
from typing import Optional, Callable
import json
import os


class SettingsView:
    def __init__(self, on_back: Optional[Callable] = None):
        self.on_back = on_back
        self.settings_file = "storage/settings.json"
        self.settings = self._load_settings()
        
        # 音量設定
        self.volume_slider = ft.Slider(
            min=0.1,
            max=1.0,
            value=self.settings.get("default_volume", 0.8),
            divisions=9,
            label="音量: {value}",
            width=300
        )
        
        # デフォルト難易度
        self.difficulty_dropdown = ft.Dropdown(
            label="デフォルト難易度",
            width=200,
            options=[
                ft.dropdown.Option("easy", "簡単"),
                ft.dropdown.Option("medium", "普通"),
                ft.dropdown.Option("hard", "難しい")
            ],
            value=self.settings.get("default_difficulty", "medium")
        )
        
        # デフォルト問題セット
        self.problem_set_dropdown = ft.Dropdown(
            label="デフォルト問題セット",
            width=200,
            options=[
                ft.dropdown.Option("statistics", "統計学"),
                ft.dropdown.Option("math", "数学"),
                ft.dropdown.Option("general", "一般知識"),
                ft.dropdown.Option("science", "科学")
            ],
            value=self.settings.get("default_problem_set", "statistics")
        )
        
        # スヌーズ設定
        self.snooze_enabled = ft.Checkbox(
            label="デフォルトでスヌーズを有効にする",
            value=self.settings.get("default_snooze_enabled", True)
        )
        
        self.snooze_duration = ft.TextField(
            label="デフォルトスヌーズ間隔(秒)",
            value=str(self.settings.get("default_snooze_duration", 300)),
            width=200
        )
        
        self.snooze_max_count = ft.TextField(
            label="デフォルト最大スヌーズ回数",
            value=str(self.settings.get("default_snooze_max_count", 3)),
            width=200
        )
        
        # アプリ設定
        self.window_width = ft.TextField(
            label="ウィンドウ幅",
            value=str(self.settings.get("window_width", 800)),
            width=150
        )
        
        self.window_height = ft.TextField(
            label="ウィンドウ高さ",
            value=str(self.settings.get("window_height", 600)),
            width=150
        )
        
    def build(self) -> ft.Control:
        header = ft.Row([
            ft.IconButton(
                icon="arrow_back",
                tooltip="戻る",
                on_click=self._on_back_click
            ),
            ft.Text(
                "設定",
                size=24,
                weight=ft.FontWeight.BOLD
            )
        ])
        
        # 音量設定セクション
        volume_section = ft.Container(
            content=ft.Column([
                ft.Text("音量設定", size=18, weight=ft.FontWeight.BOLD),
                self.volume_slider
            ], spacing=10),
            padding=20,
            bgcolor="blue50",
            border_radius=10
        )
        
        # デフォルト設定セクション
        defaults_section = ft.Container(
            content=ft.Column([
                ft.Text("デフォルト設定", size=18, weight=ft.FontWeight.BOLD),
                ft.Row([
                    self.difficulty_dropdown,
                    self.problem_set_dropdown
                ], spacing=20),
            ], spacing=10),
            padding=20,
            bgcolor="green50",
            border_radius=10
        )
        
        # スヌーズ設定セクション
        snooze_section = ft.Container(
            content=ft.Column([
                ft.Text("スヌーズ設定", size=18, weight=ft.FontWeight.BOLD),
                self.snooze_enabled,
                ft.Row([
                    self.snooze_duration,
                    self.snooze_max_count
                ], spacing=20)
            ], spacing=10),
            padding=20,
            bgcolor="orange50",
            border_radius=10
        )
        
        # アプリ設定セクション
        app_section = ft.Container(
            content=ft.Column([
                ft.Text("アプリ設定", size=18, weight=ft.FontWeight.BOLD),
                ft.Row([
                    self.window_width,
                    self.window_height
                ], spacing=20)
            ], spacing=10),
            padding=20,
            bgcolor="purple50",
            border_radius=10
        )
        
        # 保存・リセットボタン
        buttons_row = ft.Row([
            ft.ElevatedButton(
                text="設定を保存",
                on_click=self._save_settings,
                bgcolor="green",
                color="white",
                width=150
            ),
            ft.ElevatedButton(
                text="デフォルトに戻す",
                on_click=self._reset_settings,
                bgcolor="red",
                color="white",
                width=150
            )
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
        
        main_content = ft.Column([
            header,
            ft.Divider(),
            volume_section,
            defaults_section,
            snooze_section,
            app_section,
            ft.Divider(),
            buttons_row
        ], spacing=20)
        
        return ft.Column(
            [main_content],
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
    
    def _load_settings(self) -> dict:
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def _save_settings(self, e):
        try:
            settings = {
                "default_volume": self.volume_slider.value,
                "default_difficulty": self.difficulty_dropdown.value,
                "default_problem_set": self.problem_set_dropdown.value,
                "default_snooze_enabled": self.snooze_enabled.value,
                "default_snooze_duration": int(self.snooze_duration.value),
                "default_snooze_max_count": int(self.snooze_max_count.value),
                "window_width": int(self.window_width.value),
                "window_height": int(self.window_height.value)
            }
            
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            self.settings = settings
            self._show_message("設定を保存しました")
            
        except Exception as ex:
            self._show_message(f"保存に失敗しました: {str(ex)}")
    
    def _reset_settings(self, e):
        # デフォルト値にリセット
        self.volume_slider.value = 0.8
        self.difficulty_dropdown.value = "medium"
        self.problem_set_dropdown.value = "statistics"
        self.snooze_enabled.value = True
        self.snooze_duration.value = "300"
        self.snooze_max_count.value = "3"
        self.window_width.value = "800"
        self.window_height.value = "600"
        
        self._show_message("設定をデフォルトに戻しました")
    
    def _on_back_click(self, e):
        if self.on_back:
            self.on_back()
    
    def _show_message(self, message: str):
        print(f"Settings: {message}")
    
    def get_view(self) -> ft.Control:
        return self.build()