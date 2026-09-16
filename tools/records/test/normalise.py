import sys, yaml, json
d = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
print(json.dumps(d, sort_keys=True, separators=(",", ":"), default=str))
