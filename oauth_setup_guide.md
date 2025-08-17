# GitHub Actions + 個人認証 設定ガイド

## 🎯 概要

GitHub Actions + 個人認証（OAuth 2.0）を使用して、サービスアカウントなしで勤怠botを運用する方法です。

**メリット：**
- ✅ 完全無料（月2000分まで）
- ✅ 個人アカウントで認証
- ✅ サービスアカウント不要
- ✅ 完全自動化
- ✅ ログが確認できる

## 🔧 詳細設定手順

### 1. Google Cloud Console設定

#### 1.1 プロジェクト作成
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成（例：`attendance-bot-oauth`）
3. プロジェクトを選択

#### 1.2 OAuth同意画面の設定
1. **APIとサービス** → **OAuth同意画面** を選択
2. **外部**を選択
3. 以下の情報を入力：
   - **アプリ名**: `勤怠お知らせBot`
   - **ユーザーサポートメール**: 自分のメールアドレス
   - **開発者連絡先情報**: 自分のメールアドレス
4. **保存して続行**をクリック
5. **スコープ**で「Google Sheets API」を追加
6. **テストユーザー**で自分のメールアドレスを追加
7. **保存して続行**をクリック

#### 1.3 認証情報の作成
1. **APIとサービス** → **認証情報** を選択
2. **認証情報を作成** → **OAuth 2.0 クライアントID** を選択
3. **アプリケーションの種類**で「デスクトップアプリ」を選択
4. **名前**: `attendance-bot-desktop`
5. **作成**をクリック
6. **JSONをダウンロード**をクリック

#### 1.4 Google Sheets API有効化
1. **APIとサービス** → **ライブラリ** を選択
2. **Google Sheets API**を検索
3. **有効にする**をクリック

### 2. ダウンロードしたJSONファイルの確認

ダウンロードしたJSONファイルを開いて、以下のような内容になっていることを確認：

```json
{
  "installed": {
    "client_id": "your-client-id.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "your-client-secret",
    "redirect_uris": ["http://localhost"]
  }
}
```

### 3. GitHub Secrets設定

1. [GitHubリポジトリ](https://github.com/shishimai3x/attendance-bot)にアクセス
2. **Settings** → **Secrets and variables** → **Actions**
3. **New repository secret**をクリックして以下を追加：

| Secret名 | 値 |
|---------|-----|
| `SPREADSHEET_ID` | `1lSBogD5N-kqphr0Vc7aLKM2hhfwqliHpemjvWgIssOs` |
| `SHEET_NAME` | `8月シフト` |
| `DISCORD_WEBHOOK_URL` | `https://discord.com/api/webhooks/1406517569778880583/uo-MxGcQ4qfNXhPb-FyDksMTmJLsGRqN37ms3ykzQuAAu-D85xn9tJs4m62kQYeEcLGp` |
| `GOOGLE_OAUTH_CLIENT_CONFIG` | ダウンロードしたJSONファイルの**全体の内容** |

### 4. 初回認証の実行

1. **Actions**タブに移動
2. **勤怠お知らせBot（個人認証版）**ワークフローを選択
3. **Run workflow**ボタンをクリック
4. 初回実行時に認証エラーが発生する可能性があります（正常です）

### 5. ローカルでの初回認証（推奨）

GitHub Actionsでの初回認証は複雑なため、ローカルで初回認証を行い、トークンをGitHub Secretsに設定することを推奨します。

#### 5.1 ローカル環境での認証
```bash
# 仮想環境を作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係をインストール
pip install -r requirements.txt

# 環境変数を設定
export SPREADSHEET_ID="1lSBogD5N-kqphr0Vc7aLKM2hhfwqliHpemjvWgIssOs"
export SHEET_NAME="8月シフト"
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/1406517569778880583/uo-MxGcQ4qfNXhPb-FyDksMTmJLsGRqN37ms3ykzQuAAu-D85xn9tJs4m62kQYeEcLGp"
export GOOGLE_OAUTH_CLIENT_CONFIG='{"installed":{"client_id":"...","project_id":"...","auth_uri":"...","token_uri":"...","auth_provider_x509_cert_url":"...","client_secret":"...","redirect_uris":["http://localhost"]}}'

# 認証実行
python attendance_bot_oauth.py
```

#### 5.2 生成されたトークンの確認
認証が成功すると、`token.pickle`ファイルが生成されます。

#### 5.3 トークンをGitHub Secretsに設定
`token.pickle`ファイルの内容をBase64エンコードして、`GOOGLE_OAUTH_TOKEN`としてGitHub Secretsに設定：

```bash
# Base64エンコード
base64 -i token.pickle
```

| Secret名 | 値 |
|---------|-----|
| `GOOGLE_OAUTH_TOKEN` | Base64エンコードされたトークン |

### 6. 自動実行の確認

設定が完了すると、毎日10:30（JST）に自動で実行されるようになります。

## 🔍 トラブルシューティング

### よくある問題

1. **認証エラー**
   - OAuth同意画面の設定を確認
   - テストユーザーに自分のメールアドレスが追加されているか確認
   - スコープにGoogle Sheets APIが含まれているか確認

2. **トークンエラー**
   - ローカルで初回認証を実行
   - 生成されたトークンをGitHub Secretsに設定

3. **権限エラー**
   - スプレッドシートが自分のアカウントで共有されているか確認

### ログ確認

- **GitHub Actions**: Actionsタブ → ワークフロー → ジョブ → ログ
- **ローカル**: `python attendance_bot_oauth.py`

## 🎯 メリット

- **完全無料**: GitHub Actionsの月2000分まで無料
- **個人認証**: サービスアカウント不要
- **自動化**: 毎日10:30に自動実行
- **ログ確認**: 実行状況を詳細に確認可能
- **手動実行**: いつでも手動でテスト実行可能

これで、個人アカウントで完結した永続的な勤怠botが完成します！
