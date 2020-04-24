
# TODO:
#
#   - Error handling
#       * merge conflict?
#   - Add an option to clone all repos in an organization
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
    io = os.system("git checkout " + branch)
    #printf("io 1 = " + str(io))
    if (io == 0): io = os.system("git merge upstream/" + branch)
    #printf("io 2 = " + str(io))
    if (io == 0): io = os.system("git push --all")
    #printf("io 3 = " + str(io))
    if (io == 0): io = os.system("git checkout -")  # Go back to the last branch
    #printf("io 4 = " + str(io))
    return io

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

    ntotal = 0
    nfail  = 0
    nsuccess = 0
    failures = []

    for repo in repos:
        printf(this + "folder = " + repo["folder"])

        io = 0
        if (os.path.exists(path / repo["folder"])):
            os.chdir(path / repo["folder"])
        else:
            if ("origin" in repo):
                # If the folder doesn't exist, try cloning it from origin
                origin = repo["origin"]
                printf(this + "cloning from origin: " + origin)

                if (not os.path.exists(path / repo["folder"] / "..")):
                    os.mkdir(path / repo["folder"] / "..")

                os.chdir(path / repo["folder"] / "..")
                io = os.system("git clone --recursive " + origin)
                if (io == 0): os.chdir(path / repo["folder"])

            else:
                printf(this + "error: folder \"" + str(path / repo["folder"]) + "\" does not exist and no origin is listed")
                io = -1

        # Stash any unsaved changes.  It's a bad idea to run this script on
        # folders that you work out of, but we'll try to save just in case.
        stashing = False
        if (io == 0):
            stashing = True
            io = os.system("git stash")

        if (io == 0):
            io = os.system("git fetch upstream")
            if (io != 0):
                if ("upstream" in repo):
                    # If upstream remote doesn't exist, try adding it.
                    upstream = repo["upstream"]
                    printf(this + "adding upstream remote: " + upstream)
                    io = os.system("git remote add upstream " + upstream)
                    io = os.system("git fetch upstream")

                else:
                    printf(this + "error: no upstream remote found for \"" + str(path / repo["folder"]) + "\"")
                    io = -1

        if (io == 0):
            if "branches" in repo:
                for branch in repo["branches"]:
                    io = sync_branch(branch)
                    ntotal += 1
                    if (io == 0):
                        nsuccess += 1
            else:
                io = sync_branch(default_branch)
                ntotal += 1
                if (io == 0):
                    nsuccess += 1

        if (io != 0):
            nfail += 1
            failures.append(repo["folder"])

        # Restore stashed changes to last branch
        if (stashing): os.system("git stash pop")

        printf('')

    printf(this + "============ sync:  " + str(nsuccess) + " branches succeeded, " + str(nfail) + " failed ============")

    if (nfail != 0):
        printf(this + "failed in folders: " + str(failures))
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

