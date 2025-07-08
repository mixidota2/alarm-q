# -*- coding: utf-8 -*-
import unittest
from unittest.mock import Mock, patch
import os
import sys
import tempfile
import wave
import struct
import math

# Add src to path for importing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.audio import AudioController
import flet as ft


class TestAudioController(unittest.TestCase):
    def setUp(self):
        """各テストの前に実行される初期化処理"""
        self.audio_controller = AudioController()
        self.mock_page = Mock(spec=ft.Page)
        self.mock_page.overlay = []
    
    def tearDown(self):
        """各テストの後に実行されるクリーンアップ処理"""
        self.audio_controller.stop_alarm()
    
    def test_set_page(self):
        """ページ参照の設定をテスト"""
        # テスト実行
        self.audio_controller.set_page(self.mock_page)
        
        # 検証
        self.assertEqual(self.audio_controller.page, self.mock_page)
    
    def test_initial_state(self):
        """初期状態をテスト"""
        self.assertIsNone(self.audio_controller.audio_player)
        self.assertFalse(self.audio_controller.is_playing)
        self.assertFalse(self.audio_controller.should_loop)
        self.assertIsNone(self.audio_controller.page)
    
    @patch('os.path.exists')
    @patch('flet.Audio')
    def test_play_alarm_with_valid_file(self, mock_audio, mock_exists):
        """有効な音声ファイルでのアラーム再生をテスト"""
        # モックの設定
        mock_exists.return_value = True
        mock_audio_instance = Mock()
        mock_audio.return_value = mock_audio_instance
        
        # テストデータ
        sound_config = {
            'file': 'assets/sounds/test_alarm.wav',
            'volume': 0.8,
            'loop': True
        }
        
        # テスト実行
        result = self.audio_controller.play_alarm(sound_config)
        
        # 検証
        self.assertEqual(result, mock_audio_instance)
        self.assertTrue(self.audio_controller.is_playing)
        self.assertTrue(self.audio_controller.should_loop)
        mock_audio.assert_called_once()
        
        # Audio作成時の引数を検証
        args, kwargs = mock_audio.call_args
        self.assertEqual(kwargs['volume'], 0.8)
        self.assertTrue(kwargs['autoplay'])
    
    @patch('os.path.exists')
    def test_play_alarm_with_nonexistent_file(self, mock_exists):
        """存在しない音声ファイルでのアラーム再生をテスト"""
        # モックの設定 - すべてのファイルが存在しない
        mock_exists.return_value = False
        
        # テストデータ
        sound_config = {
            'file': 'nonexistent.wav',
            'volume': 0.8,
            'loop': True
        }
        
        # テスト実行
        result = self.audio_controller.play_alarm(sound_config)
        
        # 検証 - テスト用音声が作成される（Noneが返される）
        self.assertIsNone(result)
        self.assertTrue(self.audio_controller.is_playing)
    
    def test_create_temporary_audio_file(self):
        """テスト用の音声ファイル作成をテスト"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # テスト用音声ファイルを作成
            self._create_test_wav_file(temp_path)
            
            # ファイルが正常に作成されていることを確認
            self.assertTrue(os.path.exists(temp_path))
            self.assertGreater(os.path.getsize(temp_path), 100)  # 最低限のサイズ
            
            # WAVファイルとして読み込み可能かテスト
            with wave.open(temp_path, 'r') as wav_file:
                self.assertEqual(wav_file.getnchannels(), 1)  # モノラル
                self.assertEqual(wav_file.getsampwidth(), 2)   # 16ビット
                self.assertEqual(wav_file.getframerate(), 44100)  # サンプルレート
        
        finally:
            # クリーンアップ
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def _create_test_wav_file(self, filepath):
        """テスト用のWAVファイルを作成"""
        sample_rate = 44100
        duration = 0.5  # 0.5秒
        frequency = 440  # A4音
        
        samples = []
        for i in range(int(sample_rate * duration)):
            t = i / sample_rate
            amplitude = 0.5 * math.sin(2 * math.pi * frequency * t)
            sample = int(amplitude * 32767)
            samples.append(sample)
        
        with wave.open(filepath, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            packed_samples = struct.pack('<' + 'h' * len(samples), *samples)
            wav_file.writeframes(packed_samples)
    
    def test_stop_alarm(self):
        """アラーム停止をテスト"""
        # モックのオーディオプレイヤーを設定
        mock_audio_player = Mock(spec=ft.Audio)
        self.audio_controller.audio_player = mock_audio_player
        self.audio_controller.is_playing = True
        self.audio_controller.should_loop = True
        
        # テスト実行
        self.audio_controller.stop_alarm()
        
        # 検証
        self.assertFalse(self.audio_controller.is_playing)
        self.assertFalse(self.audio_controller.should_loop)
        mock_audio_player.pause.assert_called_once()
    
    def test_stop_alarm_with_exception(self):
        """アラーム停止時の例外処理をテスト"""
        # モックのオーディオプレイヤーを設定（例外を発生させる）
        mock_audio_player = Mock(spec=ft.Audio)
        mock_audio_player.pause.side_effect = Exception("Test exception")
        self.audio_controller.audio_player = mock_audio_player
        self.audio_controller.is_playing = True
        
        # テスト実行（例外が発生しないことを確認）
        self.audio_controller.stop_alarm()
        
        # 検証
        self.assertFalse(self.audio_controller.is_playing)
    
    def test_get_audio_control(self):
        """オーディオコントロール取得をテスト"""
        # 初期状態
        self.assertIsNone(self.audio_controller.get_audio_control())
        
        # オーディオプレイヤーを設定
        mock_audio_player = Mock(spec=ft.Audio)
        self.audio_controller.audio_player = mock_audio_player
        
        # テスト実行
        result = self.audio_controller.get_audio_control()
        
        # 検証
        self.assertEqual(result, mock_audio_player)
    
    @patch('os.path.exists')
    @patch('flet.Audio')
    def test_relative_path_conversion(self, mock_audio, mock_exists):
        """相対パスから絶対パスへの変換をテスト"""
        mock_exists.return_value = True
        mock_audio_instance = Mock()
        mock_audio.return_value = mock_audio_instance
        
        # 相対パスでテスト
        sound_config = {
            'file': 'assets/sounds/alarm.wav',
            'volume': 0.8,
            'loop': True
        }
        
        # テスト実行
        self.audio_controller.play_alarm(sound_config)
        
        # 検証 - 絶対パスに変換されていることを確認
        # mock_existsが呼ばれた引数を確認
        call_args = mock_exists.call_args_list
        self.assertTrue(any(os.path.isabs(call[0][0]) for call in call_args))
    
    def test_state_change_callback(self):
        """音声状態変更コールバックをテスト"""
        # モックのオーディオプレイヤーを設定
        mock_audio_player = Mock(spec=ft.Audio)
        self.audio_controller.audio_player = mock_audio_player
        self.audio_controller.is_playing = True
        self.audio_controller.should_loop = True
        
        # モックイベントを作成
        mock_event = Mock()
        mock_event.data = "completed"
        
        # テスト実行
        self.audio_controller._on_state_changed(mock_event)
        
        # 検証 - ループ再生のためのseekとresumeが呼ばれる
        mock_audio_player.seek.assert_called_once_with(0)
        mock_audio_player.resume.assert_called_once()
    
    def test_duration_change_callback(self):
        """音声長変更コールバックをテスト"""
        # モックイベントを作成
        mock_event = Mock()
        mock_event.data = 2.5  # 2.5秒
        
        # テスト実行（例外が発生しないことを確認）
        self.audio_controller._on_duration_changed(mock_event)
        
        # このメソッドはログ出力のみなので、例外が発生しなければOK
        self.assertTrue(True)
    
    @patch('os.path.exists')
    @patch('flet.Audio')
    def test_default_volume_and_loop(self, mock_audio, mock_exists):
        """デフォルトの音量とループ設定をテスト"""
        mock_exists.return_value = True
        mock_audio_instance = Mock()
        mock_audio.return_value = mock_audio_instance
        
        # 音量とループ設定なしのconfig
        sound_config = {
            'file': 'assets/sounds/alarm.wav'
        }
        
        # テスト実行
        self.audio_controller.play_alarm(sound_config)
        
        # 検証 - デフォルト値が使用されている
        args, kwargs = mock_audio.call_args
        self.assertEqual(kwargs['volume'], 0.8)  # デフォルト音量
        self.assertTrue(self.audio_controller.should_loop)  # デフォルトループ


if __name__ == '__main__':
    unittest.main()