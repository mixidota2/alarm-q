from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class DayOfWeek(Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


@dataclass
class SoundConfig:
    file: str
    volume: float
    loop: bool
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SoundConfig":
        return cls(
            file=data["file"],
            volume=data["volume"],
            loop=data["loop"]
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file": self.file,
            "volume": self.volume,
            "loop": self.loop
        }


@dataclass
class SnoozeConfig:
    enabled: bool
    duration: int
    max_count: int
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SnoozeConfig":
        return cls(
            enabled=data["enabled"],
            duration=data["duration"],
            max_count=data["max_count"]
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "duration": self.duration,
            "max_count": self.max_count
        }


@dataclass
class Alarm:
    id: str
    enabled: bool
    time: str
    days: List[str]
    label: str
    problem_sets: List[str]
    difficulty: str
    sound: SoundConfig
    snooze: SnoozeConfig
    last_triggered: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Alarm":
        return cls(
            id=data["id"],
            enabled=data["enabled"],
            time=data["time"],
            days=data["days"],
            label=data["label"],
            problem_sets=data["problem_sets"],
            difficulty=data["difficulty"],
            sound=SoundConfig.from_dict(data["sound"]),
            snooze=SnoozeConfig.from_dict(data["snooze"]),
            last_triggered=None
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "enabled": self.enabled,
            "time": self.time,
            "days": self.days,
            "label": self.label,
            "problem_sets": self.problem_sets,
            "difficulty": self.difficulty,
            "sound": self.sound.to_dict(),
            "snooze": self.snooze.to_dict()
        }
    
    def should_trigger(self, now: datetime) -> bool:
        if not self.enabled:
            return False
        
        # 曜日を英語形式で統一
        weekday_map = {
            0: "monday", 1: "tuesday", 2: "wednesday", 3: "thursday",
            4: "friday", 5: "saturday", 6: "sunday"
        }
        weekday = weekday_map[now.weekday()]
        if weekday not in self.days:
            return False
        
        alarm_time = datetime.strptime(self.time, "%H:%M").time()
        target_datetime = datetime.combine(now.date(), alarm_time)
        diff = abs((now - target_datetime).total_seconds())
        
        if self.last_triggered:
            same_day = self.last_triggered.date() == now.date()
            same_alarm = abs((self.last_triggered - target_datetime).total_seconds()) < 60
            if same_day and same_alarm:
                return False
        
        return diff <= 30