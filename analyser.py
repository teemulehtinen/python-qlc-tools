#!/usr/bin/env python3
import ast


class Analyser(ast.NodeVisitor):

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
        self.visit(root)
        return { a.__class__.__name__: a.get_report() for a in self.analysis }

    def generic_visit(self, node):
        for a in self.analysis:
            a.visit(node)
        super().generic_visit(node)

class AbstractAnalysis(ast.NodeVisitor):
    
    def get_report(self):
        raise(NotImplementedError("Abstrach method must be implemented"))
    
    def generic_visit(self, node):
        pass

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

    def visit_Name(self, node):
        t = type(node.ctx)
        if t == ast.Store and not node.id in self.variable_names:
            self.variable_names.append(node.id)
        elif (
            t == ast.Load and node.id in self.BUILT_IN_SELECTION
            and not node.id in self.variable_names + self.built_in_functions
        ):
            self.built_in_functions.append(node.id)

    def generic_visit(self, node):
        word = self.CLASS_TO_RESERVED.get(type(node))
        if word and not word in self.reserved_words:
            self.reserved_words.append(word)

    def get_report(self):
        return {
            'variable_names': self.variable_names,
            'built_in_functions': self.built_in_functions,
            'reserved_words': self.reserved_words
        }

class TryFloatExceptDetector(AbstractAnalysis):

    def __init__(self):
        self.try_stack = []
        self.float_lines = []
        self.report = []

    def visit_Try(self, node):
        self.try_stack.append(node.lineno)

    def visit_Call(self, node):
        if type(node.func) == ast.Name and node.func.id == 'float':
            self.float_lines.append(node.lineno)

    def visit_ExceptHandler(self, node):
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



def analyse_files(file_name_list):
    import json
    analyser = Analyser([
        NamesCollector,
        TryFloatExceptDetector
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
