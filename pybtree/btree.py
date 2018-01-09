from pystrct import StructFile
from itertools import chain
from .pysearch import search


class Node():
    """Represent a Node in BTree.

    Properties:
        leaf -- If node is a leaf, True. Otherwise, False
        n_keys -- number of keys in node
        keys -- a list of tuples (key, value), ordered by key
        children -- a list of child Nodes
    """
    def __init__(self, pos, **kwargs):
        """Create a new Node representation.

        Keyword arguments:
            pos -- node's position in file
            keys -- node's keys (default [(0, 0)] * (order * 2))
            children -- node's children (default [None] * (2 * order + 1))
        """
        self.pos = pos
        self.keys = kwargs.get('keys', [])
        self.children = kwargs.get('children', [])

    @property
    def keys(self):
        return self.__keys

    @keys.setter
    def keys(self, other):
        self.__keys = list(other)
        self.__keys.sort(key=lambda x: x[0])

    @property
    def children(self):
        return self.__children

    @children.setter
    def children(self, other):
        self.__children = list(other)

    @property
    def is_leaf(self):
        """Return True, if node is a leaf, i.e., has no child."""
        return self.n_children == 0

    @property
    def n_keys(self):
        """Return the number of keys in node."""
        return len(self.keys)

    @property
    def n_children(self):
        """Return the number of keys in node."""
        return len(self.children)

    def to_list(self):
        """Convert Node to tuple."""
        keys = chain.from_iterable(self.keys)                                # [(1,2), (3,4)] => [1,2,3,4]
        children = [n.pos if type(n) is Node else n for n in self.children]  # node => node.pos

        # Position, # of keys, # of children, keys, children's position
        return [self.pos, self.n_keys, self.n_children] + list(keys) + children

    def search(self, key):
        """Search for a node with key.

        Return a child index.

        Keyword arguments:
            key -- key to be search in node
        """
        # If node is leaf, there is no other path
        if self.is_leaf:
            return None

        # Find the next node to key
        for i in range(self.n_keys):
            # If node.key > key
            if self.keys[i][0] > key:
                # Return left node, because key < node.key
                return i

        # Return most-right node, because key is greater than all keys
        return self.n_keys

    def append_key(self, key, value):
        """Append a key to node.

        Keyword arguments:
            key -- key to be appended
            value -- key's value
        """
        self.keys = self.__keys + [(key, value)]

    def append(self, key, value, child):
        """Append a key,value with right child.

        Keyword arguments:
            key -- key to be appended
            value -- key's value
            child -- a Node object or int
        """
        # Append key,value pair
        self.append_key(key, value)

        # Find pair's position in keys list
        i = self.keys.index((key, value))

        first_key = child.keys[0][0]
        i = i + 1 if first_key > key else i

        # Append child
        self.__append_child(i, child)

    def remove_key(self, i):
        """Remove the ith key.

        Keyword argument:
            i -- key's index
        """
        del self.keys[i]

    def remove_child(self, i):
        """Remove the ith child.

        Keyword argument:
            i -- child's index
        """
        del self.children[i]

    def __append_child(self, i, child):
        """Append a child to node.

        Keyword argument:
            i -- index where child should be inserted
            child -- a Node object or int
        """
        children1 = self.children[0:i]    # children before child
        children2 = self.children[i:]     # children after child

        # New children list
        self.children = children1 + [child] + children2

    @classmethod
    def object(cls, pos, keys, children):
        """Create a Node object from params.

        Keyword argument:
            pos -- node's file index
            values -- a tuple with position, keys and children
        """
        # Node's (keys, values)
        keys = list(zip(*[iter(keys)] * 2))

        # Return a Node object
        return cls(pos, keys=keys, children=children)

    def __eq__(self, other):
        """Equal comparison between nodes."""
        return self.pos == other.pos

class BTree():
    """Represent a on-disk BTree implementation.

    Properties:
        root -- a Node as root tree
        order -- BTree order (default 60)
    """
    root = Node(1)

    def __init__(self, filepath, order=60, **kwargs):
        """Construct a tree.

        Keyword argument:
            filepath -- path to save BTree
            order -- BTree order (default 60)
        """
        # Open file with tree
        self.__file = StructFile(filepath, 'i')

        # Load BTree's first 2 levels
        self.__bootstrap(order)

    @property
    def order(self):
        return self.__order

    @property
    def max_keys(self):
        return self.__order * 2

    @property
    def min_keys(self):
        return self.__order

    @property
    def max_children(self):
        return self.max_keys + 1

    @property
    def min_children(self):
        return self.__order + 1

    @property
    def node_len(self):
        return self.max_keys * 2 + self.max_children + 3

    def insert(self, key, value):
        """Insert key,value in the BTree.

        Keyword arguments:
            key -- key to be inserted
            value -- key's value
        """
        # Search for a leaf that can have the key
        father = self.root
        node = father
        i = father.search(key)

        while i is not None:
            father = node
            node = self.__get_node(node.children[i])
            i = node.search(key)

        # Here, the leaf was already found
        node.append_key(key, value)

        # If node is full, we need to break into parts
        if node.n_keys > self.max_keys:
            self.__split(father, node)
        else:
            # Save on-disk
            self.__save(node)

    def delete(self, key):
        """Delete a key from the BTree.

        Keyword arguments:
            key -- key to be deleted
        """
        # Search node with key
        node = self.root                            # start from root
        i = search(node.keys, key, lambda x: x[0])  # node.key's index
        j = i + 1 if i is not None else None

        while i is None and not node.is_leaf:
            father = node
            j = node.search(key)
            node = self.__get_node(node.children[j])
            i = search(node.keys, key, lambda x: x[0])

        # Key was not found
        if i is None:
            return

        # Here, we found the node with key
        # While node not a leaf, pass key to a leaf and then remove it
        while not node.is_leaf:
            k, v = node.keys[i]
            child = node.children[i + 1]

            # Swap keys
            node.keys[i] = child.keys[0]
            child.keys[0] = (k, v)

            # Save changes on-disk
            self.__save(node)

            # Update node
            father = node
            node = child
            i = 0

        # Just remove
        node.remove_key(i)
        self.__save(node)

        # If leaf has less keys then the minimum (underflow)...
        if node != self.root and node.n_keys < self.min_keys:
            # Rotate or join
            self.__rotajoin(father, node, j)

    def search(self, key, node=None):
        """Search a key in the BTree.

        Return value, if key was found. -1, otherwise.

        Keyword arguments:
            key -- key to be searched
            node -- node to start the search from.
        """
        # If node is None, node = root
        node = self.root if node is None else self.__get_node(node)

        # Try to find a key in node.keys
        i = search(node.keys, key, lambda x: x[0])

        # If didn't find, search in other node
        if i is None:
            # But if the current node is a leaf,
            # there is no other node
            if node.is_leaf:
                return None

            # Find node to search for the key
            i = node.search(key)
            node = node.children[i]

            # Search for key
            return self.search(key, node)
        else:
            # Return key's value
            return node.keys[i][1]

    def display(self, node=None, level=0):
        """String representation of a BTree."""
        node = self.root if node is None else self.__get_node(node)

        t = "\t" * level
        header = t + "#{}, {} keys, {} children"
        keys = t + "\tKeys: {}"
        children = t + "\tChildren: {}"

        pos = [self.__get_node(child).pos for child in node.children]

        if level == 0:
            print("Order: {}".format(self.order))

        print(header.format(node.pos, node.n_keys, node.n_children))
        print(keys.format(str(node.keys)))
        print(children.format(str(pos)))
        print('-' * 60)

        for child in node.children:
            self.display(child, level + 1)

    def check(self, node=None):
        """Return True if all nodes in tree follow the rules of a BTree."""
        node = self.root if node is None else self.__get_node(node)

        # Number of keys
        keys = node.n_keys >= self.min_keys and node.n_keys <= self.max_keys
        if not keys and node.pos != self.root.pos:
            raise ValueError('Node with {} keys. Interval should be [{}, {}] keys.'.format(node.n_keys,
                                                                                           self.min_keys,
                                                                                           self.max_keys))
        # Number of children
        if not node.is_leaf:
            children = node.n_children == node.n_keys + 1
            if not children:
                raise ValueError('Node with {} keys and {} children'.format(node.n_keys, node.n_children))

            # Children less than parent
            for i in range(0, node.n_keys):
                child = self.__get_node(node.children[i])
                less = [k < node.keys[i][0] for k, _ in child.keys]

                if not all(less):
                    raise ValueError('Child key greater or equal than parent key.')

            # Last child greater than parent
            i = node.n_keys
            child = self.__get_node(node.children[i])
            greater = [k > node.keys[-1][0] for k, _ in child.keys]

            if not all(greater):
                raise ValueError('Child key less or equal than parent key.')

        # Check recursively
        other = [self.check(child) for child in node.children]

        # Return True, if every thing is OK
        return all(other)

    def __bootstrap(self, order):
        """Get root from file if exists. Create, otherwise."""
        # Get tree's order
        o = self.__file.next()

        if o is not None:  # there is data in file
            # Set order
            self.__order = o

            # Get root's position
            pos = self.__file.next()
            self.root = self.__load(pos, True)
        else:
            self.__order = order            # set order
            self.__file.append([order])     # save order
            self.__save(self.root)          # save root

    def __load(self, pos, ld_children=False):
        """Load a node's data from file and return a Node object.

        Keyword argument:
            pos -- node's index in file
            ld_children -- When True, load all node's children (default False)
        """
        n_keys = self.__file.get(pos + 1)      # get number of keys
        n_children = self.__file.next()        # get number of children

        # Get keys
        keys = self.__file.get(self.__file.tell, n_keys * 2)

        # Get children
        i = self.__file.tell + (self.max_keys - n_keys) * 2
        children = self.__file.get(i, n_children)

        # Load children by its position
        if ld_children:
            children = [self.__load(p) for p in children]

        # Return a Node object
        return Node.object(pos, keys, children)

    def __get_child(self, node, i):
        """Get a node's child. If child is a number, load from file.

        Keyword arguments:
            node -- node with child
            i -- child's index in node
        """
        # Short name
        child = node.children[i]

        # Save, if loaded
        node.children[i] = self.__get_node(child)

        # Return loaded node
        return node.children[i]

    def __get_node(self, node):
        """Get a node. If node is a number, load from file.

        Keyword arguments:
            node -- a node
        """
        return node if type(node) is Node else self.__load(node)

    def __save(self, node):
        """Save node in file.

        Keyword arguments:
            node -- a node to be saved
        """
        # Get node's attributes
        values = node.to_list()

        # Complete keys and children with -1
        i = 3 + node.n_keys * 2 # end of keys

        keys = values[3:i]      # get keys
        children = values[i:]   # get children

        keys += [-1, -1] * (self.max_keys - node.n_keys)           # 2*order keys
        children += [-1] * (self.max_children - node.n_children)   # 2*order+1 children

        values = values[0:3] + keys + children                      # update values

        # Write node on-disk
        n = len(values)
        [self.__file.write(node.pos + i, [values[i]]) for i in range(n)]

    def __remove(self, node):
        """Remove a node from file.

        Keyword argument:
            node -- node to be removed
        """
        # If node to be removed is the root...
        if node == self.root:
            # Erase all data
            self.__file.truncate(self.__file.length)
            return

        # Number of nodes in file - size of one node
        # The last element in array is (len(array) - 1)
        last_i = self.__file.length - self.node_len

        # Get last node in file
        last = self.__load(last_i)

        if self.root.n_keys == 0:
            self.__get_child(self.root, 0)
            self.root.children[0].pos = self.root.pos
            self.root = self.root.children[0]
        elif last.pos != node.pos:
            # Need to update position
            # Find last's father to update position
            father = self.root
            key = last.keys[0][0]

            i = father.search(key)
            child = self.__get_node(father.children[i])

            while child.pos != last.pos:
                father = child
                i = father.search(key)
                child = self.__get_node(father.children[i])

            # Update father's child position and save
            father.children = [self.__get_node(child) for child in father.children]
            children_pos = [child.pos for child in father.children]
            j = children_pos.index(last.pos)

            father.children[j].pos = node.pos
            self.__save(father)

            # Update last's position and save
            last.pos = node.pos
            self.__save(last)

        # Delete last
        self.__file.truncate(self.node_len)

    def __split(self, father, child):
        """Split child.

        Keyword arguments:
            father -- a node with child in node.children
            child -- a node
        """
        # Get split index
        i = child.n_keys // 2

        # Get split key,value pair
        k, v = child.keys[i]

        # Split keys and children
        new_keys = child.keys[i + 1:]
        child_keys = child.keys[:i]

        new_children = child.children[i + 1:]
        child_children = child.children[:i + 1]

        # Create a new node
        node = Node(self.__file.length, keys=new_keys, children=new_children)

        # Save new node on-disk
        self.__save(node)

        # Check if it is root
        if father == child:
            # Create a new father for child
            father = Node(self.root.pos, keys=[(k,v)], children=[child, node])

            # Set new root as father
            self.root = father

            # Update child's file position (old root)
            child.pos = self.__file.length
            self.__save(child)
            self.__save(father)
        else:
            # Link the new node with father
            father.append(k, v, node)

            # If father is full, split father
            if father.n_keys > self.max_keys:

                # Grandparent starts at root
                grandpa = self.root

                # If there is a grandfather
                if father != self.root:
                    # Find grandfather
                    i = grandpa.search(k)
                    node = self.__get_node(grandpa.children[i])
                    i = node.search(k)

                    # While father not found in grandpa.children
                    while node != father:
                        grandpa = node
                        node = self.__get_node(node.children[i])
                        i = node.search(k)

                # Split again
                self.__split(grandpa, father)
            else:
                self.__save(father)

        # Update child's keys
        child.keys = child_keys
        child.children = child_children

        # Save changes
        self.__save(child)

    def __rotajoin(self, father, leaf, j):
        """Make a rotation, if possible. Join, otherwise.

        Keyword arguments:
            father -- a parent node
            leaf -- father's child
            j -- leaf's index on father
        """

        # Make sure the children are not just numbers
        left_brother = Node(-1)

        if j > 0:
            self.__get_child(father, j - 1)
            left_brother = father.children[j - 1]

        right_brother = Node(-1)

        if j < father.n_children - 1:
            self.__get_child(father, j + 1)
            right_brother = father.children[j + 1]

        # If any brother can lose a key
        if left_brother.n_keys > self.min_keys:
            # Rotate right
            self.__rotate_right(father, leaf, j)
        elif right_brother.n_keys > self.min_keys:
            # Rotate left
            self.__rotate_left(father, leaf, j)
        # No child is able to lose a key
        else:
            # Join nodes
            self.__join(father, j)

    def __rotate(self, father, child, ki, ci, fk):
        """Rotate to left/right.

        Keyword arguments:
            father -- a node
            child -- a node in father.children
            ki -- key's index
            ci -- child's index
            fk -- father's key index
        """
        k, v = father.keys[ki]                  # get key
        father.remove_key(ki)                   # to delete from father
        child.append_key(k, v)                  # and insert in child

        k, v = father.children[ci].keys[fk]     # get key
        father.children[ci].remove_key(fk)      # to delete from child
        father.append_key(k, v)                 # and insert in father

        # Update children
        if not father.children[ci].is_leaf:
            if fk == -1:
                child.children = [father.children[ci].children[fk]] + child.children
            else:
                child.children = child.children + [father.children[ci].children[fk]]

            father.children[ci].remove_child(fk)

        # Save on-disk
        self.__save(father.children[ci])
        self.__save(father)
        self.__save(child)

    def __rotate_right(self, father, child, j):
        """Rotate to right.

        Keyword arguments:
            father -- a node
            child -- a node in father.children
            j -- child's index
        """
        ki = j - 1  # key's index
        ci = j - 1  # child's index
        fk = -1     # father's key index

        self.__rotate(father, child, ki, ci, fk)

    def __rotate_left(self, father, child, j):
        """Rotate to left.

        Keyword arguments:
            father -- a node
            child -- a node in father.children
            j -- child's index
        """
        ki = j      # key's index
        ci = j + 1  # child's index
        fk = 0      # father's key index

        self.__rotate(father, child, ki, ci, fk)

    def __join(self, node, i):
        """Join leafs.

        Keyword argument:
            node -- father of nodes to be joined
            i -- child's position
        """
        # Left/right brother to merge
        ki = i if i == 0 else i - 1
        j = i + 1 if i == 0 else i - 1

        # Make sure nodes are loaded
        self.__get_child(node, i)
        self.__get_child(node, j)

        k, v = node.keys[ki]                   # get key
        node.remove_key(ki)                    # to remove from father
        node.children[i].append_key(k, v)     # and append on left child

        # Merge left child's keys to right/left's child keys in the left
        right = node.children[i]
        left = node.children[j]

        node.children[i].keys = list(left.keys) + list(right.keys)

        if j == i + 1:
            node.children[i].children = list(right.children) + list(left.children)
        else:
            node.children[i].children = list(left.children) + list(right.children)

        self.__save(node.children[i])

        # Remove right child
        node.remove_child(j)

        # Save changes on-disk
        self.__save(node)

        # Save removal on-disk
        self.__remove(left)

        if node.n_keys < self.min_keys:

            # If node is root...
            if node.pos == self.root.pos:
                if node.n_keys == 0:
                    # Remove a level from tree
                    self.__remove(right)
                    right.pos = self.root.pos

                    self.root = right
                    self.__save(self.root)
            else:
                # Find node's parent
                father = self.root                          # start from root
                key = node.keys[0][0]
                j = father.search(key)
                child = self.__get_node(father.children[j])
                i = search(child.keys, key, lambda x: x[0])  # node.key's index

                while i is None and not child.is_leaf:
                    father = child
                    j = father.search(key)
                    child = self.__get_node(father.children[j])
                    i = search(child.keys, key, lambda x: x[0])

                # Rotate or join... again
                self.__rotajoin(father, child, j)
