CopyrightInfo = '''
Copyright 2010 Nathan Wilcox

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

Usage = """
FIXME not yet written
"""


import __builtin__
import sys
import pprint
from types import ModuleType



def main(args = sys.argv[1:]):
    expr, strs = args[0], args[1:]
    display(pyeval(expr, *strs))


def pyeval(expr, *args):
    return eval(expr, {}, makeStandardMagicScope(args))


def display(obj):
    if obj is not None:
        pprint.pprint(obj)


def import_last(modpath):
    mod = __import__(modpath)
    for name in modpath.split('.')[1:]:
        mod = getattr(mod, name)
    return mod


def makeStandardMagicScope(args):

    scope = MagicScope(
        args = args,
        help = HelpBrowser(),
        pf = pprint.pformat)

    # Some more shortcuts:
    for (i, arg) in enumerate(args):
        scope['a%d' % i] = arg

    return scope




class MagicScope (dict):
    def __init__(self, **kw):
        dict.__init__(self, vars(__builtin__))
        self.update(kw)

    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            try:
                method = getattr(self, 'magic_' + key)
            except AttributeError:
                return AutoImporter(import_last(key))

            return method()

    def magic_ri(self):
        self['ri'] = ri = sys.stdin.read()
        return ri

    def magic_i(self):
        return self['ri'].strip()

    def magic_rlines(self):
        return self['ri'].split('\n')

    def magic_lines(self):
        return [ l.strip() for l in self['rlines'] ]



class AutoImporter (object):
    def __init__(self, mod, parent=None):
        assert type(mod) is ModuleType, `mod`

        self._ai_mod = mod
        self._ai_parent = parent

        try:
            path = mod.__file__
        except AttributeError:
            self._ai_path = None
        else:
            if path.endswith('.pyc'):
                path = path[:-1]

            self._ai_path = path


    @property
    def _ai_fullname(self):
        return self._ai_mod.__name__

    def __repr__(self):
        return '<%s@%016x %r>' % (self.__class__.__name__, id(self), self._ai_mod)

    def __getattr__(self, name):
        try:
            x = getattr(self._ai_mod, name)
        except AttributeError:
            x = import_last(self._ai_fullname + '.' + name)

        if type(x) is ModuleType:
            return AutoImporter(x, self)
        else:
            return x



class HelpBrowser (object):
    def __init__(self, delegate=help):
        """The constructor allows dependency injection for unittests."""
        self._delegate = delegate

    def __repr__(self):
        return Usage

    def __call__(self, obj=None):
        if obj is None:
            return self

        if isinstance(obj, AutoImporter):
            obj = obj._ai_mod

        self._delegate(obj)


