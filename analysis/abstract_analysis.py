import ast

class AbstractAnalysis():
    
    def get_report(self):
        raise(NotImplementedError("Abstrach method must be implemented"))
    
    def get_class_method(self, prefix, node, default):
        return getattr(self, prefix + node.__class__.__name__, default)

    def visit(self, stack, node):
        self.get_class_method('visit_', node, self.generic_visit)(stack, node)

    def leave(self, stack, node):
        self.get_class_method('leave_', node, self.generic_leave)(stack, node)

    def generic_visit(self, stack, node):
        pass

    def generic_leave(self, stack, node):
        pass

class AbstractAnalysisWithStack(AbstractAnalysis):

    def __init__(self, names):
        self.names = names
        self.local_stack = []
    
    def add_stack(self, item):
        self.local_stack.append(item)
    
    def peek_stack(self):
        if len(self.local_stack) > 0:
            return self.local_stack[-1]
        return None

    def pop_stack(self):
        return self.local_stack.pop()
