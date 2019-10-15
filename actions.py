from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

# Import rasa functions
from rasa_sdk import Action
from rasa_sdk.events import SlotSet

# Data handling
import pandas as pd
# Text handling
import string
# Import re for text search and pattern recognition
import re
from re import search
# Import numpy for calculating multidim arrays 
import numpy as np
# Import sqlite3 for returning search queries
import sqlite3
# Import pickle for retrieving saved objects
import pickle
# Import other packages
import json
import logging

# Import Gensim packages
import gensim
from gensim import corpora
from gensim.models import LdaModel, LdaMulticore
from gensim.similarities import Similarity

logger = logging.getLogger(__name__)


# Create references

# Load LDA model
lda_model_tfidf = LdaModel.load('./lda_data/lda_model_tfidf.model')

# Load the BoW model
bow_corpus = corpora.MmCorpus('./lda_data/bow_corpus.mm')

# load the index
index = Similarity.load('./lda_data/wine.index')

# Create indices, a vector of wine names to position in data
wine_data = pd.read_csv('./lda_data/df_out_data.csv',index_col=0)
wine_best = wine_data.loc[wine_data['points']>90,['winery','variety','designation_replace']].sample(5)


indices = pd.Series(wine_data.index,index=wine_data.designation_replace).drop_duplicates()

indices.index.names=['name']


# Function that takes in wine name as input and outputs most similar wines
# provided by datacamp

def recommend(name, model=lda_model_tfidf):
    
    # Get the index of the wine that matches the title
    idx = indices[name].min()
    
    # Get vector representation
    vec=model[bow_corpus[idx]]
    
    # Perform a similarity query against the corpus
    sims = index[vec]

    # Sort the wine based on the similarity scores
    sims = sorted(enumerate(sims), key=lambda x: x[1], reverse=True)

    # Get the scores of the 10 most similar wines
    sims = sims[1:5]

    # Get the wine indices
    wine_indices = [i[0] for i in sims]

    # Return the top 5 most similar wines
    return wine_data[['designation_replace','variety','winery','province','country','description_replace']].iloc[wine_indices]


def load_obj(name ):
        with open('obj/' + name + '.pkl', 'rb') as f:
            return pickle.load(f)
    
map_dict=load_obj('map_dict')
patterns=load_obj('patterns_dict')

def replaceNone(val,asiterator={}):
    '''A None type is replaced with an empty dictionary or list as specified. 
    Other values are returned normally. 
    None types and empty dict or lists are considered equal so the last value
    is always returned in a clash '''
    return val or asiterator

def correct(string):
        corrected_values= []
        for value, err_pattern in map_dict.items():
            # Check if the pattern occurs in the message 
            try:
                lookup=string.text
            except:
                lookup=string
            # Search for the error pattern and return the corrected value
            if err_pattern.search(lookup.lower()):
                #corrected_values=value
                corrected_values.append(value)
                
        return corrected_values
    
# Define a function to find the entity type for corrected items
def entity_type(word):
    matched_entity = None
    for entity, pattern in patterns.items():
        # Check if the pattern occurs in the message 
        try:
            lookup=word.text
        except:
            lookup=word
            lookup=re.sub('[1-9]','_num',lookup)
        if pattern.search(lookup):
            matched_entity = entity
            
    return matched_entity

# Formatting
negSQLFormats=[
    "{} <> '{}'",
    "{} NOT IN {}"
]

# Initialize empty dictionaries and lists
params, entities, alt_params = {}, [], {}

# Define update_params as an evolving understanding or parameters
def update_params(params,entities,forget={}):

    excluded=[]; alt_params={}
    
    # Generate SQL script to explicitly exclude all entities in negative list
    if forget:
        
        # len of elements of a multidimensional list does not work as intended
        # (i.e. to get number of elements of each list)
        # instead we're using size from numpy
        lengths= [(k,np.size(*v)) for k,*v in forget.items()]
        
        invalid= [k for k,v in lengths if v<=1]
        
        # handle entity with multiple values
        negfilters = [negSQLFormats[1].format(k,*v) for k,*v in forget.items() if k not in invalid]

        # add removed elements i.e entities with one value to filters
        
        if invalid:
            remove=[(negSQLFormats[0].format(k,*unwanted)) for k,
                    *unwanted in forget.items() if k in invalid]
            
            negfilters.append(remove[0])
    else:
        negfilters=[]
    
    # Ensure that params and entities do not hold any values they are supposed to forget
    
    if any(forget):
        for key, value in forget.items():
            
            # One entity can have multiple values - food: (cheeseburger, fries, pickle).
            # Keep all values except those we are explicitly told to forget
            if np.size(params.get(key).split(', '))>1:
                params[key]=', '.join([val for val in set(params[key].split(', ')) if val not in value ])
            
            # Simple equality then remove
            if params.get(key) == value:
                # return value and remove it from params
                params.pop(key)
                
        # Drop the values from entities 
        entities=[e for e in entities if e['entity'] not in forget.keys() or e['value'] not in forget.values()]
                    
    for ent in entities:
        
        # prevent duplicate values of the same entity
        if ent["entity"] in params.keys() and ent["entity"] != str(ent["value"]):     
            params[ent["entity"]] = params[ent["entity"]] + ', '+ str(ent["value"])
        else:
            params[ent["entity"]] = str(ent["value"])
            
        terms=[t for t in set(params[ent["entity"]].split(', ')) if t not in ["and", "or", "maybe"]] 

        # alternative params is a list of tokens in the entity
        if np.size(terms)<2:
            alt_params[ent["entity"]] = str(ent["value"])
        else:
            alt_params[ent["entity"]] = tuple(terms)                        

        params[ent['entity']]=', '.join(terms)
        
    negfilters= replaceNone(negfilters,[])
    
    return params, alt_params, negfilters


def list_wines(params,alt_params={},
               excluded=[],
               bug_testing="ALL"):
    
    # Create the base query
    query = 'SELECT *, RANK() OVER(PARTITION BY food ORDER BY variety) as cat_count FROM pairings'
 
    # Add filter clauses for each of the parameters
    if len(params) > 0:
        if alt_params:
            # alt_params is only created if there are multiple values assigned to some entity
            # it will only contain entities found in the message
      
            ''' Handle multiple values assigned to a single entity'''
            
            # len of elements of a multidimensional list does not work as intended
            # (i.e. to get number of elements of each list)
            # instead we're using size from numpy
            lengths= [(k,np.size(*v)) for k,*v in alt_params.items()]
            invalid= [k for k,v in lengths if v<=1]
            
            # filters are used to generate SQL 
            filters = ["{} in {}".format(k,*v) for k,*v in alt_params.items() if k not in invalid]
            

            ''' Handle entity value pairs'''
            # add removed elements to to filters
            if invalid:
                filters.append(" and ".join(["{}=?".format(k) for k in alt_params.keys() if k in invalid]))
                t = tuple([v for k,v in alt_params.items() if k in invalid])    
                        
        else:
            filters = ["{}=?".format(k) for k in params]
            t=tuple(params.values())

        query += " WHERE " + " and ".join(filters) 
      
    
        # Add any items to exclude to the query     
        query +=  "".join([' and {}'.format(e) for e in excluded])
    
    else:
        # Add any items to exclude to the query when params are not given but exclusions are given
        if excluded:
            query += " WHERE " + " and ".join([e for e in excluded])
   
    # Open connection to DB      
    conn = sqlite3.connect('./sqlite/db/pairings.db')
        
    # Create a cursor
    c = conn.cursor()
         
    # bug testing
    if bug_testing == "ALL":
        print("params: " + str(params) + '\n')
        print("alt_params: " + str(alt_params) + '\n')
        print("query: " + str(query) + '\n')   
    #############

    # Execute the query
    try:
        c.execute(query) 
    except:
        c.execute(query, t)
                
        # bug testing
        if bug_testing!="NONE":
            print("tuple: " + str(t) + '\n')
        #############
                
    # Return the results
    return c.fetchall(), c.close()


    
class  ActionFindWinePair ( Action ):
    
    
    def name(self):
        return "action_find_pair"

    def run(self, dispatcher, tracker, domain):
                                    
        check_variables= ['food','variety','condition','name'] 

        entities = tracker.latest_message.get("entities", [])

        entities = [{'entity':str(e["entity"]),'value':str(e["value"])} for e in entities if str(e["entity"]) in check_variables and e["value"] != None ]
        
        #dispatcher.utter_message("{}".format(params))

        if entities==[]:
            
            message=tracker.latest_message.text.lower()
            corrected_values=correct(message)
            entities= [{'entity':entity_type(val),
                        'value':val}
                       for val in corrected_values if val in message]
                        
            #dispatcher.utter_message("entities found are: {}".format(entities))
            

            # Call update params to add or modify search parameters
            params=replaceNone(tracker.get_slot("params"))
            forget=replaceNone(tracker.get_slot("neg_params"))
            
            params,alt_params,excluded= update_params(params,entities,forget)
            
            logger.debug(alt_params)
            
            # Find matching wines
            
            results=[r for r in list_wines(params,alt_params,excluded)[0]]
            
            names = [r[1] for r in sorted(results, key=lambda x: x[-1])]
            n = min(len(results), 3)
            suggestions = names[:3]

            # Engage bot to respond with search results
            #dispatcher.utter_message("{}".format(suggestions))
            
            dispatcher.utter_template("utter_pair", tracker)
            
            # We want to output in a block format with the food and suggested  
            recommend_list=[("{}: \n" + "try a {} like {}").format(r[3],r[2],r[1]) for r in  sorted(results, key=lambda x: x[-1])]
            
            recommend_script="with "+ "\nfor ".join(recommend_list[:3])
            
            dispatcher.utter_message(recommend_script)
            
            return [SlotSet("prev_suggestions", suggestions),SlotSet("params", params),SlotSet("neg_params", {})]

        
class  ActionNegative ( Action ):
    
    def name(self):
        return "action_negative"
    
    def run(self, dispatcher, tracker, domain):
        
        check_variables= ['food','variety','condition','name'] 

        entities = tracker.latest_message.get("entities", [])

        entities = [{'entity':str(e["entity"]),'value':str(e["value"])} for e in entities if str(e["entity"]) in check_variables and e["value"] != None ]
        
        #entities= [e for e in entities if str(e["entity"]) in check_variables and e["value"] != None  ]   
        
        forget = {}
        
        for ent in entities:
            
            # prevent duplicate values of the same entity
            if ent["entity"] in forget.keys() and ent["entity"] != str(ent["value"]):
                forget[ent["entity"]].append(str(ent["value"]))
            else:
                forget[ent["entity"]] = [str(ent["value"])]
        
        forget={k:tuple(v) if np.size(v)>1 else str(v[0]) for k,v in forget.items()}
        
        dispatcher.utter_message("Ok I won't include these items in the search")
        
        description=[', '.join(v[:]) if np.size(v)>1 else v for v in forget.values()]
        message=', '.join(description)
        dispatcher.utter_message("{}".format(message))
        
        return [SlotSet("neg_params", forget)]

    
class ActionGreetUser(Action):
    
    """Greets the user"""

    def name(self):
        
        return "action_greet_user"

    
    def run(self, dispatcher, tracker, domain):

        intent = tracker.latest_message["intent"].get("name")

        name_entity = next(tracker.get_latest_entity_values("person"), None)

        if name_entity is not None:
            
            dispatcher.utter_template("utter_greet_name", tracker, person=name_entity)
            
            return []

        else:
            
            dispatcher.utter_template("utter_greet", tracker)

            return []    

class ActionInform ( Action ):
    
    def name(self):
        return "action_inform"

    def run(self, dispatcher, tracker, domain): 
        
        message=tracker.latest_message.get("text")
        
        intent_ranking = tracker.latest_message.get("intent_ranking", [])
        
        logger.debug(intent_ranking)
        
        title={
            "greet": "I just wanted to say hello",
            "negative":"I am unhappy or want something different",
            "findWinePair":"I wanted to search for a wine",
            "bye":"I was just leaving",
            "affirmative":"You found what I was looking for",
            "findSimilarList":"I wanted to find a wine similar to something I already like",
            "other": "I want to see more options",
            "describe":"I would like to describe the problem"
        }
        
        # Keep the most likely intents based on the ranking scores
        
        if len(intent_ranking)>1:
            
            state=replaceNone(tracker.get_slot("state"),0)
            
            message_title=["Sorry, but I'm not sure how to help", 
                           "let's try some more options"]
            n=min(state,len(message_title)-1)
            
            intent_ranking=intent_ranking[state+1:]
            
            intents= [intent.get("name", "") for intent in intent_ranking[0:2]]
            
            if len(intents)==1:
                intents.append("describe")
            
            # Keep entities for the variables we care about         
            entities = tracker.latest_message.get("entities", [])

            check_variables= ['food','variety','condition','name'] 
            
            ents=  {e["entity"]: e["value"] for e in entities if e["entity"] in check_variables}
            #[x.get("entity"): x.get("value") for x in entities if x.get("entity") in check_variables]
            
            #entities_json = json.dumps(ents)

            responses={
                (0,intents[0]):(title[intents[0]],intents[0],1),
                (1,intents[1]):(title[intents[1]],intents[1],2),
                (2,"other"):(title["other"],"inform",2)
            }
            
            buttons = []
            
            '''
            for intent in first_intent_names:
                logger.debug(intent)
                logger.debug(entities)
                buttons.append(
                    {
                        "title": intent,
                        "payload": "/{}{}".format(intent, entities_json),
                    }
                )
            '''   

            for intent in intents:
                logger.debug(intent)
                logger.debug(entities)

                bot_message,intent,state= responses.get((state,intent))

                buttons.append(
                    {
                        "title": bot_message,
                        "payload": "/{}".format(intent),
                    }
                )

            bot_message,intent,state= responses.get((state,"other"))

            buttons.append(
                {
                    "title": bot_message,
                    "payload": "/{}".format(intent),
                }
            )
            
            dispatcher.utter_button_message(message_title[n], buttons=buttons)

            return [SlotSet("state", state)]
        
        dispatcher.utter_message("intents rankings: {}".format(intent_ranking))
        
        return []

    
class ActionSimilar ( Action ):
    
    ''' Find similar wines to something selected or chosen'''
    
    def name(self):
        return "action_find_similar"

    def run(self, dispatcher, tracker, domain): 
                
        suggestions = replaceNone(tracker.get_slot("prev_suggestions"),[])
        
        name = replaceNone(tracker.get_slot("name"),[])
        
        find_similar_list= name + suggestions
        
        find_similar_list=[name for name in find_similar_list if name in indices]
        
        
        if find_similar_list != []:
            
            find_similar_list=iter(find_similar_list)
        
            resultsdf=pd.Dataframe

            resultsdf=recommend(next(find_similar_list))
            
            
            
            name_list = list(resultsdf.designation_replace)
            
            variety_list = list(resultsdf.variety)
            
            winery_list = list(resultsdf.winery)
            
            result_list=list(zip(resultsdf.winery, resultsdf.variety, resultsdf.designation_replace))
            
            
            dispatcher.utter_message("{} is a really great choice.. a {} from {}".format((name_list[0],variety_list[0],winery_list[0])))
            
            SlotSet("winery", winery_list[1])
            
            SlotSet("name", name_list[1])
            
            SlotSet("variety", variety_list[1])
            
            dispatcher.utter_template("utter_similar", tracker)
            
            # We want to output in a block format with the best matching wines from the data
            recommend_list=[("{} makes a really good {}" + "\nlook for the {} label").format(r[0],r[1],r[2]) for r in  result_list[1:]]
            
            recommend_script="\n".join(recommend_list)
            
            dispatcher.utter_message(recommend_script)

            
            return [SlotSet("winery", None), SlotSet("name", None), SlotSet("variety", None)]
            
           
        else:
            
            dispatcher.utter_message("Sorry! I was not able to find anything like that\n Here are some favorites".format(name))
            
            result_list=list(zip(wine_best.winery, wine_best.variety, wine_best.designation_replace))
            
            recommend_list=[("{} try the {}" + "\nlook for the {} label").format(r[0],r[1],r[2]) for r in  result_list[:3]]
            
            recommend_script="from "+"\n".join(recommend_list)
            
            dispatcher.utter_message(recommend_script)
            
                        
            return []
        
    
