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
Let's say that you've forked the [JSON class from nlohmann](https://github.com/nlohmann/json).  Perhaps you're making your own contributions to the project, or you want to reduce dependencies on external forks, or you just have a personal vendeta against nlohmann himself.  Look, your multigenerational feud with the Lohmann family is really none of my business.

But now you want to keep your fork up to date with nlohmann's original fork.  Despite the bitterness in your heart, you have to admit he's coming out with some great new features and he's absolutely crushing those bugs.  Maybe you log on to github dot com every few days and make a pull request from nlohmann's fork to your fork.  Unfortunately after a while you start to forget.

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
Let's say that you have a repo for a library called [colormapper](https://github.com/JeffIrwin/colormapper) for mapping scalar floats to RGB triplets.  You also have a couple projects for [Conway's game of life](https://github.com/JeffIrwin/life) and [fitness data heatmapping](https://github.com/JeffIrwin/maph), both of which depend on `colormapper`.  Maybe the `colormapper` library even has CI/CD and testing built into itself, but you also want to test it within the context of the other projects that use it, and take advantage of all the new features and bug fixes.

With `pgh`, you can automate the process of updating submodules within all the parent repos that use them.  Simply define the submodule relations in a JSON file `origins.json` (there are some other submodules [bat](https://github.com/JeffIrwin/bat) and [pnmio](https://github.com/JeffIrwin/pnmio) too):

    [
    	{
    		"folder": "auto-repos/life",
    		"origin": "https://github.com/JeffIrwin/life",
    		"submodules":
    		[
    			"submodules/bat",
    			"submodules/colormapper",
    			"submodules/pnmio"
    		]
    	},
    	{
    		"folder": "auto-repos/maph",
    		"origin": "https://github.com/JeffIrwin/maph",
    		"submodules":
    		[
    			"submodules/bat",
    			"submodules/colormapper"
    		]
    	}
    ]

Note that you don't need to redefine the URL of the submodules, that is already covered in `.gitmodules`.  Just define the filesystem path to everything in the `submodules` array.

Now run:

    python3 pgh.py -s origins.json

