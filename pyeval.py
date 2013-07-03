#! /usr/bin/env python

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

import __builtin__
import sys
import pprint
from types import ModuleType
import os

# NOTE: I do not know how well this will work in practice:
# If sys.stdout.encoding is not set (because stdout is not a terminal),
# we use LC_CTYPE *anyway*.
try:
    Encoding = sys.stdout.encoding or os.environ.get('LC_CTYPE', 'UTF-8').split( '.', 1 )[-1]

except ValueError:
    raise SystemExit(
        'Could not determine output encoding.  Set the LC_CTYPE environment variable to a desired python encoding.'
        )


def main(args = sys.argv[1:]):
    expr, strs = args[0], args[1:]
    display(pyeval(expr, *strs))


def pyeval(expr, *args):

    scope = MagicScope(
        args = args,
        help = HelpWrapper(),
        srcpath = get_source_path,
        pf = pprint.pformat)

    # Some more shortcuts:
    for (i, arg) in enumerate(args):
        scope['a%d' % i] = arg

    return eval(expr, {}, scope)


def display(obj):
    if obj is None:
        return

    it = [obj]
    if type(obj) not in (str, unicode):
        try:
            it = iter(obj)
        except TypeError:
            pass

    for elem in it:
        print unicode(elem).encode(Encoding)



def import_last(modpath):
    mod = __import__(modpath)
    for name in modpath.split('.')[1:]:
        mod = getattr(mod, name)
    return mod



class AutoImporter (object):
    def __init__(self, mod, parent=None):
        assert type(mod) is ModuleType, `mod`

        self._ai_mod = mod
        self._ai_parent = parent

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
        return sys.stdin.readlines()

    def magic_lines(self):
        for l in self['rlines']:
            yield l.strip()


class HelpWrapper (object):
    def __repr__(self):
        return repr(help)

    def __call__(self, obj=None):
        if isinstance(obj, AutoImporter):
            obj = obj._ai_mod
        help(obj)


def get_source_path(mod):
    if isinstance(mod, AutoImporter):
        mod = mod._ai_mod
    path = mod.__file__
    if path.endswith('.pyc'):
        path = path[:-1]
    assert path.endswith('.py'), `path`
    return path



if __name__ == '__main__':
    main()
