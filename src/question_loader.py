import json
import os
from typing import List, Dict, Any
from models.problem import Problem


class ProblemLoader:
    def __init__(self, problems_dir: str = "problems"):
        self.problems_dir = problems_dir
        self.cache: Dict[str, List[Problem]] = {}
    
    def load_problem_set(self, set_name: str) -> List[Problem]:
        if set_name in self.cache:
            return self.cache[set_name]
        
        set_path = os.path.join(self.problems_dir, "quiz", f"{set_name}.json")
        
        try:
            with open(set_path, 'r', encoding='utf-8') as f:
                problems_data = json.load(f)
            
            problems = []
            for problem_data in problems_data:
                if self._validate_problem(problem_data):
                    problem = Problem.from_dict(problem_data)
                    problems.append(problem)
            
            self.cache[set_name] = problems
            return problems
            
        except Exception as e:
            print(f"問題セット読み込みエラー: {e}")
            return []
    
    def load_problems_by_difficulty(self, set_name: str, difficulty: str) -> List[Problem]:
        all_problems = self.load_problem_set(set_name)
        return [p for p in all_problems if p.difficulty.value == difficulty]
    
    def get_available_problem_sets(self) -> List[str]:
        quiz_dir = os.path.join(self.problems_dir, "quiz")
        if not os.path.exists(quiz_dir):
            return []
        
        problem_sets = []
        for filename in os.listdir(quiz_dir):
            if filename.endswith('.json'):
                problem_sets.append(filename[:-5])
        
        return problem_sets
    
    def _validate_problem(self, problem: Dict[str, Any]) -> bool:
        required_fields = ["id", "type", "category", "title", "difficulty", "content"]
        if not all(field in problem for field in required_fields):
            return False
        
        if problem["type"] == "quiz":
            return self._validate_quiz_content(problem["content"])
        
        return True
    
    def _validate_quiz_content(self, content: Dict[str, Any]) -> bool:
        required_fields = ["question", "options", "correct_answers"]
        if not all(field in content for field in required_fields):
            return False
        
        question = content["question"]
        if not isinstance(question, dict) or "text" not in question:
            return False
        
        options = content["options"]
        if not isinstance(options, list) or len(options) == 0:
            return False
        
        for option in options:
            if not isinstance(option, dict) or "id" not in option or "content" not in option:
                return False
        
        correct_answers = content["correct_answers"]
        if not isinstance(correct_answers, list) or len(correct_answers) == 0:
            return False
        
        option_ids = {opt["id"] for opt in options}
        if not all(ans in option_ids for ans in correct_answers):
            return False
        
        return True


class QuestionLoader(ProblemLoader):
    """ProblemLoaderの別名として使用"""
    
    def load_problems(self, set_name: str, difficulty: str) -> List[Problem]:
        """指定されたセットと難易度の問題を読み込み"""
        return self.load_problems_by_difficulty(set_name, difficulty)