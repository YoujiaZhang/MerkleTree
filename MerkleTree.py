from Crypto.Hash import SHA256
from graphviz import Digraph
from random import randint
import copy
import math
import time

'''
创作者：张由甲
时间：2011.11.3

创建一棵 Merkle 树
'''

class TreeNode:
    '''
    树节点类
    '''
    def __init__(self, value, leftNode=None, rightNode=None, hash=None, childNum=None, depth=None, id=None, father=None, primeNum=None, hashIsRight=True, generation=None,):
        self.value = value          # 节点保存的数据
        self.leftNode = leftNode    # 节点的左孩子
        self.rightNode = rightNode  # 节点的右孩子
        self.hash = hash            # hash值
        self.childNum = childNum    # 节点拥有的孩子数量
        self.depth = depth          # 节点的高度
        self.id = id                # 唯一的标号
        self.father = father        # 父亲节点
        self.primeNum = primeNum    # 大素数
        self.hashIsRight = hashIsRight  # 该节点的hash值是否正确
        self.generation = generation    # 该节点的添加代

    def __str__(self):
        # 可以打印树中某个节点的信息
        return 'Node(value='+self.value+', prime='+self.primeNum+', hash='+self.hash+')'


class MerkleTree:
    '''
    Merkle 树用于保证数据的完整性
    一、查询某一个元素是否《存在》树上
    二、查询某一个元素是否《不在》树上
    '''

    def __init__(self):
        self.history = 1 # 创建节点的代数，初始化为第一代节点
        self.newNodes = []
        self.root = TreeNode(
            value='root',
            hash='',
            childNum=0,
            depth=0,
            id=str(time.time()),
            generation=self.history,
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
        # 如果给定构造的节点数据为空，返回Merkle树初始状态
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
                generation=self.history,
            )
            treeNodeData.append(copyNode)

        # 构造所有的中间节点 -> nodeQueue
        nodeQueue = []
        for index in range(0, len(treeNodeData), 2):
            mergeStrings = treeNodeData[index].value + \
                ' '+treeNodeData[index+1].value
            hashString = self.calculate_hash(
                treeNodeData[index].hash+treeNodeData[index+1].hash)
            mergeNode = TreeNode(
                value=mergeStrings,
                hash=hashString,
                leftNode=treeNodeData[index],
                rightNode=treeNodeData[index+1],
                depth=1,
                childNum=2,
                id=str(time.time()),
                primeNum=str(
                    int(treeNodeData[index].primeNum)*int(treeNodeData[index+1].primeNum)),
                generation=self.history,
            )
            treeNodeData[index].father = mergeNode
            treeNodeData[index+1].father = mergeNode
            nodeQueue.append(mergeNode)

        # 逐层向上合并节点
        while len(nodeQueue) > 1:
            temp = []
            for index in range(0, len(nodeQueue), 2):
                mergeStrings = nodeQueue[index].value + \
                    ' '+nodeQueue[index+1].value
                hashString = self.calculate_hash(
                    nodeQueue[index].hash+nodeQueue[index+1].hash)
                mergeNode = TreeNode(
                    value=mergeStrings,
                    hash=hashString,
                    depth=nodeQueue[index].depth+1,
                    childNum=nodeQueue[index].childNum +
                    nodeQueue[index+1].childNum,
                    leftNode=nodeQueue[index],
                    rightNode=nodeQueue[index+1],
                    id=str(time.time()),
                    primeNum=str(
                        int(nodeQueue[index].primeNum)*int(nodeQueue[index+1].primeNum)),
                    generation=self.history,
                )
                nodeQueue[index].father = mergeNode
                nodeQueue[index+1].father = mergeNode
                temp.append(mergeNode)

            # 一棵完全2叉树构建完成
            nodeQueue = temp
        return nodeQueue[0]

    def build_merkle_tree(self, nodeData, way='filling', sorted=False):
        if len(nodeData) == 0:
            print('构建了个寂寞')
            return

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
                    # print(newNodePrime, ' 重复！！')
                    continue
                else:
                    break
            rootPrime = str(int(rootPrime) * int(newNodePrime))
            thisTime = str(time.time())
            newNode = TreeNode(
                value=data,
                hash=self.calculate_hash(data+newNodePrime+thisTime),
                depth=0,
                childNum=0,
                id=thisTime,
                primeNum=newNodePrime,
                generation=self.history,
            )
            treeNodeData.append(newNode)
            print('节点构造完成：', str(newNode))

        if way == 'filling':
            self.root = self.bulid_complete_binary_tree(treeNodeData)
            self.newNodes = [self.root]

        elif way == 'imbalance':
            # 计算能构造一颗完全二叉树的节点数量
            treeDepth = int(math.log2(len(treeNodeData)))  # 向下取整

            if treeDepth == 0:
                offset = 0
            else:
                offset = 2**treeDepth

            # 分叉两个 子集
            # 子集1：可以构造一棵完全二叉树
            # 子集2：不足一颗完全二叉树
            treeNodeDataSub_1 = [treeNodeData[i] for i in range(0, offset)]
            treeNodeDataSub_2 = [treeNodeData[i] for i in range(offset, len(treeNodeData))]

            # print(len(treeNodeDataSub_1))
            # print(len(treeNodeDataSub_2))

            self.root = self.bulid_complete_binary_tree(treeNodeDataSub_1)
            # 将剩余的不足2的整数幂的节点，依次插入
            for node in treeNodeDataSub_2:
                self.insert(node, addAgain=True)

    def add(self, Data):
        self.history += 1
        rootPrime = self.root.primeNum
        # 构造每一个叶子节点
        treeNodeData = []
        while True:
            newNodePrime = self.generate_prime_number()
            if int(rootPrime) == 1:
                break
            if int(rootPrime) % int(newNodePrime) == 0 and int(rootPrime) > int(newNodePrime):
                # print(newNodePrime, ' 重复！！')
                continue
            else:
                break
        rootPrime = str(int(rootPrime) * int(newNodePrime))
        thisTime = str(time.time())
        newNode = TreeNode(
            value=Data,
            hash=self.calculate_hash(Data+newNodePrime+thisTime),
            depth=0,
            childNum=0,
            id=thisTime,
            primeNum=newNodePrime,
            generation=self.history,
        )
        treeNodeData.append(newNode)
        for node in treeNodeData:
            self.insert(node)

        print('节点构造完成：', str(newNode))
    
    def insert(self, node, addAgain=False):
        if addAgain == False:
            self.newNodes = []
        self.newNodes.append(node)
        canNodes = []
        searchQueue = []
        thisNode = self.root
        if 2**(thisNode.depth) != thisNode.childNum:
            # 说明这个节点是不够的
            searchQueue.append(self.root)
            while len(searchQueue) != 0:
                thisNode = searchQueue[0]
                searchQueue.pop(0)
                # print(str(thisNode))
                if thisNode.leftNode==None or thisNode.rightNode==None and thisNode.depth!=0:
                    print('check',str(thisNode))
                    canNodes.append(thisNode)
                
                if thisNode.rightNode and thisNode.rightNode.depth!=0 and 2**thisNode.rightNode.depth!=thisNode.rightNode.childNum:
                    searchQueue.append(thisNode.rightNode)
                if thisNode.leftNode and thisNode.leftNode.depth!=0 and 2**thisNode.leftNode.depth!=thisNode.leftNode.childNum:
                    searchQueue.append(thisNode.leftNode)
                
                # print('满足条件的孩子',[i.depth for i in searchQueue])
            thisNode = canNodes[len(canNodes)-1]
        # print('##################')
        # print(str(thisNode))
        # print('##################')
        if thisNode == self.root:
            #######################################
            # 原先的树已经满了，需要构建新的根，和右分支 #
            # 分两种情况：                          #
            # 一、原先的树不是“满”，而是完全没有       #
            # 二、第一步完成之后完全缺失右子树         #
            # 二、满树                             #
            #######################################

            if thisNode.value == 'root':
                # 第一种情况 原先的树不是“满”，而是完全没有
                # 构造新树根
                newRoot = TreeNode(
                    value=node.value,
                    hash=self.calculate_hash(node.hash),
                    depth=node.depth+1,
                    childNum=node.childNum+1,
                    leftNode=node,
                    rightNode=None,
                    id=str(time.time()),
                    primeNum=str(int(node.primeNum)),
                    generation=self.history,
                )
                node.father = newRoot
                self.root = newRoot  # 移植成功
                # 记录新加入的节点
                self.newNodes.append(newRoot)
                return

            elif thisNode.depth == 1 and thisNode.rightNode == None:
                # 第二种情况 第一步完成之后完全缺失右子树
                thisNode.value = thisNode.value+' '+node.value
                thisNode.hash = self.calculate_hash(
                    thisNode.leftNode.hash+node.hash)
                thisNode.childNum += 1
                thisNode.primeNum = str(
                    int(thisNode.primeNum)*int(node.primeNum))

                thisNode.rightNode = node
                node.father = thisNode
                return

            # 第三  种情况 满树
            nowTreeDepth = thisNode.depth
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
                    generation=self.history,
                )
                self.newNodes.append(newright_temp)
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
                primeNum=str(int(thisNode.primeNum)*int(newright.primeNum)),
                generation=self.history,
            )
            self.newNodes.append(newRoot)
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
            if thisNode != None and thisNode.depth==1:
                if thisNode.leftNode == None:
                    thisNode.leftNode = node
                else:
                    thisNode.rightNode = node
                node.father = thisNode

            # 第二种情况 先构建右分支（左延伸）
            if thisNode != None and thisNode.depth != 1:

                if thisNode.rightNode == None:
                    nowTreeDepth = thisNode.leftNode.depth
                else:
                    nowTreeDepth = thisNode.rightNode.depth
                
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
                        generation=self.history,
                    )
                    self.newNodes.append(newright_temp)
                    newright.father = newright_temp
                    newright = newright_temp
                # 循环结束 构建右分支完成，并进行添加

                if thisNode.rightNode == None:
                    thisNode.rightNode = newright
                else:
                    thisNode.leftNode = newright

                newright.father = thisNode

            ######################################
            # 统一更新每个节点的数据                 #
            ######################################
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

    def merkle_path(self, proofPath):
        '''
        描述：从叶子到树根的路径称为 Merkle Path ，它可以用来证明事务(string)的存在
        参数：proofPath 已经构建好的证明路径
        '''
        if proofPath == None:
            print('请检查验证路径的合理性')
            return
        queue = [proofPath]
        thisNode = None
        while len(queue) != 0:
            thisNode = queue[0]
            queue.pop(0)
            if thisNode.leftNode:
                queue.append(thisNode.leftNode)
            if thisNode.rightNode:
                queue.append(thisNode.rightNode)

        thisNode = thisNode.father
        while thisNode != None:
            mergeHash = ''
            if thisNode.leftNode:
                mergeHash = thisNode.leftNode.hash
            if thisNode.rightNode:
                mergeHash = mergeHash + thisNode.rightNode.hash

            mergeHash = self.calculate_hash(mergeHash)
            if thisNode.hash == mergeHash:
                thisNode.hashIsRight = True
            else:
                # print('error')
                thisNode.hashIsRight = False

            thisNode.hash = mergeHash
            thisNode = thisNode.father

        dot = self.show(proofPath, proof=True)
        if proofPath.hashIsRight:
            dot.attr(label=r'\nMerkle tree is complete')
        else:
            dot.attr(label=r'\nMerkle tree has been modified')
        return dot

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
                        proofNode.rightNode.value = 'Ref Hash'
                    proofNode.value = '✱'
                    proofNode = proofNode.leftNode

                elif copynode.rightNode and int(copynode.rightNode.primeNum) % int(prime) == 0:
                    copynode = copynode.rightNode

                    if proofNode.leftNode:
                        proofNode.leftNode.leftNode = None
                        proofNode.leftNode.rightNode = None
                        proofNode.leftNode.value = 'Ref Hash'
                    proofNode.value = '✱'
                    proofNode = proofNode.rightNode
                else:
                    break
            proofNode.value = 'Target'
            proofPath.value = 'Root'

        else:
            copynode = None
            proofPath = None
            print('没有这个节点的信息')

        if showNode == True:
            self.show(copynode)

        return copynode, proofPath

    def tampering_test(self, proofPath, Index):
        if proofPath == None:
            print('请检查验证路径的合理性')
            return
        proofPath = copy.deepcopy(proofPath)
        queue = [proofPath]
        count = 0
        thisNode = None
        while len(queue) != 0:
            thisNode = queue[0]
            queue.pop(0)
            if not(thisNode.leftNode or thisNode.rightNode):
                count += 1
            if count == Index:
                thisNode.value = 'Modified'
                thisNode.hash = 'chaos'
                break
            if thisNode.leftNode:
                queue.append(thisNode.leftNode)
            if thisNode.rightNode:
                queue.append(thisNode.rightNode)
        return proofPath

    def getTreePrime(self,):
        allPrime = []
        queue = [self.root]
        thisNode = None
        while len(queue) != 0:
            thisNode = queue[0]
            queue.pop(0)
            if thisNode.leftNode == None and thisNode.rightNode == None:
                allPrime.append(thisNode.primeNum)
            if thisNode.leftNode:
                queue.append(thisNode.leftNode)
            if thisNode.rightNode:
                queue.append(thisNode.rightNode)
        return allPrime

    def compare(self, showHistory=False):
        dot = self.show()
        if showHistory == False:
            for node in self.newNodes:
                dot.node(node.id, _attributes={'fillcolor': '#FFCDD2'})
        else:
            allColor = ['#FFCDD2', '#FFE0B2', '#FFF9C4',
                        '#C8E6C9', '#B2EBF2', '#BBDEFB', '#E1BEE7']
            queue = [self.root]
            thisNode = None
            while len(queue) != 0:
                thisNode = queue[0]
                queue.pop(0)
                dot.node(thisNode.id, _attributes={
                    'fillcolor': allColor[abs(thisNode.generation-self.history) % len(allColor)]
                }
                )
                if thisNode.leftNode:
                    queue.append(thisNode.leftNode)
                if thisNode.rightNode:
                    queue.append(thisNode.rightNode)
        return dot
    
    def remove(self, prime):
        if int(self.root.primeNum)%int(prime) != 0:
            print('这棵树上没有这个叶子')
            return

        queue = [self.root]
        thisNode = None
        while len(queue) != 0:
            thisNode = queue[0]
            queue.pop(0)
            if thisNode.leftNode==None and thisNode.rightNode==None and thisNode.primeNum==str(prime):
                break
            if thisNode.leftNode:
                queue.append(thisNode.leftNode)
            if thisNode.rightNode:
                queue.append(thisNode.rightNode)
        
        print(str(thisNode))
        print(str(thisNode.father))
        hisFather = thisNode.father
        if hisFather.leftNode==thisNode:
            hisFather.leftNode = None
        elif hisFather.rightNode==thisNode:
            hisFather.rightNode = None
        
        # 自下而上的矫正数据
        while hisFather:
            if hisFather.leftNode and hisFather.leftNode.childNum<=0 and hisFather.leftNode.depth!=0:
                hisFather.leftNode = None
            if hisFather.rightNode and hisFather.rightNode.childNum<=0 and hisFather.rightNode.depth!=0:
                hisFather.rightNode = None
                
            MergeString = ''
            MergeHash = ''
            MergePrime = 1

            if hisFather.leftNode:
                MergeString = hisFather.leftNode.value
                MergeHash = hisFather.leftNode.hash
                MergePrime = int(hisFather.leftNode.primeNum)
            if hisFather.rightNode:
                MergeString = MergeString + ' ' + hisFather.rightNode.value
                MergeHash = MergeHash + hisFather.rightNode.hash
                MergePrime = MergePrime * int(hisFather.rightNode.primeNum)

            hisFather.childNum -= 1
            hisFather.value = MergeString
            hisFather.hash = self.calculate_hash(MergeHash)
            hisFather.primeNum = str(MergePrime)
            hisFather = hisFather.father
        
        # 树根矫正
        if self.root.childNum == 0:
            self.root = TreeNode(
                value='root',
                hash='',
                childNum=0,
                depth=0,
                id=str(time.time()),
                generation=self.history,
                primeNum=self.generate_prime_number()
            )
        # 树根到叶子的路径矫正
        while self.root.depth>=2 and ((self.root.leftNode!=None)^(self.root.rightNode!=None)):
            if self.root.leftNode:
                self.root = self.root.leftNode
            elif self.root.rightNode:
                self.root = self.root.rightNode
            self.root.father = None
        return

    def show(self, node=None, proof=False):
        if node == None:
            node = self.root
        dot = Digraph(name='MerkleTree', format='png')

        # 标注树的高度
        for i in range(node.depth+1):
            dot.node(
                name=str(i),
                label='depth : '+str(node.depth-i),
                _attributes={'color': '#FFFFFF'})

        for i in range(node.depth):
            dot.edge(str(i), str(i+1), _attributes={'arrowhead': 'none', 'color': '#FFFFFF'})

        queue = [node]
        count = 0
        while len(queue) != 0:
            temp = []
            for node_i in queue:
                nodeString = 'childNum:' + str(node_i.childNum)

                if len(node_i.value) > 8:
                    strings = str(node_i.value).split(' ')
                    strsL = len(strings)-1
                    nodeString = strings[0] + ' ~ ' + \
                        strings[strsL] + '\n' + nodeString
                else:
                    nodeString = node_i.value + '\n' + nodeString
                node_color = '#FFFFFF'

                if proof == True:
                    if node_i.value == 'Ref Hash':
                        node_color = '#FFA500'
                        nodeString = node_i.value

                    elif node_i.value == 'Target':
                        node_color = '#BBDEFB'
                        nodeString = node_i.value
                    elif node_i.value == 'Modified':
                        node_color = '#E0E0E0'
                        nodeString = node_i.value
                    else:
                        node_color = '#C8E6C9'
                        nodeString = '√'

                    if node_i.hashIsRight == False:
                        node_color = '#FFCDD2'
                        nodeString = '✕'

                    if not(node_i.leftNode or node_i.rightNode):
                        count += 1
                        nodeString = str(count)+'\n'+nodeString

                dot.node(
                    name=node_i.id,
                    label=nodeString,
                    style='filled',
                    fillcolor=node_color)

                if node_i.leftNode:
                    temp.append(node_i.leftNode)
                    dot.edge(node_i.id, node_i.leftNode.id)

                if node_i.rightNode:
                    temp.append(node_i.rightNode)
                    dot.edge(node_i.id, node_i.rightNode.id)

            queue = temp
        # dot.view()
        return dot
