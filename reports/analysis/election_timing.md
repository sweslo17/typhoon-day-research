# 選舉時序與颱風假探索統計

這份表是探索性統計，不是因果推論。總統大選若在隔年一月，前一年颱風季會被標記為 `next_year_presidential`。
各 group 是非互斥標籤，因此 rows 不應加總解讀。

| group | rows | stopped_signal_rows | stopped_signal_rate |
| --- | ---: | ---: | ---: |
| `same_year_presidential` | 1627 | 740 | 45.48% |
| `same_year_local` | 1158 | 482 | 41.62% |
| `next_year_presidential` | 1177 | 469 | 39.85% |
| `next_year_local` | 1783 | 773 | 43.35% |
| `major_election_within_180_days` | 2184 | 896 | 41.03% |
| `off_cycle` | 225 | 58 | 25.78% |
