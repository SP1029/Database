class NumBuckets:
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
        if not (self.MIN_YEAR <= year and year<=self.MAX_YEAR):
            return []
        
        year_ix = year - self.MIN_YEAR
        
        if self.present[year_ix]:
            min_ix = self.ge_disk_ix[year_ix]
            max_ix = self.le_disk_ix[year_ix]
            return list(range(min_ix,max_ix+1))
        else:
            return []
        
    def get_le(self,year):
        if not (self.MIN_YEAR <= year and year<=self.MAX_YEAR):
            return []
        
        year_ix = year - self.MIN_YEAR
        
        if self.le_disk_ix[year_ix]!=-1:
            return list( range(0, self.le_disk_ix[year_ix]+1) )
        else:
            return []
    
    def get_ge(self,year):
        if not (self.MIN_YEAR <= year and year<=self.MAX_YEAR):
            return []
        
        year_ix = year - self.MIN_YEAR
        
        if self.ge_disk_ix[year_ix]!=self.count_tuples:
            return list( range(self.ge_disk_ix[year_ix], self.count_tuples) )
        else:
            return []
        
# index.py
class Bucket():
    def __init__(self, year, diskloc):
        self.year = year
        self.disklocstart = diskloc
        self.disklocend = diskloc
        # Counter for number of words that end at this node
        self.cnt = 0

class Node:
    """
    Define a class for each node in the trie.
    """

    def __init__(self):
        # Array to store links to child nodes (26 lowercase letters)
        self.links = [None] * 26
        # Array of year bucket
        self.buckets = []

        # data stored for global trie
        self.disklocstart = -1
        self.disklocend = -1
        # Counter for number of words that end at this node
        self.cnt = 0

    def contains_key(self, ch):
        """
        Check if the node contains a specific key.
        """
        try:
            return self.links[ord(ch) - ord('a')] is not None
        except Exception as e:
            print(ch)
            raise e

    def get(self, ch):
        """
        Get the child node corresponding to a key.
        """
        return self.links[ord(ch) - ord('a')]

    def put(self, ch, node):
        """
        Insert a child node with a specific key.
        """
        self.links[ord(ch) - ord('a')] = node

    def increase_end(self):
        """
        Increment the count of words that end at this node.
        """
        self.cnt += 1

    def set_disklocstart(self, loc):
        """
        Set the disklocstart for this node.
        """
        if self.disklocstart == -1:
            self.disklocstart = loc

    def set_disklocend(self, loc):
        """
        Set the disklocend for this node.
        """
        self.disklocend = loc


class Trie:
    """
    Define a class for the trie data structure.
    """

    def __init__(self, min_year=1900, max_year=2100):
        """
        Constructor to initialize the trie with an empty root node.
        """
        self.root = Node()
        self.min_year = min_year
        self.max_year = max_year

    def insert(self, word, diskloc):
        """
        Insert a word into the trie with its disk location.
        """
        node = self.root
        for ch in word:
            if not node.contains_key(ch):
                node.put(ch, Node())
                node = node.get(ch)
                node.set_disklocstart(diskloc)
                node.set_disklocend(diskloc)
            else:
                
                # prev = node
                node = node.get(ch)
                node.set_disklocend(diskloc)
                # node.set_disklocstart(prev.disklocstart)
        node.increase_end()
        

    def traverse(self, word):
        """
        Traverse the trie to the end of the given word or prefix.
        Returns the node if found, else None.
        """
        node = self.root
        for ch in word:
            # print(ch)
            if node.contains_key(ch):
                node = node.get(ch)
            else:
                # print("hey")
                return None
        return node
    
    def set_year_wise_locs(self, name, year, diskloc):
        node = self.root
        for ch in name:
            if len(node.buckets)==0 or node.buckets[-1].year!=year:
                node.buckets.append(Bucket(year, diskloc))
            else:
                node.buckets[-1].disklocend = diskloc

            if node.contains_key(ch):
                node = node.get(ch)
            else:
                # should not reach here
                print ("something is wrong!")
                break
        
        # last node
        if len(node.buckets)==0 or node.buckets[-1].year!=year:
                node.buckets.append(Bucket(year, diskloc))
        else:
            node.buckets[-1].disklocend = diskloc
        node.buckets[-1].cnt += 1
        
class Checker:
    def __init__(self, ix1_to_ix2):
        self.ix1_to_ix2 = ix1_to_ix2
        self.n = len(ix1_to_ix2)
        
    def process(self, indexes):
        
        # Old Indexes
        if len(indexes)==0:
            return indexes
        
        cost = indexes[-1] - indexes[0] + 1 - len(indexes)
        
        # New Indexes
        new_indexes = [None] * len(indexes)
        new_indexes = [self.ix1_to_ix2[ix] for ix in indexes]
                
        new_indexes.sort()
        
        new_cost = new_indexes[-1] - new_indexes[0] + 1 - len(new_indexes)
        
        if new_cost < cost:
            return new_indexes
        else:
            return indexes

class Index:
    def __init__(self, ix1_to_ix2, global_trie, num_buckets):
        self.checker = Checker(ix1_to_ix2)
        self.count_tuples = len(ix1_to_ix2)
        self.global_trie = global_trie
        self.num_buckets = num_buckets

def my_index( tuples ):
    
    n = len(tuples)
    
    # Name Year
    sorted_by_name_year = sorted(tuples, key=lambda x: (x[1], x[2]))
    disk_sorted_by_name_year = [t[0] for t in sorted_by_name_year]
    
    # Year Name
    sorted_by_year_name = sorted(tuples, key=lambda x: (x[2], x[1]))
    disk_sorted_by_year_name = [t[0] for t in sorted_by_year_name]
    
    # Disk
    disk = disk_sorted_by_year_name + disk_sorted_by_name_year
    
    # Num Buckets
    num_buckets = NumBuckets(sorted_by_year_name)
    
    # For translation
    year_to_name_disk_ix = [(sorted_by_name_year[i][2], n + i) for i in range(n)]
    year_to_name_disk_ix = sorted(year_to_name_disk_ix, key=lambda x: x[0])
    ix1_to_ix2 = [t[1] for t in year_to_name_disk_ix]
    
    # Global Trie
    global_trie = Trie()
    for idx, record in enumerate(sorted_by_name_year):
        name = record[1]
        diskloc = n + idx  
        global_trie.insert(name, diskloc)

    for idx, record in enumerate(sorted_by_year_name):
        name = record[1]
        year = int(record[2])
        diskloc = idx
        global_trie.set_year_wise_locs(name, year, diskloc)
    
    # Index
    idx_stat = Index(ix1_to_ix2, global_trie, num_buckets)
    
    return disk, idx_stat