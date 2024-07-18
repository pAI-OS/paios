#!/bin/bash
set -euo pipefail

# Directory containing trusted public keys
TRUSTED_KEYS_DIR=".github/gpg-keys"

# Use the GPG_KEYSERVER environment variable, defaulting to keyserver.ubuntu.com if not set
GPG_KEYSERVER="${GPG_KEYSERVER:-keyserver.ubuntu.com}"

# Check if we should verify all commits or just incoming ones
CHECK_ALL_COMMITS="${CHECK_ALL_COMMITS:-false}"

# Import all maintainer public keys and set ultimate trust
for key in "$TRUSTED_KEYS_DIR"/*; do
  gpg --import "$key"
  key_id=$(gpg --with-colons --show-keys "$key" | awk -F: '/^pub:/ {print $5}')
  echo -e "5\ny\n" | gpg --command-fd 0 --expert --batch --edit-key "$key_id" trust
done

# Function to check if a key is signed by a trusted key
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

# Determine the range of commits to check
if [ "$CHECK_ALL_COMMITS" = "true" ]; then
  echo "Checking all commits in the repository"
  commit_range="--all"
else
  if [ "$GITHUB_EVENT_NAME" == "pull_request" ]; then
    # For pull requests, check commits between base and head
    commit_range="${GITHUB_BASE_REF}..${GITHUB_HEAD_REF}"
  elif [ "$GITHUB_EVENT_NAME" == "push" ]; then
    # For pushes, check commits between before and after the push
    commit_range="${GITHUB_EVENT_BEFORE}..${GITHUB_SHA}"
  else
    echo "Unsupported event type: $GITHUB_EVENT_NAME"
    exit 1
  fi
  echo "Checking commits in range: $commit_range"
fi

# Verify each commit
for commit in $(git rev-list --no-merges $commit_range); do
  echo "Verifying commit: $commit"
  
  # Get the author of the commit
  commit_author=$(git log -1 --format='%an <%ae>' $commit)
  
  # Get detailed signature information
  signature_info=$(git verify-commit "$commit" 2>&1)
  signature_status=$(git log -1 --format='%G?' $commit)
  
  echo "Signature status: $signature_status"
  echo "Signature info: $signature_info"
  
  # Check if it's a GPG signature (not SSH)
  if [[ "$signature_status" != "G" && "$signature_status" != "U" ]]; then
    echo "::error file=.github/scripts/verify-signatures.sh::Commit $commit by $commit_author is not signed with GPG (status: $signature_status)"
    exit 1
  fi
  
  # Get the signing key ID
  signing_key=$(git log --format='%GK' -n 1 "$commit")
  
  # Check if the signing key is a maintainer key
  if gpg --list-keys --with-colons "$signing_key" | grep -q "^pub"; then
    echo "::notice file=.github/scripts/verify-signatures.sh::Commit $commit by $commit_author is signed by a trusted key: $signing_key"
    continue
  fi
  
  # If not a maintainer key, check if it's signed by a maintainer
  if ! is_signed_by_trusted_key "$signing_key"; then
    echo "::error file=.github/scripts/verify-signatures.sh::Commit $commit by $commit_author is signed by an untrusted key: $signing_key"
    exit 1
  fi
  
  echo "::notice file=.github/scripts/verify-signatures.sh::Commit $commit by $commit_author has a valid signature from a trusted key"
done

echo "::notice file=.github/scripts/verify-signatures.sh::All commits have valid GPG signatures from trusted keys."
