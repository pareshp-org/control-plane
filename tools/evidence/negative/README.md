# Lane 2 negative corpus — location forwarder

protocol/09-fixtures.md section 2 assigns Lane 2 the negative-fixture root
`tools/evidence/negative/NT-<nn>/`. The fixtures themselves live at:

    tools/evidence/tests/negative/NT-<nn>/
    tools/evidence/tests/negative/GATE-L2-<nnn>/

One copy only. There is no second copy under this directory and none is to be
created: a duplicated fixture is a fixture that can drift, and a drifted
negative is a gate that stops discriminating without anyone editing the gate.

Every gate declaration under tools/evidence/gates/ names its fixture by the
real path above. The declaration is the index; this file is a signpost.
