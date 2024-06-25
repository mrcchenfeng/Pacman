# searchAgents.py
# ---------------
#许可信息:您可以出于教育目的自由使用或扩展这些项目,前提是
# (1)您不散发或发布解决方案,
# (2)您保留本声明,以及
# (3)您提供明确的加州大学伯克利分校归属,包括指向 http://ai.berkeley.edu 的链接.
# 
# 归属信息:吃豆人AI项目是在加州大学伯克利分校开发的.
# 核心项目和自动评分器主要由John DeNero(denero@cs.berkeley.edu)和Dan Klein(klein@cs.berkeley.edu)创建.
# 学生端自动评分由Brad Miller、Nick Hay和Pieter Abbeel(pabbeel@cs.berkeley.edu)添加.


"""
此文件包含所有可以选择来控制 Pacman 的Agent. 自
选择一个Agent,在运行 pacman.py 时使用“-p”选项. 参数可以是
使用“-a”传递给Agent. 例如,要加载使用
深度优先搜索 (DFS),运行以下命令:

> python pacman.py -p SearchAgent -a fn=depthFirstSearch

可以在项目中找到调用其他搜索策略的命令
描述.

请仅更改要求您更改的文件部分. 寻找线条
也就是说

"*** 您的代码在这里 ***"

您填写的部分从大约 3/4 开始. 关注项目
有关详细信息,请说明.

祝你好运,搜索愉快!
"""

from typing import List, Tuple, Any
from game import Directions
from game import Agent
from game import Actions
import util
import time
import search
import pacman

class GoWestAgent(Agent):
    "一个向西走直到它不能的特工."

    def getAction(self, state):
        "Agent接收 GameState(在 pacman.py 中定义)."
        if Directions.WEST in state.getLegalPacmanActions():
            return Directions.WEST
        else:
            return Directions.STOP

#######################################################
#             这部分是为你写的,但只会起作用             #
#               填写部分 search.py 后                  #
#######################################################

class SearchAgent(Agent):
    """
    这个非常通用的搜索Agent使用提供的搜索来查找路径
    算法,然后返回操作以遵循该
    路径.

    默认情况下,此Agent在 PositionSearchProblem 上运行 DFS 以查找
    位置 (1,1)
    fn 的选项包括:
      depthFirstSearch 或 dfs
      breadthFirstSearch 或 bfs


    Note: 您不应更改 SearchAgent 中的任何代码
    """

    def __init__(self, fn='depthFirstSearch', prob='PositionSearchProblem', heuristic='nullHeuristic'):
        # 警告:下面采用了一些高级 Python 魔法来找到正确的函数和问题

        # 从名称和启发式中获取搜索函数
        if fn not in dir(search):
            raise AttributeError(fn + ' 不是 search.py 中的搜索功能.')
        func = getattr(search, fn)
        if 'heuristic' not in func.__code__.co_varnames:
            print('[SearchAgent] 使用函数 ' + fn)
            self.searchFunction = func
        else:
            if heuristic in globals().keys():
                heur = globals()[heuristic]
            elif heuristic in dir(search):
                heur = getattr(search, heuristic)
            else:
                raise AttributeError(heuristic + ' 不是 searchAgents.py 或 search.py 中的函数.')
            print('[SearchAgent] 使用函数 %s 和启发式 %s' % (fn, heuristic))
            # Note: this bit of Python trickery combines the search algorithm and the heuristic
            self.searchFunction = lambda x: func(x, heuristic=heur)

        # Get the search problem type from the name
        if prob not in globals().keys() or not prob.endswith('Problem'):
            raise AttributeError(prob + ' 不是 SearchAgents.py 中的搜索问题类型.')
        self.searchType = globals()[prob]
        print('[SearchAgent] 使用问题类型' + prob)

    def registerInitialState(self, state):
        """
        这是Agent第一次看到游戏的布局
        板.在这里,我们选择一条通往目标的道路.在此阶段,Agent
        应该计算目标的路径并将其存储在局部变量中.
        所有的工作都是用这种方法完成的！

        state: a GameState 对象 (pacman.py)
        """
        if self.searchFunction == None: raise Exception("没有为 SearchAgent 提供搜索功能")
        starttime = time.time()
        problem = self.searchType(state) # 提出新的搜索问题
        self.actions  = self.searchFunction(problem) # 查找路径
        if self.actions == None:
            self.actions = []
        totalCost = problem.getCostOfActions(self.actions)
        print('找到的总成本为 %d 的路径,以 %.1f 秒为单位' % (totalCost, time.time() - starttime))
        if '_expanded' in dir(problem): print('扩展的搜索节点: %d' % problem._expanded)

    def getAction(self, state):
        """
        返回前面选择的路径中的下一个操作 (在
        registerInitialState). 返回 Directions.STOP 如果没有进一步的
        要采取的行动.

        state: a GameState 对象 (pacman.py)
        """
        if 'actionIndex' not in dir(self): self.actionIndex = 0
        i = self.actionIndex
        self.actionIndex += 1
        if i < len(self.actions):
            return self.actions[i]
        else:
            return Directions.STOP

class PositionSearchProblem(search.SearchProblem):
    """
    搜索问题定义了状态空间、开始状态、目标测试、后继者
    函数和成本函数. 此搜索问题可用于查找路径
    到吃豆板上的特定点.

    状态空间由吃豆子游戏中的 (x,y) 位置组成.

    Note: 这个搜索问题是完全指定的;你不应该改变它.
    """

    def __init__(self, gameState, costFn = lambda x: 1, goal=(1,1), start=None, warn=True, visualize=True):
        """
        存储开始和目标.

        gameState: 一个 GameState 对象 (pacman.py)
        costFn: 从搜索状态(元组)到非负数的函数
        goal: gameState 中的位置
        """
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition()
        if start != None: self.startState = start
        self.goal = goal
        self.costFn = costFn
        self.visualize = visualize
        if warn and (gameState.getNumFood() != 1 or not gameState.hasFood(*goal)):
            print('警告:这看起来不像一个普通的搜索迷宫')

        # 用于展示目的
        self._visited, self._visitedlist, self._expanded = {}, [], 0 # 不要更改

    def getStartState(self):
        return self.startState

    def isGoalState(self, state):
        isGoal = state == self.goal

        # 仅供展示之用
        if isGoal and self.visualize:
            self._visitedlist.append(state)
            import __main__
            if '_display' in dir(__main__):
                if 'drawExpandedCells' in dir(__main__._display): #@UndefinedVariable
                    __main__._display.drawExpandedCells(self._visitedlist) #@UndefinedVariable

        return isGoal

    def getSuccessors(self, state):
        """
        返回后续状态、它们需要的操作以及 1 的成本.
         如 search.py 所述:
             对于给定状态,这应该返回一个三元组列表,
         (successor, action, stepCost), 其中“successor”是
         当前状态的继承者,“行动”是行动
         需要到达那里,而“stepCost”是增量
         扩展到该继任者的成本
        """

        successors = []
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x,y = state
            dx, dy = Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextState = (nextx, nexty)
                cost = self.costFn(nextState)
                successors.append( ( nextState, action, cost) )

        # 用于展示目的的簿记
        self._expanded += 1 # 不要更改
        if state not in self._visited:
            self._visited[state] = True
            self._visitedlist.append(state)

        return successors

    def getCostOfActions(self, actions):
        """
        返回特定动作序列的成本.如果这些动作包括非法移动,则返回999999.
        """
        if actions == None: return 999999
        x,y= self.getStartState()
        cost = 0
        for action in actions:
            # 检查找出下一个状态,看看它是否合法
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]: return 999999
            cost += self.costFn((x,y))
        return cost

class StayEastSearchAgent(SearchAgent):
    """
    一个用于位置搜索的Agent,其成本函数会对位于棋盘西侧的位置进行惩罚.

    踏入仓位 (x,y) 的成本函数为 1/2^x.
    """
    def __init__(self):
        self.searchFunction = search.uniformCostSearch
        costFn = lambda pos: .5 ** pos[0]
        self.searchType = lambda state: PositionSearchProblem(state, costFn, (1, 1), None, False)

class StayWestSearchAgent(SearchAgent):
    """
    一个用于位置搜索的Agent,其成本函数会对位于棋盘东侧的位置进行惩罚.

    踏入仓位 (x,y) 的成本函数为 2^x.
    """
    def __init__(self):
        self.searchFunction = search.uniformCostSearch
        costFn = lambda pos: 2 ** pos[0]
        self.searchType = lambda state: PositionSearchProblem(state, costFn)

def manhattanHeuristic(position, problem, info={}):
    "PositionSearchProblem 的曼哈顿距离启发式"
    xy1 = position
    xy2 = problem.goal
    return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])

def euclideanHeuristic(position, problem, info={}):
    "PositionSearchProblem 的欧几里得距离启发式"
    xy1 = position
    xy2 = problem.goal
    return ( (xy1[0] - xy2[0]) ** 2 + (xy1[1] - xy2[1]) ** 2 ) ** 0.5

#####################################################
#         这部分是不完整的. 是时候编写代码了!         #
#####################################################

class CornersProblem(search.SearchProblem):
    """
    此搜索问题查找穿过布局所有四个角的路径.

    您必须选择合适的状态空间和后续函数
    """

    def __init__(self, startingGameState: pacman.GameState):
        """
        存储墙壁、吃豆人的起始位置和角落.
        """
        self.walls = startingGameState.getWalls()
        self.startingPosition = startingGameState.getPacmanPosition()
        top, right = self.walls.height-2, self.walls.width-2
        self.corners = ((1,1), (1,top), (right, 1), (right, top))
        for corner in self.corners:
            if not startingGameState.hasFood(*corner):
                print('警告:角落里没有食物 ' + str(corner))
        self._expanded = 0 # 不要改变;扩展的搜索节点数

    def getStartState(self):
        """
        返回开始状态(在状态空间中,而不是完整的 Pacman 状态
        空间)
        """
        "*** 您的代码在这里 ***"
        util.raiseNotDefined()

    def isGoalState(self, state: Any):
        """
        返回此搜索状态是否为问题的目标状态.
        """
        "*** 您的代码在这里 ***"
        util.raiseNotDefined()

    def getSuccessors(self, state: Any):
        """
        返回继承国、它们需要的操作以及 1 的成本.

         如 search.py 所述:
            对于给定状态,这应该返回一个三元组列表,(successor,
            action, stepCost),其中 'successor' 是当前
            状态,“action”是到达那里所需的操作,“stepCost”
            是扩展到该继任者的增量成本
        """

        successors = []
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            # 如果动作是合法的,则将后继状态添加到后继列表中.
            # 以下是一个代码片段,用于判断新位置是否撞到墙上:
            # x, y = currentPosition  
            # dx, dy = Actions.directionToVector(action)  
            # nextx, nexty = int(x + dx), int(y + dy)  
            # hitsWall = self.walls[nextx][nexty]


            "*** 您的代码在这里 ***"

        self._expanded += 1 # 不要更改
        return successors

    def getCostOfActions(self, actions):
        """
        这个函数返回特定动作序列的成本.如果这些动作包括非法的移动,
        则返回 999999.这个函数已经为你实现了
        """
        if actions == None: return 999999
        x,y= self.startingPosition
        for action in actions:
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]: return 999999
        return len(actions)


def cornersHeuristic(state: Any, problem: CornersProblem):
    """
    您定义的 CornersProblem 的启发式方法.

      state:   当前搜索状态
               (您在搜索问题中选择的数据结构)

      problem: 此布局的 CornersProblem 实例.

    此函数应始终返回一个数字,该数字是
    从状态到问题目标的最短路径;即 它应该是
    可接受(以及一致).
    """
    corners = problem.corners # 这些是拐角坐标
    walls = problem.walls # 这些是迷宫的墙壁,作为网格(game.py)

    "*** YOUR CODE HERE ***"
    return 0 # 默认为简单解决方案

class AStarCornersAgent(SearchAgent):
    "使用 A* 和 foodHeuristic 的 FoodSearchProblem 的 SearchAgent"
    def __init__(self):
        self.searchFunction = lambda prob: search.aStarSearch(prob, cornersHeuristic)
        self.searchType = CornersProblem

class FoodSearchProblem:
    """
    查找收集所有与
    吃豆人游戏中的食物(点).

    此问题中的搜索状态是一个元组(pacmanPosition, foodGrid),其中
      pacmanPosition: 指定 Pacman 位置的整数元组 (x,y)
      foodGrid:       a True或False的网格(见 game.py),指定剩余食物
    """
    def __init__(self, startingGameState: pacman.GameState):
        self.start = (startingGameState.getPacmanPosition(), startingGameState.getFood())
        self.walls = startingGameState.getWalls()
        self.startingGameState = startingGameState
        self._expanded = 0 # 不要更改
        self.heuristicInfo = {} # 用于启发式存储信息的字典

    def getStartState(self):
        return self.start

    def isGoalState(self, state):
        return state[1].count() == 0

    def getSuccessors(self, state):
        "返回继承国、它们需要的操作以及 1 的成本."
        successors = []
        self._expanded += 1 # 不要更改
        for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x,y = state[0]
            dx, dy = Actions.directionToVector(direction)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextFood = state[1].copy()
                nextFood[nextx][nexty] = False
                successors.append( ( ((nextx, nexty), nextFood), direction, 1) )
        return successors

    def getCostOfActions(self, actions):
        """这个函数返回特定动作序列的成本.
        如果这些动作包括非法移动,则返回999999."""
        x,y= self.getStartState()[0]
        cost = 0
        for action in actions:
            # figure out the next state and see whether it's legal
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]:
                return 999999
            cost += 1
        return cost

class AStarFoodSearchAgent(SearchAgent):
    "使用 A* 和 foodHeuristic 的 FoodSearchProblem 的 SearchAgent"
    def __init__(self):
        self.searchFunction = lambda prob: search.aStarSearch(prob, foodHeuristic)
        self.searchType = FoodSearchProblem

def foodHeuristic(state: Tuple[Tuple, List[List]], problem: FoodSearchProblem):
    """
    FoodSearchProblem 的启发式方法位于此处.

    这种启发式方法必须保持一致,以确保正确性. 首先,试着来
    提出可接受的启发式方法;几乎所有可接受的启发式方法都是
    也始终如一.

    如果使用 A* 找到更差的解决方案,则统一成本搜索会发现,
    你的启发式方法*不*一致,可能不可接受！ 在
    另一方面,不可接受或不一致的启发式方法可能会找到最佳
    解决方案,所以要小心.

    状态是一个元组(pacmanPosition, foodGrid),其中 foodGrid 是一个网格
    (参见 game.py) 的 True 或 False.你可以调用 foodGrid.asList() 来获取
    取而代之的是食物坐标列表.

    如果您想访问墙壁、胶囊等信息,您可以查询
    问题. 例如,problem.walls 为您提供了墙壁位置的网格
    是.

    如果要*存储*信息以在其他调用中重用
    启发式,有一个名为 problem.heuristicInfo 的字典,您可以
    用.例如,如果您只想计算一次墙壁并将其存储
    值,请尝试: problem.heuristicInfo['wallCount'] = problem.walls.count()
    对此启发式方法的后续调用可以访问
    problem.heuristicInfo['wallCount']
    """
    position, foodGrid = state
    "*** 您的代码在这里 ***"
    return 0

class ClosestDotSearchAgent(SearchAgent):
    "使用一系列搜索搜索所有食物"
    def registerInitialState(self, state):
        self.actions = []
        currentState = state
        while(currentState.getFood().count() > 0):
            nextPathSegment = self.findPathToClosestDot(currentState) # 缺失的一块
            self.actions += nextPathSegment
            for action in nextPathSegment:
                legal = currentState.getLegalActions()
                if action not in legal:
                    t = (str(action), str(currentState))
                    raise Exception('findPathToClosestDot 返回了非法移动:%s！\n%s' % t)
                currentState = currentState.generateSuccessor(0, action)
        self.actionIndex = 0
        print('找到成本为 %d 的路径.' % len(self.actions))

    def findPathToClosestDot(self, gameState: pacman.GameState):
        """
        返回最近点的路径(操作列表),从 gameState 开始.
        """
        # 下面是 startState 的一些有用元素
        startPosition = gameState.getPacmanPosition()
        food = gameState.getFood()
        walls = gameState.getWalls()
        problem = AnyFoodSearchProblem(gameState)

        "*** 您的代码在这里 ***"
        util.raiseNotDefined()

class AnyFoodSearchProblem(PositionSearchProblem):
    """
    寻找通往任何食物的路径的搜索问题.

    此搜索问题与 PositionSearchProblem 类似,但具有
    不同的目标测试,您需要在下面填写. 状态空间和
    后继函数无需更改.

    上面的类定义,AnyFoodSearchProblem(PositionSearchProblem),
    继承 PositionSearchProblem 的方法.

    您可以使用此搜索问题来帮助您填写 findPathToClosestDot
    方法.
    """

    def __init__(self, gameState):
        "存储来自 gameState 的信息. 您无需更改此设置."
        # 储存食物以备后用
        self.food = gameState.getFood()

        # 存储 PositionSearchProblem 的信息(无需更改此信息)
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition()
        self.costFn = lambda x: 1
        self._visited, self._visitedlist, self._expanded = {}, [], 0 # 不要更改

    def isGoalState(self, state: Tuple[int, int]):
        """
        状态是吃豆子的位置.用目标测试填写它,它将
        完成问题定义.
        """
        x,y = state

        "*** 您的代码在这里 ***"
        util.raiseNotDefined()

def mazeDistance(point1: Tuple[int, int], point2: Tuple[int, int], gameState: pacman.GameState) -> int:
    """
    使用搜索函数返回任意两点之间的迷宫距离
    你已经建造了.gameState 可以是任何游戏状态 -- Pacman 的
    该状态下的位置将被忽略.
    用法示例: mazeDistance( (2,4), (5,6), gameState)

    对于您的 ApproximateSearchAgent 来说,这可能是一个有用的帮助程序函数.
    """
    x1, y1 = point1
    x2, y2 = point2
    walls = gameState.getWalls()
    assert not walls[x1][y1], 'point1 is a wall: ' + str(point1)
    assert not walls[x2][y2], 'point2 is a wall: ' + str(point2)
    prob = PositionSearchProblem(gameState, start=point1, goal=point2, warn=False, visualize=False)
    return len(search.bfs(prob))
