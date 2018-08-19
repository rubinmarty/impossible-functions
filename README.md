# impossible-functions

A guide to doing some pretty impossible looking stuff in Python, based off of [this](http://math.andrej.com/2007/09/28/seemingly-impossible-functional-programs/) article by Martin Escardo.

I highly recommend just reading that link instead of this, though if you have trouble with the Haskell, this repo is intended as a more introductory version written in Python.

## Motivation

Imagine the following two Python functions:

```
def func1(arg):
    return 2 * (arg + 3)

def func2(arg):
    return (2 * arg) + 6
```

In some sense, anyone reading the above code would know that the two functions as defined are "equivalent" (at least assuming that they are only passed `int`s as input). But if you were to actually run `func1 == func2`, you wouldn't be surprised to have Python return False.

In fact, general tests for function equality are provably _impossible_ to perform, so it's no surprise that Python doesn't even bother.

What the following tutorial demonstrates is a limited case where it is actally possible to test two functions for equality. If you've made it this far and this kind of thing seems interesting to you, I hope you enjoy.
## The Types

### Basic Types

There are two basic types we will be dealing with that you should already be familiar with:

#### Natural

An integer greater than or equal to zero. We implement these using Python's `int`s, and we just take care to only use non-negative values.

#### Bool

True or False. Built in to Python as `bool`.

### Advanced Types

There are also two more complex type of objects in this guide.

#### Cantor : Natural -> Bool

A "Cantor" in this guide will be defined as a function from the Naturals to the Bools. In other words, you can think of it as a method of assigning a truth value to each integer greater than or equal to zero.

Alternatively, you can choose to view these as infinite-length lists of Bools. As an example, you can think of the Cantor that is the `is_even` function as the list `[True, False, True, False, True, ...]`, whereas the `equals_zero` function might be written as `[True, False, False, False, False, ...]`

These are implemented using the custom class `Cantor`.

#### Pred : Cantor -> Bool

A "Pred" or predicate function is a function that takes in a Cantor and returns a Bool. Possible examples of predicate functions are "is the third value in this Cantor False" and "are the first, second, and fifth values all True". Note that a Pred must be <a id="decidable-main" href="#decidable-foot">decidable</a>, so "is this Cantor made entirely of Trues" is not a valid Pred.

Predicates are implemented as standard Python functions and defined using both `def`s and `lambda`s.

---

Now that we have our types, we can fully state our motivating question: How can we write a function that will determine whether two Preds are equivalent to one another? It might seem like the only possible method would be to test that the two Preds return the same value for each possible Cantor input, but a test of this nature is clearly infeasible, given that there are a limitless number of Cantors.

In reality we can do much better.

## The Building Blocks of the Code

Let's dive right in to some implementations that will hopefully clear things up a bit.

We start with our Cantor class:

```
class Cantor(object):
    """A representation of a function from the natural
    numbers into bools. Alternatively, a representation
    of an infinite-length list of bools"""
    def __init__(self, func):
        self.func = func
        
    def __getitem__(self, index):
        return self.func(index)
```

For now, a Cantor is essentially just a thin wrapper class for a function. You can call the internal function via standard Python array indexing like so:

```
>>> cantor = Cantor(lambda i: i % 2 == 0) # The 'is_even' Cantor
>>> cantor[0]
True
>>> cantor[1]
False
>>> cantor[2]
True
>>> cantor[3]:
False
```

Let's extend this class a little bit:

```
    def __radd__(self, bools):
        def new_func(index):
            if index < len(bools):
                return bools[index]
            return self[index - len(bools)]
        return Cantor(new_func)
```

This code is a little complex, but it essentially allows us to append boolean values to the left of a cantor the same way we might do so to a normal list. Let's see it in action:

```
>>> another_cantor = [False, True] + cantor
>>> another_cantor[0]
False
>>> another_cantor[1]
True
>>> all(cantor[i] == another_cantor[i + 2] for i in range(99))
True
```

In other words, `[False, True] + cantor` works no differently than Python list addition normally does. In much the same way that `[1, 2] + [3, 4]` equals `[1, 2, 3, 4]`, we can see that `[False, True] + [True, False, True, False, ...]` equals `[False, True, True, False, True, False, ...]`. However, unlike when concatinating two lists, we are only allowed to extend on the left side of a Cantor (think about why).

Now that we have our types down, let's get to the hard part.

We define the following three functions:
  * `for_some(pred)` - determine whether there exists at least one possible input for which the predicate would return True
  * `for_every(pred)` - determine whether the predicate would return True on every single input
  * `find(pred)` - returns some Cantor which fulfils the input Pred. In the event that no such fulfilling Cantor exists, `find` can return any Cantor at all

These are defined as follows:

```
def for_some(pred):
    cantor = find(pred)
    return pred(cantor)

def for_every(pred):
    not_pred = lambda cantor: not pred(cantor)
    return not(for_some(not_pred))

def find(pred):
    if for_some(lambda cantor: pred([False] + cantor)):
        return [False] + find(lambda cantor: pred([False] + cantor))
    else:
        return [True] + find(lambda cantor: pred([True] + cantor))
```

These functions all depend on each other and can be fairly tricky to understand, so I recommend taking your time here.

`for_some` seems pretty straightforward (if we just assume that the call to `find` works) - we simply try to find a Cantor that satisfies our Pred, and if one exists then `for_some` returns `True`. But it `find` fails to locate such a Cantor, `for_some` will return `False`.

`for_every` is also pretty simple once we accept that `for_some` works - we just use a [De Morgan](https://en.wikipedia.org/wiki/De_Morgan%27s_laws) style piece of logic to say that a Pred holds on every single Cantor if its negation doesn't hold on any Cantors.

`find` is the trickiest to grok here, especially because it's defined in terms of `for_some`, which we already defined in terms of `find`. Essentially, what `find` does is it tries to to find a fulfilling Cantor that begins with a `False` - if none can be found, it returns one that begins with a `True` instead. It can definitely be hard to follow until you've traced through it with some real examples - try working through some of the test cases in the source code.

(An aside - these functions are not actually defined as written above in the source code. As given here, these functions will cause an infinite loop when evoked, and so in reality Python forces you to explicitly define them in such a way that they evaluate <a id="lazy-main" href="#lazy-foot">lazily</a>.) 

## Function Equality

Now that we have all the pieces down, the final piece of code is actually quite simple. We can define function equality as follows:

```
def equal(pred1, pred2):
    def pred3(cantor):
        return pred1(cantor) == pred2(cantor)
    return for_every(pred3)
```

In other words, two Preds are equivalent if they return the same value for every single possible Cantor input. Since we already have `for_every` defined, this function is a piece of cake.

If you're still having doubts at this point, it's likely that you don't really trust our definition of `find`. If that's the case, I encourage you reread the previous section, and really to just download the source code and run the tests yourself. Or see <a id="possible-main" href="#possible-foot">this footnote</a> for some of the intuition behind how this is all possible.

## Footnotes

### <a id="decidable-foot" href="#decidable-main">Decidability of Predicates</a>

In short, a Pred being "decidable" means that for any input we give it, it will return either True or False and not run forever.

So the following are all valid Preds:

```
def pred1(cantor):
    return cantor[0]

def pred2(cantor):
    return cantor[0] and not cantor[1] and cantor[2]

def pred3(cantor):
    if cantor[0]:
        if cantor[2] and cantor[17]:
            return cantor[5 + int(cantor[65])]
        else:
            return cantor[242]
    else:
        return True
```

Whereas the following are all invalid Preds, as they could each potentially run forever given certain inputs:
```
def pred3(cantor):
    i = 0
    while cantor[i]:
        i += 2
    return cantor[i + 1]

def pred4(cantor):
    for b in cantor:
        if b:
            return True

def pred5(cantor):
    return max(cantor)
```

### <a id="lazy-foot" href="#lazy-main">Lazy Evaluation</a>

The actual functions make heavy use of lambdas to postpone evaluation and mimic the natural behavior of Haskell. The source code defines them as follows:

```
def for_some(pred):
    cantor = Cantor(lambda i: find(pred)[i])
    return pred(cantor)

def for_every(pred):
    not_pred = lambda cantor: not pred(cantor)
    return not(for_some(not_pred))

def find(pred):
    if for_some(lambda cantor: pred([False] + cantor)):
        return [False] + Cantor(lambda i: find(lambda cantor: pred([False] + cantor))[i])
    else:
        return [True] + Cantor(lambda i: find(lambda cantor: pred([True] + cantor))[i])
```

### <a id="possible-foot" href="#possible-main">How Is Any of this Even Possible?</a>

If you're anything like me, you read all this and still have some intuition that what this code purports to do should be impossible. Functions tend to be arbitrarily complex objects, and so the idea that we should be able to compare two of them for equality just by invoking them a finite number of times seems like either madness or downright lying.

For a fuller explanation, I recommend you read the article linked at the top of this page, but essentially the trick boils down to this: the Pred functions that we use here aren't really as complex as you might think they are. Since each one has to be decidable (see footnote above), it turns out it's quite easy to prove that any particular Pred can only really look at a bounded number of elements from its input Cantor. Once you understand that, the idea that comparing two Preds is possible sounds simple - if two Preds each only look at the first N elements of their inputs, you only have to check that they behave the same on inputs of size N or less. Of course, the tricky part is how you actually compute this N, which it isn't really obvious that any of the code above is doing.

This type of code would not be possible on predicates defined on lists of integers (instead of lists of bools), because the above logic doesn't hold (bonus question: why doesn't it?)
