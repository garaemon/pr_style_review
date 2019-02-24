from collections import namedtuple


LinterResult = namedtuple(
    'LinterResult', ['level', 'line_number', 'message', 'linter_name',
                     'file_name'])


def pretty_print_linter_result(result_array):
    for result in result_array:
        print('{}:L{} {}'.format(result.file_name, result.line_number,
                                 result.message))
