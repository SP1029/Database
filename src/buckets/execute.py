def my_execute(query, idx_stat):
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

    # name-only queries
    if is_name and not is_year:
        return []

    # year-only queries
    elif is_year and not is_name:
        for op, year in year_predicates:
            if op == '=':
                return idx_stat.buckets.get_eq(year)
            elif op == '<=':
                return idx_stat.buckets.get_le(year)
            elif op == '>=':
                return idx_stat.buckets.get_ge(year)

    # name-year queries
    elif is_name and is_year:
        return []
        
    else:
        return []
