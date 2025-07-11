# alearm-q（アラームクイズアプリ）

アラームが鳴ったときに問題（クイズ）を解くことで停止する目覚ましアプリです。ラズパイ + タッチスクリーン環境での使用を想定していますが、デスクトップ環境でも動作します。

## 機能概要

- **アラーム機能**: 指定時刻にアラームを発火（音声再生機能完全対応）
- **クイズシステム**: 数学、一般知識、科学の問題を出題
- **正解まで継続**: 正解するまでアラーム音が止まらない
- **複数難易度**: 簡単・普通・難しいの3段階
- **タッチ操作対応**: ラズパイのタッチスクリーンに最適化

## 現在の実装状況（Phase 1-2完了）

✅ **実装済み**:
- プロジェクト構造とデータモデル
- アラーム設定・管理機能（音声再生完全対応）
- クイズ表示・正誤判定システム
- 基本UI（メイン画面、アラーム設定画面、クイズ画面）
- 問題管理UI
- 設定画面UI
- アラーム音声ファイル・システムオーディオ対応
- サンプル問題データ（数学・一般知識・科学）
- 包括的テストスイート

🚧 **今後実装予定**:
- ラズパイでの最終動作確認
- 追加の問題データセット

## Run the app

### uv

Run as a desktop app:

```bash
uv run flet run
```

Run as a web app:

```bash
uv run flet run --web
```

For more details on running the app, refer to the [Getting Started Guide](https://flet.dev/docs/getting-started/).

## プロジェクト構造

```
alearm-q/
├── src/                    # ソースコード
│   ├── main.py            # メインアプリケーション
│   ├── alarm_manager.py   # アラーム管理
│   ├── quiz_manager.py    # クイズ管理
│   ├── question_loader.py # 問題データ読み込み
│   ├── models/            # データモデル
│   ├── ui/                # UI コンポーネント
│   └── utils/             # ユーティリティ
├── problems/              # 問題データ（JSON）
│   └── quiz/              # クイズ問題
├── assets/                # アセット（アイコン等）
├── storage/               # 設定・データ保存
├── DESIGN.md              # 設計ドキュメント
└── pyproject.toml         # プロジェクト設定
```

## 開発・テスト

Testing:
```bash
uv run pytest tests/
```

Type checking:
```bash
uv run mypy src/
```

Linting:
```bash
uv run ruff check src/
```

Formatting:
```bash
uv run ruff format src/
```

## 技術仕様

### 音声システム
- **システムオーディオ**: プラットフォーム固有のコマンドを使用
  - Linux: `aplay` または `paplay`
  - macOS: `afplay`  
  - Windows: PowerShell Media.SoundPlayer
- **音声ファイル形式**: WAV、MP3対応
- **ループ再生**: アラーム音の連続再生機能

## 最近の更新

### v0.1.0 - 音声システム修正・機能追加
- ✅ **音声再生バグ修正**: Fletオーディオからシステムオーディオに切り替え
- ✅ **マルチプラットフォーム対応**: Linux/macOS/Windows各OSでの音声再生
- ✅ **UI機能拡張**: 問題管理画面、設定画面を追加
- ✅ **テスト充実**: 音声システムとアラーム機能の包括的テスト
- ✅ **音声ファイル追加**: デフォルトアラーム音と追加サウンド

## Build the app

### Android

```
flet build apk -v
```

For more details on building and signing `.apk` or `.aab`, refer to the [Android Packaging Guide](https://flet.dev/docs/publish/android/).

### iOS

```
flet build ipa -v
```

For more details on building and signing `.ipa`, refer to the [iOS Packaging Guide](https://flet.dev/docs/publish/ios/).

### macOS

```
flet build macos -v
```

For more details on building macOS package, refer to the [macOS Packaging Guide](https://flet.dev/docs/publish/macos/).

### Linux

```
flet build linux -v
```

For more details on building Linux package, refer to the [Linux Packaging Guide](https://flet.dev/docs/publish/linux/).

### Windows

```
flet build windows -v
```

For more details on building Windows package, refer to the [Windows Packaging Guide](https://flet.dev/docs/publish/windows/).