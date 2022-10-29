init-env:
	conda env create --file environment.yml && conda activate pacman-env

start-env:
	conda activate pacman-env

leave-env:
	conda deactivate

delete-env:
	conda env remove -n pacman-env

play:
	python run.py

ai:
	python run.py