init-env:
	conda env create --file environment.yml

start-env:
	conda activate chess-env

leave-env:
	conda deactivate