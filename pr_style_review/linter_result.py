from collections import namedtuple


LinterResult = namedtuple(
    'LinterResult', ['level', 'line_number', 'message', 'linter_name',
                     'file_name'])
