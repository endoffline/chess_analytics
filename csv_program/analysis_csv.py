import chess
from IPython.display import SVG
from lib import chess_analysis, chess_io
import chess_plot


def main():
    engine = chess_analysis.connect_to_stockfish()

    # Open PGN file
    # filename = "kasparov_karpov_1986"
    # filename = "kramnik_leko_2001"
    # filename = "dariushmoalemi_grumpy123us_2018"
    # filename = "tissir_dreev_2004"
    # filename = "short_vaganian_1989"
    # filename = "smyslov_h_donner_1967"
    filename = "capablanca_alekhine_1927"

    chess_io.init_folder_structure(filename)  # prepare folder structure for output
    pgn = chess_io.open_pgn(filename)

    act_game = chess_analysis.read_game(pgn)

    print(act_game.headers["Event"] + " / " + act_game.headers["White"] +
          " - " + act_game.headers["Black"] + "  " + act_game.headers["Result"] +
          " / " + act_game.headers["Date"])

    counts = {
        "fullmove_number": [],  # stores the move numbers
        "ply_number": [],  # number of plies
        "turn": [],  # White = True, Black = False
        "san": [],  # stores a move in Standard Algebraic Notation (SAN)
        "lan": [],  # stores a move in Long Algebraic Notation (LAN)
        "score": [],  # stores the scores calculated by Stockfish
        "score_change": [],  # stores the change of scores between the current and previous move
        "score_change_category": [],  # stores the significance of the score change
        "move_count": [],  # stores the number of possible moves in this turn
        "best_move": [],  # stores the best move in SAN
        "best_move_score": [],  # stores the best move's score
        "best_move_score_diff": [],  # stores the difference between the calculated best move and the actual move
        "best_move_score_diff_category": [],  # stores the category for the calculated difference
        "is_check": [],  # stores if the move checks the opposed king
        "is_capture": [],  # stores is the move actually captures a piece
        "is_castling": [],  # stores if the king has been castled
        "possible_moves_count": [],  # stores the number of possible moves for the next player
        "possible_moves_quality": [],  # stores the probability of move to improve the Stockfish evaluation
        "captures": [],  # stores the squares for every possible capture
        "is_capture_count": [],  # stores the number of possible captures
        "is_capture_weighted": [],  # stores the centipawn value for the possible captures

        "attackers_white": [],  # stores the square names for the pieces that attack White
        "attackers_count_white": [],  # stores the number of attacks by the opponent
        "attacked_pieces_white": [],  # stores the square names for the pieces attackd by the opponent
        "attacked_pieces_count_white": [],  # stores the number of attacked squares for White
        "guards_white": [],  # stores the squares of white pieces that guard other white pieces
        "guards_count_white": [],
        "guarded_pieces_white": [],  # stores the squares guarded by white pieces
        "guarded_pieces_count_white": [],
        "attacked_guarded_pieces_white": [],  # stores the squares, which are guarded by a white piece and attacked by a black piece
        "attacked_guarded_pieces_count_white": [],
        "unopposed_threats_white": [],  # stores the squares for undefended threatened pieces for white
        "unopposed_threats_count_white": [],
        "threats_count_white": [],  # stores the number of threats threatening white pieces
        "forking_pieces_white": [],  # stores the squares for white pieces that create forks
        "fork_count_white": [],  # stores the number of white pieces that create forks
        "pin_count_white": [],  # stores the number of pins that attack white
        "skewer_count_white": [],  # stores the number of skewers that attack white
        "attackers_black": [],
        "attackers_count_black": [],  # stores the number of possible attacks/threats by the opponent
        "attacked_pieces_black": [],
        "attacked_pieces_count_black": [],
        "guards_black": [],
        "guards_count_black": [],
        "guarded_pieces_black": [],
        "guarded_pieces_count_black": [],
        "attacked_guarded_pieces_black": [],
        "attacked_guarded_pieces_count_black": [],
        "unopposed_threats_black": [],
        "unopposed_threats_count_black": [],
        "threats_count_black": [],
        "forking_pieces_black": [],
        "fork_count_black": [],
        "pin_count_black": [],
        "skewer_count_black": [],

        "attackers_centipawn_white": [],
        "attacked_pieces_centipawn_white": [],
        "guards_centipawn_white": [],
        "guarded_pieces_centipawn_white": [],
        "attacked_guarded_pieces_centipawn_white": [],
        "unopposed_threats_centipawn_white": [],
        "threats_centipawn_white": [],

        "attackers_centipawn_black": [],
        "attacked_pieces_centipawn_black": [],
        "guards_centipawn_black": [],
        "guarded_pieces_centipawn_black": [],
        "attacked_guarded_pieces_centipawn_black": [],
        "unopposed_threats_centipawn_black": [],
        "threats_centipawn_black": [],

        "attackers_count_all": [],
        "attacked_pieces_count_all": [],
        "guards_count_all": [],
        "guarded_pieces_count_all": [],
        "attacked_guarded_pieces_count_all": [],
        "unopposed_threats_count_all": [],
        "threats_count_all": [],
        "fork_count_all": [],
        "pin_count_all": [],
        "skewer_count_all": [],

        "attacked_pieces_centipawn_all": [],
        "guarded_pieces_centipawn_all": [],
        "attacked_guarded_pieces_centipawn_all": [],
        "unopposed_threats_centipawn_all": [],
        "threats_centipawn_all": [],  # stores and compares the centipawn values of threats for black and white
        "attack_defense_relation1": [],  # stores the centipawn value of all in attacks involved pieces
        "attack_defense_relation2": [],
        "material": [],  # stores the centipawn value for all remaining pieces on the board and compares the two sides
        "pawn_ending": [],  # stores if only kings and pawns are left on the board
        "rook_ending": [],  # stores if only kings, rooks and possible pawns are left on the board
    }

    time = 0.100

    # Get the intial board of the game
    board = act_game.board()
    print(board.fen())
    chess_io.export_board_svg(board, filename, len(counts["san"]), None)
    prev_score = 0
    score_change = 0
    score = 0
    best_move = None
    next_best_move = None

    # Iterate through all moves and play them on a board.
    for ply_number, mv in enumerate(act_game.mainline_moves(), start=1):
        print("ply: ", ply_number)
        # calculate opportunities before applying the move
        fullmove_number = board.fullmove_number
        turn = board.turn
        san = board.san(mv)
        lan = board.lan(mv)
        move_count = chess_analysis.compute_move_count(board)
        is_capture = board.is_capture(mv)
        is_capture_weighted = chess_analysis.compute_is_capture_weighted(board, mv)
        is_castling = board.is_castling(mv)

        if best_move is None:  # calculate best move for first turn
            not_needed, best_move = chess_analysis.compute_score(engine, board, time)
        best_move_score = chess_analysis.compute_best_move_score(engine, board, best_move, time)

        best_move = board.san(best_move)

        # apply move
        board.push(mv)
        score, next_best_move = chess_analysis.compute_score(engine, board, time)
        score_change = chess_analysis.compute_score_change(prev_score, score)
        score_change_category = chess_analysis.compute_score_change_category(score_change)
        best_move_score_diff = abs(best_move_score - score)
        best_move_score_diff_category = chess_analysis.categorize_best_move_score_diff(best_move_score_diff,
                                                                                       best_move, san)

        is_check = board.is_check()
        possible_moves_count = chess_analysis.compute_move_count(board)
        possible_moves_quality = chess_analysis.compute_possible_moves_quality(engine, board, time, score)
        captures = chess_analysis.compute_possible_captures(board)
        captures = chess_analysis.get_to_square_pieces(captures)
        is_capture_count = len(captures)

        # White player
        attack_moves_white = chess_analysis.compute_attack_moves(board, chess.BLACK)
        attackers_white = chess_analysis.get_from_square_pieces(attack_moves_white)
        attackers_count_white = len(attackers_white)
        attacked_pieces_white = list(set(chess_analysis.get_to_square_pieces(attack_moves_white)))
        attacked_pieces_count_white = len(attacked_pieces_white)
        guard_moves_white = chess_analysis.compute_guard_moves(board, chess.WHITE)
        guards_white = chess_analysis.get_from_square_pieces(guard_moves_white)
        guards_count_white = len(guards_white)
        guarded_pieces_white = list(set(chess_analysis.get_to_square_pieces(guard_moves_white)))
        guarded_pieces_count_white = len(guarded_pieces_white)
        attacked_guarded_pieces_white = chess_analysis.compute_attacked_guarded_pieces(attack_moves_white,
                                                                                       guard_moves_white)
        attacked_guarded_pieces_count_white = len(attacked_guarded_pieces_white)
        unopposed_threats_white = chess_analysis.compute_unopposed_threats(attacked_pieces_white, guarded_pieces_white)
        unopposed_threats_count_white = len(unopposed_threats_white)
        forking_pieces_white = chess_analysis.compute_forks(board, chess.WHITE)
        fork_count_white = len(forking_pieces_white)
        pin_moves_white, skewer_moves_white = chess_analysis.compute_xray_attack_moves(board, chess.WHITE)
        pin_count_white = len(pin_moves_white)
        skewer_count_white = len(skewer_moves_white)
        threats_weighted_count_white = len(chess_analysis.compute_threat_moves_weighted(board, attack_moves_white,
                                                                                    attacked_guarded_pieces_white))

        # Black player
        attack_moves_black = chess_analysis.compute_attack_moves(board, chess.WHITE)
        attackers_black = chess_analysis.get_from_square_pieces(attack_moves_black)
        attackers_count_black = len(attackers_black)
        attacked_pieces_black = list(set(chess_analysis.get_to_square_pieces(attack_moves_black)))
        attacked_pieces_count_black = len(attacked_pieces_black)
        guard_moves_black = chess_analysis.compute_guard_moves(board, chess.BLACK)
        guards_black = chess_analysis.get_from_square_pieces(guard_moves_black)
        guards_count_black = len(guards_black)
        guarded_pieces_black = list(set(chess_analysis.get_to_square_pieces(guard_moves_black)))
        guarded_pieces_count_black = len(guarded_pieces_black)
        attacked_guarded_pieces_black = chess_analysis.compute_attacked_guarded_pieces(attack_moves_black,
                                                                                       guard_moves_black)
        attacked_guarded_pieces_count_black = len(attacked_guarded_pieces_black)
        unopposed_threats_black = chess_analysis.compute_unopposed_threats(attacked_pieces_black, guarded_pieces_black)
        unopposed_threats_count_black = len(unopposed_threats_black)
        forking_pieces_black = chess_analysis.compute_forks(board, chess.BLACK)
        fork_count_black = len(forking_pieces_black)
        pin_moves_black, skewer_moves_black = chess_analysis.compute_xray_attack_moves(board, chess.BLACK)
        pin_count_black = len(pin_moves_black)
        skewer_count_black = len(skewer_moves_black)
        threats_weighted_count_black = len(
            chess_analysis.compute_threat_moves_weighted(board, attack_moves_black, attacked_guarded_pieces_black))

        attackers_centipawn_white = chess_analysis.get_pieces_centipawn_sum(board, attackers_white)
        attacked_pieces_centipawn_white = chess_analysis.get_pieces_centipawn_sum(board, attacked_pieces_white)
        guards_centipawn_white = chess_analysis.get_pieces_centipawn_sum(board, guards_white)
        guarded_pieces_centipawn_white = chess_analysis.get_pieces_centipawn_sum(board, guarded_pieces_white)
        attacked_guarded_pieces_centipawn_white = chess_analysis.get_pieces_centipawn_sum(board,
                                                                                          attacked_guarded_pieces_white)
        unopposed_threats_centipawn_white = chess_analysis.get_pieces_centipawn_sum(board, unopposed_threats_white)
        threats_centipawn_white = chess_analysis.compute_threats_weighted(board, attack_moves_white,
                                                                         attacked_guarded_pieces_white)
        attackers_centipawn_black = chess_analysis.get_pieces_centipawn_sum(board, attackers_black)
        attacked_pieces_centipawn_black = chess_analysis.get_pieces_centipawn_sum(board, attacked_pieces_black)
        guards_centipawn_black = chess_analysis.get_pieces_centipawn_sum(board, guards_black)
        guarded_pieces_centipawn_black = chess_analysis.get_pieces_centipawn_sum(board, guarded_pieces_black)
        attacked_guarded_pieces_centipawn_black = chess_analysis.get_pieces_centipawn_sum(board,
                                                                                          attacked_guarded_pieces_black)
        unopposed_threats_centipawn_black = chess_analysis.get_pieces_centipawn_sum(board, unopposed_threats_black)
        threats_centipawn_black = chess_analysis.compute_threats_weighted(board, attack_moves_black,
                                                                         attacked_guarded_pieces_black)

        attack_defense_relation1 = chess_analysis.compute_attack_defense_relation_centipawn1(board)
        attack_defense_relation2 = chess_analysis.compute_attack_defense_relation_centipawn2(guards_centipawn_white,
                                                                                             guarded_pieces_centipawn_white,
                                                                                             attacked_pieces_centipawn_white,
                                                                                             attackers_centipawn_white,
                                                                                             guards_centipawn_black,
                                                                                             guarded_pieces_centipawn_black,
                                                                                             attacked_pieces_centipawn_black,
                                                                                             attackers_centipawn_black)
        material = chess_analysis.compute_material_centipawn(board)
        pawn_ending = chess_analysis.compute_pawn_ending(board)
        rook_ending = chess_analysis.compute_rook_ending(board)



        # append parameters to the arrays
        counts["fullmove_number"].append(fullmove_number)
        counts["ply_number"].append(ply_number)
        counts["turn"].append(turn)
        counts["san"].append(san)
        counts["lan"].append(lan)
        counts["score"].append(score)
        counts["score_change"].append(score_change)
        counts["score_change_category"].append(score_change_category)
        counts["move_count"].append(move_count)
        counts["best_move"].append(best_move)
        counts["best_move_score"].append(best_move_score)
        counts["best_move_score_diff"].append(best_move_score_diff)
        counts["best_move_score_diff_category"].append(best_move_score_diff_category)
        counts["is_check"].append(is_check)
        counts["is_capture"].append(is_capture)
        counts["is_castling"].append(is_castling)
        counts["possible_moves_count"].append(possible_moves_count)
        counts["possible_moves_quality"].append(possible_moves_quality/(possible_moves_count if possible_moves_count > 0 else 1))
        counts["captures"].append(', '.join(str(s) for s in chess_analysis.get_square_names(captures)))
        counts["is_capture_count"].append(is_capture_count)
        counts["is_capture_weighted"].append(is_capture_weighted)
        counts["attackers_white"].append(', '.join(str(s) for s in chess_analysis.get_square_names(attackers_white)))
        counts["attackers_count_white"].append(attackers_count_white)
        counts["attacked_pieces_white"].append(
            ', '.join(str(s) for s in chess_analysis.get_square_names(attacked_pieces_white)))
        counts["attacked_pieces_count_white"].append(attacked_pieces_count_white)
        counts["guards_white"].append(', '.join(str(s) for s in chess_analysis.get_square_names(guards_white)))
        counts["guards_count_white"].append(guards_count_white)
        counts["guarded_pieces_white"].append(
            ', '.join(str(s) for s in chess_analysis.get_square_names(guarded_pieces_white)))
        counts["guarded_pieces_count_white"].append(guarded_pieces_count_white)
        counts["attacked_guarded_pieces_white"].append(
            ', '.join(str(s) for s in chess_analysis.get_square_names(attacked_guarded_pieces_white)))
        counts["attacked_guarded_pieces_count_white"].append(attacked_guarded_pieces_count_white)
        counts["unopposed_threats_white"].append(
            ', '.join(str(s) for s in chess_analysis.get_square_names(unopposed_threats_white)))
        counts["unopposed_threats_count_white"].append(unopposed_threats_count_white)
        counts["threats_count_white"].append(threats_weighted_count_white)
        counts["forking_pieces_white"].append(', '.join(str(s) for s in chess_analysis.get_square_names(forking_pieces_white)))
        counts["fork_count_white"].append(fork_count_white)
        counts["pin_count_white"].append(pin_count_white)
        counts["skewer_count_white"].append(skewer_count_white)

        counts["attackers_black"].append(', '.join(str(s) for s in chess_analysis.get_square_names(attackers_black)))
        counts["attackers_count_black"].append(attackers_count_black)
        counts["attacked_pieces_black"].append(
            ', '.join(str(s) for s in chess_analysis.get_square_names(attacked_pieces_black)))
        counts["attacked_pieces_count_black"].append(attacked_pieces_count_black)
        counts["guards_black"].append(', '.join(str(s) for s in chess_analysis.get_square_names(guards_black)))
        counts["guards_count_black"].append(guards_count_black)
        counts["guarded_pieces_black"].append(
            ', '.join(str(s) for s in chess_analysis.get_square_names(guarded_pieces_black)))
        counts["guarded_pieces_count_black"].append(guarded_pieces_count_black)
        counts["attacked_guarded_pieces_black"].append(
            ', '.join(str(s) for s in chess_analysis.get_square_names(attacked_guarded_pieces_black)))
        counts["attacked_guarded_pieces_count_black"].append(attacked_guarded_pieces_count_black)
        counts["unopposed_threats_black"].append(
            ', '.join(str(s) for s in chess_analysis.get_square_names(unopposed_threats_black)))
        counts["unopposed_threats_count_black"].append(unopposed_threats_count_black)
        counts["threats_count_black"].append(threats_weighted_count_black)
        counts["forking_pieces_black"].append(', '.join(str(s) for s in chess_analysis.get_square_names(forking_pieces_black)))
        counts["fork_count_black"].append(fork_count_black)
        counts["pin_count_black"].append(pin_count_black)
        counts["skewer_count_black"].append(skewer_count_black)

        counts["attackers_centipawn_white"].append(attackers_centipawn_white)
        counts["attacked_pieces_centipawn_white"].append(attacked_pieces_centipawn_white)
        counts["guards_centipawn_white"].append(guards_centipawn_white)
        counts["guarded_pieces_centipawn_white"].append(guarded_pieces_centipawn_white)
        counts["attacked_guarded_pieces_centipawn_white"].append(attacked_guarded_pieces_centipawn_white)
        counts["unopposed_threats_centipawn_white"].append(unopposed_threats_centipawn_white)
        counts["threats_centipawn_white"].append(threats_centipawn_white)
        counts["attackers_centipawn_black"].append(attackers_centipawn_black)
        counts["attacked_pieces_centipawn_black"].append(attacked_pieces_centipawn_black)
        counts["guards_centipawn_black"].append(guards_centipawn_black)
        counts["guarded_pieces_centipawn_black"].append(guarded_pieces_centipawn_black)
        counts["attacked_guarded_pieces_centipawn_black"].append(attacked_guarded_pieces_centipawn_black)
        counts["unopposed_threats_centipawn_black"].append(unopposed_threats_centipawn_black)
        counts["threats_centipawn_black"].append(threats_centipawn_black)

        counts["attackers_count_all"].append(attackers_count_white + attackers_count_black)
        counts["attacked_pieces_count_all"].append(attacked_pieces_count_white + attacked_pieces_count_black)
        counts["guards_count_all"].append(guards_count_white + guards_count_black)
        counts["guarded_pieces_count_all"].append(guarded_pieces_count_white + guarded_pieces_count_black)
        counts["attacked_guarded_pieces_count_all"].append(
            attacked_guarded_pieces_count_white + attacked_guarded_pieces_count_black)
        counts["unopposed_threats_count_all"].append(unopposed_threats_count_white + unopposed_threats_count_black)
        counts["threats_count_all"].append(threats_weighted_count_white + threats_weighted_count_black)
        counts["fork_count_all"].append(fork_count_white + fork_count_black)
        counts["pin_count_all"].append(pin_count_white + pin_count_black)
        counts["skewer_count_all"].append(skewer_count_white + skewer_count_black)
        counts["attacked_pieces_centipawn_all"].append(
            attacked_pieces_centipawn_white + attacked_pieces_centipawn_black)
        counts["guarded_pieces_centipawn_all"].append(guarded_pieces_centipawn_white + guarded_pieces_centipawn_black)
        counts["attacked_guarded_pieces_centipawn_all"].append(
            attacked_guarded_pieces_centipawn_white + attacked_guarded_pieces_centipawn_black)
        counts["unopposed_threats_centipawn_all"].append(
            unopposed_threats_centipawn_white + unopposed_threats_centipawn_black)
        counts["threats_centipawn_all"].append(threats_centipawn_white - threats_centipawn_black)
        counts["attack_defense_relation1"].append(attack_defense_relation1)
        counts["attack_defense_relation2"].append(attack_defense_relation2)
        counts["material"].append(material)
        counts["pawn_ending"].append(pawn_ending)
        counts["rook_ending"].append(rook_ending)

        chess_io.export_board_svg(board, filename, len(counts["san"]), mv)
        print('actual_score: ', score)
        print('actual_best_move: ', best_move, ' best_score: ', best_move_score)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        best_move = next_best_move
        prev_score = score

    SVG(chess.svg.board(board=board, size=400))

    chess_plot.plot_graph(act_game, filename, counts)
    chess_io.write_dict_to_csv(filename, counts)
    engine.quit()
    return 0


main()
