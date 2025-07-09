# -*- coding: utf-8 -*-
import flet as ft
from typing import Optional
from ui.main_view import MainView
from ui.alarm_view import AlarmView
from ui.quiz_view import QuizView
from alarm_manager import AlarmManager
from models.alarm import Alarm


class AlarmApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.alarm_manager = AlarmManager(on_alarm_trigger=self._on_alarm_trigger)
        self.current_view: Optional[ft.Control] = None
        self.alarm_triggered = False
        
        self.page.title = "alearm-q"
        self.page.window_width = 800
        self.page.window_height = 600
        self.page.window_resizable = False
        
        # 日本語フォント設定
        import os
        font_paths = [
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/System/Library/Fonts/Helvetica.ttc"
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                self.page.fonts = {"JapaneseFont": font_path}
                self.page.theme = ft.Theme(font_family="JapaneseFont")
                break
        
        self.main_view = MainView(
            on_alarm_settings=self._show_alarm_settings,
            on_show_message=self._show_message
        )
        self._show_main_view()
        
        self.alarm_manager.start()
    
    def _show_main_view(self):
        self.page.clean()
        self.current_view = self.main_view.get_view()
        self.page.add(self.current_view)
        self.page.update()
    
    def _show_alarm_settings(self, alarm_id: Optional[str] = None):
        self.page.clean()
        alarm_view = AlarmView(
            on_back=self._show_main_view,
            alarm_id=alarm_id
        )
        self.current_view = alarm_view.get_view()
        self.page.add(self.current_view)
        self.page.update()
    
    def _on_alarm_trigger(self, alarm: Alarm):
        import logging
        logging.info(f"[MainApp] アラーム発火処理開始: {alarm.label}")
        
        if self.alarm_triggered:
            logging.info("[MainApp] 既にアラーム発火中のためスキップ")
            return
        
        self.alarm_triggered = True
        self.page.clean()
        
        logging.info(f"[MainApp] QuizView作成 - 問題セット: {alarm.problem_sets}, 難易度: {alarm.difficulty}")
        
        quiz_view = QuizView(
            problem_sets=alarm.problem_sets,
            difficulty=alarm.difficulty,
            on_quiz_complete=self._on_quiz_complete
        )
        
        # ページ参照を設定
        quiz_view.set_page(self.page)
        
        # システムオーディオで音声再生を開始
        quiz_view.start_alarm_sound(alarm.sound)
        logging.info("システムオーディオでアラーム音声再生を開始")
        
        self.current_view = quiz_view.get_view()
        self.page.add(self.current_view)
        self.page.update()
        
        logging.info("[MainApp] アラーム発火処理完了")
    
    def _on_quiz_complete(self, success: bool):
        self.alarm_triggered = False
        self.alarm_manager.stop_current_alarm()
        
        if success:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("正解！アラームを停止しました。"),
                bgcolor=ft.Colors.GREEN
            )
        else:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("すべての問題が終了しました。"),
                bgcolor=ft.Colors.BLUE
            )
        
        self.page.snack_bar.open = True
        self._show_main_view()
    
    def _show_message(self, message: str):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor="blue"
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def cleanup(self):
        self.alarm_manager.stop()


def main(page: ft.Page):
    app = AlarmApp(page)
    
    def on_window_event(e):
        if e.data == "close":
            app.cleanup()
    
    page.on_window_event = on_window_event


ft.app(main)
