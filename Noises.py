# this class is meant to implement a noise
from abc import *
import random


class Noise:
    """
    Generic Noise class, any future ones can inherit from this one.
    Each noise has to be assigned to a correlative Task_id
    """

    def __init__(self, task_id):
        self.assigned_task = task_id

    """
    generate method returns the integer that will be added to the wcet
    """
    @abstractmethod
    def generate(self):
        pass


class GaussianNoise(Noise):
    """
    Specific class for gaussian noises
    """

    def __init__(self, task_id, mean, std):
        super().__init__(task_id)
        self.mean = mean
        self.std = std

    def generate(self):
        return round(random.gauss(self.mean, self.std))

class UniformNoise(Noise):
    """
    Specific class for uniform noises, requires two endpoints
    """

    def __init__(self, task_id, low_end, high_end):
        super().__init__(task_id)
        self.low_end = low_end
        self.high_end = high_end

    def generate(self):
        return round(random.uniform(self.low_end, self.high_end))



