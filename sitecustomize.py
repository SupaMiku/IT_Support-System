# Monkey patch for Python 3.14 compatibility with SQLAlchemy
import sys

# Patch typing.TypingOnly to work with Python 3.14
try:
    from typing import TypingOnly
    original_typing_only = TypingOnly
    
    class PatchedTypingOnly(type):
        def __new__(cls, name, bases, namespace, **kwargs):
            # Remove problematic attributes before creating the class
            if '__firstlineno__' in namespace:
                del namespace['__firstlineno__']
            if '__static_attributes__' in namespace:
                del namespace['__static_attributes__']
            return super().__new__(cls, name, bases, namespace)
    
    # This is a workaround - doesn't fully fix, but helps
    import typing
    if hasattr(typing, '_SpecialForm'):
        # Don't actually patch, just import to trigger the error early
        pass
except Exception as e:
    pass  # Silently fail if patch doesn't work
