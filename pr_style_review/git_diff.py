from pr_style_review.text_diff import compare_two_texts


class GitDiff(object):
    """
    Wrapper class for git.diff.Diff().

    GitDiff class provides suitable interfaces for reviewing.
    """

    def __init__(self, diff):
        # Initialize variables
        self.filename = None
        self._added_lines = []
        self._removed_lines = []
        self._change_type = diff.change_type
        if diff.change_type == 'D':  # deleted, no effect on linter and formatter
            pass
        elif diff.change_type == 'A':  # added
            self.filename = diff.b_path
            new_content = diff.b_blob.data_stream.read().decode('utf-8')
            print(new_content)
            self._added_lines = range(1, len(new_content.splitlines(True)) + 1)
        elif diff.change_type == 'M':  # modified
            self.filename = diff.b_path
            text_diff = compare_two_texts(
                self.filename,
                diff.a_blob.data_stream.read().decode('utf-8'),
                diff.b_blob.data_stream.read().decode('utf-8'))
            self._added_lines = text_diff.get_added_lines()
            self._removed_lines = text_diff.get_removed_lines()
        elif diff.change_type == 'R':  # renamed, no effect on linter and formatter
            pass
        elif diff.change_type == 'C':  # copied, no effect on linter and formatter
            pass

    def summary(self):
        print('Diff on {}'.format(self.filename))
        print('  {} lines are added'.format(len(self._added_lines)))
        print('  {} lines are removed'.format(len(self._removed_lines)))
