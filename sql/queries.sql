-- Feature view for ML model training.
-- Each row is one fight. Rolling stats (slpm, str_acc, etc.) reflect only
-- fights with a lower fight_id than the current fight (retroactive).
-- fight_id is sequential, so this correctly handles same-day fights.
-- Fighters with no prior history have NULL for all rolling stats.
--
-- f1 = the fighter with the lower fighter_id in the pairing (arbitrary but consistent).
-- f2 = the fighter with the higher fighter_id.
-- Use the `winner` column to derive the target label.
--
-- This is a regular view. If query performance is a concern after the database
-- grows, replace CREATE VIEW with CREATE MATERIALIZED VIEW and run
-- REFRESH MATERIALIZED VIEW fight_features after each data load.

DROP VIEW IF EXISTS fight_features;
CREATE VIEW fight_features AS
WITH fight_durations AS (
    SELECT
        fight_id,
        fight_date,
        ((round - 1) * 300.0 + EXTRACT(EPOCH FROM end_time)) / 60.0 AS duration_minutes
    FROM fights
),

-- Aggregate round-level stats to the fight level for each fighter
fighter_fight_totals AS (
    SELECT
        fighter_id,
        fight_id,
        SUM(sig_strikes_landed)    AS sig_landed,
        SUM(sig_strikes_attempted) AS sig_attempted,
        SUM(takedowns_landed)      AS td_landed,
        SUM(takedowns_attempted)   AS td_attempted,
        SUM(submissions_attempted) AS subs_attempted
    FROM rounds
    GROUP BY fighter_id, fight_id
),

-- Per (fighter, fight): own totals + opponent totals + fight duration.
-- This is the source used when computing retroactive rolling averages.
-- Fights with missing round data are excluded (no rows = not counted in history).
fight_data AS (
    SELECT
        mine.fighter_id,
        mine.fight_id,
        fd.fight_date,
        fd.duration_minutes,
        mine.sig_landed,
        mine.sig_attempted,
        mine.td_landed,
        mine.td_attempted,
        mine.subs_attempted,
        opp.sig_landed    AS opp_sig_landed,
        opp.sig_attempted AS opp_sig_attempted,
        opp.td_landed     AS opp_td_landed,
        opp.td_attempted  AS opp_td_attempted
    FROM fighter_fight_totals mine
    JOIN fight_durations fd
        ON fd.fight_id = mine.fight_id
    -- Identify the opponent (always exactly 2 fighters per fight_id)
    JOIN fighter_fights ff_opp
        ON  ff_opp.fight_id   = mine.fight_id
        AND ff_opp.fighter_id != mine.fighter_id
    JOIN fighter_fight_totals opp
        ON  opp.fighter_id = ff_opp.fighter_id
        AND opp.fight_id   = mine.fight_id
),

-- For each (fighter, fight), aggregate all fights strictly before this
-- fight's date to produce retroactive pre-fight statistics.
-- LEFT JOIN ensures fighters entering their first fight still get a row
-- with all NULL stats rather than being dropped.
retroactive AS (
    SELECT
        cur.fighter_id,
        cur.fight_id,

        -- SLpM: significant strikes landed per minute
        CASE WHEN SUM(h.duration_minutes) > 0
             THEN SUM(h.sig_landed) / SUM(h.duration_minutes)
             ELSE NULL END                                              AS slpm,

        -- Str. Acc.: sig strikes landed / sig strikes attempted
        CASE WHEN SUM(h.sig_attempted) > 0
             THEN SUM(h.sig_landed)::NUMERIC / SUM(h.sig_attempted)
             ELSE NULL END                                              AS str_acc,

        -- SApM: significant strikes absorbed per minute (opponent's landed)
        CASE WHEN SUM(h.duration_minutes) > 0
             THEN SUM(h.opp_sig_landed) / SUM(h.duration_minutes)
             ELSE NULL END                                              AS sapm,

        -- Str. Def.: % of opponent's sig strikes that did NOT land
        CASE WHEN SUM(h.opp_sig_attempted) > 0
             THEN (SUM(h.opp_sig_attempted) - SUM(h.opp_sig_landed))::NUMERIC
                  / SUM(h.opp_sig_attempted)
             ELSE NULL END                                              AS str_def,

        -- TD Avg.: takedowns landed per 15 minutes
        CASE WHEN SUM(h.duration_minutes) > 0
             THEN SUM(h.td_landed) / SUM(h.duration_minutes) * 15
             ELSE NULL END                                              AS td_avg,

        -- TD Acc.: takedowns landed / takedowns attempted
        CASE WHEN SUM(h.td_attempted) > 0
             THEN SUM(h.td_landed)::NUMERIC / SUM(h.td_attempted)
             ELSE NULL END                                              AS td_acc,

        -- TD Def.: % of opponent's TD attempts that did NOT land
        CASE WHEN SUM(h.opp_td_attempted) > 0
             THEN (SUM(h.opp_td_attempted) - SUM(h.opp_td_landed))::NUMERIC
                  / SUM(h.opp_td_attempted)
             ELSE NULL END                                              AS td_def,

        -- Sub Avg.: submission attempts per 15 minutes
        CASE WHEN SUM(h.duration_minutes) > 0
             THEN SUM(h.subs_attempted) / SUM(h.duration_minutes) * 15
             ELSE NULL END                                              AS sub_avg

    FROM fighter_fights cur
    LEFT JOIN fight_data h
        ON  h.fighter_id = cur.fighter_id
        AND h.fight_id   < cur.fight_id
    GROUP BY cur.fighter_id, cur.fight_id
),

-- For each (fighter, fight), count wins/losses/draws from all prior fights.
-- winner = 'Draw' means a draw; winner = fighter_name means a win; anything
-- else where winner IS NOT NULL is a loss.
-- Debut fighters get 0/0/0 (factually correct, unlike the NULL rolling stats).
fighter_record AS (
    SELECT
        cur.fighter_id,
        cur.fight_id,
        COUNT(*) FILTER (
            WHERE f_hist.winner = fi.fighter_name
        )                                                               AS wins,
        COUNT(*) FILTER (
            WHERE f_hist.winner IS NOT NULL
              AND f_hist.winner != 'Draw'
              AND f_hist.winner != fi.fighter_name
        )                                                               AS losses,
        COUNT(*) FILTER (
            WHERE f_hist.winner = 'Draw'
        )                                                               AS draws
    FROM fighter_fights cur
    JOIN fighters fi ON fi.fighter_id = cur.fighter_id
    LEFT JOIN fighter_fights ff_hist
        ON  ff_hist.fighter_id = cur.fighter_id
        AND ff_hist.fight_id   < cur.fight_id
    LEFT JOIN fights f_hist ON f_hist.fight_id = ff_hist.fight_id
    GROUP BY cur.fighter_id, cur.fight_id
),

-- Assign fighter labels consistently: f1 = lower fighter_id, f2 = higher
fighter_pairs AS (
    SELECT
        fight_id,
        MIN(fighter_id) AS f1_id,
        MAX(fighter_id) AS f2_id
    FROM fighter_fights
    GROUP BY fight_id
)

SELECT
    -- Fight metadata
    f.fight_id,
    f.event_name,
    f.fight_date,
    f.weight_class,
    f.title_bout,
    f.winner,
    f.win_method,

    -- Fighter 1 basic info
    fi1.fighter_id   AS f1_fighter_id,
    fi1.fighter_name AS f1_name,
    fi1.height       AS f1_height,
    fi1.weight       AS f1_weight,
    fi1.reach        AS f1_reach,
    fi1.stance       AS f1_stance,
    fi1.dob          AS f1_dob,

    -- Fighter 1 pre-fight record
    rec1.wins        AS f1_wins,
    rec1.losses      AS f1_losses,
    rec1.draws       AS f1_draws,

    -- Fighter 1 pre-fight rolling stats
    r1.slpm          AS f1_slpm,
    r1.str_acc       AS f1_str_acc,
    r1.sapm          AS f1_sapm,
    r1.str_def       AS f1_str_def,
    r1.td_avg        AS f1_td_avg,
    r1.td_acc        AS f1_td_acc,
    r1.td_def        AS f1_td_def,
    r1.sub_avg       AS f1_sub_avg,

    -- Fighter 2 basic info
    fi2.fighter_id   AS f2_fighter_id,
    fi2.fighter_name AS f2_name,
    fi2.height       AS f2_height,
    fi2.weight       AS f2_weight,
    fi2.reach        AS f2_reach,
    fi2.stance       AS f2_stance,
    fi2.dob          AS f2_dob,

    -- Fighter 2 pre-fight record
    rec2.wins        AS f2_wins,
    rec2.losses      AS f2_losses,
    rec2.draws       AS f2_draws,

    -- Fighter 2 pre-fight rolling stats
    r2.slpm          AS f2_slpm,
    r2.str_acc       AS f2_str_acc,
    r2.sapm          AS f2_sapm,
    r2.str_def       AS f2_str_def,
    r2.td_avg        AS f2_td_avg,
    r2.td_acc        AS f2_td_acc,
    r2.td_def        AS f2_td_def,
    r2.sub_avg       AS f2_sub_avg

FROM fights f
JOIN fighter_pairs fp ON fp.fight_id    = f.fight_id
JOIN fighters fi1     ON fi1.fighter_id = fp.f1_id
JOIN fighters fi2     ON fi2.fighter_id = fp.f2_id
JOIN retroactive r1      ON r1.fighter_id   = fp.f1_id AND r1.fight_id = f.fight_id
JOIN retroactive r2      ON r2.fighter_id   = fp.f2_id AND r2.fight_id = f.fight_id
JOIN fighter_record rec1 ON rec1.fighter_id = fp.f1_id AND rec1.fight_id = f.fight_id
JOIN fighter_record rec2 ON rec2.fighter_id = fp.f2_id AND rec2.fight_id = f.fight_id
ORDER BY f.fight_date, f.fight_id;
