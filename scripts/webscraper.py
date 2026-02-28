import requests
from bs4 import BeautifulSoup
import pandas as pd

all_urls = ["http://ufcstats.com/statistics/fighters?char=a&page=all",
            "http://ufcstats.com/statistics/fighters?char=b&page=all",
            "http://ufcstats.com/statistics/fighters?char=c&page=all",
            "http://ufcstats.com/statistics/fighters?char=d&page=all",
            "http://ufcstats.com/statistics/fighters?char=e&page=all",
            "http://ufcstats.com/statistics/fighters?char=f&page=all",
            "http://ufcstats.com/statistics/fighters?char=g&page=all",
            "http://ufcstats.com/statistics/fighters?char=h&page=all",
            "http://ufcstats.com/statistics/fighters?char=i&page=all",
            "http://ufcstats.com/statistics/fighters?char=j&page=all",
            "http://ufcstats.com/statistics/fighters?char=k&page=all",
            "http://ufcstats.com/statistics/fighters?char=l&page=all",
            "http://ufcstats.com/statistics/fighters?char=m&page=all",
            "http://ufcstats.com/statistics/fighters?char=n&page=all",
            "http://ufcstats.com/statistics/fighters?char=o&page=all",
            "http://ufcstats.com/statistics/fighters?char=p&page=all",
            "http://ufcstats.com/statistics/fighters?char=q&page=all",
            "http://ufcstats.com/statistics/fighters?char=r&page=all",
            "http://ufcstats.com/statistics/fighters?char=s&page=all",
            "http://ufcstats.com/statistics/fighters?char=t&page=all",
            "http://ufcstats.com/statistics/fighters?char=u&page=all",
            "http://ufcstats.com/statistics/fighters?char=v&page=all",
            "http://ufcstats.com/statistics/fighters?char=w&page=all",
            "http://ufcstats.com/statistics/fighters?char=x&page=all",
            "http://ufcstats.com/statistics/fighters?char=y&page=all",
            "http://ufcstats.com/statistics/fighters?char=z&page=all",]

url = "http://ufcstats.com/statistics/events/completed?page=all"


def get_winner(soup):
    competitors = soup.find_all("div", class_="b-fight-details__person")

    for comp in competitors:
        status = comp.find("i", class_="b-fight-details__person-status")
        if status and status.get_text(strip=True) == "W":
            name = comp.find("a", class_="b-fight-details__person-link").get_text(strip=True)
            return name

    return "Draw"

def scrape_basic_fighter_info(all_urls):
    rows = []
    for index, url in enumerate(all_urls):
        print(f"PROCESSING PAGE {index}")
        response = requests.get(url)

        soup = BeautifulSoup(response.content, "html.parser")

        table_rows = soup.find_all("tr", class_ = "b-statistics__table-row")

        fighter_links = []
        for i in range(2, len(table_rows)):
            fighter_link = table_rows[i].find('a')
            fighter_links.append(fighter_link.get('href'))

        for i in range(len(fighter_links)):
            fighter_response = requests.get(fighter_links[i])
            print(f'Processing link: {fighter_links[i]}')
            fighter_soup = BeautifulSoup(fighter_response.content, "html.parser")
            name = fighter_soup.find("span", class_ = "b-content__title-highlight").get_text(strip=True)
            record = fighter_soup.find("span", class_ = "b-content__title-record").get_text(strip=True)
            info = fighter_soup.find_all("li", class_ = "b-list__box-list-item b-list__box-list-item_type_block")
            for j in range(14):
                label = info[j].find("i")
                label.extract()
            height = info[0].get_text(strip=True)
            weight = info[1].get_text(strip=True)
            reach = info[2].get_text(strip=True)
            stance = info[3].get_text(strip=True) 
            dob = info[4].get_text(strip=True)
            slpm = info[5].get_text(strip=True)
            str_acc = info[6].get_text(strip=True)
            sapm = info[7].get_text(strip=True)
            str_def = info[8].get_text(strip=True)
            td_avg = info[10].get_text(strip=True)
            td_acc = info[11].get_text(strip=True)
            td_def = info[12].get_text(strip=True)
            sub_avg = info[13].get_text(strip=True)
            rows.append({
                "fighter_name": name,
                "fighter_record": record,
                "height": height,
                "weight": weight,
                "reach": reach,
                "stance": stance,
                "dob": dob,
                "SLpM": slpm,
                "Str_Acc": str_acc,
                "SApM": sapm,
                "Str_def": str_def,
                "TD_Avg": td_avg,
                "TD_Acc": td_acc,
                "TD_Def": td_def,
                "Sub_avg": sub_avg
    
            })
    return rows


def scrape_ufc_fights(url):
    rows = []
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    table_rows = soup.find_all("tr", class_ = "b-statistics__table-row")
    card_links = []
    for i in range(2, len(table_rows)):
        link = table_rows[i].find("a").get('href')
        card_links.append(link)
    for i in range(len(card_links)-1, -1, -1):
        response = requests.get(card_links[i])
        print(f"PROCESSING CARD {i}")
        soup = BeautifulSoup(response.content, "html.parser")
        event_name = soup.find("span", class_="b-content__title-highlight").get_text(strip=True)
        info = soup.find_all("li", class_="b-list__box-list-item")
        for j in range(len(info)):
            label = info[j].find("i")
            label.extract()
        fight_date = info[0].get_text(strip=True)
        location = info[1].get_text(strip=True)
        table_rows = soup.find_all("tr", class_ = "b-fight-details__table-row b-fight-details__table-row__hover js-fight-details-click")
        fight_links = []
        for j in range(len(table_rows)):
            link = table_rows[j].get("data-link")
            fight_links.append(link)
        for j in range(len(fight_links)-1, -1, -1):
            response = requests.get(fight_links[j])
            soup = BeautifulSoup(response.content, "html.parser")
            winner = get_winner(soup) # returns name of winner or "draw" if draw
            weight_class = soup.find("i", class_="b-fight-details__fight-title").get_text(strip=True)
            win_method = soup.find("i", style="font-style: normal").get_text(strip=True)
            info = soup.find_all("i", class_="b-fight-details__text-item")
            for k in range(len(info)):
                label = info[k].find("i", class_="b-fight-details__label")
                if not label:
                    continue
                label.extract()
            detail = soup.find_all("p", class_="b-fight-details__text")
            for k in range(len(detail)):
                label = detail[k].find('i', class_="b-fight-details__label")
                if not label:
                    continue
                label.extract()
            round = info[0].get_text(strip=True)
            end_time = info[1].get_text(strip=True)
            referee = info[3].get_text(strip=True)
            detail = detail[1].get_text(strip=True)
            rows.append({
                "event_name": event_name,
                "fight_date": fight_date,
                "location": location,
                "weight_class": weight_class,
                "winner": winner,
                "win_method": win_method,
                "detail": detail,
                "round": round,
                "end_time": end_time,
                "referee": referee
                })
    return rows

def get_duplicate_fighter_id(fighter_name, url, df):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    record = soup.find("span", class_ = "b-content__title-record").get_text(strip=True)
    info = soup.find_all("li", class_="b-list__box-list-item b-list__box-list-item_type_block")
    for j in range(14):
        label = info[j].find('i')
        label.extract()
        height = info[0].get_text(strip=True)
        weight = info[1].get_text(strip=True)
        reach = info[2].get_text(strip=True)
        stance = info[3].get_text(strip=True) 
        dob = info[4].get_text(strip=True)
    fighter_id = df[(df['fighter_name'] == fighter_name) &
                    (df['fighter_record'] == record) &
                    (df['height'] == height) & 
                    (df['weight'] == weight) & 
                    (df['reach'] == reach) &
                    (df['stance'] == stance) &
                    (df['dob'] == dob)].index
    return fighter_id[0]

# This algorithm parses through the ufc fight page in the same way that scrape_ufc_fights does. This way the fight_id will
# just be the iteration the algorithm is in. At each fight, the algorithm will collect the names of each fighter. The algo will then check if 
# the fighter names are in a list that contains duplicate names. If the names are duplicates then the algo will go the fighters page for more details
# and discern which fighter it is. This will avoid the costly operation of visiting urls since most fighter names are unique. Fighter names will be used to
# extract their fighter_id from cleaned_ufc_fights.csv:
# Output will be a file names fighter_fights.csv with columns, fighter_id, fight_id

def fighter_fights(url, csv):
    rows = []
    fighter_df = pd.read_csv(csv)
    fighter_df.index = fighter_df.index + 1 
    duplicates = list(fighter_df[fighter_df['fighter_name'].duplicated()]['fighter_name'])
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table_rows = soup.find_all('tr', class_= 'b-statistics__table-row')
    card_links = []
    for i in range(2, len(table_rows)):
        link = table_rows[i].find('a').get('href')
        card_links.append(link)
    fight_id = 1
    for i in range(len(card_links)-1, -1, -1):
        response = requests.get(card_links[i])
        print(f'PROCESSING CARD {i}')
        soup = BeautifulSoup(response.content, "html.parser")
        table_rows = soup.find_all('tr', class_="b-fight-details__table-row b-fight-details__table-row__hover js-fight-details-click")
        for i in range(len(table_rows)-1, -1, -1):
            tags = table_rows[i].find_all('a')
            for i in range(len(tags)-1, max(-1, len(tags) - 2 - 1), -1):
                fighter_name = tags[i].get_text(strip=True)
                if fighter_name in duplicates:
                    fighter_id = get_duplicate_fighter_id(fighter_name, tags[i].get('href'), fighter_df)
                else:
                    fighter_id = fighter_df[fighter_df['fighter_name'] == fighter_name].index[0]

                rows.append({
                    "fight_id": fight_id,
                    "fighter_id": fighter_id,
                })
            fight_id += 1
    return rows

def rows_from_fight(features, fight_id, fighter_a_id, fighter_b_id):
    rows = []
    rounds = 0
    if len(features) != 0:
        rounds = (len(features) - 38) // 38

    for round in range(rounds):
        kd_idx = 22 + round * 20
        sig_str_idx = 24 + (round*20)
        total_str_idx = 28 + round * 20
        td_idx = 30 + round * 20
        sub_att_idx = 34 + round * 20
        rev_idx = 36 + round * 20
        ctr_time_idx = 38 + round * 20
        head_idx = (44 + rounds * 20) + round * 18
        body_idx = (46 + rounds * 20) + round * 18
        body_idx = (46 + rounds * 20) + round * 18
        leg_idx = (48 + rounds * 20) + round * 18
        distance_idx = (50 + rounds * 20) + round * 18
        clinch_idx = (52 + rounds * 20) + round * 18
        ground_idx = (54 + rounds * 20) + round * 18
        rows.append({
            "fight_id": fight_id,
            "fighter_id": fighter_a_id,
            "round": round+1,
            "kd": features[kd_idx],
            "sig_str": features[sig_str_idx],
            "total_str": features[total_str_idx],
            "td": features[td_idx],
            "sub_att": features[sub_att_idx],
            "reversals": features[rev_idx],
            "ctr_time": features[ctr_time_idx],
            "head": features[head_idx],
            "body": features[body_idx],
            "leg": features[leg_idx],
            "distance": features[distance_idx],
            "clinch": features[clinch_idx],
            "ground": features[ground_idx]
            })
        
    for round in range(rounds):
        kd_idx = 23 + round * 20
        sig_str_idx = 25 + (round*20)
        total_str_idx = 29 + round * 20
        td_idx = 31 + round * 20
        sub_att_idx = 35 + round * 20
        rev_idx = 37 + round * 20
        ctr_time_idx = 39 + round * 20
        head_idx = (45 + rounds * 20) + round * 18
        body_idx = (47 + rounds * 20) + round * 18
        leg_idx = (49 + rounds * 20) + round * 18
        distance_idx = (51 + rounds * 20) + round * 18
        clinch_idx = (53 + rounds * 20) + round * 18
        ground_idx = (55 + rounds * 20) + round * 18
        rows.append({
            "fight_id": fight_id,
            "fighter_id": fighter_b_id,
            "round": round+1,
            "kd": features[kd_idx],
            "sig_str": features[sig_str_idx],
            "total_str": features[total_str_idx],
            "td": features[td_idx],
            "sub_att": features[sub_att_idx],
            "reversals": features[rev_idx],
            "ctr_time": features[ctr_time_idx],
            "head": features[head_idx],
            "body": features[body_idx],
            "leg": features[leg_idx],
            "distance": features[distance_idx],
            "clinch": features[clinch_idx],
            "ground": features[ground_idx]
            })
    return rows


def fight_rounds(url, csv):
    rows = []
    fighter_df = pd.read_csv(csv)
    fighter_df.index = fighter_df.index + 1 
    duplicates = list(fighter_df[fighter_df['fighter_name'].duplicated()]['fighter_name'])
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    table_rows = soup.find_all("tr", class_ = "b-statistics__table-row")
    card_links = []
    for i in range(2, len(table_rows)):
        link = table_rows[i].find("a").get('href')
        card_links.append(link)
    fight_id = 1
    for i in range(len(card_links)-1, -1, -1):
        response = requests.get(card_links[i])
        print(f"PROCESSING CARD {i}")
        soup = BeautifulSoup(response.content, "html.parser")
        table_rows = soup.find_all("tr", class_ = "b-fight-details__table-row b-fight-details__table-row__hover js-fight-details-click")
        fight_links = []
        for j in range(len(table_rows)):
            link = table_rows[j].get("data-link")
            fight_links.append(link)
        for j in range(len(fight_links)-1, -1, -1):
            response = requests.get(fight_links[j])
            soup = BeautifulSoup(response.content, "html.parser")
            fighter_names = soup.find_all('a', class_='b-link b-fight-details__person-link')
            fighter_name_a = fighter_names[0].get_text(strip=True)
            fighter_name_b = fighter_names[1].get_text(strip=True)

            if fighter_name_a in duplicates:
                fighter_link = fighter_names[0].get('href')
                fighter_a_id = get_duplicate_fighter_id(fighter_name_a, fighter_link, fighter_df)
            else:
                fighter_a_id = fighter_df[fighter_df['fighter_name'] == fighter_name_a].index[0]

            if fighter_name_b in duplicates:
                fighter_link = fighter_names[1].get('href')
                fighter_b_id = get_duplicate_fighter_id(fighter_name_b, fighter_link, fighter_df)
            else:
                fighter_b_id = fighter_df[fighter_df['fighter_name'] == fighter_name_b].index[0]
            
            data = soup.find_all('p', class_ = "b-fight-details__table-text")
            features = []
            for point in data:
                features.append(point.get_text(strip=True))

            new_rows = rows_from_fight(features, fight_id, fighter_a_id, fighter_b_id)
            rows = rows + new_rows
            fight_id += 1
    return rows

            
# # -----------------------------------------------
# # EXAMPLE USAGE
# # -----------------------------------------------
# save_location = "fighters.csv"
# rows = scrape_basic_fighter_info(all_urls)
# fighter_data = pd.DataFrame(rows)
# fighter_data.index = fighter_data.index + 1
# fighter_data.index.name = "fighter_id"
# fighter_data.to_csv(save_location, index=True)
# print(f"CSV saved succesfully to {save_location} !")

# save_location = "ufc_fights.csv"
# rows = scrape_ufc_fights(url)
# fight_data = pd.DataFrame(rows)
# fight_data.index = fight_data.index + 1
# fight_data.index.name = "fight_id"
# fight_data.to_csv(save_location, index=True)

# csv = "../raw/fighters.csv"
# rows = fighter_fights(url, csv)
# save_location = "fighter_fights.csv"
# data = pd.DataFrame(rows)
# data.to_csv(save_location, index=False)



# TO-DO keep index when making fighter and fight csvs
# rows = fight_rounds(url, "../raw/fighters.csv")
# data = pd.DataFrame(rows)
# data.to_csv("rounds.csv", index=False)