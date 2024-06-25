# pacman.py
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
Pacman.py 文件包含了经典吃豆人游戏的逻辑以及运行游戏的主要代码.这个文件被分为三个部分:

(i) 你与吃豆人世界的接口:
贪吃蛇是一个复杂的环境.你可能不想阅读我们编写的所有代码来确保游戏正常运行.
这个部分包含了你需要理解的代码部分,以便完成这个项目.同时,game.py 文件中的一些代码你也应该理解.

(ii) 吃豆人的隐藏秘密:
这个部分包含了贪吃蛇环境使用的所有逻辑代码,用于决定谁可以移动到哪里,
当东西碰撞时谁会死亡等等.你不需要阅读这部分代码,但如果你愿意的话,可以阅读.

(iii) 开始游戏的框架:
最后一部分包含了用于读取你用来设置游戏的命令的代码,然后启动一个新游戏,
以及链接所有外部部分(Agent函数、图形等).检查这一部分以查看所有可用的选项.

要玩你的第一个游戏,请在命令行中输入 'python pacman.py'.
使用 'a'、's'、'd' 和 'w' 键(或箭头键)进行移动.祝你玩得开心！
"""
from game import GameStateData
from game import Game
from game import Directions
from game import Actions
from util import nearestPoint
from util import manhattanDistance
import util, layout
import sys, types, time, random, os

###################################################
#   你与贪吃蛇世界的接口:一个游戏状态(GameState)  #
###################################################

class GameState:
    """
    一个GameState指定了完整的游戏状态,包括食物、胶囊、Agent配置和得分变化.

    GameState由Game对象使用,以捕获游戏的实际状态,
    并可供Agent用来推理游戏.

    GameState中的大部分信息都存储在GameStateData对象中.
    我们强烈建议你通过下面的访问器方法来访问这些数据,而不是直接引用GameStateData对象.

    请注意,在经典的Pacman游戏中,Pacman总是Agent0.
    """

    ####################################################
    #         访问器方法:使用这些方法访问状态数据        #
    ####################################################

    # static 变量跟踪哪些状态调用了 getLegalActions
    explored = set()
    def getAndResetExplored():
        tmp = GameState.explored.copy()
        GameState.explored = set()
        return tmp
    getAndResetExplored = staticmethod(getAndResetExplored)

    def getLegalActions( self, agentIndex=0 ):
        """
        返回指定Agent的合法动作.
        """
#        GameState.explored.add(self)
        if self.isWin() or self.isLose(): return []

        if agentIndex == 0:  # Pacman 正在移动
            return PacmanRules.getLegalActions( self )
        else:
            return GhostRules.getLegalActions( self, agentIndex )

    def generateSuccessor( self, agentIndex, action):
        """
        在指定的Agent执行操作后返回后续状态.
        """
        # 检查继任者是否存在
        if self.isWin() or self.isLose(): raise Exception('Can\'t generate a successor of a terminal state.')

        # 复制当前状态
        state = GameState(self)

        # 让智能体的逻辑处理其动作对棋盘的影响
        if agentIndex == 0:  # Pacman 正在移动
            state.data._eaten = [False for i in range(state.getNumAgents())]
            PacmanRules.applyAction( state, action )
        else:                # 一个鬼在移动
            GhostRules.applyAction( state, action, agentIndex )

        # 时间流逝
        if agentIndex == 0:
            state.data.scoreChange += -TIME_PENALTY # 等待的处罚
        else:
            GhostRules.decrementTimer( state.data.agentStates[agentIndex] )

        # 解决多智能体效应
        GhostRules.checkDeath( state, agentIndex )

        # 簿记
        state.data._agentMoved = agentIndex
        state.data.score += state.data.scoreChange
        GameState.explored.add(self)
        GameState.explored.add(state)
        return state

    def getLegalPacmanActions( self ):
        return self.getLegalActions( 0 )

    def generatePacmanSuccessor( self, action ):
        """
        在指定的 pacman 移动后生成后续状态
        """
        return self.generateSuccessor( 0, action )

    def getPacmanState( self ):
        """
        返回 pacman 的 AgentState 对象(game.py)

        state.pos 给出当前位置
        state.direction 给出了行进向量
        """
        return self.data.agentStates[0].copy()

    def getPacmanPosition( self ):
        return self.data.agentStates[0].getPosition()

    def getGhostStates( self ):
        return self.data.agentStates[1:]

    def getGhostState( self, agentIndex ):
        if agentIndex == 0 or agentIndex >= self.getNumAgents():
            raise Exception("Invalid index passed to getGhostState")
        return self.data.agentStates[agentIndex]

    def getGhostPosition( self, agentIndex ):
        if agentIndex == 0:
            raise Exception("Pacman's index passed to getGhostPosition")
        return self.data.agentStates[agentIndex].getPosition()

    def getGhostPositions(self):
        return [s.getPosition() for s in self.getGhostStates()]

    def getNumAgents( self ):
        return len( self.data.agentStates )

    def getScore( self ):
        return float(self.data.score)

    def getCapsules(self):
        """
        返回剩余胶囊的位置列表 (x,y).
        """
        return self.data.capsules

    def getNumFood( self ):
        return self.data.food.count()

    def getFood(self):
        """
        返回布尔食物指示符变量的网格.

        可以通过列表表示法访问网格,因此要检查
        (x,y) 位置是否有食物,只需调用

        currentFood = state.getFood()
        if currentFood[x][y] == True: ...
        """
        return self.data.food

    def getWalls(self):
        """
        返回一个布尔值网格,表示墙壁的指示变量.

        可以通过列表表示法访问网格,因此,要检查
        (x,y) 位置是否有墙壁,只需调用

        walls = state.getWalls()
        if walls[x][y] == True: ...
        """
        return self.data.layout.walls

    def hasFood(self, x, y):
        return self.data.food[x][y]

    def hasWall(self, x, y):
        return self.data.layout.walls[x][y]

    def isLose( self ):
        return self.data._lose

    def isWin( self ):
        return self.data._win

    #############################################
    #               Helper方法:                  #
    #             您不需要直接调用这些            #
    #############################################

    def __init__( self, prevState = None ):
        """
        通过从其前置状态复制信息来生成新状态.
        """
        if prevState != None: # 初始状态
            self.data = GameStateData(prevState.data)
        else:
            self.data = GameStateData()

    def deepCopy( self ):
        state = GameState( self )
        state.data = self.data.deepCopy()
        return state

    def __eq__( self, other ):
        """
        允许比较两种状态.
        """
        return hasattr(other, 'data') and self.data == other.data

    def __hash__( self ):
        """
        允许状态成为字典的键.
        """
        return hash( self.data )

    def __str__( self ):

        return str(self.data)

    def initialize( self, layout, numGhostAgents=1000 ):
        """
        从布局数组创建初始游戏状态(请参阅 layout.py).
        """
        self.data.initialize(layout, numGhostAgents)

############################################################################
#                            吃豆人隐藏的秘密                               #
#                                                                          #
#                       您不需要查看文件此部分中的代码.                       #
############################################################################

SCARED_TIME = 40    # 鬼被吓坏了
COLLISION_TOLERANCE = 0.7 # 鬼魂必须离吃豆人有多近才能杀死
TIME_PENALTY = 1 # 每轮损失的分数

class ClassicGameRules:
    """
    这些游戏规则管理游戏的控制流,决定何时
    以及游戏的开始和结束方式.
    """
    def __init__(self, timeout=30):
        self.timeout = timeout

    def newGame( self, layout, pacmanAgent, ghostAgents, display, quiet = False, catchExceptions=False):
        agents = [pacmanAgent] + ghostAgents[:layout.getNumGhosts()]
        initState = GameState()
        initState.initialize( layout, len(ghostAgents) )
        game = Game(agents, display, self, catchExceptions=catchExceptions)
        game.state = initState
        self.initialState = initState.deepCopy()
        self.quiet = quiet
        return game

    def process(self, state, game):
        """
        检查是否该结束游戏了.
        """
        if state.isWin(): self.win(state, game)
        if state.isLose(): self.lose(state, game)

    def win( self, state, game ):
        if not self.quiet: print("pacman取得胜利！得分:\t %d" % state.data.score)
        game.gameOver = True

    def lose( self, state, game ):
        if not self.quiet: print("pacman死了！得分:\t %d" % state.data.score)
        game.gameOver = True

    def getProgress(self, game):
        return float(game.state.getNumFood()) / self.initialState.getNumFood()

    def agentCrash(self, game, agentIndex):
        if agentIndex == 0:
            print("吃豆人坠毁")
        else:
            print("一个幽灵坠毁了")

    def getMaxTotalTime(self, agentIndex):
        return self.timeout

    def getMaxStartupTime(self, agentIndex):
        return self.timeout

    def getMoveWarningTime(self, agentIndex):
        return self.timeout

    def getMoveTimeout(self, agentIndex):
        return self.timeout

    def getMaxTimeWarnings(self, agentIndex):
        return 0

class PacmanRules:
    """
    这些函数控制着 pacman 如何与他的环境进行交互
    经典的游戏规则.
    """
    PACMAN_SPEED=1

    def getLegalActions( state ):
        """
        返回可能操作的列表.
        """
        return Actions.getPossibleActions( state.getPacmanState().configuration, state.data.layout.walls )
    getLegalActions = staticmethod( getLegalActions )

    def applyAction( state, action ):
        """
        编辑状态以反映操作的结果.
        """
        legal = PacmanRules.getLegalActions( state )
        if action not in legal:
            raise Exception("Illegal action " + str(action))

        pacmanState = state.data.agentStates[0]

        # 更新配置
        vector = Actions.directionToVector( action, PacmanRules.PACMAN_SPEED )
        pacmanState.configuration = pacmanState.configuration.generateSuccessor( vector )

        # 吃
        next = pacmanState.configuration.getPosition()
        nearest = nearestPoint( next )
        if manhattanDistance( nearest, next ) <= 0.5 :
        # 去除食物
            PacmanRules.consume( nearest, state )
    applyAction = staticmethod( applyAction )

    def consume( position, state ):
        x,y = position
        # 吃食物
        if state.data.food[x][y]:
            state.data.scoreChange += 10
            state.data.food = state.data.food.copy()
            state.data.food[x][y] = False
            state.data._foodEaten = position
            # TODO: 缓存食物数量？
            numFood = state.getNumFood()
            if numFood == 0 and not state.data._lose:
                state.data.scoreChange += 500
                state.data._win = True
        # 吃胶囊
        if( position in state.getCapsules() ):
            state.data.capsules.remove( position )
            state.data._capsuleEaten = position
            # 重置所有鬼魂害怕的计时器
            for index in range( 1, len( state.data.agentStates ) ):
                state.data.agentStates[index].scaredTimer = SCARED_TIME
    consume = staticmethod( consume )

class GhostRules:
    """
    这些功能决定了幽灵如何与环境互动.
    """
    GHOST_SPEED=1.0
    def getLegalActions( state, ghostIndex ):
        """
        鬼魂停不下来,除非他们
        到达死胡同,但可以在十字路口转弯 90 度.
        """
        conf = state.getGhostState( ghostIndex ).configuration
        possibleActions = Actions.getPossibleActions( conf, state.data.layout.walls )
        reverse = Actions.reverseDirection( conf.direction )
        if Directions.STOP in possibleActions:
            possibleActions.remove( Directions.STOP )
        if reverse in possibleActions and len( possibleActions ) > 1:
            possibleActions.remove( reverse )
        return possibleActions
    getLegalActions = staticmethod( getLegalActions )

    def applyAction( state, action, ghostIndex):

        legal = GhostRules.getLegalActions( state, ghostIndex )
        if action not in legal:
            raise Exception("Illegal ghost action " + str(action))

        ghostState = state.data.agentStates[ghostIndex]
        speed = GhostRules.GHOST_SPEED
        if ghostState.scaredTimer > 0: speed /= 2.0
        vector = Actions.directionToVector( action, speed )
        ghostState.configuration = ghostState.configuration.generateSuccessor( vector )
    applyAction = staticmethod( applyAction )

    def decrementTimer( ghostState):
        timer = ghostState.scaredTimer
        if timer == 1:
            ghostState.configuration.pos = nearestPoint( ghostState.configuration.pos )
        ghostState.scaredTimer = max( 0, timer - 1 )
    decrementTimer = staticmethod( decrementTimer )

    def checkDeath( state, agentIndex):
        pacmanPosition = state.getPacmanPosition()
        if agentIndex == 0: # 吃豆子刚刚搬家;任何人都可以杀了他
            for index in range( 1, len( state.data.agentStates ) ):
                ghostState = state.data.agentStates[index]
                ghostPosition = ghostState.configuration.getPosition()
                if GhostRules.canKill( pacmanPosition, ghostPosition ):
                    GhostRules.collide( state, ghostState, index )
        else:
            ghostState = state.data.agentStates[agentIndex]
            ghostPosition = ghostState.configuration.getPosition()
            if GhostRules.canKill( pacmanPosition, ghostPosition ):
                GhostRules.collide( state, ghostState, agentIndex )
    checkDeath = staticmethod( checkDeath )

    def collide( state, ghostState, agentIndex):
        if ghostState.scaredTimer > 0:
            state.data.scoreChange += 200
            GhostRules.placeGhost(state, ghostState)
            ghostState.scaredTimer = 0
            # 为第一人称添加
            state.data._eaten[agentIndex] = True
        else:
            if not state.data._win:
                state.data.scoreChange -= 500
                state.data._lose = True
    collide = staticmethod( collide )

    def canKill( pacmanPosition, ghostPosition ):
        return manhattanDistance( ghostPosition, pacmanPosition ) <= COLLISION_TOLERANCE
    canKill = staticmethod( canKill )

    def placeGhost(state, ghostState):
        ghostState.configuration = ghostState.start
    placeGhost = staticmethod( placeGhost )

#############################
#       启动游戏的框架       #
#############################

def default(str):
    return str + ' [Default: %default]'

def parseAgentArgs(str):
    if str == None: return {}
    pieces = str.split(',')
    opts = {}
    for p in pieces:
        if '=' in p:
            key, val = p.split('=')
        else:
            key,val = p, 1
        opts[key] = val
    return opts

def readCommand( argv ):
    """
    从命令行处理用于运行 pacman 的命令.
    """
    from optparse import OptionParser
    usageStr = """
    用法:      python pacman.py <options>
    例子:   (1) python pacman.py
                    - 启动互动游戏
                (2) python pacman.py --layout smallClassic --zoom 2
                OR  python pacman.py -l smallClassic -z 2
                    - 在较小的棋盘上开始互动游戏,放大
    """
    parser = OptionParser(usageStr)

    parser.add_option('-n', '--numGames', dest='numGames', type='int',
                      help=default('要玩的游戏数量'), metavar='GAMES', default=1)
    parser.add_option('-l', '--layout', dest='layout',
                      help=default('从中加载地图布局的LAYOUT_FILE'),
                      metavar='LAYOUT_FILE', default='mediumClassic')
    parser.add_option('-p', '--pacman', dest='pacman',
                      help=default('pacmanAgents 模块中要使用的Agent TYPE'),
                      metavar='TYPE', default='KeyboardAgent')
    parser.add_option('-t', '--textGraphics', action='store_true', dest='textGraphics',
                      help='仅将输出显示为文本', default=False)
    parser.add_option('-q', '--quietTextGraphics', action='store_true', dest='quietGraphics',
                      help='生成最小输出且无图形', default=False)
    parser.add_option('-g', '--ghosts', dest='ghost',
                      help=default('ghostAgents 模块中要使用的 ghost agent TYPE'),
                      metavar = 'TYPE', default='RandomGhost')
    parser.add_option('-k', '--numghosts', type='int', dest='numGhosts',
                      help=default('要使用的最大幽灵数量'), default=4)
    parser.add_option('-z', '--zoom', type='float', dest='zoom',
                      help=default('缩放图形窗口的大小'), default=1.0)
    parser.add_option('-f', '--fixRandomSeed', action='store_true', dest='fixRandomSeed',
                      help='修复了随机种子以始终玩同一游戏', default=False)
    parser.add_option('-r', '--recordActions', action='store_true', dest='record',
                      help='将游戏历史记录写入文件(按游戏时间命名)', default=False)
    parser.add_option('--replay', dest='gameToReplay',
                      help='用于重播的录制游戏文件(pickle)', default=None)
    parser.add_option('-a','--agentArgs',dest='agentArgs',
                      help='发送到Agent的逗号分隔值.例如“opt1=val1,opt2,opt3=val3”')
    parser.add_option('-x', '--numTraining', dest='numTraining', type='int',
                      help=default('有多少集正在训练(抑制输出)'), default=0)
    parser.add_option('--frameTime', dest='frameTime', type='float',
                      help=default('帧之间的延迟时间;<0 表示键盘'), default=0.1)
    parser.add_option('-c', '--catchExceptions', action='store_true', dest='catchExceptions',
                      help='在游戏期间打开异常处理和超时', default=False)
    parser.add_option('--timeout', dest='timeout', type='int',
                      help=default('Agent在单个游戏中可以花费计算的最长时间'), default=30)

    options, otherjunk = parser.parse_args(argv)
    if len(otherjunk) != 0:
        raise Exception('Command line input not understood: ' + str(otherjunk))
    args = dict()

    # 修复随机种子
    if options.fixRandomSeed: random.seed('cs188')

    # 选择布局
    args['layout'] = layout.getLayout( options.layout )
    if args['layout'] == None: raise Exception("The layout " + options.layout + " cannot be found")

    # 选择 Pacman Agent
    noKeyboard = options.gameToReplay == None and (options.textGraphics or options.quietGraphics)
    pacmanType = loadAgent(options.pacman, noKeyboard)
    agentOpts = parseAgentArgs(options.agentArgs)
    if options.numTraining > 0:
        args['numTraining'] = options.numTraining
        if 'numTraining' not in agentOpts: agentOpts['numTraining'] = options.numTraining
    pacman = pacmanType(**agentOpts) # 使用 agentArgs 实例化 Pacman
    args['pacman'] = pacman

    # 不显示训练游戏
    if 'numTrain' in agentOpts:
        options.numQuiet = int(agentOpts['numTrain'])
        options.numIgnore = int(agentOpts['numTrain'])

    # 选择幽灵Agent
    ghostType = loadAgent(options.ghost, noKeyboard)
    args['ghosts'] = [ghostType( i+1 ) for i in range( options.numGhosts )]

    # 选择显示格式
    if options.quietGraphics:
        import textDisplay
        args['display'] = textDisplay.NullGraphics()
    elif options.textGraphics:
        import textDisplay
        textDisplay.SLEEP_TIME = options.frameTime
        args['display'] = textDisplay.PacmanGraphics()
    else:
        import graphicsDisplay
        args['display'] = graphicsDisplay.PacmanGraphics(options.zoom, frameTime = options.frameTime)
    args['numGames'] = options.numGames
    args['record'] = options.record
    args['catchExceptions'] = options.catchExceptions
    args['timeout'] = options.timeout

    # 特殊情况:录制的游戏不使用 runGames 方法或 args 结构
    if options.gameToReplay != None:
        print('Replaying recorded game %s.' % options.gameToReplay)
        import pickle
        f = open(options.gameToReplay, 'rb')
        try: recorded = pickle.load(f)
        finally: f.close()
        recorded['display'] = args['display']
        replayGame(**recorded)
        sys.exit(0)

    return args

def loadAgent(pacman, nographics):
    # 在所有 pythonPath 目录中查找正确的模块,
    pythonPathStr = os.path.expandvars("$PYTHONPATH")
    if pythonPathStr.find(';') == -1:
        pythonPathDirs = pythonPathStr.split(':')
    else:
        pythonPathDirs = pythonPathStr.split(';')
    pythonPathDirs.append('.')

    for moduleDir in pythonPathDirs:
        if not os.path.isdir(moduleDir): continue
        moduleNames = [f for f in os.listdir(moduleDir) if f.endswith('gents.py')]
        for modulename in moduleNames:
            try:
                module = __import__(modulename[:-3])
            except ImportError:
                continue
            if pacman in dir(module):
                if nographics and modulename == 'keyboardAgents.py':
                    raise Exception('Using the keyboard requires graphics (not text display)')
                return getattr(module, pacman)
    raise Exception('The agent ' + pacman + ' is not specified in any *Agents.py.')

def replayGame( layout, actions, display ):
    import pacmanAgents, ghostAgents
    rules = ClassicGameRules()
    agents = [pacmanAgents.GreedyAgent()] + [ghostAgents.RandomGhost(i+1) for i in range(layout.getNumGhosts())]
    game = rules.newGame( layout, agents[0], agents[1:], display )
    state = game.state
    display.initialize(state.data)

    for action in actions:
            # 执行操作
        state = state.generateSuccessor( *action )
        # 更改显示
        display.update( state.data )
        # 允许游戏特定条件(赢、输等)
        rules.process(state, game)

    display.finish()

def runGames( layout, pacman, ghosts, display, numGames, record, numTraining = 0, catchExceptions=False, timeout=30 ):
    import __main__
    __main__.__dict__['_display'] = display

    rules = ClassicGameRules(timeout)
    games = []

    for i in range( numGames ):
        beQuiet = i < numTraining
        if beQuiet:
                # 禁止输出和图形
            import textDisplay
            gameDisplay = textDisplay.NullGraphics()
            rules.quiet = True
        else:
            gameDisplay = display
            rules.quiet = False
        game = rules.newGame( layout, pacman, ghosts, gameDisplay, beQuiet, catchExceptions)
        game.run()
        if not beQuiet: games.append(game)

        if record:
            import time, pickle
            fname = ('recorded-game-%d' % (i + 1)) +  '-'.join([str(t) for t in time.localtime()[1:6]])
            f = open(fname, 'wb')
            components = {'layout': layout, 'actions': game.moveHistory}
            pickle.dump(components, f)
            f.close()

    if (numGames-numTraining) > 0:
        scores = [game.state.getScore() for game in games]
        wins = [game.state.isWin() for game in games]
        winRate = wins.count(True)/ float(len(wins))
        print('平均分:\t\t\t', sum(scores) / float(len(scores)))
        print('分数:\t\t\t', ', '.join([str(score) for score in scores]))
        print('胜率:\t\t\t %d/%d (%.2f)' % (wins.count(True), len(wins), winRate))
        print('记录:\t\t\t', ', '.join([ ['Loss', 'Win'][int(w)] for w in wins]))

    return games

if __name__ == '__main__':
    """
    运行 pacman.py 时调用的 main 函数
    从命令行:

    > python pacman.py

    有关详细信息,请参阅用法字符串.

    > python pacman.py --help
    """
    args = readCommand( sys.argv[1:] ) # 根据输入获取游戏组件
    runGames( **args )

    # import cProfile
    # cProfile.run("runGames( **args )")
    pass
