import flet as ft
from typing import Optional, Dict, Any
import os
from .system_audio import SystemAudioController


class AudioController:
    def __init__(self):
        self.is_playing = False
        self.should_loop = False
        self.page = None
        self.system_audio = SystemAudioController()  # システムオーディオを使用
    
    def set_page(self, page: ft.Page):
        """ページ参照を設定"""
        self.page = page
    
    def play_alarm(self, sound_config: Dict[str, Any]):
        if self.is_playing:
            self.stop_alarm()
        
        # システムオーディオで音声再生
        try:
            success = self.system_audio.play_alarm(sound_config)
            if success:
                self.is_playing = True
                self.should_loop = sound_config.get("loop", True)
                
                import logging
                logging.info(f"システムオーディオで音声再生開始: {sound_config['file']}")
                
                # unknown control audio表示を避けるため、Noneを返す
                return None
            else:
                import logging
                logging.error("システムオーディオでの音声再生に失敗")
                return None
        except Exception as e:
            import logging
            logging.error(f"システムオーディオエラー: {e}")
            return None
    
    def stop_alarm(self):
        """アラーム音声を停止"""
        if self.is_playing:
            try:
                self.system_audio.stop_alarm()
                self.is_playing = False
                
                import logging
                logging.info("システムオーディオでアラーム音声停止")
            except Exception as e:
                import logging
                logging.error(f"システムオーディオ停止エラー: {e}")
    
    def _create_test_audio(self):
        """テスト用の音声コントロールを作成（音声ファイルがない場合）"""
        import logging
        logging.info("音声ファイルがないため、テスト用の音声を作成")
        # 実際の音声ファイルを使用せず、ログだけで代替
        self.is_playing = True
        return None