#MAIN PYTHON FILE FOR THE PROJECT 

#importing the required libraries
import os
import struct 
from collections import OrderedDict

#CONSTATS + UTILITY FUNCTIONS
MAGIC_NUMBER = b'4337PRJ3'
BLOCK_SIZE = 512
DEGREE = 10
MAX_KEYS = 2*DEGREE - 1
MAX_CHILDREN = MAX_KEYS + 1
#helper function to create the blank block
def blank_block():
    return b'\x00'*BLOCK_SIZE

#B-TREE NODE CLASS
class BTreeNode:
    #Constructor
    def __init__(self, block_id, is_root=False): 
        self.block_id = block_id
        self.parent_id = 0  
        self.is_root = is_root
        self.num_keys = 0
        self.keys = [0] * MAX_KEYS 
        self.values = [0] * MAX_KEYS
        self.children = [0] * MAX_CHILDREN
    #Converts the node to bytes
    def to_bytes(self): 
        data = struct.pack('>Q', self.block_id) #Block ID
        data += struct.pack('>Q', self.parent_id) #Parent ID
        data += struct.pack('>Q', self.num_keys) #Number of keys
        data += struct.pack(f'>{MAX_KEYS}Q', *self.keys) #Keys 
        data += struct.pack(f'>{MAX_KEYS}Q', *self.values) #Values
        data += struct.pack(f'>{MAX_CHILDREN}Q', *self.children) #Children
        return data + blank_block()[len(data):] 
    @staticmethod 
    #Converts bytes to node
    def from_bytes(data):
        block_id, parent_id, num_keys = struct.unpack('>QQQ', data[:24]) #Block ID, Parent ID, Number of keys
        keys = list(struct.unpack(f'>{MAX_KEYS}Q', data[24:24 + 8 * MAX_KEYS])) #Keys
        values = list(struct.unpack(f'>{MAX_KEYS}Q', data[24 + 8 * MAX_KEYS:24 + 16 * MAX_KEYS])) #Values
        children = list(struct.unpack(f'>{MAX_CHILDREN}Q', data[24 + 16 * MAX_KEYS:24 + 16 * MAX_KEYS + 8 * MAX_CHILDREN])) #Children
        node = BTreeNode(block_id) #Create a new node
        node.parent_id = parent_id #Set the parent ID
        node.num_keys = num_keys #Set the number of keys
        node.keys = keys #Set the keys
        node.values = values #Set the values
        node.children = children #Set the children
        return node #Return the node

#B-TREE HEADER CLASS 
class BTreeHeader:
    #Constructor
    def __init__(self): 
        self.magic_number = MAGIC_NUMBER #Magic number
        self.root_id = 0 #Root ID
        self.next_block_id = 1 #Next block ID
    #Converts the header to bytes
    def to_bytes(self): 
        data = self.magic_number #Magic number
        data += struct.pack('>Q', self.root_id) #Root ID
        data += struct.pack('>Q', self.next_block_id) #Next block ID
        return data + blank_block()[len(data):] #Return the data
    @staticmethod 
    #Converts bytes to header
    def from_bytes(data):
        magic_number = data[:8]  #Magic number
        if magic_number != MAGIC_NUMBER: #Check if the magic number is valid
            raise ValueError("Invalid magic number in file header.")
        root_id, next_block_id = struct.unpack('>QQ', data[8:24]) #Root ID, Next block ID
        header = BTreeHeader() #Create a new header
        header.root_id = root_id #Set the root ID
        header.next_block_id = next_block_id #Set the next block ID
        return header #Return the header
    

#B-TREE CLASS
class BTree: 
    #Constructor
    def __init__(self, file_name):
        self.file_name = file_name
        self.header = BTreeHeader()  # Initialize the header
        self.file = None
        self.cache = OrderedDict()  # Cache for nodes
        self.cache_limit = 3  # Limit the cache size 
    
    #FILE REALTED FUNCTIONS
    #Opens the file
    def open_file(self, mode='rb+'): 
        if not os.path.exists(self.file_name):#Check if the file exists
            raise FileNotFoundError(f"file '{self.file_name}' does not exist.") #Raise an error if the file does not exist
        self.file = open(self.file_name, mode) #Open the file
        header_data = self.file.read(BLOCK_SIZE) #Read the header
        try: # Try to read the header
            self.header = BTreeHeader.from_bytes(header_data) 
        except ValueError: #Raise an error if the header is invalid
            raise ValueError(f"file '{self.file_name}' has an invalid format.")
    #Creates a new file
    def create_file(self):
        if os.path.exists(self.file_name):  # Check if the file already exists
            overwrite = input(f"File '{self.file_name}' exists. Overwrite? (yes/no): ").strip().lower()
            if overwrite != 'yes':
                return
        self.file = open(self.file_name, 'wb+')  # Open the file in write mode
        self.file.write(self.header.to_bytes())  # Write the header to the file
        print(f"Created new file '{self.file_name}'.")
    #Closes the file
    def close_file(self):
        if self.file: #Check if the file is open
            self.file.close() #Close the file
    #Save the header to the file: by writing it to the beginning of the file and flushing the file
    def save_header(self): 
        if not self.file: #Check if the file is open 
            raise ValueError("file is not open.")
        self.file.seek(0) #Seek to the beginning of the file
        self.file.write(self.header.to_bytes()) #Write the header to the file
        self.file.flush() #Flush the file which writes the data to the disk and clears the buffer
    #Check if the file is open
    def is_file_open(self):  
        if not self.file: #Check if the file is open
            print("there is no file that is open. usse 'CREATE' or 'OPEN' option first.")
            return False #Return False if the file is not open
        return True #Return True if the file is open
    
    #LRU CACE MANAGEMNET FUNCTIONS 
    #Load a node from the file 
    def load_node(self, block_id: int) -> BTreeNode: 
        if block_id in self.cache: #Check if the node is in the cache
            node = self.cache.pop(block_id) #Pop the node from the cache
            self.cache[block_id] = node #Add the node to the end of the cache
            return node #Return the node
        #Read the node from the file
        if not self.file: #Check if the file is open
            raise ValueError("file is not open.") #Raise an error if the file is not open
        position = block_id * BLOCK_SIZE #Calculate the position of the block in the file
        self.file.seek(position) #Seek to the position of the block in the file
        block_data = self.file.read(BLOCK_SIZE) #Read the block data from the file
        node = BTreeNode.from_bytes(block_data) #Create a new node from the block data
        # Add to cache
        if len(self.cache) >= self.cache_limit: #Check if the cache is full
            evicted_block_id, _ = self.cache.popitem(last=False) #Evict the least recently used node from the cache
            print(f"evicted node with block ID {evicted_block_id} from memory.") 
        self.cache[block_id] = node #Add the node to the cache
        return node #Return the node
    #Save a node to the file
    def save_node(self, node: BTreeNode):
        if not self.file: #`Check if the file is open`
            raise ValueError("file is not open.")
        position = node.block_id * BLOCK_SIZE #Calculate the position of the block in the file
        self.file.seek(position) #Seek to the position of the block in the file
        self.file.write(node.to_bytes()) #Write the node to the file
        # Update the cache
        if node.block_id in self.cache: #Check if the node is in the cache
            self.cache.pop(node.block_id)  # Remove old entry
        elif len(self.cache) >= self.cache_limit: #Check if the cache is full
            evicted_block_id, _ = self.cache.popitem(last=False) #Evict the least recently used node from the cache
            print(f"evicted node with block ID {evicted_block_id} from memory.")
        self.cache[node.block_id] = node #Add the node to the cache
    #Allocate a new node in the file
    def allocate_node(self, is_root=False) -> BTreeNode:
        block_id = self.header.next_block_id #Get the next block ID
        self.header.next_block_id += 1 #Increment the next block ID
        self.save_header() #Save the header to the file
        return BTreeNode(block_id, is_root=is_root) #Return a new node with the allocated block ID
    
    #COMMANDS 
    
    #INSERT COMMAND
    #Insert a key-value pair into the B-Tree 
    def insert(self, key, value): 
        if not self.is_file_open(): #Check if the file is open
            print("No file is open. Use 'CREATE' or 'OPEN' first.")
            return
        if self.search(key, show_error=False) is not None: #Check if the key already exists in the B-Tree
            print(f"Key {key} already exists. Duplicate keys are not allowed.")
            return
        # Insert key-value pair
        if self.header.root_id == 0:  # Empty tree
            root = self.allocate_node(is_root=True) # Allocate a new root node
            root.keys[0] = key # Set the key
            root.values[0] = value # Set the value
            root.num_keys = 1 # Set the number of keys
            self.header.root_id = root.block_id # Set the root ID
            self.save_header() # Save the header to the file
            self.save_node(root) # Save the root node to the file
            print(f"Inserted key {key} into a new root.") 
        else: # Non-empty tree
            root = self.load_node(self.header.root_id) # Load the root node
            if self._insert_non_full(root, key, value):  # Check if root overflowed
                new_root = self.allocate_node(is_root=True) # Allocate a new root node
                new_root.children[0] = root.block_id # Set the old root as the first child
                self._split_child(new_root, 0, root) # Split the old root
                self.header.root_id = new_root.block_id # Set the new root ID
                self.save_header() # Save the header to the file
                self.save_node(new_root) # Save the new root node to the file
            print(f"Inserted key {key}.") # Print a message if the key is inserted successfully
    #Insert a key-value pair into a non-full node
    def _insert_non_full(self, node, key, value): 
        i = node.num_keys - 1 # Get the index of the last key
        if node.children[0] == 0:  # Leaf node
            # Insert key into the correct position
            while i >= 0 and key < node.keys[i]: # Find the correct position to insert the key
                node.keys[i + 1] = node.keys[i] # Shift keys to the right
                node.values[i + 1] = node.values[i] # Shift values to the right
                i -= 1 # Move to the previous key
            node.keys[i + 1] = key 
            node.values[i + 1] = value 
            node.num_keys += 1 
            self.save_node(node)  # Save changes to file and cache
            return node.num_keys > MAX_KEYS # Check if the node is full
        else: # Internal node
            while i >= 0 and key < node.keys[i]: # Find the correct child to insert the key
                i -= 1 # Move to the previous key
            i += 1 # Move to the correct child
            child = self.load_node(node.children[i])  # Load child node
            if self._insert_non_full(child, key, value): # Recursively insert into child
                self._split_child(node, i, child) # Split child if it overflows
            self.save_node(node)  # Save parent node changes
            return node.num_keys > MAX_KEYS # Check if the node is full
    # Function to split a child node
    def _split_child(self, parent, index, child): 
        new_node = self.allocate_node() # Allocate a new node
        new_node.num_keys = DEGREE - 1
        for j in range(DEGREE - 1): # Copy keys and values to new node
            new_node.keys[j] = child.keys[j + DEGREE]
            new_node.values[j] = child.values[j + DEGREE]
        if child.children[0] != 0: # Copy children if not a leaf node
            for j in range(DEGREE): # Copy children to new node
                new_node.children[j] = child.children[j + DEGREE]
        child.num_keys = DEGREE - 1 # Update child node
        for j in range(parent.num_keys, index, -1): # Shift children to the right
            parent.children[j + 1] = parent.children[j]
        parent.children[index + 1] = new_node.block_id # Set new node as child
        for j in range(parent.num_keys - 1, index - 1, -1): # Shift keys and values to the right
            parent.keys[j + 1] = parent.keys[j]
            parent.values[j + 1] = parent.values[j]
        parent.keys[index] = child.keys[DEGREE - 1] 
        parent.values[index] = child.values[DEGREE - 1] 
        parent.num_keys += 1
        self.save_node(child)
        self.save_node(new_node)
    
    # SEARCH COMMAND
    # Search for a key in the B-Tree
    def search(self, key, show_error=True): 
        if not self.is_file_open():  # Check if the file is open
            if show_error:
                print("No file is open. Use 'CREATE' or 'OPEN' first.")
            return None
        if self.header.root_id == 0:  # Check if the B-Tree is empty
            if show_error:
                print("The B-Tree is empty.")
            return None
        value = self._search_recursive(self.load_node(self.header.root_id), key)  # Recursively search for the key
        if value is not None:
            if show_error:
                print(f"Key: {key}, Value: {value}")  # Print the key-value pair if found
        else:
            if show_error:
                print(f"Error: Key {key} not found.")  # Print an error message if the key is not found
        return value

    # Recursive search function
    def _search_recursive(self, node, key):
        i = 0
        while i < node.num_keys and key > node.keys[i]:  # Find the correct key position
            i += 1
        if i < node.num_keys and key == node.keys[i]:  # Check if the key is found
            return node.values[i]
        if node.children[0] == 0:  # Check if the node is a leaf node
            return None
        return self._search_recursive(self.load_node(node.children[i]), key)  # Recursively search for the key

    
    #PRINT COMMAND
    def print_tree(self): #Print the key-value pairs in the B-Tree
        if not self.is_file_open(): #Check if the file is open
            return
        if self.header.root_id == 0: #Check if the B-Tree is empty
            print("The tree is empty.")
            return
        self._print_recursive(self.load_node(self.header.root_id)) # Recursively print the key-value pairs
    #Recursive print function to print the key-value pairs in the B-Tree
    def _print_recursive(self, node): 
        for i in range(node.num_keys):# Print the key-value pairs
            if node.children[i] != 0: # Recursively print child nodes
                self._print_recursive(self.load_node(node.children[i]))
            print(f"Key: {node.keys[i]}, Value: {node.values[i]}")
        if node.children[node.num_keys] != 0: # Recursively print the last child node
            self._print_recursive(self.load_node(node.children[node.num_keys]))
    
    #EXTRACT COMMAND
    def extract(self, output_file): #Extract the key-value pairs to a file
        if not self.is_file_open(): #Check if the file is open
            return
        if self.header.root_id == 0: #Check if the B-Tree is empty
            print("The tree is empty.")
            return
        if os.path.exists(output_file): #Check if the output file already exists
            overwrite = input(f"File '{output_file}' exists. Overwrite? (yes/no): ").strip().lower()
            if overwrite != 'yes': #
                print("Extraction aborted.") #Abort the extraction if the user does not want to overwrite the file
                return
        with open(output_file, 'w') as f: #Open the output file in write mode
            self._extract_recursive(self.load_node(self.header.root_id), f) # Recursively extract the key-value pairs
        print(f"Extracted to {output_file}.")
    #Recursive extract function to extract the key-value pairs to a file
    def _extract_recursive(self, node, file_handle):
        for i in range(node.num_keys): # Extract the key-value pairs
            if node.children[i] != 0: # Recursively extract child nodes
                self._extract_recursive(self.load_node(node.children[i]), file_handle)
            file_handle.write(f"{node.keys[i]},{node.values[i]}\n") # Write the key-value pair to the file
        if node.children[node.num_keys] != 0: # Recursively extract the last child node
            self._extract_recursive(self.load_node(node.children[node.num_keys]), file_handle)
    
    #LOAD COMMAND 
    def load(self, input_file): #Load the key-value pairs from a file
        if not self.is_file_open(): #Check if the file is open
            print("there is no file that is open. use 'CREATE' or 'OPEN' first to create/open a file.")
            return
        try: #Try to load the key-value pairs from the file
            with open(input_file, 'r') as f: #Open the input file in read mode
                for line in f: #Read each line in the file
                    key, value = map(int, line.strip().split(',')) #Split the line by comma and convert the values to integers
                    if self.search(key, show_error=False) is not None:  #Check if the key already exists in the B-Tree to avoid duplicates
                        print(f"Skipping duplicate key: {key}")
                        continue #Skip the key if it already exists
                    self.insert(key, value) #Insert the key-value pair into the B-Tree
            print(f"Loaded key-value pairs from '{input_file}'.") #Print a message if the key-value pairs are loaded successfully
        except Exception as e: #Catch any exceptions that occur while loading the key-value pairs
            print(f"Error loading file: {e}")

#MAIN FUNCTION
def main():
    btree = None #Create a new B-Tree object
    while True: #Run an infinite loop to accept user commands
        print("\nCommands: CREATE, OPEN, INSERT, SEARCH, LOAD, PRINT, EXTRACT, QUIT") #Print the available commands
        command = input("Enter command: ").strip().lower() #Get the user command
        #Create command
        if command == 'create': 
            file_name = input("Enter file name: ").strip() #Get the file name from the user
            btree = BTree(file_name) #Create a new B-Tree object
            btree.create_file() #Create a new file
        #Open command
        elif command == 'open':
            file_name = input("Enter file name: ").strip() #Get the file name from the user
            try: #Try to open the file
                btree = BTree(file_name) #Create a new B-Tree object
                btree.open_file() #Open the file
                print(f"Opened file '{file_name}' successfully.")
            except Exception as e: #Catch any exceptions that occur while opening the file
                print(f"Error opening file: {e}")
        #Insert, Search, Print, Extract, Load commands
        elif command in ['insert', 'search', 'print', 'extract', 'load']:
            if not btree or not btree.file: #Check if the file is open
                print("no file is open. you can use the 'CREATE' or 'OPEN' first to open a file.") #Print an error message if the file is not open
                continue
            #Insert Command
            if command == 'insert':
                key = int(input("Enter key: ")) #Get the key from the user
                value = int(input("Enter value: ")) #Get the value from the user
                btree.insert(key, value) #Insert the key-value pair into the B-Tree
            #Search Command
            elif command == 'search':
                key = int(input("Enter key: ")) #Get the key from the user
                btree.search(key, show_error=True) #Search for the key in the B-Tree
            #Print Command
            elif command == 'print':
                btree.print_tree() #Print the key-value pairs in the B-Tree
            #Extract Command
            elif command == 'extract':
                output_file = input("Enter output file name: ").strip() #Get the output file name from the user
                btree.extract(output_file) #Extract the key-value pairs to a file
            #Load Command
            elif command == 'load': 
                input_file = input("Enter input file name: ").strip() #Get the input file name from the user
                btree.load(input_file) #Load the key-value pairs from the file
        #Quit Command
        elif command == 'quit':
            if btree: #Check if the B-Tree object exists
                btree.close_file() #Close the file
            break
        #Invalid Command
        else:
            print("Invalid command. Please try again.")
if __name__ == "__main__":
    main()