SELECT * FROM move where game_id = 12
SELECT MAX(ply_number), game_id from move group by game_id order by ply_number
SELECT AVG(score_shift) from move group by ply_number
SELECT game_id from move as a where 
SELECT * FROM move where game_id IN (SELECT max(ply_number), game_id from move as b group by game_id having max(ply_number) < 120)
SELECT avg(score_shift) from move

SELECT SUM(a) FROM (SELECT COUNT(*) as a FROM move where best_move_score_diff >= 90 and best_move_score_diff < 200 GROUP BY ply_number)
SELECT SUM(a) FROM (SELECT COUNT(*) as a FROM move where best_move_score_diff >= 200 GROUP BY ply_number)

SELECT * FROM move where best_move_score_diff >= 90 and best_move_score_diff < 200 GROUP BY ply_number

SELECT COUNT(*) as a FROM move where best_move_score_diff >= 40 and best_move_score_diff < 90