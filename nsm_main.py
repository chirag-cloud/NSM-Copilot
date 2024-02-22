#Library imports
import re
from flask import Flask,jsonify,request
from flask_cors import cross_origin
import json
import numpy as np
import os
from datetime import datetime
import pandas as pd
from openai.embeddings_utils import get_embedding, cosine_similarity
import csv
import tiktoken
import ast

#Local file Imports
from openai_crendentials import openai_keys
from redis_credentials import get_redis_object
from promptRoadMap import returnRoadmapPrompt
from prompt_createNSM import returnCreateNSMContext


app = Flask(__name__)

#global variables
redisconvo =[]
openai = openai_keys()
Redis = get_redis_object()

#RAG
'''
    Helps to create embeddings, It Reads a CSV file containing a column 'id', tokenize the 'id' values,
    filters out rows with token counts exceeding 8192, and creates embeddings
    using the 'text-embedding-ada-002' engine. Saves the resulting array data
    as a NumPy file.

    Parameters:
    - csv_file_path (str): Path to the CSV file.

    Returns:
    None
'''
def createEmbeddings(csv_file_path):
    df=pd.read_csv(os.path.join(os.getcwd(),csv_file_path))
    df["id"] = df["id"].astype(str)
    tokenizer = tiktoken.get_encoding("cl100k_base")
    df['n_tokens'] = df["id"].apply(lambda x: len(tokenizer.encode(x)))
    df = df[df.n_tokens<8192]
    df['ada_v2'] = df["id"].apply(lambda x : get_embedding(x, engine = 'text-embedding-ada-002'))
    array_data = df.to_numpy()
    np.save("./../conversation/embedded_array.npy", array_data)
    # df.to_csv("./../conversation/embedded_convo.csv")


'''
    Removes last row from a file

    Parameters:
    - path (str): Path to the CSV file where last row needs to be removed

    Returns:
    None
'''
def remove_last_row(path):
    with open(path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        data = list(reader)

    data = data[:-1]
    
    with open(path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)

'''
    Save conversation logs to a CSV file.

    Parameters:
    - id: The ID associated with the conversation.
    - conversation: The content of the conversation.
    - is_complete: A boolean indicating whether the conversation is complete.
    - freshStart: A boolean indicating whether conversation is a fresh start.
'''
def saveLogs(id, conversation, is_complete,freshStart):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if the conversation is already in the CSV file
    csv_file_path = './../conversation/convo.csv'
    # rows = []
    last_row_contents = None
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            last_row_contents = row
            # rows.append(row)

    # Write the conversation data to the CSV file
    with open(csv_file_path, 'a', newline='') as file:
        writer = csv.writer(file)

        # Handle incomplete conversations
        if not is_complete:
            if freshStart:
                writer.writerow([id, conversation,timestamp, 'Incomplete'])
            else:
                if last_row_contents and last_row_contents[-1] == "Incomplete":
                    remove_last_row(csv_file_path)
                    writer.writerow([id, conversation, timestamp, 'Incomplete'])
                else:
                    writer.writerow([id, conversation, timestamp, 'Incomplete'])
        else:
            writer.writerow([id, conversation, timestamp, 'Complete'])

''' 
    Save NSM data to a CSV file & create embeddings out of it for RAG.

    Parameters:
    - id: The identifier associated with the data entry.
    - nsm: NSM data (optional).
    - hasNSM: Flag indicating the presence of NSM (optional).
    - hasEpics: Flag indicating the presence of epics (optional).
    - hasGeneratedRoadmap: Flag indicating whether a roadmap has been generated (optional).
    - idea: Idea associated with the data entry (optional).
    - roadmap: Roadmap data (optional).
    - selectedEpics: Selected epics data (optional).
    - allNSM: All NSM data (optional).
'''
def saveNSMData(id, nsm=None, hasNSM=None, hasEpics=None, hasGeneratedRoadmap=None, idea=None,
              roadmap=None, selectedEpics=None,allNSM=None):
    csv_file = "./../conversation/embedded_convo.csv"
    existing_data = {}
    print("ID in embeddings",id)
    try:
        with open(csv_file, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                existing_data[row['id']] = row
    except FileNotFoundError:
        pass

    # Check if the ID already exists in the data
    if str(id) in existing_data:
        # Update existing data with new data for the specific ID
        updated_data = {
            'id': str(id),
            'nsm': nsm if nsm is not None else existing_data[str(id)]['nsm'],
            'hasNSM': hasNSM if hasNSM is not None else existing_data[str(id)]['hasNSM'],
            'hasEpics': hasEpics if hasEpics is not None else existing_data[str(id)]['hasEpics'],
            'hasGeneratedRoadmap': hasGeneratedRoadmap if hasGeneratedRoadmap is not None else existing_data[str(id)]['hasGeneratedRoadmap'],
            'idea': idea if idea is not None else existing_data[str(id)]['idea'],
            'roadmap': roadmap if roadmap is not None else existing_data[str(id)]['roadmap'],
            'selectedEpics': selectedEpics if selectedEpics is not None else existing_data[str(id)]['selectedEpics'],
            'allNSM': allNSM if allNSM is not None else existing_data[str(id)]['allNSM']
        }
        existing_data[str(id)].update(updated_data)
    else:
        # Add new entry if the ID doesn't exist
        new_entry = {
            'id': str(id),
            'nsm': nsm,
            'hasNSM': hasNSM,
            'hasEpics': hasEpics,
            'hasGeneratedRoadmap': hasGeneratedRoadmap,
            'idea': idea,
            'roadmap': roadmap,
            'selectedEpics': selectedEpics,
            'allNSM':allNSM
        }
        existing_data[str(id)] = new_entry

    # Write the updated data back to the CSV file
    fieldnames = existing_data.values().__iter__().__next__().keys()
    with open(csv_file, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Write header
        writer.writeheader()

        # Write rows
        writer.writerows(existing_data.values())
    createEmbeddings(csv_file)

"""
    Search for similar id in embeddings based on a user id and get corresponding results.

    Parameters:
    - user_query: The query for searching in embeddings.

    Returns:
    - result: The most relevant entry based on the search.
"""
def searchInEmbeddings(user_query):
    max_similarity_threshold = 0.88
    embedded_array = np.load("./../conversation/embedded_array.npy", allow_pickle=True)
    df = pd.DataFrame(embedded_array, columns=["id","nsm","hasNSM","hasEpics","hasGeneratedRoadmap","idea","roadmap","selectedEpics","allNSM","n_tokens","ada_v2"])
    embedding = get_embedding(
        user_query,
        engine="text-embedding-ada-002" # engine should be set to the deployment name you chose when you deployed the text-embedding-ada-002 (Version 2) model
    )
    df["similarities"] = df.ada_v2.apply(lambda x: cosine_similarity(x, embedding))

    res = (
        df.sort_values("similarities", ascending=False)
        .head(3)
    )
    print(res)
    result = res.iloc[0]
    if(result['similarities'] < max_similarity_threshold):  #replace with variable
        result = "na"
    print("Answer based on search",result['id'])
    return result

"""
   To keep new NSM generated, Updated previous NSMs

    Parameters:
    - user_query: The query for searching in embeddings.

    Returns:
    - result: The most relevant entry based on the search.
"""
def update_nsm(new_nsm,allNSM):
    # Get the current NSM queue
    redis_nsm_queue_length = 3
    nsm_queue = allNSM['nsm']

    # Check if the new NSM is different from the current one
    if not nsm_queue or new_nsm != nsm_queue[-1]:
        # Append the new NSM to the queue
        nsm_queue.append(new_nsm)

        # If the queue exceeds three elements, remove the oldest one
        if len(nsm_queue) > redis_nsm_queue_length:
            nsm_queue.pop(0)

"""
Save NSM (North Star Metric) data in Redis.

Parameters:
- id: User email id.
- redisconvo: Serialized conversation data stored in Redis.
- nsm: Current NSM
- hasNSM: Flag indicating the presence of NSM.
- hasEpics: Flag indicating the presence of epics.
- hasGeneratedRoadmap: Flag indicating whether a roadmap has been generated.
- kill: Flag indicating whether to terminate the conversation.
- isNew: Flag indicating whether the entry is a new conversation.
- idea: idea presented at start of conversation.
"""
def saveNSMinRedis(id,redisconvo,nsm,hasNSM,hasEpics,hasGeneratedRoadmap,kill,isNew,idea):
    print("INSIDE SAVE IN REDIS")
    serialized_conversation = json.dumps(redisconvo)
    if(kill):
        # prevConvo = json.dumps(redisconvo)
        saveLogs(id,serialized_conversation,True,False)

    existing_value = Redis.get(id)
    if existing_value is not None:
        existing_value = json.loads(existing_value)

    if not isNew:
        print("inside false is new")
        idea = existing_value.get('idea', idea)
        print("inside idea not none and idea is:",idea)
    try:
        if not existing_value['allNSM']['nsm']:
            print("inside not ALL NSM")
            allNSM = {'nsm': []}
        else:
            print("INSIDE YES ALL NSM")
            allNSM = existing_value['allNSM']

        if(existing_value['hasNSM']):
            update_nsm(existing_value['nsm'],allNSM)
            print("INSIDE UPDATE ALL NSM:")
            print("UPDATED NSM:",allNSM['nsm'])
    except Exception as err:
        print("ERR", err)
        allNSM = {'nsm': []}

    value = {
        'conversation': serialized_conversation,
        'nsm':nsm,
        'hasNSM':hasNSM,
        'hasEpics':hasEpics,
        'hasGeneratedRoadmap':hasGeneratedRoadmap,
        'idea':idea,
        'selectedEpics':"",
        'allNSM': allNSM
        # 'prevConversation':prevConvo
    }
    Redis.set(id, json.dumps(value))
    print("Convo saved in redis successfully")

"""
    Save roadmap data in Redis.

    Parameters:
    - id: User email id.
    - redisconvo: Serialized conversation data stored in Redis.
    - roadmaparray: Array containing Epic Roadmap .
    - RoadmapPresent: Flag indicating whether a roadmap is created or not.
"""
def saveRoadMapinRedis(id,redisconvo,roadmaparray,RoadmapPresent):
    print("INSIDE SAVE IN REDIS")
    serialized_conversation = json.dumps(redisconvo)
    redisdata = Redis.get(id)
    if redisdata is None:
        print("Inside redis none")
        value = {
        'conversation': serialized_conversation,
        'roadmap':roadmaparray
        }
        Redis.set(id, json.dumps(value))
    else:
        redisdata = json.loads(redisdata)
        redisdata['conversation'] = serialized_conversation
        if(RoadmapPresent):
            redisdata['roadmap'] = roadmaparray
        Redis.set(id, json.dumps(redisdata))
    print("Convo saved in redis NSM successfully")

"""
    Create an array of roadmap by separating entries from a formatted Epic Roadmap string generated by AI.
    Uses Regular expression to mach quarter, Epic Header, Epics details, is_Edited remains False when generating roadmap first time
    Parameters:
    - roadmap_string: The formatted roadmap string.

    Returns:
    - roadmap_array: An array of roadmap entries.
"""
def create_roadmap_array(roadmap_string):
    quarters = roadmap_string.split("\n\nQuarter ")
 
    id = 1
    roadmap_array = []
 
    for quarter in quarters:
        lines = quarter.strip().split("\n")
        quarter_header = lines[0].replace(":", "")
 
        for i in range(1, len(lines)):
            parts = re.split(r':\s', lines[i], 1)  # Use re.split to split only once
 
            step_header = re.sub(r'^\d+\.\s', '', parts[0])
            step_details = parts[1] if len(parts) > 1 else ''  # Handle the case where there are no details
            
            if step_header:
                roadmap_array.append({
                    "id": id,
                    "quarter": f"Quarter {quarter_header}",
                    "roadmap_header": step_header,
                    "roadmap_details": step_details,
                    "isEdited":False
                })
                id += 1
 
    return roadmap_array

"""
    Generate Epic Roadmap based on NSM generated previously.

    Endpoint: /generateEpicRoadmap

    Request JSON Parameters:
    - isNew: Flag indicating whether it's a new conversation.
    - message: User input message.
    - email: id

    Returns:
    - JSON response containing RoadMapFlag and Generated Roadmap for first time.
"""
@cross_origin(origin='*')
@app.route('/generateEpicRoadmap',methods=['POST'])
def generateEpicRoadmap():
    request_data=request.get_json()
    if(request_data['isNew'] == "yes"):
        try:
            conversation =[]
            id = request.headers.get('email')
            embeddingsId = id
            search_id = id + "_NSMCopilot"
            redisData = Redis.get(search_id)
            idea = json.loads(redisData)['idea']
            NSM = json.loads(redisData)['nsm']
            prevConvo = json.loads(json.loads(redisData)['conversation']) # search_convo(search_id)
            epic_roadmap_prompt =  returnRoadmapPrompt(NSM,idea,prevConvo) 
            conversation.append(epic_roadmap_prompt)
            response = openai.ChatCompletion.create(
            engine="chatgpt", # The deployment name you chose when you deployed the GPT-35-Turbo or GPT-4 model.
            messages=conversation[0],
            temperature=0
            )
            conversation[0].append({"role": "assistant", "content": response['choices'][0]['message']['content']})
            id = id +"_withNSM"
            roadmaparray = create_roadmap_array(response['choices'][0]['message']['content'])
            saveRoadMapinRedis(id,conversation,roadmaparray,True)
            saveNSMData(embeddingsId, roadmap=roadmaparray, hasEpics=True, hasGeneratedRoadmap=True)
            data = json.loads(Redis.get(search_id))
            data['hasGeneratedRoadmap'] = True
            Redis.set(search_id, json.dumps(data))
            headers = {'Access-Control-Allow-Origin': '*'}
            json_data = json.dumps({"RoadMapFlag":True,"Result": roadmaparray})
            return json_data, 200, headers     
        except Exception as err:
            print("ERROR!! -",err)
            return json.dumps({"Result":"Server is currently overloaded. Please try again"})
    else:
        message = request_data['message']
        id = request.headers.get('email')
        # roadMap = request_data['needRoadMap']
        id = id + "_withNSM"
        redisconvo = json.loads(json.loads(Redis.get(id))['conversation'])
        if message.lower()=="kill":
            saveRoadMapinRedis(id,redisconvo,"",False)
            print("******Closing conversation*********")
            return "Thankyou for your time!!"
        else:
            try:
                # RoadMapFlag = False
                # if(roadMap):
                #     selected_epics = request_data['selectedEpics']
                #     message = returnRoadmapPrompt(selected_epics)
                #     RoadMapFlag = True
                redisconvo[0].append({"role": "user", "content": message})   
                response = openai.ChatCompletion.create(
                    engine="chatgpt", # The deployment name you chose when you deployed the GPT-35-Turbo or GPT-4 model.
                    messages=redisconvo[0],
                    temperature=0
                    )
                redisconvo[0].append({"role": "assistant", "content": response['choices'][0]['message']['content']})
                print("\n" + response['choices'][0]['message']['content'] + "\n")
                json_data = json.dumps({"RoadMapFlag":False,"Result": response['choices'][0]['message']['content']})
                # convo_data = json.dumps(redisconvo)
                saveRoadMapinRedis(id,redisconvo,"",False)
                headers = {'Access-Control-Allow-Origin': '*'}
                return json_data, 200, headers
            except Exception as err:
                print("ERROR:",err)
                return json.dumps({"Result":"Server is currently overloaded. Please try again"})

"""
    Create North star metric based on user idea and by asking about each paradigm.

    Request JSON Parameters:
    - isNew: Flag indicating whether it's a new conversation.
    - message: User input message.
    - idea: Idea associated with the conversation.
    
    Returns:
    - JSON response containing summary, Result.
"""
@cross_origin(origin='*')
@app.route('/non-nsm',methods=['POST'])
def create_nsm():
    min_idea_word_length = 4
    max_initial_response_length = 1500
    request_data=request.get_json()
    if(request_data['isNew'] == "yes"):
        try:
            conversation =[]
            id = request.headers.get('email')
            id = id + "_NSMCopilot"
            idea = request_data['idea']
            create_nsm_prompt = returnCreateNSMContext(idea)
            if(len(idea.split()) < min_idea_word_length):
                json_data = json.dumps({"summary":False,"Result": "Sorry I need more details. Could you please elaborate your idea?","idea":False})
                headers = {'Access-Control-Allow-Origin': '*'}
                return json_data, 200, headers   
            conversation.append(create_nsm_prompt)
            response = openai.ChatCompletion.create(
            engine="chatgpt", # The deployment name you chose when you deployed the GPT-35-Turbo or GPT-4 model.
            messages=conversation[0],
            temperature=0
            )
            
            # If Condition to handle when GPT asks all the Paradigms at once
            if(len(response['choices'][0]['message']['content'])>max_initial_response_length):
                conversation[0].append({"role": "assistant", "content": response['choices'][0]['message']['content']})
                conversation[0].append({"role": "user", "content": """Let's break down the discussion into individual paradigms. Please respond to each paradigm one at a time, and feel free to proceed without apologizing for 
                                    asking multiple questions.Start with asking first paradigm now"""})
                response = openai.ChatCompletion.create(
                        engine="chatgpt", # The deployment name you chose when you deployed the GPT-35-Turbo or GPT-4 model.
                        messages=conversation[0],
                        temperature=0
                    )
                # print(response)
                print("AFTER cutting response from GPT:","\n" + response['choices'][0]['message']['content'] + "\n") 
            conversation[0].append({"role": "assistant", "content": response['choices'][0]['message']['content']})
            
            saveLogs(id,conversation,False,True)
            json_data = json.dumps({"summary":False,"Result": response['choices'][0]['message']['content']})
            saveNSMinRedis(id,conversation,"",False,False,False,False,True,idea)
            headers = {'Access-Control-Allow-Origin': '*'}
            return json_data, 200, headers     
        except Exception as err:
            print("ERROR!! -",err)
            return json.dumps({"summary":False,"Result":"Server is currently overloaded. Please try again"})
    else:
        message = request_data['message']
        id = request.headers.get('email')
        embeddingsId = id
        id = id + "_NSMCopilot"
        data = json.loads(Redis.get(id))
        redisconvo = json.loads(data['conversation'])
        idea = data['idea']
        allNSM = data['allNSM']
        if message.lower()=="kill":
            # GPT call to get NSM created by user at end of conversation
            redisconvo[0].append({"role": "user", "content": "Print North Star Metric in this format  NSM:(exact nsm generated)"})   
            response = openai.ChatCompletion.create(
                    engine="chatgpt", # The deployment name you chose when you deployed the GPT-35-Turbo or GPT-4 model.
                    messages=redisconvo[0],
                    temperature=0
                    )
            try:
                nsm_match = re.search(r'NSM: (.+)', response['choices'][0]['message']['content'])
                nsm = nsm_match.group(1)
                print("North Star Metric (NSM):", nsm)
                NSMFlag = True 
            except:
                print("inside except block of kill")
                NSMFlag=False
                nsm=""
            saveNSMinRedis(id,redisconvo,nsm,NSMFlag,False,False,True,False,"")
            print("******Closing conversation*********")
            return "Thankyou for your time!!"
        else:
            try:
                redisconvo[0].append({"role": "user", "content": message})   
                response = openai.ChatCompletion.create(
                    engine="chatgpt", # The deployment name you chose when you deployed the GPT-35-Turbo or GPT-4 model.
                    messages=redisconvo[0],
                    temperature=0
                    )
                redisconvo[0].append({"role": "assistant", "content": response['choices'][0]['message']['content']})
                print("\n" + response['choices'][0]['message']['content'] + "\n")
                
                #Pattern match to check if NSM is generated by user, So to send flag as true to show generated NSM on larger window in UI
                pattern = r'Your NSM'
                if re.search(pattern, response['choices'][0]['message']['content'], re.IGNORECASE): #or "vision" in response['choices'][0]['message']['content']:
                    print("INSIDE RE SEARCH")
                    flag = True
                    redisconvo[0].append({"role": "user", "content": "Print North Star Metric in this format  NSM:(exact nsm generated)"})   
                    nsmResponse = openai.ChatCompletion.create(
                            engine="chatgpt", 
                            messages=redisconvo[0],
                            temperature=0
                            )
                    redisconvo[0].append({"role": "assistant", "content": nsmResponse['choices'][0]['message']['content']})
                    saveLogs(id,redisconvo,True,False)
                    #Pattern match to save NSM generated
                    try:
                        print("NSM RESPONSE:",nsmResponse['choices'][0]['message']['content'])
                        nsm_match = re.search(r'NSM: (.+)', nsmResponse['choices'][0]['message']['content'])
                        NSM = nsm_match.group(1)
                        print("North Star Metric (NSM):", NSM)
                        NSM_Flag = True

                    except Exception as errors:
                        print("inside except block of kill",errors)
                        NSM_Flag=False
                        NSM=""
                    saveNSMData(embeddingsId, nsm=NSM, hasNSM=True, hasEpics=False, hasGeneratedRoadmap=False, idea=idea, allNSM=allNSM)
                else:
                    data = json.loads(Redis.get(id))
                    if data['hasNSM']:
                        print("inside afterNSM")
                        NSM_Flag= True
                        NSM = data['nsm']
                        flag = False
                        print("AFTER NSM:",NSM,"and flag:",NSM_Flag)
                    else:
                        flag = False
                        NSM_Flag=False
                        NSM=""
                # Using RE to remove unwanted string generated by GPT
                output = re.sub(r'^.*?(9|10)\. North Star Metric:', '', response['choices'][0]['message']['content'], flags=re.DOTALL)
                json_data = json.dumps({"summary":flag,"Result": output})
                if(flag == False):
                    # serialized_conversation = json.dumps(redisconvo)
                    saveLogs(id,redisconvo,False,False)
                saveNSMinRedis(id,redisconvo,NSM,NSM_Flag,False,False,False,False,"")
                headers = {'Access-Control-Allow-Origin': '*'}
                return json_data, 200, headers
            except Exception as err:
                print("ERROR:",err)
                return json.dumps({"summary":False,"Result":"Server is currently overloaded. Please try again"})

"""
    Search In Embeddings and get current status of NSM, Roadmap generated with ID

    Endpoint: /nsm-status

    Request JSON Parameters:
    - id : email
    
    Returns:
    - JSON response containing NSM, hasNSM, Roadmap, hasGeneratedRoadmap and selected Epics
 """
@app.route("/nsm-status",methods=['GET'])
def check_nsm():
    id = request.headers.get('email')
    embeddingsId = id 
    print("EMBEDDINGS ID:",embeddingsId)
    id = id + "_NSMCopilot"
    result = searchInEmbeddings(embeddingsId)
    NSM = result['nsm'] #data['nsm']
    try:
        hasNSM = result['hasNSM'] #data['hasNSM']
    except:
        print("INSIDE hasNSM except")
        hasNSM = False
    try:
        selectedEpics = ast.literal_eval(result["selectedEpics"]) #data['selectedEpics']
    except:
        print("INSIDE selected except")
        selectedEpics =""
    try:
        hasGeneratedRoadmap = result['hasGeneratedRoadmap'] #data['hasGeneratedRoadmap']
    except:
        print("INSIDE hasGenerated except")
        hasGeneratedRoadmap = False
    try:
        # redisData = json.loads(Redis.get(roadmapid))
        roadmap = ast.literal_eval(result["roadmap"])
    except Exception as ex:
        print("INSIDE Roadmap except",ex)
        roadmap = ""
    return json.dumps({"NSM":NSM,"hasNSM":hasNSM,"selectedEpics":selectedEpics,"hasGeneratedRoadmap":hasGeneratedRoadmap,"roadmap":roadmap})

'''
Save the edited roadmap array.

Parameters:
  - id: Email
  - editedRoadMap: The edited roadmap array.

'''
@app.route("/saveEpics",methods=['POST'])
def saveEpics():
  request_data=request.get_json()
  id = request.headers.get('email')
  embeddingsID = id
  id = id +"_withNSM"
  editedroadmaparray = request_data['editedRoadMap']
  redisData = json.loads(Redis.get(id))
  redisData['roadmap'] = editedroadmaparray
  Redis.set(id, json.dumps(redisData))
  saveNSMData(embeddingsID, roadmap=editedroadmaparray)
  return jsonify({
    "Result":"Saved Successfully"
  })

'''
Save the promoted epics.

Parameters:
  - id: Email
  - selectedEpics: String containing selected epics.

'''
@app.route("/promoteEpics",methods=['POST'])
def promoteEpics():
  request_data=request.get_json()
  id = request.headers.get('email')
  embeddingsID = id
  id = id + "_NSMCopilot"
  selectedEpics = request_data['selectedEpics']
  redisData = json.loads(Redis.get(id))
  print("Redis Saved:" ,redisData)
  redisData['selectedEpics'] = selectedEpics
  saveNSMData(embeddingsID, selectedEpics=selectedEpics)
  Redis.set(id, json.dumps(redisData))
  return jsonify({
    "Result":"Saved Successfully"
  })

'''
 To check if routes are up and running
'''
@app.route("/check",methods=['GET'])
def check():
  return jsonify({
    "Status":"active"
  })



if __name__ == '__main__':
  if(os.environ['FLASK_ENV']==True or os.environ['FLASK_ENV']==str(1)):
    app.run(host='0.0.0.0', port=6000)
  else:
    app.run(port=6000)


# @cross_origin(origin='*')
# @app.route('/nsm',methods=['POST'])
# def context():
#     request_data=request.get_json()
#     if(request_data['isNew'] == "yes"):
#         try:
#             conversation =[]
#             id = request.headers.get('email')
#             id = id + "_NSM"
#             context = returnPrompt(variable.challenge, variable.questions, variable.customer,variable.customer_description, variable.NSM, variable.Vision_Statement, variable.Current_vs_Future_State, variable.NSM_Pillars, variable.SWOT_Analysis, variable.SWOT_Pillars, variable.Risks_or_Challenges_to_consider, variable.Best_in_Class, variable.Experience_Play, variable.Industry, variable.Industry_Experience_Plays, variable.Customer_Centricity_Benefits, variable.Customer_Loyalty_Facts, variable.Customer_Loyalty_Tablestakes, variable.Competitor_Top_Friction_Points, variable.CX_Promise, variable.Loyalty_Experience_Aspirational_Example, variable.How_Might_We, variable.Blue_Ocean_Framework, variable.Experience_Pillars, variable.Strategic_Themes, variable.Strategic_Roadmap, variable.quardant_explaination)
#             User_Question = """Generate initiatives related to the CX/UX category for GP"""
#             nsm_prompt = [
#                 {"role": "system", "content": context},
#                 {"role": "user", "content": User_Question},
#             ]
#             conversation.append(nsm_prompt)
#             response = openai.ChatCompletion.create(
#             engine="chatgpt", # The deployment name you chose when you deployed the GPT-35-Turbo or GPT-4 model.
#             messages=conversation[0]
#             )
#             # response = openai.ChatCompletion.create(
#             #     engine="chatgpt", # The deployment name you chose when you deployed the ChatGPT or GPT-4 model.
#             #     messages = conversation[0],
#             #     temperature=0.5,
#             #     max_tokens=4000,
#             #     top_p=0.5,
#             #     #pre_response_text="You're referring to Ascensus project where there are multiple problems. Major ones are Poor backlog health and excessive Sprint injection.",
#             #     frequency_penalty=0,
#             #     presence_penalty=0,
#             #     stop=None
#             # )
#             conversation[0].append({"role": "assistant", "content": response['choices'][0]['message']['content']})
#             json_data = json.dumps({"Result": response['choices'][0]['message']['content']})
            
#             saveNSMinRedis(id,conversation)
#             headers = {'Access-Control-Allow-Origin': '*'}
#             return json_data, 200, headers     
#         except Exception as err:
#             print("ERROR!! -",err)
#             return json.dumps({"Result":"Server is currently overloaded. Please try again"})
#     else:
#         message = request_data['message']
#         id = request.headers.get('email')
#         id = id + "_NSM"
#         redisconvo = json.loads(json.loads(Redis.get(id))['conversation'])
#         if message.lower()=="kill":
#             saveNSMinRedis(id,redisconvo)
#             print("******Closing conversation*********")
#             return "Thankyou for your time!!"
#         else:
#             try:
#                 redisconvo[0].append({"role": "user", "content": message})   
#                 response = openai.ChatCompletion.create(
#                     engine="chatgpt", # The deployment name you chose when you deployed the GPT-35-Turbo or GPT-4 model.
#                     messages=redisconvo[0]
#                     )
#                 # response = openai.ChatCompletion.create(
#                 #     engine="chatgpt",
#                 #     messages =redisconvo[0],
#                 #     temperature=0.5,
#                 #     max_tokens=4000,
#                 #     top_p=0.5,
#                 #     frequency_penalty=0,
#                 #     presence_penalty=0,
#                 #     stop=None
#                 # )
#                 redisconvo[0].append({"role": "assistant", "content": response['choices'][0]['message']['content']})
#                 print("\n" + response['choices'][0]['message']['content'] + "\n")
#                 json_data = json.dumps({"Result": response['choices'][0]['message']['content']})
#                 # convo_data = json.dumps(redisconvo)
#                 saveNSMinRedis(id,redisconvo)
#                 headers = {'Access-Control-Allow-Origin': '*'}
#                 return json_data, 200, headers
#             except Exception as err:
#                 print("ERROR:",err)
#                 return json.dumps({"Result":"Server is currently overloaded. Please try again"})

# def chat():
#     Roadmap = roadmap()

# if(roadMap):
#             conversation[0].append({"role": "user", "content": """Generate Epic Roadmap for me based on previously epics generated in this format:
#                                                                 Here is your Epic Roadmap: 
#                                                                     Quarter 1: 
#                                                                     1.Roadmap no.1 .... and so on"""})   
#             response = openai.ChatCompletion.create(
#                 engine="chatgpt", # The deployment name you chose when you deployed the GPT-35-Turbo or GPT-4 model.
#                 messages=conversation[0],
#                 temperature=0
#                 )
#             conversation[0].append({"role": "assistant", "content": response['choices'][0]['message']['content']})
#             # try:
#             roadmap_match = re.search(r"Here is your Epic Roadmap", response['choices'][0]['message']['content'],re.DOTALL)
#             if(roadmap_match):
#                 RoadMapFlag = True 
#             else:
#                 RoadMapFlag=False
#             json_data = json.dumps({"RoadMapFlag":RoadMapFlag,"Result": response['choices'][0]['message']['content']})
#             id = id +"_withNSM"
#             saveRoadMapinRedis(id,conversation)
#             headers = {'Access-Control-Allow-Origin': '*'}
#             return json_data, 200, headers