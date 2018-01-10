# Getting Started
*pybtree* is a package the implements a **BTree on-disk**.

## Installation
```bash
$ pip3 install pybtree
```

## Dependencies
```bash
$ pip3 install pystrct
```

## Example
```python
from pybtree import BTree

# Open/create a BTree file
btree = BTree('records.btree')

# Insert the key 34 and value 68 associated
btree.insert(34, 68)

# Return 68
btree.search(34)
```
