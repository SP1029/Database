class Buckets:
    def __init__(self, tuples):
        self.MIN_YEAR = 1900
        self.MAX_YEAR = 2100
        self.count_years = self.MAX_YEAR - self.MIN_YEAR + 1
        self.count_tuples = len(tuples)

        self.le_disk_ix = [-1] * self.count_years
        self.ge_disk_ix = [self.count_tuples] * self.count_years
        self.present = [False] * self.count_years
        
        for disk_ix, t in enumerate(tuples):
            year = t[2]
            year_ix = year - self.MIN_YEAR
            self.le_disk_ix[year_ix] = max(self.le_disk_ix[year_ix], disk_ix)
            self.ge_disk_ix[year_ix] = min(self.ge_disk_ix[year_ix], disk_ix)
        
        for i in range(self.count_years):
            if i > 0:
                self.le_disk_ix[i] = max(self.le_disk_ix[i], self.le_disk_ix[i-1])
                
            ix = self.count_years - 1 - i
            if ix < self.count_years - 1:
                self.ge_disk_ix[ix] = min(self.ge_disk_ix[ix], self.ge_disk_ix[ix+1])
                
            if self.le_disk_ix[i]!=-1:
                self.present[i] = True
                
    def get_eq(self, year):
        year_ix = year - self.MIN_YEAR
        
        if self.present[year_ix]:
            min_ix = self.ge_disk_ix[year_ix]
            max_ix = self.le_disk_ix[year_ix]
            return list(range(min_ix,max_ix+1))
        else:
            return []
        
    def get_le(self,year):
        year_ix = year - self.MIN_YEAR
        
        if self.le_disk_ix[year_ix]!=-1:
            return list( range(0, self.le_disk_ix[year_ix]+1) )
        else:
            return []
    
    def get_ge(self,year):
        year_ix = year - self.MIN_YEAR
        
        if self.ge_disk_ix[year_ix]!=self.count_tuples:
            return list( range(self.ge_disk_ix[year_ix], self.count_tuples) )
        else:
            return []


class Index:
    def __init__(self, tuples):
        sorted_by_year_name = sorted(tuples, key=lambda x: (x[2], x[1].lower()))
        disk_sorted_by_year_name = [t[0] for t in sorted_by_year_name]
        
        self.buckets = Buckets(sorted_by_year_name)
        self.disk = disk_sorted_by_year_name
    
    def get_disk(self):
        disk = self.disk
        self.disk = None
        return disk
    

################################
# Non Editable Region Starting #
################################
def my_index( tuples ):
    
    idx_stat = Index(tuples)
    return idx_stat.get_disk(), idx_stat