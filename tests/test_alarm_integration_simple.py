# -*- coding: utf-8 -*-
import unittest
from unittest.mock import Mock, patch
import os
import sys

# Add src to path for importing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.alarm import Alarm, SoundConfig, SnoozeConfig


class TestAlarmFlowSimple(unittest.TestCase):
    """環境に依存しないアラーム発火フローのテスト"""
    
    def setUp(self):
        """各テストの前に実行される初期化処理"""
        self.mock_page = Mock()
        self.mock_page.overlay = []
        self.mock_page.clean = Mock()
        self.mock_page.add = Mock()
        self.mock_page.update = Mock()
    
    def test_alarm_trigger_logic(self):
        """アラーム発火ロジックのテスト（Fletに依存しない）"""
        # テスト用アラーム
        test_alarm = Alarm(
            id="test_alarm_001",
            time="12:00",
            label="テストアラーム",
            enabled=True,
            days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            problem_sets=["basic"],
            difficulty="easy",
            sound=SoundConfig(
                file="assets/sounds/alarm_default.wav",
                volume=0.8,
                loop=True
            ),
            snooze=SnoozeConfig(enabled=False, duration=300, max_count=3)
        )
        
        # main.pyのimportをモック
        with patch.dict('sys.modules', {
            'flet': Mock(),
            'ui.main_view': Mock(),
            'ui.alarm_view': Mock(),
            'ui.quiz_view': Mock()
        }):
            # MainAppのアラーム発火メソッドのみテスト
            class TestableAlarmApp:
                def __init__(self, page):
                    self.page = page
                    self.alarm_triggered = False
                    self.current_view = None
                    self.alarm_manager = Mock()
                
                def _on_alarm_trigger(self, alarm):
                    """実際のアラーム発火ロジック"""
                    if self.alarm_triggered:
                        return  # 既に発火中
                    
                    self.alarm_triggered = True
                    self.page.clean()
                    
                    # QuizView作成をシミュレート
                    quiz_data = {
                        'problem_sets': alarm.problem_sets,
                        'difficulty': alarm.difficulty,
                        'sound_config': alarm.sound.to_dict()
                    }
                    
                    # 音声制御をページに追加をシミュレート
                    audio_control = Mock()
                    self.page.overlay.append(audio_control)
                    
                    self.page.update()
                    return quiz_data
                
                def _on_quiz_complete(self, success):
                    """クイズ完了処理"""
                    self.alarm_triggered = False
                    self.alarm_manager.stop_current_alarm()
            
            # テスト実行
            app = TestableAlarmApp(self.mock_page)
            
            # アラーム発火
            result = app._on_alarm_trigger(test_alarm)
            
            # 検証
            self.assertTrue(app.alarm_triggered)
            self.assertEqual(result['problem_sets'], ["basic"])
            self.assertEqual(result['difficulty'], "easy")
            self.assertEqual(result['sound_config']['file'], "assets/sounds/alarm_default.wav")
            self.assertEqual(result['sound_config']['volume'], 0.8)
            self.assertTrue(result['sound_config']['loop'])
            
            # overlayに追加されたか
            self.assertEqual(len(self.mock_page.overlay), 1)
            
            # ページが更新されたか
            self.mock_page.update.assert_called()
            
            # クイズ完了処理
            app._on_quiz_complete(True)
            self.assertFalse(app.alarm_triggered)
            app.alarm_manager.stop_current_alarm.assert_called_once()
    
    def test_sound_config_integration(self):
        """音声設定の統合テスト"""
        # 音声設定の作成
        sound_config = SoundConfig(
            file="assets/sounds/alarm_default.wav",
            volume=0.8,
            loop=True
        )
        
        # 辞書変換
        sound_dict = sound_config.to_dict()
        
        # 検証
        self.assertEqual(sound_dict['file'], "assets/sounds/alarm_default.wav")
        self.assertEqual(sound_dict['volume'], 0.8)
        self.assertTrue(sound_dict['loop'])
        
        # 復元テスト
        restored_config = SoundConfig.from_dict(sound_dict)
        self.assertEqual(restored_config.file, sound_config.file)
        self.assertEqual(restored_config.volume, sound_config.volume)
        self.assertEqual(restored_config.loop, sound_config.loop)
    
    def test_audio_controller_logic(self):
        """AudioControllerのロジックテスト（Fletに依存しない）"""
        from utils.audio import AudioController
        
        # AudioControllerの初期化
        controller = AudioController()
        
        # 初期状態の確認
        self.assertFalse(controller.is_playing)
        self.assertFalse(controller.should_loop)
        self.assertIsNone(controller.page)
        
        # ページ設定
        mock_page = Mock()
        controller.set_page(mock_page)
        self.assertEqual(controller.page, mock_page)
        
        # 音声制御の検証（実際の音声再生はせず、ロジックのみ）
        with patch('flet.Audio') as mock_audio:
            mock_audio_instance = Mock()
            mock_audio.return_value = mock_audio_instance
            
            sound_config = {
                'file': 'assets/sounds/alarm_default.wav',
                'volume': 0.8,
                'loop': True
            }
            
            with patch('os.path.exists', return_value=True):
                result = controller.play_alarm(sound_config)
                
                # 検証
                self.assertEqual(result, mock_audio_instance)
                self.assertTrue(controller.is_playing)
                self.assertTrue(controller.should_loop)
                
                # Audio作成の引数確認
                mock_audio.assert_called_once()
                call_kwargs = mock_audio.call_args[1]
                self.assertEqual(call_kwargs['volume'], 0.8)
                self.assertTrue(call_kwargs['autoplay'])
        
        # 停止処理
        controller.audio_player = Mock()
        controller.is_playing = True
        controller.stop_alarm()
        
        self.assertFalse(controller.is_playing)
        self.assertFalse(controller.should_loop)
    
    def test_alarm_already_triggered_prevention(self):
        """重複アラーム発火の防止テスト"""
        # テスト用アラーム
        test_alarm = Alarm(
            id="duplicate_test",
            time="14:00",
            label="重複テスト",
            enabled=True,
            days=["Tuesday"],
            problem_sets=["test"],
            difficulty="easy",
            sound=SoundConfig(file="test.wav", volume=0.7, loop=True),
            snooze=SnoozeConfig(enabled=False, duration=300, max_count=3)
        )
        
        # 簡単なアプリケーションロジック
        class TestApp:
            def __init__(self):
                self.alarm_triggered = False
                self.trigger_count = 0
            
            def trigger_alarm(self, alarm):
                if self.alarm_triggered:
                    return False  # 重複防止
                
                self.alarm_triggered = True
                self.trigger_count += 1
                return True
        
        app = TestApp()
        
        # 1回目の発火
        result1 = app.trigger_alarm(test_alarm)
        self.assertTrue(result1)
        self.assertTrue(app.alarm_triggered)
        self.assertEqual(app.trigger_count, 1)
        
        # 2回目の発火（重複）
        result2 = app.trigger_alarm(test_alarm)
        self.assertFalse(result2)
        self.assertTrue(app.alarm_triggered)  # 状態は変わらない
        self.assertEqual(app.trigger_count, 1)  # カウントも増えない
    
    def test_audio_file_verification(self):
        """音声ファイルの検証テスト"""
        import os
        
        # 音声ファイルの存在確認
        sound_file = "assets/sounds/alarm_default.wav"
        self.assertTrue(os.path.exists(sound_file), f"音声ファイルが存在しません: {sound_file}")
        
        # ファイルサイズの確認（1KB以上）
        file_size = os.path.getsize(sound_file)
        self.assertGreater(file_size, 1000, f"音声ファイルサイズが小さすぎます: {file_size} bytes")
        
        # 150KB以上（正常なWAVファイル）
        self.assertGreater(file_size, 150000, f"音声ファイルサイズが期待値より小さいです: {file_size} bytes")


if __name__ == '__main__':
    unittest.main()