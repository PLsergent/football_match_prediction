# Football match prediction
Machine learning project that aims at predicting a football game output based on the game stats. We can then assess which metric has the most influence on the result and establish the **best scenario to win a match of football**.

## Dataset

- `data.csv`: exported data.
- `sport_monks_api.py`: used to collect the data needed for the training of the model
- `init_dataframe.ipynb`: used to init our dataframe with the data collected, and export a csv file.

## Usage

Requirement: python and poetry installed

```
poetry install
poetry run jupyter notebook ./init_dataframe.ipynb
```