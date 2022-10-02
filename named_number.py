from fancy_number import FancyInt

from name_fmt import NameFmt, RandomizedNameFmt, IncrementingNameFmt


class NamedNumber(FancyInt):
    def __new__(cls, i: int | str | None = None, fmt: str = "%adjective% %animal%",
                fmt_type: type = RandomizedNameFmt, groups: dict | None = None, **group_kwargs):

        name_fmt = fmt if isinstance(fmt, NameFmt) else fmt_type(fmt=fmt, groups=groups, **group_kwargs)

        # if no value is specified, generate a random value
        if i is None or i == "random":
            i = name_fmt.random_number()

        # if a string is specified, convert it to int
        if isinstance(i, str):
            i = name_fmt.int_from_name(i)

        if isinstance(i, (list, tuple, set)):
            return type(i)(cls(_i, fmt=fmt, fmt_type=fmt_type, groups=groups, **group_kwargs) for _i in i)

        if isinstance(i, slice):
            start = i.start if i.start is not None else 0
            stop = i.stop if i.stop is not None else name_fmt.max_number + 1
            step = i.step if i.step is not None else 1
            i = range(start, stop, step)

        if isinstance(i, range):
            return [cls(_i, fmt=fmt, fmt_type=fmt_type, groups=groups, **group_kwargs) for _i in i]

        if not isinstance(i, int):
            try:
                i = int(i)
            except:
                raise Exception(f"invalid input type: {type(i)}")

        # if not in valid range, just return int instead
        if isinstance(i, int) and (i < 0 or i > name_fmt.max_number):
            return i

        name = name_fmt.name_from_int(i)
        strings = name_fmt.strings_from_name(name)
        indices = name_fmt.indices_from_name(strings)

        self = int.__new__(cls, i)
        self.fmt = name_fmt
        self.name = name
        self.strings = strings
        self.indices = indices
        return self

    def __repr__(self):
        return f'<{self.name} ({super().__repr__()})>'

    def __str__(self):
        return self.name

    def math_result(self, r):
        if isinstance(r, int) and 0 <= r <= self.fmt.max_number:
            r = self.fmt(r)
        return r

    def __contains__(self, item):
        return item in self.name

    def __iter__(self):
        for i in range(len(self.indices)):
            yield self.strings[i], self.indices[i]

    def __getitem__(self, item):
        return self.name[item]

    def __setitem__(self, key, value):
        raise NotImplementedError("cannot set item on NamedNumber")

    def __eq__(self, other):
        r = super().__eq__(other)
        return r or isinstance(other, str) and other == self.name


if __name__ == "__main__":
    p = NamedNumber(0)
