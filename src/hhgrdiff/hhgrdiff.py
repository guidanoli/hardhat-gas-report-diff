#!/usr/bin/env python3

from enum import Enum, auto

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


def print_table_line(before, after, key, keep_zeros=False, both=False, **opts):
    name = f'`{key}`'
    if key in before and key in after:
        before_avg = before[key]['avg']
        after_avg = after[key]['avg']
        if not (not keep_zeros and before_avg == after_avg):
            print_list_in_markdown_table(
                [name] + calculate_line(before_avg, after_avg))
    elif not both:
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


def print_subdict_in_markdown_table(before, after, datakey, **opts):
    before_data = before[datakey]
    after_data = after[datakey]
    all_keys = dicts_union(before_data, after_data)
    for key in all_keys:
        print_table_line(before_data, after_data, key, **opts)


def format_markdown(before, after, **opts):
    print_list_in_markdown_table(MARKDOWN_TABLE_COLUMNS)
    print_list_in_markdown_table(MARKDOWN_TABLE_ALIGNMENTS)
    print_subdict_in_markdown_table(before, after, 'methods', **opts)
    print_subdict_in_markdown_table(before, after, 'deployments', **opts)


def run(before, after, **opts):
    """Processes hardhat gas reports in files `before` and `after`
    and prints Markdown table comparing the two

    Arguments:
        before - gas report before changes
        after - gas report after changes
        opts - options dictionary

    Options:
        keep_zeros - print lines where diff is zero (default: false)
        both - only print lines where both have data (default: false)
    """
    before = new_report_dict_from_file(before)
    after = new_report_dict_from_file(after)
    format_markdown(before, after, **opts)
