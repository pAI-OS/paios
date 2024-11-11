from typing import Callable, TypeVar

T = TypeVar("T")

class TextSplitterAdapter:

    def __init__(self, obj: T, **adapted_methods: Callable):
        self.obj = obj
        self.__dict__.update(adapted_methods)

    def __getattr__(self, attr):
        """All non-adapted calls are passed to the object."""
        return getattr(self.obj, attr)

    def original_dict(self):
        """Print original object dict."""
        return self.obj.__dict__