# 目覚ましアプリ（alearm-q）設計ドキュメント

## 概要

alearm-qは、アラームが鳴ったときに問題（クイズまたはゲーム）を解くことで停止する目覚ましアプリです。Fletフレームワークを使用してPythonで開発されます。

## アーキテクチャ

### プロジェクト構造

```
alearm-q/
├── src/
│   ├── main.py                 # メインアプリケーション
│   ├── alarm_manager.py        # アラーム管理クラス
│   ├── quiz_manager.py         # クイズ管理クラス
│   ├── question_loader.py      # 問題データ読み込み
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_view.py        # メイン画面
│   │   ├── alarm_view.py       # アラーム設定画面
│   │   ├── quiz_view.py        # クイズ画面
│   │   └── problem_view.py     # 問題管理画面
│   ├── models/
│   │   ├── __init__.py
│   │   ├── problem.py          # 問題データモデル
│   │   ├── alarm.py            # アラーム設定モデル
│   │   └── handlers.py         # 問題ハンドラー
│   └── utils/
│       ├── __init__.py
│       ├── audio.py            # 音声制御
│       └── storage.py          # データ保存
├── problems/                   # 問題データフォルダ
│   ├── quiz/
│   │   ├── math/
│   │   ├── general/
│   │   └── science/
│   └── games/                  # 将来拡張用
├── assets/                     # アセット
│   ├── sounds/
│   └── images/
└── storage/                    # 設定・データ保存
```

## データ構造

### 問題データ構造（拡張可能）

基本構造：
```json
{
  "id": "問題ID",
  "type": "quiz|game",
  "category": "カテゴリ",
  "title": "問題タイトル",
  "difficulty": "easy|medium|hard",
  "content": {
    // タイプ別の詳細データ
  }
}
```

### クイズ形式

```json
{
  "id": "q001",
  "type": "quiz",
  "category": "math",
  "title": "二次方程式の解",
  "difficulty": "medium",
  "content": {
    "question": {
      "type": "text|text_with_latex|image",
      "text": "問題文",
      "image": "画像パス（オプション）"
    },
    "options": [
      {
        "id": "選択肢ID",
        "type": "text|latex|image",
        "content": "選択肢内容"
      }
    ],
    "correct_answers": ["正解の選択肢IDリスト"]
  }
}
```

### ゲーム形式（将来拡張）

```json
{
  "id": "g001",
  "type": "game",
  "category": "skill",
  "title": "ビリビリ棒",
  "difficulty": "hard",
  "content": {
    "game_type": "steady_hand",
    "config": {
      "maze_path": "assets/maze1.json",
      "time_limit": 30,
      "collision_sensitivity": 5
    },
    "success_condition": {
      "type": "reach_goal",
      "parameters": {
        "goal_area": {"x": 290, "y": 190, "radius": 10}
      }
    }
  }
}
```

### アラーム設定データ

```json
{
  "id": "alarm_001",
  "enabled": true,
  "time": "07:00",
  "days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
  "label": "平日の目覚まし",
  "problem_sets": ["math_basic", "general_knowledge"],
  "difficulty": "medium",
  "sound": {
    "file": "assets/sounds/alarm.mp3",
    "volume": 0.8,
    "loop": true
  },
  "snooze": {
    "enabled": true,
    "duration": 300,
    "max_count": 3
  }
}
```

## 主要クラス設計

### アラーム管理システム

#### アラーム監視とスケジューリング

```python
import threading
import time
from datetime import datetime
from typing import List, Optional

class AlarmScheduler:
    def __init__(self):
        self.alarms: List[Alarm] = []
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.check_interval = 30  # 30秒ごとにチェック
    
    def start(self):
        """アラーム監視開始"""
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
    
    def _monitor_loop(self):
        """定期的にアラーム時刻をチェック"""
        while self.running:
            now = datetime.now()
            for alarm in self.alarms:
                if alarm.should_trigger(now):
                    self._trigger_alarm(alarm)
            time.sleep(self.check_interval)
```

#### アラーム設定クラス

```python
class Alarm:
    def __init__(self, config: dict):
        self.id = config["id"]
        self.enabled = config["enabled"]
        self.time = config["time"]  # "HH:MM"
        self.days = config["days"]
        self.label = config["label"]
        self.problem_sets = config["problem_sets"]
        self.difficulty = config["difficulty"]
        self.sound = config["sound"]
        self.last_triggered = None
    
    def should_trigger(self, now: datetime) -> bool:
        """現在時刻でアラームを発火すべきか判定"""
        if not self.enabled:
            return False
        
        # 曜日・時刻チェック
        weekday = now.strftime("%A").lower()
        if weekday not in self.days:
            return False
        
        # 時刻チェック（30秒の誤差範囲）
        alarm_time = datetime.strptime(self.time, "%H:%M").time()
        target_datetime = datetime.combine(now.date(), alarm_time)
        diff = abs((now - target_datetime).total_seconds())
        
        return diff <= 30
```

#### 音声制御

```python
class AudioController:
    def __init__(self):
        self.audio_player: Optional[ft.Audio] = None
        self.is_playing = False
    
    def play_alarm(self, sound_config: dict):
        """アラーム音再生"""
        self.audio_player = ft.Audio(
            src=sound_config["file"],
            volume=sound_config["volume"],
            autoplay=True
        )
        self.is_playing = True
        return self.audio_player
    
    def stop_alarm(self):
        """アラーム音停止"""
        if self.audio_player:
            self.audio_player.pause()
            self.is_playing = False
```

### 問題表示・クイズシステム

#### 問題レンダリング

```python
class QuestionRenderer:
    def __init__(self):
        self.latex_enabled = False  # 将来実装
    
    def render_question(self, question_data: dict) -> ft.Control:
        """問題文をレンダリング"""
        question_type = question_data["type"]
        
        if question_type == "text":
            return ft.Text(question_data["text"], size=18, weight=ft.FontWeight.BOLD)
        elif question_type == "text_with_latex":
            return self._render_latex_text(question_data["text"])
        elif question_type == "image":
            return ft.Column([
                ft.Text(question_data["text"], size=18) if question_data.get("text") else None,
                ft.Image(src=question_data["image"], width=400, height=300)
            ])
    
    def render_options(self, options: List[dict], allow_multiple: bool = True) -> List[ft.Control]:
        """選択肢をレンダリング"""
        option_controls = []
        for option in options:
            if allow_multiple:
                control = ft.Checkbox(
                    label=option["content"] if option["type"] == "text" else None,
                    data=option["id"],
                    content=self._render_option_content(option) if option["type"] != "text" else None
                )
            else:
                control = ft.Radio(
                    label=option["content"] if option["type"] == "text" else None,
                    value=option["id"],
                    data=option["id"]
                )
            option_controls.append(control)
        return option_controls
```

#### クイズセッション管理

```python
class QuizSession:
    def __init__(self, problem_sets: List[str], difficulty: str):
        self.problem_sets = problem_sets
        self.difficulty = difficulty
        self.problems: List[dict] = []
        self.current_problem_index = 0
        self.total_attempts = 0
        self.correct_answers = 0
    
    def start_session(self):
        """クイズセッション開始"""
        self.problems = self._load_problems()
        self.current_problem_index = 0
    
    def submit_answer(self, selected_options: List[str]) -> bool:
        """回答を提出して正誤判定"""
        current_problem = self.get_current_problem()
        if not current_problem:
            return False
        
        self.total_attempts += 1
        correct_answers = set(current_problem["content"]["correct_answers"])
        selected_answers = set(selected_options)
        
        is_correct = correct_answers == selected_answers
        
        if is_correct:
            self.correct_answers += 1
            return True
        else:
            # 不正解の場合、次の問題に進む
            self.current_problem_index += 1
            return False
    
    def is_session_complete(self) -> bool:
        """セッション完了判定"""
        return self.correct_answers > 0  # 1問正解で完了
```

#### 問題データローダー

```python
class ProblemLoader:
    def __init__(self, problems_dir: str = "problems"):
        self.problems_dir = problems_dir
        self.cache: Dict[str, List[dict]] = {}
    
    def load_problem_set(self, set_name: str) -> List[dict]:
        """問題セットを読み込み"""
        if set_name in self.cache:
            return self.cache[set_name]
        
        set_path = os.path.join(self.problems_dir, "quiz", f"{set_name}.json")
        
        try:
            with open(set_path, 'r', encoding='utf-8') as f:
                problems = json.load(f)
            
            validated_problems = [p for p in problems if self._validate_problem(p)]
            self.cache[set_name] = validated_problems
            return validated_problems
            
        except Exception as e:
            print(f"問題セット読み込みエラー: {e}")
            return []
    
    def _validate_problem(self, problem: dict) -> bool:
        """問題データの検証"""
        required_fields = ["id", "type", "category", "title", "difficulty", "content"]
        return all(field in problem for field in required_fields)
```

### 問題ハンドラー（抽象化）

```python
from abc import ABC, abstractmethod

class ProblemHandler(ABC):
    @abstractmethod
    def render(self, page: ft.Page, problem_data: dict) -> ft.Control:
        """問題UIをレンダリング"""
        pass
    
    @abstractmethod
    def check_answer(self, user_input: any) -> bool:
        """回答の正誤判定"""
        pass
    
    @abstractmethod
    def get_progress(self) -> float:
        """進行状況を取得（0.0-1.0）"""
        pass

class QuizHandler(ProblemHandler):
    def __init__(self):
        self.selected_options = []
        self.problem_data = None
        self.question_renderer = QuestionRenderer()
    
    def render(self, page: ft.Page, problem_data: dict) -> ft.Control:
        self.problem_data = problem_data
        content = problem_data["content"]
        
        question_control = self.question_renderer.render_question(content["question"])
        options_controls = self.question_renderer.render_options(content["options"])
        
        return ft.Column([
            question_control,
            ft.Divider(),
            *options_controls
        ])
    
    def check_answer(self, selected_options: list) -> bool:
        correct = set(self.problem_data["content"]["correct_answers"])
        selected = set(selected_options)
        return correct == selected
```

### 問題ファクトリー

```python
class ProblemFactory:
    handlers = {
        "quiz": QuizHandler,
        # "game": GameHandler,  # 将来拡張
    }
    
    @classmethod
    def create_handler(cls, problem_type: str) -> ProblemHandler:
        handler_class = cls.handlers.get(problem_type)
        if not handler_class:
            raise ValueError(f"Unsupported problem type: {problem_type}")
        return handler_class()
```

## UI設計（ラズパイ・タッチスクリーン特化）

### ターゲット環境
- **メイン環境**: ラズパイ + 7インチタッチスクリーン（1024x600 / 800x480）
- **将来対応**: 3.5インチタッチスクリーン（480x320）
- **操作方式**: タッチ操作メイン（マウス・キーボード不要）

### 画面遷移

```
メイン画面（/）
├── アラーム一覧（/alarms）
├── アラーム設定（/alarms/new, /alarms/edit/{id}）
├── 問題管理（/problems）
└── 設定（/settings）

アラーム発火時（フルスクリーン・脱出不可）
└── 問題解決画面（/solve）
    ├── 問題表示（上半分）
    ├── 選択肢ボタン群（下半分上部）
    └── 回答ボタン（下半分下部）
```

### 画面レイアウト設計

#### クイズ画面（7インチ向け）
```
┌─────────────────────────────┐
│                             │
│     問題文表示エリア          │ 上半分1/2
│  （テキスト・数式・画像）      │ 大きく表示
│        大きく表示           │
│                             │
├─────────────────────────────┤
│ ┌─────┐ ┌─────┐ ┌─────┐    │
│ │選択肢A│ │選択肢B│ │選択肢C│    │ 下半分の
│ └─────┘ └─────┘ └─────┘    │ 上部3/4
│ ┌─────┐ ┌─────┐ ┌─────┐    │ ボタン方式
│ │選択肢D│ │選択肢E│ │選択肢F│    │
│ └─────┘ └─────┘ └─────┘    │
├─────────────────────────────┤
│      ┌────────────┐         │ 下半分の
│      │    回答    │         │ 下部1/4
│      └────────────┘         │
└─────────────────────────────┘
```

#### クイズ画面（3.5インチ向け）
```
┌─────────────────┐
│                 │
│  問題文表示      │ 上半分1/2
│                 │
├─────────────────┤
│ ┌─────────────┐ │
│ │   選択肢A    │ │
│ └─────────────┘ │
│ ┌─────────────┐ │ 下半分の
│ │   選択肢B    │ │ 上部3/4
│ └─────────────┘ │ (縦配置)
│ ┌─────────────┐ │
│ │   選択肢C    │ │
│ └─────────────┘ │
├─────────────────┤
│ ┌─────────────┐ │ 下半分の
│ │     回答     │ │ 下部1/4
│ └─────────────┘ │
└─────────────────┘
```

### タッチインターフェース設計

#### ボタンデザイン仕様
- **選択肢ボタン**:
  - サイズ: 最小60x40px（タッチターゲット確保）
  - 未選択: 薄いグレー背景、黒文字
  - 選択済み: 青色背景、白文字
  - タッチ時: 一瞬の色変化でフィードバック
- **回答ボタン**:
  - サイズ: 大きめ（120x50px以上）
  - 緑色背景、白文字
  - 中央配置で目立つ配色

#### インタラクション仕様
- **タップフィードバック**: 即座の視覚的反応
- **複数選択**: 複数ボタンの同時選択可能
- **スクロール**: 長い問題文のタッチスクロール対応
- **戻る操作無効**: アラーム発火時の脱出防止

### 画面別詳細設計

#### メイン画面
- **大型ボタン**: 主要機能へのアクセス
- **次回アラーム表示**: 視認性の高い時刻表示
- **アラーム一覧**: ON/OFF切り替えスイッチ

#### アラーム設定画面
- **時刻選択**: 大きなタイムピッカー
- **曜日選択**: トグルボタン形式
- **問題設定**: ドロップダウンメニュー
- **保存・キャンセル**: 分かりやすい配置

#### アラーム発火時の特別仕様
- **フルスクリーン**: 他の操作を完全無効化
- **目立つ背景**: 赤系の背景で緊急感演出
- **大きな文字**: 寝起きでも読みやすいサイズ
- **脱出不可**: 正解まで他画面への移動不可

### レスポンシブ対応

#### 画面サイズ別調整
- **7インチ（800x480）**: ベース設計
- **3.5インチ（480x320）**: 
  - 選択肢の縦配置
  - フォントサイズ縮小
  - ボタンサイズ調整（最小サイズ維持）

#### パフォーマンス考慮
- **軽量UI**: ラズパイでもスムーズな動作
- **最小限のアニメーション**: 処理負荷軽減
- **効率的更新**: 必要部分のみレンダリング

## 技術仕様

### 使用技術
- **UI**: Flet (Python + Flutter)
- **数式表示**: LaTeX対応（将来実装）
- **音声**: Fletの Audio widget
- **データ保存**: JSON ファイル
- **画像**: Fletの Image widget

### 正解判定ロジック
- 選択された選択肢のセット == 正解選択肢のセット
- 完全一致のみ正解（部分正解なし）
- 不正解時は次の問題を出題
- 正解するまでアラーム継続

### 拡張性
- 新しい問題タイプ（ゲーム）の追加が容易
- 問題ハンドラーの抽象化により統一インターフェース
- プラグイン方式での機能拡張

## 実装優先度

### Phase 1（初期実装）
- [x] 基本設計
- [x] プロジェクト構造作成
- [x] クイズハンドラー実装
- [x] 基本的なUI実装
- [x] アラーム機能実装

### Phase 2（拡張）
- [ ] LaTeX数式表示
- [ ] 画像問題対応
- [ ] 音声制御改善
- [ ] データ管理UI

### Phase 3（ゲーム対応）
- [ ] ゲームハンドラー実装
- [ ] Canvas利用のゲーム
- [ ] ビリビリ棒ゲーム
- [ ] その他ミニゲーム

## 実装状況（2025年7月5日時点）

### 完了した機能
- **プロジェクト構造**: 設計通りにディレクトリ構造を作成完了
- **データモデル**: Problem、Alarm、QuizContentなどの型安全なデータクラス実装
- **問題管理システム**: JSON形式の問題データ読み込み・検証機能
- **UI基盤**: MainView、AlarmView、QuizView の基本実装
- **アラーム機能**: 時刻監視とアラーム発火システム
- **クイズシステム**: 問題表示と正誤判定機能
- **サンプルデータ**: 数学、一般知識、科学の問題データ作成

### 設計からの変更点

#### 1. UI実装アプローチの変更
**設計**: `ft.UserControl`を継承したクラス設計
**実装**: Fletの現行バージョンでは`UserControl`が利用不可のため、通常のクラス + `build()`メソッドパターンに変更

#### 2. カラーAPI変更対応
**設計**: `ft.colors.*`を使用
**実装**: Fletの現行バージョンでは文字列ベースの色指定（例: `"blue"`, `"red900"`）に変更

#### 3. フォント設定の追加
**設計**: 特に言及なし
**実装**: 日本語文字化け対応のため、Noto Sans CJKフォント設定とエンコーディング宣言を追加

#### 4. ボタン機能の段階実装
**設計**: すべてのUI機能を同時実装
**実装**: アラーム設定機能を優先実装し、問題管理・設定機能は「今後実装予定」メッセージで対応

### 技術的な課題と解決

#### 1. 相対インポート問題
- **問題**: モジュール間の相対インポートでエラー発生
- **解決**: プロジェクトルートからの絶対インポートに変更

#### 2. デスクトップ環境での警告
- **現象**: Gdk-Message、Atk-CRITICAL警告が表示
- **対応**: アプリケーション動作に影響なし、表示上の警告として許容

#### 3. 日本語フォント対応
- **問題**: 日本語文字の表示で文字化け
- **解決**: UTF-8エンコーディング宣言とNoto Sans CJKフォント設定

### 動作確認済み機能
- [x] アプリケーション起動（デスクトップモード）
- [x] メイン画面表示
- [x] アラーム設定画面遷移
- [x] 日本語文字表示
- [x] ボタンクリック反応
- [x] 基本的なUI操作

### 今後の実装予定
- [ ] 問題管理UI（Phase 2）
- [ ] 設定画面UI（Phase 2）
- [ ] アラーム音声ファイル
- [ ] 実際のアラーム発火テスト
- [ ] ラズパイでの動作確認

## 注意事項

- アラーム機能は実際の時刻に基づいて動作
- 問題データは外部ファイルで管理
- 正解するまでアラーム音が継続
- 複数の問題セットから選択可能
- 拡張可能な設計を重視
- 現在はデスクトップ環境での開発・テスト段階