import chess
from IPython.display import SVG
from lib import chess_analysis, chess_io
import chess_plot


def main():

    engine = chess_analysis.connect_to_stockfish()

    # Open PGN file
    # filename = "kasparov_karpov_1986"
    filename = "kramnik_leko_2001"
    # filename = "lcc2017"
    chess_io.init_folder_structure(filename)
    pgn = chess_io.open_pgn(filename)

    # for i in range(35):
    #    act_game = chess.pgn.read_game(pgn)

    act_game = chess_analysis.read_game(pgn)

    print(act_game.headers["Event"] + " / " + act_game.headers["White"] +
          " - " + act_game.headers["Black"] + "  " + act_game.headers["Result"] +
          " / " + act_game.headers["Date"])

    # Register a standard info handler.
    # info_handler = chess.uci.InfoHandler()
    # engine.info_handlers.append(info_handler)

    counts = {
        "fullmove_number": [],  # stores the move numbers
        "turn": [],
        "san": [],  # stores a move in Standard Algebraic Notation (SAN)
        "lan": [],  # stores a move in Long Algebraic Notation (LAN)
        "score": [],  # stores the scores calculated by Stockfish
        "score_shift": [],
        "score_shift_category": [],
        "move_count": [],  # stores the number of possible moves in this turn
        "best_move": [],  # stores the best move in SAN
        "best_move_score": [],  # stores the best move's score
        "best_move_score_diff": [],  # stores the difference between the calculated best move and the actual move
        "best_move_score_diff_category": [],  # stores the category for the calculated difference
        "is_check": [],  # stores if the move checks the opposed king
        "is_capture": [],  # stores is the move actually captures a piece
        "is_castling": [],  # stores if the king has been castled
        "possible_moves_count": [],  # stores the number of possible moves for the next player
        "is_capture_count": [],  # stores the number of possible captures
        "attackers_white": [],
        "attackers_count_white": [],  # stores the number of possible attacks/threats by the opponent
        "threatened_pieces_white": [],
        "threatened_pieces_count_white": [],
        "guards_white": [],
        "guards_count_white": [],
        "guarded_pieces_white": [],
        "guarded_pieces_count_white": [],
        "threatened_guarded_pieces_white": [],
        "threatened_guarded_pieces_count_white": [],
        "unopposed_threats_white": [],
        "unopposed_threats_count_white": [],
        "attackers_black": [],
        "attackers_count_black": [],  # stores the number of possible attacks/threats by the opponent
        "threatened_pieces_black": [],
        "threatened_pieces_count_black": [],
        "guards_black": [],
        "guards_count_black": [],
        "guarded_pieces_black": [],
        "guarded_pieces_count_black": [],
        "threatened_guarded_pieces_black": [],
        "threatened_guarded_pieces_count_black": [],
        "unopposed_threats_black": [],
        "unopposed_threats_count_black": [],
        "threatened_pieces_centipawn_white": [],
        "guarded_pieces_centipawn_white": [],
        "threatened_guarded_pieces_centipawn_white": [],
        "unopposed_threats_centipawn_white": [],
        "threatened_pieces_centipawn_black": [],
        "guarded_pieces_centipawn_black": [],
        "threatened_guarded_pieces_centipawn_black": [],
        "unopposed_threats_centipawn_black": [],
        "attackers_count_all": [],
        "threatened_pieces_count_all": [],
        "guards_count_all": [],
        "guarded_pieces_count_all": [],
        "threatened_guarded_pieces_count_all": [],
        "unopposed_threats_count_all": [],
        "threatened_pieces_centipawn_all": [],
        "guarded_pieces_centipawn_all": [],
        "threatened_guarded_pieces_centipawn_all": [],
        "unopposed_threats_centipawn_all": [],
        "pawn_ending": [],  # stores if only kings and pawns are left on the board
        "rook_ending": [],  # stores if only kings, rooks and possible pawns are left on the board
    }

    time = 0.100

    # Get the intial board of the game
    board = act_game.board()
    print(board.fen())
    chess_io.export_board_svg(board, filename, len(counts["san"]), None)
    prev_score = 0
    score_shift = 0
    # Iterate through all moves and play them on a board.
    for mv in act_game.mainline_moves():
        # calculate opportunities before applying the move
        fullmove_number = board.fullmove_number
        turn = board.turn
        san = board.san(mv)
        lan = board.lan(mv)
        move_count = chess_analysis.compute_move_count(board)
        is_capture = board.is_capture(mv)
        is_castling = board.is_castling(mv)

        # apply move
        board.push(mv)

        score_a = chess_analysis.compute_score(engine, board, time)
        is_check = board.is_check()
        possible_moves_count = chess_analysis.compute_move_count(board)
        captures = chess_analysis.compute_captures(board)
        is_capture_count = len(captures)

        # White player
        attack_moves_white = chess_analysis.compute_attack_moves(board, chess.BLACK)
        attackers_white = chess_analysis.compute_from_square_pieces(attack_moves_white)
        attackers_count_white = len(attackers_white)
        threatened_pieces_white = chess_analysis.compute_to_square_pieces(attack_moves_white)
        threatened_pieces_count_white = len(threatened_pieces_white)
        guard_moves_white = chess_analysis.compute_guard_moves_alt(board, chess.WHITE)
        guards_white = chess_analysis.compute_from_square_pieces(guard_moves_white)
        guards_count_white = len(guards_white)
        guarded_pieces_white = chess_analysis.compute_to_square_pieces(guard_moves_white)
        guarded_pieces_count_white = len(guarded_pieces_white)
        threatened_guarded_pieces_white = chess_analysis.compute_threatened_guarded_pieces(attack_moves_white, guard_moves_white)
        threatened_guarded_pieces_count_white = len(threatened_guarded_pieces_white)
        unopposed_threats_white = chess_analysis.compute_unopposed_threats(threatened_pieces_white, guarded_pieces_white)
        unopposed_threats_count_white = len(unopposed_threats_white)

        # Black player
        attack_moves_black = chess_analysis.compute_attack_moves(board, chess.WHITE)
        attackers_black = chess_analysis.compute_from_square_pieces(attack_moves_black)
        attackers_count_black = len(attackers_black)
        threatened_pieces_black = chess_analysis.compute_to_square_pieces(attack_moves_black)
        threatened_pieces_count_black = len(threatened_pieces_black)
        guard_moves_black = chess_analysis.compute_guard_moves_alt(board, chess.BLACK)
        guards_black = chess_analysis.compute_from_square_pieces(guard_moves_black)
        guards_count_black = len(guards_black)
        guarded_pieces_black = chess_analysis.compute_to_square_pieces(guard_moves_black)
        guarded_pieces_count_black = len(guarded_pieces_black)
        threatened_guarded_pieces_black = chess_analysis.compute_threatened_guarded_pieces(attack_moves_black, guard_moves_black)
        threatened_guarded_pieces_count_black = len(threatened_guarded_pieces_black)
        unopposed_threats_black = chess_analysis.compute_unopposed_threats(threatened_pieces_black, guarded_pieces_black)
        unopposed_threats_count_black = len(unopposed_threats_black)

        threatened_pieces_centipawn_white = chess_analysis.compute_pieces_centipawn_sum(board, threatened_pieces_white)
        guarded_pieces_centipawn_white = chess_analysis.compute_pieces_centipawn_sum(board, guarded_pieces_white)
        threatened_guarded_pieces_centipawn_white = chess_analysis.compute_pieces_centipawn_sum(board, threatened_guarded_pieces_white)
        unopposed_threats_centipawn_white = chess_analysis.compute_pieces_centipawn_sum(board, unopposed_threats_white)
        threatened_pieces_centipawn_black = chess_analysis.compute_pieces_centipawn_sum(board, threatened_pieces_black)
        guarded_pieces_centipawn_black = chess_analysis.compute_pieces_centipawn_sum(board, guarded_pieces_black)
        threatened_guarded_pieces_centipawn_black = chess_analysis.compute_pieces_centipawn_sum(board, threatened_guarded_pieces_black)
        unopposed_threats_centipawn_black = chess_analysis.compute_pieces_centipawn_sum(board, unopposed_threats_black)

        if counts["score"]:
            score_shift = chess_analysis.compute_score_shift(prev_score, score_a)
        score_shift_category = chess_analysis.compute_score_shift_category(score_shift)
        pawn_ending = chess_analysis.pawn_ending(board.fen())
        rook_ending = chess_analysis.rook_ending(board.fen())

        # remove move to calculate the best move as well as the difference between the best move and the actual move
        board.pop()

        score_b, best_move_b = chess_analysis.compute_score_alternative(engine, board, time)
        best_move_score_b = chess_analysis.compute_best_move_score_alternative(engine, board, best_move_b, time)

        best_move_scores = chess_analysis.compute_best_move(engine, board, time)

        if len(best_move_scores) > 1:
            best_move_scores.sort(key=lambda scores: scores[0], reverse=board.turn)
            best_move = board.san(best_move_scores[0][1])
            best_move_score = best_move_scores[0][0]
            best_move_score_diff = abs(best_move_scores[0][0] - score_a)
            best_move_score_diff_category = chess_analysis.categorize_best_move_score_diff(best_move_score_diff, best_move, san)

        else:
            best_move = "-"
            best_move_score = 0
            best_move_score_diff = 0
            best_move_score_diff_category = -1

        prev_score = score_a

        # push actual move to the board again
        board.push(mv)

        counts["fullmove_number"].append(fullmove_number)
        counts["turn"].append(turn)
        counts["san"].append(san)
        counts["lan"].append(lan)
        counts["score"].append(score_a)
        counts["score_shift"].append(score_shift)
        counts["score_shift_category"].append(score_shift_category)
        counts["move_count"].append(move_count)
        counts["best_move"].append(best_move)
        counts["best_move_score"].append(best_move_score)
        counts["best_move_score_diff"].append(best_move_score_diff)
        counts["best_move_score_diff_category"].append(best_move_score_diff_category)
        counts["is_check"].append(is_check)
        counts["is_capture"].append(is_capture)
        counts["is_castling"].append(is_castling)
        counts["possible_moves_count"].append(possible_moves_count)
        counts["is_capture_count"].append(is_capture_count)
        counts["attackers_white"].append(', '.join(str(s) for s in chess_analysis.get_square_names(attackers_white)))
        counts["attackers_count_white"].append(attackers_count_white)
        counts["threatened_pieces_white"].append(', '.join(str(s) for s in chess_analysis.get_square_names(threatened_pieces_white)))
        counts["threatened_pieces_count_white"].append(threatened_pieces_count_white)
        counts["guards_white"].append(', '.join(str(s) for s in chess_analysis.get_square_names(guards_white)))
        counts["guards_count_white"].append(guards_count_white)
        counts["guarded_pieces_white"].append(', '.join(str(s) for s in chess_analysis.get_square_names(guarded_pieces_white)))
        counts["guarded_pieces_count_white"].append(guarded_pieces_count_white)
        counts["threatened_guarded_pieces_white"].append(', '.join(str(s) for s in chess_analysis.get_square_names(threatened_guarded_pieces_white)))
        counts["threatened_guarded_pieces_count_white"].append(threatened_guarded_pieces_count_white)
        counts["unopposed_threats_white"].append(', '.join(str(s) for s in chess_analysis.get_square_names(unopposed_threats_white)))
        counts["unopposed_threats_count_white"].append(unopposed_threats_count_white)
        counts["attackers_black"].append(', '.join(str(s) for s in chess_analysis.get_square_names(attackers_black)))
        counts["attackers_count_black"].append(attackers_count_black)
        counts["threatened_pieces_black"].append(
            ', '.join(str(s) for s in chess_analysis.get_square_names(threatened_pieces_black)))
        counts["threatened_pieces_count_black"].append(threatened_pieces_count_black)
        counts["guards_black"].append(', '.join(str(s) for s in chess_analysis.get_square_names(guards_black)))
        counts["guards_count_black"].append(guards_count_black)
        counts["guarded_pieces_black"].append(', '.join(str(s) for s in chess_analysis.get_square_names(guarded_pieces_black)))
        counts["guarded_pieces_count_black"].append(guarded_pieces_count_black)
        counts["threatened_guarded_pieces_black"].append(
            ', '.join(str(s) for s in chess_analysis.get_square_names(threatened_guarded_pieces_black)))
        counts["threatened_guarded_pieces_count_black"].append(threatened_guarded_pieces_count_black)
        counts["unopposed_threats_black"].append(
            ', '.join(str(s) for s in chess_analysis.get_square_names(unopposed_threats_black)))
        counts["unopposed_threats_count_black"].append(unopposed_threats_count_black)

        counts["threatened_pieces_centipawn_white"].append(threatened_pieces_centipawn_white)
        counts["guarded_pieces_centipawn_white"].append(guarded_pieces_centipawn_white)
        counts["threatened_guarded_pieces_centipawn_white"].append(threatened_guarded_pieces_centipawn_white)
        counts["unopposed_threats_centipawn_white"].append(unopposed_threats_centipawn_white)
        counts["threatened_pieces_centipawn_black"].append(threatened_pieces_centipawn_black)
        counts["guarded_pieces_centipawn_black"].append(guarded_pieces_centipawn_black)
        counts["threatened_guarded_pieces_centipawn_black"].append(threatened_guarded_pieces_centipawn_black)
        counts["unopposed_threats_centipawn_black"].append(unopposed_threats_centipawn_black)
        counts["attackers_count_all"].append(attackers_count_white+attackers_count_black)
        counts["threatened_pieces_count_all"].append(threatened_pieces_count_white+threatened_pieces_count_black)
        counts["guards_count_all"].append(guards_count_white+guards_count_black)
        counts["guarded_pieces_count_all"].append(guarded_pieces_count_white+guarded_pieces_count_black)
        counts["threatened_guarded_pieces_count_all"].append(threatened_guarded_pieces_count_white+threatened_guarded_pieces_count_black)
        counts["unopposed_threats_count_all"].append(unopposed_threats_count_white+unopposed_threats_count_black)
        counts["threatened_pieces_centipawn_all"].append(threatened_pieces_centipawn_white+threatened_pieces_centipawn_black)
        counts["guarded_pieces_centipawn_all"].append(guarded_pieces_centipawn_white+guarded_pieces_centipawn_black)
        counts["threatened_guarded_pieces_centipawn_all"].append(threatened_guarded_pieces_centipawn_white+threatened_guarded_pieces_centipawn_black)
        counts["unopposed_threats_centipawn_all"].append(unopposed_threats_centipawn_white+unopposed_threats_centipawn_black)
        counts["pawn_ending"].append(pawn_ending)
        counts["rook_ending"].append(rook_ending)

        chess_io.export_board_svg(board, filename, len(counts["san"]), mv)
        print('actual_score: ', score_a, ' alt_score: ', score_b)
        print('actual_best_move: ', best_move, ' best_score: ', best_move_scores[0][0])
        #print('alt_best_move: ', a_best_move, ' alt_best_score: ', a_best_move_score)

        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    SVG(chess.svg.board(board=board, size=400))

    chess_plot.plot_graph(act_game, filename, counts)
    print("before csv")
    print(counts)
    chess_io.write_dict_to_csv(filename, counts)
    print("after csv")
    return 0


main()
