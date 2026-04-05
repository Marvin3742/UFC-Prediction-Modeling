DROP TABLE IF EXISTS fighters CASCADE;
DROP TABLE IF EXISTS fights CASCADE;
DROP TABLE IF EXISTS fighter_fights CASCADE;
DROP TABLE IF EXISTS rounds CASCADE;

CREATE TABLE fighters (
	fighter_id SERIAL PRIMARY KEY,
	fighter_name TEXT NOT NULL, 
	height INT, 
	weight INT, 
	reach INT, 
	stance TEXT,
	dob DATE,
	wins INT,
	losses INT,
	draws INT,
	CONSTRAINT unique_fighter
		UNIQUE (fighter_name, height, weight, reach, stance, dob)
);


CREATE TABLE fights (
	fight_id SERIAL PRIMARY KEY,
	event_name TEXT,
	fight_date DATE,
	weight_class TEXT,
	winner TEXT, 
	win_method TEXT, 
	fight_detail TEXT,
	round INT,
	end_time INTERVAL,
	referee TEXT,
	city TEXT,
	state TEXT,
	country TEXT,
	title_bout BOOL,

	CONSTRAINT unique_fight
		UNIQUE (event_name, fight_date, winner, win_method, fight_detail, round, end_time, referee)
);

CREATE TABLE fighter_fights (
	fight_id INT NOT NULL,
	fighter_id INT NOT NULL,
	-- advances INT,
	-- adhg INT,
	-- adtb INT,
	-- adtm INT,
	-- adts INT,
	-- submissions INT, 
	-- slam_rate NUMERIC(4,3) DEFAULT 0.000,
	-- takedowns_slams INT,


	PRIMARY KEY(fighter_id, fight_id),

	FOREIGN KEY (fighter_id)
		REFERENCES fighters(fighter_id)
		ON DELETE CASCADE,

	FOREIGN KEY (fight_id)
		REFERENCES fights(fight_id)
		ON DELETE CASCADE

);

CREATE TABLE rounds(
	fighter_id INT NOT NULL,
	fight_id INT NOT NULL,
	round_number INT NOT NULL,

	kd INT,
	sig_strikes_landed INT DEFAULT 0,
	sig_strikes_attempted INT DEFAULT 0,
	sig_strikes_landed_distance INT DEFAULT 0,
	sig_strikes_attempted_distance INT DEFAULT 0,
	sig_strikes_landed_clinch INT DEFAULT 0,
	sig_strikes_attempted_clinch INT DEFAULT 0,
	sig_strikes_landed_ground INT DEFAULT 0,
	sig_strikes_attempted_ground INT DEFAULT 0,
	sig_strike_percentage NUMERIC(4,3) DEFAULT 0.000,
	total_strikes_landed INT DEFAULT 0,
	total_strikes_attempted INT DEFAULT 0,
	sig_head_strikes_landed INT DEFAULT 0,
	sig_head_strikes_attempted INT DEFAULT 0,
	sig_body_strikes_landed INT DEFAULT 0,
	sig_body_strikes_attempted INT DEFAULT 0,
	sig_leg_strikes_landed INT DEFAULT 0,
	sig_leg_strikes_attempted INT DEFAULT 0,
	takedowns_landed INT DEFAULT 0,
	takedowns_attempted INT DEFAULT 0,
	takedown_percentage NUMERIC(4,3) DEFAULT 0.000,
	submissions_attempted INT DEFAULT 0,
	reversals INT DEFAULT 0,
	control_time INTERVAL,
	
	

	PRIMARY KEY(fighter_id, fight_id, round_number),

	FOREIGN KEY(fighter_id, fight_id)
		REFERENCES fighter_fights(fighter_id, fight_id)
		ON DELETE CASCADE,

	CHECK (round_number >= 1)

);
