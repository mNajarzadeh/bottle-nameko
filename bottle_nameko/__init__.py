"""
bottle nameko.

"""

__version__ = "0.1.1"
__author__ = 'Mohammad Najarzadeh'
__email__ = 'm.najarzadeh1993@gmail.com'
__credits__ = ''

__all__ = ["Gateway"]


def __getattr__(name):
    if name == "Gateway":
        from .gateway import Gateway

        globals()["Gateway"] = Gateway
        return Gateway

    raise AttributeError(
        f"module {__name__!r} has no attribute {name!r}"
    )