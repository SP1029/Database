def my_execute(clause, idx):
    
    ans = []
    
    # Single
    if len(clause)==1:
        col, op, value = clause[0]
        
        # Name only
        if col=="name":
            value = value.strip("'\"").lower()
            # Exact match
            if op == '=':
                node = idx.global_trie.traverse(value)
                if node and node.cnt > 0:
                    start = node.disklocstart
                    end = node.disklocstart + node.cnt - 1
                    ans = list(range(start, end + 1))
                
            elif op == 'LIKE':
                # Prefix match
                if value.endswith('%'):
                    prefix = value[:-1]
                    node = idx.global_trie.traverse(prefix)
                    if node and node.disklocstart != -1 and node.disklocend != -1:
                        ans = list(range(node.disklocstart, node.disklocend + 1))
                    
                   
                # Exact match
                else:
                    node = idx.global_trie.traverse(value)
                    if node and node.cnt > 0:
                        start = node.disklocstart
                        end = node.disklocstart + node.cnt - 1
                        ans = list(range(start, end + 1))
                    
        # Year Only
        else:
            value = int(value)
            match op:
                case "=":
                    ans = idx.num_buckets.get_eq(value)
                    
                case "<=":
                    ans = idx.num_buckets.get_le(value)
                    
                case ">=":
                    ans = idx.num_buckets.get_ge(value)

    # Name and Year
    else:
        (_, n_op, n_value), (_, y_op, y_value) = clause
        
        y_value = int(y_value)
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
            for buck in node.buckets:
                if buck.year < ystart: continue
                if buck.year > yend: break
                ans.extend(range(buck.disklocstart, buck.disklocend + 1))
                
        ans = idx.checker.process(ans)
        
    return ans
        