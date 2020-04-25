import re

class treeNode:
    """FP树类的定义"""
    def __init__(self, nameValue, numOccur, parentNode):
        self.name = nameValue  # 存放节点名字的变量
        self.count = numOccur  # 计数器
        self.nodeLink = None  # 用于链接相似的元素项
        self.parent = parentNode  # 指向当前节点的父节点
        self.children = {}  # 存放节点的子节点

    def inc(self, numOccur):
        """对count变量增加给定值"""
        self.count += numOccur

    def disp(self, ind=1):
        """用于将树以文本形式显示"""
        print('  '*ind, self.name, ' ', self.count)
        for child in self.children.values():
            child.disp(ind+1)


def updateHeader(nodeToTest, targetNode):
    """
    更新头指针，建立相同元素之间的关系，例如： 左边的r指向右边的r值，就是后出现的相同元素 指向 已经出现的元素
    从头指针的nodeLink开始，一直沿着nodeLink直到到达链表末尾。这就是链表。
    性能：如果链表很长可能会遇到迭代调用的次数限制。
    :param nodeToTest: 满足minSup {所有的元素+(value, treeNode)}
    :param targetNode: Tree对象的子节点
    :return:
    """
    # 建立相同元素之间的关系，例如： 左边的r指向右边的r值
    while (nodeToTest.nodeLink is not None):
        nodeToTest = nodeToTest.nodeLink
    nodeToTest.nodeLink = targetNode

def updateTree(items, inTree, headerTable, count):
    """
    更新FP-tree，第二次遍历
    # 针对每一行的数据
    # 最大的key,  添加
    :param items: 满足minSup 排序后的元素key的数组（大到小的排序）
    :param inTree: 空的Tree对象
    :param headerTable: 满足minSup {所有的元素+(value, treeNode)}
    :param count: 原数据集中每一组Kay出现的次数
    :return:
    """
    # 取出 元素 出现次数最高的如果该元素在 inTree.children 这个字典中，就进行累加
    # 如果该元素不存在 就 inTree.children 字典中新增key，value为初始化的 treeNode 对象
    if items[0] in inTree.children:
        # 更新 最大元素，对应的 treeNode 对象的count进行叠加
        inTree.children[items[0]].inc(count)
    else:
        # 如果不存在子节点，我们为该inTree添加子节点
        inTree.children[items[0]] = treeNode(items[0], count, inTree)
        # 如果满足minSup的dist字典的value值第二位为null， 我们就设置该元素为 本节点对应的tree节点
        # 如果元素第二位不为null，我们就更新header节点
        if headerTable[items[0]][1] is None:
            # headerTable只记录第一次节点出现的位置
            headerTable[items[0]][1] = inTree.children[items[0]]
        else:
            # 本质上是修改headerTable的key对应的Tree的nodeLink值
            updateHeader(headerTable[items[0]][1], inTree.children[items[0]])
    if len(items) > 1:
        # 递归的调用，在items[0]的基础上，添加item0[1]做子节点， count只要循环的进行累计加和而已，统计出节点的最后的统计值
        updateTree(items[1:], inTree.children[items[0]], headerTable, count)

def createTree(dataSet, minSup=1):
    """
    生成FP-tree
    :param dataSet: dist{行：出现次数}的样本数据
    :param minSup: 最小的支持度
    :return:
        retTree  FP-tree
        headerTable 满足minSup {所有的元素+(value, treeNode)}
    """
    headerTable = {}  # 支持度>=minSup的dist{所有元素：出现的次数}
    for trans in dataSet:  # 循环 dist{行：出现次数}的样本数据，对所有的行进行循环，得到行里面的所有元素
        for item in trans:  # 统计每一行中，每个元素出现的总次数
            headerTable[item] = headerTable.get(item, 0) + dataSet[trans]
    for k in list(headerTable.keys()):  # python3中.keys()返回的是迭代器不是list,不能在遍历时对其改变。
        if headerTable[k] < minSup:
            del(headerTable[k])  # 删除 headerTable中，元素次数<最小支持度的元素
    freqItemSet = set(headerTable.keys())  # 满足minSup: set(各元素集合)
    if len(freqItemSet) == 0:   # 如果不存在，直接返回None
        return None, None
    for k in headerTable:
        headerTable[k] = [headerTable[k], None]  # 格式化： dist{元素key: [元素次数, None]}

    # 创建树
    retTree = treeNode('Null Set', 1, None)
    for tranSet, count in dataSet.items():   # 循环 dist{行：出现次数}的样本数据
        localD = {}  # localD = dist{元素key: 元素总出现次数}
        for item in tranSet:
            if item in freqItemSet:   # 判断是否在满足minSup的集合中
                localD[item] = headerTable[item][0]
        if len(localD) > 0:
            # p=key,value; 所以是通过value值的大小，进行从大到小进行排序
            # orderedItems 表示取出元组的key值，也就是字母本身，但是字母本身是大到小的顺序
            orderedItems = [v[0] for v in sorted(localD.items(), key=lambda p: p[1], reverse=True)]
            updateTree(orderedItems, retTree, headerTable, count)  # 填充树，通过有序的orderedItems的第一位，进行顺序填充 第一层的子节点。
    return retTree, headerTable

# 定义一个简单的数据集
def loadSimpDat():
    simpDat = [['r', 'z', 'h', 'j', 'p'],
               ['z', 'y', 'x', 'w', 'v', 'u', 't', 's'],
               ['z'],
               ['r', 'x', 'n', 'o', 's'],
               ['y', 'r', 'x', 'z', 'q', 't', 'p'],
               ['y', 'z', 'x', 'e', 'q', 's', 't', 'm']]
    return simpDat

# 实现数据集从列表到字典的类型转换
def createInitSet(dataSet):
    retDict = {}
    for trans in dataSet:
            retDict[frozenset(trans)] = 1
    return retDict

def ascendTree(leafNode, prefixPath):
    """
    迭代上溯整棵树(如果存在父节点，就记录当前节点的name值)
    :param leafNode: 查询的节点对于的nodeTree
    :param prefixPath: 要查询的节点值
    :return:
    """
    if leafNode.parent is not None:
        prefixPath.append(leafNode.name)
        ascendTree(leafNode.parent, prefixPath)

def findPrefixPath(basePat, treeNode):
    """
    遍历链表直到结尾，返回给定元素项结尾的所有路径
    :param basePat: 要查询的节点值
    :param treeNode: 查询的节点所在的当前nodeTree
    :return:
            condPats 对非basePat的倒叙值作为key,赋值为count数

    """
    condPats = {}
    while treeNode is not None:  # 对 treeNode的link进行循环
        prefixPath = []
        ascendTree(treeNode, prefixPath)  # 寻找改节点的父节点，相当于找到了该节点的频繁项集
        # 避免单独`Z`一个元素，添加了空节点
        if len(prefixPath) > 1:
            # 对非basePat的倒叙值作为key,赋值为count数
            # prefixPath[1:] 变frozenset后，字母就变无序了
            # condPats[frozenset(prefixPath)] = treeNode.count
            condPats[frozenset(prefixPath[1:])] = treeNode.count
        # 递归寻找改节点的下一个 相同值的链接节点
        treeNode = treeNode.nodeLink
    return condPats

def mineTree(inTree, headerTable, minSup, preFix, freqItemList):
    """
    创建条件FP树
    :param inTree: myFPtree
    :param headerTable: 满足minSup {所有的元素+(value, treeNode)}
    :param minSup: 最小支持项集
    :param preFix: preFix为newFreqSet上一次的存储记录，一旦没有myHead，就不会更新
    :param freqItemList: 用来存储频繁子项的列表
    :return:
    """
    # 通过value进行从小到大的排序， 得到频繁项集的key
    # 最小支持项集的key的list集合
    bigL = [v[0] for v in sorted(headerTable.items(), key=lambda p: str(p[1]))]
    # 循环遍历最频繁项集的key，从小到大的递归寻找对应的频繁项集
    for basePat in bigL:
        # preFix为newFreqSet上一次的存储记录，一旦没有myHead，就不会更新
        newFreqSet = preFix.copy()
        newFreqSet.add(basePat)

        freqItemList.append(newFreqSet)
        condPattBases = findPrefixPath(basePat, headerTable[basePat][1])
        # 构建FP-tree
        myCondTree, myHead = createTree(condPattBases, minSup)
        # 挖掘条件 FP-tree, 如果myHead不为空，表示满足minSup {所有的元素+(value, treeNode)}
        if myHead is not None:
            print('conditional tree for: ', newFreqSet)
            myCondTree.disp(1)
            # 递归 myHead 找出频繁项集
            mineTree(myCondTree, myHead, minSup, newFreqSet, freqItemList)


def main():
    # # 测试FP构建函数
    # simpDat = loadSimpDat()
    # print(simpDat)
    # initSet = createInitSet(simpDat)
    # print(initSet)
    # myFPtree, myHeaderTab = createTree(initSet, 3)
    # myFPtree.disp()

    # # 抽取条件模式基
    # simpDat = loadSimpDat()
    # initSet = createInitSet(simpDat)
    # myFPtree, myHeaderTab = createTree(initSet, 3)
    # print(findPrefixPath('x', myHeaderTab['x'][1]))
    # print(findPrefixPath('z', myHeaderTab['z'][1]))
    # print(findPrefixPath('r', myHeaderTab['r'][1]))

    # # 创建条件FP树
    # simpDat = loadSimpDat()
    # initSet = createInitSet(simpDat)
    # myFPtree, myHeaderTab = createTree(initSet, 3)
    # freqItems = []
    # mineTree(myFPtree, myHeaderTab, 3, set([]), freqItems)
    # print(freqItems)

    # 从新闻网站点击流中挖掘
    parseDat = [line.split() for line in open('kosarak.dat').readlines()]  # 导入数据集
    initSet = createInitSet(parseDat)  # 对初始数据集格式化
    myFPtree, myHeaderTab = createTree(initSet, 100000)  # 构建FP树，从中寻找至少被10万人浏览过的新闻报道
    myFreList = []  # 创建空列表保存频繁项集
    mineTree(myFPtree, myHeaderTab, 100000, set([]), myFreList)
    print(len(myFreList))
    print(myFreList)


if __name__ == "__main__":
    main()
