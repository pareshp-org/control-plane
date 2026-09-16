"""validators.drift — the independent second verifier (spec 53.1).

Package-level note, not a module to import logic from: every assertion
module here (``assert_*.py``) registers itself into ``verifier.ASSERTIONS``
as an import-time side effect, discovered by ``verifier.py``'s own
``_discover_assertion_modules()``.
"""
