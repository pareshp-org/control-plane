// Self-hosted Renovate configuration for the operations VM.
// Part of the minimum reconstruction set (Section 45.1): a rebuild replays this
// file; it is never re-derived by hand.
// The repository list is supplied by run-renovate.sh from the registry at run
// time (invariant 52). Discovery is off, so no repository the registry does not
// name is ever picked up.
// Auto-merge-on-green is a repository-side policy exception carried by two
// rulesets and a policies.yaml entry (D74, D89). This host configures none of
// it, and the fleet default here is closed (invariant 79, invariant 80).
module.exports = {
  platform: 'github',
  autodiscover: false,
  onboarding: false,
  requireConfig: 'optional',
  dependencyDashboard: true,
  automerge: false,
  ignoreScripts: true,
};
