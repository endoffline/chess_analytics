import chess
from lib import chess_analysis, chess_io
from lib import chess_moves
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.game import Game
from datetime import datetime, date


def bulk_analyse(engine, session, act_game):

    # times = [0.010, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001]
    times = [0.010, 0.020, 0.050, 0.100, 0.200, 0.500, 1.000, 2.000, 0.001]
    depths = [17, 20]

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
                   whiteelo=(int(act_game.headers["WhiteElo"]) if act_game.headers["WhiteElo"].isdigit() else None),
                   blackelo=(int(act_game.headers["BlackElo"]) if act_game.headers["BlackElo"].isdigit() else None),
                   result=act_game.headers["Result"]
                   )

    print(db_game)

    # Iterate through all moves and play them on a board.
    prev_score = 0
    best_moves_b = []
    for ply_number, mv in enumerate(act_game.mainline_moves(), start=1):
        for i in range(0, 5):
            db_mv, temp_best_moves_b = chess_moves.compute_move(engine, board, mv, ply_number, times, depths, prev_score, best_moves_b)
            db_game.moves.append(db_mv)
            print(db_mv)
        prev_score = db_mv.score
        best_moves_b = temp_best_moves_b
        # push actual move to the board again
        board.push(mv)

    db_game.length = int(ply_number)
    session.add(db_game)
    session.commit()


def main():

    chess_engine = chess_analysis.connect_to_stockfish()
    db_engine = create_engine('sqlite:///bulk_analysis_' + date.today().strftime("%Y-%m-%d") + '.db', echo=True)
    Base.metadata.create_all(db_engine)
    Session = sessionmaker(bind=db_engine)
    session = Session()
    # Open PGN file
    filename = "lcc2017_mini"
    chess_io.init_folder_structure(filename)
    pgn = chess_io.open_pgn(filename)

    while True:
        act_game = chess.pgn.read_game(pgn)
        if act_game is None:
            break

        bulk_analyse(chess_engine, session, act_game)
    session.close()
    chess_engine.quit()

main()

