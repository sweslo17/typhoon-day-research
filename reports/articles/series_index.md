# 颱風假的科學：風雨、政治與停班停課的資料冒險

每到颱風接近台灣，社群上最穩定的天氣現象不是雨帶，而是「明天會不會放颱風假」的集體預測市場。有人看雷達回波，有人看縣市首長臉色，有人把前一次被罵爆的記憶拿出來當模型參數。這個系列想做的事很簡單：把這些猜測拆開，用資料一層一層看。

我們整理了行政院人事行政總處歷次天然災害停止上班上課公告，解析 2001-07-30 到 2026-06-28 的公告附件，建立 5,220 列縣市層級決策資料；同時抓取中央氣象署 WPPS 風雨預報格式，建立後續「放假前預估」與「放假後實際觀測」可以銜接的資料管線。

## 系列文章

1. [颱風假的科學：誰在風雨前按下暫停鍵](01-typhoon-day-science.md)
2. [放假標準不是一句話：七級風、十級陣風與地方裁量](02-standards-history.md)
3. [選舉年比較容易放颱風假嗎？先別急著相信都市傳說](03-election-years.md)
4. [哪個縣市最愛放颱風假？排行榜背後其實是地形](04-county-ranking.md)
5. [本週會放颱風假嗎？做一個透明但不裝神的模型](05-prediction-model.md)

## 主要產物

- 完整資料：`../../data/processed/dgpa_decisions.csv`
- 分析摘要：`../analysis/summary.md`
- 有趣發現：`../analysis/interesting_findings.md`
- 選舉時序表：`../analysis/election_timing.md`
- 週內預測範例：`../generated/prediction_week_taipei.json`
