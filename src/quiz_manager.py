import random
from typing import List, Optional, Callable
from models.problem import Problem
from models.handlers import ProblemFactory, ProblemHandler
from question_loader import ProblemLoader


class QuizSession:
    def __init__(self, problem_sets: List[str], difficulty: str, problems_dir: str = "problems"):
        self.problem_sets = problem_sets
        self.difficulty = difficulty
        self.problems: List[Problem] = []
        self.current_problem_index = 0
        self.total_attempts = 0
        self.correct_answers = 0
        self.problem_loader = ProblemLoader(problems_dir)
        self.current_handler: Optional[ProblemHandler] = None
        self.on_answer_callback: Optional[Callable] = None
    
    def start_session(self):
        self.problems = self._load_problems()
        self.current_problem_index = 0
        self.total_attempts = 0
        self.correct_answers = 0
        
        if self.problems:
            random.shuffle(self.problems)
    
    def get_current_problem(self) -> Optional[Problem]:
        if not self.problems or self.current_problem_index >= len(self.problems):
            return None
        return self.problems[self.current_problem_index]
    
    def get_current_handler(self) -> Optional[ProblemHandler]:
        current_problem = self.get_current_problem()
        if not current_problem:
            return None
        
        if not self.current_handler:
            self.current_handler = ProblemFactory.create_handler(current_problem.type.value)
            if hasattr(self.current_handler, 'on_answer_submit'):
                self.current_handler.on_answer_submit = self._on_answer_submit
        
        return self.current_handler
    
    def _on_answer_submit(self, selected_options: List[str]):
        if self.on_answer_callback:
            self.on_answer_callback(selected_options)
    
    def submit_answer(self, selected_options: List[str]) -> bool:
        current_problem = self.get_current_problem()
        if not current_problem:
            return False
        
        self.total_attempts += 1
        
        handler = self.get_current_handler()
        if not handler:
            return False
        
        is_correct = handler.check_answer(selected_options)
        
        if is_correct:
            self.correct_answers += 1
            return True
        else:
            self.current_problem_index += 1
            self.current_handler = None
            return False
    
    def is_session_complete(self) -> bool:
        return self.correct_answers > 0
    
    def has_more_problems(self) -> bool:
        return self.current_problem_index < len(self.problems)
    
    def get_session_stats(self) -> dict:
        return {
            "total_attempts": self.total_attempts,
            "correct_answers": self.correct_answers,
            "current_problem": self.current_problem_index + 1,
            "total_problems": len(self.problems),
            "completion_rate": self.correct_answers / max(self.total_attempts, 1)
        }
    
    def _load_problems(self) -> List[Problem]:
        all_problems = []
        
        for problem_set in self.problem_sets:
            problems = self.problem_loader.load_problems_by_difficulty(problem_set, self.difficulty)
            all_problems.extend(problems)
        
        return all_problems