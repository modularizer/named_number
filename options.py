class OptionGroup(object):
    def __new__(cls, options: str | list, *a, **kw):
        # print(options)
        if isinstance(options, (Charset, Wordlist)):
            return options
        if isinstance(options, str):
            return Charset(options)
        if all(isinstance(o, str) and len(o) == 1 for o in options):
            return Charset("".join(options))
        if isinstance(options, list):
            options = [str(v) for v in options]
        return Optionset(options, *a, **kw)

    def to_int(self, value: str) -> int:
        if value in self:
            return self.index(value)
        n = len(self)
        value = [v for v in value if v in self]
        vals = [self.index(v) * (n ** (len(value) - i - 1)) for i, v in enumerate(value)]
        i = sum(vals)
        return i

    def from_int(self, value: int) -> str | list:
        assert value >= 0, "value must be positive"
        n = len(self)
        if value < n:
            return self[value]
        s = []
        while value:
            s = [self[value % n]] + s
            value //= n
        if all(isinstance(_c, str) for _c in s):
            s = "".join(s)
        return s

    def bit_length(self):
        if len(self) == 0:
            return 0
        return (len(self)-1).bit_length()

    def __add__(self, other):
        return type(self)(super().__add__([v for v in other if v not in self]))

    def __radd__(self, other):
        return type(self)(super().__radd__([v for v in self if v not in other]))

    def __sub__(self, other):
        return type(self)([v for v in self if v not in other])

    def __rsub__(self, other):
        return type(self)([v for v in other if v not in self])


class Optionset(OptionGroup, list):
    def __new__(cls, *a, **kw):
        o = list.__new__(cls)
        o.__init__(*a, **kw)
        return o


class Wordlist(Optionset):
    def __init__(self, fn, load: bool = True):
        super().__init__()
        if isinstance(fn, str):
            self.fn = fn
            self.loaded = False
        else:
            self.fn = None
            self.extend(fn)
            self.loaded = True
        if load:
            self.load()

    def load(self):
        if not self.loaded:
            fn = self.fn
            if fn.endswith(".json"):
                import json
                with open(fn) as f:
                    d = json.load(f)
            elif fn.endswith(".yml") or fn.endswith(".yaml"):
                import yaml
                with open(fn) as f:
                    d = yaml.safe_load(f)
            else:
                d = [v.replace('\n', '') for v in open(fn).readlines()]
            self.extend(d)
            self.loaded = True
            return d
        return self


class Charset(OptionGroup, str):
    def __new__(cls, s):
        if isinstance(s, list):
            s = "".join(s)
        o = str.__new__(cls, s)
        o.__init__()
        return o

    def __getitem__(self, item):
        return Charset(''.join(super().__getitem__(item)))

    def from_int(self, i):
        o = super().from_int(i)
        return "".join(o)


class Options(dict):
    wordsets = {
        'colors_16': ['aqua', 'black', 'blue', 'fuchsia', 'gray', 'green', 'lime', 'maroon', 'navy', 'olive', 'purple',
                      'red', 'silver', 'teal', 'white', 'yellow'],
        'singular_animals_128': Wordlist('wordlists/128_singular_animals.txt', load=False),
        'plural_animals_128': Wordlist('wordlists/128_plural_animals.txt', load=False),
        'rgb_24bit': [(r, g, b) for b in range(256) for g in range(256) for r in range(256)],
        'singular_nouns_1k': Wordlist('wordlists/1k_singular_nouns.txt', load=False),
        'plural_nouns_1k': Wordlist('wordlists/1k_plural_nouns.txt', load=False),
        'adjectives_1k':Wordlist('wordlists/1k_adjectives.txt', load=False),
    }

    charsets = {
        'binary': '01',
        'octadecimal': '01234567',
        'decimal': '0123456789',
        'hexadecimal': '0123456789abcdef',
        'lowercase': 'abcdefghijklmnopqrstuvwxyz',
        'uppercase': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'punctuation': '!"' + "#$%&'()*+,-./:;<=>?@[\]^_`{|}~'",
        'whitespace': "".join(chr(i) for i in [32, 9, 10, 13, 11, 12]),
        'ascii_128': "".join(chr(i) for i in range(128)),
        'ascii_128_unescaped': "".join(chr(i) for i in range(128) if '\\' not in repr(chr(i))),
        'ascii_256': "".join(chr(i) for i in range(256)),
        'ascii_256_unescaped': "".join(chr(i) for i in range(256) if '\\' not in repr(chr(i))),
        'ascii_512': "".join(chr(i) for i in range(512)),
        'ascii_512_unescaped': "".join(chr(i) for i in range(512) if '\\' not in repr(chr(i))),
        'ascii_1028': "".join(chr(i) for i in range(1028)),
        'ascii_1028_unescaped': "".join(chr(i) for i in range(1028) if '\\' not in repr(chr(i))),
        'greek_lowercase': 'αβγδεζηθικλμνξοπρστυφχψω',
        'greek_uppercase': 'ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ',
        'vowels_lowercase': 'aeiou',
        'vowels_uppercase': 'AEIOU',
        'vowels': 'aeiouAEIOU',
        'consonants_lowercase': 'bcdfghjklmnpqrstvwxyz',
        'consonants_uppercase': 'BCDFGHJKLMNPQRSTVWXYZ',
        'consonants': 'bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ',
    }

    super_charsets = {
        'alphabet': charsets['lowercase'] + charsets['uppercase'],
        'alphanumeric_lowercase': charsets['lowercase'] + charsets['decimal'],
        'alphanumeric_uppercase': charsets['uppercase'] + charsets['decimal'],
        'alphanumeric': charsets['lowercase'] + charsets['uppercase'] + charsets['decimal'],
        'greek_alphabet': charsets['greek_lowercase'] + charsets['greek_uppercase']
    }
    charsets.update(super_charsets)

    groups = wordsets.copy()
    groups.update(charsets)
    
    wordset_aliases = {
        'colors': 'colors_16',
        "color": "colors_16",
        'plural_animal': 'plural_animals_128',
        'plural_animals': 'plural_animals_128',
        'animals': 'plural_animals_128',
        "singular_animal": "singular_animals_128",
        "animal": "singular_animals_128",
        'plural_nouns': 'plural_nouns_1k',
        "plural_noun": "plural_nouns_1k",
        "singular_nouns": "singular_nouns_1k",
        "singular_noun": "singular_nouns_1k",
        "noun": "singular_nouns_1k",
        'adjectives': 'adjectives_1k',
        'adjective': 'adjectives_1k',
    }
    charset_aliases = {
        'ascii_lowercase': 'lowercase',
        'az': 'lowercase',
        'ascii_uppercase': 'uppercase',
        'AZ': 'uppercase',
        'ALPHABET': 'uppercase',
        'aZ': 'alphabet',
        'english_alphabet': 'alphabet',
        'az9': 'alphanumeric_lowercase',
        'AZ9': 'alphanumeric_uppercase',
        'aZ9': 'alphanumeric',
        '09': 'decimal',
        'digits': 'decimal',
        'digit': 'decimal',
        '07': 'octadecimal',
        'octdigits': 'octadecimal',
        'octdigit': 'octadecimal',
        'hexdigits': 'hexadecimal',
        'hexdigit': 'hexadecimal',
        'hex': 'hexadecimal',
        'hs': 'hexadecimal',
        'bin': 'binary',
        'bs': 'binary',
        'printable': 'ascii_128_unescaped',
        'greek': 'greek_alphabet',
        'GREEK': 'greek_uppercase',
        'VOWELS': 'vowels_uppercase',
        'VOWEL': 'vowels_uppercase',
        'CONSONANTS': 'consonants_uppercase',
        'CONSONANT': 'consonants_uppercase',
        "vowel": "vowels",
        "consonant": "consonants"
    }
    aliases = wordset_aliases.copy()
    aliases.update(charset_aliases)

    def __init__(self, groups: dict = None, **group_kwargs):
        if groups is not None:
            self.groups.update(groups)
        self.groups.update(group_kwargs)
        super().__init__(self.groups)
      
    def __getitem__(self, item):
        if isinstance(item, str) and item.isnumeric():
            item = int(item)
        if isinstance(item, int):
            v = [str(v) for v in range(item)]
        elif isinstance(item, slice):
            start = item.start if item.start is not None else 0
            step = item.step if item.step is not None else 1
            v = [str(v) for v in range(start, item.stop, step)]
        elif item in self:
            v = super().__getitem__(item)
        elif item in self.aliases:
            v = self[self.aliases[item]]
        else:
            return None
        # print(f"{v=}, {type(v)}")
        if not isinstance(v, OptionGroup):
            v = OptionGroup(v)
            self[item] = v
        if isinstance(v, Wordlist) and not v.loaded:
            v.load()
        # print(f"{v=}")
        return v
    
    def __dir__(self):
        return list(self.keys()) + list(self.aliases.keys())

    def __repr__(self):
        return 'charsets and wordlists'

    @staticmethod
    def trim(s):
        if isinstance(s, str):
            if s.startswith('0x'):
                s = s[2:]
            if s[0] == 'b' and all(v in '01 ' for v in s[1:]):
                s = s[1:]
                s = s.replace(' ', '')
        return s
    
    @classmethod
    def identify(cls, s):
        s = cls.trim(s)

        for group_name, group in cls.groups.items():
            s_in_v = isinstance(s, str) and isinstance(group, str) and all(_char in group for _char in s)
            s_in_v |= isinstance(group, list) and s in group

            try:
                if s_in_v:
                    if group_name in cls.aliases.values():
                        for alias, val in cls.aliases.items():
                            if val == group_name:
                                return alias
                    return group_name
            except:
                pass
        return -1


options = Options()

if __name__ == "__main__":
    o = options
    # print(o.animals)

