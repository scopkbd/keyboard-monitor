# キーボードモニター - アーキテクチャ設計書

## 概要

このドキュメントは、キーボードモニターソフトウェアのアーキテクチャ設計について詳細に説明します。

## システム全体アーキテクチャ

### 設計方針

1. **シングルプロセス設計**: CLIモードで単一プロセス内でキーロガーとユーザーインターフェースを管理
2. **マルチスレッド構成**: UI応答性とキー監視の独立性を確保
3. **モジュラー設計**: 各機能を独立したクラスで実装し、保守性を向上
4. **データ駆動**: JSON形式でのデータ管理により、柔軟性と拡張性を確保

### 全体構成図

```
┌─────────────────────────────────────────────────────────────┐
│                    Keyboard Monitor                         │
├─────────────────────────────────────────────────────────────┤
│  Main Thread (UI)           │  Background Thread (Logger)   │
│  ┌─────────────────────┐    │  ┌─────────────────────────┐   │
│  │ CLI Interface       │    │  │ Keyboard Listener       │   │
│  │ - Command Parser    │    │  │ - Key Event Capture     │   │
│  │ - Status Display    │    │  │ - Modifier Detection    │   │
│  │ - User Interaction  │    │  │ - Sequence Tracking     │   │
│  └─────────────────────┘    │  └─────────────────────────┘   │
│           │                 │            │                   │
│           │ Commands        │ Key Data   │                   │
│           ▼                 │            ▼                   │
│  ┌─────────────────────┐    │  ┌─────────────────────────┐   │
│  │ Controller          │◄───┼──│ Data Processor          │   │
│  │ - State Management  │    │  │ - Event Analysis        │   │
│  │ - Command Routing   │    │  │ - Statistics Update     │   │
│  │ - Thread Coordination│   │  │ - Sequence Analysis     │   │
│  └─────────────────────┘    │  └─────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    Shared Data Layer                        │
│  ┌─────────────────────┐    ┌─────────────────────────┐     │
│  │ Statistics Manager  │    │ Configuration Manager   │     │
│  │ - Real-time Stats   │    │ - Settings              │     │
│  │ - Historical Data   │    │ - User Preferences      │     │
│  │ - Analysis Results  │    │ - System Configuration  │     │
│  └─────────────────────┘    └─────────────────────────┘     │
├─────────────────────────────────────────────────────────────┤
│                    Storage Layer                            │
│  ┌─────────────────────┐    ┌─────────────────────────┐     │
│  │ JSON Data Store     │    │ Backup Manager          │     │
│  │ - keyboard_log.json │    │ - Auto Backup           │     │
│  │ - Atomic Writes     │    │ - Data Recovery         │     │
│  │ - Data Validation   │    │ - Compression           │     │
│  └─────────────────────┘    └─────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## コンポーネント設計

### 1. メインコントローラー（keyboard_monitor.py）

**責務**:
- アプリケーションのライフサイクル管理
- スレッド間の調整
- コマンドルーティング
- エラーハンドリング

**主要メソッド**:
```python
class KeyboardMonitor:
    def __init__(self)
    def start_cli_mode(self)
    def start_logging(self)
    def stop_logging(self)
    def get_status(self)
    def get_statistics(self)
    def shutdown(self)
```

### 2. キーロガー（logger.py）

**責務**:
- キーボードイベントの監視
- モディファイアキーの状態管理
- リアルタイムデータ処理
- イベントキューの管理

**主要メソッド**:
```python
class KeyboardLogger:
    def __init__(self, data_processor)
    def start_logging(self)
    def stop_logging(self)
    def on_key_press(self, key)
    def on_key_release(self, key)
    def get_modifier_state(self)
    def process_key_event(self, key, modifiers)
```

**スレッド設計**:
- バックグラウンドスレッドで実行
- ノンブロッキングキーイベント処理
- スレッドセーフなデータ共有

### 3. データプロセッサー（data_processor.py）

**責務**:
- キーイベントの分析
- 統計データの更新
- シーケンス分析
- データの正規化

**主要メソッド**:
```python
class DataProcessor:
    def __init__(self, statistics_manager)
    def process_key_event(self, key_code, key_name, modifiers, timestamp)
    def update_key_statistics(self, key_code, modifiers)
    def update_sequence_analysis(self, key_code)
    def update_predecessor_analysis(self, current_key, previous_key, modifiers)
```

### 4. 統計マネージャー（statistics.py）

**責務**:
- 統計データの管理
- リアルタイム計算
- 履歴データの保持
- 分析結果の生成

**主要メソッド**:
```python
class StatisticsManager:
    def __init__(self, data_store)
    def update_statistics(self, key_data)
    def get_real_time_stats(self)
    def get_historical_stats(self, date_range)
    def get_top_keys(self, limit=10)
    def get_modifier_analysis(self)
    def get_sequence_analysis(self)
    def calculate_typing_patterns(self)
```

### 5. データストア（data_store.py）

**責務**:
- JSONファイルの読み書き
- データの永続化
- バックアップ管理
- データ整合性の保証

**主要メソッド**:
```python
class DataStore:
    def __init__(self, file_path)
    def load_data(self)
    def save_data(self, data)
    def backup_data(self)
    def validate_data(self, data)
    def migrate_data(self, old_version, new_version)
```

## データフロー設計

### 1. キーイベント処理フロー

```
[キー押下]
    ↓
[Keyboard Listener]
    ↓
[Modifier State Detection]
    ↓
[Event Queue]
    ↓
[Data Processor]
    ↓
[Statistics Update]
    ↓
[Data Store]
```

### 2. 統計分析フロー

```
[Raw Key Data]
    ↓
[Basic Statistics] → [Key Frequency]
    ↓
[Modifier Analysis] → [Combination Patterns]
    ↓
[Sequence Analysis] → [Bigram/Trigram]
    ↓
[Predecessor Analysis] → [Key Relationships]
    ↓
[Report Generation]
```

### 3. リアルタイム表示フロー

```
[Background Thread]
    ↓
[Shared State Update]
    ↓
[Main Thread]
    ↓
[CLI Display Refresh]
    ↓
[User Interface Update]
```

## スレッド設計詳細

### メインスレッド (UI Thread)

**責務**:
- ユーザーインターフェースの管理
- コマンド入力の処理
- リアルタイム表示の更新
- システム制御

**v1.0での主要改善**:
- **入力中表示停止**: `input_in_progress`フラグによる表示更新の制御
- **カーソル位置制御**: ANSIエスケープシーケンスによる効率的な画面更新
- **非破壊的表示**: 画面全体をクリアせずに必要部分のみ更新

**実装パターン**:
```python
def _cli_command_loop(self):
    while self.cli_running:
        try:
            # 入力開始前にフラグを設定（表示更新を停止）
            self.input_in_progress = True
            command = input(f"{Fore.CYAN}> {Style.RESET_ALL}").strip().lower()
            # 入力完了後にフラグをクリア（表示更新を再開）
            self.input_in_progress = False

            # コマンド処理
            self.process_command(command)

        except (EOFError, KeyboardInterrupt):
            self.input_in_progress = False
            break

def _display_loop(self):
    last_display_lines = 0
    while self.cli_running:
        # 入力中でない場合のみ表示更新
        if self.keyboard_logger.is_running() and not self.input_in_progress:
            # カーソル位置制御による上書き更新
            if last_display_lines > 0:
                print(f"\033[{last_display_lines}A", end="")

            display_content = self._get_real_time_display()
            print(display_content)
            last_display_lines = display_content.count('\n') + 1

        time.sleep(self.config.get_display_refresh_interval())
```

### バックグラウンドスレッド (Logger Thread)

**責務**:
- キーボードイベントの監視
- データの非同期処理
- 統計情報の更新
- ファイルの自動保存

**実装パターン**:
```python
def logger_thread_main(self):
    with keyboard.Listener(
        on_press=self.on_key_press,
        on_release=self.on_key_release
    ) as listener:
        while self.logging_active:
            # イベント処理とデータ更新
            self.process_pending_events()

            # 定期的な保存
            if self.should_save():
                self.save_data()

            time.sleep(0.01)  # 高頻度処理
```

## エラーハンドリング設計

### エラー分類

1. **システムエラー**
   - 権限不足
   - ファイルアクセス失敗
   - メモリ不足

2. **データエラー**
   - JSON形式エラー
   - データ破損
   - バージョン不整合

3. **運用エラー**
   - 設定エラー
   - ユーザー入力エラー
   - ネットワークエラー

### エラー処理戦略

```python
class ErrorHandler:
    def handle_system_error(self, error):
        # ログ記録
        self.log_error(error)

        # ユーザー通知
        self.notify_user(error)

        # 復旧処理
        if self.can_recover(error):
            self.attempt_recovery(error)
        else:
            self.graceful_shutdown()

    def handle_data_error(self, error):
        # データバックアップ
        self.backup_current_data()

        # データ復旧
        self.restore_from_backup()

        # 継続可能性の判断
        if self.data_is_valid():
            self.continue_operation()
        else:
            self.reset_data_store()
```

## パフォーマンス設計

### メモリ管理

1. **キーイベントバッファ**
   - 固定サイズのリングバッファ
   - 最大1000イベント保持
   - 古いイベントの自動削除

2. **統計データ圧縮**
   - 低頻度データの統合
   - 閾値以下のデータ削除
   - 定期的なデータクリーンアップ

### CPU最適化

1. **非同期処理**
   - キーイベント処理の非同期化
   - ファイルI/Oの非同期化
   - 統計計算の分散処理

2. **キャッシュ戦略**
   - 頻繁にアクセスされるデータのメモリキャッシュ
   - LRUキャッシュの実装
   - 計算結果のキャッシュ

## セキュリティ設計

### データ保護

1. **ファイルアクセス制御**
   - 適切なファイル権限設定
   - 一時ファイルの安全な削除
   - アクセスログの記録

2. **データ匿名化**
   - オプションでの機密データ除外
   - ハッシュ化による匿名化
   - データの暗号化（将来実装）

### プロセス保護

1. **権限最小化**
   - 必要最小限の権限で実行
   - サンドボックス環境の検討
   - 外部通信の制限

## 拡張性設計

### プラグインアーキテクチャ

将来的なプラグイン対応のための設計：

```python
class PluginManager:
    def __init__(self):
        self.plugins = []

    def load_plugin(self, plugin_path):
        # プラグインの動的ロード
        pass

    def register_event_handler(self, event_type, handler):
        # イベントハンドラーの登録
        pass
```

### 設定拡張

```python
class ConfigurationManager:
    def __init__(self):
        self.config_schema = self.load_schema()

    def validate_config(self, config):
        # 設定の検証
        pass

    def extend_schema(self, new_schema):
        # スキーマの拡張
        pass
```
