import subprocess
import json
import sys

from pr_style_review.linter_result import LinterResult

def run_pylint(target_file, pylint_executable='pylint'):
    """
    Run pylint and return result as array of LinterResult
    """
    commands = [pylint_executable, target_file, '-f', 'json']
    try:
        pylint_output = subprocess.check_output(commands)
    except Exception as e:
        pylint_output = e.output
    # print('pylint output is "{}"'.format(pylint_output))
    pylint_result_array = json.loads(pylint_output)
    linter_result_array = []
    for pylint_result in pylint_result_array:
        # convert pylint result to LinterResult
        linter_result_array.append(LinterResult(
            linter_name='pylint',
            level=pylint_result['type'],
            line_number=pylint_result['line'],
            file_name=target_file,
            message=pylint_result['message']))
    return linter_result_array


if __name__ == '__main__':
    print(run_pylint(sys.argv[1]))
