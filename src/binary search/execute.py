# You are allowed to import any modules whatsoever (not even numpy, sklearn etc)
# The use of file IO is forbidden. Your code should not read from or write onto files

# SUBMIT YOUR CODE AS TWO PYTHON (.PY) FILES INSIDE A ZIP ARCHIVE
# THE NAME OF THE PYTHON FILES MUST BE index.py and execute.py

# DO NOT CHANGE THE NAME OF THE METHODS my_execute BELOW
# THESE WILL BE INVOKED BY THE EVALUATION SCRIPT. CHANGING THESE NAMES WILL CAUSE EVALUATION FAILURE

# You may define any new functions, variables, classes here
# For example, functions to create indices or statistics

################################
# Non Editable Region Starting #
################################
def my_execute( clause, idx ):
################################
#  Non Editable Region Ending  #
################################
	# print("somethign")
    # Helper function for binary search left boundary
	def binary_search_left(sorted_list, target, key=lambda x: x):
		left, right = 0, len(sorted_list)
		while left < right:
			mid = (left + right) // 2
			if key(sorted_list[mid]) < target:
				left = mid + 1
			else:
				right = mid
		return left

	# Helper function for binary search right boundary
	def binary_search_right(sorted_list, target, key=lambda x: x):
		left, right = 0, len(sorted_list)
		while left < right:
			mid = (left + right) // 2
			if key(sorted_list[mid]) <= target:
				left = mid + 1
			else:
				right = mid
		return left

	# Extract sorted tuples and disk layouts
	name_sorted_tuples = idx['name_sorted_tuples']
	year_sorted_tuples = idx['year_sorted_tuples']
	# id_sorted_tuples = idx['id_sorted_tuples']      

	#  # Extract sorted id lists
	# name_sorted_ids = idx['name_sorted_ids']
	# year_sorted_ids = idx['year_sorted_ids']
	id_sorted_ids = idx['id_sorted_ids']

	# Extract disk boundaries
	# id_start = idx['id_sorted_start']
	# id_end = idx['id_sorted_end']
	# name_start = idx['name_sorted_start']
	# name_end = idx['name_sorted_end']
	# year_start = idx['year_sorted_start']
	# year_end = idx['year_sorted_end']

	# Initialize result_ids as None
	result_ids = None

	for predicate in clause:
		field, cmp_op, value = predicate
		current_ids = []

		if field == 'name':
			# Remove both single and double quotes
			value = value.strip("'\"") # this is because value is wrapped by both single quotes and double quotes in the given clauses. for example: ['name', 'LIKE', "'c%'"] and ['name', 'LIKE', "'jafif'"]
			# print(value)
		
		if field == 'year':
			# print("hi")
			val = int(value)
			min_year = idx['min_year']
			max_year = idx['max_year']
			
			if cmp_op == '=':
				if val < min_year or val > max_year:
					current_ids = []
				else:
					left = binary_search_left(year_sorted_tuples, val, key=lambda x: x[2])
					right = binary_search_right(year_sorted_tuples, val, key=lambda x: x[2])
					current_ids = [t[0] for t in year_sorted_tuples[left:right]]
			
			elif cmp_op == '<=':
				if val < min_year:
					current_ids = []
				else:
					right_val = min(val, max_year)
					right = binary_search_right(year_sorted_tuples, right_val, key=lambda x: x[2])
					current_ids = [t[0] for t in year_sorted_tuples[0:right]]
			
			elif cmp_op == '>=':
				if val > max_year:
					current_ids = []
				else:
					left_val = max(val, min_year)
					left = binary_search_left(year_sorted_tuples, left_val, key=lambda x: x[2])
					current_ids = [t[0] for t in year_sorted_tuples[left:]]
		
		elif field == 'name':
			if cmp_op == '=':
				target_name = value
				left = binary_search_left(name_sorted_tuples, target_name, key=lambda x: x[1])
				right = binary_search_right(name_sorted_tuples, target_name, key=lambda x: x[1])
				current_ids = [t[0] for t in name_sorted_tuples[left:right]]
			
			elif cmp_op == 'LIKE':
				prefix = value[:-1]  # Remove the '%'
				if not prefix:
					current_ids = [t[0] for t in name_sorted_tuples]
				else:
					left = binary_search_left(name_sorted_tuples, prefix, key=lambda x: x[1][:len(prefix)])
					# Compute the upper bound for the prefix
					prefix_upper = list(prefix)
					i = len(prefix_upper) - 1
					while i >= 0 and prefix_upper[i] == 'z':
						prefix_upper[i] = 'a'
						i -= 1
					if i >= 0:
						prefix_upper[i] = chr(ord(prefix_upper[i]) + 1)
						prefix_upper = ''.join(prefix_upper)
					else:
						prefix_upper = prefix
					right = binary_search_left(name_sorted_tuples, prefix_upper, key=lambda x: x[1][:len(prefix)])
					current_ids = [t[0] for t in name_sorted_tuples[left:right]]
		
		# Combine the current_ids with the overall result_ids
		if result_ids is None:
			result_ids = set(current_ids)
		else:
			result_ids = result_ids.intersection(set(current_ids))

	# If no matching IDs, return an empty list
	if not result_ids:
		return []

	# Map result_ids to disk locations
	diskloc_list = []
	for id in result_ids:
		# Binary search to find the index in the disk_sorted_ids
		left, right = 0, len(id_sorted_ids) - 1
		loc = -1
		while left <= right:
			mid = (left + right) // 2
			if id_sorted_ids[mid] == id:
				loc = mid
				break
			elif id_sorted_ids[mid] < id: 
				left = mid + 1
			else:
				right = mid - 1
		if loc != -1:
			diskloc_list.append(loc)

	# sort to minimize seek time
	diskloc_list.sort() 


	# Use this method to take a WHERE clause specification
	# and return results of the resulting query
	# clause is a list containing either one or two predicates
	# Each predicate is itself a list of 3 objects, column name, comparator and value
	# idx contains the packaged variable returned by the my_index method

	# THE METHOD MUST RETURN A SINGLE LIST OF INDICES INTO THE DISK MAP
	return diskloc_list