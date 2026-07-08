# 颱風假的科學：完整文章包

這個資料夾是可直接整理後發布到 Medium 的長文版本。早期草稿仍保留在 `reports/medium/`；這裡的文章已經補上完整敘事、圖表插入點、資料口徑與來源。

## 發布順序

1. `01-typhoon-day-science.md`  
   總論：颱風假到底是氣象題、行政題，還是社會題？
2. `02-standards-history.md`  
   法規與制度史：七級風、十級陣風、雨量與地方裁量。
3. `03-election-years.md`  
   選舉時序：同年選舉、隔年總統大選，和不要過度解讀的探索統計。
4. `04-county-ranking.md`  
   縣市排行榜：誰常放，為什麼排行榜不能直接叫「愛放」。
5. `05-prediction-model.md`  
   預測方法：透明 baseline、如何輸入本週風雨資料、如何解讀機率。

## 圖表與資料

- 縣市停止上班上課排行：`../analysis/stop_count.svg`
- 人事總處公告解析資料：`../../data/processed/dgpa_decisions.csv`
- 選舉時序探索統計：`../analysis/election_timing.csv`
- CWA WPPS 風雨預報解析：`../../data/processed/cwa_wpps_forecast.csv`
- 範例預測：`../generated/prediction_2026-07-08_taipei_scenario.json`

## 發布提醒

- Medium 不一定能直接使用 repo 裡的相對圖片路徑；發布時可將 SVG 另存為 PNG 後上傳。
- 文章內的統計是探索性結果，不是因果推論。
- `next_year_presidential` 是刻意設計的時序標籤，因為台灣總統大選常在一月，前一年颱風季可能比同年颱風季更接近選舉壓力。
