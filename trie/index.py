# index.py

class Node:
    """
    Define a class for each node in the trie.
    """

    def __init__(self):
        # Array to store links to child nodes (26 lowercase letters)
        self.links = [None] * 26
        # Disk location start and end for this node
        self.disklocstart = -1
        self.disklocend = -1
        # Counter for number of words that end at this node
        self.cnt = 0

    def contains_key(self, ch):
        """
        Check if the node contains a specific key.
        """
        return self.links[ord(ch) - ord('a')] is not None

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
    sorted_by_name = sorted(data, key=lambda x: x[1].lower())
    # Assign disk locations n to 2n-1 for sorted_by_name
    disk_sorted_by_name = [t[0] for t in sorted_by_name]

    # Concatenate the two sorted lists
    disk = disk_sorted_by_year_name + disk_sorted_by_name

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
    for idx, record in enumerate(sorted_by_name):
        name = record[1].lower()
        diskloc = len(sorted_by_year_name) + idx  # n to 2n-1
        # print(name, diskloc, record)
        global_trie.insert(name, diskloc)

    # Build per-year tries for conjunctive queries (disk locations 0 to n-1)
    year_trie_list = []
    i = 0
    for year in unique_years:
        # Extract records for the current year, sorted by name
        records_for_year = [t for t in sorted_by_year_name if t[2] == year]
        # Sort records by name within the year
        records_for_year_sorted = sorted(records_for_year, key=lambda x: x[1].lower())
        # Initialize a new trie for this year
        trie = Trie()
        for idx, record in enumerate(records_for_year_sorted):
            # print(i + idx, record)
            name = record[1].lower()
            diskloc = idx + i # 0 to n-1 within year_trie
            trie.insert(name, diskloc)
        # Append the (year, trie) tuple
        # print(year)
        # trie.print_all_strings_with_frequencies()
        # print()
        year_trie_list.append((year, trie))
        i += len(records_for_year)
        
    

    # Store indexing statistics
    idx_stat = {
        'disk_len': len(disk),  # List of ids sorted by year & name and then by name
        'min_year': min_year,
        'max_year': max_year,
        'year_sorted_list': year_sorted_list,  # List of (year, disklocstart)
        'year_trie_list': year_trie_list,      # List of (year, trie)
        'global_trie': global_trie              # Trie for name-only queries
    }

    return disk, idx_stat
