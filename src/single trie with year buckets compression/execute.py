# execute.py

from index import Trie  # Import Trie class from index.py

def my_execute(query, idx_stat):
    # print(query)
    """
    Execute a conjunctive query with predicates on 'year' and 'name'.

    Parameters:
        query (list of lists): Each sublist represents a predicate, e.g., ['year', '>=', '2000'].
        idx_stat (dict): Dictionary containing indexing statistics and structures.

    Returns:
        disk_indices (list): List of disk positions corresponding to the final matching IDs.
    """
    # Helper function to perform binary search for year
    def binary_search_year(year_sorted_list, target_year):
        left, right = 0, len(year_sorted_list) - 1
        while left <= right:
            mid = (left + right) // 2
            mid_year = year_sorted_list[mid][0]
            if mid_year == target_year:
                return mid
            elif mid_year < target_year:
                left = mid + 1
            else:
                right = mid - 1
        return -1

    # Determine the type of query
    is_name = False
    is_year = False
    name_predicate = None
    year_predicates = []

    for predicate in query:
        field, op, value = predicate
        if field == 'name':
            is_name = True
            name_predicate = (op, value)
        elif field == 'year':
            is_year = True
            year_predicates.append((op, int(value)))

    # Initialize a set for matching disk indices
    matching_disk_indices = []

    # Handle name-only queries
    if is_name and not is_year:
        op, value = name_predicate
        value = value.strip("'\"").lower()
        if op == '=':
            node = idx_stat['global_trie'].traverse_exact_word(value)
            if node:
                word_start = node.disklocstart
                word_cnt = node.cnt;
            else:
                return matching_disk_indices
            if word_start != -1:
                start = word_start
                end = word_start + word_cnt - 1
                matching_disk_indices.extend(range(start, end + 1))
        elif op == 'LIKE':
            if value.endswith('%'):
                prefix = value[:-1]
                node = idx_stat['global_trie'].traverse_prefix(prefix)
                if node:
                    prefix_start = node.disklocstart
                    prefix_end = node.disklocend;
                else:
                    return matching_disk_indices
                if prefix_start != -1:
                    # print("here")
                    matching_disk_indices.extend(range(prefix_start, prefix_end + 1))
                    # print(matching_disk_indices)
                    # print(range(node.disklocstart, node.disklocend + 1))
            # else:
            #     # Treat as exact match if no wildcard
            #     node = idx_stat['global_trie'].traverse(value)
            #     if node and node.cnt > 0:
            #         start = node.disklocstart
            #         end = node.disklocstart + node.cnt - 1
            #         matching_disk_indices.extend(range(start, end + 1))

    # Handle year-only queries
    elif is_year and not is_name:
        for op, val in year_predicates:
            if op == '=':
                idx = binary_search_year(idx_stat['year_sorted_list'], val)
                if idx != -1:
                    start = idx_stat['year_sorted_list'][idx][1]
                    # Determine the count by checking the next year or end of list
                    if idx + 1 < len(idx_stat['year_sorted_list']):
                        end = idx_stat['year_sorted_list'][idx + 1][1] - 1
                    else:
                        end = idx_stat['disk_len'] // 2 - 1  # n-1
                    matching_disk_indices.extend(range(start, end + 1))
            elif op == '<':
                # Find all years less than val
                for (year, disklocstart) in idx_stat['year_sorted_list']:
                    if year < val:
                        # Determine the end for this year
                        idx = binary_search_year(idx_stat['year_sorted_list'], year)
                        if idx != -1:
                            if idx + 1 < len(idx_stat['year_sorted_list']):
                                end = idx_stat['year_sorted_list'][idx + 1][1] - 1
                            else:
                                end = idx_stat['disk_len'] // 2 - 1  # n-1
                            matching_disk_indices.extend(range(disklocstart, end + 1))
            elif op == '<=':
                # Find all years less than or equal to val
                for (year, disklocstart) in idx_stat['year_sorted_list']:
                    if year <= val:
                        # Determine the end for this year
                        idx = binary_search_year(idx_stat['year_sorted_list'], year)
                        if idx != -1:
                            if idx + 1 < len(idx_stat['year_sorted_list']):
                                end = idx_stat['year_sorted_list'][idx + 1][1] - 1
                            else:
                                end = idx_stat['disk_len'] // 2 - 1  # n-1
                            matching_disk_indices.extend(range(disklocstart, end + 1))
            elif op == '>':
                # Find all years greater than val
                for (year, disklocstart) in idx_stat['year_sorted_list']:
                    if year > val:
                        # Determine the end for this year
                        idx = binary_search_year(idx_stat['year_sorted_list'], year)
                        if idx != -1:
                            if idx + 1 < len(idx_stat['year_sorted_list']):
                                end = idx_stat['year_sorted_list'][idx + 1][1] - 1
                            else:
                                end = idx_stat['disk_len'] // 2 - 1  # n-1
                            matching_disk_indices.extend(range(disklocstart, end + 1))
            elif op == '>=':
                # Find all years greater than or equal to val
                for (year, disklocstart) in idx_stat['year_sorted_list']:
                    if year >= val:
                        # Determine the end for this year
                        idx = binary_search_year(idx_stat['year_sorted_list'], year)
                        if idx != -1:
                            if idx + 1 < len(idx_stat['year_sorted_list']):
                                end = idx_stat['year_sorted_list'][idx + 1][1] - 1
                            else:
                                end = idx_stat['disk_len'] // 2 - 1  # n-1
                            matching_disk_indices.extend(range(disklocstart, end + 1))

    # Handle conjunctive queries (both name and year predicates)
    elif is_name and is_year:
        # Extract name predicate
        op, value = name_predicate
        value = value.strip("'\"").lower()

        # Extract year predicates
        # year_ops = year_predicates  # List of tuples (op, val)

        min_year = idx_stat['min_year']
        max_year = idx_stat['max_year']
        (yop, val) = year_predicates[0]

        # Find all years that satisfy all year predicates

        if yop == "=":
            ystart = val
            yend = val
        elif yop == "<=":
            ystart = min_year
            yend = min(max_year,val) 
        elif yop == ">=":
            ystart = max(min_year,val)
            yend = max_year

        # valid_years = set()
        # for (year, trie) in idx_stat['year_trie_list']:
        #     satisfies = True
        #     for (yop, val) in year_ops:
        #         if yop == '=':
        #             if year != val:
        #                 satisfies = False
        #                 break
        #         elif yop == '<':
        #             if not (year < val):
        #                 satisfies = False
        #                 break
        #         elif yop == '<=':
        #             if not (year <= val):
        #                 satisfies = False
        #                 break
        #         elif yop == '>':
        #             if not (year > val):
        #                 satisfies = False
        #                 break
        #         elif yop == '>=':
        #             if not (year >= val):
        #                 satisfies = False
        #                 break
        #         else:
        #             # Unsupported operator
        #             satisfies = False
        #             break
        #     if satisfies:
        #         valid_years.add(year)

        # print(valid_years)

        # For each valid year, traverse its trie based on name predicate

        if op == '=' or (op == 'LIKE' and not value.endswith('%')):
            node = idx_stat['global_trie'].traverse_exact_word(value)
            for buck in node.buckets:
                if buck.year < ystart: continue
                if buck.year > yend: break
                if buck.cnt > 0:
                    start = buck.disklocstart
                    end = start + buck.cnt - 1
                    matching_disk_indices.extend(range(start, end + 1))
        elif op == 'LIKE':
            prefix = value[:-1]
            node = idx_stat['global_trie'].traverse_prefix(prefix)            
            # print("here1")
            # for year in valid_years:
            #     try:
            #         buck = node.buckets[year-min_year]
            #     except Exception as e:
            #         print(year, yop, val)
            #         raise e
            #     # print("here2 ", year)
            #     if buck is not None:
            #         # print(year, range(node.disklocstart, node.disklocend + 1))
            #         # print("here3", year, buck.disklocstart, buck.disklocend)
            #         matching_disk_indices.extend(range(buck.disklocstart, buck.disklocend + 1))
            #         # print(matching_disk_indices)
            for buck in node.buckets:
                if buck.year < ystart: continue
                if buck.year > yend: break
                matching_disk_indices.extend(range(buck.disklocstart, buck.disklocend + 1))

        # for (year, trie) in idx_stat['year_trie_list']:

        #     # print("heyy")
        #     if year not in valid_years:
        #         continue
        #     if op == '=':
        #         word_start, word_cnt = trie.traverse_exact_word(value)
        #         if word_start != -1:
        #             start = word_start
        #             end = word_start + word_cnt - 1
        #             matching_disk_indices.extend(range(start, end + 1))
        #             # print(ma/tching_disk_indices)
        #     elif op == 'LIKE':
        #         if value.endswith('%'):
        #             prefix = value[:-1]
        #             # print(prefix)
        #             prefix_start, prefix_end = trie.traverse_prefix(prefix)
        #             # print(year)
        #             # print(trie.get_all_words())
        #             if prefix_start != -1:
        #                 # print(year, range(prefix_start, prefix_end + 1))
        #                 matching_disk_indices.extend(range(prefix_start, prefix_end + 1))
                        # print(matching_disk_indices)
                # else:
                #     # Treat as exact match if no wildcard
                #     node = trie.traverse(value)
                #     if node and node.cnt > 0:
                #         start = node.disklocstart
                #         end = node.disklocstart + node.cnt - 1
                #         matching_disk_indices.extend(range(start, end + 1))

        # Map the disk locations from 0 to n-1 back to the main disk list
        # final_disk_indices = []
        # for diskloc in matching_disk_indices:
        #     if 0 <= diskloc < idx_stat['disk_len'] // 2:
        #         final_disk_indices.append(diskloc)
        # final_disk_indices.sort()
        # return final_disk_indices
        # return matching_disk_indices

    else:
        # Unsupported query type or no predicates
        return []

    # After handling all cases, map the disklocs to the main disk list
    # if is_name and not is_year:
    #     # Name-only queries: disklocs from n to 2n-1
    #     final_disk_indices = []
    #     for diskloc in matching_disk_indices:
    #         if idx_stat['disk_len'] // 2 <= diskloc < idx_stat['disk_len']:
    #             final_disk_indices.append(diskloc)
    #     final_disk_indices.sort()
    #     return final_disk_indices
    # elif is_year and not is_name:
    #     # Year-only queries: disklocs from 0 to n-1
    #     final_disk_indices = []
    #     for diskloc in matching_disk_indices:
    #         if 0 <= diskloc < idx_stat['disk_len'] // 2:
    #             final_disk_indices.append(diskloc)
    #     final_disk_indices.sort()
    #     return final_disk_indices
    # else:
    #     # Conjunctive queries already handled above
    #     return final_disk_indices

    # print (matching_disk_indices)
    return matching_disk_indices
