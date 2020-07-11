# pgh
Python git helper, for common tasks that can be automated

## Prerequisites
1.  [git](https://git-scm.com/downloads)
2.  [Python 3](https://www.python.org/downloads/)

## Download
    git clone --recursive https://github.com/JeffIrwin/pgh
    cd pgh

## Usage

### Keeping forks up to date
Let's say that you've forked the JSON class from nlohmann.  Perhaps you're making your own contributions to the project, or you want to reduce dependencies on external forks, or you just have a personal vendeta against nlohmann himself.

Now you want to keep your fork up to date with nlohmann's original fork.  Maybe you log on to github dot com every few days and make a pull request from nlohmann's fork to your fork.  But after a while you start to forget.

With `pgh`, you can automate updating your fork from its upstream fork.  Simply define the relation of your `json` fork to nlohmann's upstream in a JSON file `forks.json`, along with some other repos like `pugixml`:

    [
        {
        	"folder": "auto-repos/json/",
        	"origin": "https://github.com/JeffIrwin/json",
        	"upstream": "https://github.com/nlohmann/json",
        	"branches": ["develop", "master"]
        },
        {
        	"folder": "auto-repos/pugixml/",
        	"origin": "https://github.com/JeffIrwin/pugixml",
        	"upstream": "https://github.com/zeux/pugixml"
        }
    ]

The `folder` value sets a workspace directory for `pgh` to pull and push updates from/to each fork.  By default, only the `master` branch is synced, but you can define an array of other `branches` to also sync.

Now run:

    python3 pgh.py -f forks.json
    
You can setup a Windows Task Scheduler or cron task to sync everything nightly or once a week.

### Keeping submodule dependencies up to date
