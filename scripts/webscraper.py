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

csv = "../raw/fighters.csv"
rows = fighter_fights(url, csv)
save_location = "fighter_fights.csv"
data = pd.DataFrame(rows)
data.to_csv(save_location, index=False)



# TO-DO keep index when making fighter and fight csvs