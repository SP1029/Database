class StringIndex:
    def __init__(self, data, offset):
        self.data = data
        self.offset = offset
    
    # Helper function for binary search left boundary
    def binary_search_left(self, target, start_ix, end_ix):
        left, right = start_ix, end_ix
        while left < right:
            mid = (left + right) // 2
            if self.data[mid] < target:
                left = mid + 1
            else:
                right = mid
        return left

    # Helper function for binary search right boundary
    def binary_search_right(self, target, start_ix, end_ix):
        left, right = start_ix, end_ix
        while left < right:
            mid = (left + right) // 2
            if self.data[mid] <= target:
                left = mid + 1
            else:
                right = mid
        return left
    
    def get_name_match(self, name, start_ix=-1, end_ix=-1):
        if start_ix==-1:
            start_ix = 0
            end_ix = len(self.data)-1
        left = self.binary_search_left(name, start_ix, end_ix)
        right = self.binary_search_right(name, start_ix, end_ix)
        return left  + self.offset, right  + self.offset - 1
       
    def get_prefix_match(self, prefix, start_ix=-1, end_ix=-1):
        if start_ix==-1:
            start_ix = 0
            end_ix = len(self.data)-1
        left = self.binary_search_left(prefix, start_ix, end_ix)
        right = self.binary_search_right(prefix.ljust(10,'z'), start_ix, end_ix)
        return left + self.offset, right + self.offset - 1

class ArrayIndex(StringIndex):
    def __init__(self, tuples, offset):
        self.MIN_YEAR = 1900
        self.MAX_YEAR = 2100
        self.count_years = self.MAX_YEAR - self.MIN_YEAR + 1
        self.count_tuples = len(tuples)
        
        self.end_ix = [-1] * self.count_years
        self.start_ix = [self.count_tuples] * self.count_years
        self.present = [False] * self.count_years
        
        for disk_ix, t in enumerate(tuples):
            year = t[2]
            year_ix = year - self.MIN_YEAR
            self.end_ix[year_ix] = max(self.end_ix[year_ix], disk_ix)
            self.start_ix[year_ix] = min(self.start_ix[year_ix], disk_ix)
            
        for i in range(self.count_years):
            if self.end_ix[i]!=-1:
                self.present[i] = True
                
        data = [t[1] for t in tuples]
        StringIndex.__init__(self, data, offset)
        
    def get_prefix_match_year(self, year, prefix):
        year_ix = year - self.MIN_YEAR
        
        if self.present[year_ix]:
            start_ix = self.start_ix[year_ix]
            end_ix = self.end_ix[year_ix]
            ans = self.get_prefix_match(prefix, start_ix, end_ix)
            return ans
        else:
            return []
    
    def get_name_match_year(self, year, name):
        year_ix = year - self.MIN_YEAR
        
        if self.present[year_ix]:
            start_ix = self.start_ix[year_ix]
            end_ix = self.end_ix[year_ix]
            ans = self.get_name_match(name, start_ix, end_ix)
            return ans
        else:
            return []
        

def my_index(data):
    
    ### DISK
    # Sort data by id, by name and by year
    year_name_sorted_tuples = sorted(data, key=lambda x: (x[2], x[1].lower()))
    name_year_sorted_tuples = sorted(data, key=lambda x: ( x[1].lower(),x[2]))
 
    # Create disk layouts
    disk_by_year = [t[0] for t in year_name_sorted_tuples]
    disk_by_name = [t[0] for t in name_year_sorted_tuples]
 
    disk =  disk_by_year + disk_by_name
    
    # idx
    arrIdx = ArrayIndex(year_name_sorted_tuples,0)
    strIdx = StringIndex([t[1] for t in name_year_sorted_tuples], len(year_name_sorted_tuples))
    
    # Build year_sorted_list: sorted list of (year, disklocstart)
    years = [int(t[2]) for t in data]
    unique_years = sorted(set(years))
    year_sorted_list = []
    for year in unique_years:
        # Find the first occurrence of the year in sorted_by_year_name
        for idx, record in enumerate(year_name_sorted_tuples):
            if record[2] == year:
                year_sorted_list.append((year, idx))
                break
    
    idx_stat = {
        'arrIdx': arrIdx,
        'strIdx': strIdx,
        'year_sorted_list': year_sorted_list,  # List of (year, disklocstart)
        'disk_len': len(disk),  # List of ids sorted by year & name and then by name
        'year_list': years
    }

    return disk, idx_stat
