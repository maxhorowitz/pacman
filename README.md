# Pacman
Jacob Ball, Max Horowitz, Sophie Lopez

# Setup
We assume you have `conda` installed on your machine. If you don't, install it first.
For first time running, you need to create a virtual environment on your machine that has all of the necessary dependencies. To do this, run `conda env create --file environment.yml`.
Once the virtual environment is set up, run `conda activate pacman-env` to enter the environment.
To leave the virtual environment when you are done playing, run `conda deactivate`.
To delete the virtual environment, run `conda env remove -n pacman-env`.

# Gameplay
To watch the AI engine play on its own, run `make ai`.
To run a benchmark test of the AI engine, run `make benchmark`.
To play yourself, run `make user`.

# Credits
Uses 'pacmancode' for Pacman game implementation (rules, gameflow, etc.) as well as for its GUI. It can be found at https://pacmancode.com.