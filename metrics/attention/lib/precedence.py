# metrics/attention/lib/precedence.py
# DR-5 category precedence. MasterSpec v4.0 Section 97.4 line 8973; Section 67.1 line 5573.
# The order is read from calibration.yaml through load_calibration(); it is never written here.
from config import load_calibration, value


def signature(session):
    """Two windows contain the SAME session when their event instants are identical."""
    return tuple(ev[0].isoformat() for ev in session)


def resolve(window_sessions, cal=None):
    """window_sessions: [(category, session)]. Returns (winners, losers), same shape.

    Insertion order of the first-seen signature is preserved, so the result is
    deterministic for a given input file and does not depend on hash ordering.
    """
    cal = cal or load_calibration()
    order = value(cal, "precedence_order")
    rank = {name: i for i, name in enumerate(order)}
    for category, _ in window_sessions:
        if category not in rank:
            raise SystemExit("ATTN ERROR category-not-in-precedence:%s" % category)
    groups = {}
    for category, session in window_sessions:
        groups.setdefault(signature(session), []).append((category, session))
    winners, losers = [], []
    for sig in groups:
        ordered = sorted(groups[sig], key=lambda cs: rank[cs[0]])
        winners.append(ordered[0])
        losers.extend(ordered[1:])
    return winners, losers
