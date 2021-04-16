"""Backports of features implemented in versions newer than the youngest one
supported by powpow.

----------------------------
Classes:

    _NOT_FOUND, cached_property

Are redistributed / licensed under the following terms:

    Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010,
    2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021 Python
    Software Foundation; All Rights Reserved

    PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
    --------------------------------------------

    1. This LICENSE AGREEMENT is between the Python Software Foundation
    ("PSF"), and the Individual or Organization ("Licensee") accessing and
    otherwise using this software ("Python") in source or binary form and its
    associated documentation.

    2. Subject to the terms and conditions of this License Agreement, PSF
    hereby grants Licensee a nonexclusive, royalty-free, world-wide license to
    reproduce, analyze, test, perform and/or display publicly, prepare
    derivative works, distribute, and otherwise use Python alone or in any
    derivative version, provided, however, that PSF's License Agreement and
    PSF's notice of copyright, i.e., "Copyright (c) 2001, 2002, 2003, 2004,
    2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016,
    2017, 2018, 2019, 2020, 2021 Python Software Foundation; All Rights
    Reserved" are retained in Python alone or in any derivative version
    prepared by Licensee.

    3. In the event Licensee prepares a derivative work that is based on or
    incorporates Python or any part thereof, and wants to make the derivative
    work available to others as provided herein, then Licensee hereby agrees to
    include in any such work a brief summary of the changes made to Python.

    4. PSF is making Python available to Licensee on an "AS IS" basis.  PSF
    MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR IMPLIED.  BY WAY OF
    EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND DISCLAIMS ANY REPRESENTATION
    OR WARRANTY OF MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR
    THAT THE USE OF PYTHON WILL NOT INFRINGE ANY THIRD PARTY RIGHTS.

    5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON FOR ANY
    INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES OR LOSS AS A RESULT OF
    MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON, OR ANY DERIVATIVE
    THEREOF, EVEN IF ADVISED OF THE POSSIBILITY THEREOF.

    6. This License Agreement will automatically terminate upon a material
    breach of its terms and conditions.

    7. Nothing in this License Agreement shall be deemed to create any
    relationship of agency, partnership, or joint venture between PSF and
    Licensee.  This License Agreement does not grant permission to use PSF
    trademarks or trade name in a trademark sense to endorse or promote
    products or services of Licensee, or any third party.

    8. By copying, installing or otherwise using Python, Licensee agrees to be
    bound by the terms and conditions of this License Agreement.
----------------------------
"""
from threading import RLock

_NOT_FOUND = object()


class cached_property:
    def __init__(self, func):
        self.func = func
        self.attrname = None
        self.__doc__ = func.__doc__
        self.lock = RLock()

    def __set_name__(self, owner, name):
        if self.attrname is None:
            self.attrname = name
        elif name != self.attrname:
            raise TypeError(
                "Cannot assign the same cached_property to two different names "
                f"({self.attrname!r} and {name!r})."
            )

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if self.attrname is None:
            raise TypeError(
                "Cannot use cached_property instance without calling "
                "__set_name__ on it.")
        try:
            cache = instance.__dict__
        # not all objects have __dict__ (e.g. class defines slots)
        except AttributeError:
            msg = (
                f"No '__dict__' attribute on {type(instance).__name__!r} "
                f"instance to cache {self.attrname!r} property."
            )
            raise TypeError(msg) from None
        val = cache.get(self.attrname, _NOT_FOUND)
        if val is _NOT_FOUND:
            with self.lock:
                # check if another thread filled cache while we awaited lock
                val = cache.get(self.attrname, _NOT_FOUND)
                if val is _NOT_FOUND:
                    val = self.func(instance)
                    try:
                        cache[self.attrname] = val
                    except TypeError:
                        msg = (
                            f"The '__dict__' attribute on "
                            f"{type(instance).__name__!r} instance does not "
                            f"support item assignment for caching "
                            f"{self.attrname!r} property."
                        )
                        raise TypeError(msg) from None
        return val
