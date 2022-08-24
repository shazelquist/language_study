#!/usr/bin/python3
#!C:/Python_X64/python
# -*- coding = utf-8 -*-
"""
Provides functionality for quickly developing python tests & operations by methods

@add_func  # add method to list of options
@param_convert  # convert parameters in the form typename:value

test with $./suite.py echo parameters...
"""
# Shane_Hazelquist #Date: Saturday, 8/13/2022  #Time: 0:6.46
# Imports:
from sys import argv
from json import loads
from inspect import signature

# Directive:
# Generate a simple suite wrapper for python projects
# TODO:
# -keyword arguments with type conversions
# -generic functions like help worker
# -types translator pass
# -check requirements for argv escapes with \"
# -auto type method

__suite_methods__ = {}
__suite_conversions__ = []
__types__ = {
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
    "json": loads,
    "strbool": lambda x: not (x.lower() == "false" or x.lower() == "f"),
}


def add_func(func):
    """
    suite(func)

    Adds function to the list of options for cmdline suite
    Can be invoked manually or through decorators

    Examples:
        def foo(param):
            pass

        add_func(foo)

        @add_func
        def bar(param):
            pass
    """
    __suite_methods__[func.__name__] = func

    def wrapped(*args, **kwargs):
        func(*args, **kwargs)

    return wrapped


def add_type(name, func):
    """
    add_type(name, func)

    Add/Update convertable type
    """
    __types__.update({name: func})


def param_convert(func):
    """
    param_convert(func)

    Adds function to the list that permits argument conversion

    Example:
        @add_func
        @param_convert
        def bar(param):
            pass
    """
    __suite_conversions__.append(func.__name__)
    return func


@add_func
@param_convert
def echo(*args, **kwargs):
    """
    echo(*args,**kwargs)

    print given arguments

    This is a good example for testing inputs
    """
    print("args: {}\nkwargs: {}".format(args, kwargs))


@add_func
def suite_methods():
    print("Avaliable methods:")
    for k in __suite_methods__:
        print("\t{}{}".format(k, signature(__suite_methods__[k])), end="\n")


def run_suite():
    """
    run_suite()

    runs the suite given argv values

    if param_convert enabled
    arguments follow: "typename:value" format.
    """
    i = 0
    pargv = argv[1:]
    if not pargv:  # not pargv
        suite_methods()
    while i < len(pargv):
        if pargv[i] in __suite_methods__.keys():
            lim = i + 1
            kwarg = {}
            if i < len(pargv) - 1:
                while (
                    i < len(pargv) - 1
                    and lim < len(pargv)
                    and pargv[lim] not in __suite_methods__.keys()
                ):
                    if pargv[i] in __suite_conversions__:
                        if (
                            "=" in pargv[lim]
                        ):  # only works for str values, no conversion can take place currently
                            print("kv update canidate:", pargv[lim])
                            sep = pargv[lim].index("=")
                            k, v = pargv[lim][:sep], pargv[lim][sep + 1 :]
                            # kwarg.update({t: v})
                            # del pargv[lim]
                            # lim-=1
                            pargv[lim] = {k: v}
                        if ":" in pargv[lim]:
                            sep = pargv[lim].index(":")
                            t, v = pargv[lim][:sep], pargv[lim][sep + 1 :]
                            if t in __types__:
                                pargv[lim] = __types__[t](v)
                            else:
                                print("could not find type", t)
                    lim += 1

            __suite_methods__[pargv[i]](*pargv[i + 1 : lim], **kwarg)
        else:
            print('Could not find option "{}"'.format(pargv[i]))
            lim = i + 1
        i = lim


def main():
    print("main for suite.py")
    print(__suite_methods__)
    print(__suite_conversions__)
    run_suite()


if __name__ == "__main__":
    main()
