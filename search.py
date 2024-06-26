# search.py
# ---------
#许可信息:您可以出于教育目的自由使用或扩展这些项目,前提是
# (1)您不散发或发布解决方案,
# (2)您保留本声明,以及
# (3)您提供明确的加州大学伯克利分校归属,包括指向 http://ai.berkeley.edu 的链接.
# 
# 归属信息:吃豆人AI项目是在加州大学伯克利分校开发的.
# 核心项目和自动评分器主要由John DeNero(denero@cs.berkeley.edu)和Dan Klein(klein@cs.berkeley.edu)创建.
# 学生端自动评分由Brad Miller、Nick Hay和Pieter Abbeel(pabbeel@cs.berkeley.edu)添加.


"""
在 search.py 中,您将实现通用搜索算法,这些算法由
Pacman Agent(searchAgents.py).
"""

import util

class SearchProblem:
    """
    此类概述了搜索问题的结构,但不实现
    任何方法(在面向对象的术语中:抽象类).

    你永远不需要改变这个类中的任何内容.
    """

    def getStartState(self):
        """
        返回搜索问题的开始状态.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state:搜索状态

        当且仅当状态为有效的目标状态时,返回 True.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state:搜索状态

        对于给定状态,这应该返回一个三元组列表,(successor,
        action, stepCost),其中 'successor' 是当前
        状态,“action”是到达那里所需的操作,“stepCost”是
        扩展到该继任者的增量成本.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions:要执行的操作列表

        此方法返回特定操作序列的总成本.
        该序列必须由合法动作组成.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    返回解决 tinyMaze 的一系列移动. 对于任何其他迷宫,
    移动顺序不正确,因此仅将其用于 tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]

def depthFirstSearch(problem: SearchProblem):
    """
    DFS
    首先在搜索树中搜索最深的节点.

    您的搜索算法需要返回一个操作列表,该列表达到
    目标.确保实现图形搜索算法.

    首先,您可能需要尝试以下一些简单的命令来
    了解传入的搜索问题:

    print("Start:", problem.getStartState())
    print("Is the start a goal?", problem.isGoalState(problem.getStartState()))
    print("Start's successors:", problem.getSuccessors(problem.getStartState()))
    """
    "*** 您的代码在这里 ***"
    # print("Start:", problem.getStartState())
    # print("Is the start a goal?", problem.isGoalState(problem.getStartState()))
    # print("Start's successors:", problem.getSuccessors(problem.getStartState()))
    stack = util.Stack()
    stack.push((problem.getStartState(), []))
    visited = set()
    while not stack.isEmpty():
        current_state, path = stack.pop()
        if problem.isGoalState(current_state):
            return path
        if current_state in visited:
            continue
        visited.add(current_state)
        for successors in problem.getSuccessors(current_state):
            succerror, active, _ = successors
            stack.push((succerror, path + [active]))
    return []
    util.raiseNotDefined()

def breadthFirstSearch(problem: SearchProblem):
    """ BFS
    首先在搜索树中搜索最浅的节点."""
    "*** 您的代码在这里 ***"
    queue = util.Queue()
    queue.push((problem.getStartState(), []))
    visited = set()
    while not queue.isEmpty():
        current_state, path = queue.pop()
        if problem.isGoalState(current_state):
            return path
        if current_state in visited:
            continue
        visited.add(current_state)
        for successors in problem.getSuccessors(current_state):
            succerror, active, _ = successors
            queue.push((succerror, path + [active]))
    return []

    util.raiseNotDefined()

def uniformCostSearch(problem: SearchProblem):
    """首先搜索总成本最低的节点."""
    "*** 您的代码在这里 ***"
    util.raiseNotDefined()

def nullHeuristic(state, problem=None):
    """
    启发式函数估计从当前状态到最近状态的成本
    目标. 这种启发式是微不足道的.
    """
    return 0

def aStarSearch(problem: SearchProblem, heuristic=nullHeuristic):
    """A*
    首先搜索组合成本和启发式最低的节点."""
    "*** 您的代码在这里 ***"
    util.raiseNotDefined()


# 缩写
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
