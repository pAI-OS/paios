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

# Print trusted keys
echo "Trusted keys:"
gpg --list-keys --fingerprint

# Function to check if a key is trusted or signed by a trusted key
is_key_trusted_or_signed_by_trusted() {
  local key_id="$1"
  local trusted_fingerprints=$(gpg --with-colons --list-keys --fingerprint | awk -F: '/^fpr:/ && !/:sub:/ {print $10}')
  
  # Check if the key is directly trusted
  if echo "$trusted_fingerprints" | grep -q "$key_id"; then
    echo "Key $key_id is directly trusted"
    return 0
  fi
  
  # Fetch the key from keyserver
  gpg --keyserver "$GPG_KEYSERVER" --recv-keys "$key_id"
  
  # Print the imported key details
  echo "Imported key details:"
  gpg --list-keys "$key_id"
  
  # Print the signatures on the key
  echo "Signatures on the key:"
  gpg --list-signatures "$key_id"
  
  # Check if the key is signed by a trusted key
  for trusted_fpr in $trusted_fingerprints; do
    if gpg --check-sigs --with-colons "$key_id" | grep -q "sig:!:::::::::$trusted_fpr:"; then
      echo "Key $key_id is signed by trusted key $trusted_fpr"
      return 0
    fi
  done
  
  echo "Key $key_id is neither trusted nor signed by any trusted key"
  return 1
}

# Debug: Print GPG version and configuration
echo "GPG version:"
gpg --version
echo "GPG configuration:"
gpg --list-config

# Debug: List imported keys
echo "Imported GPG keys:"
gpg --list-keys

# Determine the range of commits to check
if [ "$CHECK_ALL_COMMITS" = "true" ]; then
  echo "Checking all commits in the repository"
  commit_range="--all"
else
  if [ "$GITHUB_EVENT_NAME" == "pull_request" ]; then
    # For pull requests, check commits between base and head
    commit_range="origin/${GITHUB_BASE_REF}..HEAD"
  elif [ "$GITHUB_EVENT_NAME" == "push" ]; then
    # For pushes, check commits between before and after the push
    commit_range="${GITHUB_EVENT_BEFORE}..${GITHUB_SHA}"
  else
    echo "Unsupported event type: $GITHUB_EVENT_NAME"
    exit 1
  fi
  echo "Checking commits in range: $commit_range"
fi

# Add a failure flag
failure=false

# Verify each commit, including merge commits
for commit in $(git rev-list $commit_range); do
  echo "Verifying commit: $commit"
  
  # Get the author of the commit
  commit_author=$(git log -1 --format='%an <%ae>' $commit)
  echo "Commit author: $commit_author"

  # Get detailed signature information
  echo "Attempting to verify commit signature..."
  signature_info=$(git verify-commit "$commit" 2>&1) || true
  echo "Raw signature info: $signature_info"
  
  # Check if it's an SSH signature
  if [[ "$signature_info" == "Good \"git\" signature"* ]]; then
    echo "::warning file=.github/scripts/verify-signatures.sh::Commit $commit by $commit_author is signed with SSH, but only GPG is accepted"
    failure=true
    continue
  fi

  signature_status=$(git log -1 --format='%G?' $commit)
  echo "Signature status: $signature_status"
  
  # Check if it's a GPG signature (not SSH)
  if [[ "$signature_status" != "G" && "$signature_status" != "U" && "$signature_status" != "E" ]]; then
    echo "::warning file=.github/scripts/verify-signatures.sh::Commit $commit by $commit_author is not signed with GPG (status: $signature_status)"
    failure=true
    continue
  fi
  
  # Get the signing key ID and trim whitespace
  signing_key=$(git log --format='%GK' -n 1 "$commit" | tr -d '[:space:]')
  echo "Signing key: $signing_key"
  
  if [ -z "$signing_key" ]; then
    echo "::warning file=.github/scripts/verify-signatures.sh::No signing key found for commit $commit by $commit_author"
    failure=true
    continue
  fi
  
  if [[ "$signing_key" == "B5690EEEBB952194" ]]; then
    echo "::notice file=.github/scripts/verify-signatures.sh::Commit $commit by $commit_author is signed by GitHub (likely made through web interface or API)"
  elif ! is_key_trusted_or_signed_by_trusted "$signing_key"; then
    echo "::warning file=.github/scripts/verify-signatures.sh::Commit $commit by $commit_author is signed by a key neither trusted nor signed by any trusted key: $signing_key"
    failure=true
    continue
  else
    echo "::notice file=.github/scripts/verify-signatures.sh::Commit $commit by $commit_author has a valid signature from a trusted key or a key signed by a trusted key"
  fi
done

# Check if any warnings were issued
if [ "$failure" = true ]; then
  echo "::error file=.github/scripts/verify-signatures.sh::Some commits have signature verification issues."
  exit 1
else
  echo "::notice file=.github/scripts/verify-signatures.sh::All commits have valid GPG signatures from trusted keys."
fi