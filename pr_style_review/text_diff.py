import difflib
from collections import namedtuple


TextDiff = namedtuple(
    'TextDiff', ['change_type', 'from_text_line_number',
                 'to_text_line_number', 'content'])


class TextDiffLet(object):
    """
    Container of multiple TextDiff instances.
    """

    def __init__(self, file_name):
        self._file_name = file_name
        self._text_diff_array = []

    def add_text_diff(self, text_diff):
        self._text_diff_array.append(text_diff)

    def get_added_lines(self):
        added_lines = []
        for d in self._text_diff_array:
            if d.change_type == 'A':
                added_lines.append(d.to_text_line_number)
        return added_lines

    def get_removed_lines(self):
        removed_lines = []
        for d in self._text_diff_array:
            if d.change_type == 'D':
                removed_lines.append(d.to_text_line_number)
        return removed_lines

    def summary(self):
        print('{} lines difference are detected on {}'.format(
            len(self._text_diff_array), self._file_name))
        print('  {} lines are added'.format(
            len(
                [d for d in self._text_diff_array if d.change_type == 'A'])))
        print('  {} lines are deleted'.format(
            len(
                [d for d in self._text_diff_array if d.change_type == 'D'])))
        for d in self._text_diff_array:
            if d.change_type == 'A':
                print('L{} is added to the text'.format(d.to_text_line_number))
            if d.change_type == 'D':
                print('L{} is removed from the text'.format(d.from_text_line_number))


def compare_two_texts(file_name, from_text, to_text):
    """
    Compare two texts and return summary as TextDiffLet instance

    This implementation is based on https://bit.ly/2TghR9y.
    """
    diff_let = TextDiffLet(file_name)
    differ = difflib.Differ()
    diffs = differ.compare(from_text.splitlines(True),
                           to_text.splitlines(True))
    to_text_line_num = 0
    from_text_line_num = 0
    diff_count = 0
    for diff in diffs:
        diff_count = diff_count + 1
        code = diff[:2]
        # if there is no difference, diff should starts with two
        # white spaces('  ').
        if code in ("  ", "+ "):
            to_text_line_num += 1
        if code in ("  ", "- "):
            # if code starts with '- ', the line is deleted from
            # to_text.
            from_text_line_num += 1
        if code == "+ ":
            text_diff = TextDiff('A', from_text_line_num,
                                 to_text_line_num,
                                 diff[2:].strip())
            diff_let.add_text_diff(text_diff)
        if code == "- ":
            text_diff = TextDiff('D', from_text_line_num,
                                 to_text_line_num,
                                 diff[2:].strip())
            diff_let.add_text_diff(text_diff)
    return diff_let
