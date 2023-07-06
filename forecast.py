import markov
import json
from termcolor import colored

def make_predictions(params, markov_model):
    keywords = {
        "tavg" : "avg temp of the day in °C",
        "tmax" : "max temp of the day in °C",
        "tmin" : "min temp of the day in °C",
        "prcp" : "level of precipitation in mm",
        "wspd" : "avg windspeed of the day in km/h"
    }

    input_params = [
        ["tavg" , None],
        ["tmax" , None],
        ["tmin" , None],
        ["prcp" , None],
        ["wspd" , None]
    ]

    print(colored("\nMaking Forecasts\n", "cyan", attrs=["bold"]))

    for input_param in input_params:
        if input_param[0] in params:
            input_param[1] = input(f"What is the initial {keywords[input_param[0]]} ({input_param[0]})? ")

    weather_info = [(input_param[0], input_param[1]) for input_param in input_params if input_param[1] != None]
    classified_weather_info = markov.classify_weather_info(weather_info)

    num_days = -1
    while True:
        try:
            num_days = int(input("Enter desired number of days' predictions to be attempted from initial state: "))
            if num_days > 0:
                break
            else:
                print("Please enter a valid integer greater than 0.")
        except ValueError:
            print("Please enter a valid integer greater than 0.")

    
#     for i in range(num_days):
#         print(colored(f"\nOn Day {i + 1} ({classified_weather_info[:-4]}): ", "white", attrs=["bold"]))
#         if classified_weather_info not in markov_model:
#             print(f"\nMeteorological data for San Jose from 2014 ~ 2022 is insufficient to accurately \n\
# predict weather on Day {i + 1} and beyond for the selected set of parameters. To predict \n\
# further into the future, try loading up a model trained on fewer parameters. However, considering the \n\
# parameters on Day {i + 1} independently can give us some guesses: \n")
#             single_params = classified_weather_info.split("; ")[:-1]
#             single_param_models = json.load(open("data/pre_built_models/single_parameters.json"))
#             for data in single_params:
#                 param = ""
#                 for letter in data:
#                     if letter.isalpha(): param += letter
#                 print(f"Generally, a day where {data} has: ")
#                 for possibility, probability in single_param_models[param][data + "; | "].items():
#                     print(f"--- {probability * 100}% chance of {possibility[:-4]} the next day")
#                 print()
#             break

#         for possibility, probability in markov_model[classified_weather_info].items():
#             print(f"--- {probability * 100}% chance of {possibility[:-4]} the next day")
        
#         old_state = classified_weather_info
#         classified_weather_info = max(markov_model[classified_weather_info], key=markov_model[classified_weather_info].get)
#         if classified_weather_info == old_state:
#             print(f"\nOn Day {i + 1} the most likely weather the next day is equivalent to the current weather. \nThis means \
# that the Markov chain model has entered a state of absorbent/recurrent behavior, which the system cannot escape. \nRunning \
# the forecast any further would yield the same prediction (the current weather) without any transitions.\n")
#             break


def use_pre_built_model():
    print(colored("\nUsing a Pre-Built Model", "cyan", attrs=["bold"]))
    text = """
Instructions:

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

Select an option (enter 1, 2, 3, 4, 5, or 0): """
    selection = int(input(text))
    while selection not in [1, 2, 3, 4, 5, 0]:
        selection = int(input("Please enter a valid choice (enter 1, 2, 3, 4, 5, or 0): "))
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

    make_predictions(pre_built_models[selection], markov_model)

def make_new_model_and_predict():
    print(colored('\nGenerating a New Model\n', "cyan", attrs=["bold"]))
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
    for param in input_params:
        selection = input(f"Do you wish to include {keywords[param[0]]} ({param[0]}) as a parameter? [y/n] ")
        while not (selection.strip().lower() == "y" or selection.strip().lower() == "n"):
            selection = input(f"Please enter a valid choice. [y/n] ")
        if selection.strip().lower() == "y":
            param[1] = True

    selection = input("\nConfiguration complete. Enter y to continue or n to quit. ")
    while not (selection.strip().lower() == "y" or selection.strip().lower() == "n"):
            selection = input(f"Please enter a valid choice. [y/n] ")
    if selection.strip().lower() == "n":
        quit()        
    print("\nGenerating Model...")
    params = [param[0] for param in input_params if param[1]]
    markov_model = markov.make_markov_model("data/san_jose_weather.csv", params, 1)
    print("\nMarkov Model built!")
    make_predictions(params, markov_model)





def main_menu():
    print(colored('\nMarkov-Chain Weather Forecast Model', "cyan", attrs=["bold"]))
    
    text = """To get started, please select one of the following:

[1] Use a pre-built model to forecast weather.
[2] Newly generate a model with parameters of your choice.
[0] Quit the program.

Select an option (enter 1, 2, or 0): """
    selection = int(input(text))
    while selection not in [1, 2, 0]:
        selection = int(input("Please enter a valid choice (enter 1, 2, or 0): "))
    if selection == 0:
        quit()
    elif selection == 1:
        use_pre_built_model()
    elif selection == 2:
        make_new_model_and_predict()

if __name__ == "__main__":
    main_menu()