import re
import sys
import os
import math
from typing import List, Tuple, Any

try:
    import numpy as np
except:
    np = None


from options import Options, Optionset, Charset


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
                 encrypt = None, decrypt = None, **group_kwargs):
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

    def init_cipher(self):
        pass

    def encrypt(self, i):
        return i

    def decrypt(self, i):
        return i

    def name_from_int(self, i: int) -> str:
        assert 0 <= i <= self.max_number, "integer out of range"
        i = self.encrypt(i)
        indices = self.list_of_components(i, self.bases, byteorder=self.byteorder)
        values = [self.groups[i][ind] for i, ind in enumerate(indices)]
        return self.sub_list(self.pattern, values, self.fmt)

    def strings_from_name(self, name: str) -> List[str]:
        values = re.fullmatch(self.match_pattern, name).groups()
        return values

    def indices_from_name(self, name: str | List[str]) -> List[int]:
        if isinstance(name, str):
            values = self.strings_from_name(name)
        else:
            values = name
        indices = [group.index(values[i]) for i, group in enumerate(self.groups)]
        return indices

    def int_from_indices(self, indices: List[int]) -> int:
        v = indices[-1]
        for i, _v in enumerate(reversed(indices[:-1])):
            v += _v * self.prod(self.bases[-i-1:])
        return self.decrypt(v)

    def int_from_name(self, name: str):
        return self.int_from_indices(self.indices_from_name(name))

    def random_number(self) -> int:
        if self.rng is not None:
            r = int(self.rng.random() * self.max_number)
        else:
            r = int.from_bytes(os.urandom(int(self.max_number.bit_length()/8)), self.byteorder) % (self.max_number + 1)
        return r

    def random_named_number(self) -> int:
        from named_number import NamedNumber
        return NamedNumber(self.random_number(), fmt=self)

    def named_number(self, i: int | None = None, **kw) -> int:
        from named_number import NamedNumber
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


class IncrementingNameFmt(NameFmt):
    pass


class RandomizedNameFmt(NameFmt):
    def init_cipher(self):
        self.mapping = self.rng.permutation(self.max_number)

    def encrypt(self, i):
        return self.mapping[i]

    def decrypt(self, i):
        return np.argmax(self.mapping==i)


if __name__ == "__main__":
    import matplotlib

    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt

    r= RandomizedNameFmt("%adjective% %color% %animal% %99%")
    # s = r.fmt_num.bit_length()

    plt.scatter(list(range(1000)), [r.encrypt(i) for i in range(1000)])
    # plt.show()