from Crypto.Hash import SHA256
import math

class TreeNode:
    def __init__(self, value, leftNode=None, rightNode=None):
        self.value = value
        self.leftNode = leftNode
        self.rightNode = rightNode

class MerkleTree:
    def __init__(self):
        self.root = TreeNode('root')

    def calculate_hash(self, data):
        bytes_data = bytearray(data, "utf-8")
        h = SHA256.new()
        h.update(bytes_data)
        return h.hexdigest()

    def build_merkle_tree(self, nodeData):
        treeNodeData = [TreeNode(self.calculate_hash(data)) for data in nodeData]
        treeDepth = math.ceil(math.log2(len(treeNodeData)))

        for i in range(len(treeNodeData)):
            child_L = i * 2 + 1
            child_R = i * 2 + 2
            if child_L < len(treeNodeData):
                treeNodeData[i].leftNode = treeNodeData[child_L]
            if child_R < len(treeNodeData):
                treeNodeData[i].rightNode = treeNodeData[child_R]
                
        return treeNodeData[0]


