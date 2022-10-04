import re
import sys
import os
import math
import time
from typing import List, Tuple, Any

try:
    # trying to avoid requiring numpy (or any external packages)
    # although it is required for the RandomizedNameFmt class
    import numpy as np
except:
    np = None


from .options import Options, Optionset, Charset


class NameFmt(object):
    name_pattern = "[a-zA-Z0-9]+[a-zA-Z0-9_-]*?"
    pattern = rf"%({name_pattern}#?\d*)%"
    """regular expression pattern used to match group names in format"""

    @staticmethod
    def sub_list(pattern: str, values: list, s: str) -> str:
        """substitute values in order for each pattern match in some string"""
        i = iter(values)
        return re.sub(pattern, lambda *a: str(next(i)), s)

    @staticmethod
    def prod(arr: List[int]) -> int:
        """get the product of integers in a list"""
        mx = arr[-1]
        for b in reversed(arr[:-1]):
            mx *= b
        return mx

    @classmethod
    def list_of_components(cls, i: int, bases: list[int] | int | None = None, base: int | None = 10,
                           byteorder: str = sys.byteorder):
        """convert an integer to a list of components using a list of bases"""
        if bases is None:
            bases = base
        if isinstance(bases, int):
            bases = math.ceil(math.log(i, bases))
        else:
            mx = cls.prod(bases) - 1
            assert 0 <= i <= mx, f"value out of range [0, {mx}]"

        ordered_bases = cls.sort_by_byteorder(bases, byteorder)

        values = []
        for base in ordered_bases:
            v = i % base
            i //= base
            values.insert(0, v)
        return values

    @classmethod
    def sort_by_byteorder(cls, values: List[int | Any], byteorder: str | List[int | float] = sys.byteorder) -> list:
        assert byteorder in ["little", "big"] or isinstance(byteorder, (list, tuple)) and len(byteorder) == len(values), \
            "byte order must be 'little', 'big', or a list of values"
        if isinstance(byteorder, str):
            byteorder = byteorder.lower()
            assert byteorder in ["little", "big"], "byte order must be 'little' or 'big'"
            ordered_values = values if byteorder == "big" else reversed(values)
        elif isinstance(byteorder, (list, tuple)) and len(byteorder) == len(values):
            ordered_values = [base for _, base in sorted(zip(byteorder, values))]
        else:
            raise Exception("invalid byteorder")
        return ordered_values

    @classmethod
    def interpret_format(cls, fmt: str, options: Options | None = None) -> \
            Tuple[str, str, List[str], List[Optionset | str | List[str]], List[int], int]:
        """interpret a format string """
        if isinstance(fmt, cls):
            return fmt.fmt, fmt.match_pattern, fmt.group_names, fmt.groups, fmt.bases, fmt.max_number

        group_strs = re.findall(cls.pattern, fmt)
        group_names = []
        """list of names of all the groups used in the format"""
        fmts = []
        for group_str in group_strs:
            group_name, *a = group_str.split("#")
            group_names.append(group_name)
            n = int(a[0]) if a else 1
            group_names += (n - 1) * [group_name]
            fmts.append(f"%{group_name}%" * n)

        # safe_fmt = re.escape
        # safe_fmt = fmt  # TODO escape the input format string so that it can include . and other special characters
        fmt = cls.sub_list(cls.pattern, fmts, fmt)

        if options is None:
            options = Options()
        groups = [options[group_name] for group_name in group_names]
        bases = [len(group) for group in groups]

        group_match_patterns = [f"([{group}])" if isinstance(group, (Charset, str)) else f"({cls.name_pattern})" for group in groups]
        match_pattern = cls.sub_list(cls.pattern, group_match_patterns, fmt)
        max_number = cls.prod(bases) - 1
        return fmt, match_pattern, group_names, groups, bases, max_number

    def __init__(self, fmt: str = "%adjective% %animal%", groups: dict | None = None, rng: None = None,
                 random_seed: int | None = 12345, options: Options | None = None,  byteorder: str = sys.byteorder,
                 encrypt=None, decrypt=None, **group_kwargs):
        if options is None:
            options = Options()
        self.options = options
        if groups is not None:
            self.options.update(groups)
        self.options.update(group_kwargs)

        if encrypt is not None:
            self.encrypt = encrypt
        if decrypt is not None:
            self.decrypt = decrypt

        self.original_fmt = fmt
        self.byteorder = byteorder
        self.fmt, self.match_pattern, self.group_names, self.groups, self.bases, self.max_number = self.interpret_format(fmt, options)
        self.random_seed = random_seed
        self.rng = np.random.default_rng(random_seed) if np is not None and rng is None  and random_seed is not None else rng
        self.init_cipher()

    def name_from_int(self, i: int) -> str:
        i = self.encrypt(i)
        name = self._name_from_int(i)
        return self.reformat(name)

    def _name_from_int(self, i: int) -> str:
        assert 0 <= i <= self.max_number, "integer out of range"
        indices = self.list_of_components(i, self.bases, byteorder=self.byteorder)
        values = [self.groups[i][ind] for i, ind in enumerate(indices)]
        return self.sub_list(self.pattern, values, self.fmt)

    def strings_from_name(self, name: str) -> List[str]:
        name = self.deformat(name)
        return self._strings_from_name(name)

    def _strings_from_name(self, name: str) -> List[str]:
        values = re.fullmatch(self.match_pattern, name).groups()
        return list(values)

    def indices_from_name(self, name: str | List[str]) -> List[int]:
        name = self.deformat(name) if isinstance(name, str) else [self.deformat(n) for n in name]
        return self._indices_from_name(name)

    def _indices_from_name(self, name: str | List[str]) -> List[int]:
        if isinstance(name, str):
            values = self._strings_from_name(name)
        else:
            values = name
        indices = [group.index(values[i]) for i, group in enumerate(self.groups)]
        return indices

    def int_from_indices(self, indices: List[int]) -> int:
        v = self._int_from_indices(indices)
        return self.decrypt(v)

    def _int_from_indices(self, indices: List[int]) -> int:
        v = indices[-1]
        for i, _v in enumerate(reversed(indices[:-1])):
            v += _v * self.prod(self.bases[-i-1:])
        return v

    def int_from_name(self, name: str):
        return self.int_from_indices(self.indices_from_name(name))

    def _int_from_name(self, name: str):
        return self._int_from_indices(self._indices_from_name(name))

    def random_number(self) -> int:
        r = int.from_bytes(os.urandom(int(self.max_number.bit_length()/8)), self.byteorder) % (self.max_number + 1)
        return r

    def random_named_number(self) -> int:
        from named_number import NamedNumber
        return NamedNumber(self.random_number(), fmt=self)

    def named_number(self, i: int | None = None, **kw) -> int:
        from .named_number import NamedNumber
        if i is None:
            i = self.random_number()
        return NamedNumber(i, fmt=self, **kw)

    def __len__(self) -> int:
        return self.max_number

    def __repr__(self) -> str:
        return f"<NameFmt('{self.original_fmt}')>"

    def __call__(self, i: int | None = None, **kw) -> int:
        return self.named_number(i, **kw)

    def range(self, *a):
        return [self(i) for i in range(*a)]

    def __getitem__(self, item):
        return self(item)

    def init_cipher(self):
        pass

    def encrypt(self, i):
        return i

    def decrypt(self, i):
        return i

    def deformat(self, name):
        return name

    def reformat(self, name):
        return name

    def plot_encryption(self, x=100, require_reversible=True):
        import matplotlib.pyplot as plt

        if isinstance(x, int):
            x = range(x)

        if isinstance(x, slice):
            start = x.start if x.start is None else 0
            stop = x.stop if x.stop is not None else self.max_number + 1
            step = x.step if x.step is not None else 1
            x = range(start, stop, step)

        y = []
        for _x in x:
            _y = self.encrypt(_x)
            if require_reversible:
                assert self.decrypt(_y) == _x, "encryption not reversible"
            y.append(_y)
        plt.scatter(x, y)


class IncrementingNameFmt(NameFmt):
    pass


class RandomizedNameFmt(NameFmt):
    max_size_allowed = 1 << 23
    mappings = {}

    def init_cipher(self):
        if self.max_number not in self.mappings:
            n = self.max_number + 1
            if n > self.max_size_allowed:
                raise Exception(f"RandomizedNameFmt does not support sets greater than {self.max_size_allowed} ({n})")
            # print(f"shuffling array of size {n}")
            t0 = time.time()
            m = self.rng.permutation(self.max_number + 1)
            e = time.time() - t0
            # print(f"{e=}")
            self.mappings[self.max_number] = m
        self.mapping = self.mappings[self.max_number]

    def encrypt(self, i):
        return self.mapping[i]

    def decrypt(self, i):
        return np.argmax(self.mapping==i)

    def plot_performance(self, bit_length_range=range(28)):
        import matplotlib.pyplot as plt

        def shuffle_time(n):
            t0 = time.time()
            self.rng.permutation(n)
            return time.time() - t0

        x = list(bit_length_range)
        y = [shuffle_time(1<<_x) for _x in x]
        plt.plot(y)


if __name__ == "__main__":
    import matplotlib
    matplotlib.use('TkAgg')

    fmt = RandomizedNameFmt("%adjective% %color% %animal%")
    for i in range(10):
        print(fmt(i))

    fmt.plot_encryption()
