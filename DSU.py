# Disjoint Set Union (DSU) Datastructure for
# Randomized Krukal's implementation

import collections
import typing

# Creating type for a generic default key dict implementation
K = typing.TypeVar('K')
V = typing.TypeVar('V')

# Subclassing of typing.Generic is required inorder to be able to 
# pass in type hints during variable declarations
class DefaultKeyDict(collections.defaultdict, typing.Generic[K, V]):
    """
    We create our our default dict class so that we can pass in factory
    functions that work on keys, by default the key func doesnt take any arguments
    """
    def __init__(self, key_func: typing.Callable[[K], V]) -> None:
        super().__init__()
        self.key_func = key_func

    def __missing__(self, key: K) -> V:
        self[key] = self.key_func(key)
        return self[key]

class DisjointSet(typing.Generic[K]):
    def __init__(self, M: int, N: int) -> None:
        self.M, self.N = M, N
        self.sizes: collections.defaultdict[K, int] = collections.defaultdict(int)
        self.parents: DefaultKeyDict[K, K] = DefaultKeyDict(lambda pt: pt)

    def get_ultimate_parent(self, pt: K) -> K:
        if self.parents[pt] == pt:
            return pt
        else:
            self.parents[pt] = self.get_ultimate_parent(self.parents[pt])
            return self.parents[pt]

    def union(self, pt1: K, pt2: K) -> bool:
        ulp1, ulp2 = self.get_ultimate_parent(pt1), self.get_ultimate_parent(pt2)
        if ulp1 != ulp2:
            if self.sizes[ulp1] < self.sizes[ulp2]:
                self.parents[ulp1] = ulp2
                self.sizes[ulp2] += self.sizes[ulp1]
            else:
                self.parents[ulp2] = ulp1
                self.sizes[ulp1] += self.sizes[ulp2]
        return ulp1 != ulp2
