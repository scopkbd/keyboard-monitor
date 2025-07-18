# GUI版要件仕様書

## 機能要件

### FR-01: メインウィンドウ
- **説明**: アプリケーションのメイン画面
- **要件**:
  - 1200x800px のデフォルトサイズ
  - 最小サイズ 800x600px
  - リサイズ可能
  - Windows標準の最小化/最大化/閉じるボタン

### FR-02: ナビゲーション
- **説明**: 機能間の移動
- **要件**:
  - 左サイドバーによる主要機能への直接アクセス
  - アイコン + テキストによる分かりやすい表示
  - 現在位置の視覚的ハイライト

### FR-03: ダッシュボード
- **説明**: 現在の状況の一覧表示
- **要件**:
  - 記録状況（開始/停止状態）
  - リアルタイム統計（現在セッション、総計）
  - クイック操作ボタン（開始/停止/統計表示）

### FR-04: 統計表示
- **説明**: キーボード使用統計の表示
- **要件**:
  - 基本統計（総キーストローク、期間、平均）
  - キー使用頻度ランキング（トップ10以上）
  - モディファイア組み合わせ分析
  - シーケンス分析（bigram/trigram）

### FR-04-2: 統合分析画面
- **説明**: 包括的なキーボード使用パターン分析画面
- **要件**:
  - **ステータスバー統計表示**: 総キーストロークと記録期間をヘッダー部に表示
  - **上位キー分析カード**: 使用頻度ランキング（テーブル形式）と使用率の表示
  - **モディファイア詳細カード**: 4列グリッド形式（Shift/Ctrl/Alt/Super）での修飾キー分析
    - 各修飾キーごとの上位5キーランキング表示
    - 修飾キー別の色分けとランキング順位による濃淡表示
  - **統合シーケンス分析カード**: キー中心の前後関係マップ（3列レイアウト）
    - 左列: 直前に押されたキーのランキング（上位3位）
    - 中央: メインキー（使用頻度順の上位5キー）
    - 右列: 直後に押されたキーのランキング（上位3位）
  - **データ更新機能**: 手動更新ボタンによる最新データの反映
  - **データエクスポート機能**: JSON/CSV形式での統計データ出力
  - **レスポンシブレイアウト**: ウィンドウサイズに応じたカード配置の調整
  - **テーマ対応**: ダーク/ライトモードでの適切な色彩表示

### FR-05: グラフ表示
- **説明**: データの視覚的表示
- **要件**:
  - キー使用頻度の棒グラフ/円グラフ
  - 時系列グラフ（時間別使用パターン）
  - キーボードヒートマップ
  - インタラクティブな操作（ズーム、フィルタ）

### FR-06: 設定管理
- **説明**: アプリケーションの各種設定
- **要件**:
  - 記録設定（間隔、除外アプリ）
  - 表示設定（テーマ、フォント）
  - 通知設定（アラート、レポート）
  - エクスポート設定（形式、保存先）

### FR-07: システムトレイ
- **説明**: 最小化時の操作
- **要件**:
  - システムトレイアイコン表示
  - 右クリックメニュー（開始/停止/表示/終了）
  - 通知機能（重要イベント）

### FR-08: データエクスポート
- **説明**: 統計データの外部出力
- **要件**:
  - JSON, CSV, Excel形式対応
  - 全データエクスポート（累積統計）
  - グラフ画像エクスポート（PNG, SVG）

## 非機能要件

### NFR-01: パフォーマンス
- **起動時間**: 5秒以内
- **応答時間**: UI操作に対して1秒以内の応答
- **メモリ使用量**: 常駐時50MB以下
- **CPU使用率**: アイドル時1%以下

### NFR-02: 安定性
- **連続動作**: 24時間以上の安定動作
- **異常終了**: 予期しない終了時のデータ保護
- **リソース管理**: メモリリーク防止

### NFR-03: ユーザビリティ
- **学習コスト**: 初回使用時にマニュアル不要
- **操作性**: 主要操作が3クリック以内
- **アクセシビリティ**: キーボード操作対応

### NFR-04: 互換性
- **OS**: Windows 10/11対応
- **Python**: 3.8以上
- **解像度**: 1024x768以上

### NFR-05: セキュリティ
- **プライバシー**: ローカルデータ保存のみ
- **権限**: 必要最小限の権限で動作
- **データ保護**: 個人情報の適切な取り扱い

## UI/UX要件

### UX-01: テーマシステム
- **Darkテーマ**: デフォルト、目に優しい配色
- **Lightテーマ**: 明るい環境用
- **カスタムテーマ**: アクセントカラー変更可能

### UX-02: レスポンシブデザイン
- **ウィンドウサイズ対応**: 各コンポーネントの適応的配置
- **解像度対応**: 高DPI環境での適切な表示

### UX-03: フィードバック
- **視覚的フィードバック**: ボタン押下、状態変化の明確な表示
- **音声フィードバック**: 重要なイベント時の音声通知（オプション）
- **進捗表示**: 長時間処理中の進捗バー

## 技術要件

### TR-01: アーキテクチャ
- **パターン**: MVC（Model-View-Controller）
- **分離**: GUI層とビジネスロジック層の分離
- **再利用**: 既存のCLI機能の活用

### TR-02: 依存関係
- **CustomTkinter**: GUI フレームワーク
- **matplotlib**: グラフ描画
- **pystray**: システムトレイ
- **Pillow**: 画像処理

### TR-03: データ連携
- **既存データ**: 現在のJSON形式データとの完全互換
- **リアルタイム更新**: GUI表示の自動更新
- **並行処理**: GUI と記録処理の独立動作

## 制約条件

### C-01: 既存システム
- **後方互換性**: 既存のCLI機能を維持
- **データ互換性**: 現在のデータ形式を変更不可
- **設定互換性**: 既存の設定ファイルとの互換性

### C-02: リソース制約
- **開発期間**: 2-3ヶ月
- **追加依存**: 軽量なライブラリのみ使用
- **配布サイズ**: インストーラー50MB以下

### C-03: 運用制約
- **自動更新**: 将来的な機能追加に対応
- **設定移行**: バージョンアップ時の設定継承
- **データ移行**: 過去データの確実な引き継ぎ

## 受け入れ基準

### AC-01: 機能完成度
- [ ] 既存CLI機能の100%GUI化
- [ ] すべての統計情報のグラフ表示
- [ ] 設定項目の完全なGUI操作
- [ ] エラーハンドリングの適切な実装

### AC-02: 品質基準
- [ ] ユニットテスト90%以上のカバレッジ
- [ ] 統合テストの全ケース通過
- [ ] ユーザビリティテストの完了
- [ ] パフォーマンステストの合格

### AC-03: ドキュメント
- [ ] ユーザーマニュアルの完成
- [ ] 開発者ドキュメントの整備
- [ ] APIドキュメントの作成
- [ ] トラブルシューティングガイド

## リスク分析

### R-01: 技術リスク
- **CustomTkinter習得**: 学習コストと開発遅延
- **グラフライブラリ統合**: matplotlib とtkinter の組み合わせ問題
- **対策**: プロトタイプ開発による事前検証

### R-02: パフォーマンスリスク
- **リアルタイム更新**: GUI更新による性能低下
- **大量データ**: 長期使用時のデータ量増大
- **対策**: 効率的な更新アルゴリズム、データ分割

### R-03: ユーザビリティリスク
- **複雑性**: 機能追加による操作複雑化
- **学習コスト**: 新規ユーザーの使用困難
- **対策**: ユーザーテスト、段階的機能公開
