# lib-maxiv-mainiac

## Summary

Base class with methods supporting MaxIV command-line programs.

The software development group needs to ensure that command line programs have consistent arguments and logging.
This reduces development time to create a familiar argument pattern and logging for users.
This library provides a base class to implement standard command arguments and log location and format.

This is a Python library with API to assist command line main programs.

## Usage
In your python main program, inherit from Mainiac and provide four required methods.  
Please see the tests for more working examples.


```python
from dls_mainiac_lib.mainiac import Mainiac
...
class MyApp(Mainiac):
    def __init__(self):
        super().__init__("my_app")
...
    # ----------------------------------------------------------
    def run(self):
        """
        The method called by Mainiac to perform the business logic of the app.
        To access command line args, use self._args.
        """
        do_some_good_stuff(self._args.my_positional, self._args.my_keyword)

    # ----------------------------------------------------------
    def version(self):
        """
        Method called from Mainiac after command line parsing.
        """
        return "x.y.z"

    # ----------------------------------------------------------
    def about(self):
        """
        Method called from Mainiac after command line parsing.
        """
        return {
            "url": "/some/good/url",
            "description": "A good description"
        }

    # ----------------------------------------------------------
    def build_parser(self, positionals=[]):
        """
        Method called from Mainiac before command line parsing.
        """

        # Make a parser.
        parser = argparse.ArgumentParser()

        # Add keyword arguments.
        parser.add_argument("--my_keyword")

        # Add positional arguments.
        parser.add_argument(type=str, dest="my_positional")

        return parser
```

## FAQ

____________________________________________________________________________
##### What advantages does mainiac offer?

1. Logging to rotating log files.
1. Log formatting.
1. Common command line arguments like --verbose, --version and --about.
1. Easy to layer onto existing command line programs.

____________________________________________________________________________
##### Is it possible to use a default subcommand?

Yes.  Your build_parser() method should return a dict describing the default subcommand.

```python

return {
    "parser": parser,
    "subcommand_dest": "my_subcommand_dest",
    "default_subcommand": "my_default_subcommand"
}
```

In this case, a trial parse is done with the original command line args.
If a failure seems to indicate that none of the known subcommands was given, 
then the default subcommand is inserted at the beginning of the args and the parse is tried again.

Caveats of the default subcommand feature.
1. There must be one and only one subcommand in the arguments added to the argparser.
1. The subcommand must be the first one in the command line arglist.
1. If the user mis-types the subcommmand, then the error the user sees might be hard to understand.

____________________________________________________________________________
##### How do I convert my program to use the mainiac?

