# setup_vscode.sh

# Description: This script is used to setup the VSCode settings.json file by
# substituting the PAIOS_BEARER_TOKEN value from the .env file in the backend
# directory. This allows the REST Client extension to use the PAIOS_BEARER_TOKEN
# value to authenticate requests to the PAIOS API.

# Get the absolute path to the script's parent directory
PARENT_DIR=$(dirname "$(dirname "$(realpath "$0")")")

# Define the source and target files
SOURCE_FILE="$PARENT_DIR/.vscode/settings.json.sample"
TARGET_FILE="$PARENT_DIR/.vscode/settings.json"

# Load the VITE_PAIOS_BEARER_TOKEN from .env and substitute in settings.json.sample
source "$PARENT_DIR/backend/.env"
if [ -z "$PAIOS_BEARER_TOKEN" ]; then
  echo "Warning: PAIOS_BEARER_TOKEN is not set in backend/.env."
  echo "Please ensure to set PAIOS_BEARER_TOKEN by running the backend or manually setting it in backend/.env."
else
  sed "s/your_token_value_here/$PAIOS_BEARER_TOKEN/g" "$SOURCE_FILE" > "$TARGET_FILE"
fi
