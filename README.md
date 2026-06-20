# HADAOJI PRINT 見積・請求アプリ v1

スマホから見積書・請求書PDFを作るためのStreamlit版です。

## 起動方法（Mac）

```bash
cd hadaoji_quote_streamlit_v1
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Cloud

1. GitHubにこのフォルダをアップ
2. Streamlit Cloudで `app.py` を指定
3. 発行されたURLをスマホで開く

## 実装済み

- 見積書 / 請求書 / 納品書切替
- PDF出力
- ボディマスター
- 製版代
- プリント代
- 特色プリント
  - 原価 +100円
  - 販売 +150円
- 利益計算
- 請求書のみ振込先表示
