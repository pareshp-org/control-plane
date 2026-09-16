#!/usr/bin/env bash
# infra/layer-b/provision-encrypted-volume.sh
# Idempotent. Run from the repository root; acts on layerb-host over SSH.
# Creates nothing if the mapper is already open and mounted.
set -euo pipefail
DECL="infra/layer-b/encrypted-volume.yaml"
DEV=$(yq -r '.volume.device' "$DECL")
MAP=$(yq -r '.volume.mapper_name' "$DECL")
MNT=$(yq -r '.volume.mount_point' "$DECL")
OPTS=$(yq -r '.volume.mount_options' "$DECL")
CIPHER=$(yq -r '.volume.cipher' "$DECL")

if ! ssh -o BatchMode=yes -o ConnectTimeout=5 layerb-host true 2>/dev/null; then
  echo "PROVISION_INDETERMINATE layerb-host unreachable"; exit 2
fi

ssh layerb-host "set -euo pipefail
if mountpoint -q '$MNT'; then echo 'ALREADY_MOUNTED'; exit 0; fi
if ! sudo cryptsetup isLuks '$DEV' 2>/dev/null; then
  # The passphrase is supplied interactively by the Founder. It is never
  # stored on the host and never appears in this repository.
  # Guard checks the block device for an existing LUKS header, not the
  # device-mapper path (which disappears after reboot even when the header
  # is intact). DF-0696: the old [ ! -e /dev/mapper/$MAP ] guard was true
  # after every reboot, causing luksFormat to reformat and destroy data.
  # The cipher is read locally from the declaration (infra/layer-b/encrypted-volume.yaml)
  # and interpolated here as a literal - the remote host has no copy of this
  # repository to read it from, so it is never decorative.
  sudo cryptsetup luksFormat --type luks2 --cipher '$CIPHER' --batch-mode '$DEV'
fi
if [ ! -e /dev/mapper/$MAP ]; then
  sudo cryptsetup open '$DEV' '$MAP'
fi
if ! sudo blkid /dev/mapper/$MAP >/dev/null 2>&1; then sudo mkfs.ext4 /dev/mapper/$MAP; fi
sudo mkdir -p '$MNT'
sudo mount -o '$OPTS' /dev/mapper/$MAP '$MNT'
sudo mkdir -p '$MNT/postgres' '$MNT/documents' '$MNT/grafana'
sudo chmod 700 '$MNT' '$MNT/postgres' '$MNT/documents' '$MNT/grafana'
echo 'PROVISIONED'"
