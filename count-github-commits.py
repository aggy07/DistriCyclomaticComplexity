#! /usr/bin/env python
import json
import requests


def count_user_commits(user):
    r = requests.get('https://api.github.com/users/%s/repos' % user)
    repos = json.loads(r.content)

    for repo in repos:
        if repo['fork'] is True:
            # skip it
            continue
        n = count_repo_commits(repo['url'] + '/commits')
        repo['num_commits'] = n
        yield repo


def count_repo_commits(commits_url, _acc=0):
    r = requests.get(commits_url)
    commits = json.loads(r.content)
    n = len(commits)
    if n == 0:
        return _acc
    link = r.headers.get('link')
    if link is None:
        return _acc + n
    next_url = find_next(r.headers['link'])
    if next_url is None:
        return _acc + n
    # try to be tail recursive, even when it doesn't matter in CPython
    return count_repo_commits(next_url, _acc + n)


# given a link header from github, find the link for the next url which they use for pagination
def find_next(link):
    for l in link.split(','):
        a, b = l.split(';')
        if b.strip() == 'rel="next"':
            return a.strip()[1:-1]


if __name__ == '__main__':
    import sys
    try:
        user = sys.argv[1]
    except IndexError:
        print ("Usage: %s <username>" % sys.argv[0])
        sys.exit(1)
    total = 0
    for repo in count_user_commits(user):
        print ("Repo `%(name)s` has %(num_commits)d commits, size %(size)d." % repo)
        total += repo['num_commits']
    print ("Total commits: %d" % total)

##
## Testing Code Complexity and Repo stuff
##
##


import numpy as np
from git import Repo
import os
from radon.complexity import cc_rank, cc_visit
import shutil
from itertools import count


repo_loc = './repository'
repo_counter = count()
repo_dir = repo_loc + str(next(repo_counter))

if not os.path.exists(repo_dir):
    os.makedirs(repo_dir)

if not os.listdir(repo_dir):
    print('cloning repository into directory: {0}'.format(repo_dir))
    Repo.clone_from("https://github.com/fogleman/Minecraft", repo_dir)
    print('cloning finished')

repo = Repo(repo_dir)
assert not repo.bare



heads = repo.heads
master = heads.master
tags = repo.tags


fifty_first_commits = list(repo.iter_commits('master', max_count=50))
all_commits = list(repo.iter_commits('master'))
print("First fifty commits = {0}".format(fifty_first_commits))
print("All commits = {0}".format(all_commits))
print("LEN of All commits = {0}".format(len(all_commits)))

first_commit = all_commits[-1]
print("first ever commit = ", first_commit.hexsha)
# repo.commit(first_commit.hexsha)

print("current hexsha = ", repo.head.object.hexsha)

git = repo.git
# git.checkout(all_commits[-1].hexsha)
git.checkout(all_commits[0].hexsha)


################## get all files from repo ####################

from os import walk

# files = []
# for (dirpath, dirnames, filenames) in walk('./repo0'):
#     for filename in filenames:
#         if '.py' in filename:
#             dirpath = dirpath.replace("\\", "/")
#             print(dirpath + '/' + filename)
#             files.append(dirpath + '/' + filename)

import os
import os.path
files = []
path = "/home/arvind/Downloads/github count/1241096-584707d3fca316ac56b00204babe7d1a9bbac594/repository0"
python_files = [p for p in os.listdir(path) if p.endswith('.py')]
print(python_files)
files.append(path + '/' + python_files[0])


print(files)
#print("Files = ", f)

################## calculate cyclomatic complexity ####################


from radon.visitors import ComplexityVisitor
import radon


with open(files[0]) as f:
    data = f.read()
    print(data)
    cc = radon.complexity.cc_visit(data)
    for cc_item in cc:
        print("complexity = ", cc_item.complexity)
    print("Average complexity = "  , np.average(cc_item.complexity))


