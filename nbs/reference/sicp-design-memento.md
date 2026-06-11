# λ SICP Design Memento
*For LLM-driven software design · Python / fastai / fastcore spirit*

---

> SICP is not a book about Scheme. It is a book about controlling complexity through the disciplined use of abstraction. Its deepest lesson: **programs are not just instructions for machines — they are precise, expressive communication with other minds.**

---

## λ1 — Abstraction as the core discipline

Every problem should be solved at the *right level of abstraction*. Good design builds layers: each layer speaks a language adapted to its domain and hides the machinery below. Never reach through a layer.

**Key insight:** Name the process, not the steps.

**Ask yourself:**
- What is the "language" at this level of my system — what are its primitives, means of combination, means of abstraction?
- Am I naming a *what* or a *how*? Could I swap the implementation without changing the interface?
- If I described this module to a domain expert (not a programmer), would the names make immediate sense?

```python
# ✗ procedural noise — how
result = []
for x in data:
    if x > 0: result.append(x ** 2)

# ✓ abstraction — what  (fastcore spirit)
def positive_squares(xs):
    "Squares of positive values."
    return [x**2 for x in xs if x > 0]

# further: lift to higher-order (map/filter compose)
from fastcore.foundation import L
L(data).filter(lambda x: x>0).map(lambda x: x**2)
# fastcore's L is a list with method chaining —
# abstraction over iteration, in the spirit of SICP's sequence operations
```

**Key concepts:** procedural abstraction · data abstraction · syntactic abstraction · wishful thinking

---

## λ2 — Higher-order functions — procedures as values

Functions that accept or return functions are the principal tool for capturing common patterns. SICP shows that `map`, `filter`, `accumulate`, and `flatmap` are not library conveniences — they are the algebra of sequences.

**Key insight:** If you write the same shape twice, extract it as a higher-order procedure.

**Ask yourself:**
- Is there a repeated structural pattern (transform, filter, fold, accumulate) that could be parameterized by a function?
- Are my callbacks/lambdas getting complex? They deserve names and tests of their own.
- Could I compose two existing functions to make this third one — or do I truly need new logic?

```python
# SICP pattern: fixed-point search — general, then specialized
def fixed_point(f, first_guess, tol=1e-5):
    "Iterate f until convergence. Returns fixed point x s.t. f(x)≈x."
    x = first_guess
    while True:
        nx = f(x)
        if abs(nx - x) < tol: return nx
        x = nx

# derive sqrt via average damping — no new algorithm needed
def average_damp(f):
    return lambda x: (x + f(x)) / 2

sqrt = lambda n: fixed_point(average_damp(lambda x: n/x), 1.0)

# fastai parallel: delegates pattern — wrap behavior, not just data
from fastcore.basics import delegates

@delegates(pd.DataFrame.__init__)
class RichFrame(pd.DataFrame):
    "Adds domain methods; all DataFrame args forwarded automatically."
    pass
```

---

## λ3 — Closure & lexical scope — data hiding without classes

A closure captures its defining environment. This makes it possible to create objects with private state using only functions — no class machinery required. SICP demonstrates that objects, modules, and encapsulation emerge naturally from λ.

> "The key insight is that the object's local state is the environment in which the procedure was defined." — Abelson & Sussman

**Ask yourself:**
- Am I reaching for a class just to hold a single piece of state? A closure may be simpler and more composable.
- Is this "object" really just a configured function — would `partial` or a factory suffice?
- What is the minimal interface? Expose a function, not an object, when callers need only one operation.

```python
# closure as accumulator (SICP §3.1)
def make_accumulator(n):
    def acc(amount):
        nonlocal n
        n += amount
        return n
    return acc

# fastcore spirit: funcs as configured callables
from functools import partial

def make_scaler(mean, std):
    "Returns a normalizer closed over the dataset statistics."
    return lambda x: (x - mean) / std

normalize = make_scaler(train.mean(), train.std())
```

**Key concepts:** closure = object · dispatch table · message passing · environment model

---

## λ4 — Data abstraction & wishful thinking

Design the *interface before* the implementation. Define constructors and selectors first; write all higher-level code as if those abstractions already exist. This is "wishful thinking" as engineering method — and it maps directly to TDD and type-first design.

**Key insight:** The abstraction barrier is the contract. Violating it (reaching in to touch the representation) is the root of fragile code.

**Ask yourself:**
- Can I write the algorithm using only the interface, without knowing the representation?
- If the underlying data structure changed (list → dict → numpy array), how many call sites would break?
- Am I using a `dataclass`/`TypedDict` to make the abstraction barrier explicit and machine-checked?

```python
# wishful thinking in practice — write usage first
from dataclasses import dataclass

@dataclass
class Interval:
    "Abstraction barrier: only lo/hi are exposed."
    lo: float
    hi: float

def add_intervals(a: Interval, b: Interval) -> Interval:
    return Interval(a.lo + b.lo, a.hi + b.hi)

# fastcore: show_doc / docments make the interface the primary artifact
from fastcore.docments import docments
docments(add_intervals)  # → shows typed, documented interface
```

---

## λ5 — Metalinguistic abstraction — build the language you need

When a problem domain has its own vocabulary and rules, the most powerful move is to build a small language (DSL) whose primitives match the domain. SICP's chapters on eval/apply show that an interpreter is a small, composable structure — not a mystery.

**Key insight:** When you find yourself writing *glue code* everywhere, you're probably missing an embedded language.

**Ask yourself:**
- Is there a recurring pattern that would read more naturally as a declaration than an imperative sequence?
- Could a decorator, context manager, or `__init_subclass__` eliminate boilerplate by encoding a protocol?
- Am I building infrastructure that other developers will use? If so, what is the "language" they'll speak with it?

```python
# fastai's `delegates` + `typedispatch` ≈ a mini DSL for ML pipelines
from fastcore.dispatch import typedispatch

@typedispatch
def encode(x: str):  return x.encode()
@typedispatch
def encode(x: list): return [encode(i) for i in x]

# Wickham's R pipes are the same idea: a language of verbs for data
# df |> filter(x>0) |> mutate(y=x^2) |> summarise(mean(y))
# Python equivalent with method chaining (polars):
(df
  .filter(pl.col("x") > 0)
  .with_columns((pl.col("x")**2).alias("y"))
  .select(pl.col("y").mean())
)
```

**Key concepts:** eval / apply · DSL design · method chaining · type dispatch

---

## λ6 — State, mutation & the costs of assignment

Before SICP's chapter 3, programs are pure substitution machines — beautifully simple. Assignment introduces time, identity, and hidden dependencies. SICP teaches us that mutation is a tool with a cost, not a default.

> **The assignment axiom:** "Once we introduce assignment, a variable is no longer simply a name for a value — it is a place where a value can be stored and changed." Prefer immutability; introduce state consciously and locally.

**Ask yourself:**
- Is this variable mutated in more than one place? Could I make it the return value of a function instead?
- Could this class be replaced by a frozen `dataclass` + pure transformations?
- Where is the single source of truth for this state, and who owns the right to change it?

```python
# prefer: return new state, don't mutate
from dataclasses import replace, dataclass

@dataclass(frozen=True)
class TrainState:
    epoch: int
    loss:  float
    lr:    float

def step(state: TrainState, new_loss: float) -> TrainState:
    return replace(state, epoch=state.epoch+1, loss=new_loss)
```

---

## λ7 — Streams & lazy evaluation — decouple generation from consumption

SICP's streams (lazy lists) show that you can reason about infinite sequences by separating the *description* of a computation from its *execution*. Python generators and itertools are this idea verbatim.

**Ask yourself:**
- Am I materializing a full list when only the first N elements are needed?
- Could a generator decouple data production from processing, making each independently testable?
- Is my pipeline pulling data (generator/iterator) or pushing data (callback hell)? Pull is usually simpler.

```python
# SICP stream of primes → Python generator (same idea)
def sieve(stream):
    p = next(stream)
    yield p
    yield from sieve(x for x in stream if x % p)

from itertools import islice, count
list(islice(sieve(count(2)), 10))  # first 10 primes, lazily

# fastai DataLoader is a lazy stream: transform pipeline decoupled from training
# each batch is computed on demand — unbounded datasets, bounded memory
```

**Key concepts:** generators · itertools · yield from · lazy = decouple

---

## λ8 — The metacircular evaluator — code is data

SICP's culminating move: a Lisp interpreter written in Lisp. This homoiconicity (code and data share the same structure) is the source of macros, metaprogramming, and self-modifying systems. Python's decorators and AST tools are the same lever.

**Key insight:** If your abstraction has no representation as data, it cannot be inspected, serialized, or transformed.

**Ask yourself:**
- Can I represent my computation as data (a config dict, a graph, a typed AST) — and then interpret or compile it?
- Am I using decorators to transform functions at definition time, adding behaviour without touching the body?
- Is there a "plan" object that separates *describing* a computation from *running* it (cf. lazy evaluation, Spark DAGs, SQLAlchemy queries)?

```python
# decorator = function that transforms a function at definition time
import functools, time

def timed(fn):
    "Wraps fn; prints wall-time on each call."
    @functools.wraps(fn)
    def wrapper(*a, **kw):
        t0 = time.perf_counter()
        r  = fn(*a, **kw)
        print(f"{fn.__name__} → {time.perf_counter()-t0:.3f}s")
        return r
    return wrapper

# fastcore `patch` — adds methods to existing classes from outside
from fastcore.basics import patch

@patch
def describe(self: list): return f"list of {len(self)} items"
```

---

## λ∞ — The SICP checklist — before writing any function

### Design
- [ ] What abstraction level am I at? What are my primitives here?
- [ ] Can I name the *what* without specifying the *how*?
- [ ] Is there an abstraction barrier I should define first?
- [ ] Would wishful thinking produce a cleaner interface than bottom-up building?
- [ ] Am I solving the general problem or a special case? Should I solve the general one?

### Composition & state
- [ ] Is this function pure? If not, is the impurity isolated and explicit?
- [ ] Could this be expressed as a composition of existing higher-order functions?
- [ ] Am I introducing mutable state? Can I make it local and bounded?
- [ ] Is there a lazy/streaming version that decouples production from consumption?
- [ ] If I describe this as data, can it be inspected, tested, or replayed?

---

*Abelson & Sussman · Structure and Interpretation of Computer Programs · MIT Press*
*fastcore · fastai · tidyverse · λ all the way down*
