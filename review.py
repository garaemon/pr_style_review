#!/usr/bin/env python

import os
import sys

from argparse import ArgumentParser

from git import Repo
from pr_style_review.git_diff import GitDiff
from pr_style_review.pylint import run_pylint
from pr_style_review.linter_result import pretty_print_linter_result
from pr_style_review.github import Github


def main(git_repo, target, dry_run):
    gh = Github(dry_run=dry_run)
    gh.login()
    repo = Repo.init(git_repo)
    # create diff object from target to head
    before_commit = repo.commit(target)
    head_commit_id = repo.head.commit.hexsha
    diff_array_to_head = before_commit.diff('HEAD')
    # diff_array_to_head is an array of git diff object.
    # Each object represents change to one file.
    if 'TRAVIS_PULL_REQUEST_SHA' in os.environ:
        pr_head_commit_id = os.environ['TRAVIS_PULL_REQUEST_SHA']
    else:
        pr_head_commit_id = ''
    print('head_commit_id: {}'.format(head_commit_id))
    print('pr_head_commit_id: {}'.format(pr_head_commit_id))
    diffs = [GitDiff(d) for d in diff_array_to_head]
    changed_files = [d for d in diffs if d.filename is not None]
    for diff in changed_files:
        print('Detect change in {}'.format(diff.filename))
        filename = diff.filename
        if filename.endswith('.py'):
            print('Run pylint on {}'.format(filename))
            linter_result_array = run_pylint(filename)
            print('pylint reports {} messages'.format(len(linter_result_array)))
        else:
            linter_result_array = []
        filtered_linter_result = diff.filter_linter_result(linter_result_array)
        print('filtered linter result is {}'.format(len(filtered_linter_result)))
        pretty_print_linter_result(filtered_linter_result)
        for linter_result in filtered_linter_result:
            commit_id = linter_result.resolve_commit_id(repo)

            position = linter_result.resolve_position(repo, commit_id)
            gh.post_review_comment(commit_id, position, linter_result)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('git_directory')
    parser.add_argument('target_branch')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    main(args.git_directory, args.target_branch, args.dry_run)
    # with open(sys.argv[1]) as f:
    #     from_text = f.read()
    # with open(sys.argv[2]) as f:
    #     to_text = f.read()
    # compare_two_texts_and_get_changed_lines(
    #     sys.argv[1], from_text, to_text)
