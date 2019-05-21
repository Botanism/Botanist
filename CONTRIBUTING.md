# Contributing

Although contributing to the project is allowed and even encouraged it has to follow a few rules in order to actually benefit the project.

- First of each update feature change/addition should be made in its own PR. Having multiple new features in a single PR is discouraged.

- The PR should not enter in conflict with the branch it's compared to. This excludes PR related to changing features which will obviously change the code. The intent is to preserve the global state of the code to allow other developers to keep up to date more easily and have some sort of consistency. For example you shouldn't change the name of global settings located in `settings.py`; unless that is the point of the PR.
- Your code should follow [PEP8](https://www.python.org/dev/peps/pep-0008/) standards. The only allowed exception is the use of tabs instead of spaces. That is if your tabs are **four** spaces wide.
- All extensions should be properly configure to generate nice logs using the `logging` module. However this is easy as you only have to copy/paste the according section of code (see any extension for further information)
- All checks that you wish to include should be put in `checks.py`



This is a *guideline* which means that some exceptions may be made. However it is recommend that you respect it for your contribution to be validated. If you have any other question or think a point is unclear or too limiting feel free to contact an @admin

