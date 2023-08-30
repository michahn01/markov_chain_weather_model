import markov
import json
import numpy as np
from termcolor import colored

def make_predictions(state, params, markov_model, generic_model, num_days):   
    print(colored("\nPREDICTIONS\n", "cyan", attrs=["bold"]), end="")

    all_possibilities = markov.construct_states_vector_template(params)
    generic_vector = markov.construct_generic_probability_vector(generic_model, all_possibilities)
    transition_matrix = markov.construct_transition_matrix(markov_model, all_possibilities, generic_vector)
    state_prob_vector = markov.construct_state_probability_vector(markov_model, all_possibilities, state, generic_vector)

    prediction_keywords = {
        "18 < tavg <= 25": "Moderate average temperature",
        "tavg <= 18": "Cold average temperature",
        "25 < tavg": "Hot average temperature",
        "18 < tmin": "Warm minimum temperature",
        "tmin <= 18": "Cold minimum temperature",
        "18 < tmax <= 25": "Moderate maximum temperature",
        "tmax <= 18": "Cold maximum temperature",
        "25 < tmax": "Hot maximum temperature",
        "prcp == 0": "No rain",
        "0 < prcp <= 5": "A slight drizzle",
        "5 < prcp <= 10": "Moderate rain",
        "10 < prcp": "Lots of rain",
        "wspd <= 5": "Low wind speed",
        "5 < wspd <= 10": "Moderate wind speed",
        "10 < wspd": "High wind speed"
    }

    
    for i in range(num_days):
        print(colored(f"\nOn Day {i+1}: \n", "white", attrs=["bold"]), end="")
        indices = sorted(range(len(state_prob_vector)), key=lambda i: state_prob_vector[i], reverse=True)[:10]
        for index in indices:
            prob = state_prob_vector[index]*100
            if prob < 0.5: continue
            print("---", end="")
            print(colored(f"{prob}%", "white", attrs=["bold"]), end="")
            print(" chance of:")

            info = all_possibilities[index]
            info_bits = info[:-2].split("; ")

            for i in range(len(info_bits) - 1):
                print(f"   * {prediction_keywords[info_bits[i]]} ({info_bits[i]}), with")
            print(f"   * {prediction_keywords[info_bits[len(info_bits) - 1]]} ({info_bits[len(info_bits) - 1]})")
            # print(f"     {info}")
        print("--- and some more possibilities of lower likelihoods")
        state_prob_vector = np.dot(transition_matrix, state_prob_vector)

    options_after_prediction(markov_model, params)

def print_warning():
    warning = """
* A note about the number of parameters:

TLDR: 
more parameters -> 
model more quickly decays into a steady state when making long-run predictions.

Full Explanation:

For weather states that were never observed from 2014 to 2022, the model has no data
to compute state transition probabilities (i.e., it has no way to tell what 
weather is likely next). This becomes problematic if there's a 
need to compute probabilities for weather unobserved in the sample. To 
counter this, some filler values can be made up and used for the state transition
probabilities of unobserved events. E.g., Laplace smoothing could be used, but 
that would assume a uniform distribution of state probabilities. With weather, we 
know that's not the case, so I instead used a form of smoothing somewhat similar 
in principle to the Maximum Likelihood Estimation (MLE), where for any unobserved 
state of weather the probabilities of transitioning into some next state are 
simply set equal to the distribution of those states in the sample itself (by 
definition, this makes the observed data most probable -- at 100% -- for the transition 
probability vectors we make up, hence maximizing the joint-likelihood function). 

Using more parameters at once means dealing with more theoretically possible 
weather conditions, which means there are more unobserved weather states whose transition
probabilities have to be set equal to the "filler" values described above. For example, 
if all possible parameters of this model are used, there are 216 theoretically possible 
weather states, but only 34 weather states have actually been observed in the sample data. 
Because the resulting transition matrix is sparse, more column vectors use the same "filler" 
vector (the vector whose state transition probabilities mirror the sample's distribution) 
and thus have identical transition probabilities. As a result, when making long-run predictions 
the model more quickly decays into a steady state with very little variety. 

To give an analogy, imagine that you have four doors to choose from (each door analogous to 
transitioning into a particular weather state in the Markov chain). Each each door leads to a 
unique place with four more unique doors, there'll be a lot of variety in where you end up. 
But if three of the foor doors lead to then same place (analogous to using a lot of the identical 
"filler" transition probabilities in the model), then there'll be a lot less variety in where 
you might end up. 
"""

    text = """
Before proceeding, do you wish to read the warning about the 
number of parameters used to train a model? [y/n]"""

    print(text)

    selection = input("Select a choice (enter y or n): ").strip()
    while not (selection.lower() == "y" or selection.lower() == "n"):
        selection = input(f"Please enter a valid choice. [y/n] ").strip()
    if selection.lower() == "y":
        print(warning)
        selection = input("Press y to proceed: ").strip()
        while not (selection.lower() == "y"):
            selection = input(f"Please enter a valid choice. [y] ").strip()

def setup_predictions(params, markov_model):
    keywords = {
        "tavg" : "avg temp today in °C",
        "tmax" : "max temp today in °C",
        "tmin" : "min temp today in °C",
        "prcp" : "level of precipitation today in mm",
        "wspd" : "avg windspeed today in km/h"
    }

    input_params = {
        "tavg" : None,
        "tmax" : None,
        "tmin" : None,
        "prcp" : None,
        "wspd" : None
    }

    param_ranges = {
        "tavg" : ["18 °C < tavg <= 25 °C", "tavg <= 18 °C", "25 °C < tavg"],
        "tmin" : ["18 °C < tmin <= 25 °C", "tmin <= 18 °C", "25 °C < tmin"],
        "tmax" : ["18 °C < tmax <= 25 °C", "tmax <= 18 °C", "25 °C < tmax"],
        "prcp" : ["prcp == 0 mm", "0 mm < prcp <= 5 mm", "5 mm < prcp <= 10 mm", "10 mm < prcp"],
        "wspd" : ["wspd <= 5 km/h", "5 km/h < wspd <= 10 km/h", "10 km/h < wspd"]
    }

    incompatible_ranges = {
        "18 °C < tavg <= 25 °C" : ["25 °C < tmin", "tmax <= 18 °C"],
        "tavg <= 18 °C" : ["18 °C < tmin <= 25 °C", "25 °C < tmin"],
        "25 °C < tavg" : ["18 °C < tmax <= 25 °C", "tmax <= 18 °C"],

        "18 °C < tmin <= 25 °C": ["tmax <= 18 °C", "tavg <= 18 °C"],
        "tmin <= 18 °C" : [],
        "25 °C < tmin": ["18 °C < tavg <= 25 °C", "tavg <= 18 °C", "18 °C < tmax <= 25 °C", "tmax <= 18 °C"],

        "18 °C < tmax <= 25 °C" : ["25 °C < tavg", "25 °C < tmin"], 
        "tmax <= 18 °C" : ["18 °C < tmin <= 25 °C", "25 °C < tmin", "18 °C < tavg <= 25 °C", "25 °C < tavg"], 
        "25 °C < tmax" : []       
    }

    def convert(param_range):
        if param_range == "18 °C < tmin <= 25 °C" or param_range == "25 °C < tmin":
            param_range = "18 °C < tmin"
        return param_range.replace(" °C", "").replace(" mm", "").replace(" km/h", "") + "; "

    print(colored("\nMAKING FORECASTS\n", "cyan", attrs=["bold"]))

    print("To predict the weather in the future, we will start by describing today's weather.")

    for param in params:
        print(colored(f"\n{param}) ", "white", attrs=["bold"]), end="")
        print(f"Select a range for {keywords[param]} ({param}): \n")
        i = 1
        for value_range in param_ranges[param]:
            print(f"[{i}] {value_range}\n")
            i += 1
        selection = input(f"Choose an option (enter {','.join([str(j) for j in range(1, i)])}): ").strip()
        while selection not in [str(j) for j in range(1, i)]:
            selection = input(f"Please choose a valid option (enter {','.join([str(j) for j in range(1, i)])}): ").strip()
        selection = param_ranges[param][int(selection) - 1]
        input_params[param] = convert(selection)

        # removing incompatible possibilities
        if selection in incompatible_ranges:
            for ir in incompatible_ranges[selection]:
                for range_param in param_ranges:
                    try:
                        param_ranges[range_param].remove(ir)
                    except:
                        pass

    classified_weather_info = "".join([input_params[param] for param in params if input_params[param] != None])
    # print(classified_weather_info)
    num_days = -1
    while True:
        try:
            enter_txt = """
Enter desired number of days' predictions to be
attempted from initial state (suggested: 1 ~ 10): """
            num_days = int(input(enter_txt))
            if num_days > 0:
                break
            else:
                print("Please enter a valid integer greater than 0.")
        except ValueError:
            print("Please enter a valid integer greater than 0.")

    markov_model, generic_model = markov.make_markov_model("data/san_jose_weather.csv", params, 1)
    make_predictions(classified_weather_info, params, markov_model, generic_model, num_days)
    
def options_after_prediction(markov_model, params):
    print("\n\nYou have reached the end of the model's forecasts.")
    print("Select [n] to quit the program or [y] to try something else.")
    selection = input("\nEnter y or n: ").strip()
    while not (selection.lower() == "y" or selection.lower() == "n"):
            selection = input(f"Please enter a valid choice. [y/n] ").strip()
    if selection.lower() == "n":
        quit()   
    print("""
Options:
[1] Run forecasts again with the same model.
[2] Return to the main menu.
""")
    selection = input("Enter 1 or 2: ").strip()
    while selection not in ["1", "2"]:
        selection = input("Please enter a valid choice (enter 1 or 2): ").strip()
    selection = int(selection)
    if selection == 1:
        setup_predictions(params, markov_model)
        return
    main_menu()

def use_pre_built_model():
    print(colored("\nUSING A PRE-BUILT MODEL", "cyan", attrs=["bold"]))

    print(colored("\nINSTRUCTIONS", "white", attrs=["bold"]))
    print("""
Choose a pre-built model to use. Each model has been trained on a different 
set of parameters (note: a model cannot make predictions about parameters it 
was not trained on). 

Keywords:
"tavg" -> avg temp of day in °C
"tmax -> max temp of day in °C
"tmin" -> min temp of day in °C
"prcp" -> level of precipitation in mm
"wspd" -> avg windspeed of day in km/h

Available Pre-Built Models:

[1] Model #1: trained on "tavg" and "tmax" 
[2] Model #2: trained on "tavg", "tmax", and "prcp"
[3] Model #3: trained on "tavg", "prcp", and "wspd" 
[4] Model #4: trained on "tavg", "tmax", "tmin", and "prcp"
[5] Model #5: trained on "tavg", "tmax", "tmin", "prcp", and "wspd"
""")

    print_warning()

    print(colored("\nPICK A MODEL", "white", attrs=["bold"]))

    setup_text = """
Keywords:
"tavg" -> avg temp of day in °C
"tmax -> max temp of day in °C
"tmin" -> min temp of day in °C
"prcp" -> level of precipitation in mm
"wspd" -> avg windspeed of day in km/h

Available Pre-Built Models:

[1] Model #1: trained on "tavg" and "tmax" 
[2] Model #2: trained on "tavg", "tmax", and "prcp"
[3] Model #3: trained on "tavg", "prcp", and "wspd" 
[4] Model #4: trained on "tavg", "tmax", "tmin", and "prcp"
[5] Model #5: trained on "tavg", "tmax", "tmin", "prcp", and "wspd"
[0] Quit the program

Select an option (enter 1, 2, 3, 4, 5, or 0): """
    selection = input(setup_text).strip()
    while selection not in ["1", "2", "3", "4", "5", "0"]:
        selection = input("Please enter a valid choice (enter 1, 2, 3, 4, 5, or 0): ").strip()
    selection = int(selection)
    if selection == 0:
        quit()
    
    pre_built_models = {
        1 : ("tavg", "tmax"),
        2: ("tavg", "tmax", "prcp"),
        3: ("tavg", "prcp", "wspd"),
        4: ("tavg", "tmax", "tmin", "prcp"),
        5: ("tavg", "tmax", "tmin", "prcp", "wspd")
    }

    file_name = "_".join(param for param in pre_built_models[selection]) + ".json"
    markov_model = json.load(open("data/pre_built_models/" + file_name))

    setup_predictions(pre_built_models[selection], markov_model)

def make_new_model_and_predict():
    print(colored('\nGENERATING A NEW MODEL', "cyan", attrs=["bold"]))
    input_params = [
        ["tavg" , False],
        ["tmax" , False],
        ["tmin" , False],
        ["prcp" , False],
        ["wspd" , False]
    ]
    keywords = {
        "tavg" : "avg temp of the day in °C",
        "tmax" : "max temp of the day in °C",
        "tmin" : "min temp of the day in °C",
        "prcp" : "level of precipitation in mm",
        "wspd" : "avg windspeed of the day in km/h"
    }

    print("\nAvailable parameters: \n")
    for key, val in keywords.items():
        print(f"{key}: {val}")
    
    print()

    print_warning()

    for param in input_params:
        selection = input(f"\nDo you wish to include {keywords[param[0]]} ({param[0]}) as a parameter? [y/n] ").strip()
        while not (selection.lower() == "y" or selection.lower() == "n"):
            selection = input(f"Please enter a valid choice. [y/n] ").strip()
        if selection.lower() == "y":
            param[1] = True

    selection = input("\nConfiguration complete. Enter y to continue or n to quit. ").strip()
    while not (selection.lower() == "y" or selection.lower() == "n"):
            selection = input(f"Please enter a valid choice. [y/n] ").strip()
    if selection.lower() == "n":
        quit()        
    print("\nGenerating Model...")
    params = [param[0] for param in input_params if param[1]]
    markov_model = markov.make_markov_model("data/san_jose_weather.csv", params, 1)
    print("\nMarkov Model built!")
    setup_predictions(params, markov_model)





def main_menu():

    print(colored('\nMarkov-Chain Weather Forecast Model', "cyan", attrs=["bold"]))

    text = """
To get started, please select one of the following:

[1] Use a pre-built model to forecast weather.
[2] Newly generate a model with parameters of your choice.
[0] Quit the program.

Select an option (enter 1, 2, or 0): """
    selection = input(text).strip()
    while selection not in ["1", "2", "0"]:
        selection = input("Please enter a valid choice (enter 1, 2, or 0): ").strip()
    selection = int(selection)
    if selection == 0:
        quit()
    elif selection == 1:
        use_pre_built_model()
    elif selection == 2:
        make_new_model_and_predict()

if __name__ == "__main__":
    main_menu()
