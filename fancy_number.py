class FancyNumber(object):
    """fancy class which can be used to subclass a number so that the result of mathmatecal operations
    return an instance of the fancy number object"""

    def math_result(self, r):
        """cast the result of a mathematical operation into"""
        try:
            return type(self)(r)
        except:
            return r

    def __add__(self, *a, **kw):
        return self.math_result(super().__add__(*a, **kw))

    def __radd__(self, *a, **kw):
        return self.math_result(super().__radd__(*a, **kw))

    def __sub__(self, *a, **kw):
        return self.math_result(super().__sub__(*a, **kw))

    def __rsub__(self, *a, **kw):
        return self.math_result(super().__rsub__(*a, **kw))

    def __mul__(self, *a, **kw):
        return self.math_result(super().__mul__(*a, **kw))

    def __rmul__(self, *a, **kw):
        return self.math_result(super().__rmul__(*a, **kw))

    def __matmul__(self, *a, **kw):
        return self.math_result(super().__matmul__(*a, **kw))

    def __rmatmul__(self, *a, **kw):
        return self.math_result(super().__rmatmul__(*a, **kw))

    def __rdiv__(self, *a, **kw):
        return self.math_result(super().__rdiv__(*a, **kw))

    def __truediv__(self, *a, **kw):
        return self.math_result(super().__truediv__(*a, **kw))

    def __rtruediv__(self, *a, **kw):
        return self.math_result(super().__rtruediv__(*a, **kw))

    def __floordiv__(self, *a, **kw):
        return self.math_result(super().__floordiv__(*a, **kw))

    def __rfloordiv__(self, *a, **kw):
        return self.math_result(super().__rfloordiv__(*a, **kw))

    def __divmod__(self, *a, **kw):
        return self.math_result(super().__divmod__(*a, **kw))

    def __rdivmod__(self, *a, **kw):
        return self.math_result(super().__rdivmod__(*a, **kw))

    def __mod__(self, *a, **kw):
        return self.math_result(super().__mod__(*a, **kw))

    def __rmod__(self, *a, **kw):
        return self.math_result(super().__rmod__(*a, **kw))

    def __rshift__(self, *a, **kw):
        return self.math_result(super().__rshift__(*a, **kw))

    def __rrshift__(self, *a, **kw):
        return self.math_result(super().__rrshift__(*a, **kw))

    def __lshift__(self, *a, **kw):
        return self.math_result(super().__lshift__(*a, **kw))

    def __rlshift__(self, *a, **kw):
        return self.math_result(super().__rlshift__(*a, **kw))

    def __pow__(self, *a, **kw):
        return self.math_result(super().__pow__(*a, **kw))

    def __rpow__(self, *a, **kw):
        return self.math_result(super().__rpow__(*a, **kw))

    def __and__(self, *a, **kw):
        return self.math_result(super().__and__(*a, **kw))

    def __rand__(self, *a, **kw):
        return self.math_result(super().__rand__(*a, **kw))

    def __or__(self, *a, **kw):
        return self.math_result(super().__or__(*a, **kw))

    def __ror__(self, *a, **kw):
        return self.math_result(super().__ror__(*a, **kw))

    def __xor__(self, *a, **kw):
        return self.math_result(super().__xor__(*a, **kw))

    def __rxor__(self, *a, **kw):
        return self.math_result(super().__rxor__(*a, **kw))

    def __abs__(self, *a, **kw):
        return self.math_result(super().__abs__(*a, **kw))

    def __invert__(self, *a, **kw):
        return self.math_result(super().__invert__(*a, **kw))

    def __pos__(self, *a, **kw):
        return self.math_result(super().__pos__(*a, **kw))

    def __neg__(self, *a, **kw):
        return self.math_result(super().__neg__(*a, **kw))

    def __round__(self, *a, **kw):
        return self.math_result(super().__round__(*a, **kw))

    def __trunc__(self, *a, **kw):
        return self.math_result(super().__trunc__(*a, **kw))


class FancyInt(FancyNumber, int):
    """a fancy integer which can be extended and will remain a FancyInt even when math is done to it"""
    @classmethod
    def from_bytes(cls, *a, **kw) -> int:
        return cls(int.from_bytes(*a, **kw))


class FancyFloat(FancyNumber, float):
    """a fancyfloat which can be extended and will remain a FancyFloat even when math is done to it"""
    @staticmethod
    def fromhex(*args, **kwargs):
        return FancyFloat(float.fromhex(*args, *kwargs))

    def __ceil__(self, *a, **kw):
        return self.math_result(super().__ceil__(*a, **kw))


if __name__ == "__main__":
    import os

    class MyMagicNumber(FancyInt):
        """a fun integer which prints itself as an additional expression"""
        def __repr__(self):
            rand = int(int.from_bytes(os.urandom(32), "little")/(1 << (32*8))*self)
            return f"{int(self -rand)} + {rand}"

    s = MyMagicNumber(50)
    for _ in range(10):
        print(f"my number is equal to {s}")
