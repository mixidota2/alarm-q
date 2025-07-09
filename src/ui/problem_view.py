# -*- coding: utf-8 -*-
import flet as ft
from typing import Optional, Callable, List, Dict
import json
import os
from question_loader import ProblemLoader


class ProblemView:
    def __init__(self, on_back: Optional[Callable] = None):
        self.on_back = on_back
        self.problem_loader = ProblemLoader()
        self.available_sets = self.problem_loader.get_available_problem_sets()
        self.selected_set = None
        
        self.problem_set_dropdown = ft.Dropdown(
            label="問題セット",
            width=200,
            options=[
                ft.dropdown.Option(set_name, set_name.capitalize()) 
                for set_name in self.available_sets
            ],
            on_change=self._on_set_change
        )
        
        self.problems_list = ft.Column(spacing=10)
        self.problem_count_text = ft.Text("", size=16)
        
    def build(self) -> ft.Control:
        header = ft.Row([
            ft.IconButton(
                icon="arrow_back",
                tooltip="戻る",
                on_click=self._on_back_click
            ),
            ft.Text(
                "問題管理",
                size=24,
                weight=ft.FontWeight.BOLD
            )
        ])
        
        controls_row = ft.Row([
            self.problem_set_dropdown,
            ft.ElevatedButton(
                text="新しい問題を追加",
                on_click=self._add_problem,
                bgcolor="green",
                color="white"
            ),
            ft.ElevatedButton(
                text="問題セットを作成",
                on_click=self._create_problem_set,
                bgcolor="blue",
                color="white"
            )
        ], spacing=10)
        
        main_content = ft.Column([
            header,
            ft.Divider(),
            controls_row,
            self.problem_count_text,
            ft.Divider(),
            ft.Container(
                content=self.problems_list,
                expand=True
            )
        ])
        
        return ft.Column(
            [main_content],
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
    
    def _on_set_change(self, e):
        self.selected_set = e.control.value
        self._load_problems()
    
    def _load_problems(self):
        if not self.selected_set:
            return
            
        problems = self.problem_loader.load_problem_set(self.selected_set)
        self.problem_count_text.value = f"問題数: {len(problems)}問"
        
        self.problems_list.controls.clear()
        
        for i, problem in enumerate(problems):
            problem_item = self._create_problem_item(problem, i)
            self.problems_list.controls.append(problem_item)
    
    def _create_problem_item(self, problem, index: int) -> ft.Control:
        difficulty_colors = {
            "easy": "green",
            "medium": "orange", 
            "hard": "red"
        }
        
        difficulty_chip = ft.Chip(
            label=ft.Text(problem.difficulty.value),
            bgcolor=difficulty_colors.get(problem.difficulty.value, "grey")
        )
        
        content = ft.Column([
            ft.Row([
                ft.Text(f"{index + 1}. {problem.title}", size=16, weight=ft.FontWeight.BOLD),
                difficulty_chip
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text(
                problem.content.get("question", {}).get("text", "")[:100] + "...",
                size=12,
                color="grey700"
            ),
            ft.Row([
                ft.ElevatedButton(
                    text="編集",
                    on_click=lambda e, p=problem: self._edit_problem(p),
                    bgcolor="blue",
                    color="white",
                    width=100
                ),
                ft.ElevatedButton(
                    text="削除",
                    on_click=lambda e, p=problem: self._delete_problem(p),
                    bgcolor="red",
                    color="white",
                    width=100
                )
            ], spacing=10)
        ], spacing=5)
        
        return ft.Card(
            content=ft.Container(
                content=content,
                padding=15
            ),
            margin=ft.margin.only(bottom=10)
        )
    
    def _add_problem(self, e):
        if not self.selected_set:
            self._show_message("問題セットを選択してください")
            return
        # TODO: 問題追加ダイアログを表示
        self._show_message("問題追加機能は実装中です")
    
    def _create_problem_set(self, e):
        # TODO: 問題セット作成ダイアログを表示
        self._show_message("問題セット作成機能は実装中です")
    
    def _edit_problem(self, problem):
        # TODO: 問題編集ダイアログを表示
        self._show_message(f"問題「{problem.title}」の編集機能は実装中です")
    
    def _delete_problem(self, problem):
        # TODO: 削除確認ダイアログを表示
        self._show_message(f"問題「{problem.title}」の削除機能は実装中です")
    
    def _on_back_click(self, e):
        if self.on_back:
            self.on_back()
    
    def _show_message(self, message: str):
        print(f"Message: {message}")
    
    def get_view(self) -> ft.Control:
        return self.build()