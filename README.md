# alearm-q（アラームクイズアプリ）

アラームが鳴ったときに問題（クイズ）を解くことで停止する目覚ましアプリです。ラズパイ + タッチスクリーン環境での使用を想定していますが、デスクトップ環境でも動作します。

## 機能概要

- **アラーム機能**: 指定時刻にアラームを発火 ⚠️ **現在バグのため動作しません**
- **クイズシステム**: 数学、一般知識、科学の問題を出題
- **正解まで継続**: 正解するまでアラーム音が止まらない
- **複数難易度**: 簡単・普通・難しいの3段階
- **タッチ操作対応**: ラズパイのタッチスクリーンに最適化

## 現在の実装状況（Phase 1完了）

✅ **実装済み**:
- プロジェクト構造とデータモデル
- アラーム設定・管理機能（⚠️ バグあり：実際のアラーム発火が動作しません）
- クイズ表示・正誤判定システム
- 基本UI（メイン画面、アラーム設定画面、クイズ画面）
- サンプル問題データ（数学・一般知識・科学）

🚧 **今後実装予定**:
- 問題管理UI
- 設定画面UI
- アラーム音声ファイル
- ラズパイでの最終動作確認

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

## 既知の問題

⚠️ **アラーム機能のバグ**: 現在、アラーム機能は実装されていますが、実際のアラーム発火が正常に動作しません。アラーム設定UI は利用できますが、指定時刻になってもアラームが鳴らない状態です。

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