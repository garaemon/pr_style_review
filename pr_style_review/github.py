from github3 import login


class Github(object):

    def __init__(self, dry_run=False):
        self._dry_run = dry_run
        self._gh = None

    def login(self):
        if self._dry_run is not False:
            self._gh = login()

    def _post_review_comment(self, filename, commit, line_number, message):
        if self._dry_run is False:
            self._gh.create_review_comment(
                message, commit, filename, line_number)
        else:
            print({
                'body': message,
                'commit_id': commit,
                'position': line_number,
                'path': filename
            })

    def post_review_comment(self, commit_id, linter_result):
        self._post_review_comment(linter_result.file_name,
                                  commit_id,
                                  linter_result.line_number,
                                  linter_result.message)
