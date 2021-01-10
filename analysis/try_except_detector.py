import ast
from .abstract_analysis import AbstractAnalysisWithStack

class TryExceptDetector(AbstractAnalysisWithStack):

  VALUE_ERROR_CALLS = ('int', 'float')

  def __init__(self, names):
    super().__init__(names)
    self.report = []

  def visit_Try(self, stack, node):
    self.add_stack({
      'try': node,
      'causes': []
    })
  
  def visit_ExceptHandler(self, stack, node):
    top = self.peek_stack()
    if node.type == None:
      causes = top['causes']
    elif type(node.type) == ast.Name and node.type.id == 'ValueError':
      causes = [c for c in top['causes'] if c[0] in self.VALUE_ERROR_CALLS]
    elif type(node.type) == ast.Name and node.type.id == 'ZeroDivisionError':
      causes = [c for c in top['causes'] if c[0] == 'div']
    else:
      return
    self.report.append({
      'try': top['try'].lineno,
      'causes': causes,
      'except': node.lineno
    })

  def leave_Try(self, stack, node):
    self.pop_stack()

  def visit_Call(self, stack, node):
    top = self.peek_stack()
    if (
      top and (top['try'], 'body') in stack
      and type(node.func) == ast.Name and type(node.func.ctx) == ast.Load
      and node.func.id in self.VALUE_ERROR_CALLS
      and not node.func.id in self.names.scope[-1]
    ):
      top['causes'].append((node.func.id, node.lineno))

  def visit_BinOp(self, stack, node):
    top = self.peek_stack()
    if (
      top and (top['try'], 'body') in stack
      and type(node.op) == ast.Div and (type(node.right) != ast.Num or node.right.n == 0)
    ):
      top['causes'].append(('div', node.lineno))

  def get_report(self):
      return self.report
