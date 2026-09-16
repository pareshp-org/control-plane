"""reconciler.comparators - the Phase-1 declared-versus-actual comparison set (spec 53.1).

Every module in this package registers exactly one comparator with
reconciler.registry.comparator and exposes one function:

    compare(declared, actual, as_of) -> tuple[list[Finding], int]

`declared` is a reconciler.cli.DeclaredState (the fixture's declared/**
tree); `actual` is a reconciler.state.port.GitHubState adapter; `as_of`
is a datetime.date. No comparator may call the wall clock directly -
every date comparison uses `as_of` (spec 0.5 acceptance rule 2).

This package is discovered dynamically by reconciler.cli._load_comparators
via pkgutil.iter_modules - dropping a new comparator module in here is
enough to register it; nothing else needs editing.
"""
