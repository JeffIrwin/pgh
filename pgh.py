
# TODO:
#
#   - error handling
#       * at least "fatal: 'upstream' does not appear to be a git repository"
#       * merge conflict?
#   - take forks.json filename as cmd arg, operate on folders relative to forks.json
#   - success/fail count at end of log
#   - add JSON entry for upstream URL, optionally set upstream first time
#       * could even clone optionally
#   - add Windows Task Scheduler item
#

import json
import os

this = "pgh:  "

def sync_branch(branch):
    print(this + "branch = " + branch, flush = True)
    os.system("git checkout " + branch)
    os.system("git merge upstream/" + branch)
    os.system("git push --all")
    os.system("git checkout -")  # Go back to the last branch

def sync_forks():

    # See:
    #
    #   https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/syncing-a-fork
    #

    print()
    print(this + "starting")

    default = "master"

    rfile = "forks.json"
    print(this + "loading JSON file \"" + rfile + "\" ...")
    repos = json.load(open(rfile, 'r'))
    print(this + "repos =\n" + json.dumps(repos, indent = 4))

    for repo in repos:
        print(this + "folder = " + repo["folder"])
        os.chdir(repo["folder"])

        # Stash any unsaved changes
        os.system("git stash")

        os.system("git fetch upstream")

        if "branches" in repo:
            for branch in repo["branches"]:
                sync_branch(branch)
        else:
            sync_branch(default)

        # Restore stashed changes to last branch
        os.system("git stash pop")

        print()

    print(this + "done")

def main():
    sync_forks()

main()

