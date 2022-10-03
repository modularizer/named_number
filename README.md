* [Getting Started](#getting-started)
  * [basic](#basic)
  * [why](#why)
  * [custom](#custom-format)
  
* [Command Line](#command-line)
* [Shuffling](#shuffling)
  * [limitations](#limitations)
  * [encryption placeholder](#encryption-placeholder)  
* [Stylizing](#stylizing)

# Getting started

### basic
Create an integer with a seemingly randomly shuffled name associated with it
```python
from named_number import NamedNumber
x = NamedNumber(50)
print(f"{x=}")  # x=<destructive rhino (50)>
print(str(x))  # destructive rhino
```

Mapping is one to one and reversible so you can also look up a number by its name
```python
print(int(NamedNumber("destructive rhino"))) # 50
```

### why
* fun
* just because
* generate easy to remember names for files, records, parts, etc.
* `flexible pig` is easier to remember than `116994`
* use for auto-generated temporary passwords or two-step verification

### math
Do math on it and get results in the same named format (_see fancy_number.py for how this works_)
```python
print(f"{x+1=}")  # x+1=<crucial impala (51)>
x *= 2
print(f"{x=}")  # x=<huge crocodile (100)>
```

### custom format
Specify your own format using common wordsets and character sets
```python
y = NamedNumber(422, "Bob saw %4% %adjective% %plural_animals% which were all %color%")
print(f"{y=}") # <Bob saw 3 impressive wombats which were all maroon (422)>
```

### custom wordlists
Specify your own custom wordlists
```python
z = NamedNumber(30, "%emotion%_%animal%", emotion=['happy', 'sad', 'angry', 'hungry'])
print(f"{z=}") # z=<happy_rabbit (30)>
```

### saved format
Save name formats and use them to generate numbers
```python
from named_number import RandomizedNameFmt
fmt = RandomizedNameFmt("%emotion% %animal% %hex#5%", emotion=['happy', 'sad', 'angry', 'hungry'])

print(f"{fmt(0)=}") # fmt(0)=<sad skunk 3113e (0)>
print(f"{fmt[1]=}") # fmt[1]=<happy woodchuck a48ef (1)>
print(f"{fmt[2:10:3]=}") # fmt[2:10:3]=[<hungry kookaburra 3ec9f (2)>, <hungry iguana 841c4 (5)>, <sad shark 11041 (8)>]
```

### moderately interesting
See the individual values of the components
```python
print(dict(x)) # {'huge': 151, 'crocodile': 29}
```
# Command Line

### generate a random number
```commandline
python src
```

### convert a number
```commandline
python src 51
```

### or multiple
```commandline
python src 51 52
```
```commandline
python src :5
```
```commandline
python src 10:15
```
```commandline
python src 20:40:7
```

### specify format
```commandline
python src :4 --fmt="%emotion% %pet%" --emotion=["happy","sad","angry","hungry"] --pet=["puppy","kitten","turtle","lizard"]
```

### specify --shuffle (default) or --inc
```commandline
python src :8 --fmt="%emotion% %pet%"  --inc --emotion=["happy","sad","angry","hungry"] --pet=["puppy","kitten","turtle","lizard"]
```

### specify seed
```commandline
python src 50 --seed=321
```

# Shuffling

### problem
The default functionality of the `NameFmt` object is to use the first wordlist as the high bit, second as next highest, 
etc. and to convert a number to a list of indices for the bases. Therefore, it will by default produce ordered  incrementing results.

```python
fmt = NameFmt(fmt="%first% %second%", first=["red", "green", "blue"], second=["car", "bike"])
print(fmt[:]) # [<red car (0)>, <red bike (1)>, <green car (2)>, <green bike (3)>, <blue car (4)>, <blue bike (5)>]
```

### solution
In some cases this is the desired result, but in other cases it is not. Therefore, we need some reversible way of 
scrambling the numbers, so that we instead get this.

```python
fmt = RandomizedNameFmt(fmt="%first% %second%", first=["red", "green", "blue"], second=["car", "bike"])
print(fmt[:]) # [<blue car (0)>, <green bike (1)>, <red car (2)>, <green car (3)>, <red bike (4)>, <blue bike (5)>]
```

One easy way to do this is to create a one-to-one mapping is to create a shuffled list of numbers and use the 
`index <-> value` mapping. This works well for small wordsets but scales poorly as it requires you to precompute
the large shuffled list and then store it in memory or some form of a memory-mapped file.

### limitations
`RandomizedNameFmt` works using `np.random.permutation`, but it can be **very slow to initialize if used with sets of length > (1<<23)**.
Therefore, due to memory and performance concerns, `max_size_allowed = 1 << 23`. Use `RandomizedNameFmt.plot_performance` to plot
initialization time for varying sized optionsets.


### encryption placeholder
We don't yet have a great solution, but we have left a few functions which can be overwritten to use whatever shuffling algorithm you desire.
```python
class MyNameFmt(NameFmt):
    def init_cipher(self):
        # setup here
        pass

    def encrypt(self, i):
        return (7 * i + 23) % self.max_number

    def decrypt(self, i):
        return int((i - 23 % self.max_number)/7)

my_fmt = MyNameFmt()
my_fmt.plot_encryption(50)
print(my_fmt[:5]) # [<all chimpanzee (0)>, <all doe (1)>, <all fish (2)>, <all goat (3)>, <all horse (4)>]
```


## Stylizing
To allow for additional fine-tuning of the string, we have also included placeholders for stylizing and de-stylizing the names.

```python
class sPoNGEboBNameFmt(RandomizedNameFmt):
    def reformat(self, name):
        NAME = name.upper()
        n = int(len(name)/2 + 1)
        upper = self.rng.permutation([0]*n + [1]*n)
        return "".join([NAME[i] if upper[i] else name[i] for i in range(len(name))])
    
    def deformat(self, name):
        return name.lower()

s_fmt = sPoNGEboBNameFmt()
print(s_fmt[:5]) # [<CLean GOat (0)>, <SuBjecTIve BaT (1)>, <inVALuAbLE boNObo (2)>, <TiGht groUnDHOG (3)>, <BroWn yAK (4)>]
```

## Options

### wordlists
load your own wordlist from file using the `Wordlist` class. `.json`, `.yml` are supported. for `.txt` files or other formats it is assumed that there is one word per line.
```python
from options import Wordlist
from name_fmt import RandomizedNameFmt
w = Wordlist("wordlists/128_singular_animals.txt")

r = RandomizedNameFmt("%animal%", animal=w)
```

### pre-existing lists
#### wordsets
```python
print(list(options.wordsets.keys()))
# ['colors_16', 'singular_animals_128', 'plural_animals_128', 'rgb_24bit', 'singular_nouns_1k', 'plural_nouns_1k',
# 'adjectives_1k']
```

#### charsets
```python
print(list(options.charsets.keys()))
# ['binary', 'octadecimal', 'decimal', 'hexadecimal', 'lowercase', 'uppercase', 'punctuation', 'whitespace',
# 'ascii_128', 'ascii_128_unescaped', 'ascii_256', 'ascii_256_unescaped', 'ascii_512', 'ascii_512_unescaped',
# 'ascii_1028', 'ascii_1028_unescaped', 'greek_lowercase', 'greek_uppercase', 'vowels_lowercase',
# 'vowels_uppercase', 'vowels', 'consonants_lowercase', 'consonants_uppercase', 'consonants', 'alphabet',
# 'alphanumeric_lowercase', 'alphanumeric_uppercase', 'alphanumeric', 'greek_alphabet']
```

#### wordset aliases
```python
print(list(options.wordset_aliases.keys()))
# ['colors', 'color', 'plural_animal', 'plural_animals', 'animals', 'singular_animal', 'animal', 'plural_nouns',
# 'plural_noun', 'singular_nouns', 'singular_noun', 'noun', 'adjectives', 'adjective']
```


#### charset aliases
```python
print(list(options.charset_aliases.keys()))
# ['ascii_lowercase', 'az', 'ascii_uppercase', 'AZ', 'ALPHABET', 'aZ', 'english_alphabet', 'az9', 'AZ9', 'aZ9',
# '09', 'digits', 'digit', '07', 'octdigits', 'octdigit', 'hexdigits', 'hexdigit', 'hex', 'hs', 'bin', 'bs',
# 'printable', 'greek', 'GREEK', 'VOWELS', 'VOWEL', 'CONSONANTS', 'CONSONANT', 'vowel', 'consonant']
```

### example
```python
fmt = NameFmt("%greek#7% %hex#4%")
print([fmt.random_named_number() for _ in range(5)]) # [<λΥΞΓιΕΑ 82 (34166216153218)>, <πκΟΧβΣγ 3c (47605451108924)>, <ΟξημΓψΞ 47 (119835652408647)>, <Ιψεσζωπ 78 (101633973378936)>, <τΞζΕκυΨ 9b (58779657092763)>]
```