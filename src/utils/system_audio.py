import os
import subprocess
import threading
import platform
from typing import Optional, Dict, Any


class SystemAudioController:
    """システムコマンドを使用した音声制御"""
    
    def __init__(self):
        self.current_process: Optional[subprocess.Popen] = None
        self.is_playing = False
        self.should_loop = False
        self.loop_thread: Optional[threading.Thread] = None
    
    def play_alarm(self, sound_config: Dict[str, Any]):
        """アラーム音声を再生"""
        if self.is_playing:
            self.stop_alarm()
        
        sound_file = sound_config["file"]
        if not os.path.exists(sound_file):
            print(f"音声ファイルが見つかりません: {sound_file}")
            sound_file = "assets/sounds/alarm_default.wav"
            if not os.path.exists(sound_file):
                print("デフォルト音声ファイルも見つかりません")
                return None
        
        self.should_loop = sound_config.get("loop", True)
        self.is_playing = True
        
        # ループ再生を別スレッドで実行
        self.loop_thread = threading.Thread(
            target=self._play_loop,
            args=(sound_file, sound_config.get("volume", 0.8)),
            daemon=True
        )
        self.loop_thread.start()
        
        return True
    
    def _play_loop(self, sound_file: str, volume: float):
        """ループ再生処理"""
        while self.is_playing and self.should_loop:
            try:
                # プラットフォームに応じたコマンドを使用
                system = platform.system()
                
                if system == "Linux":
                    # aplayコマンドを試す（Raspberry Pi標準）
                    cmd = ["aplay", "-q", sound_file]
                    try:
                        self.current_process = subprocess.Popen(
                            cmd,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        self.current_process.wait()
                    except FileNotFoundError:
                        # aplayがない場合はpaplayを試す
                        cmd = ["paplay", sound_file]
                        self.current_process = subprocess.Popen(
                            cmd,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        self.current_process.wait()
                
                elif system == "Darwin":  # macOS
                    cmd = ["afplay", sound_file]
                    self.current_process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    self.current_process.wait()
                
                elif system == "Windows":
                    # Windows Media Player
                    cmd = ["powershell", "-c", f"(New-Object Media.SoundPlayer '{sound_file}').PlaySync()"]
                    self.current_process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    self.current_process.wait()
                
            except Exception as e:
                print(f"音声再生エラー: {e}")
                break
        
        self.is_playing = False
    
    def stop_alarm(self):
        """アラーム音声を停止"""
        self.should_loop = False
        self.is_playing = False
        
        if self.current_process:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=1)
            except:
                try:
                    self.current_process.kill()
                except:
                    pass
            self.current_process = None
    
    def get_audio_control(self):
        """互換性のためのメソッド"""
        return None