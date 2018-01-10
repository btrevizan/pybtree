# pybtree's API

`class` pybtree.**BTree**(*filepath, order*): return a BTree object.

- `string` **filepath**: relative/absolute path to a BTree file.
- `int` **order**: minimum number of keys per node *(default 60)*. Once a BTree is created,
the `order` doesn't need to be defined.

### Methods
**insert**(*key, value*): insert a `key` with the associated `value`.
- `int` **key**: a unique key to be inserted.
- `int` **value**: value associated with key.

---
`int` **search**(*key*): search for a `key` and return its `value`. Return `None`, if key does not exist.

---
**delete**(*key*): delete a `key` from BTree.

---
**display**(): print the BTree's nodes with levels.

---
`bool` **check**(): look for inconsistencies in the BTree. Raise `ValueError`, if found some inconsistency.
Return True, otherwise.

## Properties
`int` **order**: btree's order. Equivalente to `min_keys`.

---
`int` **max_keys**: maximum number of keys per node (`2 * order`).

---
`int` **min_keys**: minimum number of keys per node.

---
`int` **max_children**: maximum number of children per node (`max_keys + 1`).

---
`int` **min_children**: minimum number of children per node (`min_keys + 1`).

---
`int` **node_len**: number of integers numbers used to save a node in file.
