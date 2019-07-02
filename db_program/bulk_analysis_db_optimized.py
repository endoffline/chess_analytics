import chess
from lib import chess_analysis, chess_io
from lib import chess_moves
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.game import Game
from datetime import datetime


def bulk_analyse(engine, session, act_game):
    time = 0.100
    # Get the intial board of the game
    board = act_game.board()

    print(act_game.headers["Event"] + " / " + act_game.headers["White"] +
          " - " + act_game.headers["Black"] + "  " + act_game.headers["Result"] +
          " / " + act_game.headers["Date"])

    db_game = Game(event=act_game.headers["Event"],
                   site=act_game.headers["Site"],
                   date=datetime.strptime(act_game.headers["Date"], '%Y.%m.%d').date(),
                   round=act_game.headers["Round"],
                   white=act_game.headers["White"],
                   black=act_game.headers["Black"],
                   result=act_game.headers["Result"]
                   )

    print(db_game)

    # Iterate through all moves and play them on a board.
    prev_score = 0
    for ply_number, mv in enumerate(act_game.mainline_moves(), start=1):
        db_mv = chess_moves.compute_move_optimized(engine, board, mv, ply_number, time, prev_score)
        db_game.moves.append(db_mv)
        prev_score = db_mv.score
        print(db_mv)

        # push actual move to the board again
        board.push(mv)

    session.add(db_game)
    session.commit()


def main():

    chess_engine = chess_analysis.connect_to_stockfish()
    db_engine = create_engine('sqlite:///chess_optimized.db', echo=True)
    Base.metadata.create_all(db_engine)
    Session = sessionmaker(bind=db_engine)
    session = Session()
    # Open PGN file
    # filename = "kasparov_karpov_1986"
    # filename = "kramnik_leko_2001"
    # filename = "lcc2017_mini"
    filename = "lcc2017"
    chess_io.init_folder_structure(filename)
    pgn = chess_io.open_pgn(filename)

    # for i in range(35):
    #   act_game = chess.pgn.read_game(pgn)

    while True:
        act_game = chess.pgn.read_game(pgn)
        if act_game is None:
            break

        bulk_analyse(chess_engine, session, act_game)


main()

