from collections import defaultdict, OrderedDict

import simpletex

class Formatter:
    def __init__(self):
        pass
    def __call__(self, *args, **kwargs) -> str:
        if not args and not kwargs:
            raise TypeError("Can't re-instantiate an instance of {}.".format(self.__class__.__name__))
        else:
            return self.format_text(*args, **kwargs)
    def format_text(self, text) -> str:
        """Should be overridden by subclasses."""
        return text
    def __enter__(self):
        simpletex._CONTEXT.push(Paragraph())
    def __exit__(self, *args):
        formattedText = self(simpletex._CONTEXT.pop())
        simpletex._CONTEXT.write(formattedText)
        

class Text:
    def __init__(self):
        super().__setattr__('_text', defaultdict(lambda: ''))
        super().__setattr__('_order', [])

    def __getattr__(self, attr):
        if attr not in self:
            self._order.append(attr)
        return self._text[attr]

    def __setattr__(self, attr, value):
        if attr not in self:
            self._order.append(attr)
        self._text[attr] = value

    def __contains__(self, item):
        return item in self._order
    
    def __iter__(self):
        return (self._text[line] for line in self._order)
    
    def __repr__(self):
        return "{}{}".format(self.__class__.__name__, self._order)

    def __str__(self):
        """Should be overridden by subclasses."""
        return ''.join(map(str, self))

    def __enter__(self):
        raise TypeError("Can't use {} as a context manager.".format(self.__class__.name))
    def __exit__(self, *args):
        pass


class Paragraph:
    def __init__(self):
        super().__init__()
        self._text = []

    def __iter__(self):
        return iter(self._text)
        
    def write(self, text):
        self._text.append(text)
        
    def __str__(self):
        return '\n'.join(map(str, self))

    def __enter__(self):
        raise TypeError("Can't use {} as a context manager.".format(self.__class__.name))
    def __exit__(self, *args):
        pass
    

# Used in the preamble to organize declarations.
# Each registry is responsible for keeping track of and formatting a type of declaration (imports, font declarations, etc.)
class Registry:
    def __init__(self):
        super().__init__()
        self._entries = OrderedDict()

    def __iter__(self):
        return iter(self._entries)

    def items(self):
        """Returns an iterator over the key-value pairs in the registry."""
        return self._entries.items()
        
    def register(self, key, value=None):
        """Registers an entry under the given key, if not already present."""
        self._entries.setdefault(key, value)

    #Should be overridden in subclasses
    @staticmethod
    def _entry_line(entry, value):
        """Formats a single registration entry as text."""
        return entry

    # Generally should not be overridden
    # Override _entry_line instead
    def __str__(self):
        return '\n'.join(str(self._entry_line(key, value)) for key, value in self.items())

