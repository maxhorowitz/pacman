import chess
import chess.svg

def main():
  board = chess.Board()
  boardsvg = chess.svg.board(board, size=350)

  outputfile = open('test.svg', "w")
  outputfile.write(boardsvg)
  outputfile.close()
  outputfile

main()