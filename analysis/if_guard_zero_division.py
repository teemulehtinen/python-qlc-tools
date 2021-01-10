import ast
from .abstract_analysis import AbstractAnalysis

class IfGuardZeroDivision(AbstractAnalysis):

  def __init__(self):
    self.if_stack = []

  def mark_if(self, lineno, var, search_else):
    self.if_stack.append({
      'if': lineno,
      'var': var,
      'else': search_else
    })

  def visit_If(self, node):
    if type(node.test) == ast.Compare and len(node.comparators) == 1:
      left = node.left
      op = type(node.ops[0])
      right = node.comparators[0]
      if (
        type(left) == ast.Name and type(left.ctx) == ast.Load
        and type(right) == ast.Num
      ):
        if (
          (op == ast.NotEq and right.n == 0)
          or (op == ast.Gt and right.n >= 0)
          or (op == ast.GtE and right.n > 0)
        ):
          self.mark_if(node.lineno, left.id, False)
        elif op == ast.Eq and right.n == 0:
          self.mark_if(node.lineno, left.id, True)
      elif (
        type(node.Left) == ast.Num
        and type(right) == ast.Name and type(right.ctx) == ast.Load
      ):
        if (
          (op == ast.NotEq and left.n == 0)
          or (op == ast.Lt and left.n >= 0)
          or (op == ast.LtE and left.n > 0)
        ):
          self.mark_if(node.lineno, right.id, False)
        elif op == ast.Eq and left.n == 0:
          self.mark_if(node.lineno, right.id, True)

  def get_report(self):
    return {}
