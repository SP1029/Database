# index.py

class Bucket():
    def __init__(self, year, diskloc):
        self.year = year
        self.disklocstart = diskloc
        self.disklocend = diskloc
        # Counter for number of words that end at this node
        self.cnt = 0

class RadixNode:
    """
    Represents a node in the Radix Tree.
    """

    def __init__(self, edge_label=""):
        """
        Initializes a RadixNode.

        Parameters:
        - edge_label (str): The string label on the edge leading to this node.
        """
        self.edge_label = edge_label  # Label on the incoming edge
        self.children = []            # List of child RadixNodes
        self.buckets = []             # Array of year bucket
        self.disklocstart = -1        # Start disk location for this node
        self.disklocend = -1          # End disk location for this node
        self.cnt = 0                  # Number of words ending at this node

    def increase_end(self):
        """
        Increments the count of words that end at this node.
        """
        self.cnt += 1

    def set_disklocstart(self, loc):
        """
        Sets the disklocstart if it hasn't been set yet.

        Parameters:
        - loc (int): The disk location to set.
        """
        if self.disklocstart == -1:
            self.disklocstart = loc

    def set_disklocend(self, loc):
        """
        Sets the disklocend to the provided location.

        Parameters:
        - loc (int): The disk location to set.
        """
        if self.disklocend < loc:
            self.disklocend = loc



class Trie:
    """
    Represents the Radix Tree (Compressed Trie) data structure without using dictionaries.
    """

    def __init__(self, min_year=1900, max_year=2100):
        """
        Initializes the Radix Trie with an empty root node.
        """
        self.root = RadixNode()
        self.min_year = min_year
        self.max_year = max_year


    def insert(self, word, diskloc):
        """
        Inserts a word into the Radix Tree along with its disk location.

        Parameters:
        - word (str): The word to insert.
        - diskloc (int): The disk location associated with the word.
        """
        node = self.root
        idx = 0  # Current index in the word

        while idx < len(word):
            current_char = word[idx]
            child, child_index = self._find_child(node, current_char)

            if child:
                label = child.edge_label
                common_length = self._common_prefix_length(word, idx, label)

                if common_length == len(label):
                    # Complete match of the edge label; move to the child node
                    node = child
                    # Update disklocend as this node now includes the new diskloc
                    node.set_disklocend(diskloc)
                    idx += common_length

                    # If we've reached the end of the word, increment cnt
                    if idx == len(word):
                        node.increase_end()
                else:
                    # Partial match; need to split the node
                    common_prefix = label[:common_length] #ap
                    remaining_label = label[common_length:] #ple  in case of apricot node

                    # Create a new intermediate node with the common prefix
                    intermediate_node = RadixNode(edge_label=common_prefix)
                    # Update disk locations for the intermediate node
                    intermediate_node.disklocstart = min(child.disklocstart, diskloc)
                    intermediate_node.disklocend = max(child.disklocend, diskloc)

                    # Update the existing child node's edge_label
                    child.edge_label = remaining_label
                    # Add the existing child to the intermediate node's children
                    intermediate_node.children.append(child)

                    # Replace the original child with the intermediate node in the parent's children list
                    node.children[child_index] = intermediate_node

                    node = intermediate_node
                    idx += common_length

                    # Insert the remaining part of the word, if any
                    remaining_word = word[idx:]
                    if remaining_word:
                        new_child = RadixNode(edge_label=remaining_word)
                        new_child.set_disklocstart(diskloc)
                        new_child.set_disklocend(diskloc)
                        new_child.increase_end()
                        node.children.append(new_child)
                    else:
                        # The word ends at the intermediate node
                        node.increase_end()

                    # Update disk locations for the intermediate node
                    node.set_disklocstart(diskloc)
                    node.set_disklocend(diskloc)
                    break  # Insertion complete
            else:
                # No matching child; add a new child with the remaining word
                remaining_word = word[idx:]
                new_node = RadixNode(edge_label=remaining_word)
                new_node.set_disklocstart(diskloc)
                new_node.set_disklocend(diskloc)
                new_node.increase_end()
                node.children.append(new_node)
                break  # Insertion complete

    def traverse_prefix(self, word):
        """
        Traverses the Radix Tree to the end of the given word or prefix.

        Parameters:
        - word (str): The word or prefix to traverse.

        Returns:
        - RadixNode or None: The node corresponding to the end of the word/prefix if found, else None.
        """
        node = self.root
        idx = 0
        # print("Hey ", word)
        while idx < len(word):
            current_char = word[idx]
            # print(idx, current_char)
            # print([i.edge_label for i in node.children])
            child, _ = self._find_child(node, current_char)
            # print(child.edge_label)

            if child:
                label = child.edge_label
                # print("hey", label)
                if self._common_prefix_length(word, idx, label) > 0:
                    node = child
                    common_length = self._common_prefix_length(word, idx, label)
                    idx += common_length
                else:
                    # Mismatch in the label
                    return -1, -1
            else:
                # No matching child
                return -1, -1

        return node
    
    def traverse_exact_word(self, word):
        """
        Traverses the Radix Tree to the end of the given word or prefix.

        Parameters:
        - word (str): The word or prefix to traverse.

        Returns:
        - RadixNode or None: The node corresponding to the end of the word/prefix if found, else None.
        """
        node = self.root
        idx = 0

        while idx < len(word):
            current_char = word[idx]
            # print(idx, current_char)
            # print([i.edge_label for i in node.children])
            child, _ = self._find_child(node, current_char)
            # print(child.edge_label)

            if child:
                # print("hey")
                label = child.edge_label
                if label == word[idx:]:
                    return child
                elif word.startswith(label, idx):
                    node = child
                    idx += len(label)
                else:
                    # Mismatch in the label
                    return -1, -1
            else:
                # No matching child
                return -1, -1

        return -1, -1
    
    def set_year_wise_locs(self, name, year, diskloc):
        node = self.root
        idx = 0

        while idx < len(name):
            current_char = name[idx]
            child, _ = self._find_child(node, current_char)
            # print(ch)
            # if node.buckets[year-self.min_year] is None:
            #     node.buckets[year-self.min_year] = Bucket()
            #     node.buckets[year-self.min_year].disklocstart = diskloc                
            # node.buckets[year-self.min_year].disklocend = diskloc

            if len(node.buckets)==0 or node.buckets[-1].year!=year:
                node.buckets.append(Bucket(year, diskloc))
            else:
                node.buckets[-1].disklocend = diskloc

            if child:
                # print("hey")
                label = child.edge_label
                if label == name[idx:]:
                    node = child
                    idx += len(label)
                elif name.startswith(label, idx):
                    node = child
                    idx += len(label)
                else:
                    # should not reach here
                    print ("something is wrong!")
                    break
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



 

    def _find_child(self, node, char):
        """
        Finds a child node of the given node that starts with the specified character.

        Parameters:
        - node (RadixNode): The parent node.
        - char (str): The character to match.

        Returns:
        - tuple: (child_node or None, index in the children list)
        """
        for index, child in enumerate(node.children):
            if child.edge_label.startswith(char):
                return child, index
        return None, -1

    def _common_prefix_length(self, word, word_idx, label):
        """
        Finds the length of the common prefix between the word starting at word_idx and the label.

        Parameters:
        - word (str): The word being inserted or searched.
        - word_idx (int): The current index in the word.
        - label (str): The edge label to compare with.

        Returns:
        - int: The length of the common prefix.
        """
        max_length = min(len(label), len(word) - word_idx)
        i = 0
        while i < max_length and word[word_idx + i] == label[i]:
            i += 1
        return i

    def get_all_words(self):
        """
        Retrieves all unique words stored in the Radix Tree.

        Returns:
        - list of str: All unique words stored in the Radix Tree.
        """
        words = []

        def dfs(node, path):
            # If node.cnt >0, add current path to words
            if node.cnt > 0:
                words.append(path)
            # Traverse children
            for child in node.children:
                dfs(child, path + child.edge_label)

        # Start DFS from root with empty path
        dfs(self.root, "")

        return words


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
    for idx, record in enumerate(sorted_by_name_year):
        name = record[1].lower()
        diskloc = len(sorted_by_year_name) + idx  # n to 2n-1
        # print(name, diskloc, record)
        global_trie.insert(name, diskloc)

    for idx, record in enumerate(sorted_by_year_name):
        name = record[1].lower()
        year = int(record[2])
        diskloc = idx
        global_trie.set_year_wise_locs(name, year, diskloc)

    # Build per-year tries for conjunctive queries (disk locations 0 to n-1)
    # year_trie_list = []
    # i = 0
    # for year in unique_years:
    #     # Extract records for the current year, sorted by name
    #     records_for_year = [t for t in sorted_by_year_name if t[2] == year]
    #     # Sort records by name within the year
    #     records_for_year_sorted = sorted(records_for_year, key=lambda x: x[1].lower())
    #     # Initialize a new trie for this year
    #     trie = Trie()
    #     for idx, record in enumerate(records_for_year_sorted):
    #         # print(i + idx, record)
            
    #         name = record[1].lower()
    #         diskloc = idx + i # 0 to n-1 within year_trie
    #         trie.insert(name, diskloc)
    #         # print(name, diskloc, record)
    #     # Append the (year, trie) tuple
    #     # print(year)
    #     # trie.print_all_strings_with_frequencies()
    #     # print()
    #     year_trie_list.append((year, trie))
    #     i += len(records_for_year)
        
    

    # Store indexing statistics
    idx_stat = {
        'disk_len': len(disk),  # List of ids sorted by year & name and then by name
        'min_year': min_year,
        'max_year': max_year,
        'year_sorted_list': year_sorted_list,  # List of (year, disklocstart)
        # 'year_trie_list': year_trie_list,      # List of (year, trie)
        'global_trie': global_trie              # Trie for name-only queries
    }

    return disk, idx_stat
