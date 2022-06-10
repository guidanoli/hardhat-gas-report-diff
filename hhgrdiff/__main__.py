#!/usr/bin/env python3

################################################################
# Hardhat Gas Report Diff
# ==============================================================
# Steps:
# 1) Run `npx hardhat test` before and after applying
#    some change to the smart contracts you're testing
# 2) Save the gas reports into separate files (e.g.
#    `before.txt` and `after.txt`)
# 3) Run `python -m hardhat-gas-report-diff before.txt after.txt`
# 4) It should output a Markdown table showing how much each
#    method call and deployment cost changed (also in %)
################################################################

import argparse
from enum import Enum, auto
from .version import __version__

METHOD_COLUMNS = (
    'contract',
    'method',
    'min',
    'max',
    'avg',
    'calls',
    'avgeur',
)

DEPLOYMENT_COLUMNS = (
    'contract',
    'min',
    'max',
    'avg',
    'pctg',
    'avgeur',
)


class State(Enum):
    """
    Finite machine states that relate to sections of gas reports
    """
    HEADER = auto()
    METHODS = auto()
    DEPLOYMENTS = auto()


def flatten_line(line):
    """
    Convert line into a nice clean list of columns
    Example: '│ foo · bar · hello world │' ---> ['foo', 'bar', 'hello world']
    Argument:
        line - str
    Return:
        list[str]
    """
    return [col for column in line.split('·')
            if (col := column.strip('│| \n'))]


def new_report_dict_from_file(filename):
    """
    Create a report dictionary from file
    Argument:
        filename
    Return:
        report dictionary
        {
            'methods': {
                [method_name]: {see METHOD_COLUMNS}
            },
            'deployments': {
                [contract_name]: {see DEPLOYMENT_COLUMNS}
            }
        }
    """
    methods = {}
    deployments = {}
    state = State.HEADER
    next_state = state

    with open(filename) as fp:
        for line in fp:
            if state == State.HEADER:
                if 'Contract' in line:
                    next_state = State.METHODS
            elif state == State.METHODS:
                if 'Deployments' in line:
                    next_state = State.DEPLOYMENTS
                else:
                    data = flatten_line(line)
                    if len(data) == len(METHOD_COLUMNS):
                        labeled_data = dict(zip(METHOD_COLUMNS, data))
                        key = (labeled_data['contract'] +
                               '.' +
                               labeled_data['method'])
                        methods[key] = labeled_data
            elif state == State.DEPLOYMENTS:
                data = flatten_line(line)
                if len(data) == len(DEPLOYMENT_COLUMNS):
                    labeled_data = dict(zip(DEPLOYMENT_COLUMNS, data))
                    key = labeled_data['contract']
                    deployments[key] = labeled_data
            else:
                raise RuntimeError('Unkown state ' + str(state))
            state = next_state

    return dict(methods=methods, deployments=deployments)


MARKDOWN_TABLE_COLUMNS = (
    'Method call or Contract deployment',
    'Before',
    'After',
    'After - Before',
    '(After - Before) / Before',
)

MARKDOWN_TABLE_ALIGNMENTS = (
    ':-',
    ':-:',
    ':-:',
    ':-:',
    ':-:',
)


def print_list_in_markdown_table(lst):
    print('| {} |'.format(' | '.join(lst)))


def dicts_union(d1, d2):
    return sorted(set(d1) | set(d2))


def calculate_line(before, after):
    before_int = int(before)
    diff = int(after) - before_int
    diff_pct = diff / before_int
    return [before, after,
            "{:+d}".format(diff), "{:+.2f}%".format(100*diff_pct)]


def print_table_line(before, after, key, args):
    name = f'`{key}`'
    if key in before and key in after:
        before_avg = before[key]['avg']
        after_avg = after[key]['avg']
        if not (not args.keep_zeros and before_avg == after_avg):
            print_list_in_markdown_table(
                [name] + calculate_line(before_avg, after_avg))
    elif not args.both:
        if key in before:
            before_avg = before[key]['avg']
            print_list_in_markdown_table([
                name, before_avg, '-', '-', '-',
            ])
        elif key in after:
            after_avg = after[key]['avg']
            print_list_in_markdown_table([
                name, '-', after_avg, '-', '-',
            ])


def print_subdict_in_markdown_table(before, after, datakey, args):
    before_data = before[datakey]
    after_data = after[datakey]
    all_keys = dicts_union(before_data, after_data)
    for key in all_keys:
        print_table_line(before_data, after_data, key, args)


def format_markdown(before, after, args):
    print_list_in_markdown_table(MARKDOWN_TABLE_COLUMNS)
    print_list_in_markdown_table(MARKDOWN_TABLE_ALIGNMENTS)
    print_subdict_in_markdown_table(before, after, 'methods', args)
    print_subdict_in_markdown_table(before, after, 'deployments', args)


if __name__ == '__main__':
    about = ('Process hardhat gas reports and calculate the difference in ' +
             'gas costs of methods calls (on average) and of deployments')
    parser = argparse.ArgumentParser(
        prog='python -m hhgrdiff', description=about)
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
        '-z', dest='keep_zeros', action='store_true', default=False,
        help='print methods/deployments with zero average cost change')
    parser.add_argument(
        '-b', dest='both', action='store_true', default=False,
        help='only print methods/deployments with data on both reports')
    args = parser.parse_args()
    before = new_report_dict_from_file(args.before)
    after = new_report_dict_from_file(args.after)
    format_markdown(before, after, args)
