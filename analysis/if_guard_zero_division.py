import ast
from .abstract_analysis import AbstractAnalysisWithStack

class IfGuardZeroDivision(AbstractAnalysisWithStack):

  def __init__(self, names):
    super().__init__(names)
    self.report = []

  def visit_If(self, stack, node):
    var = None
    search_else = False
    if type(node.test) == ast.Compare and len(node.test.comparators) == 1:
      left = node.test.left
      op = type(node.test.ops[0])
      right = node.test.comparators[0]
      if (
        type(left) == ast.Name and type(left.ctx) == ast.Load
        and type(right) == ast.Num
      ):
        if (
          (op == ast.NotEq and right.n == 0)
          or (op == ast.Gt and right.n == 0)
          or (op == ast.GtE and right.n == 1)
        ):
          var = left.id
        elif op == ast.Eq and right.n == 0:
          var = left.id
          search_else = True
      elif (
        type(left) == ast.Num
        and type(right) == ast.Name and type(right.ctx) == ast.Load
      ):
        if (
          (op == ast.NotEq and left.n == 0)
          or (op == ast.Lt and left.n == 0)
          or (op == ast.LtE and left.n == 1)
        ):
          var = right.id
        elif op == ast.Eq and left.n == 0:
          var = right.id
          search_else = True
    self.add_stack({
      'if': node,
      'var': var,
      'else': search_else,
      'guarding': []
    })

  def leave_If(self, stack, node):
    top = self.pop_stack()
    if top['var'] and len(top['guarding']) > 0:
      self.report.append({
        'if': top['if'].lineno,
        'var': top['var'],
        'else': top['else'],
        'guarding': top['guarding']
      })

  def visit_BinOp(self, stack, node):
    top = self.peek_stack()
    if (
      top and (top['if'], 'orelse' if top['else'] else 'body') in stack
      and type(node.op) == ast.Div and type(node.right) == ast.Name
      and type(node.right.ctx) == ast.Load and node.right.id == top['var']
    ):
      top['guarding'].append(node.lineno)

  def get_report(self):
    return self.report
