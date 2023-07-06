from csv import DictReader, reader
import json
from datetime import date, time, datetime

# A function to check if date is within desired range.
# In this case, we check whether date is in 
# September, October, or November
def is_within_date_range(date):
    month = int(date[5:7])
    date = int(date[8:10])
    return (month >= 9 and month <= 11)

# analyze and categorize weather info into a "state" of a Markov model
# only date, tavg, tmin, tmax, prcp, and wspd will be considered, 
# if available. Other data will be silently ignored. 
def classify_weather_info(weather_info):
    state = ""
    for param, value in weather_info:
        if param == "\ufeffdate": 
            state += value[5:7] + "; "
        elif param == "tavg" or param == "tmin" or param == "tmax":
            try:
                value = float(value)
            except:
                # if temperature data somehow missing, assume typical weather
                state += f"18 < {param} <= 25; "
                continue
            if value <= 18:
                state += f"{param} <= 18; "
            elif value <= 25:
                state += f"18 < {param} <= 25; "
            else:
                state += f"25 < {param}; "
        elif param == "prcp" or param == "wspd":
            try:
                value = float(value)
            except:
                # if temperature data somehow missing, assume no rain or moderate wind
                state += f"{param} == 0; " if param == "prcp" else f"0 < {param} <= 5; "
                continue
            if value == 0:
                state += f"{param} == 0; "
            elif value <= 5:
                state += f"0 < {param} <= 5; "
            elif value <= 10:
                state += f"5 < {param} <= 10; "
            else:
                state += f"10 < {param}; "
    return state + "| "

def insert_into_markov_model(markov_model, current_state, next_state):
    if current_state in markov_model:
        if next_state in markov_model[current_state]:
            markov_model[current_state][next_state] += 1
        else:
            markov_model[current_state][next_state] = 1
    else:
        markov_model[current_state] = { next_state : 1 }

# Requirements: "file_path" must be a csv file, "params" must be an iterable
# Possible values for "params":
# date,tavg,tmin,tmax,prcp,wspd
def make_markov_model(file_path, params, n_gram):
    markov_model = {}
    with open(file_path, 'r') as csv_file:
        csv_reader = DictReader(csv_file)
        # skip first line
        next(csv_reader)
        current_state = ""
        len_curr = 0
        next_state = ""
        len_next = 0
        for row in csv_reader:
            date = row["\ufeffdate"]
            weather_info = ((param, row[param]) for param in params)
            if len_curr != n_gram:
                current_state += classify_weather_info(weather_info)
                len_curr += 1
            elif len_next != n_gram:
                next_state += classify_weather_info(weather_info)
                len_next += 1
            else:
                insert_into_markov_model(markov_model, current_state, next_state)
                current_state = ""
                len_curr = 0
                next_state = ""
                len_next = 0

    for curr in markov_model:
        total = 0
        for future in markov_model[curr]:
            total += markov_model[curr][future]
        for future in markov_model[curr]:
            markov_model[curr][future] /= total

    return markov_model

def print_markov_model(model):
    for state in model:
        print(f"Current State: {state}")
        for future in model[state]:
            print(f"One possible future: {future} count: {model[state][future]}")
        print("\n")

def save_markov_model(model):
    with open(f"data/pre_built_models/model_created_on_{date.today()}_{datetime.now().time()}.json", 'w', encoding='utf-8') as f: 
        json.dump(model, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    # to access "date" parameter, use "\ufeffdate"
    model = make_markov_model("data/san_jose_weather.csv", ["tavg", "prcp", "wspd"], 1)
    save_markov_model(model)
