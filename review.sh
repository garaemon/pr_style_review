#!/bin/bash
# based on https://qiita.com/azu/items/c2305f3dded3fda968e0

# Test if pull request
if [ "$TRAVIS_PULL_REQUEST" = "false" ] || [ -z "$TRAVIS_PULL_REQUEST" ]; then
  echo 'not pull request.'
  exit 0
fi

# Fetch other branch
# To avoid ambiguous argument
# http://stackoverflow.com/questions/37303969/git-fatal-ambiguous-argument-head-unknown-revision-or-path-not-in-the-workin
if [ "$TRAVIS" == "true" ]; then
  #resolving `detached HEAD` by attaching HEAD to the `TRAVIS_FROM_BRANCH` branch
  TRAVIS_FROM_BRANCH="travis_from_branch"
  git branch $TRAVIS_FROM_BRANCH
  git checkout $TRAVIS_FROM_BRANCH

  #fetching `TRAVIS_BRANCH` branch
  git fetch origin $TRAVIS_BRANCH
  git checkout -qf FETCH_HEAD
  git branch $TRAVIS_BRANCH
  git checkout $TRAVIS_BRANCH

  #switch to `TRAVIS_FROM_BRANCH`
  git checkout $TRAVIS_FROM_BRANCH
fi

# Diff Target Branch
# diff HEAD...target
# http://stackoverflow.com/questions/3161204/find-the-parent-branch-of-a-git-branch
# http://qiita.com/upinetree/items/0b74b08b64442f0a89b9
# declare diffBranchName=$(git show-branch | grep '*' | grep -v "$(git rev-parse --abbrev-ref HEAD)" | head -1 | awk -F'[]~^[]' '{print $2}')
declare diffBranchName=origin/master

# filter files and lint
echo "${diffBranchName}...HEAD"
git diff --name-only --diff-filter=ACMR $diffBranchName \
| grep -a '.*.py$' \
| xargs ./bin/pylint_checkstyle.py \
| checkstyle_filter-git diff ${diffBranchName} \
| saddler report \
    --require saddler/reporter/github \
    --reporter Saddler::Reporter::Github::PullRequestReviewComment

git diff --name-only --diff-filter=ACMR $diffBranchName \
| grep -a '.*.yml$' -o '.*.yaml$' \
| xargs ./bin/yamllint_checkstyle.py \
| checkstyle_filter-git diff ${diffBranchName} \
| saddler report \
    --require saddler/reporter/github \
    --reporter Saddler::Reporter::Github::PullRequestReviewComment
