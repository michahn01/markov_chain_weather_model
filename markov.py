from csv import DictReader, reader
import json
from datetime import date, time, datetime
import numpy as np # for matrix multiplication
import itertools


# A function to check if date is within desired range.
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
        elif param == "tavg" or param == "tmax" or param == "tmin":
            try:
                value = float(value)
            except:
                # if temperature data somehow missing, assume typical weather
                if param == "tmin":
                    state += f"18 < {param}; "
                else:
                    state += f"18 < {param} <= 25; "
                continue
            if value <= 18:
                state += f"{param} <= 18; "
            elif value <= 25:
                if param == "tmin":
                    state += f"18 < {param}; "
                else:
                    state += f"18 < {param} <= 25; "
            else:
                if param == "tmin":
                    state += f"18 < {param}; "
                else:
                    state += f"25 < {param}; "
        elif param == "prcp" or param == "wspd":
            try:
                value = float(value)
            except:
                # if temperature data somehow missing, assume no rain or moderate wind
                state += f"{param} == 0; " if param == "prcp" else f"{param} <= 5; "
                continue
            if value == 0 and param == "prcp":
                state += f"{param} == 0; "
            elif value <= 5:
                if param == "prcp":
                    state += f"0 < {param} <= 5; "
                else:
                    state += f"{param} <= 5; "
            elif value <= 10:
                state += f"5 < {param} <= 10; "
            else:
                state += f"10 < {param}; "
    return state

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
# tavg,tmin,tmax,prcp,wspd
def make_markov_model(file_path, params, n_gram):
    raw_frequencies = {}
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
                insert_into_markov_model(raw_frequencies, current_state, next_state)
                current_state = ""
                len_curr = 0
                next_state = ""
                len_next = 0

    # a model that holds pr(transitioning into state A | currently in state B)
    markov_model = {}
    # a generic model that holds pr(transitioning into state A)
    generic_probabilities = {}

    total = 0
    for curr in raw_frequencies:
        markov_model[curr] = {}
        sub_total = 0
        for future in raw_frequencies[curr]:
            sub_total += raw_frequencies[curr][future]
            total += raw_frequencies[curr][future]
        for future in raw_frequencies[curr]:
            markov_model[curr][future] = raw_frequencies[curr][future] / sub_total
            if future in generic_probabilities:
                generic_probabilities[future] += raw_frequencies[curr][future]
            else:
                generic_probabilities[future] = raw_frequencies[curr][future]
    for possibility in generic_probabilities:
        generic_probabilities[possibility] /= total

    return markov_model, generic_probabilities

def print_markov_model(model):
    for state in model:
        print(f"Current State: {state}")
        for future in model[state]:
            print(f"One possible future: {future} count: {model[state][future]}")
        print("\n")

def save_markov_model(model):
    with open(f"data/pre_built_models/model_created_on_{date.today()}_{datetime.now().time()}.json", 'w', encoding='utf-8') as f: 
        json.dump(model, f, ensure_ascii=False, indent=4) 

# construct a python vector containing all potential weather conditions 
# (each weather condition represents a state of the Markov chain) that
# can be constructed as combinations of the possible values of the given parameters 
def construct_states_vector_template(params):
    vec = []
    param_values = {
        "tavg" : ["18 < tavg <= 25; ", "tavg <= 18; ", "25 < tavg; "],
        "tmin" : ["tmin <= 18; ", "18 < tmin; "],
        "tmax" : ["18 < tmax <= 25; ", "tmax <= 18; ", "25 < tmax; "],
        "prcp" : ["prcp == 0; ", "0 < prcp <= 5; ", "5 < prcp <= 10; ", "10 < prcp; "],
        "wspd" : ["wspd <= 5; ", "5 < wspd <= 10; ", "10 < wspd; "]
    }
    param_values = [param_values[param] for param in params]
    combinations = ["".join(combo) for combo in itertools.product(*param_values)]
    
    return combinations

# without considering the current state, constructs a vector
# containing the probability of entering each state in model 
# from an unknown current state
# put simply, whereas a Markov chain considers the p(entering some state A | we're in state B), 
# the following function computes p(entering some state A).
# These generic probabilities will be used for states in 
# the Markov chain which have never been observed in the sample data. 
def construct_generic_probability_vector(generic_model, all_possibilities):
    vec = []
    for possibility in all_possibilities:
        if possibility in generic_model:
            vec.append(generic_model[possibility])
        else:
            vec.append(0)
    return np.array(vec)

# construct a numpy vector containing probabilities of all possible weather conditions 
# that can occur after the given state.
# If a given state was never observed in the training data, the generic vector will be used.
# all_possibilities must be a vector constructed using "construct_states_vector_template(params)"
def construct_state_probability_vector(markov_model, all_possibilities, state, generic_vector):
    vec = []
    if state in markov_model:
        probabilities = markov_model[state]
        for possibility in all_possibilities:
            if possibility in probabilities:
                vec.append(markov_model[state][possibility])
            else:
                vec.append(0)
        return np.array(vec)
    else:
        return generic_vector

def construct_transition_matrix(markov_model, all_possibilities, generic_vector):
    col_vecs = []
    for possibility in all_possibilities:
        vec = construct_state_probability_vector(markov_model, all_possibilities, possibility, generic_vector)
        col_vecs.append(vec)
    return np.column_stack(col_vecs)

if __name__ == "__main__":
    params = ["tavg", "tmax", "tmin", "prcp", "wspd"]
    model, generic_model = make_markov_model("data/san_jose_weather.csv", params, 1)
    
    all_possibilities = construct_states_vector_template(params)
    generic_vector = construct_generic_probability_vector(generic_model, all_possibilities)
    transition_matrix = construct_transition_matrix(model, all_possibilities, generic_vector)
    column_sums = np.sum(transition_matrix, axis=0)
    # print(column_sums)
    # print(np.sum(generic_model))

    # import random
    # random_curr = model[random.choice(list(model.keys()))]
    # random_state = random_curr[random.choice(list(random_curr.keys()))]
    # print(sum([val for key, val in random_curr.items()]))
    # statevec = construct_state_probability_vector(model, all_possibilities, random_state, generic_vector)
    # print(sum(statevec))
    
    save_markov_model(model)
