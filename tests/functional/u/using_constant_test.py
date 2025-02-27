"""Verify if constant tests are used inside if statements."""
# pylint: disable=invalid-name, missing-docstring,too-few-public-methods
# pylint: disable=expression-not-assigned, useless-object-inheritance
# pylint: disable=missing-parentheses-for-call-in-test, unnecessary-comprehension, condition-evals-to-constant
# pylint: disable=use-list-literal, use-dict-literal

import collections


def function():
    yield


class Class(object):

    def method(self):
        pass


instance = Class()

if collections: # [using-constant-test]
    pass

# GenExpr
if (node for node in range(10)): # [using-constant-test]
    pass

if lambda: None: # [using-constant-test]
    pass

if function: # [using-constant-test]
    pass

if Class: # [using-constant-test]
    pass

if 2: # [using-constant-test]
    pass

if True: # [using-constant-test]
    pass

if '': # [using-constant-test]
    pass

if b'': # [using-constant-test]
    pass

if 2.0: # [using-constant-test]
    pass

if {}: # [using-constant-test]
    pass

if {1, 2, 3}: # [using-constant-test]
    pass

if (1, 2, 3): # [using-constant-test]
    pass

if (): # [using-constant-test]
    pass

if [1, 2, 3]: # [using-constant-test]
    pass

if []: # [using-constant-test]
    pass

# Generator
generator = function()
if generator: # [using-constant-test]
    pass

if 1 if 2 else 3: # [using-constant-test]
    pass

def test_comprehensions():
    [data for data in range(100) if abs] # [using-constant-test]
    [data for data in range(100) if 1] # [using-constant-test]
    (data for data in range(100) if abs) # [using-constant-test]
    (data for data in range(100) if 1) # [using-constant-test]
    {data for data in range(100) if abs} # [using-constant-test]
    {data: 1 for data in range(100) if abs} # [using-constant-test]


# UnboundMethod / Function
if Class.method:  # [using-constant-test]
    pass

# BoundMethod
if instance.method:  # [using-constant-test]
    pass

# For these, we require to do inference, even though the result can be a
# constant value. For some of them, we could determine that the test
# is constant, such as 2 + 3, but the components of the BinOp
# can be anything else (2 + somefunccall).

name = 42
if name:
    pass

if 3 + 4:
    pass

if 3 and 4:
    pass

if not 3:
    pass

if instance.method():
    pass

if 2 < 3:
    pass

if tuple((1, 2, 3)):
    pass

if dict():
    pass

if tuple():
    pass

if list():
    pass

if [1, 2, 3][:1]:
    pass

def test(*args):
    if args:
        return 42
    return None

def test_good_comprehension_checks():
    [data for data in range(100)]
    [data for data in range(100) if data]
    [data for data in range(100) if abs(data)]
    (data for data in range(100) if data)
    (data for data in range(100) if abs(data))
    {data for data in range(100) if data}
    {data for data in range(100) if abs(data)}
    {data: 1 for data in range(100) if data}
    {data: 1 for data in range(100)}
