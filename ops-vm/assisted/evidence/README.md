# Evidence template — `ops-vm/assisted/vm-buildout-request.md`

Copy this into `vm-buildout.md` in this directory once a human has executed
the checklist in `../vm-buildout-request.md`. Never commit a credential,
access key, console password, or payment-instrument value.

```markdown
# VM buildout evidence

executed_by: <GitHub login of the human who ran this>
executed_at: <date>

1. cloud_console_access:
   account_id: <account id, not credential>
2. payment_method_on_file: <yes/no>
3. vm_provisioned:
   instance_id: <instance id>
   region: <region>
4. private_network_path:
   network_id: <network/VPC id>
   vpn_or_mesh_enrolment: <method>
5. ssh_shell_gate:
   check_output: |
     <verbatim stdout of infra/network/check-shell-gate.sh over the new host>
   result: <PASS/FAIL>
6. object_locked_backup_bucket:
   bucket_name: <name>
   credential_domain: <how it differs from the VM's own account/role>
   lock_mode: <governance/compliance>
   retention_period: <duration>
```

A checklist item left blank means that step has not happened; do not fill a
placeholder value in to make the template look complete.
