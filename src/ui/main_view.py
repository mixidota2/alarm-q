# -*- coding: utf-8 -*-
import flet as ft
from typing import List, Optional, Callable
from models.alarm import Alarm
from utils.storage import AlarmStorage


class MainView:
    def __init__(self, on_alarm_settings: Optional[Callable] = None, on_show_message: Optional[Callable] = None, 
                 on_problem_settings: Optional[Callable] = None, on_settings: Optional[Callable] = None):
        self.on_alarm_settings = on_alarm_settings
        self.on_show_message = on_show_message
        self.on_problem_settings = on_problem_settings
        self.on_settings = on_settings
        self.alarm_storage = AlarmStorage()
        self.alarms: List[Alarm] = []
        self.next_alarm_text = ft.Text(
            "次のアラーム: 未設定",
            size=18,
            weight=ft.FontWeight.BOLD
        )
        self.alarms_list = None  # buildメソッドで初期化
    
    def build(self) -> ft.Control:
        title = ft.Text(
            "alarm-q",
            size=32,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        )
        
        alarm_settings_btn = ft.ElevatedButton(
            text="アラーム設定",
            on_click=self._on_alarm_settings_click,
            width=200,
            height=50,
            bgcolor="blue",
            color="white"
        )
        
        problem_settings_btn = ft.ElevatedButton(
            text="問題管理",
            on_click=self._on_problem_settings_click,
            width=200,
            height=50,
            bgcolor="green",
            color="white"
        )
        
        settings_btn = ft.ElevatedButton(
            text="設定",
            on_click=self._on_settings_click,
            width=200,
            height=50,
            bgcolor="orange",
            color="white"
        )
        
        buttons_row = ft.Row(
            [alarm_settings_btn, problem_settings_btn, settings_btn],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20
        )
        
        # アラーム一覧用のColumn（現在は使用しないがself.alarms_listを初期化）
        self.alarms_list = ft.Column(spacing=10)
        
        # ListViewを使用してスクロール可能にする（より確実な方法）
        all_items = []
        
        # ヘッダー部分をListViewの要素として追加
        all_items.append(
            ft.Container(
                content=title,
                padding=20,
                alignment=ft.alignment.center
            )
        )
        
        all_items.append(
            ft.Container(
                content=self.next_alarm_text,
                padding=20,
                alignment=ft.alignment.center
            )
        )
        
        all_items.append(
            ft.Container(
                content=buttons_row,
                padding=20,
                alignment=ft.alignment.center
            )
        )
        
        all_items.append(ft.Divider())
        
        all_items.append(
            ft.Container(
                content=ft.Text(
                    "アラーム一覧",
                    size=20,
                    weight=ft.FontWeight.BOLD
                ),
                padding=ft.padding.symmetric(horizontal=20, vertical=10)
            )
        )
        
        # アラーム項目を追加
        for alarm in self.alarms:
            alarm_item = self._create_alarm_item(alarm)
            all_items.append(
                ft.Container(
                    content=alarm_item,
                    padding=ft.padding.symmetric(horizontal=20, vertical=5)
                )
            )
        
        # ListViewを使用
        main_listview = ft.ListView(
            controls=all_items,
            expand=True,
            spacing=0,
            padding=ft.padding.all(0)
        )
        
        return main_listview
    
    def _on_alarm_settings_click(self, e):
        if self.on_alarm_settings:
            self.on_alarm_settings()
    
    def _on_problem_settings_click(self, e):
        print("問題管理ボタンがクリックされました")
        if self.on_problem_settings:
            self.on_problem_settings()
    
    def _on_settings_click(self, e):
        print("設定ボタンがクリックされました")
        if self.on_settings:
            self.on_settings()
    
    def refresh_alarms(self):
        self.alarms = self.alarm_storage.load_alarms()
        self._update_next_alarm()
        self._update_alarms_list()
    
    def _update_next_alarm(self):
        enabled_alarms = [alarm for alarm in self.alarms if alarm.enabled]
        if enabled_alarms:
            next_alarm = min(enabled_alarms, key=lambda a: a.time)
            self.next_alarm_text.value = f"次のアラーム: {next_alarm.time} ({next_alarm.label})"
        else:
            self.next_alarm_text.value = "次のアラーム: 未設定"
        
    
    def _update_alarms_list(self):
        # ListView方式では、get_view()を再度呼び出して全体を再構築
        # このメソッドは現在使用されていないが、互換性のため残す
        pass
        
    
    def _create_alarm_item(self, alarm: Alarm) -> ft.Control:
        switch = ft.Switch(
            value=alarm.enabled,
            on_change=lambda e, a=alarm: self._toggle_alarm(a, e.control.value)
        )
        
        time_text = ft.Text(
            alarm.time,
            size=18,
            weight=ft.FontWeight.BOLD
        )
        
        label_text = ft.Text(
            alarm.label,
            size=14,
            color="grey700"
        )
        
        days_text = ft.Text(
            ", ".join(alarm.days),
            size=12,
            color="grey500"
        )
        
        info_column = ft.Column([
            time_text,
            label_text,
            days_text
        ])
        
        edit_button = ft.IconButton(
            icon="edit",
            tooltip="編集",
            on_click=lambda e, a=alarm: self._edit_alarm(a.id)
        )
        
        return ft.Card(
            content=ft.Container(
                content=ft.Row([
                    info_column,
                    ft.Row([edit_button, switch], spacing=10)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=15
            ),
            margin=ft.margin.only(bottom=10)
        )
    
    def _toggle_alarm(self, alarm: Alarm, enabled: bool):
        alarm.enabled = enabled
        self.alarm_storage.save_alarm(alarm)
        self._update_next_alarm()
    
    def _edit_alarm(self, alarm_id: str):
        if self.on_alarm_settings:
            self.on_alarm_settings(alarm_id)
    
    def get_view(self) -> ft.Control:
        self.refresh_alarms()
        return self.build()