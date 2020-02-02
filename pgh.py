
# TODO:
#
#   - Error handling
#       * at least "fatal: 'upstream' does not appear to be a git repository"
#       * merge conflict?
#   - Success/fail count at end of log
#   - Add JSON entry for upstream URL, optionally set upstream first time
#       * 'git remote add upstream https://github.com/ORG/REPO'
#       * could even clone optionally.  save these in a separate all.json file
#         or find a way to clone all repos in an org.
#   - Readme
#

import argparse
import json
import os
import pathlib

from datetime import datetime

this = "pgh:  "

def printf(string):
    print(string, flush = True)

def sync_branch(branch):
    printf(this + "branch = " + branch)
    os.system("git checkout " + branch)
    os.system("git merge upstream/" + branch)
    os.system("git push --all")
    os.system("git checkout -")  # Go back to the last branch

def sync_forks(args):

    # Get updates from upstream forks and save them to your personal backup
    # forks.  See:
    #
    #   https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/syncing-a-fork
    #

    printf('')
    printf(this + "starting")
    printf(this + datetime.now().isoformat())

    default_branch = "master"

    printf(this + "loading JSON file \"" + args.forks + "\" ...")
    repos = json.load(open(args.forks, 'r'))
    printf(this + "repos =\n" + json.dumps(repos, indent = 4))

    path = pathlib.Path(args.forks).parent.absolute()
    printf(this + "path = " + str(path))

    for repo in repos:
        printf(this + "folder = " + repo["folder"])
        os.chdir(path / repo["folder"])

        # Stash any unsaved changes.  It's a bad idea to run this script on
        # folders that you work out of, but we'll try to save just in case.
        os.system("git stash")

        os.system("git fetch upstream")

        if "branches" in repo:
            for branch in repo["branches"]:
                sync_branch(branch)
        else:
            sync_branch(default_branch)

        # Restore stashed changes to last branch
        os.system("git stash pop")

        printf('')

    printf(this + "done")

def pgh_parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("forks", type = str,
            help = "JSON file listing the forked repository folders")
    return parser.parse_args()

def main():
    args = pgh_parse_args()
    sync_forks(args)

main()

