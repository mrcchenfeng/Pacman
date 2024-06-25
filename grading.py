# grading.py
# ----------
#许可信息:您可以出于教育目的自由使用或扩展这些项目,前提是
# (1)您不散发或发布解决方案,
# (2)您保留本声明,以及
# (3)您提供明确的加州大学伯克利分校归属,包括指向 http://ai.berkeley.edu 的链接.
# 
# 归属信息:吃豆人AI项目是在加州大学伯克利分校开发的.
# 核心项目和自动评分器主要由John DeNero(denero@cs.berkeley.edu)和Dan Klein(klein@cs.berkeley.edu)创建.
# 学生端自动评分由Brad Miller、Nick Hay和Pieter Abbeel(pabbeel@cs.berkeley.edu)添加.


"自动评分器的通用代码"

from html import escape
import time
import json
import traceback
from collections import defaultdict
import util

class Grades:
  "一个用于项目成绩的数据结构,以及用于显示它们的格式化代码"
  def __init__(self, projectName, questionsAndMaxesList,
               gsOutput=False, edxOutput=False, muteOutput=False):
    """
    定义了项目的评分方案
      projectName: 项目名称
      questionsAndMaxesDict: (问题名称,每个问题的最高分数)列表
    """
    self.questions = [el[0] for el in questionsAndMaxesList]
    self.maxes = dict(questionsAndMaxesList)
    self.points = Counter()
    self.messages = dict([(q, []) for q in self.questions])
    self.project = projectName
    self.start = time.localtime()[1:6]
    self.sane = True # 合理性检查
    self.currentQuestion = None # 我们正在评分的题目
    self.edxOutput = edxOutput
    self.gsOutput = gsOutput  # GradeScope 输出
    self.mute = muteOutput
    self.prereqs = defaultdict(set)

    #print('Autograder transcript for %s' % self.project)
    print('从 %d-%d 开始,时间为 %d:%0.2d:%0.2d' % self.start)

  def addPrereq(self, question, prereq):
    self.prereqs[question].add(prereq)

  def grade(self, gradingModule, exceptionMap = {}, bonusPic = False):
    """
    为每个问题评分
      gradingModule: 包含所有评分函数的模块(通过 sys.modules[__name__] 传入)
    """

    completedQuestions = set([])
    for q in self.questions:
      print('\n问题 %s' % q)
      print('=' * (9 + len(q)))
      print
      self.currentQuestion = q

      incompleted = self.prereqs[q].difference(completedQuestions)
      if len(incompleted) > 0:
          prereq = incompleted.pop()
          print(
"""*** NOTE: 在处理问题%s之前,请确保完成问题 %s,
*** 因为问题 %s 建立在问题 %s 的答案之上.
""" % (prereq, q, q, prereq))
          continue

      if self.mute: util.mutePrint()
      try:
        util.TimeoutFunction(getattr(gradingModule, q),1800)(self) # 调用问题的函数
        #TimeoutFunction(getattr(gradingModule, q),1200)(self) # 调用问题的函数
      except Exception as inst:
        self.addExceptionMessage(q, inst, traceback)
        self.addErrorHints(exceptionMap, inst, q[1])
      except:
        self.fail('FAIL:以字符串异常终止.')
      finally:
        if self.mute: util.unmutePrint()

      if self.points[q] >= self.maxes[q]:
        completedQuestions.add(q)

      print('\n### 问题 %s: %d/%d ###\n' % (q, self.points[q], self.maxes[q]))


    print('\n完成时间 %d:%02d:%02d' % time.localtime()[3:6])
    print("\n暂定等级\n==================")

    for q in self.questions:
      print('问题 %s: %d/%d' % (q, self.points[q], self.maxes[q]))
    print('------------------')
    print('总: %d/%d' % (self.points.totalCount(), sum(self.maxes.values())))
    if bonusPic and self.points.totalCount() == 25:
      print("""

                         万岁爷爷.
                        捉鬼之王万岁.

                  ---      ----      ---
                  |  \    /  + \    /  |
                  | + \--/      \--/ + |
                  |   +     +          |
                  | +     +        +   |
                @@@@@@@@@@@@@@@@@@@@@@@@@@
              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            \   @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
             \ /  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
              V   \   @@@@@@@@@@@@@@@@@@@@@@@@@@@@
                   \ /  @@@@@@@@@@@@@@@@@@@@@@@@@@
                    V     @@@@@@@@@@@@@@@@@@@@@@@@
                            @@@@@@@@@@@@@@@@@@@@@@
                    /\      @@@@@@@@@@@@@@@@@@@@@@
                   /  \  @@@@@@@@@@@@@@@@@@@@@@@@@
              /\  /    @@@@@@@@@@@@@@@@@@@@@@@@@@@
             /  \ @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            /    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                @@@@@@@@@@@@@@@@@@@@@@@@@@
                    @@@@@@@@@@@@@@@@@@

""")
    print("""
您的成绩尚未注册.要注册您的成绩,请确保遵循您的讲师的指南以获得项目学分.
""")

    if self.edxOutput:
        self.produceOutput()
    if self.gsOutput:
        self.produceGradeScopeOutput()

  def addExceptionMessage(self, q, inst, traceback):
    """
    格式化异常消息的方法,这更复杂,因为我们需要转义跟踪回溯,但将异常包装在 <pre> 标签中
    """
    self.fail('FAIL:引发异常: %s' % inst)
    self.addMessage('')
    for line in traceback.format_exc().split('\n'):
        self.addMessage(line)

  def addErrorHints(self, exceptionMap, errorInstance, questionNum):
    typeOf = str(type(errorInstance))
    questionName = 'q' + questionNum
    errorHint = ''

    # 特定于问题的错误提示
    if exceptionMap.get(questionName):
      questionMap = exceptionMap.get(questionName)
      if (questionMap.get(typeOf)):
        errorHint = questionMap.get(typeOf)
    # 如果不存在特定问题的错误消息,则回退到一般错误消息
    if (exceptionMap.get(typeOf)):
      errorHint = exceptionMap.get(typeOf)

    # 如果没有错误提示,则不包含 HTML
    if not errorHint:
      return ''

    for line in errorHint.split('\n'):
      self.addMessage(line)

  def produceGradeScopeOutput(self):
    out_dct = {}

    # 整个提交的总分
    total_possible = sum(self.maxes.values())
    total_score = sum(self.points.values())
    out_dct['score'] = total_score
    out_dct['max_score'] = total_possible
    out_dct['output'] = "总分 (%d / %d)" % (total_score, total_possible)

    # 个人测试
    tests_out = []
    for name in self.questions:
      test_out = {}
      # 测试名称
      test_out['name'] = name
      # 考试成绩
      test_out['score'] = self.points[name]
      test_out['max_score'] = self.maxes[name]
      # 别人
      is_correct = self.points[name] >= self.maxes[name]
      test_out['output'] = "  问题 {num} ({points}/{max}) {correct}".format(
          num=(name[1] if len(name) == 2 else name),
          points=test_out['score'],
          max=test_out['max_score'],
          correct=('X' if not is_correct else ''),
      )
      test_out['tags'] = []
      tests_out.append(test_out)
    out_dct['tests'] = tests_out

    # 文件输出
    with open('gradescope_response.json', 'w') as outfile:
        json.dump(out_dct, outfile)
    return

  def produceOutput(self):
    edxOutput = open('edx_response.html', 'w')
    edxOutput.write("<div>")

    # 第一次求和
    total_possible = sum(self.maxes.values())
    total_score = sum(self.points.values())
    checkOrX = '<span class="incorrect"/>'
    if (total_score >= total_possible):
        checkOrX = '<span class="correct"/>'
    header = """
        <h3>
            总分 ({total_score} / {total_possible})
        </h3>
    """.format(total_score = total_score,
      total_possible = total_possible,
      checkOrX = checkOrX
    )
    edxOutput.write(header)

    for q in self.questions:
      if len(q) == 2:
          name = q[1]
      else:
          name = q
      checkOrX = '<span class="incorrect"/>'
      if (self.points[q] >= self.maxes[q]):
        checkOrX = '<span class="correct"/>'
      #messages = '\n<br/>\n'.join(self.messages[q])
      messages = "<pre>%s</pre>" % '\n'.join(self.messages[q])
      output = """
        <div class="test">
          <section>
          <div class="shortform">
            Question {q} ({points}/{max}) {checkOrX}
          </div>
        <div class="longform">
          {messages}
        </div>
        </section>
      </div>
      """.format(q = name,
        max = self.maxes[q],
        messages = messages,
        checkOrX = checkOrX,
        points = self.points[q]
      )
      # print("*** 问题的输出 %s " % q[1])
      # print(output)
      edxOutput.write(output)
    edxOutput.write("</div>")
    edxOutput.close()
    edxOutput = open('edx_grade', 'w')
    edxOutput.write(str(self.points.totalCount()))
    edxOutput.close()

  def fail(self, message, raw=False):
    "将健全性检查位设置为 false 并输出一条消息"
    self.sane = False
    self.assignZeroCredit()
    self.addMessage(message, raw)

  def assignZeroCredit(self):
    self.points[self.currentQuestion] = 0

  def addPoints(self, amt):
    self.points[self.currentQuestion] += amt

  def deductPoints(self, amt):
    self.points[self.currentQuestion] -= amt

  def assignFullCredit(self, message="", raw=False):
    self.points[self.currentQuestion] = self.maxes[self.currentQuestion]
    if message != "":
      self.addMessage(message, raw)

  def addMessage(self, message, raw=False):
    if not raw:
        # 我们假设以 HTML 格式化的原始消息是单独打印的
        if self.mute: util.unmutePrint()
        print('*** ' + message)
        if self.mute: util.mutePrint()
        message = escape(message)
    self.messages[self.currentQuestion].append(message)

  def addMessageToEmail(self, message):
    print("WARNING**** addMessageToEmail 已弃用 %s" % message)
    for line in message.split('\n'):
      pass
      #print('%%% ' + line + ' %%%')
      #self.messages[self.currentQuestion].append(line)





class Counter(dict):
  """
  默认为 0 的 Dict
  """
  def __getitem__(self, idx):
    try:
      return dict.__getitem__(self, idx)
    except KeyError:
      return 0

  def totalCount(self):
    """
    返回所有键的计数总和.
    """
    return sum(self.values())
