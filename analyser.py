#!/usr/bin/env python3
import ast
from analysis import (NamesCollector, TryExceptDetector)


class Analyser:

	@staticmethod
	def read_source_file(file_name):
		with open(file_name) as f:
			return list(f)

	def __init__(self, analysis_classes):
		self.analysis = tuple(cls() for cls in analysis_classes)

	def analyse_source_file(self, file_name):
		lines = self.read_source_file(file_name)
		return self.analyse_root(ast.parse("".join(lines)))

	def analyse_root(self, root):
		self.visit([], root, 'root')
		return { a.__class__.__name__: a.get_report() for a in self.analysis }

	def visit(self, stack, node, ref):
		for a in self.analysis:
			a.visit(stack, node, ref)
		for field, value in ast.iter_fields(node):
			for item in value if isinstance(value, list) else [value]:
				if isinstance(item, ast.AST):
					self.visit(stack + [node], item, field)
		for a in self.analysis:
			a.leave(stack, node, ref)


def analyse_files(file_name_list):
	import json
	analyser = Analyser([
		NamesCollector,
		TryExceptDetector
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
