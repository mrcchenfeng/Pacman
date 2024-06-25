# textDisplay.py
# --------------
#许可信息:您可以出于教育目的自由使用或扩展这些项目,前提是
# (1)您不散发或发布解决方案,
# (2)您保留本声明,以及
# (3)您提供明确的加州大学伯克利分校归属,包括指向 http://ai.berkeley.edu 的链接.
# 
# 归属信息:吃豆人AI项目是在加州大学伯克利分校开发的.
# 核心项目和自动评分器主要由John DeNero(denero@cs.berkeley.edu)和Dan Klein(klein@cs.berkeley.edu)创建.
# 学生端自动评分由Brad Miller、Nick Hay和Pieter Abbeel(pabbeel@cs.berkeley.edu)添加.


import time
try: 
    import pacman
except:
    pass

DRAW_EVERY = 1
SLEEP_TIME = 0 # 这可以被__init__覆盖
DISPLAY_MOVES = False
QUIET = False # 抑制输出

class NullGraphics:
    def initialize(self, state, isBlue = False):
        pass

    def update(self, state):
        pass

    def checkNullDisplay(self):
        return True

    def pause(self):
        time.sleep(SLEEP_TIME)

    def draw(self, state):
        print(state)

    def updateDistributions(self, dist):
        pass

    def finish(self):
        pass

class PacmanGraphics:
    def __init__(self, speed=None):
        if speed != None:
            global SLEEP_TIME
            SLEEP_TIME = speed

    def initialize(self, state, isBlue = False):
        self.draw(state)
        self.pause()
        self.turn = 0
        self.agentCounter = 0

    def update(self, state):
        numAgents = len(state.agentStates)
        self.agentCounter = (self.agentCounter + 1) % numAgents
        if self.agentCounter == 0:
            self.turn += 1
            if DISPLAY_MOVES:
                ghosts = [pacman.nearestPoint(state.getGhostPosition(i)) for i in range(1, numAgents)]
                print("%4d) P: %-8s" % (self.turn, str(pacman.nearestPoint(state.getPacmanPosition()))),'| Score: %-5d' % state.score,'| Ghosts:', ghosts)
            if self.turn % DRAW_EVERY == 0:
                self.draw(state)
                self.pause()
        if state._win or state._lose:
            self.draw(state)

    def pause(self):
        time.sleep(SLEEP_TIME)

    def draw(self, state):
        print(state)

    def finish(self):
        pass
