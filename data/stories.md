## greet 1
* greet{"person": "Ali"}
  - slot{"person": "Ali"}
  - action_greet_user
  - utter_explain  

## happy path 1
* greet
  - action_greet_user
  - utter_explain
* findWinePair{"food":"steak"}
  - slot{"food":"steak"}
  - action_find_pair
* bye
  - utter_goodbye

## sad path 1
* greet
  - action_greet_user
  - utter_explain
* inform
  - utter_ask_food
* inform
  - utter_explain
* negative
  - action_negative

## sad path 2
* greet
  - action_greet_user
  - utter_explain
* findWinePair
  - utter_ask_food
* findWinePair{"food": "nicoise salad"}
  - slot{"food": "nicoise salad"}
  - action_find_pair

## say goodbye
* bye
    - utter_goodbye
  
## users_feedback
* describe
    - action_default_ask_rephrase

## interactive_story_1
* greet{"person": "Richard"}
    - slot{"person": "Richard"}
    - action_greet_user
    - utter_explain
* findWinePair{"food": "baingan bharta"}
    - slot{"food": "baingan bharta"}
    - action_find_pair
    - slot{"prev_suggestions": []}
    - slot{"params": {"food": "baingan bharta"}}
* findWinePair{"food": "fish curry"}
    - slot{"food": "fish curry"}
    - action_find_pair
    - slot{"prev_suggestions": []}
    - slot{"params": {"food": "fish curry"}}
* negative
    - action_default_ask_affirmation

## interactive_story_1
* greet
    - action_greet_user
    - utter_explain
* findWinePair{"food": "thyme"}
    - slot{"food": "thyme"}
    - action_find_pair

## interactive_story_2
* findWinePair{"food": "chicken roti"}
    - slot{"food": "chicken roti"}
    - action_find_pair
    - slot{"prev_suggestions": []}
    - slot{"params": {"food": "chicken roti, lamb roast"}}
* negative{"food": "chicken roti"}
    - slot{"food": "chicken roti"}
    - action_negative

## interactive_story_1
* greet
    - action_greet_user
    - utter_explain
* findWinePair{"food": "pork"}
    - slot{"food": "pork"}
    - action_find_pair
    - slot{"prev_suggestions": ["Ca' del Solo Vineyard", "Mediterra ", "Nasiakos "]}
    - slot{"params": {"food": "vegetarian, pork, chinese"}}
* findWinePair{"food": "braised beef"}
    - slot{"food": "braised beef"}
    - action_find_pair
    - slot{"prev_suggestions": ["Vigneto Corda della Briccolina"]}
    - slot{"params": {"food": "braised beef"}}
* affirmative
    - utter_needhelp
    - utter_explain
* bye
    - utter_goodbye

## interactive_story_1
* greet{"person": "Sahil"}
    - slot{"person": "Sahil"}
    - action_greet_user
    - utter_explain
* findWinePair{"food": "chicken marsala"}
    - slot{"food": "chicken marsala"}
    - action_find_pair
* findWinePair{"food": "chicken marsala"}
    - slot{"food": "chicken marsala"}
    - action_find_pair
    - slot{"prev_suggestions": []}
    - slot{"params": {"food": "chicken marsala"}}
* findWinePair{"food": "roast lamb"}
    - slot{"food": "roast lamb"}
    - action_find_pair
    - slot{"prev_suggestions": ["Two Passions", "Manor House", "Thelema "]}
    - slot{"params": {"food": "roast lamb"}}

## interactive_story_1
* greet
    - action_greet_user
    - utter_explain
* inform{"condition": "red", "variety": "cabernet sauvignon"}
    - slot{"condition": "red"}
    - slot{"variety": "cabernet sauvignon"}
    - action_inform
    - action_find_pair
* negative{"variety": "cabernet sauvignon"}
    - slot{"variety": "cabernet sauvignon"}
    - action_negative
   
## interactive_story_1
* inform{"variety": "merlot"}
    - slot{"variety": "merlot"}
    - action_inform
    - action_find_pair
    - slot{"prev_suggestions": ["Decoy Sonoma County", "Classic Collection", "Chelsea Goldschmidt Alexander Valley"]}
    - slot{"params": {"variety": "merlot"}}
    - slot{"neg_params": {}}
* negative{"variety": "merlot"}
    - slot{"variety": "merlot"}
    - action_negative
    - slot{"neg_params": {"variety": "merlot"}}
    - action_find_pair

## interactive_story_2
* inform{"variety": "merlot"}
    - slot{"variety": "merlot"}
    - action_inform
    - action_find_pair
    - slot{"prev_suggestions": ["Decoy Sonoma County", "Classic Collection", "Chelsea Goldschmidt Alexander Valley"]}
    - slot{"params": {"variety": "merlot"}}
    - slot{"neg_params": {}}
* negative{"variety": "merlot"}
    - slot{"variety": "merlot"}
    - action_negative
    - slot{"neg_params": {"variety": "merlot"}}
    - action_find_pair
    - slot{"prev_suggestions": ["Couronne et Lions", "Anemos", "Mythic River"]}
    - slot{"neg_params": {}}
   
## interactive_story_1
* greet{"person": "sahil"}
    - slot{"person": "sahil"}
    - action_greet_user
    - utter_explain
* inform{"condition": "dry", "variety": "chardonnay"}
    - slot{"condition": "dry"}
    - slot{"variety": "chardonnay"}
    - action_inform
    - action_find_pair
* findSimilarList{"variety": "cabernet sauvignon"}
    - slot{"variety": "cabernet sauvignon"}
