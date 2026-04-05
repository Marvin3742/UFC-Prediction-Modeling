WITH prior_fight_stats AS (
    SELECT
        r.fighter_id,
        r.fight_id,
        SUM(r.sig_strikes_landed)    AS ssl,
        SUM(r.sig_strikes_attempted) AS ssa,
        SUM(r.takedowns_landed)      AS tdl,
        SUM(r.takedowns_attempted)   AS tda,
        SUM(r.submissions_attempted) AS suba,
        SUM(
            CASE
                WHEN f.round = r.round_number
                THEN EXTRACT(EPOCH FROM f.end_time) / 60.0
                ELSE 5.0
            END
        ) AS fight_minutes
    FROM rounds r
    JOIN fights f ON r.fight_id = f.fight_id
    GROUP BY r.fighter_id, r.fight_id
	ORDER BY r.fight_id
),

opponent_fight_stats AS (
    SELECT
        ff_self.fighter_id,
        ff_self.fight_id,
        SUM(r.sig_strikes_landed)    AS opp_ssl,
        SUM(r.sig_strikes_attempted) AS opp_ssa,
        SUM(r.takedowns_landed)      AS opp_tdl,
        SUM(r.takedowns_attempted)   AS opp_tda
    FROM fighter_fights ff_self
    JOIN fighter_fights ff_opp ON ff_opp.fight_id = ff_self.fight_id
                               AND ff_opp.fighter_id <> ff_self.fighter_id
    JOIN rounds r ON r.fighter_id = ff_opp.fighter_id
                 AND r.fight_id = ff_opp.fight_id
    GROUP BY ff_self.fighter_id, ff_self.fight_id
	order by ff_self.fight_id
),
fighter_temp AS (
    SELECT ff.fighter_id, current_f.*, pfs.ssl, pfs.ssa, pfs.tdl, pfs.tda, pfs.suba, pfs.fight_minutes
    FROM fighter_fights ff
    JOIN fights current_f  ON ff.fight_id = current_f.fight_id
    JOIN prior_fight_stats pfs ON pfs.fighter_id = ff.fighter_id and pfs.fight_id = ff.fight_id
)
-- select * from fighter_temp
,

fighter_prior_stats AS (
	SELECT 
		fighter_id, fight_id, 
		SUM(ssl) OVER (
			PARTITION BY fighter_id
			ORDER BY fight_id
			ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
		) AS prev_strikes_landed,

		SUM(ssa) OVER(
			PARTITION BY fighter_id
			ORDER BY fight_id
			ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
			) AS prev_strikes_absorbed,
			
		SUM(tdl) OVER (
			PARTITION BY fighter_id
			ORDER BY fight_id
			ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
		) AS prev_takedowns_landed,

		SUM(tda) OVER(
			PARTITION BY fighter_id
			ORDER BY fight_id
			ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
			) AS prev_takedowns_attempted,
			
		SUM(suba) OVER (
			PARTITION BY fighter_id
			ORDER BY fight_id
			ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
		) AS prev_submissions_attempted,

		SUM(fight_minutes) OVER(
			PARTITION BY fighter_id
			ORDER BY fight_id
			ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
			) AS prev_total_minutes
			
	FROM fighter_temp
	ORDER BY fight_id
)
select * from fighter_prior_stats
group by fighter_prior_stats.fighter_id
,
opponent_prior_stats AS (
	select 
	fighter_id, 
	current_fight_id
	-- prev_ssl, prev_ssa, prev_tdl, prev_tda, prev_suba, prev_total_minutes
	from(
	    SELECT *
	    FROM fighter_fights ff
	    JOIN fights current_f  ON ff.fight_id = current_f.fight_id
	    JOIN opponent_fight_stats ofs ON ofs.fighter_id = ff.fighter_id and ofs.fight_id = ff.fight_id
		)
)
select * from opponent
,

fighter_stats AS (
    SELECT
        fps.fighter_id,
        fps.current_fight_id                                                           AS fight_id,
        ROUND((fps.ssl::NUMERIC  / NULLIF(fps.total_minutes, 0)), 3)                  AS slpm,
        ROUND((fps.ssl::NUMERIC  / NULLIF(fps.ssa::NUMERIC, 0)), 3)                   AS str_acc,
        ROUND((ops.opp_ssl::NUMERIC / NULLIF(fps.total_minutes, 0)), 3)               AS sapm,
        ROUND((1 - ops.opp_ssl::NUMERIC / NULLIF(ops.opp_ssa::NUMERIC, 0)), 3)        AS str_def,
        ROUND((fps.tdl::NUMERIC  / NULLIF(fps.total_minutes, 0) * 15), 3)             AS td_avg,
        ROUND((fps.tdl::NUMERIC  / NULLIF(fps.tda::NUMERIC, 0)), 3)                   AS td_acc,
        ROUND((1 - ops.opp_tdl::NUMERIC / NULLIF(ops.opp_tda::NUMERIC, 0)), 3)        AS td_def,
        ROUND((fps.suba::NUMERIC / NULLIF(fps.total_minutes, 0) * 15), 3)             AS sub_avg
    FROM fighter_prior_stats fps
    LEFT JOIN opponent_prior_stats ops
           ON fps.fighter_id = ops.fighter_id
          AND fps.current_fight_id = ops.current_fight_id
)
SELECT
    f.*,

    fa.fighter_id      AS fighter_a_id,
    fa.fighter_name    AS fighter_a_name,
    fa.height          AS fighter_a_height,
    fa.weight          AS fighter_a_weight,
    fa.reach           AS fighter_a_reach,
    fa.stance          AS fighter_a_stance,
    fa.dob             AS fighter_a_dob,
    fa.wins            AS fighter_a_wins,
    fa.losses          AS fighter_a_losses,
    fa.draws           AS fighter_a_draws,

    sa.slpm            AS fighter_a_slpm,
    sa.str_acc         AS fighter_a_str_acc,
    sa.sapm            AS fighter_a_sapm,
    sa.str_def         AS fighter_a_str_def,
    sa.td_avg          AS fighter_a_td_avg,
    sa.td_acc          AS fighter_a_td_acc,
    sa.td_def          AS fighter_a_td_def,
    sa.sub_avg         AS fighter_a_sub_avg,

    fb.fighter_id      AS fighter_b_id,
    fb.fighter_name    AS fighter_b_name,
    fb.height          AS fighter_b_height,
    fb.weight          AS fighter_b_weight,
    fb.reach           AS fighter_b_reach,
    fb.stance          AS fighter_b_stance,
    fb.dob             AS fighter_b_dob,
    fb.wins            AS fighter_b_wins,
    fb.losses          AS fighter_b_losses,
    fb.draws           AS fighter_b_draws,

    sb.slpm            AS fighter_b_slpm,
    sb.str_acc         AS fighter_b_str_acc,
    sb.sapm            AS fighter_b_sapm,
    sb.str_def         AS fighter_b_str_def,
    sb.td_avg          AS fighter_b_td_avg,
    sb.td_acc          AS fighter_b_td_acc,
    sb.td_def          AS fighter_b_td_def,
    sb.sub_avg         AS fighter_b_sub_avg

FROM fights f
JOIN fighter_fights ffa  ON f.fight_id = ffa.fight_id
JOIN fighters fa         ON ffa.fighter_id = fa.fighter_id
JOIN fighter_fights ffb  ON f.fight_id = ffb.fight_id
JOIN fighters fb         ON ffb.fighter_id = fb.fighter_id
LEFT JOIN fighter_stats sa ON sa.fighter_id = fa.fighter_id AND sa.fight_id = f.fight_id
LEFT JOIN fighter_stats sb ON sb.fighter_id = fb.fighter_id AND sb.fight_id = f.fight_id
WHERE fa.fighter_id < fb.fighter_id
ORDER BY f.fight_date, f.fight_id;