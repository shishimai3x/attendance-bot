#!/usr/bin/env python3
"""
シンプル版 勤怠お知らせBot
判定ロジックを整理し、指定された出力形式に対応
"""

import os
import json
import re
from datetime import datetime, date, timedelta
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import pytz

class AttendanceBotClean:
    """シンプル版勤怠Bot"""
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    
    def __init__(self):
        """初期化"""
        self.spreadsheet_id = os.getenv('SPREADSHEET_ID', "1lSBogD5N-kqphr0Vc7aLKM2hhfwqliHpemjvWgIssOs")
        self.sheet_name = os.getenv('SHEET_NAME', "8月シフト")
        self.discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL', "https://discord.com/api/webhooks/1406517569778880583/uo-MxGcQ4qfNXhPb-FyDksMTmJLsGRqN37ms3ykzQuAAu-D85xn9tJs4m62kQYeEcLGp")
        
        # 名前対応表
        self.name_mapping = {
            "三上大慈": "三上大慈",
            "井上津留美": "井上つるみ",
            "伊藤正": "伊藤正",
            "林和紀": "林和紀",
            "水口佳代": "水口佳代",
            "みどり": "水口佳代",
            "石川翔太": "石川翔太",
            "藤川千秋": "藤川千秋",
            "三浦紘太": "三浦紘太",
            "台信明": "台信明",
            "大東希星": "大東希星",
            "小川えりこ": "小川枝里子",
            "小玉志穂": "小玉志穂",
            "徳瓜野": "徳瓜野",
            "永井柚葉": "永井柚葉",
            "谷口寿美子": "谷口寿美子",
            "貴志祐介": "貴志祐介",
            "近井美絵": "近井美絵",
            "鈴木友也": "鈴木友也",
            "高野香奈子": "高野香奈子"
        }
        
        # Google Sheets API認証
        self.service = self.authenticate()
    
    def authenticate(self):
        """Google Sheets API認証"""
        import base64
        creds = None
        try:
            # デバッグ情報
            print(f"GITHUB_ACTIONS環境変数: {os.getenv('GITHUB_ACTIONS')}")
            print(f"GOOGLE_OAUTH_TOKEN環境変数: {'設定済み' if os.getenv('GOOGLE_OAUTH_TOKEN') else '未設定'}")
            # GitHub Actions環境では事前生成されたトークンを使用
            if os.getenv('GITHUB_ACTIONS') or os.getenv('CI'):
                print("GitHub Actions環境を検出")
                token_data = os.getenv('GOOGLE_OAUTH_TOKEN')
                if token_data and len(token_data) > 100:
                    print("事前生成トークンを使用")
                    token_bytes = base64.b64decode(token_data)
                    creds = pickle.loads(token_bytes)
                else:
                    print(f"トークンデータ: {token_data[:50] if token_data else 'None'}...")
                    raise Exception("GOOGLE_OAUTH_TOKEN環境変数が設定されていません")
            else:
                print("ローカル環境を検出")
                if os.path.exists('token.pickle'):
                    with open('token.pickle', 'rb') as token:
                        creds = pickle.load(token)
                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                    else:
                        client_config = json.loads(os.getenv('GOOGLE_OAUTH_CLIENT_CONFIG', '{}'))
                        if not client_config:
                            raise Exception("GOOGLE_OAUTH_CLIENT_CONFIG環境変数が設定されていません")
                        print("ブラウザ認証を開始")
                        flow = InstalledAppFlow.from_client_config(client_config, self.SCOPES)
                        creds = flow.run_local_server(port=0)
                    with open('token.pickle', 'wb') as token:
                        pickle.dump(creds, token)
            service = build('sheets', 'v4', credentials=creds)
            print("Google Sheets API認証成功")
            return service
        except Exception as e:
            print(f"Google Sheets API認証エラー: {e}")
            raise
    
    def get_sheet_data(self):
        """シートデータを取得"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!A:ZZ"
            ).execute()
            # 背景色情報も取得
            result_with_colors = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id,
                ranges=f"{self.sheet_name}!A:ZZ",
                fields='sheets(data(rowData(values(effectiveFormat/backgroundColor))))'
            ).execute()
            return result.get('values', []), result_with_colors
        except Exception as e:
            print(f"シートデータ取得エラー: {e}")
            raise
    
    def find_today_column(self, data):
        """今日の列を探す（JST基準）"""
        jst = pytz.timezone('Asia/Tokyo')
        today = datetime.now(jst).date()
        # 行2（日付行）をチェック
        if len(data) < 2:
            return None
        date_row = data[1]  # 行2（0ベースなので1）
        # 今日の日付形式
        date_formats = [
            today.strftime('%m/%d'),      # 8/17
            today.strftime('%d'),         # 17
        ]
        for col_idx, cell in enumerate(date_row):
            if not cell:
                continue
            cell_str = str(cell).strip()
            # 各日付形式でチェック
            for date_format in date_formats:
                if date_format in cell_str:
                    print(f"今日の列を発見: 列{col_idx+1} ({cell_str})")
                    return col_idx
        print("今日の列が見つかりませんでした")
        return None
    
    def get_cell_background_color(self, row_data, col_index):
        """セルの背景色を取得"""
        try:
            if not row_data or col_index >= len(row_data):
                return None
            
            cell_data = row_data[col_index]
            if not cell_data or 'effectiveFormat' not in cell_data:
                return None
            
            bg_color = cell_data['effectiveFormat']['backgroundColor']
            return bg_color
            
        except Exception as e:
            return None
    
    def is_green_color(self, bg_color):
        """緑色かどうかを判定"""
        if not bg_color:
            return False
        
        # RGB値で判定
        red = bg_color.get('red', 0)
        green = bg_color.get('green', 0)
        blue = bg_color.get('blue', 0)
        
        # 緑色の判定（実際の色に合わせて調整）
        green_conditions = [
            green > 0.4 and red < 0.4 and blue < 0.4,  # 標準的な緑
            green > 0.6 and red < 0.3 and blue < 0.3,  # 濃い緑
            green > 0.5 and red < 0.2 and blue < 0.2,  # 明るい緑
            green > 0.7 and red < 0.6 and blue < 0.5,  # 実際のスプレッドシートの緑色
            green > red and green > blue and green > 0.5,  # より柔軟な緑色判定
        ]
        
        return any(green_conditions)
    
    def classify_attendance(self, cell_value, bg_color):
        """勤怠を分類（OFFでなくセルに何か文字列があれば出社、その内容を表示）"""
        if not cell_value or str(cell_value).strip() == '':
            return 'off'
        cell_str = str(cell_value).strip()
        # 緑色の背景 → リモート
        if self.is_green_color(bg_color):
            return 'remote'
        # OFF・休み系ワードが含まれていれば休み
        off_patterns = ['OFF', '休', '休み', '休暇', '有給', '欠勤']
        for pattern in off_patterns:
            if pattern.upper() in cell_str.upper():
                return 'off'
        # それ以外で何か文字列があれば出社
        return 'onsite'
    
    def to_discord_name(self, sheet_name):
        """シフト表名をDiscord名に変換"""
        if not sheet_name:
            return None
        
        # 空白除去
        sheet_name = str(sheet_name).strip()
        
        # 対応表に存在する場合は変換
        if sheet_name in self.name_mapping:
            return self.name_mapping[sheet_name]
        
        # 対応表にない場合はそのまま返す
        return sheet_name
    
    def process_attendance(self):
        """勤怠情報を処理"""
        try:
            print("=== 勤怠情報処理開始 ===")
            
            # シートデータを取得
            data, color_data = self.get_sheet_data()
            
            if not data or len(data) < 4:
                raise Exception("シートデータが取得できませんでした")
            
            # 今日の列を探す（行2から）
            today_col = self.find_today_column(data)
            
            if today_col is None:
                raise Exception("今日の列が見つかりませんでした")
            
            # 名前列は列1（固定）
            name_col = 0
            
            # 背景色データを取得
            color_rows = []
            if 'sheets' in color_data and color_data['sheets']:
                sheet_data = color_data['sheets'][0]
                if 'data' in sheet_data and sheet_data['data']:
                    color_rows = sheet_data['data'][0].get('rowData', [])
            
            # 各行を処理（行4以降）
            onsite_people = []
            remote_people = []
            
            for row_idx, row in enumerate(data[3:], start=3):  # 行4以降（0ベースなので3）
                if len(row) <= max(today_col, name_col):
                    continue
                
                # 名前を取得
                name = row[name_col] if name_col < len(row) else None
                if not name:
                    continue
                
                # 今日のセルの値を取得
                today_cell = row[today_col] if today_col < len(row) else None
                
                # 背景色を取得
                bg_color = None
                if row_idx < len(color_rows) and color_rows[row_idx]:
                    row_data = color_rows[row_idx].get('values', [])
                    bg_color = self.get_cell_background_color(row_data, today_col)
                
                # 勤怠を分類
                attendance_type = self.classify_attendance(today_cell, bg_color)
                
                # Discord名に変換
                discord_name = self.to_discord_name(name)
                
                print(f"  {name} -> {discord_name}: {today_cell} ({attendance_type})")
                
                # データを追加（OFFは無視）
                if attendance_type == 'onsite':
                    # 注記がある場合は時間に含める
                    time_with_note = str(today_cell) if today_cell else ''
                    onsite_people.append({
                        'name': discord_name,
                        'time': time_with_note
                    })
                elif attendance_type == 'remote':
                    # 注記がある場合は時間に含める
                    time_with_note = str(today_cell) if today_cell else ''
                    remote_people.append({
                        'name': discord_name,
                        'time': time_with_note
                    })
            
            print(f"出社: {len(onsite_people)}人")
            print(f"リモート: {len(remote_people)}人")
            
            return {
                'onsite': onsite_people,
                'remote': remote_people
            }
            
        except Exception as e:
            print(f"勤怠情報処理エラー: {e}")
            raise
    
    def generate_text_output(self, attendance_data):
        """テキスト出力を生成（指定された形式, JST基準の日付）"""
        jst = pytz.timezone('Asia/Tokyo')
        today = datetime.now(jst).strftime('%m/%d')
        text_lines = [
            f"## {today} 本日の勤怠情報 (ざっくりシフトより)",
        ]
        
        # 出社
        if attendance_data['onsite']:
            text_lines.append("### 🏢 出社")
            text_lines.append("```")
            # 最長の名前を取得して時間の開始位置を決定
            max_name_length = max(len(person['name']) for person in attendance_data['onsite'])
            for person in attendance_data['onsite']:
                name = person['name']
                time = self.format_time(person['time'])
                # 名前の後に適切な空白を追加して時間を揃える
                padding = " " * (max_name_length - len(name) + 2)
                text_lines.append(f"  {name}{padding}{time}")
            text_lines.append("```")
        
        # リモート
        if attendance_data['remote']:
            text_lines.append("### 🏠 リモート")
            text_lines.append("```")
            # 最長の名前を取得して時間の開始位置を決定
            max_name_length = max(len(person['name']) for person in attendance_data['remote'])
            for person in attendance_data['remote']:
                name = person['name']
                time = self.format_time(person['time'])
                # 名前の後に適切な空白を追加して時間を揃える
                padding = " " * (max_name_length - len(name) + 2)
                text_lines.append(f"  {name}{padding}{time}")
            text_lines.append("```")
        
        # 合計
        total = len(attendance_data['onsite']) + len(attendance_data['remote'])
        text_lines.append(f"**合計: {total}人**")
        
        return "\n".join(text_lines)
    
    def format_time(self, time_str):
        """時:分までの正規化のみ行い、バグが起きないようにする。"""
        if not time_str:
            return ""
        s = str(time_str).strip()
        # OFF・休み系ワードなら空文字
        off_patterns = ['OFF', '休', '休み', '休暇', '有給', '欠勤']
        for pattern in off_patterns:
            if pattern.upper() in s.upper():
                return ""
        import re
        # 区切り記号を統一
        s = s.replace('～', '-').replace('~', '-').replace('：', ':')
        # 秒を含む場合は切り捨て（例: 09:00:00 → 09:00）
        s = re.sub(r':(\d{2}):\d{2}', r':\1', s)
        # 9 → 09:00
        if re.fullmatch(r'\d{1,2}', s):
            return f"{int(s):02d}:00"
        # 9:30 → 09:30
        if re.fullmatch(r'\d{1,2}:\d{2}', s):
            h, m = s.split(':')
            return f"{int(h):02d}:{int(m):02d}"
        # 9-18 → 09:00-18:00
        m = re.fullmatch(r'(\d{1,2})-(\d{1,2})', s)
        if m:
            return f"{int(m.group(1)):02d}:00-{int(m.group(2)):02d}:00"
        # 9:30-18 → 09:30-18:00
        m = re.fullmatch(r'(\d{1,2}:\d{2})-(\d{1,2})', s)
        if m:
            h1, m1 = m.group(1).split(':')
            return f"{int(h1):02d}:{int(m1):02d}-{int(m.group(2)):02d}:00"
        # 9-18:30 → 09:00-18:30
        m = re.fullmatch(r'(\d{1,2})-(\d{1,2}:\d{2})', s)
        if m:
            h2, m2 = m.group(2).split(':')
            return f"{int(m.group(1)):02d}:00-{int(h2):02d}:{int(m2):02d}"
        # 9:30-18:30 → 09:30-18:30
        m = re.fullmatch(r'(\d{1,2}:\d{2})-(\d{1,2}:\d{2})', s)
        if m:
            h1, m1 = m.group(1).split(':')
            h2, m2 = m.group(2).split(':')
            return f"{int(h1):02d}:{int(m1):02d}-{int(h2):02d}:{int(m2):02d}"
        # 9:30/13:00-18:00 → 09:30/13:00-18:00（複雑なパターンはそのまま返す）
        return s
    
    def send_to_discord(self, text):
        """Discordに送信"""
        try:
            # DiscordのMarkdownを確実に有効にするためにembedsを使用
            payload = {
                "embeds": [
                    {
                        "description": text,
                        "color": 0x00ff00  # 緑色
                    }
                ]
            }
            
            response = requests.post(self.discord_webhook_url, json=payload)
            
            if response.status_code == 204:
                print("Discordへの送信が成功しました")
                return True
            else:
                print(f"Discord送信エラー: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Discord送信エラー: {e}")
            return False
    
    def run(self):
        """メイン処理を実行"""
        try:
            print("=== シンプル版勤怠お知らせBot開始 ===")
            
            # 勤怠情報を処理
            attendance_data = self.process_attendance()
            
            # テキスト出力を生成
            text_output = self.generate_text_output(attendance_data)
            
            # Discordに送信
            success = self.send_to_discord(text_output)
            
            if success:
                print("=== 処理完了 ===")
                return True
            else:
                print("=== 送信失敗 ===")
                return False
                
        except Exception as e:
            print(f"処理実行エラー: {e}")
            return False

# メイン実行
if __name__ == "__main__":
    bot = AttendanceBotClean()
    bot.run()
