# autograder.py
# -------------
#许可信息:您可以出于教育目的自由使用或扩展这些项目,前提是
# (1)您不散发或发布解决方案,
# (2)您保留本声明,以及
# (3)您提供明确的加州大学伯克利分校归属,包括指向 http://ai.berkeley.edu 的链接.
# 
# 归属信息:吃豆人AI项目是在加州大学伯克利分校开发的.
# 核心项目和自动评分器主要由John DeNero(denero@cs.berkeley.edu)和Dan Klein(klein@cs.berkeley.edu)创建.
# 学生端自动评分由Brad Miller、Nick Hay和Pieter Abbeel(pabbeel@cs.berkeley.edu)添加.


# 从 python 标准库导入
import grading
import importlib.util
import optparse
import os
import re
import sys
import projectParams
import random
random.seed(0)
try: 
    from pacman import GameState
except:
    pass

# 注册参数并设置默认值
def readCommand(argv):
    parser = optparse.OptionParser(description = 'Run public tests on student code')
    parser.set_defaults(generateSolutions=False, edxOutput=False, gsOutput=False, muteOutput=False, printTestCase=False, noGraphics=False)
    parser.add_option('--test-directory',
                      dest = 'testRoot',
                      default = 'test_cases',
                      help = '根测试目录,包含与每个问题对应的子目录')
    parser.add_option('--student-code',
                      dest = 'studentCode',
                      default = projectParams.STUDENT_CODE_DEFAULT,
                      help = '逗号分隔的学生代码文件列表')
    parser.add_option('--code-directory',
                    dest = 'codeRoot',
                    default = "",
                    help = '包含 student 和 testClass 代码的根目录')
    parser.add_option('--test-case-code',
                      dest = 'testCaseCode',
                      default = projectParams.PROJECT_TEST_CLASSES,
                      help = '包含此项目的 testClass 类的类')
    parser.add_option('--generate-solutions',
                      dest = 'generateSolutions',
                      action = 'store_true',
                      help = '将生成的解决方案写入 .solution 文件')
    parser.add_option('--edx-output',
                    dest = 'edxOutput',
                    action = 'store_true',
                    help = '生成 edX 输出文件')
    parser.add_option('--gradescope-output',
                    dest = 'gsOutput',
                    action = 'store_true',
                    help = '生成 GradeScope 输出文件')
    parser.add_option('--mute',
                    dest = 'muteOutput',
                    action = 'store_true',
                    help = '将执行测试的输出静音')
    parser.add_option('--print-tests', '-p',
                    dest = 'printTestCase',
                    action = 'store_true',
                    help = '在运行每个测试用例之前打印它们.')
    parser.add_option('--test', '-t',
                      dest = 'runTest',
                      default = None,
                      help = '运行一个特定的测试. 相对于测试根.')
    parser.add_option('--question', '-q',
                    dest = 'gradeQuestion',
                    default = None,
                    help = '一年级特定问题.')
    parser.add_option('--no-graphics',
                    dest = 'noGraphics',
                    action = 'store_true',
                    help = '吃豆子游戏没有图形显示.')
    (options, args) = parser.parse_args(argv)
    return options


# 确认我们应编写解决方案文件
def confirmGenerate():
    print('WARNING: 此操作将覆盖任何解决方案文件.')
    print('您确定要继续吗? (yes/no)')
    while True:
        ans = sys.stdin.readline().strip()
        if ans == 'yes':
            break
        elif ans == 'no':
            sys.exit(0)
        else:
            print('请回答“yes”或“no”')


# TODO: 修复此问题,以便其回溯功能正常工作.查看回溯模块的源代码,
# 假设其工作方式与解释器相同,则它使用co_filename.然而,这是一个只读属性.
def setModuleName(module, filename):
    functionType = type(confirmGenerate)
    classType = type(optparse.Option)

    for i in dir(module):
        o = getattr(module, i)
        if hasattr(o, '__file__'): continue

        if type(o) == functionType:
            setattr(o, '__file__', filename)
        elif type(o) == classType:
            setattr(o, '__file__', filename)
            # TODO: 将成员分配为 __file__ 的？
        #print(i, type(o))


#从 cStringIO 导入 StringIO

def loadModuleString(moduleSource):
    # 下面坏了,IMP 不相信它正在传递文件:
    #    ValueError: arg#2 应为文件或 None
    #
    #f = StringIO(moduleCodeDict[k])
    #tmp = imp.load_module(k, f, k, (".py", "r", imp.PY_SOURCE))
    tmp = imp.new_module(k)
    exec(moduleCodeDict[k] in tmp.__dict__)
    setModuleName(tmp, k)
    return tmp

import py_compile

def loadModuleFile(moduleName, filePath):
    # https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
    spec = importlib.util.spec_from_file_location(moduleName, filePath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def readFile(path, root=""):
    "从指定路径的磁盘读取文件,并以字符串形式返回"
    with open(os.path.join(root, path), 'r') as handle:
        return handle.read()


#######################################################################
# 错误提示图
#######################################################################

# TODO: 使用这些
ERROR_HINT_MAP = {
  'q1': {
    "<type 'exceptions.IndexError'>": """
      我们注意到您的项目在 q1 上抛出了一个 IndexError.
      虽然许多事情可能导致这种情况,但它可能来自
      假设来自状态空间的一定数量的继任者
      或假设给定的可用操作数量
      州.尝试使代码更通用(无硬编码索引)
      并再次提交！
    """
  },
  'q3': {
      "<type 'exceptions.AttributeError'>": """
        我们注意到您的项目在 q3 上抛出了一个 AttributeError.
        虽然许多事情可能导致这种情况,但可能是由于假设
        状态空间的一定大小或结构.例如,如果您有
        一行代码,假设状态为 (x, y),我们运行您的代码
        在具有 (x, y, z) 的状态空间上,可能会引发此错误.尝试
        使您的代码更加通用并再次提交！
    """
  }
}

import pprint

def splitStrings(d):
    d2 = dict(d)
    for k in d:
        if k[0:2] == "__":
            del d2[k]
            continue
        if d2[k].find("\n") >= 0:
            d2[k] = d2[k].split("\n")
    return d2


def printTest(testDict, solutionDict):
    pp = pprint.PrettyPrinter(indent=4)
    print("Test case:")
    for line in testDict["__raw_lines__"]:
        print("   |", line)
    print("Solution:")
    for line in solutionDict["__raw_lines__"]:
        print("   |", line)


def runTest(testName, moduleDict, printTestCase=False, display=None):
    import testParser
    import testClasses
    for module in moduleDict:
        setattr(sys.modules[__name__], module, moduleDict[module])

    testDict = testParser.TestParser(testName + ".test").parse()
    solutionDict = testParser.TestParser(testName + ".solution").parse()
    test_out_file = os.path.join('%s.test_output' % testName)
    testDict['test_out_file'] = test_out_file
    testClass = getattr(projectTestClasses, testDict['class'])

    questionClass = getattr(testClasses, 'Question')
    question = questionClass({'max_points': 0}, display)
    testCase = testClass(question, testDict)

    if printTestCase:
        printTest(testDict, solutionDict)

    # 这是一个脆弱的变通方法,用于创建一个存根(stub)成绩对象
    grades = grading.Grades(projectParams.PROJECT_NAME, [(None,0)])
    testCase.execute(grades, moduleDict, solutionDict)


# 返回所有需要运行的测试,以便运行问题
def getDepends(testParser, testRoot, question):
    allDeps = [question]
    questionDict = testParser.TestParser(os.path.join(testRoot, question, 'CONFIG')).parse()
    if 'depends' in questionDict:
        depends = questionDict['depends'].split()
        for d in depends:
            # 首先运行依赖项
            allDeps = getDepends(testParser, testRoot, d) + allDeps
    return allDeps

# 获取待评分问题列表
def getTestSubdirs(testParser, testRoot, questionToGrade):
    problemDict = testParser.TestParser(os.path.join(testRoot, 'CONFIG')).parse()
    if questionToGrade != None:
        questions = getDepends(testParser, testRoot, questionToGrade)
        if len(questions) > 1:
            print('Note: 由于依赖关系,将运行以下测试:%s' % ' '.join(questions))
        return questions
    if 'order' in problemDict:
        return problemDict['order'].split()
    return sorted(os.listdir(testRoot))


# 评估学生代码
def evaluate(generateSolutions, testRoot, moduleDict, exceptionMap=ERROR_HINT_MAP,
             edxOutput=False, muteOutput=False, gsOutput=False,
            printTestCase=False, questionToGrade=None, display=None):
    # 测试台代码的导入.请注意,由于依赖关系,testClasses 的导入必须在学生代码导入之后进行.
    import testParser
    import testClasses
    for module in moduleDict:
        setattr(sys.modules[__name__], module, moduleDict[module])

    questions = []
    questionDicts = {}
    test_subdirs = getTestSubdirs(testParser, testRoot, questionToGrade)
    for q in test_subdirs:
        subdir_path = os.path.join(testRoot, q)
        if not os.path.isdir(subdir_path) or q[0] == '.':
            continue

        # 创建一个问题对象
        questionDict = testParser.TestParser(os.path.join(subdir_path, 'CONFIG')).parse()
        questionClass = getattr(testClasses, questionDict['class'])
        question = questionClass(questionDict, display)
        questionDicts[q] = questionDict

        # 将测试用例加载到问题中
        tests = filter(lambda t: re.match('[^#~.].*\.test\Z', t), os.listdir(subdir_path))
        tests = map(lambda t: re.match('(.*)\.test\Z', t).group(1), tests)
        for t in sorted(tests):
            test_file = os.path.join(subdir_path, '%s.test' % t)
            solution_file = os.path.join(subdir_path, '%s.solution' % t)
            test_out_file = os.path.join(subdir_path, '%s.test_output' % t)
            testDict = testParser.TestParser(test_file).parse()
            if testDict.get("disabled", "false").lower() == "true":
                continue
            testDict['test_out_file'] = test_out_file
            testClass = getattr(projectTestClasses, testDict['class'])
            testCase = testClass(question, testDict)
            def makefun(testCase, solution_file):
                if generateSolutions:
                    # 将解决方案文件写入磁盘
                    return lambda grades: testCase.writeSolution(moduleDict, solution_file)
                else:
                    # 读取解决方案字典并将其作为参数传递
                    testDict = testParser.TestParser(test_file).parse()
                    solutionDict = testParser.TestParser(solution_file).parse()
                    if printTestCase:
                        return lambda grades: printTest(testDict, solutionDict) or testCase.execute(grades, moduleDict, solutionDict)
                    else:
                        return lambda grades: testCase.execute(grades, moduleDict, solutionDict)
            question.addTestCase(testCase, makefun(testCase, solution_file))

        # 注意,由于作用域原因,需要额外的函数
        def makefun(question):
            return lambda grades: question.execute(grades)
        setattr(sys.modules[__name__], q, makefun(question))
        questions.append((q, question.getMaxPoints()))

    grades = grading.Grades(projectParams.PROJECT_NAME, questions,
                            gsOutput=gsOutput, edxOutput=edxOutput, muteOutput=muteOutput)
    if questionToGrade == None:
        for q in questionDicts:
            for prereq in questionDicts[q].get('depends', '').split():
                grades.addPrereq(q, prereq)

    grades.grade(sys.modules[__name__], bonusPic = projectParams.BONUS_PIC)
    return grades.points



def getDisplay(graphicsByDefault, options=None):
    graphics = graphicsByDefault
    if options is not None and options.noGraphics:
        graphics = False
    if graphics:
        try:
            import graphicsDisplay
            return graphicsDisplay.PacmanGraphics(1, frameTime=.05)
        except ImportError:
            pass
    import textDisplay
    return textDisplay.NullGraphics()




if __name__ == '__main__':
    options = readCommand(sys.argv)
    if options.generateSolutions:
        confirmGenerate()
    codePaths = options.studentCode.split(',')
    # moduleCodeDict = {}
    # for cp in codePaths:
    #     moduleName = re.match('.*?([^/]*)\.py', cp).group(1)
    #     moduleCodeDict[moduleName] = readFile(cp, root=options.codeRoot)
    # moduleCodeDict['projectTestClasses'] = readFile(options.testCaseCode, root=options.codeRoot)
    # moduleDict = loadModuleDict(moduleCodeDict)

    moduleDict = {}
    for cp in codePaths:
        moduleName = re.match('.*?([^/]*)\.py', cp).group(1)
        moduleDict[moduleName] = loadModuleFile(moduleName, os.path.join(options.codeRoot, cp))
    moduleName = re.match('.*?([^/]*)\.py', options.testCaseCode).group(1)
    moduleDict['projectTestClasses'] = loadModuleFile(moduleName, os.path.join(options.codeRoot, options.testCaseCode))


    if options.runTest != None:
        runTest(options.runTest, moduleDict, printTestCase=options.printTestCase, display=getDisplay(True, options))
    else:
        evaluate(options.generateSolutions, options.testRoot, moduleDict,
            gsOutput=options.gsOutput,
            edxOutput=options.edxOutput, muteOutput=options.muteOutput, printTestCase=options.printTestCase,
            questionToGrade=options.gradeQuestion, display=getDisplay(options.gradeQuestion!=None, options))
