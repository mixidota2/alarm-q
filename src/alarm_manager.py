import threading
import time
import logging
from datetime import datetime
from typing import List, Optional, Callable
from models.alarm import Alarm
from utils.storage import AlarmStorage
from utils.audio import AudioController

# ログ設定
logging.basicConfig(
    filename='alarm_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(message)s'
)


class AlarmScheduler:
    def __init__(self, on_alarm_trigger: Optional[Callable] = None):
        self.alarms: List[Alarm] = []
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.check_interval = 10  # 10秒ごとにチェック（デバッグ用）
        self.alarm_storage = AlarmStorage()
        self.audio_controller = AudioController()
        self.on_alarm_trigger = on_alarm_trigger
        self.triggered_alarms: set[str] = set()
    
    def start(self):
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        logging.info("アラーム監視を開始しました")
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        logging.info("アラーム監視を停止しました")
    
    def reload_alarms(self):
        self.alarms = self.alarm_storage.load_alarms()
        logging.info(f"アラーム設定を再読み込みしました: {len(self.alarms)}件")
    
    def _monitor_loop(self):
        while self.running:
            try:
                now = datetime.now()
                logging.debug(f"アラーム監視チェック: {now.strftime('%H:%M:%S')}")
                self.reload_alarms()
                
                for alarm in self.alarms:
                    logging.debug(f"アラーム {alarm.id}: enabled={alarm.enabled}, time={alarm.time}, should_trigger={alarm.should_trigger(now)}")
                    if alarm.should_trigger(now):
                        alarm_key = f"{alarm.id}_{now.strftime('%Y%m%d')}"
                        
                        if alarm_key not in self.triggered_alarms:
                            self.triggered_alarms.add(alarm_key)
                            self._trigger_alarm(alarm)
                
                self._cleanup_old_triggered_alarms()
                
            except Exception as e:
                logging.error(f"アラーム監視エラー: {e}")
            
            time.sleep(self.check_interval)
    
    def _trigger_alarm(self, alarm: Alarm):
        alarm.last_triggered = datetime.now()
        self.alarm_storage.save_alarm(alarm)
        
        logging.info(f"アラーム発火: {alarm.label} ({alarm.time})")
        logging.info(f"  問題セット: {alarm.problem_sets}")
        logging.info(f"  難易度: {alarm.difficulty}")
        
        if self.on_alarm_trigger:
            self.on_alarm_trigger(alarm)
    
    def _cleanup_old_triggered_alarms(self):
        current_date = datetime.now().strftime('%Y%m%d')
        self.triggered_alarms = {
            key for key in self.triggered_alarms 
            if key.endswith(current_date)
        }


class AlarmManager:
    def __init__(self, on_alarm_trigger: Optional[Callable] = None):
        self.scheduler = AlarmScheduler(on_alarm_trigger)
        self.audio_controller = AudioController()
        self.current_alarm: Optional[Alarm] = None
        self.is_alarm_active = False
    
    def start(self):
        self.scheduler.start()
    
    def stop(self):
        self.scheduler.stop()
        self.stop_current_alarm()
    
    def trigger_alarm(self, alarm: Alarm):
        if self.is_alarm_active:
            return
        
        self.current_alarm = alarm
        self.is_alarm_active = True
        
        logging.info(f"アラーム開始: {alarm.label}")
        
        self.audio_controller.play_alarm(alarm.sound.to_dict())
        
        if self.scheduler.on_alarm_trigger:
            self.scheduler.on_alarm_trigger(alarm)
    
    def stop_current_alarm(self):
        if not self.is_alarm_active:
            return
        
        logging.info("アラーム停止")
        
        self.audio_controller.stop_alarm()
        self.current_alarm = None
        self.is_alarm_active = False
    
    def snooze_current_alarm(self):
        if not self.is_alarm_active or not self.current_alarm:
            return
        
        if not self.current_alarm.snooze.enabled:
            return
        
        logging.info(f"スヌーズ: {self.current_alarm.snooze.duration}秒")
        
        self.audio_controller.stop_alarm()
        
        snooze_thread = threading.Thread(
            target=self._snooze_timer,
            args=(self.current_alarm.snooze.duration,),
            daemon=True
        )
        snooze_thread.start()
    
    def _snooze_timer(self, duration: int):
        time.sleep(duration)
        
        if self.is_alarm_active and self.current_alarm:
            self.audio_controller.play_alarm(self.current_alarm.sound.to_dict())
    
    def get_current_alarm(self) -> Optional[Alarm]:
        return self.current_alarm
    
    def is_active(self) -> bool:
        return self.is_alarm_active