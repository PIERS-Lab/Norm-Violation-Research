#!/bin/bash

# 1. Load the environment variables from your .env file into this Bash session
# This automatically creates the variables $DEVICE_1_ID and $DEVICE_2_ID
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "[ERROR] .env file not found!"
    exit 1
fi

# Normalize Windows .env artifacts (CRLF/quotes) so adb serial matching works.
DEVICE_1_ID="$(printf "%s" "$DEVICE_1_ID" | tr -d '\r' | tr -d '"' | tr -d "'")"
DEVICE_2_ID="$(printf "%s" "$DEVICE_2_ID" | tr -d '\r' | tr -d '"' | tr -d "'")"

clear
echo "============================================="
echo "  TINY DELIVER CO. EXPERIMENTAL RUNNER      "
echo "============================================="
echo ""

# Helper function to pause the script until you press Enter or Down Arrow
next_step() {
    echo "👉 [PRESS ENTER] to execute: $1"
    read -r
}

# --- TRIAL 1 ---
next_step "Trial 1 - Near Cozmo Delivery (Robot 1)"
python deliver_cube.py near near near "$DEVICE_1_ID"

next_step "Trial 1 - Far Cozmo Delivery (Robot 2)"
python deliver_cube.py far near far "$DEVICE_2_ID"

echo "👉 Ask participant to reset table and advance whiteboard score."
echo "---------------------------------------------------------"

# --- TRIAL 2 ---
next_step "Trial 2 - Near Cozmo Delivery (Robot 1)"
python deliver_cube.py near mid near "$DEVICE_1_ID"

next_step "Trial 2 - Far Cozmo Delivery (Robot 2)"
python deliver_cube.py far mid far "$DEVICE_2_ID"

echo "👉 Ask participant to reset table."
echo "---------------------------------------------------------"

next_step "Trial 3 - Near Cozmo Delivery"
python deliver_cube.py near far mid "$DEVICE_1_ID"

echo "============================================="
echo "   SESSION COMPLETE                          "
echo "============================================="