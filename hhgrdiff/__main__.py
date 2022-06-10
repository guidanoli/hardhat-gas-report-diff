import argparse

from .version import __version__
from .hhgrdiff import run


if __name__ == '__main__':
    about = ('Process hardhat gas reports and calculate the difference in ' +
             'gas costs of methods calls (on average) and of deployments')
    parser = argparse.ArgumentParser(
        prog='hhgrdiff', description=about)
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument(
        'before',
        type=str,
        help='filename of report before change')
    parser.add_argument(
        'after',
        type=str,
        help='filename of report after change')
    parser.add_argument(
        '-z',
        dest='keep_zeros',
        action='store_true',
        default=False,
        help=('print methods/deployments with zero average cost change ' +
              '(default: off)'))
    parser.add_argument(
        '-b', dest='both', action='store_true', default=False,
        help=('only print methods/deployments with data on both reports ' +
              '(default: off)'))
    args = parser.parse_args()
    run(args.before,
        args.after,
        keep_zeros=args.keep_zeros,
        both=args.both)
