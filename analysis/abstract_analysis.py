import ast

class AbstractAnalysis():
    
    def get_report(self):
        raise(NotImplementedError("Abstrach method must be implemented"))
    
    def get_class_method(self, prefix, node, default):
        return getattr(self, prefix + node.__class__.__name__, default)

    def visit(self, stack, node, ref):
        self.get_class_method('visit_', node, self.generic_visit)(stack, node, ref)

    def leave(self, stack, node, ref):
        self.get_class_method('leave_', node, self.generic_leave)(stack, node, ref)

    def generic_visit(self, stack, node, ref):
        pass

    def generic_leave(self, stack, node, ref):
        pass
