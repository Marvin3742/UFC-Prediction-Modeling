import pandas as pd
import re

def height_to_inches(height_str):
    match = re.findall(r"\d+", height_str)
    if len(match) != 2:
        return None
    feet, inches = map(int, match)
    return feet * 12 + inches

def split_record_columns(df):
    record_split = df['fighter_record'].str.split('-', expand=True)

    df['wins'] = pd.to_numeric(record_split[0], errors='coerce').fillna(0).astype(int)
    df['losses'] = pd.to_numeric(record_split[1], errors='coerce').fillna(0).astype(int)
    df['draws'] = pd.to_numeric(record_split[2], errors='coerce').fillna(0).astype(int)

    return df.drop(columns=['fighter_record'])

def clean_data_point(data, data_type):
    match data_type:
        case "fighter_record":
            if data == "--" or pd.isna(data):
                return "N/A"
            else:
                match_obj = re.search(r"(\d+-\d+-\d+)", data)
                cleaned = match_obj.group(1) if match_obj else "N/A"
                return cleaned
        case "height":
            if data == "--" or pd.isna(data):
                return 0
            else:
                cleaned = height_to_inches(data)
                return cleaned
        case "weight":
            if data == "--" or pd.isna(data):
                return 0
            else: 
                cleaned = int(re.search(r"\d+", data).group())
                return cleaned
        case "reach":
            if data == "--" or pd.isna(data):
                return 0
            else:
                cleaned = int(re.search(r"\d+", data).group())
                return cleaned
        case "stance":
            if data == "--" or pd.isna(data):
                return "N/A"
            else:
                return data
        case "dob":
            if data == "--" or pd.isna(data):
                return "Jan 01, 1900"
            else:
                return data
        case "detail":
            if data == "--" or pd.isna(data):
                return "N/A"
            else:
                return data
        case _:
            return None
        

def clean_fighter_csv(fighter_csv):
    fighter_df = pd.read_csv(fighter_csv)

    fighter_df['fighter_record'] = fighter_df['fighter_record'].apply(
        lambda x: clean_data_point(x, "fighter_record")
    )
    fighter_df['height'] = fighter_df['height'].apply(
        lambda x: clean_data_point(x, "height")
    )
    fighter_df['weight'] = fighter_df['weight'].apply(
        lambda x: clean_data_point(x, "weight")
    )
    fighter_df['reach'] = fighter_df['reach'].apply(
        lambda x: clean_data_point(x, "reach")
    )
    fighter_df['stance'] = fighter_df['stance'].apply(
        lambda x: clean_data_point(x, "stance")
    )
    fighter_df['dob'] = fighter_df['dob'].apply(
        lambda x: clean_data_point(x, "dob")
    )

    return fighter_df

            # rows.append({
            #     "event_name": event_name,
            #     "fight_date": fight_date,
            #     "location": location,          --- split into city, district, country
            #     "weight_class": weight_class,  --- extract weight class and championship flag
            #     "winner": winner,
            #     "win_method": win_method, 
            #     "detail": detail,              --- handle missing values
            #     "round": round,
            #     "end_time": end_time,
            #     "referee": referee
            #     })

def split_location(df):
    location_split = (
        df['location']
        .str.split(',', expand=True)
        .apply(lambda col: col.str.strip())
    )

    num_parts = df['location'].str.count(',') + 1

    df['city'] = location_split[0]
    df['state'] = location_split[1].where(num_parts == 3)
    df['country'] = location_split[2].where(num_parts == 3)

    df.loc[num_parts == 2, 'country'] = location_split[1]

    return df.drop(columns=['location'])


def clean_ufc_fights_csv(ufc_fights_csv):
    df = pd.read_csv(ufc_fights_csv)

    new_df = split_location(df)

    new_df['detail'] = new_df['detail'].apply(
        lambda x: clean_data_point(x, "detail")
    )

    new_df['title_bout'] = new_df['weight_class'].str.contains(
    r'title|championship',
    case=False,
    na=False
    )

    return new_df


def clean_rounds(rounds_csv):
    data = pd.read_csv(rounds_csv)
    cols = ["sig_str", "total_str", "td", "head", "body", "leg", "distance", "clinch", "ground"]
    
    for col in cols:
        extracted = data[col].str.extract(r'(\d+)\s+of\s+(\d+)').astype(int)
        data[f"{col}_landed"] = extracted[0]
        data[f"{col}_attempted"] = extracted[1]
    new_data = data.drop(columns=cols)
    
    return new_data



# new_df = clean_fighter_csv("../raw/fighters.csv")
# new_df = split_record_columns(new_df)
# new_df = new_df.drop(columns=["SLpM", "Str_Acc", "SApM", "Str_def", "TD_Avg", "TD_Acc", "TD_Def", "Sub_avg"])
# new_df.to_csv("../cleaned/cleaned_fighters.csv", index=False)

# new_df = clean_ufc_fights_csv("../raw/ufc_fights.csv")
# new_df.to_csv("../cleaned/cleaned_ufc_fights.csv", index=False)

new_df = clean_rounds("../raw/rounds.csv")
new_df.to_csv('../cleaned/cleaned_rounds.csv', index=False)
