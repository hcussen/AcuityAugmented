#!/bin/bash

# This script assumes it's being run from the project directory (ynab-venmo-v2)
# Get the absolute path of the current directory
PROJECT_DIR=$(pwd)

# Create or use an iTerm2 window and navigate to the project directory
osascript <<EOF
tell application "iTerm2"
    # Create a new window or use the current one
    set myWindow to (create window with default profile)
    
    tell myWindow
        # Get the initial session (Pane A)
        set paneA to current session
        
        # Create the bottom section first (horizontal split)
        tell paneA
            set bottomPane to (split horizontally with default profile)
        end tell
        
        # Now split the top pane (paneA) vertically to create Pane B
        tell paneA
            set paneB to (split vertically with default profile)
        end tell
        
        # Set up Pane A (original pane - top left)
        tell paneA
            write text "cd \"${PROJECT_DIR}/frontend\""
            write text "pnpm dev"
        end tell
        
        # Set up Pane B (git management pane - top right)
        tell paneB
            write text "cd \"${PROJECT_DIR}\""
            write text "open -a 'Google Chrome' 'http://localhost:3000'"
            write text "open -a 'Google Chrome' 'http://localhost:8000'"
            write text "open -a 'Google Chrome' 'http://localhost:8000/docs'"
            write text "# Git management pane"
        end tell
        
        # Now split the bottom pane vertically to create Panes C and D
        tell bottomPane
            set paneC to (split vertically with default profile)
        end tell
        
        # Set up Pane C (bottom left pane)
        tell bottomPane
            write text "cd \"${PROJECT_DIR}/backend\""
            write text "conda deactivate"
            write text "source .venv/bin/activate"
            write text "fastapi dev main.py"
        end tell
        
        # Set up Pane D (bottom right pane)
        tell paneC
            write text "cd \"${PROJECT_DIR}/backend\""
            write text "conda deactivate"
            write text "source .venv/bin/activate"
        end tell
    end tell
end tell
EOF