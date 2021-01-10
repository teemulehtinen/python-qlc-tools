import ast
from .abstract_analysis import AbstractAnalysis

class NamesCollector(AbstractAnalysis):

	CLASS_TO_RESERVED_WORD = {
		ast.If: 'if', ast.For: 'for', ast.While: 'while', ast.Pass: 'pass',
		ast.Try: 'try', ast.ExceptHandler: 'except', ast.Raise: 'raise',
		ast.FunctionDef: 'def', ast.Delete: 'del', ast.Return: 'return',
		ast.Break: 'break', ast.Continue: 'continue', ast.With: 'with'
	}

	def __init__(self):
		self.scope = [{}]
		self.name_history = []

	def visit_Name(self, stack, node):
		t = type(node.ctx)
		if t == ast.Store:
			ctx = 'variable_store'
			self.scope[-1][node.id] = 'v'
		elif t == ast.Load:
			h = self.scope[-1].get(node.id, None)
			if h == 'v':
				ctx = 'variable_load'
			elif h == 'f':
				ctx = 'function_load'
			elif h == 'a':
				ctx = 'argument_load'
			else:
				ctx = 'other_load'
		self.name_history.append((node.id, node.lineno, ctx))

	def visit_FunctionDef(self, stack, node):
		self.name_history.append((node.name, node.lineno, 'function_def'))
		self.scope[-1][node.name] = 'f'
		self.scope.append(self.scope[-1].copy())

	def leave_FunctionDef(self, stack, node):
		self.scope.pop()
	
	def visit_Lambda(self, stack, node):
		self.scope.append(self.scope[-1].copy())
	
	def leave_Lambda(self, stack, node):
		self.scope.pop()

	def visit_arg(self, stack, node):
		self.name_history.append((node.arg, node.lineno, 'argument_def'))
		self.scope[-1][node.arg] = 'a'
	
	def generic_visit(self, stack, node):
		word = self.CLASS_TO_RESERVED_WORD.get(type(node))
		if word:
			self.name_history.append((word, node.lineno, 'reserved_word'))

	def get_report(self):
		return self.name_history
