init-env:
	conda env create --file environment.yml && conda activate chess-env

start-env:
	conda activate chess-env

leave-env:
	conda deactivate

delete-env:
	conda env remove -n chess-env

play:
	python simple-chess-game/gui.py