# 勤怠お知らせBot

毎朝10:30にGoogleスプレッドシートから勤怠情報を読み取り、Discordに送信するbotです。

## 🎯 特徴

- **完全無料で永続運用**: GitHub Actionsを使用
- **個人アカウント対応**: サービスアカウント不要
- **自動実行**: 毎日10:30に自動送信
- **クラウド運用**: 誰かのPCに依存しない

## 🚀 クイックスタート

### 1. GitHub Actions（推奨）

1. **リポジトリをフォーク**
   ```bash
   git clone https://github.com/yourusername/attendance-bot.git
   cd attendance-bot
   ```

2. **GitHub Secretsを設定**
   - リポジトリのSettings → Secrets and variables → Actions
   - 以下のSecretsを追加：
     - `SPREADSHEET_ID`: スプレッドシートID
     - `SHEET_NAME`: シート名（例：8月シフト）
     - `DISCORD_WEBHOOK_URL`: Discord Webhook URL
     - `GOOGLE_SERVICE_ACCOUNT_KEY`: サービスアカウントキーのJSON

3. **自動実行開始**
   - 毎日10:30（JST）に自動実行
   - Actionsタブで手動実行も可能

### 2. Google Colab（代替）

1. **ノートブックをアップロード**
   - `attendance_bot_colab.ipynb`をGoogle Colabにアップロード

2. **認証実行**
   - セルを順番に実行
   - Google認証を完了

3. **外部スケジューラー設定**
   - cron-job.orgで毎日10:30に実行

## 📋 機能

- Googleスプレッドシートから今日の勤怠情報を自動取得
- 出社・リモート・休みを自動分類
- Discord名への変換
- 毎朝10:30に自動送信

## 🔧 セットアップ

### Google Sheets API設定

1. [Google Cloud Console](https://console.cloud.google.com/)でプロジェクト作成
2. Google Sheets APIを有効化
3. サービスアカウントキーを作成
4. スプレッドシートをサービスアカウントと共有

### Discord Webhook設定

1. Discordサーバーの設定→「統合機能」→「Webhook」
2. 新しいWebhookを作成
3. Webhook URLをコピー

## 📁 ファイル構成

```
attendance-bot/
├── .github/workflows/          # GitHub Actions設定
│   └── attendance_bot.yml
├── attendance_bot_github.py    # GitHub Actions用メインスクリプト
├── attendance_bot_colab.py     # Google Colab用スクリプト
├── attendance_bot_colab.ipynb  # Google Colab用ノートブック
├── config.py                   # 設定管理
├── sheet_reader.py            # Google Sheets読み取り
├── name_mapper.py             # 名前変換
├── attendance_processor.py    # 勤怠情報処理
├── test_attendance.py         # テストスクリプト
├── requirements.txt           # 依存関係
├── name_mapping.csv           # 名前対応表
├── setup_guide.md             # 詳細セットアップガイド
├── cloud_deployment_guide.md  # クラウド運用ガイド
└── README.md                  # このファイル
```

## 🎯 運用方法

### GitHub Actions（推奨）

- **完全無料**: 月2000分まで無料
- **自動実行**: 毎日10:30（JST）
- **ログ確認**: Actionsタブで実行状況を確認
- **手動実行**: いつでも手動で実行可能

### Google Colab + 外部スケジューラー

- **個人認証**: サービスアカウント不要
- **無料運用**: Google Colabは無料
- **簡単編集**: コード変更が簡単

## 🔍 トラブルシューティング

### よくある問題

1. **認証エラー**
   - サービスアカウントキーの確認
   - スプレッドシートの共有設定確認

2. **実行時間エラー**
   - cron設定の確認（`30 1 * * *`）
   - タイムゾーンの確認（UTC）

3. **Discord送信エラー**
   - Webhook URLの確認
   - ネットワーク接続の確認

### ログ確認

```bash
# GitHub Actions
# Actionsタブ → ワークフロー → ジョブ → ログ

# ローカルテスト
python test_attendance.py
```

## 📊 運用コスト

| サービス | 月額コスト | 制限 |
|---------|-----------|------|
| GitHub Actions | 無料 | 月2000分 |
| Google Colab | 無料 | 12時間/日 |
| cron-job.org | 無料 | 月250回 |

## 🎯 推奨構成

**最適な構成：GitHub Actions**
- 完全無料
- 信頼性が高い
- 設定が簡単
- ログが確認できる

詳細な設定方法は `cloud_deployment_guide.md` を参照してください。

## 📝 ライセンス

MIT License

## 🤝 貢献

プルリクエストやイシューの報告を歓迎します！
