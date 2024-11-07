# Start mini omni server
#!/bin/bash

# Define the screen session names
SERVER_SESSION="mini-omni-server"
UI_SESSION="mini-omni-ui"

function kill_screen() {
    if screen -ls | grep -q "$1"; then
    # If the session exists, kill it
    echo "Killing existing $1 screen session..."
    screen -S "$1" -X quit
    fi
}

kill_screen $SERVER_SESSION
kill_screen $UI_SESSION

# Start the screen sessions
echo "Starting $SERVER_SESSION screen session..."
screen -S "$SERVER_SESSION" -d -m bash -c "cd mini-omni;"

echo "Starting $UI_SESSION screen session..."

# streamlit
# screen -S "$UI_SESSION" -d -m bash -c "API_URL=http://0.0.0.0:60808/chat streamlit run webui/omni_streamlit.py"

# gradio
screen -S "$UI_SESSION" -d -m bash -c "API_URL=http://0.0.0.0:60808/chat python3 webui/omni_gradio.py"

# Attach
# screen -r mini-omni-server
# screen -r mini-omni-ui

# Deattach: Ctrl+A, D