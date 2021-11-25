# MerkleTree
[Chinese](../README.md)

## Initialization

```
from MerkleTree import *

## Build a Merkle tree
mt = MerkleTree()
# Construct data -> nodeData
nodeData = []
# Build a tree, method selection imbalance
mt.build_merkle_tree(nodeData, way='imbalance')
# Show
mt.show()
```
<div align=center>
<img src="../images/init.svg"/>
</div>

## Add
```
import random

## Build a random data
num = random.randint(1,99)
# Add to the tree
mt.add(str(num))
# Show
mt.show()
```
<div align=center>
<img src="../images/add.svg"/>
</div>

```
# Add some more nodes, construct 10 nodes
for _ in range(10):
    num = random.randint(1,99)
    mt.add(str(num))

# Show
mt.show()
```
<div align=center>
<img src="../images/add2.svg"/>
</div>

There we are, a "leafy" tree. We can mark the new nodes in the tree, with the most recently added nodes marked in red, as shown below.

```
mt.compare()
```
<div align=center>
<img src="../images/compare.svg"/>
</div>

The graph shows the two rightmost nodes as the last ones added to the tree. We can also show each time a node is added, with the same batch of added nodes labeled a certain color (vertically).

<div align=center>
<img src="../images/compare2.svg"/>
</div>

## Query

By constantly adding nodes, we can have a very lush tree.    
Sometimes it is this tree that we will work with queries on, in two ways.
- Proving if a data is **existing**
- Prove if a data is **not present**

Analysis.
I was exposed to **RSA** in my undergraduate studies of cryptography. One of the keys to security is the factorization of the large prime $P$. It is easy to verify if a number is a factor of this $P$; but it is difficult to split all the factors of this large prime number. So, I would like to use this method.
- Generate a random prime number for each "leaf"
- Bottom-up, the "number" of the parent node is the product of the "numbers" of the children.

PS: The last time I used this idea was when I was doing [**Leetcode 49. group anagrams**](https://leetcode.com/problems/group-anagrams/)

```
# Get all the data of the whole tree with its own prime id
mt.getTreePrime()

# ['227', '331', '797', '941', '877', '191', '173', '577', '563', '409', '353']

# Based on the known prime ids it works
mynode, proofPath = mt.search(mt.getTreePrime()[5])

# show
mt.show(mynode)
```
<div align=center>
<img src="../images/search.svg"/>
</div>

The *proofPath* variable holds the **Merkle path** that proves that this node really exists.

## Merkle path validation

By feeding the resulting *proofPath* variable into the `merkle_path` function, it is possible to visualize whether the path is correct or not.
```
## Verify that the path meets the conditions
mt.merkle_path(proofPath)
```
<div align=center>
<img src="../images/merklePath.svg"/>
</div>

Explanation of the colors in the image.
- **orange**: indicates the testifying hash value that needs to be provided to the "requester".
- **blue**: the node that the "requester" wants to prove exists.
- **Green**: the node whose hash value was successfully verified.

When we send the orange nodes to the "requester", we may encounter a **data tampering** situation. At this point, we can verify again and see if tampering can be detected.
```
# tampering with hash data of node #3
proofPath_2 = mt.tampering_test(proofPath,2)

# Verify that
mt.merkle_path(proofPath_2)
```
<div align=center>
<img src="../images/merklePath2.svg"/>
</div>

## Delete
When data in a tree is no longer needed, leaving it in would take up space, but deleting one of the data and rebuilding the tree would require computing a lot of hash operations. To avoid this problem, our tree can delete the nodes that need to be deleted.
```
# Remove a node from this tree
mt.remove(mt.getTreePrime()[4])
mt.show()
```
<div align=center>
<img src="../images/delete.svg"/>
</div>

After the delete operation, we see that the 4th node has been deleted, and we can continue to delete or add nodes.
```
# Delete the 3rd node five times in a row
for i in range(5):
    mt.remove(mt.getTreePrime()[2])
mt.show()
```

<div align=center>
<img src="../images/delete2.svg"/>
</div>

After deleting a large number of nodes, the tree will still maintain the minimum height that satisfies the condition. The minimum height ensures that add, query, and delete operations are done with minimal cost.
We can go ahead and check that the hash value of the entire tree is maintained correctly.

<div align=center>
<img src="../images/delete3.svg"/>
</div>
