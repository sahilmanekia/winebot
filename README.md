# winebot
a content and collaborative filtering bot for recommendations and pairings in an easy conversational style

run fork and download files to a project folder. 

move lda_data out of the data folder and into the main directory, or otherwise change the relevant references in actions.py

## 1 Open a cmd or anaconda terminal and then start the actions server with
python -m rasa_core_sdk.endpoint --actions actions

## 2 Open a cmd or anaconda terminal and then start the rasa session 
### to interact and provide corrections
rasa interactive 
### to run in the shell
rasa shell
### to train model
-rasa train OR
-rasa train core OR
-rasa train nlu


# parameters
### config:
spacy/rasa nlu pipeline

### training_data
a JSON dictionary of conversations in the rasa nlu pipeline used for training the chatbot 

### params: [default None ]
a dictionary of parameters interpreted from the conversation/text input, and passed to the SQl backend

### alt_params: [default None]
a supplemental dictionary of parameters activated when the original search fails to find any results. This partitions text to try to broaden the search within the supplied parameters

### excluded [default None]
search results that explicitly excluded from future results

### message [default None]
the user message which needs to be interpreted

# dependencies
### Python packages
-rasa_nlu(spacy) -rasa_core v0.9.6 -spacy -logging -io -json -warnings -pandas -mathplotlib -re -random -numpy -sqllite3 

### Python models
-en_core_web_md
