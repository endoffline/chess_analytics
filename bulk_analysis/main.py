import chess
from IPython.display import SVG
import chess_io
import chess_analysis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.move import Move
from models.game import Game
from models.score import Score
from datetime import datetime
from time import monotonic


def bulk_analyse(filename, engine, session, act_game):

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

    #time = 0.100
    times = [0.010, 0.020, 0.050, 0.100, 0.200, 0.500, 1.000, 2.000, 5.000]
    # times = [0.010, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001]
    # Iterate through all moves and play them on a board.
    for mv in act_game.mainline_moves():
        scores_a, best_moves_a, best_move_scores_a, best_move_score_diffs_a, best_move_score_diff_categories_a = [], [], [], [], []
        scores_b, best_moves_b, best_move_scores_b, best_move_score_diffs_b, best_move_score_diff_categories_b = [], [], [], [], []

        fullmove_number = board.fullmove_number
        turn = board.turn
        san = board.san(mv)
        lan = board.lan(mv)
        move_count = chess_analysis.compute_move_count(board)
        is_capture = board.is_capture(mv)
        is_castling = board.is_castling(mv)

        # apply move
        board.push(mv)
        start = monotonic()
        for time in times:
            score_a = chess_analysis.compute_score(engine, board, time)
            scores_a.append(score_a)

        end = monotonic()
        delta = end - start
        print(start, end, delta)
        is_check = board.is_check()

        pawn_ending = chess_analysis.pawn_ending(board.fen())
        rook_ending = chess_analysis.rook_ending(board.fen())

        attack_moves = chess_analysis.compute_attack_moves(board)
        attackers = chess_analysis.compute_from_square_pieces(attack_moves)
        attackers_count = len(attackers)
        threatened_pieces = chess_analysis.compute_to_square_pieces(attack_moves)
        threatened_pieces_count = len(threatened_pieces)
        captures = chess_analysis.compute_captures(board)
        is_capture_count = len(captures)

        guard_moves = chess_analysis.compute_guard_moves(board)
        guards = chess_analysis.compute_from_square_pieces(guard_moves)
        guards_count = len(guards)
        guarded_pieces = chess_analysis.compute_to_square_pieces(guard_moves)
        guarded_pieces_count = len(guarded_pieces)

        threatened_guarded_pieces = chess_analysis.compute_threatened_guarded_pieces(attack_moves, guard_moves)
        threatened_guarded_pieces_count = len(threatened_guarded_pieces)
        unopposed_threats = chess_analysis.compute_unopposed_threats(threatened_pieces, guarded_pieces)
        unopposed_threats_count = len(unopposed_threats)
        possible_moves_count = chess_analysis.compute_move_count(board)

        board.pop()

        for time in times:
            print("Time: %d", time)
            next_move_scores_a = chess_analysis.compute_best_move(engine, board, time)

            if len(next_move_scores_a) > 1:
                next_move_scores_a.sort(key=lambda scores: scores[0], reverse=board.turn)
                best_move_a = board.san(next_move_scores_a[0][1])
                best_move_score_a = next_move_scores_a[0][0]
                best_move_score_diff_a = abs(next_move_scores_a[0][0] - score_a)
                best_move_score_diff_category_a = chess_analysis.categorize_best_move_score_diff(best_move_score_diff_a,
                                                                                                 best_move_a, san)
            else:
                best_move_a = "-"
                best_move_score_a = 0
                best_move_score_diff_a = 0
                best_move_score_diff_category_a = -1

            best_moves_a.append(best_move_a)
            best_move_scores_a.append(best_move_score_a)
            best_move_score_diffs_a.append(best_move_score_diff_a)
            best_move_score_diff_categories_a.append(best_move_score_diff_category_a)

            score_b, best_move_b = chess_analysis.compute_score_alternative(engine, board, time)
            best_move_score_b = chess_analysis.compute_best_move_score_alternative(engine, board, best_move_b, time)
            best_move_score_diff_b = abs(best_move_score_b - score_b)
            best_move_b = board.san(best_move_b)
            best_move_score_diff_category_b = chess_analysis.categorize_best_move_score_diff(best_move_score_diff_b,
                                                                                             best_move_b, san)

            scores_b.append(score_b)
            best_moves_b.append(best_move_b)
            best_move_scores_b.append(best_move_score_b)
            best_move_score_diffs_b.append(best_move_score_diff_b)
            best_move_score_diff_categories_b.append(best_move_score_diff_category_b)

        # push actual move to the board again
        board.push(mv)
        db_mv = Move(
            fullmove_number=fullmove_number,
            turn=turn,
            san=san,
            lan=lan,
            score=scores_a[3],
            move_count=move_count,
            best_move=best_moves_a[3],
            best_move_score=best_move_scores_a[3],
            best_move_score_diff=best_move_score_diffs_a[3],
            best_move_score_diff_category=best_move_score_diff_categories_a[3],
            is_check=is_check,
            is_capture=is_capture,
            is_castling=is_castling,
            possible_moves_count=possible_moves_count,
            is_capture_count=is_capture_count,
            attackers=', '.join(str(s) for s in attackers),
            attackers_count=attackers_count,
            threatened_pieces=', '.join(str(s) for s in threatened_pieces),
            threatened_pieces_count=threatened_pieces_count,
            guards=', '.join(str(s) for s in guards),
            guards_count=guards_count,
            guarded_pieces=', '.join(str(s) for s in guarded_pieces),
            guarded_pieces_count=guarded_pieces_count,
            threatened_guarded_pieces=', '.join(str(s) for s in threatened_guarded_pieces),
            threatened_guarded_pieces_count=threatened_guarded_pieces_count,
            unopposed_threats=', '.join(str(s) for s in unopposed_threats),
            unopposed_threats_count=unopposed_threats_count,
            pawn_ending=pawn_ending,
            rook_ending=rook_ending
        )
        db_game.moves.append(db_mv)
        print(db_mv)

        db_score = Score(
            score_a0010 = scores_a[0],
            score_a0020 = scores_a[1],
            score_a0050 = scores_a[2],
            score_a0100 = scores_a[3],
            score_a0200 = scores_a[4],
            score_a0500 = scores_a[5],
            score_a1000 = scores_a[6],
            score_a2000 = scores_a[7],
            score_a5000 = scores_a[8],
            best_move_a0010 = best_moves_a[0],
            best_move_a0020 = best_moves_a[1],
            best_move_a0050 = best_moves_a[2],
            best_move_a0100 = best_moves_a[3],
            best_move_a0200 = best_moves_a[4],
            best_move_a0500 = best_moves_a[5],
            best_move_a1000 = best_moves_a[6],
            best_move_a2000 = best_moves_a[7],
            best_move_a5000 = best_moves_a[8],
            best_move_score_a0010 = best_move_scores_a[0],
            best_move_score_a0020 = best_move_scores_a[1],
            best_move_score_a0050 = best_move_scores_a[2],
            best_move_score_a0100 = best_move_scores_a[3],
            best_move_score_a0200 = best_move_scores_a[4],
            best_move_score_a0500 = best_move_scores_a[5],
            best_move_score_a1000 = best_move_scores_a[6],
            best_move_score_a2000 = best_move_scores_a[7],
            best_move_score_a5000 = best_move_scores_a[8],
            best_move_score_diff_a0010 = best_move_score_diffs_a[0],
            best_move_score_diff_a0020 = best_move_score_diffs_a[1],
            best_move_score_diff_a0050 = best_move_score_diffs_a[2],
            best_move_score_diff_a0100 = best_move_score_diffs_a[3],
            best_move_score_diff_a0200 = best_move_score_diffs_a[4],
            best_move_score_diff_a0500 = best_move_score_diffs_a[5],
            best_move_score_diff_a1000 = best_move_score_diffs_a[6],
            best_move_score_diff_a2000 = best_move_score_diffs_a[7],
            best_move_score_diff_a5000 = best_move_score_diffs_a[8],
            best_move_score_diff_category_a0010 = best_move_score_diff_categories_a[0],
            best_move_score_diff_category_a0020 = best_move_score_diff_categories_a[1],
            best_move_score_diff_category_a0050 = best_move_score_diff_categories_a[2],
            best_move_score_diff_category_a0100 = best_move_score_diff_categories_a[3],
            best_move_score_diff_category_a0200 = best_move_score_diff_categories_a[4],
            best_move_score_diff_category_a0500 = best_move_score_diff_categories_a[5],
            best_move_score_diff_category_a1000 = best_move_score_diff_categories_a[6],
            best_move_score_diff_category_a2000 = best_move_score_diff_categories_a[7],
            best_move_score_diff_category_a5000 = best_move_score_diff_categories_a[8],

            score_b0010=scores_b[0],
            score_b0020=scores_b[1],
            score_b0050=scores_b[2],
            score_b0100=scores_b[3],
            score_b0200=scores_b[4],
            score_b0500=scores_b[5],
            score_b1000=scores_b[6],
            score_b2000=scores_b[7],
            score_b5000=scores_b[8],
            best_move_b0010=best_moves_b[0],
            best_move_b0020=best_moves_b[1],
            best_move_b0050=best_moves_b[2],
            best_move_b0100=best_moves_b[3],
            best_move_b0200=best_moves_b[4],
            best_move_b0500=best_moves_b[5],
            best_move_b1000=best_moves_b[6],
            best_move_b2000=best_moves_b[7],
            best_move_b5000=best_moves_b[8],
            best_move_score_b0010=best_move_scores_b[0],
            best_move_score_b0020=best_move_scores_b[1],
            best_move_score_b0050=best_move_scores_b[2],
            best_move_score_b0100=best_move_scores_b[3],
            best_move_score_b0200=best_move_scores_b[4],
            best_move_score_b0500=best_move_scores_b[5],
            best_move_score_b1000=best_move_scores_b[6],
            best_move_score_b2000=best_move_scores_b[7],
            best_move_score_b5000=best_move_scores_b[8],
            best_move_score_diff_b0010=best_move_score_diffs_b[0],
            best_move_score_diff_b0020=best_move_score_diffs_b[1],
            best_move_score_diff_b0050=best_move_score_diffs_b[2],
            best_move_score_diff_b0100=best_move_score_diffs_b[3],
            best_move_score_diff_b0200=best_move_score_diffs_b[4],
            best_move_score_diff_b0500=best_move_score_diffs_b[5],
            best_move_score_diff_b1000=best_move_score_diffs_b[6],
            best_move_score_diff_b2000=best_move_score_diffs_b[7],
            best_move_score_diff_b5000=best_move_score_diffs_b[8],
            best_move_score_diff_category_b0010=best_move_score_diff_categories_b[0],
            best_move_score_diff_category_b0020=best_move_score_diff_categories_b[1],
            best_move_score_diff_category_b0050=best_move_score_diff_categories_b[2],
            best_move_score_diff_category_b0100=best_move_score_diff_categories_b[3],
            best_move_score_diff_category_b0200=best_move_score_diff_categories_b[4],
            best_move_score_diff_category_b0500=best_move_score_diff_categories_b[5],
            best_move_score_diff_category_b1000=best_move_score_diff_categories_b[6],
            best_move_score_diff_category_b2000=best_move_score_diff_categories_b[7],
            best_move_score_diff_category_b5000=best_move_score_diff_categories_b[8],
        )

        session.add(db_score)
        session.commit()

    session.add(db_game)
    session.commit()


def main():

    chess_engine = chess_analysis.connect_to_stockfish()
    db_engine = create_engine('sqlite:///chess.db', echo=True)
    Base.metadata.create_all(db_engine)
    Session = sessionmaker(bind=db_engine)
    session = Session()
    # Open PGN file
    # filename = "kasparov_karpov_1986"
    # filename = "kramnik_leko_2001"
    filename = "lcc2017_mini"
    chess_io.init_folder_structure(filename)
    pgn = chess_io.open_pgn(filename)

    # for i in range(35):
    #   act_game = chess.pgn.read_game(pgn)

    while True:
        act_game = chess.pgn.read_game(pgn)
        if act_game is None:
            break

        bulk_analyse(filename, chess_engine, session, act_game)


main()

