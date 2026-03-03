# Python 3.14 compatibility patch for SQLAlchemy
# Place this in site-packages or use PYTHONPATH

import sys
import importlib

original_import = __builtins__.__import__

def patched_import(name, *args, **kwargs):
    if name == 'sqlalchemy.sql.elements' or name.startswith('sqlalchemy.sql'):
        # Pre-patch the typing module issues
        try:
            import typing
            # Store original TypingOnly if it exists
            if hasattr(typing, 'TypingOnly'):
                original_typing_only = typing.TypingOnly
                
                # Create a minimal TypingOnly that bypasses the assertion
                class CompatTypingOnly(type):
                    def __new__(cls, name, bases, namespace):
                        # Copy namespace but remove attrs that cause issues
                        clean_ns = dict(namespace)
                        for attr in ['__firstlineno__', '__static_attributes__']:
                            clean_ns.pop(attr, None)
                        return super().__new__(cls, name, bases, clean_ns)
                
                # Try to patch
                try:
                    typing.TypingOnly = CompatTypingOnly
                except:
                    pass
        except:
            pass
    
    return original_import(name, *args, **kwargs)

__builtins__.__import__ = patched_import
