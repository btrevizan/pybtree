## Importing
```python
from pybtree import BTree
```

## Creating a new object
```python
# Create/open a new BTree with order 2
btree = BTree('records.btree', 2)
```

## Inserting
```python
btree.insert(50, 12)
btree.insert(30, 60)
btree.insert(19, 60)
btree.insert(92, 34)  # max keys reached

btree.insert(45, 67)
btree.insert(54, 92)
btree.insert(23, 48)
```

## Let's see our BTree
```python
btree.display()
```
Result:
```
Order: 2
#1, 1 keys, 2 children
    Keys: [(45, 67)]
    Children: [33, 17]
------------------------------------------------------------
    #33, 3 keys, 0 children
        Keys: [(19, 60), (23, 48), (30, 60)]
        Children: []
------------------------------------------------------------
    #17, 3 keys, 0 children
        Keys: [(50, 12), (54, 92), (92, 34)]
        Children: []
------------------------------------------------------------
```

## Searching
```python
btree.search(30)  # return 60
btree.search(19)  # return 60
btree.search(23)  # return 48
btree.search(10)  # return None
```

## Deleting
```python
btree.delete(45)  # remove the root only key, so the BTree makes a join operation
```
Result:
```
Order: 2
#1, 1 keys, 2 children
    Keys: [(50, 12)]
    Children: [33, 17]
------------------------------------------------------------
    #33, 3 keys, 0 children
        Keys: [(19, 60), (23, 48), (30, 60)]
        Children: []
------------------------------------------------------------
    #17, 2 keys, 0 children
        Keys: [(54, 92), (92, 34)]
        Children: []
------------------------------------------------------------
```
