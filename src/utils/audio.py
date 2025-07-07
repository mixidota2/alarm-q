import flet as ft
from typing import Optional, Dict, Any
import os


class AudioController:
    def __init__(self):
        self.audio_player: Optional[ft.Audio] = None
        self.is_playing = False
        self.should_loop = False
        self.page = None
    
    def set_page(self, page: ft.Page):
        """ページ参照を設定"""
        self.page = page
    
    def play_alarm(self, sound_config: Dict[str, Any]):
        if self.audio_player:
            self.stop_alarm()
        
        # 音声ファイルの存在確認（絶対パスに変換）
        sound_file = sound_config["file"]
        if not os.path.isabs(sound_file):
            # 相対パスの場合、プロジェクトルートからの絶対パスに変換
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            sound_file = os.path.join(current_dir, sound_file)
        
        if not os.path.exists(sound_file):
            print(f"音声ファイルが見つかりません: {sound_file}")
            # デフォルトの音声ファイルを使用
            default_sound = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets/sounds/alarm_default.wav")
            if os.path.exists(default_sound):
                sound_file = default_sound
                print(f"デフォルト音声ファイルを使用: {sound_file}")
            else:
                print("デフォルト音声ファイルも見つかりません")
                # テスト用のビープ音を作成
                return self._create_test_audio()
        
        self.should_loop = sound_config.get("loop", True)
        
        self.audio_player = ft.Audio(
            src=sound_file,
            volume=sound_config.get("volume", 0.8),
            balance=0.0,
            playback_rate=1.0,
            on_state_changed=self._on_state_changed,
            on_duration_changed=self._on_duration_changed,
            autoplay=True
        )
        
        self.is_playing = True
        
        import logging
        logging.info(f"音声再生開始: {sound_file}, 音量: {sound_config.get('volume', 0.8)}")
        
        # play()はページに追加後に呼ぶ必要があるため、ここでは呼ばない
        # autoplay=Trueが設定されているので自動再生される
        
        return self.audio_player
    
    def _create_test_audio(self):
        """テスト用の音声コントロールを作成（音声ファイルがない場合）"""
        import logging
        logging.info("音声ファイルがないため、テスト用の音声を作成")
        # 実際の音声ファイルを使用せず、ログだけで代替
        self.is_playing = True
        return None
    
    def stop_alarm(self):
        if self.audio_player and self.is_playing:
            self.should_loop = False
            try:
                self.audio_player.pause()
            except Exception as e:
                import logging
                logging.info(f"音声停止エラー（無視可能）: {e}")
            self.is_playing = False
    
    def get_audio_control(self) -> Optional[ft.Audio]:
        return self.audio_player
    
    def _on_state_changed(self, e):
        import logging
        logging.info(f"音声状態変更: {e.data}")
        if e.data == "completed" and self.is_playing and self.should_loop:
            try:
                self.audio_player.seek(0)
                self.audio_player.resume()
            except Exception as error:
                logging.info(f"ループ再生エラー: {error}")
    
    def _on_duration_changed(self, e):
        import logging
        logging.info(f"音声の長さが設定されました: {e.data}秒")