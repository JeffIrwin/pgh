
# Run with:
#     python pgh.py --help

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
import sys

from datetime import datetime

this = "pgh:  "

def printf(string):
    print(string, flush = True)

def sync_branch(branch, remote):
    printf(this + "branch = " + branch)
    io = os.system("git checkout " + branch)
    #printf("io 1 = " + str(io))
    if (io == 0): io = os.system("git merge " + remote + "/" + branch)
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

    if (args.forks == None):
        return 0

    printf('')
    printf(this + "syncing forks")
    printf(this + datetime.now().isoformat())

    default_branch = "master"

    printf(this + "loading JSON file \"" + args.forks + "\" ...")
    repos = json.load(open(args.forks, 'r'))
    printf(this + "repos =\n" + json.dumps(repos, indent = 4))

    path = pathlib.Path(args.forks).parent.absolute()
    printf(this + "path = " + str(path))

    cwd = os.getcwd()

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
                    if (io == 0): io = os.system("git fetch upstream")

                else:
                    printf(this + "error: no upstream remote found for \"" + str(path / repo["folder"]) + "\"")
                    io = -1

        if (io == 0):
            if "branches" in repo:
                for branch in repo["branches"]:
                    io = sync_branch(branch, "upstream")
                    ntotal += 1
                    if (io == 0):
                        nsuccess += 1
            else:
                io = sync_branch(default_branch, "upstream")
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

    # Return to previous directory
    os.chdir(cwd)

    return nfail

def pull_submodules(args):

    if (args.submodules == None):
        return 0

    printf('')
    printf(this + "pulling submodules")
    printf(this + datetime.now().isoformat())

    default_branch = "master"

    printf(this + "loading JSON file \"" + args.submodules + "\" ...")
    repos = json.load(open(args.submodules, 'r'))
    printf(this + "repos =\n" + json.dumps(repos, indent = 4))

    path = pathlib.Path(args.submodules).parent.absolute()
    printf(this + "path = " + str(path))

    cwd = os.getcwd()

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

        if (io == 0): io = os.system("git fetch origin")

        if (io == 0):
            io = sync_branch(default_branch, "origin")

            # TODO:  handle key error if "submodules" doesn't exist
            for module in repo["submodules"]:
                printf(this + "submodule = " + module)

                # Pull latest master branch of submodule.  TODO:  branch options?
                os.chdir(path / repo["folder"] / module)
                io = os.system("git pull origin master")

                if (io == 0):
                    # Commit submodule update to parent
                    os.chdir(path / repo["folder"])

                    os.system("git add " + str(path / repo["folder"] / module))

                    # Don't check io, "nothing to commit" isn't considered a problem.
                    os.system("git commit -m \"" + this + "automatic update of " + module + "\"")

            # Multiple commits, one push, just to take it easy on the CI/CD
            # system.  Pushing each commit would test them individually,
            # which may be preferable to see more incremental test results
            if (io == 0): io = os.system("git push")

            ntotal += 1
            if (io == 0):
                nsuccess += 1

        if (io != 0):
            nfail += 1
            failures.append(repo["folder"])

        # Restore stashed changes to last branch
        if (stashing): os.system("git stash pop")

        printf('')

    printf(this + "======= pull submodules:  " + str(nsuccess) + " branches succeeded, " + str(nfail) + " failed ======")

    if (nfail != 0):
        printf(this + "failed in folders: " + str(failures))

    # Return to previous directory
    os.chdir(cwd)

    return nfail

def pgh_parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-f", "--forks", type = str,
            help = "JSON file listing the forked repository folders")

    parser.add_argument("-s", "--submodules", type = str,
            help = "JSON file listing parent repos and their submodules to be pulled")

    args = parser.parse_args()

    if (args.forks == None and args.submodules == None):
        parser.print_help()

    return args

def main():
    args = pgh_parse_args()

    io = 0
    io += sync_forks(args)
    io += pull_submodules(args)

    printf(this + "done")
    return io

sys.exit(main())

