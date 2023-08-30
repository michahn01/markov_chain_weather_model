# markov_chain_weather_model
A weather forecast model built using a Markov chain. Trained on 
weather data in San Jose from 2014 ~ 2022.

## Installing the Program 
Step 1) Ensure that you have Python3 and Pip3 installed on your machine.

Step 2) Open a terminal window.

Step 3) Clone this repository inside any location of choice on your machine and enter the project directory, by running the following two commands inside the terminal:
```
git clone https://github.com/michahn01/markov_chain_weather_model

cd markov_chain_weather_model
```

Step 4) Install the necessary dependencies with the following command:
```
pip3 install numpy termcolor
```

Step 5) Run the following command to launch the program:
```
python3 forecast.py
```

## How to use the Model

When you start the program, you are given 2 options: 

[1] Select and make forecasts with one of multiple versions of the model which were trained and saved as JSON files under [data](data/pre_built_models). Each version was trained on the same data but with different parameters (i.e., each build looks for different sets of patterns in the training data).

[2] Train your own new version of the model, on the same data as the pre-trained builds, but with parameters of your choice.

<img width="546" alt="image" src="https://github.com/michahn01/markov_chain_weather_model/assets/113268235/875a2224-52bf-47d3-a4b6-ab1bfa4ef79f">

Here's a more detailed explanation of each option.

### Option 1: Using a Pre-Trained Build

If you decide to use a pre-trained version of the model, you will be faced with the following menu:

<img width="552" alt="image" src="https://github.com/michahn01/markov_chain_weather_model/assets/113268235/7913128f-6f93-4c5c-8b3e-e92098fb45d6">

You can read the warning about the number of parameters used to train a model, if you wish:

<img width="626" alt="image" src="https://github.com/michahn01/markov_chain_weather_model/assets/113268235/28a88add-9d26-460a-ad15-4a888c326184">

You will then be prompted to pick a model. 

<img width="494" alt="image" src="https://github.com/michahn01/markov_chain_weather_model/assets/113268235/f356a0d5-495b-4fe6-afec-275c32f7596f">

Each model is trained on a different set of parameters. In terms of the Markov chain, every combination of parameters (e.g., avg temperature range, no rain or yes rain) represents a "state" of the system. 

Once you pick a model, you'll begin making forecasts with the model. From here on, the process is the same as it is from after [Option 2: Training a New Model](https://github.com/michahn01/markov_chain_weather_model/tree/master#option-2-training-a-new-model), so skip ahead to [Making Forecasts](https://github.com/michahn01/markov_chain_weather_model/tree/master#making-forecasts) to continue reading how to use the program.

### Option 2: Training a New Build

In the starting menu you can choose to train a new version of the model instead, which'll lead you to this screen.

<img width="440" alt="image" src="https://github.com/michahn01/markov_chain_weather_model/assets/113268235/0cfe83f9-dddf-4cff-ad6f-3a2709e4f667">

As in Option 1, you can choose to read the warning, or not.

You'll then be prompted to decide which parameters you want to include when training your model. 

<img width="628" alt="image" src="https://github.com/michahn01/markov_chain_weather_model/assets/113268235/6714f74b-9c35-48c2-8802-4df54ce3a13d">

Upon deciding all your parameters, the model will be generated and you will be prompted to the next section, [Making Forecasts](https://github.com/michahn01/markov_chain_weather_model/tree/master#making-forecasts), which is the same as after completing [Option 1: Using a Pre-Trained Model](https://github.com/michahn01/markov_chain_weather_model/tree/master#option-1-using-a-pre-trained-model). 

### Making Forecasts

To make predictions about the future, the Markov model needs to know what the weather is like today. So, you'll be asked to describe today's weather (the initial condition) in terms of the parameters you selected for your model (which could have been pre-trained or newly made).

An example screen:

<img width="622" alt="image" src="https://github.com/michahn01/markov_chain_weather_model/assets/113268235/630f71c3-5bf3-4732-9cad-8fb0191bad73">

You will then decide how many days into the future you want to forecast.

<img width="580" alt="image" src="https://github.com/michahn01/markov_chain_weather_model/assets/113268235/270f741c-7b9e-4889-9118-2d1708f7f007">

And voila! The model will make as many forecasts as you requested. 

<img width="461" alt="image" src="https://github.com/michahn01/markov_chain_weather_model/assets/113268235/ad391c57-d7fa-4e90-93ee-06531db59408">

## Using your Own Data
By default, the project uses weather data for San Jose from 2014 ~ 2022, gathered in Meteostat (https://meteostat.net/en/place/us/san-jose?s=KSJC0&t=2023-06-26/2023-07-03). If you would like to use your own data when training the model, write a CSV file with "date", "tavg", "tmin", "tmax", "prcp", and "wspd". Date should be structured as yyyy-mm-dd. You can include other tags, but the data-parser will ignore anything that it wasn't explicitly instructed to look for, so make sure to modify the data-parsing function (which is the classify_weather_info(weather_info) in [markov.py](markov.py) if you intend to introduce additional parameters.

Once you have your CSV file, copy and paste the file into the [data](data) subdirectory and rename the file paths in the appropriate functions in [forecast.py](forecast.py).
