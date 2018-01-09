# pybtree
[![docs](https://readthedocs.org/projects/pybtree/badge/?version=latest)](http://pybtree.readthedocs.io/en/latest/?badge=latest)

*pybtree* is a package the implements a **BTree on-disk**.

## Installation
```bash
$ pip3 install pybtree
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

## Docs and stuff
You can find docs, api and examples in [here](http://pybtree.readthedocs.io/en/latest/).

