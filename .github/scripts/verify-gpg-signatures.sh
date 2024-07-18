#!/bin/bash
set -euo pipefail

# Directory containing trusted maintainer public keys
GPG_KEYS_DIR=".github/gpg-keys"

# Use the GPG_KEYSERVER environment variable, defaulting to keyserver.ubuntu.com if not set
GPG_KEYSERVER="${GPG_KEYSERVER:-keyserver.ubuntu.com}"

# Import all maintainer public keys
for key in "$GPG_KEYS_DIR"/*; do
  gpg --import "$key"
done

# Function to check if a key is signed by a key in GPG_KEYS_DIR
is_signed_by_trusted_key() {
  local key_id="$1"
  local trusted_fingerprints=$(gpg --with-colons --fingerprint | awk -F: '/^fpr:/ {print $10}')
  
  # Fetch the key from keyserver
  gpg --keyserver "$GPG_KEYSERVER" --recv-keys "$key_id"
  
  for trusted_fpr in $trusted_fingerprints; do
    if gpg --list-sigs --with-colons "$key_id" | grep -q "sig:::::::::$trusted_fpr:"; then
      return 0
    fi
  done
  return 1
}

# Verify each commit
for commit in $(git rev-list --no-merges HEAD); do
  echo "Verifying commit: $commit"
  
  # Get the author of the commit
  commit_author=$(git log -1 --format='%an <%ae>' $commit)
  
  # Verify the commit signature
  if ! git verify-commit "$commit" 2>/dev/null; then
    echo "::error file=.github/scripts/verify-signatures.sh::Invalid signature for commit $commit by $commit_author"
    exit 1
  fi
  
  # Check if it's a GPG signature (not SSH)
  if ! git log -1 --format='%G?' $commit | grep -q 'G'; then
    echo "::error file=.github/scripts/verify-signatures.sh::Commit $commit by $commit_author is not signed with GPG"
    exit 1
  fi
  
  # Get the signing key ID
  signing_key=$(git log --format='%GK' -n 1 "$commit")
  
  # Check if the signing key is signed by a trusted key
  if ! is_signed_by_trusted_key "$signing_key"; then
    echo "::error file=.github/scripts/verify-signatures.sh::Commit $commit by $commit_author is signed by an untrusted key: $signing_key"
    exit 1
  fi
  
  echo "::notice file=.github/scripts/verify-signatures.sh::Commit $commit by $commit_author has a valid signature from a trusted key"
done

echo "::notice file=.github/scripts/verify-signatures.sh::All commits have valid GPG signatures from trusted keys."
