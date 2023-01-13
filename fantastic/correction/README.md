# Correction Interface

## Setup

To properly setup your environment for the correction interface, use :
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
```
to update some libraries

Then, you need to modify
    `fantastic/paths.py`

It holds every path of the project.
Add your absolute path to BASE_DIR using the if else structure  

To print your working directory, you can use
    `pwd`

Then execute the file 
```
    app_init.py
```
It will generate an operation tracking file and store it as a csv

## Architecture

As every web application, it contains:
- a frontend folder: ./static containing the js and css files,
                     ./templates containing the html templates of the correction interface
- a backend folder: `convert.py` containing the conversion in a new type feature,
                    `html_processing.py` containing the html rendering feature,
                    `store.py` containing the creating, deleting, storing and loading files feature,
                    `tag_prediction.py` containing the tagging feature
- a `main.py` file: Containing all the routes of the application and its global functionning

## Run

To run it, execute in your command line either: 
- from the root folder of the project:
```
uvicorn fantastic.correction.main:app
```
- from the correction folder:
```
uvicorn main:app
```

## Keybinds

- left arrow key: show previous exercise
- right arrow key: show next exercise
- up arrow key: store as well converted
- down arrow key: store as incorrectly converted
- M key: store as incorrectly extracted
- P key: predict best tags
- enter key: convert to specified tag
- C key: display XML or HTML version
