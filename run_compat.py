"""
Workaround for Python 3.14 SQLAlchemy compatibility issues
"""
import sys

# Add a compatibility layer before importing Flask
sys.dont_write_bytecode = False

# Try to run the app with PYTHONWARNINGS suppressed
import warnings
warnings.filterwarnings("ignore")

# Now we can try importing
try:
    # First, try to monkeypatch typing issues
    import typing
    import sys
    
    # For Python 3.14+, patch Generic to handle additional attributes
    original_generic_init = typing.Generic.__init_subclass__ if hasattr(typing.Generic, '__init_subclass__') else None
    
    def patched_init_subclass(cls, *args, **kwargs):
        # Remove problematic attributes that Python 3.14+ sets
        for attr in ['__firstlineno__', '__static_attributes__']:
            if hasattr(cls, attr) and attr not in ['__module__', '__qualname__']:
                try:
                    delattr(cls, attr)
                except:
                    pass
        # Don't call original - let normal class init proceed
    
    if hasattr(typing, '_SpecialForm'):
        # Patch at module level
        try:
            from sqlalchemy.util import langhelpers
            original_init_subclass = langhelpers.langhelpers.__init_subclass__
            
            def patched_langhelpers_init_subclass(cls, *args, **kwargs):
                # Skip the assertion for TypingOnly classes
                if hasattr(cls, '__mro__'):
                    bases = cls.__bases__
                    for base in bases:
                        if hasattr(base, '__name__') and base.__name__ == 'TypingOnly':
                            # Skip the assertion - just pass
                            return
                if callable(original_init_subclass):
                    original_init_subclass(cls, *args, **kwargs)
            
            langhelpers.__init_subclass__ = patched_langhelpers_init_subclass
        except:
            pass
    
except Exception as e:
    print(f"Compatibili patch partially applied: {e}")

# Now import and run the app
if __name__ == '__main__':
    from main import create_app
    
    app = create_app()
    app.run(debug=True, port=5000, host='127.0.0.1')
