from abc import ABC, abstractmethod
from typing import Any, List
import flet as ft
from .problem import Problem, QuizContent


class ProblemHandler(ABC):
    @abstractmethod
    def render(self, page: ft.Page, problem: Problem) -> ft.Control:
        pass
    
    @abstractmethod
    def check_answer(self, user_input: Any) -> bool:
        pass
    
    @abstractmethod
    def get_progress(self) -> float:
        pass


class QuizHandler(ProblemHandler):
    def __init__(self):
        self.selected_options: List[str] = []
        self.problem: Problem = None
        self.quiz_content: QuizContent = None
        self.quiz_view = None
    
    def render(self, page: ft.Page, problem: Problem) -> ft.Control:
        self.problem = problem
        self.quiz_content = QuizContent.from_dict(problem.content)
        self.selected_options = []
        
        question_text = ft.Text(
            self.quiz_content.question.text,
            size=20,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        )
        
        if self.quiz_content.question.image:
            question_image = ft.Image(
                src=self.quiz_content.question.image,
                width=400,
                height=300,
                fit=ft.ImageFit.CONTAIN
            )
            question_content = ft.Column([question_text, question_image])
        else:
            question_content = question_text
        
        option_controls = []
        for option in self.quiz_content.options:
            checkbox = ft.Checkbox(
                label=option.content,
                value=False,
                data=option.id,
                on_change=self._on_option_change
            )
            option_controls.append(checkbox)
        
        options_container = ft.Container(
            content=ft.Column(option_controls),
            padding=20
        )
        
        submit_button = ft.ElevatedButton(
            text="回答",
            on_click=self._on_submit,
            width=200,
            height=50,
            bgcolor="green",
            color="white"
        )
        
        return ft.Column([
            ft.Container(
                content=question_content,
                padding=20,
                alignment=ft.alignment.center
            ),
            ft.Divider(),
            options_container,
            ft.Container(
                content=submit_button,
                alignment=ft.alignment.center,
                padding=20
            )
        ])
    
    def _on_option_change(self, e):
        option_id = e.control.data
        if e.control.value:
            if option_id not in self.selected_options:
                self.selected_options.append(option_id)
        else:
            if option_id in self.selected_options:
                self.selected_options.remove(option_id)
    
    def _on_submit(self, e):
        if self.quiz_view and hasattr(self.quiz_view, '_on_answer_submitted'):
            self.quiz_view._on_answer_submitted(self.selected_options)
    
    def set_quiz_view(self, quiz_view):
        """QuizViewの参照を設定"""
        self.quiz_view = quiz_view
    
    def check_answer(self, selected_options: List[str]) -> bool:
        if not self.quiz_content:
            return False
        
        correct_set = set(self.quiz_content.correct_answers)
        selected_set = set(selected_options)
        return correct_set == selected_set
    
    def get_progress(self) -> float:
        if not self.quiz_content:
            return 0.0
        
        total_options = len(self.quiz_content.options)
        selected_count = len(self.selected_options)
        return min(selected_count / total_options, 1.0)


class ProblemFactory:
    handlers = {
        "quiz": QuizHandler,
    }
    
    @classmethod
    def create_handler(cls, problem_type: str) -> ProblemHandler:
        handler_class = cls.handlers.get(problem_type)
        if not handler_class:
            raise ValueError(f"Unsupported problem type: {problem_type}")
        return handler_class()