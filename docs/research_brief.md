# 颱風假的科學：研究簡報

## 官方資料源

- 停班停課公告歷史：行政院人事行政總處 `https://www.dgpa.gov.tw/informationlist?uid=374`
- 停班停課法規：全國法規資料庫「天然災害停止上班及上課作業辦法」`https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=S0110022`
- 颱風風雨預報：中央氣象署 `https://www.cwa.gov.tw/V8/C/P/Typhoon/WPPS.html`
- 風雨預報資料檔：中央氣象署 `https://www.cwa.gov.tw/Data/js/typhoon/WPPS-Data.js`
- 實際觀測：中央氣象署 CODiS `https://codis.cwa.gov.tw/StationData`

## 已確認的資料形狀

- 人事總處公告清單可追到 2001-07-30 左右的歷史公告，清單頁可解析 `pid`、公告標題、發布日期與公告頁網址。
- 公告詳情頁附件常是 Big5/CP950 HTML 表格，欄位通常包含「區域」「縣巿名稱」「是否停止辦公上課情形」。
- 中央氣象署 WPPS 資料檔包含各縣市 24 小時雨量預測表，可解析發布時間、平地雨量區間與山區雨量區間。
- CODiS 測站 API 可取得逐時觀測，欄位可對應平均風、最大陣風與累積雨量。

## 法規與制度重點

- 颱風停班停課常用門檻：暴風半徑四小時內可能經過，平均風力達七級以上或陣風達十級以上。
- 雨量、地形、交通、水電供應、災害風險等因素會進入地方裁量。
- 決策權在各直轄市、縣市首長；公告時間通常分為前一日晚間與當日清晨補充發布。

## 選舉時序假設

選舉年不能只看同一年。台灣總統大選常在一月，前一年夏秋颱風季可能更接近選舉壓力；地方選舉則常在十一月，較適合同年分析。模型與文章會分開標記：

- `same_year_presidential`
- `same_year_local`
- `next_year_presidential`
- `next_year_local`
- `major_election_within_180_days`

## Medium 系列標題建議

總題：「颱風假的科學：風雨、政治與停班停課的資料冒險」

單篇：

1. 颱風假的科學：誰在風雨前按下暫停鍵
2. 放假標準不是一句話：七級風、十級陣風與地方裁量
3. 選舉年比較容易放颱風假嗎？先別急著相信都市傳說
4. 哪個縣市最愛放颱風假？排行榜背後其實是地形
5. 本週會放颱風假嗎？做一個透明但不裝神的模型

## 目前模型定位

目前的 `TyphoonDayBaseline` 是透明 baseline，不宣稱已完成因果推論。它先把法規門檻與社會科學假設轉成可解釋分數，輸出機率、風險等級與 feature contribution。後續取得完整歷史資料後，可改成縣市固定效果、颱風固定效果、事件研究或分層 logistic regression。
