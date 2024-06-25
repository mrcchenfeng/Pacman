# testClasses.py
# --------------
#许可信息:您可以出于教育目的自由使用或扩展这些项目,前提是
# (1)您不散发或发布解决方案,
# (2)您保留本声明,以及
# (3)您提供明确的加州大学伯克利分校归属,包括指向 http://ai.berkeley.edu 的链接.
# 
# 归属信息:吃豆人AI项目是在加州大学伯克利分校开发的.
# 核心项目和自动评分器主要由John DeNero(denero@cs.berkeley.edu)和Dan Klein(klein@cs.berkeley.edu)创建.
# 学生端自动评分由Brad Miller、Nick Hay和Pieter Abbeel(pabbeel@cs.berkeley.edu)添加.


# 从 Python 标准库导入模块
import inspect
import re
import sys


# 一个类,用于在项目中模拟问题.请注意,
# 问题具有它们所值得的最大分数,并且由一系列测试用例组成.
class Question(object):

    def raiseNotDefined(self):
        print('方法未实现: %s' % inspect.stack()[1][3])
        sys.exit(1)

    def __init__(self, questionDict, display):
        self.maxPoints = int(questionDict['max_points'])
        self.testCases = []
        self.display = display

    def getDisplay(self):
        return self.display

    def getMaxPoints(self):
        return self.maxPoints

    # 请注意,“thunk”必须是接受单个参数的函数,
    # 即 'grading' 对象
    def addTestCase(self, testCase, thunk):
        self.testCases.append((testCase, thunk))

    def execute(self, grades):
        self.raiseNotDefined()

# 必须通过所有测试用例才能获得学分的问题
class PassAllTestsQuestion(Question):

    def execute(self, grades):
        # TODO: 这是使用成绩的正确方法吗？ 自动评分器似乎没有使用它.
        testsFailed = False
        grades.assignZeroCredit()
        for _, f in self.testCases:
            if not f(grades):
                testsFailed = True
        if testsFailed:
            grades.fail("Tests failed.")
        else:
            grades.assignFullCredit()

class ExtraCreditPassAllTestsQuestion(Question):
    def __init__(self, questionDict, display):
        Question.__init__(self, questionDict, display)
        self.extraPoints = int(questionDict['extra_points'])

    def execute(self, grades):
        # TODO: 这是使用成绩的正确方法吗？ 自动评分器似乎没有使用它.
        testsFailed = False
        grades.assignZeroCredit()
        for _, f in self.testCases:
            if not f(grades):
                testsFailed = True
        if testsFailed:
            grades.fail("Tests failed.")
        else:
            grades.assignFullCredit()
            grades.addPoints(self.extraPoints)

# 对于具有“points”属性的测试用例,在其中给出预测信用的问题.
# 所有其他测试都是强制性的,必须通过.
class HackedPartialCreditQuestion(Question):

    def execute(self, grades):
        # TODO: 这是使用成绩的正确方法吗？ 自动评分器似乎没有使用它.
        grades.assignZeroCredit()

        points = 0
        passed = True
        for testCase, f in self.testCases:
            testResult = f(grades)
            if "points" in testCase.testDict:
                if testResult: points += float(testCase.testDict["points"])
            else:
                passed = passed and testResult

        ## FIXME: 下面可怕的黑客匹配 q3 的逻辑
        if int(points) == self.maxPoints and not passed:
            grades.assignZeroCredit()
        else:
            grades.addPoints(int(points))


class Q6PartialCreditQuestion(Question):
    """未通过任何返回 False 的测试,否则不会影响 grades 对象.
    部分信用测试将增加所需的分数."""

    def execute(self, grades):
        grades.assignZeroCredit()

        results = []
        for _, f in self.testCases:
            results.append(f(grades))
        if False in results:
            grades.assignZeroCredit()

class PartialCreditQuestion(Question):
    """未通过任何返回 False 的测试,否则不会影响 grades 对象.
    部分信用测试将增加所需的分数."""

    def execute(self, grades):
        grades.assignZeroCredit()

        for _, f in self.testCases:
            if not f(grades):
                grades.assignZeroCredit()
                grades.fail("Tests failed.")
                return False



class NumberPassedQuestion(Question):
    """等级是通过的测试用例数."""

    def execute(self, grades):
        grades.addPoints([f(grades) for _, f in self.testCases].count(True))





# 通用测试用例的模板建模
class TestCase(object):

    def raiseNotDefined(self):
        print('方法未实现: %s' % inspect.stack()[1][3])
        sys.exit(1)

    def getPath(self):
        return self.path

    def __init__(self, question, testDict):
        self.question = question
        self.testDict = testDict
        self.path = testDict['path']
        self.messages = []

    def __str__(self):
        self.raiseNotDefined()

    def execute(self, grades, moduleDict, solutionDict):
        self.raiseNotDefined()

    def writeSolution(self, moduleDict, filePath):
        self.raiseNotDefined()
        return True

    # 测试应调用以下消息进行评分
    # 保证测试输出格式统一.
    #
    # TODO: 这有点棘手,但我们需要修复grading.py的接口
    # 为了得到一个漂亮的分层项目 - 问题 - 测试结构,
    # 那么这些应该被移到问题中.
    def testPass(self, grades):
        grades.addMessage('PASS: %s' % (self.path,))
        for line in self.messages:
            grades.addMessage('    %s' % (line,))
        return True

    def testFail(self, grades):
        grades.addMessage('FAIL: %s' % (self.path,))
        for line in self.messages:
            grades.addMessage('    %s' % (line,))
        return False

    # 这真的应该是问题级别的吗？
    #
    def testPartial(self, grades, points, maxPoints):
        grades.addPoints(points)
        extraCredit = max(0, points - maxPoints)
        regularCredit = points - extraCredit

        grades.addMessage('%s: %s (%s of %s points)' % ("PASS" if points >= maxPoints else "FAIL", self.path, regularCredit, maxPoints))
        if extraCredit > 0:
            grades.addMessage('EXTRA CREDIT: %s points' % (extraCredit,))

        for line in self.messages:
            grades.addMessage('    %s' % (line,))

        return True

    def addMessage(self, message):
        self.messages.extend(message.split('\n'))

