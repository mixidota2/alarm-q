import json
import os
from typing import List, Optional, Dict, Any
from models.alarm import Alarm


class AlarmStorage:
    def __init__(self, storage_dir: str = "storage"):
        self.storage_dir = storage_dir
        self.alarms_file = os.path.join(storage_dir, "alarms.json")
        self._ensure_storage_dir()
    
    def _ensure_storage_dir(self):
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
    
    def save_alarm(self, alarm: Alarm):
        alarms = self.load_alarms()
        
        existing_index = None
        for i, existing_alarm in enumerate(alarms):
            if existing_alarm.id == alarm.id:
                existing_index = i
                break
        
        if existing_index is not None:
            alarms[existing_index] = alarm
        else:
            alarms.append(alarm)
        
        self._save_alarms(alarms)
    
    def load_alarms(self) -> List[Alarm]:
        if not os.path.exists(self.alarms_file):
            return []
        
        try:
            with open(self.alarms_file, 'r', encoding='utf-8') as f:
                alarms_data = json.load(f)
            
            alarms = []
            for alarm_data in alarms_data:
                try:
                    alarm = Alarm.from_dict(alarm_data)
                    alarms.append(alarm)
                except Exception as e:
                    print(f"アラーム読み込みエラー: {e}")
                    continue
            
            return alarms
            
        except Exception as e:
            print(f"アラームファイル読み込みエラー: {e}")
            return []
    
    def load_alarm(self, alarm_id: str) -> Optional[Alarm]:
        alarms = self.load_alarms()
        for alarm in alarms:
            if alarm.id == alarm_id:
                return alarm
        return None
    
    def delete_alarm(self, alarm_id: str):
        alarms = self.load_alarms()
        alarms = [alarm for alarm in alarms if alarm.id != alarm_id]
        self._save_alarms(alarms)
    
    def _save_alarms(self, alarms: List[Alarm]):
        try:
            alarms_data = [alarm.to_dict() for alarm in alarms]
            with open(self.alarms_file, 'w', encoding='utf-8') as f:
                json.dump(alarms_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"アラーム保存エラー: {e}")


class SettingsStorage:
    def __init__(self, storage_dir: str = "storage"):
        self.storage_dir = storage_dir
        self.settings_file = os.path.join(storage_dir, "settings.json")
        self._ensure_storage_dir()
    
    def _ensure_storage_dir(self):
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
    
    def save_settings(self, settings: Dict[str, Any]):
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"設定保存エラー: {e}")
    
    def load_settings(self) -> Dict[str, Any]:
        if not os.path.exists(self.settings_file):
            return self._get_default_settings()
        
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"設定読み込みエラー: {e}")
            return self._get_default_settings()
    
    def _get_default_settings(self) -> Dict[str, Any]:
        return {
            "theme": "light",
            "default_volume": 0.8,
            "default_snooze_duration": 300,
            "default_snooze_count": 3,
            "screen_brightness": 1.0,
            "problem_sets": ["math", "general"],
            "default_difficulty": "medium"
        }