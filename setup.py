from setuptools import setup

setup(
    name             = "mylang",
    version          = "0.4.0",
    description      = "A custom interpreted language for maths, stats, and EE",
    py_modules       = ["main", "lexer", "parser", "interpreter",
                        "ast_nodes", "stdlib"],
    entry_points     = {
        "console_scripts": ["mylang=main:main"],
    },
    python_requires  = ">=3.10",
)
