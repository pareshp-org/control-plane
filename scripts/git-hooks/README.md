# scripts/git-hooks/

Git hooks for local enforcement. Install with:
```bash
make setup
```

## Hooks
- `pre-commit` — checks canary sentinel, scans for PAT leaks (FD-083/FD-086)
- `commit-msg` — warns if commit message doesn't follow conventional format
