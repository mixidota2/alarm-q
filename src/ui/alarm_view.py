# -*- coding: utf-8 -*-
import flet as ft
from typing import Optional, Callable, Dict
from models.alarm import Alarm, SoundConfig, SnoozeConfig
from utils.storage import AlarmStorage


class AlarmView:
    def __init__(self, on_back: Optional[Callable] = None, alarm_id: Optional[str] = None):
        self.on_back = on_back
        self.alarm_id = alarm_id
        self.alarm_storage = AlarmStorage()
        self.alarm: Optional[Alarm] = None
        
        self.time_input = ft.TextField(
            label="時刻 (HH:MM)",
            value="07:00",
            width=120
        )
        
        self.label_input = ft.TextField(
            label="ラベル",
            value="アラーム",
            width=150
        )
        
        self.days_checkboxes: Dict[str, ft.Checkbox] = {}
        self.difficulty_dropdown = ft.Dropdown(
            label="難易度",
            width=120,
            options=[
                ft.dropdown.Option("easy", "簡単"),
                ft.dropdown.Option("medium", "普通"),
                ft.dropdown.Option("hard", "難しい")
            ],
            value="medium"
        )
        
        self.problem_sets_dropdown = ft.Dropdown(
            label="問題セット",
            width=150,
            options=[
                ft.dropdown.Option("math", "数学"),
                ft.dropdown.Option("general", "一般知識"),
                ft.dropdown.Option("science", "科学")
            ],
            value="math"
        )
        
        self.volume_slider = ft.Slider(
            min=0.1,
            max=1.0,
            value=0.8,
            divisions=9,
            label="音量: {value}"
        )
        
        self.snooze_checkbox = ft.Checkbox(
            label="スヌーズ機能",
            value=True
        )
        
        self.snooze_duration = ft.TextField(
            label="間隔(秒)",
            value="300",
            width=100
        )
        
        self.snooze_max_count = ft.TextField(
            label="最大回数",
            value="3",
            width=100
        )
    
    def build(self) -> ft.Control:
        if self.alarm_id:
            self.alarm = self.alarm_storage.load_alarm(self.alarm_id)
            if self.alarm:
                self._load_alarm_data()
        
        days_row = self._create_days_row()
        
        form_column = ft.Column([
            ft.Row([
                ft.IconButton(
                    icon="arrow_back",
                    tooltip="戻る",
                    on_click=self._on_cancel
                ),
                ft.Text(
                    "アラーム設定" if not self.alarm_id else "アラーム編集",
                    size=24,
                    weight=ft.FontWeight.BOLD
                )
            ]),
            ft.Divider(),
            
            # 基本設定を横並びに
            ft.Row([
                self.time_input,
                self.label_input,
                self.difficulty_dropdown,
                self.problem_sets_dropdown
            ], spacing=15, wrap=True),
            
            # 曜日選択
            ft.Container(
                content=ft.Column([
                    ft.Text("曜日:", size=14),
                    days_row
                ], spacing=5),
                padding=ft.padding.symmetric(vertical=10)
            ),
            
            # 音量とスヌーズを横並びに
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Text("音量:", size=14),
                        self.volume_slider
                    ], spacing=5),
                    expand=1
                ),
                ft.Container(
                    content=ft.Column([
                        self.snooze_checkbox,
                        ft.Row([
                            self.snooze_duration,
                            self.snooze_max_count
                        ], spacing=10)
                    ], spacing=5),
                    expand=1
                )
            ], spacing=20),
            
            ft.Divider(),
            
            ft.Row(
                [
                    ft.ElevatedButton(
                        text="保存",
                        on_click=self._save_alarm,
                        bgcolor="green",
                        color="white"
                    ),
                    ft.ElevatedButton(
                        text="削除",
                        on_click=self._delete_alarm,
                        bgcolor="red",
                        color="white"
                    ) if self.alarm_id else None,
                    ft.ElevatedButton(
                        text="キャンセル",
                        on_click=self._on_cancel,
                        bgcolor="grey",
                        color="white"
                    )
                ] if self.alarm_id else [
                    ft.ElevatedButton(
                        text="保存",
                        on_click=self._save_alarm,
                        bgcolor="green",
                        color="white"
                    ),
                    ft.ElevatedButton(
                        text="キャンセル",
                        on_click=self._on_cancel,
                        bgcolor="grey",
                        color="white"
                    )
                ],
                spacing=20
            )
        ])
        
        # スクロール可能なコンテナで包む
        return ft.Column(
            [form_column],
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
    
    def _create_days_row(self) -> ft.Row:
        days = [
            ("monday", "月"),
            ("tuesday", "火"),
            ("wednesday", "水"),
            ("thursday", "木"),
            ("friday", "金"),
            ("saturday", "土"),
            ("sunday", "日")
        ]
        
        checkboxes = []
        for day_key, day_label in days:
            checkbox = ft.Checkbox(
                label=day_label,
                value=True if day_key in ["monday", "tuesday", "wednesday", "thursday", "friday"] else False
            )
            self.days_checkboxes[day_key] = checkbox
            checkboxes.append(checkbox)
        
        return ft.Row(checkboxes, spacing=10)
    
    def _load_alarm_data(self):
        if not self.alarm:
            return
        
        self.time_input.value = self.alarm.time
        self.label_input.value = self.alarm.label
        self.difficulty_dropdown.value = self.alarm.difficulty
        self.problem_sets_dropdown.value = self.alarm.problem_sets[0] if self.alarm.problem_sets else "math"
        self.volume_slider.value = self.alarm.sound.volume
        self.snooze_checkbox.value = self.alarm.snooze.enabled
        self.snooze_duration.value = str(self.alarm.snooze.duration)
        self.snooze_max_count.value = str(self.alarm.snooze.max_count)
        
        for day_key, checkbox in self.days_checkboxes.items():
            checkbox.value = day_key in self.alarm.days
    
    def _save_alarm(self, e):
        selected_days = [
            day_key for day_key, checkbox in self.days_checkboxes.items()
            if checkbox.value
        ]
        
        if not selected_days:
            self._show_error("少なくとも1つの曜日を選択してください")
            return
        
        try:
            sound_config = SoundConfig(
                file="assets/sounds/alarm_default.wav",
                volume=self.volume_slider.value,
                loop=True
            )
            
            snooze_config = SnoozeConfig(
                enabled=self.snooze_checkbox.value,
                duration=int(self.snooze_duration.value),
                max_count=int(self.snooze_max_count.value)
            )
            
            if self.alarm_id:
                alarm = self.alarm
                alarm.time = self.time_input.value
                alarm.label = self.label_input.value
                alarm.days = selected_days
                alarm.difficulty = self.difficulty_dropdown.value
                alarm.problem_sets = [self.problem_sets_dropdown.value]
                alarm.sound = sound_config
                alarm.snooze = snooze_config
            else:
                alarm = Alarm(
                    id=f"alarm_{len(self.alarm_storage.load_alarms()) + 1}",
                    enabled=True,
                    time=self.time_input.value,
                    days=selected_days,
                    label=self.label_input.value,
                    problem_sets=[self.problem_sets_dropdown.value],
                    difficulty=self.difficulty_dropdown.value,
                    sound=sound_config,
                    snooze=snooze_config
                )
            
            self.alarm_storage.save_alarm(alarm)
            
            if self.on_back:
                self.on_back()
                
        except Exception as ex:
            self._show_error(f"保存に失敗しました: {str(ex)}")
    
    def _delete_alarm(self, e):
        if self.alarm_id:
            try:
                self.alarm_storage.delete_alarm(self.alarm_id)
                if self.on_back:
                    self.on_back()
            except Exception as ex:
                self._show_error(f"削除に失敗しました: {str(ex)}")
    
    def _on_cancel(self, e):
        if self.on_back:
            self.on_back()
    
    def _show_error(self, message: str):
        print(f"Error: {message}")
    
    def get_view(self) -> ft.Control:
        return self.build()