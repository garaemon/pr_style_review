import os

import github3
from github3 import login


class Github(object):

    def __init__(self, dry_run=False):
        self._dry_run = dry_run
        self._gh = None
        self._pr = None

    def login(self):
        if self._dry_run is False:
            self._gh = login(username=os.environ['REVIEW_USER'],
                             token=os.environ['GITHUB_ACCESS_TOKEN'])
            owner, repo = os.environ['TRAVIS_REPO_SLUG'].split('/')
            pr_id = int(os.environ['TRAVIS_PULL_REQUEST'])
            print('target repository is {}/{} and pr id is {}'.format(
                owner, repo, pr_id))
            self._pr = self._gh.pull_request(owner, repo, pr_id)

    def _post_review_comment(self, filename, commit, line_number, message):
        if self._dry_run is False:
            try:
                self._pr.create_review_comment(message, commit, filename, line_number)
            except github3.exceptions.UnprocessableEntity as e:
                print('Detect UnprocessableEntity exception. '
                      'error message is {} and {}'.format(
                          e.message, e.errors))
                raise(e)
        else:
            print({
                'body': message,
                'commit_id': commit,
                'position': line_number,
                'path': filename
            })

    def post_review_comment(self, commit_id, position, linter_result):
        print('commenting on {}:L{} on P{}. change is {}.'.format(linter_result.file_name,
                                                                  linter_result.line_number,
                                                                  position,
                                                                  commit_id))
        self._post_review_comment(linter_result.file_name,
                                  commit_id,
                                  position,

                                  'L{}\n{}'.format(
                                      linter_result.line_number,
                                      linter_result.message
                                  ))

    def add_dummy_func(self):
        pass
