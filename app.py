import io
import contextlib
import os
import textwrap
import pandas as pd
from datetime import datetime
import joblib
import json
import sys
import time
from pathlib import Path

PREDICTIONS_FILE = "predictions.json"

R      = "\033[0m"
B      = "\033[1m"
CYAN   = "\033[96m"
RED    = "\033[91m"
YELLOW = "\033[93m"
DIM    = "\033[2m"

DUPLICATES = {
    'mike davis', 'joey gomez', 'tony johnson',
    'michael mcdonald', 'bruno silva', 'jean silva', 'victor valenzuela'
}

STANCE_PAIRS = [
    "Orthodox_vs_Orthodox", "Orthodox_vs_Southpaw", "Orthodox_vs_Switch",
    "Southpaw_vs_Orthodox", "Southpaw_vs_Southpaw", "Southpaw_vs_Switch",
    "Switch_vs_Orthodox",   "Switch_vs_Southpaw",   "Switch_vs_Switch",
]

DIFF_COLS = [
    "diff_slpm", "diff_str_acc", "diff_sapm", "diff_str_def",
    "diff_td_avg", "diff_td_acc", "diff_td_def", "diff_sub_avg",
    "diff_height", "diff_weight", "diff_reach",
    "diff_wins", "diff_losses", "diff_draws", "diff_dob",
]

def c(text, *codes):            
    return "".join(codes) + str(text) + R

def clear():
    os.system("cls" if sys.platform == "win32" else "clear")

def hr(width=52):
    print(c("  " + "─" * width, DIM))

def section(title, width=52):
    hr(width)
    print(c(f"  {title}", B))
    hr(width)

def prompt(label=""):
    tag = f"  {label} " if label else "  "
    return input(c(tag + "» ", CYAN)).strip()

def error(msg):
    print(c(f"  ✗  {msg}", RED))

def type_print(text, delay=0.02, col=""):
    for ch in text:
        print(col + ch + R, end="", flush=True)
        time.sleep(delay)
    print()

LOGO = [
    r"  ██╗   ██╗███████╗ ██████╗ ",
    r"  ██║   ██║██╔════╝██╔════╝ ",
    r"  ██║   ██║█████╗  ██║      ",
    r"  ██║   ██║██╔══╝  ██║      ",
    r"  ╚██████╔╝██║     ╚██████╗ ",
    r"   ╚═════╝ ╚═╝      ╚═════╝ ",
    r"",
    r"  ██████╗ ██████╗ ███████╗██████╗ ██╗ ██████╗████████╗██╗ ██████╗ ███╗   ██╗███████╗",
    r"  ██╔══██╗██╔══██╗██╔════╝██╔══██╗██║██╔════╝╚══██╔══╝██║██╔═══██╗████╗  ██║██╔════╝",
    r"  ██████╔╝██████╔╝█████╗  ██║  ██║██║██║        ██║   ██║██║   ██║██╔██╗ ██║███████╗",
    r"  ██╔═══╝ ██╔══██╗██╔══╝  ██║  ██║██║██║        ██║   ██║██║   ██║██║╚██╗██║╚════██║",
    r"  ██║     ██║  ██║███████╗██████╔╝██║╚██████╗   ██║   ██║╚██████╔╝██║ ╚████║███████║",
    r"  ╚═╝     ╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝ ╚═════╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝",
]

def print_logo():
    colors = [CYAN, CYAN, CYAN, CYAN, CYAN, CYAN, "", RED, RED, RED, RED, RED, RED]
    for line, col in zip(LOGO, colors):
        print(c(line, col, B) if col else "")

class BackToMenu(Exception):
    pass

@contextlib.contextmanager
def _suppress_loky_warning():
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        yield
    captured = buf.getvalue()
    if not captured:
        return
    lines = captured.splitlines(keepends=True)
    result, in_warning, skip_indented = [], False, False
    for line in lines:
        if "Could not find the number of physical cores" in line:
            in_warning = True
        elif in_warning and "LOKY_MAX_CPU_COUNT" in line:
            in_warning, skip_indented = False, True
        elif in_warning:
            pass
        elif skip_indented and line[:1] in (" ", "\t"):
            pass
        else:
            skip_indented = False
            result.append(line)
    if result:
        sys.stderr.write("".join(result))

def date_diff(date_1, date_2):
    d1 = datetime.strptime(date_1, "%Y-%m-%d")
    d2 = datetime.strptime(date_2, "%Y-%m-%d")
    return (d1 - d2).days / 365

def pick_from_list(folder, label):
    files = [f for f in sorted(Path(folder).iterdir()) if f.is_file()]
    if not files:
        error(f"No {label.lower()}s found in '{folder}/'.")
        return None
    section(f"Select {label}")
    for i, f in enumerate(files, 1):
        print(f"  [{i}] {f.name}")
    hr()
    while True:
        raw = prompt()
        if raw.lower() == "q":
            raise BackToMenu
        if raw.isdigit() and 1 <= int(raw) <= len(files):
            return files[int(raw) - 1].name
        error(f"Enter a number between 1 and {len(files)}.")

def get_fighter_ids(df, label):
    while True:
        raw = prompt(f"Fighter {label}")
        if raw.lower() == "q":
            raise BackToMenu
        if raw.isdigit():
            fid = int(raw)
            fights = pd.concat([df[df["f1_fighter_id"] == fid], df[df["f2_fighter_id"] == fid]])
            if fights.empty:
                error("Fighter ID not found.")
                continue
            latest = fights.loc[fights["fight_id"].idxmax()]
            name = latest["f1_name"] if latest["f1_fighter_id"] == fid else latest["f2_name"]
            return name, fid
        if raw.lower() in DUPLICATES:
            error(f"Multiple fighters named '{raw}'. Enter their fighter ID instead.")
            continue
        fights = pd.concat([df[df["f1_name"] == raw], df[df["f2_name"] == raw]])
        if fights.empty:
            error(f"'{raw}' not found.")
            continue
        latest = fights.loc[fights["fight_id"].idxmax()]
        if latest["f1_name"] == raw:
            return raw, latest["f1_fighter_id"]
        return raw, latest["f2_fighter_id"]

def create_features(df, fighter_a_id, fighter_b_id, title_bout):
    fights_a = pd.concat([df[df["f1_fighter_id"] == fighter_a_id], df[df["f2_fighter_id"] == fighter_a_id]])
    fights_b = pd.concat([df[df["f1_fighter_id"] == fighter_b_id], df[df["f2_fighter_id"] == fighter_b_id]])
    latest_a = fights_a.loc[[fights_a["fight_id"].idxmax()]]
    latest_b = fights_b.loc[[fights_b["fight_id"].idxmax()]]

    prefix_a = "f1" if latest_a["f1_fighter_id"].iloc[0] == fighter_a_id else "f2"
    prefix_b = "f1" if latest_b["f1_fighter_id"].iloc[0] == fighter_b_id else "f2"

    cols = ["name", "height", "weight", "reach", "stance", "dob",
            "wins", "losses", "draws",
            "slpm", "str_acc", "sapm", "str_def",
            "td_avg", "td_acc", "td_def", "sub_avg"]
    fa = {s: latest_a[f"{prefix_a}_{s}"].iloc[0] for s in cols}
    fb = {s: latest_b[f"{prefix_b}_{s}"].iloc[0] for s in cols}

    def print_fighter(tag, f):
        print(c(f"  {tag}  {f['name']}", B))
        print(c(f"  {'─'*46}", DIM))
        print(f"  {'UFC Record':<10} {f['wins']}-{f['losses']}-{f['draws']}")
        print(f"  {'Physical':<10} {f['height']}\" / {f['weight']} lbs / {f['reach']}\" reach / {f['stance']}")
        print(f"  {'Striking':<10} SLpM {f['slpm']:<11.3f} Acc {f['str_acc']:.0%}   SApM {f['sapm']:<11.3f} Def {f['str_def']:.0%}")
        print(f"  {'Grappling':<10} TD {f['td_avg']:<13.3f} Acc {f['td_acc']:.0%}   Def {f['td_def']:.0%}   Sub {f['sub_avg']:.3f}")

    section("Fighter Summary")
    print_fighter("A »", fa)
    print()
    print_fighter("B »", fb)
    hr()

    num_feats = ["slpm", "str_acc", "sapm", "str_def", "td_avg", "td_acc", "td_def", "sub_avg",
                 "height", "weight", "reach", "wins", "losses", "draws"]
    row = {"title_bout": int(title_bout)}
    for feat in num_feats:
        row[f"diff_{feat}"] = fa[feat] - fb[feat]
    row["diff_dob"] = date_diff(fa["dob"], fb["dob"])
    stance_pair = f"{fa['stance']}_vs_{fb['stance']}"
    for col in STANCE_PAIRS:
        row[col] = 1 if col == stance_pair else 0

    return pd.DataFrame([row])

def load_predictions():
    p = Path(PREDICTIONS_FILE)
    if not p.exists() or p.stat().st_size == 0:
        return []
    with open(PREDICTIONS_FILE, "r") as f:
        return json.load(f)

def save_prediction(record):
    preds = load_predictions()
    preds.append(record)
    with open(PREDICTIONS_FILE, "w") as f:
        json.dump(preds, f, indent=2)

def get_prediction(model_name, dataset_name, features_df, name_a, name_b, title_bout):
    scaler = joblib.load("scalers/scaler_v1.joblib")
    features_df = features_df.copy()
    features_df[DIFF_COLS] = scaler.transform(features_df[DIFF_COLS])

    model = joblib.load(f"models/{model_name}")
    with _suppress_loky_warning():
        prediction = model.predict(features_df)[0]
    winner = (name_a or "Fighter A") if prediction == 1 else (name_b or "Fighter B")

    section("Prediction")
    print(c(f"  {winner} wins!", YELLOW, B))
    conf = None
    if hasattr(model, "predict_proba"):
        with _suppress_loky_warning():
            proba = model.predict_proba(features_df)[0]
        conf = float(proba[prediction])
        filled = round(conf * 30)
        bar = "█" * filled + "░" * (30 - filled)
        print(c(f"  Confidence  {conf:.1%}  {bar}", DIM))
    hr()

    save_prediction({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "fighter_a": name_a or "Fighter A",
        "fighter_b": name_b or "Fighter B",
        "title_bout": title_bout,
        "dataset": dataset_name,
        "model": model_name,
        "winner": winner,
        "confidence": round(conf, 4) if conf is not None else None,
    })

def splash_screen():
    clear()
    print()
    print_logo()
    print()
    hr(44)
    type_print("  > INITIALIZING UFC PREDICTIONS v1.0 ...", 0.02, CYAN)
    time.sleep(0.3)
    type_print("  > LOADING DATASETS ............. OK", 0.02, RED)
    time.sleep(0.2)
    type_print("  > CHECKING MODELS .............. OK", 0.02, RED)
    time.sleep(0.2)
    type_print("  > ALL SYSTEMS GO", 0.03, YELLOW)
    hr(44)
    print()
    input(c("  Press ENTER to continue... ", DIM))

def match_up_screen():
    clear()
    print()
    print_logo()
    print()
    try:
        model_name = pick_from_list("models", "Model")
        if not model_name:
            return
        dataset = pick_from_list("datasets", "Dataset")
        if not dataset:
            return
        df = pd.read_csv(f"datasets/{dataset}")
        df = df.dropna()
        df = df[df["f1_dob"] != "1900-01-01"]
        df = df[df["f1_reach"] > 0]
        df = df[df["f2_reach"] > 0]
        df = df[df["f1_stance"] != "Open Stance"]
        df = df[df["f2_stance"] != "Open Stance"]

        section("Match Up")
        name_a, id_a = get_fighter_ids(df, "A")
        name_b, id_b = get_fighter_ids(df, "B")
        raw = prompt("Title fight? (y/n)")
        if raw.lower() == "q":
            return
        title_bout = raw.lower() == "y"

        print()
        features_df = create_features(df, id_a, id_b, title_bout)

        while True:
            get_prediction(model_name, dataset, features_df, name_a, name_b, title_bout)
            print("  [1]  New match up")
            print("  [2]  Try a different model")
            print("  [3]  Return to menu")
            hr()
            choice = prompt()
            if choice in ("3", "q"):
                return
            elif choice == "1":
                match_up_screen()
                return
            elif choice == "2":
                new_model = pick_from_list("models", "Model")
                if new_model:
                    model_name = new_model
            else:
                error("Invalid choice.")
    except BackToMenu:
        return

def view_past_predictions_screen():
    while True:
        clear()
        print()
        print_logo()
        print()
        preds = load_predictions()
        section("Past Predictions")
        if not preds:
            print(c("  No predictions saved yet.", DIM))
            hr()
            prompt("Press ENTER to return")
            return
        for i, p in enumerate(reversed(preds), 1):
            conf_str = f"  {p['confidence']:.1%}" if p["confidence"] is not None else ""
            title_tag = c("  [TITLE]", YELLOW) if p.get("title_bout") else ""
            print(c(f"  {i:>3}.  {p['timestamp']}", DIM) + title_tag)
            print(f"       {p['fighter_a']}  vs  {p['fighter_b']}")
            print(c(f"       Winner: ", DIM) + c(p["winner"], YELLOW, B) + c(conf_str, DIM))
            print(c(f"       Model:   {p['model']}", DIM))
            print(c(f"       Dataset: {p['dataset']}", DIM))
            hr()
        print("  [d]  Delete a prediction")
        print("  [c]  Clear all predictions")
        print("  [q]  Back to menu")
        hr()
        choice = prompt().lower()
        if choice == "q":
            return
        elif choice == "c":
            confirm = prompt("Clear all predictions? (y/n)").lower()
            if confirm == "y":
                with open(PREDICTIONS_FILE, "w") as f:
                    json.dump([], f)
        elif choice == "d":
            raw = prompt("Delete entry number")
            if raw.isdigit() and 1 <= int(raw) <= len(preds):
                idx = len(preds) - int(raw)
                preds.pop(idx)
                with open(PREDICTIONS_FILE, "w") as f:
                    json.dump(preds, f, indent=2)
            else:
                error(f"Enter a number between 1 and {len(preds)}.")
                time.sleep(0.8)

def about_screen():
    clear()
    print()
    print_logo()
    print()
    try:
        cols = max(40, os.get_terminal_size().columns)
    except OSError:
        cols = 80
    w = cols - 4

    def wrap(text):
        return textwrap.fill(text, width=w, initial_indent="  ", subsequent_indent="  ")

    section("About", w)
    print(f"  {'Version':<12}  1.0")
    print(f"  {'Author':<12}  Marvin Guerrero-Rangel")
    hr(w)
    section("How It Works", w)
    print(wrap("Predictions served using standard machine learning models."))
    hr(w)
    section("Data", w)
    print(wrap("Fighter data scraped directly from the UFC Stats website. Updated continuously after each event."))
    hr(w)
    section("Why can't I find a fighter?", w)
    print(wrap("Fighter names must match exactly as they are in the official UFC Stats website. First and last names capitalized. Whether a fighter is available for match-making depends on the dataset/model chosen. For instance, the base KNN model drops fighters with missing values in their stats. In general, the less data available on a fighter, the less likely they will be available for inference."))
    hr(w)
    prompt("Press ENTER to return")

def main_menu():
    while True:
        clear()
        print()
        print_logo()
        print()
        section("Main Menu")
        print("  [1]  New match up")
        print("  [2]  View past predictions")
        print("  [3]  About")
        print("  [q]  Quit")
        hr()
        choice = prompt()

        if choice == "1":
            match_up_screen()
        elif choice == "q":
            clear()
            print(c("\n  Goodbye.\n", DIM))
            break
        elif choice == "2":
            view_past_predictions_screen()
        elif choice == "3":
            about_screen()
        else:
            error("Invalid choice.")
            time.sleep(0.8)

if __name__ == "__main__":
    try:
        splash_screen()
        main_menu()
    except KeyboardInterrupt:
        print(c("\n\n  Interrupted. Goodbye.\n", DIM))
