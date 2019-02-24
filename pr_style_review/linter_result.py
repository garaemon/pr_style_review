import difflib
from collections import namedtuple


_LinterResult = namedtuple(
    '_LinterResult', ['level', 'line_number', 'message', 'linter_name',
                      'file_name'])


class LinterResult(_LinterResult):
    def resolve_commit_id(self, repo, rev='HEAD'):
        """
        Resolve commit id from the filename and line_number
        """

        blame_info_array = repo.blame(rev, self.file_name)
        line_number = 0
        for blame_info in blame_info_array:
            lines = blame_info[1]
            next_line_number = line_number + len(lines)
            if self.line_number > line_number and self.line_number <= next_line_number:
                return blame_info[0].hexsha
            line_number = next_line_number
        raise Exception('cannot resolve line')

    def resolve_position(self, repo, commit_id):
        diffs = repo.commit(repo.commit('{}~'.format(commit_id))).diff(commit_id)
        for d in diffs:
            if d.b_path == self.file_name:
                if d.change_type == 'A':
                    return self.line_number
                a_text = d.a_blob.data_stream.read().decode('utf-8')
                b_text = d.b_blob.data_stream.read().decode('utf-8')
                unified_diffs = difflib.unified_diff(
                    a_text.splitlines(True), b_text.splitlines(True))
                position_count = -1  # offset because unified_diff starts with '---\n' and '+++\n'
                to_file_count = 0
                this_hank_is_target = False
                for unified_line in unified_diffs:
                    if unified_line.startswith('@@'):
                        # @@ -16,5 +16,5 @@
                        plus_position = unified_line.index('+')
                        # -3 = len(' @@')
                        after_info = unified_line[plus_position+1:-3]
                        after_modification_start_line = int(after_info.split(',')[0])
                        after_modification_line_num = int(after_info.split(',')[1])
                        after_modification_end_line = after_modification_start_line + after_modification_line_num
                        print('Detect hunk L{}~L{}'.format(
                            after_modification_start_line, after_modification_end_line))
                        print('target is L{}'.format(self.line_number))
                        to_file_count = after_modification_start_line - 1
                        if (self.line_number >= after_modification_start_line and
                                self.line_number <= after_modification_end_line):
                            this_hank_is_target = True
                        else:
                            this_hank_is_target = False
                    else:
                        position_count = position_count + 1
                    if unified_line.startswith('+') or unified_line.startswith(' '):
                        to_file_count = to_file_count + 1
                        print('to_file_count = {}'.format(to_file_count))
                        if this_hank_is_target and to_file_count == self.line_number:
                            return position_count


def pretty_print_linter_result(result_array):
    for result in result_array:
        print('{}:L{} {}'.format(result.file_name, result.line_number,
                                 result.message))
