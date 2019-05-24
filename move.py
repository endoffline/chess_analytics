import chess

class Move:

    def __init__(self, board, move):
        self.__board = board
        self.__move = move

        self.fullmove_number = board.fullmove_number
        self.san = board.san(move)
        self.lan = board.lan(move)
        self.move_count = len([i for i in board.legal_moves])
        self.is_capture = board.is_capture(move)
        self.is_castling = board.is_castling(move)

        board.push(move)

