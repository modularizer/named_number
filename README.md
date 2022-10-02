# NamedNumber

Create an integer with a seemingly random name associated with it.
```python
from named_number import NamedNumber
x = NamedNumber(50)
print(f"{x=}") # x=<still red aardvark (50)>
print(str(x)) # still red aardvark
```

Do math on it and get results in the same named format.
```python
print(f"{x+1=}") # x+1=<unchanged olive rabbit (51)>
x *= 2
print(f"{x=}")# x=<huge crocodile (100)>
```

Specify your own format using common lists
```python
from options import options
print(list(options.aliases.keys()) + list(options.keys())) 
# ['colors', 'color', 'plural_animal', 'plural_animals', 'animals', 'singular_animal', 'animal', 'plural_nouns', 'plural_noun', 'singular_nouns', 'singular_noun', 'noun', 'adjectives', 'adjective', 'ascii_lowercase', 'az', 'ascii_uppercase', 'AZ', 'ALPHABET', 'aZ', 'english_alphabet', 'az9', 'AZ9', 'aZ9', '09', 'digits', 'digit', '07', 'octdigits', 'octdigit', 'hexdigits', 'hexdigit', 'hex', 'hs', 'bin', 'bs', 'printable', 'greek', 'GREEK', 'VOWELS', 'VOWEL', 'CONSONANTS', 'CONSONANT', 'vowel', 'consonant', 'colors_16', 'singular_animals_128', 'plural_animals_128', 'rgb_24bit', 'singular_nouns_1k', 'plural_nouns_1k', 'adjectives_1k', 'binary', 'octadecimal', 'decimal', 'hexadecimal', 'lowercase', 'uppercase', 'punctuation', 'whitespace', 'ascii_128', 'ascii_128_unescaped', 'ascii_256', 'ascii_256_unescaped', 'ascii_512', 'ascii_512_unescaped', 'ascii_1028', 'ascii_1028_unescaped', 'greek_lowercase', 'greek_uppercase', 'vowels_lowercase', 'vowels_uppercase', 'vowels', 'consonants_lowercase', 'consonants_uppercase', 'consonants', 'alphabet', 'alphanumeric_lowercase', 'alphanumeric_uppercase', 'alphanumeric', 'greek_alphabet']

y = NamedNumber(422, "%adjective% %color% %animal% %99%")
print(f"{y=}") # y=<confidential red porcupine 0 (422)>
```

Specify your own custom option sets
```python
z = NamedNumber(30, "%emotion%_%animal%", emotion=['happy', 'sad', 'angry', 'hungry'])
print(f"{z=}") # z=<happy_rabbit (30)>
```

Save name formats and use them to generate numbers
```python
from named_number import RandomizedNameFmt
fmt = RandomizedNameFmt("%emotion% %animal% %hex#5%", emotion=['happy', 'sad', 'angry', 'hungry'])

print(f"{fmt(0)=}") # fmt(0)=<sad skunk 3113e (0)>
print(f"{fmt[1]=}") # fmt[1]=<happy woodchuck a48ef (1)>
print(f"{fmt[2:10:3]=}") # fmt[2:10:3]=[<hungry kookaburra 3ec9f (2)>, <hungry iguana 841c4 (5)>, <sad shark 11041 (8)>]
```

See the individual values of the components
```python
print(dict(x)) # {'huge': 151, 'crocodile': 29}
```


Add custom encryption/decryption to scramble the words associated with each letter (current method is very slow and scales poorly).
Use NameFmt instead of RandomizedNameFmt for fast initialization but non-scrambled results.
```python
class RSANameFmt(NameFmt):
    def init_cipher(self):
        # setup here
        pass

    def encrypt(self, i):
        return i

    def decrypt(self, i):
        return i

n = NamedNumber(40, fmt_type=RSANameFmt)
```