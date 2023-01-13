# Cartable Fantastique Fall 2021 p1

## Setup

To properly setup your environment for this project, use :
```
    pip install -e ./
```
it will launch the setup and install all packages includin cartable-fantastique
```
    python -m spacy download fr_core_news_sm
```
and
```
    python
    import nltk
    nltk.download('punkt')
    exit()
```
to update some libraries

Then, you need to modify
    `fantastic/paths.py`

It holds every path of the project.
Add your absolute path to BASE_DIR using the if else structure  

To print your working directory, you can use
    `pwd`

## Architecture

The project is divided in multiple parts:

### tagging

Automatic tagging of exercise using ML.

You can create and prepare data, create and train or load models, evluate models and predict outputs

* data/ contains every data csv
* models/ contains every models
* prepare_data.py: generate dataframe and can save them to csv, execute function get_data() to do so
there are two main types of data: raw or without xml tags
you can label with most popular categories or only big categories
* train_models.py : create, train, load, evaluate models and use them to predict outputs

### jinja

HTML templating.

HTMLs of exercises are generated using templates located in jinja folder using jinja (in fantastic/exercises folder). There is one template by big category of exercise.

### fantastic

Core of the project.

#### /etl

Extract, Transform, Load data.
Extract from every xmls and the excel with tags
Transform the data by merging two sources and removing useless infos
Load it into json

To run it, execute with python the file:
```
fantastic/etl/pipeline.py
```

#### /correction

Correction interface.

You can visualize every exercise, change the tag of every exercise, say it is wrongly extracted, converted or well converted.

#### /exercises

Conversion of exercises.

The global architecture is explained in resources/SoutenanceFinale.pdf and in classes_demo_DVP.png

There is one folder by big cat, and one file per type of exercise.
* ../main.py is the main pipeline to execute to generate exercises
* utils.py contains useful functions
* exercise.py contains the parent class Exercise
* data.cfg is the config file
