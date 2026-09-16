#!/usr/bin/env python3
"""Notification router (Spec Sections 92.11, 92.1; D79; AT-106).

Resolves an event type against the closed push list and prints exactly one
decision line. It never sends anything, never invents a destination, and
never picks between two matching routes.

Decisions:
  ROUTE: PUSH <configuration-key> (class=<push_class>, route=<route_id>)
  ROUTE: DIGEST morning-digest (class=<push_class>, route=<route_id>, D79)
  ROUTE: REFUSED (<event_type> is not on the Section 92.11 closed push list)
  ROUTE: AMBIGUOUS (<n> routes for <event_type>: a, b)
  ROUTE: BLOCKED (<reason>)

Exit codes: 0 push or digest, 2 ambiguous or blocked, 3 refused.

Usage: route.py --list
       route.py --event-type <id> [--route <route-id>] [--clock yes|no]
"""
import argparse
import os
import sys

import yaml

ROUTING = os.path.join("notify", "routing")
CHANNELS = os.path.join("notify", "channels")


def load_routes():
    routes = {}
    if not os.path.isdir(ROUTING):
        return routes
    for name in sorted(os.listdir(ROUTING)):
        if not name.endswith(".yaml"):
            continue
        with open(os.path.join(ROUTING, name), "r",
                  encoding="utf-8") as handle:
            doc = yaml.safe_load(handle) or {}
        if isinstance(doc, dict) and doc.get("route_id"):
            routes[str(doc["route_id"])] = doc
    return routes


def channel_key(channel_id):
    path = os.path.join(CHANNELS, "%s.yaml" % channel_id)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as handle:
        doc = yaml.safe_load(handle) or {}
    key = str(doc.get("configuration_key", "")).strip()
    return key or None


def main():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--list", dest="listing", action="store_true")
    parser.add_argument("--event-type", dest="event_type", default=None)
    parser.add_argument("--route", dest="route_id", default=None)
    parser.add_argument("--clock", dest="clock", choices=["yes", "no"],
                        default=None)
    args = parser.parse_args()

    routes = load_routes()
    if not routes:
        print("ROUTE: BLOCKED (no routes declared under %s)" % ROUTING)
        return 2

    if args.listing:
        for route_id in sorted(routes):
            doc = routes[route_id]
            print("%s %s %s" % (route_id, doc.get("event_type"),
                                doc.get("push_class")))
        print("ROUTES: %d" % len(routes))
        return 0

    if not args.event_type:
        print("ROUTE: BLOCKED (no --event-type given)")
        return 2

    matches = [r for r in sorted(routes)
               if str(routes[r].get("event_type")) == args.event_type]
    if args.route_id:
        matches = [r for r in matches if r == args.route_id]
    if not matches:
        print("ROUTE: REFUSED (%s is not on the Section 92.11 closed push "
              "list)" % args.event_type)
        return 3
    if len(matches) > 1:
        print("ROUTE: AMBIGUOUS (%d routes for %s: %s)"
              % (len(matches), args.event_type, ", ".join(matches)))
        return 2

    route_id = matches[0]
    doc = routes[route_id]
    if args.clock is None:
        clock = bool(doc.get("carries_clock"))
    else:
        clock = args.clock == "yes"

    if bool(doc.get("coalesce_into_morning_digest")) and not clock:
        print("ROUTE: DIGEST morning-digest (class=%s, route=%s, D79)"
              % (doc.get("push_class"), route_id))
        return 0

    key = channel_key(str(doc.get("destination_channel")))
    if key is None:
        print("ROUTE: BLOCKED (channel %r declares no configuration_key)"
              % doc.get("destination_channel"))
        return 2
    print("ROUTE: PUSH %s (class=%s, route=%s)"
          % (key, doc.get("push_class"), route_id))
    return 0


if __name__ == "__main__":
    sys.exit(main())
