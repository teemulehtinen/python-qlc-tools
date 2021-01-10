from .abstract_analysis import AbstractAnalysis

class CallDetector(AbstractAnalysis):

  def __init__(self, built_ins):
    self.names = built_ins


