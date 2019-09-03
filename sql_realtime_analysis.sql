SELECT AVG(a0100), AVG(a1000), AVG(a20), AVG(b0100), AVG(b1000), AVG(b20) FROM 
(
SELECT 
MAX(score_a0100) - MIN(score_a0100) as a0100, 
MAX(score_a1000) - MIN(score_a1000) as a1000, 
MAX(score_a20) - MIN(score_a20) as a20, 
MAX(score_b0100) - MIN(score_b0100) as b0100, 
MAX(score_b1000) - MIN(score_b1000) as b1000, 
MAX(score_b20) - MIN(score_b20) as b20
	FROM score
	JOIN move ON score.move_id = move.id
	GROUP BY move.game_id, move.ply_number);
	
SELECT AVG(a0100) FROM 
( SELECT
MAX(score_a0100) - MIN(score_a0100) as a0100
	FROM score
	JOIN move ON score.move_id = move.id
	GROUP BY move.game_id, move.ply_number
);
