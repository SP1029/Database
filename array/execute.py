def my_execute(query, idx_stat):
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
            start, end = idx_stat['strIdx'].get_name_match(value)
            matching_disk_indices.extend(range(start, end + 1))
        elif op == 'LIKE':
            if value.endswith('%'):
                prefix = value[:-1]
                start, end = idx_stat['strIdx'].get_prefix_match(prefix)
                matching_disk_indices.extend(range(start, end + 1))
            else:
                start, end = idx_stat['strIdx'].get_name_match(value)
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
        for year in idx_stat['year_list']:
            satisfies = True
            for (yop, val) in year_ops:
                if yop == '=':
                    if year != val:
                        satisfies = False
                        break
                elif yop == '<':
                    if not (year < val):
                        satisfies = False
                        break
                elif yop == '<=':
                    if not (year <= val):
                        satisfies = False
                        break
                elif yop == '>':
                    if not (year > val):
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

        for year in valid_years:
            if op == '=':
                start, end = idx_stat['arrIdx'].get_name_match_year(year, value)
                matching_disk_indices.extend(range(start, end + 1))
            elif op == 'LIKE':
                if value.endswith('%'):
                    prefix = value[:-1]
                    start, end = idx_stat['arrIdx'].get_prefix_match_year(year, prefix)
                    matching_disk_indices.extend(range(start, end + 1))
                else:
                    start, end = idx_stat['arrIdx'].get_name_match_year(year, value)
                    matching_disk_indices.extend(range(start, end + 1))
                    
    else:
        # Unsupported query type or no predicates
        return []
    
    return matching_disk_indices
