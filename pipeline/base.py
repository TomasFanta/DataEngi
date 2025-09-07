from abc import ABC, abstractmethod

class PipelineStep(ABC):
    @abstractmethod
    def run(self, data):
        """Run step of the pipeline"""
        pass
