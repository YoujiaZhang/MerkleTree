
from ast import NodeTransformer
from Crypto.Hash import SHA256
import math
from graphviz import Digraph
import time
from random import randint
import copy

class TreeNode:
    def __init__(self, value, leftNode=None, rightNode=None, hash=None, leaf=None, childNum=None, depth=None, id=None, father=None, primeNum=None):
        self.value = value         # 节点保存的数据
        self.leftNode = leftNode   # 节点的左孩子
        self.rightNode = rightNode  # 节点的右孩子
        self.hash = hash           # hash值
        self.childNum = childNum   # 节点拥有的孩子数量
        self.depth = depth         # 节点的高度
        self.id = id               # 唯一的标号
        self.father = father       # 父亲节点
        self.primeNum = primeNum   # 大素数

    def __str__(self):
        return 'Node(value='+self.value+', prime='+self.primeNum+', hash='+self.hash+')'


class MerkleTree:
    '''
    Merkle 树用于保证数据的完整性
    一、查询某一个元素是否《存在》树上
    二、查询某一个元素是否《不在》树上
    '''

    def __init__(self):
        self.root = TreeNode(
            value='root',
            childNum=0,
            depth=0,
            id=str(time.time()),
            primeNum=self.generate_prime_number()
        )

    def calculate_hash(self, data):
        bytes_data = bytearray(data, "utf-8")
        h = SHA256.new()
        h.update(bytes_data)
        return str(h.hexdigest())

    def miller_rabin(self, p):
        if p == 1:
            return False
        if p == 2:
            return True
        if p % 2 == 0:
            return False
        m, k, = p - 1, 0
        while m % 2 == 0:
            m, k = m // 2, k + 1
        a = randint(2, p - 1)
        x = pow(a, m, p)
        if x == 1 or x == p - 1:
            return True
        while k > 1:
            x = pow(x, 2, p)
            if x == 1:
                return False
            if x == p - 1:
                return True
            k = k - 1
        return False

    def is_prime(self, p, r=40):
        for _ in range(r):
            if self.miller_rabin(p) == False:
                return False
        return True

    def generate_prime_number(self, index=10):
        num = 0
        for _ in range(index):
            num = num * 2 + randint(0, 1)
        while self.is_prime(num) == False:
            num = num + 1
        return str(num)

    def bulid_complete_binary_tree(self, treeNodeData):
        '''
        功能：构造一颗完全二叉树
        '''
        if len(treeNodeData) == 0:
            return self.root
        # 计算能构造一颗完全二叉树的节点数量
        treeDepth = math.ceil(math.log2(len(treeNodeData)))

        # 为整棵树补充需要的节点（将最后一个节点复制若干次）
        for _ in range(2**treeDepth - len(treeNodeData)):
            copyNodeString = treeNodeData[len(treeNodeData)-1].value
            copyNodeHash = treeNodeData[len(treeNodeData)-1].hash
            copyNode = TreeNode(
                value=copyNodeString,
                hash=self.calculate_hash(copyNodeHash),
                depth=0,
                childNum=0,
                id=str(time.time()),
                primeNum=self.generate_prime_number(),
            )
            treeNodeData.append(copyNode)

        # 构造所有的中间节点 -> nodeQueue
        nodeQueue = []
        for index in range(0, len(treeNodeData), 2):
            mergeStrings = treeNodeData[index].value+' '+treeNodeData[index+1].value
            hashString = self.calculate_hash(treeNodeData[index].hash+treeNodeData[index+1].hash)
            mergeNode = TreeNode(
                value=mergeStrings,
                hash=hashString,
                leftNode=treeNodeData[index],
                rightNode=treeNodeData[index+1],
                depth=1,
                childNum=2,
                id=str(time.time()),
                primeNum=str( int(treeNodeData[index].primeNum)*int(treeNodeData[index+1].primeNum))
                )
            treeNodeData[index].father = mergeNode
            treeNodeData[index+1].father = mergeNode
            nodeQueue.append(mergeNode)

        # 逐层向上合并节点
        while len(nodeQueue) > 1:
            temp = []
            for index in range(0, len(nodeQueue), 2):
                mergeStrings = nodeQueue[index].value+' '+nodeQueue[index+1].value
                hashString = self.calculate_hash(nodeQueue[index].hash+nodeQueue[index+1].hash)
                mergeNode = TreeNode(
                    value=mergeStrings,
                    hash=hashString,
                    depth=nodeQueue[index].depth+1,
                    childNum=nodeQueue[index].childNum +
                    nodeQueue[index+1].childNum,
                    leftNode=nodeQueue[index],
                    rightNode=nodeQueue[index+1],
                    id=str(time.time()),
                    primeNum=str(int(nodeQueue[index].primeNum)*int(nodeQueue[index+1].primeNum))
                    )
                nodeQueue[index].father = mergeNode
                nodeQueue[index+1].father = mergeNode
                temp.append(mergeNode)

            # 一棵完全2叉树构建完成
            nodeQueue = temp
        return nodeQueue[0]

    def build_merkle_tree(self, nodeData, way='filling', sorted=False):
        # 将每一个节点数据构造节点
        if sorted == True:
            nodeData = [int(i) for i in nodeData]
            nodeData.sort()
            nodeData = [str(i) for i in nodeData]

        rootPrime = 1
        # 构造每一个叶子节点
        treeNodeData = []
        for data in nodeData:
            while True:
                newNodePrime = self.generate_prime_number()
                if int(rootPrime) == 1:
                    break
                if int(rootPrime) % int(newNodePrime) == 0 and int(rootPrime) > int(newNodePrime):
                    print(newNodePrime, ' 重复！！')
                    continue
                else:
                    break
            rootPrime = str(int(rootPrime) * int(newNodePrime))
            print(newNodePrime)
            newNode = TreeNode(
                value=data,
                hash=self.calculate_hash(data+'+'+newNodePrime),
                depth=0,
                childNum=0,
                id=str(time.time()),
                primeNum=newNodePrime,
            )
            treeNodeData.append(newNode)

        if way == 'filling':
            self.root = self.bulid_complete_binary_tree(treeNodeData)

        elif way == 'imbalance':
            # 计算能构造一颗完全二叉树的节点数量
            treeDepth = int(math.log2(len(treeNodeData))) # 向下取整

            if treeDepth == 0:
                offset = 0
            else:
                offset = 2**treeDepth

            # 分叉两个 子集
            # 子集1：可以构造一棵完全二叉树
            # 子集2：不足一颗完全二叉树
            treeNodeDataSub_1 = [treeNodeData[i] for i in range(0, offset)]
            treeNodeDataSub_2 = [treeNodeData[i] for i in range(offset, len(treeNodeData))]

            print(len(treeNodeDataSub_1))
            print(len(treeNodeDataSub_2))

            self.root = self.bulid_complete_binary_tree(treeNodeDataSub_1)

            # 将剩余的不足2的整数幂的节点，依次插入
            for node in treeNodeDataSub_2:
                self.insert(node)

    def insert(self, node):
        searchQueue = []
        thisNode = self.root

        if 2**(thisNode.depth) != thisNode.childNum:
            # 说明这个节点是不够的
            searchQueue.append(self.root)
            while len(searchQueue) != 0:
                thisNode = searchQueue[0]
                searchQueue.pop(0)

                # print('父亲',thisNode.depth)
                if thisNode.leftNode != None and thisNode.leftNode.depth != 0 and 2**thisNode.leftNode.depth != thisNode.leftNode.childNum:
                    searchQueue.append(thisNode.leftNode)
                if thisNode.rightNode != None and thisNode.rightNode.depth != 0 and 2**thisNode.rightNode.depth**2 != thisNode.rightNode.childNum:
                    searchQueue.append(thisNode.rightNode)
                # print('满足条件的孩子',[i.depth for i in searchQueue])

        if thisNode == self.root:
            #######################################
            # 原先的树已经满了，需要构建新的根，和右分支 #
            # 分两种情况：                          #
            # 一、原先的树不是“满”，而是完全没有       #
            # 二、满树                             #
            #######################################
            nowTreeDepth = thisNode.depth
            newright = node
            for i in range(nowTreeDepth):
                newright_temp = TreeNode(
                    value=node.value,
                    hash=self.calculate_hash(newright.hash),
                    depth=newright.depth+1,
                    leftNode=newright,
                    childNum=1,
                    id=str(time.time()),
                    primeNum=newright.primeNum,
                )
                newright.father = newright_temp
                newright = newright_temp
            # 循环结束 构建右分支完成，并进行添加

            # 构造新树根
            newRoot = TreeNode(
                value=thisNode.value+' '+newright.value,
                hash=self.calculate_hash(thisNode.hash+newright.hash),
                depth=thisNode.depth+1,
                childNum=thisNode.childNum+newright.childNum,
                leftNode=thisNode,
                rightNode=newright,
                id=str(time.time()),
                primeNum=str(int(thisNode.primeNum)*int(newright.primeNum))
            )
            thisNode.father = newRoot
            newright.father = newRoot
            self.root = newRoot  # 移植成功

        else:
            #######################################
            # 在右分支上进行添加节点，补充整棵树        #
            # 分两种情况：                          #
            # 1. 在左叶子节点的旁边直接添加右叶子节点   #
            # 2. 添加右边的分支，然后作为其左叶子节点添加#
            #######################################

            # 第一种情况 直接添加
            if thisNode != None and thisNode.depth == 1 and thisNode.rightNode == None:
                thisNode.rightNode = node
                node.father = thisNode

            # 第二种情况 先构建右分支（左延伸）
            if thisNode != None and thisNode.depth != 1 and thisNode.rightNode == None:

                nowTreeDepth = thisNode.leftNode.depth
                newright = node
                for _ in range(nowTreeDepth):
                    newright_temp = TreeNode(
                        value=node.value,
                        hash=self.calculate_hash(newright.hash),
                        depth=newright.depth+1,
                        leftNode=newright,
                        childNum=1,
                        id=str(time.time()),
                        primeNum=newright.primeNum,
                    )
                    newright.father = newright_temp
                    newright = newright_temp
                # 循环结束 构建右分支完成，并进行添加

                thisNode.rightNode = newright
                newright.father = thisNode

            # 自下而上更新添加新节点之后，沿路的节点信息
            while thisNode != None:
                MergeString = ''
                MergeHash = ''
                MergePrime = 1
                if thisNode.leftNode != None:
                    MergeString = thisNode.leftNode.value
                    MergeHash = thisNode.leftNode.hash
                    MergePrime = int(thisNode.leftNode.primeNum)
                if thisNode.rightNode != None:
                    MergeString = MergeString + ' ' + thisNode.rightNode.value
                    MergeHash = MergeHash + thisNode.rightNode.hash
                    MergePrime = MergePrime * int(thisNode.rightNode.primeNum)

                thisNode.value = MergeString
                thisNode.hash = self.calculate_hash(MergeHash)
                thisNode.childNum += 1
                thisNode.primeNum = str(MergePrime)
                thisNode = thisNode.father

    def merkle_path(self, prime):
        '''
        从叶子到树根的路径称为 Merkle Path ，它可以用来证明事务(string)的存在
        '''
        searchNode = self.search(prime=int(prime))
        if searchNode != None:
            # hisFather = searchNode.father
            # proofPath = TreeNode(
            #         value=hisFather.value,
            #         hash=hisFather.hash,
            #         primeNum=hisFather.primeNum
            #         )
            # child_1 = TreeNode(
            #         value=searchNode.value,
            #         hash=searchNode.hash,
            #         primeNum=searchNode.primeNum
            #     )
            # while True:
            #     child_1 = hisFather
            #     mergeHash = ''
            #     if hisFather.leftNode and hisFather.rightNode:
            #         if hisFather.leftNode == searchNode:
            #             mergeHash = searchNode.hash+hisFather.rightNode.hash
            #             proofPath.leftNode = child_1
            #         else:
            #             mergeHash = hisFather.leftNode.hash+searchNode.hash
            #             hisFather.leftNode = None
            #             proofPath.rightNode = child_1
            #     else:
            #         if hisFather.leftNode:
            #             proofPath.leftNode = child_1
            #         if hisFather.rightNode:
            #             proofPath.rightNode = child_1
            #         mergeHash = searchNode.hash

            #     print(self.calculate_hash(mergeHash) == hisFather.hash)

            #     searchNode = hisFather
            #     hisFather = searchNode.father
            #     child_1 = proofPath

            #     if hisFather.primeNum == self.root.primeNum:
            #         break
            self.show(proofPath)

    def search(self, prime, showNode=False):
        # 保证数据类型正确
        prime = int(prime)
        # 复制这棵树
        proofNode = copy.deepcopy(self.root)
        proofPath = proofNode

        copynode = self.root
        if int(copynode.primeNum) % prime == 0:
            # 如果是 叶子节点 就退出循环
            while copynode.leftNode or copynode.rightNode:
                if copynode.leftNode and int(copynode.leftNode.primeNum) % int(prime) == 0:
                    copynode = copynode.leftNode
                    
                    if proofNode.rightNode:
                        proofNode.rightNode.leftNode = None
                        proofNode.rightNode.rightNode = None

                    proofNode.rightNode.value = 'leaf'
                    proofNode = proofNode.leftNode

                elif copynode.rightNode and int(copynode.rightNode.primeNum) % int(prime) == 0:
                    copynode = copynode.rightNode
                    
                    if proofNode.leftNode:
                        proofNode.leftNode.leftNode = None
                        proofNode.leftNode.rightNode = None
                    proofNode.leftNode.value = 'leaf'
                    proofNode = proofNode.rightNode
                else:
                    break
        else:
            copynode = None
            proofNode = None
            print('没有这个节点的信息')

        if showNode == True:
            self.show(copynode)
        
        return copynode, proofPath

    def show(self, node=None):
        if node == None:
            node = self.root
        dot = Digraph(name='MerkleTree', format='png')
        queue = [node]

        while len(queue) != 0:
            temp = []
            for node_i in queue:
                nodeString = node_i.value+'\n'+'childNum:' + \
                    str(node_i.childNum)+' depth:'+str(node_i.depth)

                dot.node(name=node_i.id, label=nodeString, style='filled', fillcolor='#FFA500')

                if node_i.leftNode:
                    temp.append(node_i.leftNode)
                    dot.edge(node_i.id, node_i.leftNode.id)

                if node_i.rightNode:
                    temp.append(node_i.rightNode)
                    dot.edge(node_i.id, node_i.rightNode.id)

            queue = temp
        dot.view()
