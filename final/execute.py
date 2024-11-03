def binary_search_left(buckets, ystart):
    """
    Finds the first index in `buckets` where buck.year >= ystart.
    """
    left, right = 0, len(buckets)
    while left < right:
        mid = (left + right) // 2
        if buckets[mid].year < ystart:
            left = mid + 1
        else:
            right = mid
    return left

def binary_search_right(buckets, yend):
    """
    Finds the first index in `buckets` where buck.year > yend.
    """
    left, right = 0, len(buckets)
    while left < right:
        mid = (left + right) // 2
        if buckets[mid].year <= yend:
            left = mid + 1
        else:
            right = mid
    return left

def get_years_in_range_exact(node,ystart,yend):
    ans = []
    buckets = node.buckets
    start_idx = binary_search_left(buckets, ystart)
    end_idx = binary_search_right(buckets, yend)
    for buck in buckets[start_idx:end_idx]:
        if buck.cnt > 0:
            start = buck.disklocstart
            end = start + buck.cnt - 1
            ans.extend(range(start, end + 1))
    return ans

def get_years_in_range(node,ystart,yend):
    ans = []
    buckets = node.buckets
    start_idx = binary_search_left(buckets, ystart)
    end_idx = binary_search_right(buckets, yend)
    for buck in buckets[start_idx:end_idx]:
        if buck.cnt > 0:
            start = buck.disklocstart
            end = buck.disklocend
            ans.extend(range(start, end + 1))
    return ans


def my_execute(clause, idx):
    
    ans = []
    
    is_name = False
    is_year = False

    for predicate in clause:
        field, op, value = predicate
        if field == 'name':
            is_name = True
            n_op = op
            n_value = value
        elif field == 'year':
            is_year = True
            y_op = op
            y_value = int(value)
            if y_op == "=":
                if not (idx.min_year<=y_value and y_value<=idx.max_year):
                    return []
            elif y_op == "<=":
                if y_value < idx.min_year:
                    return []
                if y_value >= idx.max_year:
                    is_year = False
            elif y_op == ">=":
                if y_value > idx.max_year:
                    return []
                if y_value <= idx.min_year:
                    is_year = False
    
    # Name and Year Query
    if is_name and is_year:
        
        n_value = n_value.strip("'\"").lower()
        
        # Year Filters
        if y_op == "=":
            ystart = y_value
            yend = y_value
        elif y_op == "<=":
            ystart = 1900
            yend = min(2100, y_value) 
        elif y_op == ">=":
            ystart = max(1900, y_value)
            yend = 2100
            
        if n_op == '=' or (n_op == 'LIKE' and not n_value.endswith('%')):
            node = idx.global_trie.traverse(n_value)
            if node:
                for buck in node.buckets:
                    if buck.year < ystart: continue
                    if buck.year > yend: break
                    if buck.cnt > 0:
                        start = buck.disklocstart
                        end = start + buck.cnt - 1
                        ans.extend(range(start, end + 1))
                    
        elif n_op == 'LIKE':
            prefix = n_value[:-1]
            node = idx.global_trie.traverse(prefix) 
            if node:          
                for buck in node.buckets:
                    if buck.year < ystart: continue
                    if buck.year > yend: break
                    ans.extend(range(buck.disklocstart, buck.disklocend + 1))
                
        ans = idx.checker.process(ans)
    
    # Name Only Query
    elif is_name:
        n_value = n_value.strip("'\"").lower()
        # Exact match
        if n_op == '=':
            node = idx.global_trie.traverse(n_value)
            if node and node.cnt > 0:
                start = node.disklocstart
                end = node.disklocstart + node.cnt - 1
                ans = list(range(start, end + 1))
            
        elif n_op == 'LIKE':
            # Prefix match
            if n_value.endswith('%'):
                prefix = n_value[:-1]
                node = idx.global_trie.traverse(prefix)
                if node and node.disklocstart != -1 and node.disklocend != -1:
                    ans = list(range(node.disklocstart, node.disklocend + 1))
                
               
            # Exact match
            else:
                node = idx.global_trie.traverse(n_value)
                if node and node.cnt > 0:
                    start = node.disklocstart
                    end = node.disklocstart + node.cnt - 1
                    ans = list(range(start, end + 1))
    
    # Year Ony Query
    else:        
        match y_op:
            case "=":
                ans = idx.num_buckets.get_eq(y_value)
                
            case "<=":
                ans = idx.num_buckets.get_le(y_value)
                
            case ">=":
                ans = idx.num_buckets.get_ge(y_value)

    
    
        
    return ans
        