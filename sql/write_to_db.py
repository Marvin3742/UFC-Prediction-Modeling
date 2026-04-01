import pandas as pd
import psycopg2

def write_to_fighters(csv_file):
  df = pd.read_csv(csv_file)
  conn = psycopg2.connect(
      dbname="ufc_fighter_db",
      user="postgres",
      password="347824Mg",
      host="localhost",
      port=5432
  )
  print("DB connection successful!")
  cur = conn.cursor()

  for _, row in df.iterrows():
    cur.execute(
      """
        INSERT INTO fighters(fighter_name, height, weight, reach, stance, dob, wins, losses, draws)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
      """,
      (row['fighter_name'], row['height'], row['weight'], row['reach'], row['stance'], row['dob'], row["wins"], row["losses"], row["draws"])
    )
  conn.commit()
  cur.close()
  conn.close()
  print("Values inserted into fighters table!")

def write_to_fights(csv_file):
  df = pd.read_csv(csv_file)
  conn = psycopg2.connect(
      dbname="ufc_fighter_db",
      user="postgres",
      password="347824Mg",
      host="localhost",
      port=5432
  )
  print("DB connection successful!")
  cur = conn.cursor()
  for _, row in df.iterrows():
    cur.execute(
      """
        INSERT INTO fights(event_name, fight_date, weight_class, winner, win_method, fight_detail, round, end_time, referee, city, state, country, title_bout)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
      """,
      (row['event_name'], row['fight_date'], row['weight_class'], row['winner'], row['win_method'], row['detail'], row['round'], row['end_time'], row['referee'], row['city'], row['state'], row['country'], row['title_bout'])
    )

  conn.commit()
  cur.close()
  conn.close()
  print("Values inserted into fights table!")


def write_to_fighter_fights(csv_file):
  df = pd.read_csv(csv_file)
  conn = psycopg2.connect(
    dbname='ufc_fighter_db',
    user='postgres',
    password='347824Mg',
    host='localhost',
    port=5432
  )
  print('Db connection successful!')
  cur = conn.cursor()
  for _, row in df.iterrows():
    cur.execute(
      """
        INSERT INTO fighter_fights(fight_id, fighter_id)
        VALUES (%s, %s)
      """,
      (int(row["fight_id"]), int(row['fighter_id']))
    )
  conn.commit()
  cur.close()
  conn.close()
  print("Values inserted into fighter_fights table!")

def write_to_rounds(csv_file):
  df = pd.read_csv(csv_file)
  conn = psycopg2.connect(
    dbname='ufc_fighter_db',
    user='postgres',
    password='347824Mg',
    host='localhost',
    port=5432
  )
  print('Db connection successful!')
  cur = conn.cursor()
  for _, row in df.iterrows():
    cur.execute(
      """
        INSERT INTO rounds(fight_id, fighter_id, round_number, kd, sig_strikes_landed, sig_strikes_attempted, sig_strikes_landed_distance, sig_strikes_attempted_distance, sig_strikes_landed_clinch, sig_strikes_attempted_clinch, sig_strikes_landed_ground, sig_strikes_attempted_ground, total_strikes_landed, total_strikes_attempted, sig_head_strikes_landed, sig_head_strikes_attempted, sig_body_strikes_landed, sig_body_strikes_attempted, sig_leg_strikes_landed, sig_leg_strikes_attempted, takedowns_landed, takedowns_attempted, submissions_attempted, reversals, control_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
      """,
      (int(row['fight_id']), int(row['fighter_id']), int(row['round']), int(row['kd']), int(row['sig_str_landed']), int(row['sig_str_attempted']), int(row['distance_landed']), int(row['distance_attempted']), int(row['clinch_landed']), int(row['clinch_attempted']), int(row['ground_landed']), int(row['ground_attempted']), int(row['total_str_landed']), int(row['total_str_attempted']), int(row['head_landed']), int(row['head_attempted']), int(row['body_landed']), int(row['body_attempted']), int(row['leg_landed']), int(row['leg_attempted']), int(row['td_landed']), int(row['td_attempted']), int(row['sub_att']), int(row['reversals']), row['ctr_time'])
    )
  conn.commit()
  cur.close()
  conn.close()
  print("Values inserted into rounds table!")

file = "../cleaned/cleaned_fighters.csv"
write_to_fighters(file)

file = "../cleaned/cleaned_ufc_fights.csv"
write_to_fights(file)

file = "../cleaned/fighter_fights.csv"
write_to_fighter_fights(file)

file = "../cleaned/cleaned_rounds.csv"
write_to_rounds(file)