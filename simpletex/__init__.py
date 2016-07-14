import codecs

from simpletex.core import Text, Paragraph, Registry
from simpletex.registry.core import ImportRegistry, CommandDefinitionRegistry
from simpletex.base import Command


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
        self.contextStack.append(context)

    def pop(self):
        return self.contextStack.pop()

    @property
    def top(self):
        return self.contextStack[-1]

    def write(self, text):
        self.top.write(text)

    def save(self, name):
        with codecs.open(name, "w", "utf-8") as f:
            f.write(str(self.preamble))

    def clear(self):
            super().__setattr__('preamble', _Preamble())
            super().__setattr__('contextStack', [self.preamble])

    def add_registry(self, name, registry):
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
    '\\': Command('textasciitilde'),
    '\n': r'\\',
    '-': r'{-}'
}


def _latex_escape(text):
    return ''.join(_LATEX_ESCAPE_DICT.get(char, char) for char in text)


def write(text):
    """Escapes the given string and writes it to current top-level context."""
    _CONTEXT.write(_latex_escape(str(text)))


def write_break(text):
    """Escapes the given string and writes it to current top-level context,
    adding a trailing LaTeX line break."""
    _CONTEXT.write(_latex_escape(str(text)) + r' \\')


def add_registry(name, registry):
    """Adds a registry under the given name if not already present."""
    _CONTEXT.add_registry(name, registry)


def usepackage(name, *args, **kwargs):
    _CONTEXT.imports.register(name, [args, kwargs])


def alias(name, definition):
    _CONTEXT.commandDefinitions.register(name, definition)
    return Command(name)


def save(filename):
    _CONTEXT.save(filename)


def dump():
    return str(_CONTEXT.preamble)


def clear():
    _CONTEXT.clear()
