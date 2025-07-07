# -*- coding: utf-8 -*-
import flet as ft
from typing import List, Optional, Callable
from quiz_manager import QuizSession
from utils.audio import AudioController


class QuizView:
    def __init__(self, problem_sets: List[str], difficulty: str, on_quiz_complete: Optional[Callable] = None):
        self.problem_sets = problem_sets
        self.difficulty = difficulty
        self.on_quiz_complete = on_quiz_complete
        self.quiz_session = QuizSession(problem_sets, difficulty)
        self.audio_controller = AudioController()
        self.page = None
        
        self.quiz_container = ft.Container(
            bgcolor="red50",
            padding=20,
            expand=False  # 自然な高さに変更
        )
        
        self.result_text = ft.Text(
            "",
            size=18,
            weight=ft.FontWeight.BOLD,
            color="red"
        )
        
        self.progress_text = ft.Text(
            "",
            size=16,
            color="bluegrey"
        )
    
    def build(self) -> ft.Control:
        self.quiz_session.on_answer_callback = self._on_answer_submitted
        self.quiz_session.start_session()
        
        title = ft.Text(
            "アラーム問題",
            size=28,
            weight=ft.FontWeight.BOLD,
            color="red900",
            text_align=ft.TextAlign.CENTER
        )
        
        warning_text = ft.Text(
            "正解するまでアラームは停止しません",
            size=16,
            color="red700",
            text_align=ft.TextAlign.CENTER
        )
        
        self._load_current_problem()
        
        main_content = ft.Column([
            ft.Container(
                content=ft.Column([
                    title,
                    warning_text,
                    self.progress_text,
                    self.result_text
                ]),
                padding=20,
                bgcolor="red100"
            ),
            self.quiz_container
        ])
        
        # スクロール可能にする
        return ft.Column(
            [main_content],
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
    
    def _load_current_problem(self):
        current_problem = self.quiz_session.get_current_problem()
        if not current_problem:
            self._show_no_problems()
            return
        
        handler = self.quiz_session.get_current_handler()
        if not handler:
            self._show_error("問題の読み込みに失敗しました")
            return
        
        # handlerにQuizViewの参照を設定（回答ボタンのコールバック用）
        handler.set_quiz_view(self)
        
        problem_control = handler.render(None, current_problem)
        
        self.quiz_container.content = ft.Container(
            content=problem_control,
            padding=20,
            bgcolor="white",
            border_radius=10,
            border=ft.border.all(2, "red200")
        )
        
        self._update_progress()
        
    
    def _on_answer_submitted(self, selected_options: List[str]):
        is_correct = self.quiz_session.submit_answer(selected_options)
        
        if is_correct:
            self._show_correct_answer()
        else:
            self._show_incorrect_answer()
    
    def _show_correct_answer(self):
        self.result_text.value = "正解！アラームを停止します。"
        self.result_text.color = "green"
        
        self.audio_controller.stop_alarm()
        
        
        if self.on_quiz_complete:
            self.on_quiz_complete(True)
    
    def _show_incorrect_answer(self):
        self.result_text.value = "不正解です。次の問題に進みます。"
        self.result_text.color = "red"
        
        if self.page:
            self.page.update()
        
        if self.quiz_session.has_more_problems():
            # asyncioの代わりにTimerを使用
            import threading
            timer = threading.Timer(2.0, self._load_next_problem_delayed_sync)
            timer.start()
        else:
            self._show_no_more_problems()
    
    def _load_next_problem_delayed_sync(self):
        """同期版の遅延問題読み込み"""
        self._load_current_problem()
        self.result_text.value = ""
        if self.page:
            self.page.update()
    
    async def _load_next_problem_delayed(self):
        import asyncio
        await asyncio.sleep(2)
        self._load_current_problem()
        self.result_text.value = ""
    
    def _show_no_problems(self):
        self.quiz_container.content = ft.Container(
            content=ft.Text(
                "問題が見つかりませんでした",
                size=20,
                text_align=ft.TextAlign.CENTER,
                color="red"
            ),
            padding=50,
            alignment=ft.alignment.center
        )
        
    
    def _show_no_more_problems(self):
        self.quiz_container.content = ft.Container(
            content=ft.Column([
                ft.Text(
                    "すべての問題を解きましたが、正解がありませんでした",
                    size=18,
                    text_align=ft.TextAlign.CENTER,
                    color="red"
                ),
                ft.Text(
                    "アラームを停止します",
                    size=16,
                    text_align=ft.TextAlign.CENTER,
                    color="bluegrey"
                )
            ]),
            padding=50,
            alignment=ft.alignment.center
        )
        
        self.audio_controller.stop_alarm()
        
        
        if self.on_quiz_complete:
            self.on_quiz_complete(False)
    
    def _show_error(self, message: str):
        self.quiz_container.content = ft.Container(
            content=ft.Text(
                message,
                size=20,
                text_align=ft.TextAlign.CENTER,
                color="red"
            ),
            padding=50,
            alignment=ft.alignment.center
        )
        
    
    def _update_progress(self):
        stats = self.quiz_session.get_session_stats()
        self.progress_text.value = f"問題 {stats['current_problem']}/{stats['total_problems']} - 試行回数: {stats['total_attempts']}"
        
    
    def start_alarm_sound(self, sound_config):
        # AudioControllerにページ参照を設定
        if self.page:
            self.audio_controller.set_page(self.page)
        audio_control = self.audio_controller.play_alarm(sound_config.to_dict())
        return audio_control
    
    def set_page(self, page):
        """ページ参照を設定"""
        self.page = page
    
    def update_view(self):
        """UI更新用メソッド"""
        if self.page:
            self.page.update()
    
    def get_view(self) -> ft.Control:
        return self.build()