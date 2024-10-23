while getopts ":s" opt; do
  case $opt in
    s)
      echo "\033[0;33m[RUN]\033[0m Starting setup routine..."
      ./setup.sh
      if [ $? -ne 0 ]
      then
        echo "\033[0;33m[RUN]\033[0m \033[1;31mSetup failed! \033[0m"
        echo "\033[0;33m[RUN]\033[0m \033[1;31mAborting run... \033[0m"
        exit 1
      else 
        echo "\033[0;33m[RUN]\033[0m \033[1;32mSetup successful! \033[0m"
        echo "\033[0;33m[RUN]\033[0m \033[1;32mStarting run... \033[0m"
        sleep 3
      fi
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
  esac
done

SCRIPT_DIR="$(pwd)"

# kill all tmux sessions
tmux kill-server

# create new session
tmux new-session -d -s mysession

# Upper window for script 1
tmux split-window -v -p 66
tmux send-keys -t 0 "cd '$SCRIPT_DIR/hub' && echo Starting hub... && sleep 1 && python3 main.py -c" C-m

# Middle windows for scripts 2 and 3
tmux split-window -d
tmux split-window -h
tmux send-keys -t 1 "cd '$SCRIPT_DIR/simulators' && echo Starting sensors... && sleep 7 && python3 sensor_simulator.py" C-m
tmux send-keys -t 2 "cd '$SCRIPT_DIR/simulators' && echo Starting actuators... && sleep 7 && python3 actuator_simulator.py" C-m

# attach to session
tmux select-pane -t 0
tmux attach-session -t mysession