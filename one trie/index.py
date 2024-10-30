# index.py
class Bucket():
    def __init__(self):
        self.disklocstart = -1
        self.disklocend = -1
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
        self.buckets = [Bucket()] * 201

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

    def __init__(self):
        """
        Constructor to initialize the trie with an empty root node.
        """
        self.root = Node()

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
    
    def print_all_strings_with_frequencies(self):
        """
        Print all strings stored in the trie along with their frequencies.
        """
        def dfs(node, prefix):
            if node.cnt > 0:
                print(f"{prefix}: {node.cnt}")
            for i in range(26):
                if node.links[i]:
                    ch = chr(i + ord('a'))
                    dfs(node.links[i], prefix + ch)

        dfs(self.root, "")

    def set_year_wise_locs(self, name, year, diskloc):
        node = self.root
        for ch in name:
            # print(ch)
            if node.buckets[year-1900].disklocstart == -1:
                node.buckets[year-1900].disklocstart == diskloc                
            node.buckets[year-1900].disklocend = diskloc

            if node.contains_key(ch):
                node = node.get(ch)
            else:
                # should not reach here
                print ("something is wrong!")
                break
        
        # last node
        if node.buckets[year-1900].disklocstart == -1:
            node.buckets[year-1900].disklocstart == diskloc
        node.buckets[year-1900].disklocend = diskloc
        node.buckets[year-1900].cnt += 1



def my_index(data):
    """
    Build indexes for the given data.

    Parameters:
        data (list of tuples): Each tuple contains (id, name, year).

    Returns:
        disk (list): Concatenated list of ids sorted by year & name and then by name.
        idx_stat (dict): Dictionary containing indexing statistics and structures.
    """
    # Sort data by year and within each year by name
    sorted_by_year_name = sorted(data, key=lambda x: (x[2], x[1].lower()))
    # Assign disk locations 0 to n-1 for sorted_by_year_name
    disk_sorted_by_year_name = [t[0] for t in sorted_by_year_name]

    # Sort data by name globally
    sorted_by_name_year = sorted(data, key=lambda x: (x[1].lower(), x[2]))
    # Assign disk locations n to 2n-1 for sorted_by_name
    disk_sorted_by_name_year = [t[0] for t in sorted_by_name_year]

    # Concatenate the two sorted lists
    disk = disk_sorted_by_year_name + disk_sorted_by_name_year

    # Initialize min_year and max_year
    years = [t[2] for t in data]
    min_year = min(years)
    max_year = max(years)

    # Build year_sorted_list: sorted list of (year, disklocstart)
    unique_years = sorted(set(years))
    year_sorted_list = []
    for year in unique_years:
        # Find the first occurrence of the year in sorted_by_year_name
        for idx, record in enumerate(sorted_by_year_name):
            if record[2] == year:
                year_sorted_list.append((year, idx))
                break

    # Build global trie for name-only queries (disk locations n to 2n-1)
    global_trie = Trie()
    n = len(sorted_by_name_year)
    for idx, record in enumerate(sorted_by_name_year):
        name = record[1].lower()
        diskloc = n + idx  # n to 2n-1
        # print(name, diskloc, record)
        global_trie.insert(name, diskloc)

    for idx, record in enumerate(sorted_by_year_name):
        name = record[1].lower()
        year = int(record[2])
        diskloc = idx
        global_trie.set_year_wise_locs(name, year, diskloc)
        
    

    # Store indexing statistics
    idx_stat = {
        'disk_len': len(disk),  # List of ids sorted by year & name and then by name
        'min_year': min_year,
        'max_year': max_year,
        'year_sorted_list': year_sorted_list,  # List of (year, disklocstart)
        'global_trie': global_trie              # Trie for name-only queries
    }

    return disk, idx_stat
