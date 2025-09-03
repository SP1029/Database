# You are allowed to import any modules whatsoever (not even numpy, sklearn etc)
# The use of file IO is forbidden. Your code should not read from or write onto files

# SUBMIT YOUR CODE AS TWO PYTHON (.PY) FILES INSIDE A ZIP ARCHIVE
# THE NAME OF THE PYTHON FILES MUST BE index.py and execute.py

# DO NOT CHANGE THE NAME OF THE METHODS my_index BELOW
# THESE WILL BE INVOKED BY THE EVALUATION SCRIPT. CHANGING THESE NAMES WILL CAUSE EVALUATION FAILURE

# You may define any new functions, variables, classes here
# For example, functions to create indices or statistics



################################
# Non Editable Region Starting #
################################
def my_index( tuples ):
	################################
	#  Non Editable Region Ending  #
	################################

	# This is an example only: 
	# Disk Layout: we store indices sorted by id, by year and by name
	# Stats: min_year, max_year, year_freq, name_first_char_freq

	### DISK
	# Sort data by id, by name and by year
	id_sorted_tuples = sorted(tuples, key=lambda x: x[0])
	name_sorted_tuples = sorted(tuples, key=lambda x: x[1])
	year_sorted_tuples = sorted(tuples, key=lambda x: x[2])

	# Create disk layouts
	disk_by_id = [t[0] for t in id_sorted_tuples]
	disk_by_name = [t[0] for t in name_sorted_tuples]
	disk_by_year = [t[0] for t in year_sorted_tuples]

	# Prepare final disk list with multiple sorted lists
	disk = disk_by_id + disk_by_name + disk_by_year

	# Determine boundaries of each sorted segment in the disk list
	# len_id = len(disk_by_id)
	# len_name = len(disk_by_name)
	# len_year = len(disk_by_year)


	### STATS
	# Compute statistics
	min_year = min(t[2] for t in tuples)
	max_year = max(t[2] for t in tuples)
	year_freq = [0] * (max_year - min_year + 1)
	for t in tuples:
		year_freq[t[2] - min_year] += 1

	# Name prefix frequency (first character a-z)
	name_first_char_freq = [0] * 26
	for t in tuples:
		first_char = ord(t[1][0]) - ord('a')
		name_first_char_freq[first_char] += 1

	# Package idx_stat : will contain indices and stats
	idx_stat = {
		# 'name_sorted_ids': disk_by_name,			 	# index
		# 'year_sorted_ids': disk_by_year, 		     	# index
		'id_sorted_ids': disk_by_id,					# index
		'name_sorted_tuples': name_sorted_tuples,       # should probably not have these 2 like this since they take up too much space
		'year_sorted_tuples': year_sorted_tuples,
		'year_freq': year_freq,						 	# stats
		'name_first_char_freq': name_first_char_freq,	# stats
		'min_year': min_year,						 	# stats
		'max_year': max_year					 	# stats
		# Boundaries in the concatenated disk list
		# 'id_sorted_start': 0,
		# 'id_sorted_end': len_id,                 # Exclusive
		# 'name_sorted_start': len_id,
		# 'name_sorted_end': len_id + len_name,    # Exclusive
		# 'year_sorted_start': len_id + len_name,
		# 'year_sorted_end': len_id + len_name + len_year  # Exclusive
	}


	# Use this method to create indices and statistics
	# Each tuple has 3 values -- the id, name and year
	# THE METHOD SHOULD RETURN A DISK MAP AND A VARIABLE PACKAGING INDICES AND STATS
	return disk, idx_stat
