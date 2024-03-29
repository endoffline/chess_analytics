import chess
from IPython.display import SVG
from lib import chess_analysis, chess_io
import chess_plot


def analyse(filename, engine, pgn):

    act_game = chess_analysis.read_game(pgn)

    print(act_game.headers["Event"] + " / " + act_game.headers["White"] +
          " - " + act_game.headers["Black"] + "  " + act_game.headers["Result"] +
          " / " + act_game.headers["Date"])

    # Register a standard info handler.
    # info_handler = chess.uci.InfoHandler()
    # engine.info_handlers.append(info_handler)

    counts = {
        "fullmove_number": [],  # stores the move numbers
        "san": [],  # stores a move in Standard Algebraic Notation (SAN)
        "lan": [],  # stores a move in Long Algebraic Notation (LAN)
        "move_count": [],  # stores the number of possible moves in this turn
        "score": [],  # stores the scores calculated by Stockfish
        "best_move_score_diff": [],  # stores the difference between the calculated best move and the actual move
        "best_move_score_diff_category": [],  # stores the category for the calculated difference
        "best_move": [],  # stores the best move in SAN
        "best_move_score": [],  # stores the best move's score
        "is_check": [],  # stores if the move checks the opposed king
        "is_capture": [],  # stores is the move actually captures a piece
        "pawnending": [],  # stores if only kings and pawns are left on the board
        "rookending": [],  # stores if only kings, rooks and possible pawns are left on the board
        "attackers": [],
        "attackers_count": [],  # stores the number of possible attacks/threats by the opponent
        "threatened_pieces": [],
        "threatened_pieces_count": [],
        "is_capture_count": [],  # stores the number of possible captures
        "is_castling": [],  # stores if the king has been castled
        "next_move_count": [],  # stores the number of possible moves for the next player
        "guards": [],
        "guards_count": [],
        "guarded_pieces": [],
        "guarded_pieces_count": [],
        "threatened_guarded_pieces": [],
        "threatened_guarded_pieces_count": [],
        "threatened_guarded_pieces_info": [],
        "unopposed_threats_count": []
    }

    # Get the intial board of the game
    board = act_game.board()
    print(board.fen())
    chess_io.export_board_svg(board, filename, len(counts["san"]))

    # Iterate through all moves and play them on a board.
    for move in act_game.mainline_moves():
        # calculate opportunities before applying the move
        actual_move = board.san(move)
        counts["fullmove_number"].append(board.fullmove_number)
        counts["san"].append(actual_move)
        counts["lan"].append(board.lan(move))
        move_cnt = [i for i in board.legal_moves]
        counts["move_count"].append(len(move_cnt))
        counts["is_capture"].append(board.is_capture(move))
        counts["is_castling"].append(board.is_castling(move))
        print("turn: ", board.turn)
        print("actual move: ", board.san(move), move)

        a_score, a_best_move = chess_analysis.compute_score(engine, board)
        a_best_move_score = chess_analysis.compute_best_move_alternative(engine, board, a_best_move)

        # apply move
        board.push(move)

        score = chess_analysis.compute_score_a(engine, board)

        counts["score"].append(score)
        counts["is_check"].append(board.is_check())

        counts["pawnending"].append(chess_analysis.pawn_ending(board.fen()))
        counts["rookending"].append(chess_analysis.rook_ending(board.fen()))

        attack_moves = chess_analysis.compute_attack_moves(board)
        attackers = chess_analysis.get_from_square_pieces(attack_moves)
        counts["attackers"].append(attackers)
        counts["attackers_count"].append(len(attackers))
        threatened_pieces = chess_analysis.get_to_square_pieces(attack_moves)
        counts["threatened_pieces"].append(threatened_pieces)
        counts["threatened_pieces_count"].append(len(threatened_pieces))
        captures = chess_analysis.compute_possible_captures(board)
        counts["is_capture_count"].append(len(captures))

        guard_moves = chess_analysis.compute_guard_moves(board)
        guards = chess_analysis.get_from_square_pieces(guard_moves)
        counts["guards"].append(guards)
        counts["guards_count"].append(len(guards))
        guarded_pieces = chess_analysis.get_to_square_pieces(guard_moves)
        counts["guarded_pieces"].append(guarded_pieces)
        counts["guarded_pieces_count"].append(len(guarded_pieces))

        threatened_guarded_pieces = chess_analysis.compute_attacked_guarded_pieces(attack_moves, guard_moves)
        counts["threatened_guarded_pieces"].append(threatened_guarded_pieces)
        counts["threatened_guarded_pieces_count"].append(len(threatened_guarded_pieces.get('square')))
        # counts["threatened_guarded_pieces_count"].append(len(threatened_pieces) - len(guarded_pieces))
        unopposed_threats = chess_analysis.compute_unopposed_threats(threatened_pieces, guarded_pieces)
        counts["unopposed_threats_count"].append(unopposed_threats)
        print("threatened_pieces:", len(threatened_pieces), "guarded_pieces:", len(guarded_pieces), "tg_pieces:", len(threatened_pieces) - len(guarded_pieces), "unopposed:", unopposed_threats)
        move_cnt = len([i for i in board.legal_moves])
        counts["next_move_count"].append(move_cnt)
        # remove move to calculate the best move as well as the difference between the best move and the actual move
        board.pop()

        nextmovescores = chess_analysis.compute_legal_move_scores(engine, board)

        if len(nextmovescores) > 1:
            # next_scores = [*nextmovescores.keys()]
            # next_scores.sort(reverse=board.turn)
            # print(nextmovescores)
            nextmovescores.sort(key=lambda scores: scores[0], reverse=board.turn)
            # print(nextmovescores)
            best_move = board.san(nextmovescores[0][1])
            counts["best_move"].append(best_move)
            counts["best_move_score"].append(nextmovescores[0][0])
            best_move_score_diff = abs(nextmovescores[0][0] - score)
            counts["best_move_score_diff"].append(best_move_score_diff)
            counts["best_move_score_diff_category"].append(
                chess_analysis.categorize_best_move_score_diff(best_move_score_diff, best_move, actual_move))
        else:
            counts["best_move"].append("-")
            counts["best_move_score"].append(0)
            counts["best_move_score_diff"].append(0)

        # push actual move to the board again
        board.push(move)
        chess_io.export_board_svg(board, filename, len(counts["san"]))
        print('actual_score: ', score, ' alt_score: ', a_score)
        print('actual_best_move: ', best_move, ' best_score: ', nextmovescores[0][0])
        #print('alt_best_move: ', a_best_move, ' alt_best_score: ', a_best_move_score)

        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    SVG(chess.svg.board(board=board, size=400))

    chess_plot.plot_graph(act_game, filename, counts)

    chess_io.write_dict_to_csv(filename, counts)

    return 0


def main():

    engine = chess_analysis.connect_to_stockfish()

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

        print(act_game.headers["Event"] + " / " + act_game.headers["White"] +
              " - " + act_game.headers["Black"] + "  " + act_game.headers["Result"] +
              " / " + act_game.headers["Date"])

        analyse(filename, engine, pgn)


main()
