import ast
from .abstract_analysis import AbstractAnalysis

class TryExceptDetector(AbstractAnalysis):

  def __init__(self):
    self.try_stack = []
    self.float_lines = []
    self.report = []

  def visit_Try(self, stack, node, ref):
    self.try_stack.append(node.lineno)

  def visit_Call(self, stack, node, ref):
    if type(node.func) == ast.Name and node.func.id in ('float', 'int'):
      self.float_lines.append(node.lineno)

  def visit_ExceptHandler(self, stack, node, ref):
    if len(self.try_stack) > 0:
      floats = []
      while len(self.float_lines) > 0 and self.float_lines[-1] > self.try_stack[-1]:
        floats.append(self.float_lines.pop())
      self.report.append({
        'try': self.try_stack.pop(),
        'floats': floats,
        'except': node.lineno
      })

  def get_report(self):
      return self.report
