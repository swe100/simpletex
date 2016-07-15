"""
This module provides functions to conveniently perform common operations.

..  :copyright: (c) 2016 by Samuel Li.
    :license: GNU GPLv3, see License for more details.
"""

import codecs

from simpletex.core import Text, Paragraph
from simpletex.registry.core import ImportRegistry, CommandDefinitionRegistry
from simpletex.base import Command

__all__ = ('latex_escape', 'write', 'write_break', 'add_registry',
           'usepackage', 'alias', 'save', 'dump', 'clear')


class _Preamble(Text):
    def __init__(self):
        super().__init__()
        self.classDeclaration = ''
        self.imports = ImportRegistry()
        self.commandDefinitions = CommandDefinitionRegistry()
        self.body = Paragraph()

    def write(self, text):
        # Move body last
        self.body.write(text)

    def __str__(self):
        self._order.remove('body')
        self._order.append('body')
        # Prevent race conditions
        list(map(str, self))
        return '\n\n'.join(str(item) for item in self if str(item))


class _GlobalContextManager(object):
    def __init__(self):
        super().__setattr__('preamble', _Preamble())
        super().__setattr__('contextStack', [self.preamble])

    def push(self, context):
        """Add the given context to the context stack."""
        self.contextStack.append(context)

    def pop(self):
        """Remove and returns the context at the top of the context stack."""
        return self.contextStack.pop()

    @property
    def top(self):
        """Return the context at the top of the current context stack."""
        return self.contextStack[-1]

    def write(self, text):
        """Write the given text to the top-level context."""
        self.top.write(text)

    def save(self, name):
        """Save the entire document under the given filename."""
        with codecs.open(name, "w", "utf-8") as f:
            f.write(str(self.preamble))

    def clear(self):
        """Clear all text and resets the context stack."""
        super().__setattr__('preamble', _Preamble())
        super().__setattr__('contextStack', [self.preamble])

    def add_registry(self, name, registry):
        """Add a new registry under the given name, if not already present."""
        if name not in self:
            setattr(self, name, registry)

    def __getattr__(self, name):
        return getattr(self.preamble, name)

    def __setattr__(self, name, value):
        setattr(self.preamble, name, value)

    def __contains__(self, name):
        return name in self.preamble


_CONTEXT = _GlobalContextManager()

_LATEX_ESCAPE_DICT = {
    '$': r'\$',
    '#': r'\#',
    '&': r'\&',
    '%': r'\%',
    '_': r'\_',
    '~': Command('textasciitilde'),
    '^': Command('^'),
    '{': r'\{',
    '}': r'\}',
    '\\': Command('textbackslash'),
    '\n': r'\\',
    '-': r'{-}'
}


def latex_escape(text) -> str:
    """Escape any special LaTeX characters."""
    return ''.join(str(_LATEX_ESCAPE_DICT.get(char, char))
                   for char in str(text))


def write(text):
    """Write the given text to the current top-level context."""
    _CONTEXT.write(text)


def write_break(text):
    r"""
    Write the given string, adding a LaTeX line break.

    The given text converted to a string, and a trailing
    LaTeX line break (``\\``) is appended.
    It is then written to the current top-level context.
    """
    _CONTEXT.write(str(text) + r' \\')


def add_registry(name: str, registry):
    """Add a registry under the given name if not already present."""
    _CONTEXT.add_registry(name, registry)


def usepackage(name: str, *args, **kwargs):
    """
    Add a new package import to the import registry.

    name : str
        The name of the package to import.
        Must be unique.
        If called multiple times with the same package name,
        all calls except the first are ignored.
    args : list of str
        Package import options.
    kwargs : dict of str to str
        Package import keyword options.
    """
    _CONTEXT.imports.register(name, [args, kwargs])


def alias(name: str, definition):
    r"""
    Add a new command alias to the command definition registry.

    Equivalent to the ``\newcommand`` LaTeX macro.
    Returns the new command alias, formatted as a LaTeX command.

    name : str
        The name of the new command.
        Do not include the leading backslash.
    definition : str-like object
        The definition of the new command.
    """
    _CONTEXT.commandDefinitions.register(name, definition)
    return Command(name)


def save(filename: str):
    """
    Save the entire document (including preamble) to the given file.

    filename : str
        The name of the file to save to.
        .. warning:
           Will overwrite existing files under the same name.
    """
    _CONTEXT.save(filename)


def dump() -> str:
    """Return the entire document (including preamble) as a string."""
    return str(_CONTEXT.preamble)


def clear():
    """Clear everything from the entire document."""
    _CONTEXT.clear()
