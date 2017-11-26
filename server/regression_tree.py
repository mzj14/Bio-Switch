from numpy import *

def loadDataSet(fileName):      #general function to parse tab -delimited floats
    dataMat = []                #assume last column is target value
    fr = open(fileName)
    for line in fr.readlines():
        curLine = line.strip().split()
        fltLine = list(map(float,curLine)) #map all elements to float()
        dataMat.append(fltLine)
    return dataMat

def plotBestFit(file):              #画出数据集
    import matplotlib.pyplot as plt
    dataMat=loadDataSet(file)       #数据矩阵和标签向量
    dataArr = array(dataMat)        #转换成数组
    n = shape(dataArr)[0]
    xcord1 = []; ycord1 = []        #声明两个不同颜色的点的坐标
    #xcord2 = []; ycord2 = []
    for i in range(n):
        xcord1.append(dataArr[i,0]); ycord1.append(dataArr[i,1])
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(xcord1, ycord1, s=30, c='green', marker='s')
    #ax.scatter(xcord2, ycord2, s=30, c='green')
    plt.xlabel('X1'); plt.ylabel('X2');
    plt.show()

def binSplitDataSet(dataSet, feature, value):   #该函数通过数组过滤方式将数据集合切分得到两个子集并返回
    mat0 = dataSet[nonzero(dataSet[:,feature] > value)[0],:]
    mat1 = dataSet[nonzero(dataSet[:,feature] <= value)[0],:]
    return mat0,mat1

'''
# regression tree
def regLeaf(dataSet):           #建立叶节点函数，value为所有y的均值
    # print('type dataSet[:, -1] = ', type(dataSet[:,-1]))
    return mean(dataSet[:,-1])

def regErr(dataSet):            #平方误差计算函数
    return var(dataSet[:,-1]) * shape(dataSet)[0]   #y的方差×y的数量=平方误差
'''

#模型树
def linearSolve(dataSet):   #将数据集格式化为X Y
    m,n = shape(dataSet)
    X = mat(ones((m,n))); Y = mat(ones((m,1)))
    X[:,1:n] = dataSet[:,0:n-1]; Y = dataSet[:,-1]
    xTx = X.T*X
    if linalg.det(xTx) == 0.0: #X Y用于简单线性回归，需要判断矩阵可逆
        raise NameError('This matrix is singular, cannot do inverse,\n\
        try increasing the second value of ops')
    ws = xTx.I * (X.T * Y)
    return ws,X,Y

def modelLeaf(dataSet):#不需要切分时生成模型树叶节点
    ws,X,Y = linearSolve(dataSet)
    return ws #返回回归系数

def modelErr(dataSet):#用来计算误差找到最佳切分
    ws,X,Y = linearSolve(dataSet)
    yHat = X * ws
    return sum(power(Y - yHat,2))

def chooseBestSplit(dataSet, leafType=modelLeaf, errType=modelErr, ops=(1,2)):  #最佳二元切分方式
    tolS = ops[0]; tolN = ops[1]        #tolS是容许的误差下降值，tolN是切分的最少样本数
    #如果剩余特征值的数量等于1，不需要再切分直接返回，（退出条件1）
    if len(set(dataSet[:,-1].T.tolist()[0])) == 1:
        return None, leafType(dataSet)
    m,n = shape(dataSet)
    #the choice of the best feature is driven by Reduction in RSS error from mean
    S = errType(dataSet)        #计算平方误差
    bestS = inf; bestIndex = 0; bestValue = 0
    for featIndex in range(n-1):
        #循环整个集合
        for splitVal in set((dataSet[:,featIndex].T.A.tolist())[0]):  #每次返回的集合中，元素的顺序都将不一样
            mat0, mat1 = binSplitDataSet(dataSet, featIndex, splitVal)      #将数据集合切分得到两个子集
            #如果划分的集合的大小小于切分的最少样本数，重新划分
            if (shape(mat0)[0] < tolN) or (shape(mat1)[0] < tolN): continue
            newS = errType(mat0) + errType(mat1)    #计算两个集合的平方误差和
            #平方误差和newS小于bestS，进行更新
            if newS < bestS:
                bestIndex = featIndex
                bestValue = splitVal
                bestS = newS
    #在循环了整个集合后，如果误差减少量(S - bestS)小于容许的误差下降值，则退出，（退出条件2）
    if (S - bestS) < tolS:
        return None, leafType(dataSet)
    mat0, mat1 = binSplitDataSet(dataSet, bestIndex, bestValue) #按照保存的最佳分割来划分集合
    #如果切分出的数据集小于切分的最少样本数，则退出，（退出条件3）
    if (shape(mat0)[0] < tolN) or (shape(mat1)[0] < tolN):
        return None, leafType(dataSet)
    #返回最佳二元切割的bestIndex和bestValue
    return bestIndex,bestValue

def createTree(dataSet, leafType=modelLeaf, errType=modelErr, ops=(100,12)):#assume dataSet is NumPy Mat so we can array filtering
    feat, val = chooseBestSplit(dataSet, leafType, errType, ops)    #采用最佳分割，将数据集分成两个部分
    if feat == None: return val     #递归结束条件
    retTree = {}                    #建立返回的字典
    retTree['spInd'] = feat
    retTree['spVal'] = val
    lSet, rSet = binSplitDataSet(dataSet, feat, val)    #得到左子树集合和右子树集合
    retTree['left'] = createTree(lSet, leafType, errType, ops)      #递归左子树
    retTree['right'] = createTree(rSet, leafType, errType, ops)     #递归右子树
    return retTree

def isTree(obj):
    return (type(obj).__name__ == 'dict')

#2-模型树
def modelTreeEval(model, inDat):
    print('modeTreeEval, inDat', inDat)
    print('modeTreeEval, shape(inDat) = ', shape(inDat))
    n = shape(inDat)[0]
    X = mat(ones((1, n + 1)))
    X[:, 1:n + 1] = inDat
    return float(X * model)

#对于输入的单个数据点，treeForeCast返回一个预测值。
def treeForeCast(tree, inData, modelEval=modelTreeEval):#指定树类型
    if not isTree(tree): return modelEval(tree, inData)
    print('inData = ', inData)
    print('tree[spInd] = ', tree['spInd'])
    if inData[tree['spInd']] > tree['spVal']:
        if isTree(tree['left']):#有左子树 递归进入子树
            return treeForeCast(tree['left'], inData, modelEval)
        else:#不存在子树 返回叶节点
            return modelEval(tree['left'], inData)
    else:
        if isTree(tree['right']):
            return treeForeCast(tree['right'], inData, modelEval)
        else:
            return modelEval(tree['right'], inData)

def createForeCast(tree, testData, modelEval=modelTreeEval):
    m = len(testData)
    print('testData = ', testData)
    print('m = ', m)
    yHat = mat(zeros((m, 1)))
    for i in range(m):
        print('i = ', i)
        print('testData[i] = ', testData[i])
        yHat[i, 0] = treeForeCast(tree, mat(testData[i]), modelEval)
    return yHat
