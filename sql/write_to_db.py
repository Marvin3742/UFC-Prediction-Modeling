import pandas as pd
import psycopg2

def write_to_fighters(csv_file):
  df = pd.read_csv(csv_file)
  conn = psycopg2.connect(
      dbname="ufc_fighter_db",
      user="postgres",
      password="3742",
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
      password="3742",
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
    password='3742',
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

file = "../cleaned/cleaned_fighters.csv"
write_to_fighters(file)

file = "../cleaned/cleaned_ufc_fights.csv"
write_to_fights(file)

file = "../cleaned/fighter_fights.csv"
write_to_fighter_fights(file)