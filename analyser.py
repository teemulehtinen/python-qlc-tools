#!/usr/bin/env python3
import ast
from analysis import (NamesCollector, TryExceptDetector, IfGuardZeroDivision)

class Analyser:

	@staticmethod
	def read_source_file(file_name):
		with open(file_name) as f:
			return list(f)

	def __init__(self, analysis_classes):
		self.names = NamesCollector()
		self.analysis = tuple(cls(self.names) for cls in analysis_classes)

	def analyse_source_file(self, file_name):
		lines = self.read_source_file(file_name)
		return self.analyse_root(ast.parse("".join(lines)))

	def analyse_root(self, root):
		self.visit([], root)
		return { a.__class__.__name__: a.get_report() for a in (self.names,) + self.analysis }

	def visit(self, stack, node):
		self.names.visit(stack, node)
		[a.visit(stack, node) for a in self.analysis]
		for field, value in ast.iter_fields(node):
			for item in value if isinstance(value, list) else [value]:
				if isinstance(item, ast.AST):
					self.visit(stack + [(node, field)], item)
		[a.leave(stack, node) for a in self.analysis]
		self.names.leave(stack, node)


def analyse_files(file_name_list):
	import json
	analyser = Analyser([
		TryExceptDetector,
		IfGuardZeroDivision
	])
	for file_name in file_name_list:
		print("=== {} ===".format(file_name))
		print(json.dumps(analyser.analyse_source_file(file_name), indent=4))

if __name__ == "__main__":
	import sys
	if len(sys.argv) == 1:
		print("Usage: {} [pythonsourcefiles]".format(sys.argv[0]))
	else:
		analyse_files(sys.argv[1:])
