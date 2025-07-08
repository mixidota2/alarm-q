# -*- coding: utf-8 -*-
import unittest
from unittest.mock import Mock, patch
import os
import sys
import time
from datetime import datetime

# Add src to path for importing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from alarm_manager import AlarmScheduler
from models.alarm import Alarm, SoundConfig, SnoozeConfig

# Fletが利用できない場合のための代替モック
try:
    import flet as ft
except ImportError:
    # Fletのモッククラスを作成
    class FletMock:
        class Page:
            pass
    ft = FletMock()

# 統合テスト用の簡単なアプリケーションモック
class TestAlarmApp:
    def __init__(self, page):
        self.page = page
        self.alarm_triggered = False
        self.alarm_manager = Mock()
    
    def _on_alarm_trigger(self, alarm):
        self.alarm_triggered = True
    
    def _on_quiz_complete(self, success):
        self.alarm_triggered = False


class TestAlarmIntegration(unittest.TestCase):
    def setUp(self):
        """各テストの前に実行される初期化処理"""
        self.mock_page = Mock(spec=ft.Page)
        self.mock_page.overlay = []
        self.mock_page.clean = Mock()
        self.mock_page.add = Mock()
        self.mock_page.update = Mock()
        
        # アラーム発火トリガーのモック
        self.alarm_triggered = False
        self.triggered_alarm = None
        
    def test_alarm_trigger_to_quiz_flow(self):
        """アラーム発火からクイズ画面遷移までの統合テスト"""
        # テスト用アラームを作成
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
        
        # AlarmAppのモック作成
        alarm_app = TestAlarmApp(self.mock_page)
        
        # アラーム発火をシミュレート
        with patch.object(alarm_app, '_show_main_view'):
            with patch('src.ui.quiz_view.QuizView') as mock_quiz_view_class:
                mock_quiz_view = Mock()
                mock_quiz_view.set_page = Mock()
                mock_quiz_view.start_alarm_sound = Mock(return_value=Mock())
                mock_quiz_view.get_view = Mock(return_value=Mock())
                mock_quiz_view_class.return_value = mock_quiz_view
                
                # アラーム発火をトリガー
                alarm_app._on_alarm_trigger(test_alarm)
                
                # 検証: クイズ画面が作成されたか
                mock_quiz_view_class.assert_called_once_with(
                    problem_sets=["basic"],
                    difficulty="easy",
                    on_quiz_complete=alarm_app._on_quiz_complete
                )
                
                # 検証: ページ参照が設定されたか
                mock_quiz_view.set_page.assert_called_once_with(self.mock_page)
                
                # 検証: 音声が開始されたか
                mock_quiz_view.start_alarm_sound.assert_called_once_with(test_alarm.sound)
                
                # 検証: overlayに音声コントロールが追加されたか
                self.assertEqual(len(self.mock_page.overlay), 1)
                
                # 検証: ページが更新されたか
                self.mock_page.update.assert_called()
                
                # 検証: アラーム状態が正しく設定されたか
                self.assertTrue(alarm_app.alarm_triggered)
    
    @patch('src.utils.storage.AlarmStorage')
    def test_alarm_scheduler_integration(self, mock_storage):
        """AlarmSchedulerの統合テスト"""
        # ストレージのモック設定
        test_alarm = Alarm(
            id="scheduler_test",
            time=datetime.now().strftime("%H:%M"),  # 現在時刻
            label="スケジューラーテスト",
            enabled=True,
            days=[datetime.now().strftime("%A")],  # 今日
            problem_sets=["test"],
            difficulty="medium",
            sound=SoundConfig(file="test.wav", volume=0.5, loop=True),
            snooze=SnoozeConfig(enabled=False, duration=300, max_count=3)
        )
        
        mock_storage_instance = Mock()
        mock_storage_instance.load_alarms.return_value = [test_alarm]
        mock_storage_instance.save_alarm = Mock()
        mock_storage.return_value = mock_storage_instance
        
        # トリガーコールバックのモック
        trigger_callback = Mock()
        
        # AlarmSchedulerを作成
        scheduler = AlarmScheduler(on_alarm_trigger=trigger_callback)
        scheduler.check_interval = 0.1  # 高速チェックに設定
        
        try:
            # モックでshould_triggerを常にTrueにする
            with patch.object(test_alarm, 'should_trigger', return_value=True):
                scheduler.start()
                
                # 少し待機してアラームが発火するのを待つ
                time.sleep(0.3)
                
                # 検証: トリガーが呼ばれたか
                trigger_callback.assert_called()
                call_args = trigger_callback.call_args[0]
                triggered_alarm = call_args[0]
                self.assertEqual(triggered_alarm.id, "scheduler_test")
                
        finally:
            scheduler.stop()
    
    def test_quiz_completion_flow(self):
        """クイズ完了時の処理フローテスト"""
        alarm_app = TestAlarmApp(self.mock_page)
        alarm_app.alarm_triggered = True
        
        # AlarmManagerのモック
        mock_alarm_manager = Mock()
        alarm_app.alarm_manager = mock_alarm_manager
        
        # スナックバーのモック
        self.mock_page.snack_bar = Mock()
        
        with patch.object(alarm_app, '_show_main_view') as mock_show_main:
            # 正解での完了をテスト
            alarm_app._on_quiz_complete(True)
            
            # 検証: アラーム状態がリセットされたか
            self.assertFalse(alarm_app.alarm_triggered)
            
            # 検証: アラームが停止されたか
            mock_alarm_manager.stop_current_alarm.assert_called_once()
            
            # 検証: メイン画面に戻ったか
            mock_show_main.assert_called_once()
            
            # 検証: 成功メッセージが表示されたか
            self.assertTrue(self.mock_page.snack_bar.open)
    
    @patch('src.ui.quiz_view.QuizView')
    @patch('src.utils.audio.AudioController')
    def test_audio_control_integration(self, mock_audio_controller, mock_quiz_view_class):
        """音声制御の統合テスト"""
        # AudioControllerのモック設定
        mock_audio_instance = Mock()
        mock_audio_controller.return_value = mock_audio_instance
        mock_audio_control = Mock()
        mock_audio_instance.play_alarm.return_value = mock_audio_control
        
        # QuizViewのモック設定
        mock_quiz_view = Mock()
        mock_quiz_view.start_alarm_sound.return_value = mock_audio_control
        mock_quiz_view.get_view.return_value = Mock()
        mock_quiz_view_class.return_value = mock_quiz_view
        
        # テスト用アラーム
        test_alarm = Alarm(
            id="audio_test",
            time="13:00",
            label="音声テスト",
            enabled=True,
            days=["Monday"],
            problem_sets=["test"],
            difficulty="hard",
            sound=SoundConfig(file="test.wav", volume=0.9, loop=True),
            snooze=SnoozeConfig(enabled=False, duration=300, max_count=3)
        )
        
        alarm_app = TestAlarmApp(self.mock_page)
        
        # アラーム発火
        alarm_app._on_alarm_trigger(test_alarm)
        
        # 検証: QuizViewで音声が開始されたか
        mock_quiz_view.start_alarm_sound.assert_called_once_with(test_alarm.sound)
        
        # 検証: 音声コントロールがoverlayに追加されたか
        self.assertIn(mock_audio_control, self.mock_page.overlay)
    
    def test_alarm_already_triggered_scenario(self):
        """既にアラームが発火中の場合のテスト"""
        alarm_app = TestAlarmApp(self.mock_page)
        alarm_app.alarm_triggered = True  # 既に発火中に設定
        
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
        
        with patch('src.ui.quiz_view.QuizView') as mock_quiz_view_class:
            # 2回目のアラーム発火を試行
            alarm_app._on_alarm_trigger(test_alarm)
            
            # 検証: QuizViewが作成されないこと
            mock_quiz_view_class.assert_not_called()
            
            # 検証: ページがクリアされないこと
            self.mock_page.clean.assert_not_called()


if __name__ == '__main__':
    unittest.main()