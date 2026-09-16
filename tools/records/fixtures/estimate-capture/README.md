Negative cases proved by tools/records/checks/L4-P5-04.sh, all executed, never mocked:
1. wrong transition            -> ESTIMATE FAIL not-the-capture-point:in_progress   exit 1
2. no --item-class             -> ESTIMATE ERROR missing-item-class                 exit 3
3. exempt class                -> ESTIMATE OK exempt=incident, captured False       exit 0
4. economics.yaml unreachable  -> ESTIMATE ERROR economics-unreachable              exit 3
