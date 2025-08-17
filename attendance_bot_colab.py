#!/usr/bin/env python3
"""
Google Colab用 勤怠お知らせBot
毎日10:30に自動実行されることを想定
"""

import os
import json
import re
from datetime import datetime, date
import requests
from google.colab import auth
from googleapiclient.discovery import build
import pandas as pd

class AttendanceBotColab:
    """Google Colab用勤怠Bot"""
    
    def __init__(self):
        """初期化"""
        self.spreadsheet_id = "1lSBogD5N-kqphr0Vc7aLKM2hhfwqliHpemjvWgIssOs"
        self.sheet_name = "8月シフト"
        self.discord_webhook_url = "https://discord.com/api/webhooks/1406517569778880583/uo-MxGcQ4qfNXhPb-FyDksMTmJLsGRqN37ms3ykzQuAAu-D85xn9tJs4m62kQYeEcLGp"
        
        # 名前対応表
        self.name_mapping = {
            "三上大慈": "三上大慈",
            "井上津留美": "井上つるみ",
            "伊藤正": "伊藤正",
            "林和紀": "林和紀",
            "水口佳代": "水口佳代",
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
        auth.authenticate_user()
        self.service = build('sheets', 'v4')
    
    def get_sheet_data(self):
        """シートデータを取得"""
        try:
            # データ取得
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!A:Z"
            ).execute()
            
            # 背景色情報も取得
            result_with_colors = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id,
                ranges=f"{self.sheet_name}!A:Z",
                fields='sheets(data(rowData(values(effectiveFormat/backgroundColor))))'
            ).execute()
            
            return result.get('values', []), result_with_colors
            
        except Exception as e:
            print(f"シートデータ取得エラー: {e}")
            raise
    
    def find_today_column(self, header_row):
        """今日の列を探す"""
        today = date.today()
        
        # 複数の日付形式を試す
        date_formats = [
            today.strftime('%m/%d'),      # 8/17
            today.strftime('%Y-%m-%d'),   # 2025-08-17
            today.strftime('%Y/%m/%d'),   # 2025/08/17
            today.strftime('%m月%d日'),    # 8月17日
            today.strftime('%d日'),       # 17日
        ]
        
        for i, cell in enumerate(header_row):
            if not cell:
                continue
            
            cell_str = str(cell).strip()
            
            # 各日付形式でチェック
            for date_format in date_formats:
                if date_format in cell_str:
                    print(f"今日の列を発見: 列{i+1} ({cell_str})")
                    return i
            
            # 正規表現で日付パターンをチェック
            date_patterns = [
                r'\d{1,2}/\d{1,2}',           # 8/17
                r'\d{4}-\d{1,2}-\d{1,2}',     # 2025-08-17
                r'\d{4}/\d{1,2}/\d{1,2}',     # 2025/08/17
                r'\d{1,2}月\d{1,2}日',        # 8月17日
                r'\d{1,2}日',                  # 17日
            ]
            
            for pattern in date_patterns:
                if re.search(pattern, cell_str):
                    print(f"今日の列を発見: 列{i+1} ({cell_str})")
                    return i
        
        print("今日の列が見つかりませんでした")
        return None
    
    def find_name_column(self, data, max_check_rows=10):
        """名前の列を探す"""
        if not data or len(data) < 2:
            return 0
        
        # 最初の数行をチェック
        check_rows = min(max_check_rows, len(data))
        
        # 各列の「名前らしさ」をスコア化
        column_scores = {}
        
        for col in range(min(3, len(data[0]) if data[0] else 0)):
            score = 0
            name_count = 0
            
            for row in range(1, check_rows):  # ヘッダー行を除く
                if row < len(data) and col < len(data[row]):
                    cell = data[row][col]
                    if cell and str(cell).strip():
                        cell_str = str(cell).strip()
                        
                        # 名前らしい特徴をチェック
                        if len(cell_str) >= 2 and len(cell_str) <= 10:
                            score += 1
                        if re.match(r'^[ぁ-んァ-ン一-龯a-zA-Z\s]+$', cell_str):
                            score += 2
                        if not re.search(r'\d', cell_str):
                            score += 1
                        
                        name_count += 1
            
            if name_count > 0:
                column_scores[col] = score / name_count
        
        # 最もスコアの高い列を選択
        if column_scores:
            best_column = max(column_scores, key=column_scores.get)
            print(f"名前の列を特定: 列{best_column+1}")
            return best_column
        
        print("名前の列を特定できませんでした。列0を使用します")
        return 0
    
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
            print(f"背景色取得エラー: {e}")
            return None
    
    def is_green_color(self, bg_color):
        """緑色かどうかを判定"""
        if not bg_color:
            return False
        
        # RGB値で判定
        red = bg_color.get('red', 0)
        green = bg_color.get('green', 0)
        blue = bg_color.get('blue', 0)
        
        # 緑色の判定（緑が強く、赤と青が弱い）
        return green > 0.5 and red < 0.3 and blue < 0.3
    
    def is_gray_color(self, bg_color):
        """灰色かどうかを判定"""
        if not bg_color:
            return False
        
        # RGB値で判定
        red = bg_color.get('red', 0)
        green = bg_color.get('green', 0)
        blue = bg_color.get('blue', 0)
        
        # 灰色の判定（RGB値が近い）
        return abs(red - green) < 0.1 and abs(green - blue) < 0.1 and abs(red - blue) < 0.1
    
    def classify_attendance(self, cell_value, bg_color):
        """勤怠を分類"""
        if not cell_value:
            return 'off'
        
        cell_str = str(cell_value).strip().upper()
        
        # 緑色の背景 → リモート
        if self.is_green_color(bg_color):
            return 'remote'
        
        # 灰色の背景 → 休み
        if self.is_gray_color(bg_color):
            return 'off'
        
        # "OFF" または空欄 → 休み
        if cell_str in ['OFF', '休', '休み', '']:
            return 'off'
        
        # 時間パターンのチェック（出社）
        time_patterns = [
            r'\d{1,2}:\d{2}-\d{1,2}:\d{2}',  # 9:30-18:30
            r'\d{1,2}-\d{1,2}',              # 9-18
            r'\d{1,2}:\d{2}',                # 9:30
            r'\d{1,2}時',                    # 9時
        ]
        
        for pattern in time_patterns:
            if re.search(pattern, cell_str):
                return 'onsite'
        
        # 数字のみの場合も出社として扱う
        if re.match(r'^\d+$', cell_str):
            return 'onsite'
        
        # その他は不明
        return 'unknown'
    
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
            print("勤怠情報の処理を開始...")
            
            # シートデータを取得
            data, color_data = self.get_sheet_data()
            
            if not data or len(data) < 2:
                raise Exception("シートデータが取得できませんでした")
            
            # 今日の列を探す
            header_row = data[0]
            today_col = self.find_today_column(header_row)
            
            if today_col is None:
                raise Exception("今日の列が見つかりませんでした")
            
            # 名前の列を探す
            name_col = self.find_name_column(data)
            
            # 背景色データを取得
            color_rows = []
            if 'sheets' in color_data and color_data['sheets']:
                sheet_data = color_data['sheets'][0]
                if 'data' in sheet_data and sheet_data['data']:
                    color_rows = sheet_data['data'][0].get('rowData', [])
            
            # 各行を処理
            attendance_data = {
                'onsite': [],
                'remote': [],
                'unknown': [],
                'processed_at': datetime.now().isoformat(),
                'total_people': 0
            }
            
            for row_idx, row in enumerate(data[1:], start=1):  # ヘッダー行を除く
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
                
                # データを追加
                person_data = {
                    'sheet_name': str(name),
                    'discord_name': discord_name,
                    'cell_value': str(today_cell) if today_cell else '',
                    'attendance_type': attendance_type
                }
                
                if attendance_type != 'off':
                    attendance_data[attendance_type].append(person_data)
                    attendance_data['total_people'] += 1
            
            print(f"勤怠情報処理完了: 出社{len(attendance_data['onsite'])}人, リモート{len(attendance_data['remote'])}人, 不明{len(attendance_data['unknown'])}人")
            
            return attendance_data
            
        except Exception as e:
            print(f"勤怠情報処理エラー: {e}")
            raise
    
    def generate_text_output(self, attendance_data):
        """テキスト出力を生成"""
        today = datetime.now().strftime('%Y年%m月%d日')
        
        text_lines = [
            f"📅 **{today}の勤怠情報**",
            "",
        ]
        
        # 出社
        if attendance_data['onsite']:
            text_lines.append("🏢 **出社**")
            for person in attendance_data['onsite']:
                text_lines.append(f"• {person['discord_name']} ({person['cell_value']})")
            text_lines.append("")
        
        # リモート
        if attendance_data['remote']:
            text_lines.append("🏠 **リモート**")
            for person in attendance_data['remote']:
                text_lines.append(f"• {person['discord_name']}")
            text_lines.append("")
        
        # 不明
        if attendance_data['unknown']:
            text_lines.append("❓ **不明**")
            for person in attendance_data['unknown']:
                text_lines.append(f"• {person['discord_name']} ({person['cell_value']})")
            text_lines.append("")
        
        # 合計
        text_lines.append(f"📊 **合計: {attendance_data['total_people']}人**")
        
        return "\n".join(text_lines)
    
    def send_to_discord(self, text):
        """Discordに送信"""
        try:
            payload = {
                "content": text
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
            print("=== 勤怠お知らせBot開始 ===")
            
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
    bot = AttendanceBotColab()
    bot.run()
