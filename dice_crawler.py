# -*- coding: utf-8 -*-
#by Alex Stroev

from __future__ import division

import numpy as np

import itertools
import functools
from functools import reduce


import operator
import numbers



#these three functions are used to make operators
def make_single_func(name):
    
    op = getattr(operator, name)
        
    def result(self, op=op):
        return ComplexEvent(op, self)
    
    return result


def make_func(name):
    
    op = getattr(operator, name)
        
    def result(self, other, op=op):
        if isinstance(other, BasicEvent):
            return ComplexEvent(op, self, other)
        elif isinstance(other, numbers.Real):
            return ComplexEvent(op, self, ConstantEvent(other))
    
    return result

def make_reverse_func(name):
    
    op = getattr(operator, name)
        
    def result(self, other, op=op):
        if isinstance(other, BasicEvent):
            return ComplexEvent(op, other, self)
        elif isinstance(other, numbers.Real):
            return ComplexEvent(op, ConstantEvent(other), self)
    
    return result

def roll_d6():
    """
    Test function, that returns SimpleEvent of a single die roll.

    """
    return SimpleEvent(dict(zip(np.arange(1, 7), np.ones(6)*1/6.)))
    

class BasicEvent(object):
    
    """
    Basic class for random Event classes
    """
    
    def __init__(self):
        self.simple_events = set([self])
        self.complexity = 1
        
    def __bool__(self):
        raise ValueError('The truth value of a random event is ambiguous. '
                         'Corresponding methods are not yet implemented')
        
    __nonzero__ = __bool__
    
    def __set_item__(self, key, value):
        
        def decider(self, key, value):
            return value if key else self
        

    def reroll(self, where, new=None):
        #TODO: accept arrays as where
        if new is None:
            new = roll_d6()
        
        def _reroll(self_value, where, new_value):
            where = np.array(where)
            if self_value in where:
                return new_value
            return self_value
        
        return ComplexEvent(_reroll, self, where, new)
    
    def simplify(self):
        return self

for name in ["__add__", "__sub__", "__mul__", "__truediv__", "__floordiv__",
             "__lt__", "__le__", "__eq__", "__ne__", "__gt__", "__ge__",
             "__mod__", "__pow__"]:
    setattr(BasicEvent, name, make_func(name))
    rname = ''.join((name[:2], 'r', name[2:]))
    setattr(BasicEvent, rname, make_reverse_func(name))
    
for name in ["__neg__", "__pos__", "__abs__", "__invert__"]:
    setattr(BasicEvent, name, make_single_func(name))

class ConstantEvent(BasicEvent):
    
    """
    Numeric constants get casted to this class when interact with random Events
    """
    
    def __init__(self, value):
        super().__init__()
        self.current_value = value
        self.current_prob = 1.
        
    def __iter__(self):
        self._it = False
        return self
    
    def __next__(self):
        if not self._it:
            self._it = True
            return self, self.current_value, self.current_prob
        raise StopIteration
        
    def max(self):
        return self.current_value

class SimpleEvent(BasicEvent):
    
    """
    Random event defined by possible outcomes and their probabilities.
    """
    
    def __init__(self, outcomes=None):
        
        super().__init__()
        if outcomes is None:
            self.outcomes = {0: 1}
        else:
            self.outcomes = outcomes
        
        self.complexity = len(outcomes)

    
    def __iter__(self):
        self._it = iter(self.outcomes)
        return self
    
    def __next__(self):
        self.current_value = next(self._it)
        self.current_prob = self.outcomes[self.current_value]
        return self, self.current_value, self.current_prob
    
        
    def __str__(self):
        return pd.Series(self.outcomes).__str__()
    
    def __repr__(self):
        return pd.Series(self.outcomes).__repr__()
            
class ComplexEvent(BasicEvent):
    
    """
    Result of combining several SimpleEvent events
    """
    
    def __init__(self, func, *events):
        
        super().__init__()
        
        self.func = func
        self.events = []
        for event in events:
            if isinstance(event, numbers.Real):
                event = ConstantEvent(event)
            self.events.append(event)
        self.simple_events = set.union(*[event.simple_events for event in self.events])
        self.complexity = reduce(lambda a, ev: a*ev.complexity, 
                                 self.simple_events, 1)
        
    def simplify(self):
        #TODO: custom itertools product
        #TODO: cache?
        #TODO: simplify if only one instance of each SimpleEvent
        outs = {}
        for comb in itertools.product(*self.simple_events):
            for event, val, p in comb:
                event.current_value, event.current_prob = val, p
            new_val = self.current_value
            new_p = self.current_prob
            if new_val in outs:
                outs[new_val] += new_p
            else:
                outs[new_val] = new_p
        return SimpleEvent(outs)

    @property
    def current_value(self):
        vals = [event.current_value for event in self.events]
        return self.func(*vals)
    
    @property
    def current_prob(self):
        ps = [event.current_prob for event in self.simple_events]
        return np.product(ps)
    
    def __str__(self):
        if self.complexity > 1e7:
            return f'Random event with {self.complextiy} possible states. '
            +'Use simplify() method to make computation'
        return str(self.simplify())
    
    def __repr__(self):
        if self.complexity > 1e7:
            return f'Random event with {self.complextiy} possible states. '
            +'Use simplify() method to make computation'
        return str(self.simplify())

