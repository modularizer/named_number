import argparse
import json
import sys

from named_number import NamedNumber
from name_fmt import RandomizedNameFmt, NameFmt, IncrementingNameFmt


def main():
    parser = argparse.ArgumentParser(description='convert an integer to a number')
    parser.add_argument('integer', metavar='i', nargs='*', help='the integer to convert')
    parser.add_argument('--fmt', metavar='f', type=str, default="%adjective% %animal%",
                        help='the format to use for the string', required=False)
    parser.add_argument('--shuffle', action='store_true')
    parser.add_argument('--inc', dest='shuffle', action='store_false')
    parser.set_defaults(shuffle=True)
    parser.add_argument('--seed', metavar="s", type=int, default=12345, required=False)
    parser.add_argument('--byteorder', metavar="b", type=str, default=sys.byteorder, required=False)

    args, unknown = parser.parse_known_args()

    kwargs = {}
    for arg in unknown:
        if arg.startswith(("-", "--")):
            name, *values = arg.split('=')
            value = "=".join(values).replace(",", '","').replace("[",'["').replace("]",'"]')
            value = json.loads(value)
            kwargs[name[2:]] = value

    def check(v):
        if v is None:
            return v
        if v.isnumeric():
            return int(v)
        return slice(*[int(_v) if _v else None for _v in v.split(":")])

    i = [check(v) for v in args.integer]
    if len(i) == 0:
        i = None
    if len(i) == 1:
        i = i[0]

    nn = NamedNumber(i, fmt=args.fmt, fmt_type=RandomizedNameFmt if args.shuffle else IncrementingNameFmt,
                     random_seed=args.seed, byteorder=args.byteorder, **kwargs)

    if isinstance(nn, (list, tuple, set)):
        for _nn in nn:
            print(_nn)
    else:
        print(nn)


if __name__ == "__main__":
    main()
