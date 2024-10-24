1. Update the logic in index.py and execute.py to improve performance
2. After making changes, evaluate the results by running all cells in eval_assn1_24_25_I.ipynb
3. The current logic in index.py and execute.py is suboptimal and requires optimization


| Approach      | GitHub Folder Link                                                               | t_build       | disk_size | idx_size  | t_idx       | t_seek  | t_read  | score |
|---------------|----------------------------------------------------------------------------------|---------------|-----------|-----------|-------------|---------|---------|-------|
| Binary Search | [GitHub Link](https://github.com/shrilakshmisk/CS315-A1/tree/main/assn1)         | 0.2281367667  | 300000    | 2861000   | 3.787527567 | 6400303 | 1400713 | 1     |
| Trie          | [GitHub Link](https://github.com/shrilakshmisk/CS315-A1/tree/main/trie)          | 3.812614667   | 200000    | 20771422  | 0.035879767 | 2227760 | 1400713 | 1     |
