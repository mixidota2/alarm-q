from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ProblemType(Enum):
    QUIZ = "quiz"
    GAME = "game"


class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class Problem:
    id: str
    type: ProblemType
    category: str
    title: str
    difficulty: Difficulty
    content: Dict[str, Any]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Problem":
        return cls(
            id=data["id"],
            type=ProblemType(data["type"]),
            category=data["category"],
            title=data["title"],
            difficulty=Difficulty(data["difficulty"]),
            content=data["content"]
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "category": self.category,
            "title": self.title,
            "difficulty": self.difficulty.value,
            "content": self.content
        }


@dataclass
class QuizQuestion:
    type: str
    text: str
    image: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QuizQuestion":
        return cls(
            type=data["type"],
            text=data["text"],
            image=data.get("image")
        )


@dataclass
class QuizOption:
    id: str
    type: str
    content: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QuizOption":
        return cls(
            id=data["id"],
            type=data["type"],
            content=data["content"]
        )


@dataclass
class QuizContent:
    question: QuizQuestion
    options: List[QuizOption]
    correct_answers: List[str]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QuizContent":
        return cls(
            question=QuizQuestion.from_dict(data["question"]),
            options=[QuizOption.from_dict(opt) for opt in data["options"]],
            correct_answers=data["correct_answers"]
        )