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
            node = idx_stat['global_trie'].traverse(value)
            if node and node.cnt > 0:
                start = node.disklocstart
                end = node.disklocstart + node.cnt - 1
                matching_disk_indices.extend(range(start, end + 1))
        elif op == 'LIKE':
            if value.endswith('%'):
                prefix = value[:-1]
                node = idx_stat['global_trie'].traverse(prefix)
                if node and node.disklocstart != -1 and node.disklocend != -1:
                    # print("here")
                    matching_disk_indices.extend(range(node.disklocstart, node.disklocend + 1))
                    # print(matching_disk_indices)
                    # print(range(node.disklocstart, node.disklocend + 1))
            else:
                # Treat as exact match if no wildcard
                node = idx_stat['global_trie'].traverse(value)
                if node and node.cnt > 0:
                    start = node.disklocstart
                    end = node.disklocstart + node.cnt - 1
                    matching_disk_indices.extend(range(start, end + 1))

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
        year_ops = year_predicates  # List of tuples (op, val)

        # Find all years that satisfy all year predicates
        valid_years = set()
        for year in range (1900, 2101):
            satisfies = True
            for (yop, val) in year_ops:
                if yop == '=':
                    if year != val:
                        satisfies = False
                        break
                elif yop == '<=':
                    if not (year <= val):
                        satisfies = False
                        break
                elif yop == '>=':
                    if not (year >= val):
                        satisfies = False
                        break
                else:
                    # Unsupported operator
                    satisfies = False
                    break
            if satisfies:
                valid_years.add(year)

        

        
        
        if op == '=' or (op == 'LIKE' and not value.endswith('%')):
            node = idx_stat['global_trie'].traverse(value)
            for year in valid_years:
                buck = node.buckets[year-1900]
                if  buck.cnt > 0:
                    start = buck.disklocstart
                    end = start + buck.cnt - 1
                    matching_disk_indices.extend(range(start, end + 1))
                    # print(ma/tching_disk_indices)
        elif op == 'LIKE':
            prefix = value[:-1]
            node = idx_stat['global_trie'].traverse(prefix)
            for year in valid_years:
                try:
                    buck = node.buckets[year-1900]
                except Exception as e:
                    print(year)
                    raise e
                if buck.disklocstart != -1 and buck.disklocend != -1:
                    # print(year, range(node.disklocstart, node.disklocend + 1))
                    matching_disk_indices.extend(range(buck.disklocstart, buck.disklocend + 1))
                    # print(matching_disk_indices)
                

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
