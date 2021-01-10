import ast
from .abstract_analysis import AbstractAnalysis

class NamesCollector(AbstractAnalysis):

	BUILT_IN_SELECTION = [
		'abs','all','any','bool','dict','float','input','int','len','list',
		'max','min','object','open','print','range','reversed','round','set',
		'sorted','sum','tuple','zip'
	]

	CLASS_TO_RESERVED = {
		ast.If: 'if', ast.For: 'for', ast.While: 'while',
		ast.Try: 'try', ast.ExceptHandler: 'except',
		ast.FunctionDef: 'def', ast.Return: 'return'
	}

	def __init__(self):
		self.variable_names = []
		self.built_in_functions = []
		self.reserved_words = []

	def visit_Name(self, stack, node, ref):
		t = type(node.ctx)
		if t == ast.Store and not node.id in self.variable_names:
			self.variable_names.append(node.id)
		elif (
			t == ast.Load and node.id in self.BUILT_IN_SELECTION
			and not node.id in self.variable_names + self.built_in_functions
		):
			self.built_in_functions.append(node.id)

	def generic_visit(self, stack, node, ref):
		word = self.CLASS_TO_RESERVED.get(type(node))
		if word and not word in self.reserved_words:
			self.reserved_words.append(word)

	def get_report(self):
		return {
			'variable_names': self.variable_names,
			'built_in_functions': self.built_in_functions,
			'reserved_words': self.reserved_words
		}
