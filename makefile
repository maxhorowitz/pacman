init-env:
	conda env create --file environment.yml && conda activate pacman-env

start-env:
	conda activate pacman-env

leave-env:
	conda deactivate

delete-env:
	conda env remove -n pacman-env

user:
	python run.py user

ai:
	python run.py ai