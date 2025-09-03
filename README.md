## Problem Statement

This project is database query engine built from scratch in Python. The engine is optimized for low latency and minimal resource consumption, focusing on efficient data indexing, disk layout, and query processing.

The core task was to build a query engine for a dataset with `(id, name, year)` tuples. The engine needed to support the following SQL-like queries:

* **Year-Only Queries**: `SELECT id FROM tbl WHERE year <cmp> <val>` (where `cmp` is `=`, `<=`, `>=`)
* **Name-Only Queries**: `SELECT id FROM tbl WHERE name <cmp> <val>` (where `cmp` is `=` or `LIKE 'prefix%'`)
* **Conjunctive Queries**: `SELECT id FROM tbl WHERE name <cmp> <val> AND year <cmp> <val>`

## Experimentation Results

We came up and experimented with several types of indexes finally chosing the optimal one based on time vs size trade-off which has been detailed in the report. 

The metrics taken into account were:
- Time to build the index
- Size taken by data in memory
- Size taken by the index
- Time to answer the query
- Time taken for the disk to seek the records
- Time taken for the disk to read the records


### For only numeric queries

| Approach | t\_build | disk\_size | idx\_size | t\_idx | t\_seek | t\_read | score |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Binary Search** | 0.20712 | 300000 | 2861000 | 2.831087766 | 840768 | 1158280 | 1 |
| **Buckets** | 0.26276 | 100000 | 1996 | 0.012512733 | 840768 | 1158280 | 1 |

### For all types of querries

| Approach | t\_build | disk\_size | idx\_size | t\_idx | t\_seek | t\_read | score |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Array** | 0.736580000 | 200000 | 1662898 | 0.930382966 | 2752003 | 1400708 | 1 |
| **Binary Search** | 0.2281367667 | 300000 | 2861000 | 3.787527567 | 6400303 | 1400713 | 1 |
| **Global Trie and Year Tries** | 3.812614667 | 200000 | 19770894 | 0.035879767 | 2227760 | 1400713 | 1 |
| **Single Trie with Year Buckets** | 2.3308658666 | 200000 | 13788002 | 0.028946199 | 2227760 | 1400713 | 1 |
| **One Trie Compression** | 3.0678317333 | 200000 | 10040106 | 0.0447875333 | 2227760 | 1400713 | 1 |
| **One Trie Space Optimized** | 2.32173420 | 200000 | 13788175 | 0.026583533 | 2227760 | 1400713 | 1 |
| **Global Trie and Year Tries Compression** | 3.2062207666 | 200000 | 7502228 | 0.0376125999 | 2227760 | 1400713 | 1 |
| **Filtering By Names, Then Years** | 1.4122694333 | 200000 | 6384134 | 0.1231322999  | 93206 | 1400713 | 1 |
| **Final - Single Trie With Year Buckets Translated** | 1.872402300 | 200000 | 14289759 | 0.04361066666 | 93206 | 1400713 | 1 |

## Code Structure

- `index.py`: Contains the `my_index()` function the to build index
- `execute.py`: Contains the `my_execute()` function to process a query

```bash
├── Problem Statement.pdf
├── README.md
├── Report.pdf
├── array
├── src
│   ├── array
│   │   ├── execute.py
│   │   └── index.py
│   ├── binary search
│   │   ├── execute.py
│   │   └── index.py
│   ├── buckets
│   │   ├── execute.py
│   │   └── index.py
│   ├── final
│   │   ├── execute.py
│   │   └── index.py
│   ├── global trie and year tries
│   │   ├── execute.py
│   │   └── index.py
│   ├── global trie and year tries compression
│   │   ├── execute.py
│   │   └── index.py
│   ├── single trie with year buckets
│   │   ├── execute.py
│   │   └── index.py
│   └── single trie with year buckets compression
│       ├── execute.py
│       └── index.py
└── templates
    ├── execute.py
    ├── index.py
    └── testing script.ipynb
```
