# クラウド上での永続運用ガイド

## 🎯 目標
- 個人アカウントを使用
- 無料で継続運用
- 毎日10:30に自動実行
- 誰かのPCに依存しない

## 📋 推奨方法

### 1. GitHub Actions（最推奨）

#### メリット
- 完全無料（月2000分まで）
- 設定が簡単
- 信頼性が高い
- ログが確認できる

#### セットアップ手順

1. **GitHubリポジトリを作成**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/attendance-bot.git
   git push -u origin main
   ```

2. **GitHub Secretsを設定**
   - リポジトリのSettings → Secrets and variables → Actions
   - 以下のSecretsを追加：
     - `SPREADSHEET_ID`: スプレッドシートID
     - `SHEET_NAME`: シート名
     - `DISCORD_WEBHOOK_URL`: Discord Webhook URL
     - `GOOGLE_SERVICE_ACCOUNT_KEY`: サービスアカウントキーのJSON

3. **サービスアカウントキーの取得**
   - Google Cloud Consoleでサービスアカウントを作成
   - JSONキーをダウンロード
   - スプレッドシートをサービスアカウントと共有

4. **自動実行の確認**
   - Actionsタブでワークフローの実行状況を確認
   - 手動実行も可能（workflow_dispatch）

### 2. Google Colab + 外部スケジューラー

#### メリット
- Google Colabは無料
- 個人アカウントで認証可能
- コードの変更が簡単

#### セットアップ手順

1. **Google Colabでノートブックを作成**
   - `attendance_bot_colab.ipynb`をアップロード
   - 必要なライブラリをインストール
   - Google認証を実行

2. **外部スケジューラーの設定**
   - **cron-job.org**（無料）
   - **UptimeRobot**（無料）
   - **GitHub Actions**でColabを呼び出す

3. **Colabの自動実行設定**
   ```python
   # ノートブックの最後に追加
   from google.colab import runtime
   runtime.raise_for_unexpected_disconnects()
   ```

### 3. Heroku（有料だが安定）

#### メリット
- 24時間稼働
- 設定が簡単
- ログが確認できる

#### セットアップ手順

1. **Herokuアカウント作成**
2. **Heroku CLIインストール**
3. **アプリケーション作成**
4. **環境変数設定**
5. **デプロイ**

## 🔧 詳細設定

### GitHub Actions設定

```yaml
# .github/workflows/attendance_bot.yml
name: 勤怠お知らせBot

on:
  schedule:
    # 毎日10:30に実行（JST）
    - cron: '30 1 * * *'
  workflow_dispatch:  # 手動実行も可能

jobs:
  attendance-bot:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib pandas python-dotenv requests
    
    - name: Run attendance bot
      env:
        SPREADSHEET_ID: ${{ secrets.SPREADSHEET_ID }}
        SHEET_NAME: ${{ secrets.SHEET_NAME }}
        DISCORD_WEBHOOK_URL: ${{ secrets.DISCORD_WEBHOOK_URL }}
        GOOGLE_SERVICE_ACCOUNT_KEY: ${{ secrets.GOOGLE_SERVICE_ACCOUNT_KEY }}
      run: |
        python attendance_bot_github.py
```

### Google Colab設定

```python
# 自動実行用のセル
import schedule
import time
from datetime import datetime

def run_bot():
    print(f"実行時刻: {datetime.now()}")
    bot.run()

# 毎日10:30に実行
schedule.every().day.at("10:30").do(run_bot)

# スケジューラーを開始
while True:
    schedule.run_pending()
    time.sleep(60)
```

## 🚀 運用開始

### 1. テスト実行
```bash
# ローカルでテスト
python test_attendance.py

# GitHub Actionsでテスト
# Actionsタブから手動実行
```

### 2. 監視設定
- Discordで通知の確認
- GitHub Actionsのログ確認
- エラー時のアラート設定

### 3. メンテナンス
- 月1回の動作確認
- 名前対応表の更新
- スプレッドシートの形式変更対応

## 🔍 トラブルシューティング

### よくある問題

1. **認証エラー**
   - サービスアカウントキーの確認
   - スプレッドシートの共有設定確認

2. **実行時間エラー**
   - cron設定の確認
   - タイムゾーンの確認

3. **Discord送信エラー**
   - Webhook URLの確認
   - ネットワーク接続の確認

### ログ確認方法

```bash
# GitHub Actions
# Actionsタブ → ワークフロー → ジョブ → ログ

# Google Colab
# 実行ログを確認

# ローカル
python attendance_bot_github.py
```

## 📊 運用コスト

| サービス | 月額コスト | 制限 |
|---------|-----------|------|
| GitHub Actions | 無料 | 月2000分 |
| Google Colab | 無料 | 12時間/日 |
| Heroku | $7/月 | 24時間稼働 |
| cron-job.org | 無料 | 月250回 |

## 🎯 推奨構成

**最適な構成：GitHub Actions**
- 完全無料
- 信頼性が高い
- 設定が簡単
- ログが確認できる

**代替構成：Google Colab + cron-job.org**
- 個人アカウントで認証
- 完全無料
- コード変更が簡単
