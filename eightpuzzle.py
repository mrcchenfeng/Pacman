# eightpuzzle.py
# --------------
#许可信息:您可以出于教育目的自由使用或扩展这些项目,前提是
# (1)您不散发或发布解决方案,
# (2)您保留本声明,以及
# (3)您提供明确的加州大学伯克利分校归属,包括指向 http://ai.berkeley.edu 的链接.
# 
# 归属信息:吃豆人AI项目是在加州大学伯克利分校开发的.
# 核心项目和自动评分器主要由John DeNero(denero@cs.berkeley.edu)和Dan Klein(klein@cs.berkeley.edu)创建.
# 学生端自动评分由Brad Miller、Nick Hay和Pieter Abbeel(pabbeel@cs.berkeley.edu)添加.


import search
import random

# 模块类

class EightPuzzleState:
    """
    八数码问题在课程的教科书中第64页有描述.

    这个类定义了八数码问题本身的机制.
    将该问题重新表述为搜索问题的任务留给 EightPuzzleSearchProblem 类来完成.
    """

    def __init__( self, numbers ):
        """
          从数字的顺序中构造一个新的八数码问题.

        numbers: 一个从0到8的整数列表,代表八数码问题的一个实例.
        0代表空白空间.
        因此,这个列表
            [1, 0, 2, 3, 4, 5, 6, 7, 8]

          表示这个八数码问题:
            -------------
            | 1 |   | 2 |
            -------------
            | 3 | 4 | 5 |
            -------------
            | 6 | 7 | 8 |
            ------------

        八数码问题的配置被存储在一个二维列表(列表的列表)'cells'中.
        """
        self.cells = []
        numbers = numbers[:] # 创建一个副本以避免产生副作用.
        numbers.reverse()
        for row in range( 3 ):
            self.cells.append( [] )
            for col in range( 3 ):
                self.cells[row].append( numbers.pop() )
                if self.cells[row][col] == 0:
                    self.blankLocation = row, col

    def isGoal( self ):
        """
          检查八数码问题是否处于目标状态.

            -------------
            |   | 1 | 2 |
            -------------
            | 3 | 4 | 5 |
            -------------
            | 6 | 7 | 8 |
            -------------

        >>> EightPuzzleState([0, 1, 2, 3, 4, 5, 6, 7, 8]).isGoal()
        True

        >>> EightPuzzleState([1, 0, 2, 3, 4, 5, 6, 7, 8]).isGoal()
        False
        """
        current = 0
        for row in range( 3 ):
            for col in range( 3 ):
                if current != self.cells[row][col]:
                    return False
                current += 1
        return True

    def legalMoves( self ):
        """
          返回从当前状态出发的合法移动列表.

        移动包括将空白空间向上、向下、向左或向右移动.
        这些移动分别被编码为 'up'、'down'、'left' 和 'right'.

        >>> EightPuzzleState([0, 1, 2, 3, 4, 5, 6, 7, 8]).legalMoves()
        ['down', 'right']
        """
        moves = []
        row, col = self.blankLocation
        if(row != 0):
            moves.append('up')
        if(row != 2):
            moves.append('down')
        if(col != 0):
            moves.append('left')
        if(col != 2):
            moves.append('right')
        return moves

    def result(self, move):
        """
          根据提供的移动,返回一个新的八数码问题,其中当前状态和空白位置已更新.

        移动应该是一个从 legalMoves 返回的列表中的字符串.
        非法的移动将引发异常,这可能是数组越界异常.

        NOTE: 这个函数*不会改变*当前对象.相反,它返回一个新对象.
        """
        row, col = self.blankLocation
        if(move == 'up'):
            newrow = row - 1
            newcol = col
        elif(move == 'down'):
            newrow = row + 1
            newcol = col
        elif(move == 'left'):
            newrow = row
            newcol = col - 1
        elif(move == 'right'):
            newrow = row
            newcol = col + 1
        else:
            raise "Illegal Move"

        # 创建当前八数码问题的一个副本
        newPuzzle = EightPuzzleState([0, 0, 0, 0, 0, 0, 0, 0, 0])
        newPuzzle.cells = [values[:] for values in self.cells]
        # 并更新它以反映移动
        newPuzzle.cells[row][col] = self.cells[newrow][newcol]
        newPuzzle.cells[newrow][newcol] = self.cells[row][col]
        newPuzzle.blankLocation = newrow, newcol

        return newPuzzle

    # 用于比较和显示的实用程序
    def __eq__(self, other):
        """
            重载 '==' 运算符,使得具有相同配置的两个八数码问题被视为相等.

          >>> EightPuzzleState([0, 1, 2, 3, 4, 5, 6, 7, 8]) == \
              EightPuzzleState([1, 0, 2, 3, 4, 5, 6, 7, 8]).result('left')
          True
        """
        for row in range( 3 ):
            if self.cells[row] != other.cells[row]:
                return False
        return True

    def __hash__(self):
        return hash(str(self.cells))

    def __getAsciiString(self):
        """
          返回迷宫的显示字符串
        """
        lines = []
        horizontalLine = ('-' * (13))
        lines.append(horizontalLine)
        for row in self.cells:
            rowLine = '|'
            for col in row:
                if col == 0:
                    col = ' '
                rowLine = rowLine + ' ' + col.__str__() + ' |'
            lines.append(rowLine)
            lines.append(horizontalLine)
        return '\n'.join(lines)

    def __str__(self):
        return self.__getAsciiString()

# TODO: 实现这个类中的方法

class EightPuzzleSearchProblem(search.SearchProblem):
    """
      八数码问题领域的 SearchProblem 实现

      每个状态都由一个eightPuzzle的实例表示.
    """
    def __init__(self,puzzle):
        "创建一个新的EightPuzzleSearchProblem,用于存储搜索信息."
        self.puzzle = puzzle

    def getStartState(self):
        return puzzle

    def isGoalState(self,state):
        return state.isGoal()

    def getSuccessors(self,state):
        """
          返回(后继状态,动作,步长成本)的列表,
          其中每个后继状态都是原始状态的左、右、上或下方向,每个成本为1.0
        """
        succ = []
        for a in state.legalMoves():
            succ.append((state.result(a), a, 1))
        return succ

    def getCostOfActions(self, actions):
        """
         actions(动作列表):要执行的一系列动作列表

        此方法返回特定动作序列的总成本.该序列必须由合法移动组成
        """
        return len(actions)

EIGHT_PUZZLE_DATA = [[1, 0, 2, 3, 4, 5, 6, 7, 8],
                     [1, 7, 8, 2, 3, 4, 5, 6, 0],
                     [4, 3, 2, 7, 0, 5, 1, 6, 8],
                     [5, 1, 3, 4, 0, 2, 6, 7, 8],
                     [1, 2, 5, 7, 6, 8, 0, 4, 3],
                     [0, 3, 1, 6, 8, 2, 7, 5, 4]]

def loadEightPuzzle(puzzleNumber):
    """
      puzzleNumber: 要加载的八数码问题的编号.

      从提供的EIGHT_PUZZLE_DATA中的某个八数码问题生成一个八数码对象.
      puzzleNumber 可以从 0 到 5 之间的数字中选择.

      >>> print(loadEightPuzzle(0))
      -------------
      | 1 |   | 2 |
      -------------
      | 3 | 4 | 5 |
      -------------
      | 6 | 7 | 8 |
      -------------
    """
    return EightPuzzleState(EIGHT_PUZZLE_DATA[puzzleNumber])

def createRandomEightPuzzle(moves=100):
    """
      moves: 要执行的随机移动次数

      通过在一个已解决的八数码问题上应用一系列'moves'的随机移动,
      来创建一个随机的八数码问题.
    """
    puzzle = EightPuzzleState([0,1,2,3,4,5,6,7,8])
    for i in range(moves):
        # 执行一个随机的合法移动
        puzzle = puzzle.result(random.sample(puzzle.legalMoves(), 1)[0])
    return puzzle

if __name__ == '__main__':
    puzzle = createRandomEightPuzzle(25)
    print('一个随机拼图(八数码问题):')
    print(puzzle)

    problem = EightPuzzleSearchProblem(puzzle)
    path = search.breadthFirstSearch(problem)
    print('BFS(广度优先搜索)找到了一个包含%d步的路径:%s' % (len(path), str(path)))
    curr = puzzle
    i = 1
    for a in path:
        curr = curr.result(a)
        print('经过%d步%s:%s' % (i, ("", "s")[i>1], a))
        print(curr)

        input("按回车键进入下一状态...")   # 等待按键输入
        i += 1
