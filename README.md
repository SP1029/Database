1. Update the logic in index.py and execute.py to improve performance
2. After making changes, evaluate the results by running all cells in eval_assn1_24_25_I.ipynb
3. The current logic in index.py and execute.py is suboptimal and requires optimization


| Approach      | GitHub Folder Link                                                               | t_build       | disk_size | idx_size  | t_idx       | t_seek  | t_read  | score |
|---------------|----------------------------------------------------------------------------------|---------------|-----------|-----------|-------------|---------|---------|-------|
| Binary Search | [GitHub Link](https://github.com/shrilakshmisk/CS315-A1/tree/main/assn1)         | 0.2281367667  | 300000    | 2861000   | 3.787527567 | 6400303 | 1400713 | 1     |
| Trie          | [GitHub Link](https://github.com/shrilakshmisk/CS315-A1/tree/main/trie)          | 3.812614667   | 200000    | 19770894  | 0.035879767 | 2227760 | 1400713 | 1     |
| Array         | [GitHub Link](https://github.com/shrilakshmisk/CS315-A1/tree/main/array)         | 0.736580000   | 200000    | 1662898   | 0.930382966 | 2752003 | 1400708 | 1     | 
| One Trie      | [GitHub Link](https://github.com/shrilakshmisk/CS315-A1/tree/main/one%20trie)    | 3.0674676333  | 200000    | 13788002  | 0.021993900 | 2227760 | 1400713 | 1     |
| One Trie Space Optimized | [GitHub Link](https://github.com/shrilakshmisk/CS315-A1/tree/main/one%20trie%20space%20optimized) | 2.32173420 | 200000 | 13788175 | 0.026583533 | 2227760 | 1400713 | 1 |
| Trie Compression | [GitHub Link](https://github.com/shrilakshmisk/CS315-A1/tree/main/trie%20compression) | 3.2062207666 | 200000 | 7502228 | 0.0376125999 | 2227760 | 1400713 | 1 |




### For only years query

| Approach      | GitHub Folder Link                                                               | t_build       | disk_size | idx_size  | t_idx       | t_seek  | t_read  | score |
|---------------|----------------------------------------------------------------------------------|---------------|-----------|-----------|-------------|---------|---------|-------|
| Binary Search | [GitHub Link](https://github.com/shrilakshmisk/CS315-A1/tree/main/assn1)         | 0.20712       | 300000    | 2861000   | 2.831087766 | 840768  | 1158280 | 1     |
| Buckets       | [GitHub Link](https://github.com/shrilakshmisk/CS315-A1/tree/main/buckets)       | 0.26276       | 100000    | 1996      | 0.012512733 | 0       | 1158280 | 1     |
