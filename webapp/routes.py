from flask import Flask, jsonify , Blueprint, render_template, request
import json, requests , boto3
import numpy as np
import os
import boto3
import re
from dotenv import load_dotenv

routes = Blueprint('routes', __name__)

bucket_name = 'star-rating-123'
file_name = 'neighborhoods.json'

load_dotenv()

client = boto3.client('bedrock-agent-runtime',
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name="us-west-2"
)

kb_id_crash = "M5RMNOTHJ7"
model_arn_crash = "arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
def retrieve_generated(input, kb_id_crash, model_arn_crash):
    response = client.retrieve_and_generate(
        input={
            'text': input
        },
        retrieveAndGenerateConfiguration = {
            "type":"KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration":{
                "knowledgeBaseId": kb_id_crash,
                "modelArn": model_arn_crash,
                "generationConfiguration":{
                    "promptTemplate":{
                        "textPromptTemplate":"You are a question-answering agent trained to interpret crash data for neighborhoods in San Jose and assign safety scores. Your task is to read and analyze car crash data from specific neighborhoods to assess the safety of each area. Be more critical, as crashes are a serious issue and you must grade it as such. Give lower points, even in the 3-4 point range if you must. Based on this data, you will assign a safety score between 1.0 and 10.0, where:\r\n1.0 represents an extremely unsafe neighborhood (e.g., frequent, severe crashes).\r\n10.0 represents a very safe neighborhood (e.g., no crashes, no injuries).\r\nStructure of the Data:\r\nNeighborhoods as Keys: Each neighborhood in the dataset is represented as a key, e.g., \"Sheppard\", which is associated with an array of crash data. Each crash record contains information such as:\r\n\r\nCrash Severity (e.g., minor injury, major injury, fatality)\r\nCrash Type (e.g., collision, rollover, hit-and-run)\r\nDate and Time of the crash\r\nOther factors like weather, road conditions, etc.\r\nUnderstanding the Data:\r\n\r\nEach neighborhood has multiple crash records (each entry in the array represents a separate crash).\r\nYour goal is to analyze this crash data, focusing on the severity of injuries and the frequency of crashes within each neighborhood.\r\nAssigning Weights to Factors: Use general knowledge to assign weights to different crash factors:\r\n\r\nInjury Severity should be prioritized (fatalities and major injuries weigh more than minor injuries).\r\nFrequency of Crashes should also influence the score (more frequent crashes suggest higher danger).\r\nOutliers (e.g., a single fatal crash in an otherwise safe area) should be handled, but not overemphasized.\r\nSafety Score Criteria: Based on the crash data:\r\n\r\nHigh Risk (1.0): A neighborhood with frequent crashes and severe injuries (fatalities or major injuries).\r\nLow Risk (10.0): A neighborhood with little or no crashes, no injuries, or minor incidents.\r\nIf a neighborhood has no crashes recorded in the data, assign it a perfect safety score of 10.0.\r\n\r\nIf a neighborhood has frequent severe crashes, assign it a low score (close to 1.0).\r\n\r\nHandling Missing or Incorrect Neighborhood:\r\nIf the user requests a neighborhood that is not in the provided dataset, reply that the neighborhood is not part of the city, with a message like: “The neighborhood [name] is not in the city of San Jose according to the provided data.”\r\nOutput: For each neighborhood, based on the provided crash data, return:\r\n\r\nSafety Score (a value between 1.0 and 10.0)\r\nExplanation of the score based on the crash data (e.g., “There were 5 crashes, 2 of which involved major injuries, leading to a score of 4.5.”)\r\n\r\nMake sure to always return a number. If the neighborhood can't be detected in the dataset, then make an educated estimation between 1.0 - 10.0.\r\n\r\nEvery single time I ask, you must return a safety score for a 5-year prediction and 10-year prediction. Make assumptions if needed, estimate a set of numbers between 1.0-10.0.\r\n\r\nYou must always return the following 3 pieces of information in a consistent format: A number for current Safety Score, a number for a predicted safety score 5-years in the future, and a number for a predicted safety score 10-years in the future\r\n\r\nWhen I message you, format the output as:\r\nSafety Score: (# for safety score)\r\n5-Year Safety Score Prediction: (# for Projected Safety Score in five years)\r\n10-Year Safety Score Prediction: (# for Projected Safety Score in ten years)\r\nOnly output these parameters. You must not give a reasoning behind each calculated safety score, 5-Year Safety Score Prediction, 10-Year Safety Score Prediction. Make sure to be very sure that you are allowed to predict either positive trends, as the rating increases over the years. \r\n\r\n$search_results$\r\n\r\n$output_format_instructions$\r\n"},
                        "inferenceConfig":{
                            "textInferenceConfig":{"temperature":1,"topP":1,"maxTokens":2048,"stopSequences":["\nObservation"]
                                                   }
                                            }
                                        }
                                    }
                                }
    )
    return response

kb_id_crime= "M5RMNOTHJ7"
model_arn_crime = "arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
def retrieve_generated_crime(input, kb_id_crime, model_arn_crime):
    response = client.retrieve_and_generate(
        input={
            'text': input
        },
        retrieveAndGenerateConfiguration = {
            "type":"KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration":{
                "knowledgeBaseId": kb_id_crime,
                "modelArn": model_arn_crime,
                "generationConfiguration":{
                    "promptTemplate":{
                        "textPromptTemplate":"You are a question-answering agent trained to interpret crime data for neighborhoods in San Jose and assign safety scores. Your task is to read and analyze crime data from specific neighborhoods to assess the safety of each area. Be more critical, as crime is a serious issue and you must grade it as such. Give lower points, even in the 3-4 point range if you must. Based on this data, you will assign a safety score between 1.0 and 10.0, where:\r\n1.0 represents an extremely unsafe neighborhood (e.g., frequent, violent crimes).\r\n10.0 represents a very safe neighborhood (e.g., little to no crime reported).\r\nStructure of the Data:\r\nNeighborhoods as Keys: Each neighborhood in the dataset is represented as a key (e.g., \"Sheppard\"), which is associated with an array of crime data. Each crime record contains information such as:\r\nCrime Type (e.g., theft, burglary, assault, homicide)\r\nDate and Time of the crime\r\nCrime Frequency (e.g., number of crimes in the neighborhood over time)\r\nUnderstanding the Data:\r\nEach neighborhood has multiple crime records (each entry in the array represents a separate crime incident).\r\nYour goal is to analyze this crime data, focusing on the severity of the crimes and the frequency of crimes within each neighborhood.\r\nAssigning Weights to Factors:\r\nSeverity of Crimes should be prioritized (violent crimes such as homicides, assaults, and robberies weigh more than non-violent crimes like theft or vandalism).\r\nFrequency of Crimes should also influence the score (more frequent crimes suggest higher danger).\r\nOutliers (e.g., a single violent crime in an otherwise safe area) should be handled but not overemphasized.\r\nSafety Score Criteria:\r\nBased on the crime data:\r\nHigh Risk (1.0): A neighborhood with frequent and severe crimes (e.g., multiple homicides or assaults).\r\nMedium Risk(5.0): A neighborhood with an average amount of crime.\r\nLow Risk (10.0): A neighborhood with little or no crime or only minor incidents.\r\nIf a neighborhood has no crimes recorded in the data, assign it a perfect safety score of 10.0.\r\nIf a neighborhood has frequent severe crimes, assign it a low score (close to 1.0).\r\nHandling Missing or Incorrect Neighborhood:\r\nIf the user requests a neighborhood that is not in the provided dataset, reply that the neighborhood is not part of the city, with a message like:\r\n“The neighborhood [name] is not in the city of San Jose according to the provided data.”\r\nOutput:\r\nFor each neighborhood, based on the provided crime data, return:\r\nSafety Score (a value between 1.0 and 10.0)\r\n5-Year Safety Score Prediction (based on assumed changes, trends, or estimates in crime data).\r\n10-Year Safety Score Prediction (based on assumed changes, trends, or estimates in crime data).\r\nIf the neighborhood can't be detected in the dataset, make an estimated guess between 1.0 - 10.0.\r\nMake sure to estimate a completely different set of numbers between 1.0-10.0 than any previous assumptions.\r\nFormat the Output as:\r\n\r\nSafety Score: (# for safety score)  \r\n5-Year Safety Score Prediction: (# for Projected Safety Score in five years)  \r\n10-Year Safety Score Prediction: (# for Projected Safety Score in ten years)  \r\n\r\nOnly output these parameters. You must not give a reasoning behind each calculated safety score, 5-Year Safety Score Prediction, or 10-Year Safety Score Prediction. I really want to emphasize that crime, no matter the scale, is a very serious issue and should be heavily factored into the rating.\r\n$search_results$\r\n\r\n$output_format_instructions$"},
                        "inferenceConfig":{
                            "textInferenceConfig":{
                                                   }
                                            }
                                          }
                                        }
                                    }
    )
    return response

@routes.route("/")
def index():
    return render_template("index.html")

@routes.route("/neighborhood.html")
def neighborhood():
    nName = request.args.get('nName')

    rating = getNrating(nName)
    

    response = retrieve_generated(f"Give me a safety score, 5-year safety score prediction, and 10-year safety score prediction for {nName}", kb_id_crash=kb_id_crash, model_arn_crash=model_arn_crash) 

    generated_text = response['output']['text']

    crime_response = retrieve_generated_crime(f"Give me a safety score, 5-year safety score prediction, and 10-year safety score prediction for {nName}", kb_id_crime=kb_id_crime, model_arn_crime=model_arn_crime) 

    crime_text = crime_response['output']['text']

    nScore = 0
    fiveScore = 0
    tenScore = 0
    
    nScore_match = re.search(r"Safety Score:\s*(-?\d*\.?\d+)", generated_text)
    fiveScore_match = re.search(r"5-Year Safety Score Prediction:\s*(-?\d*\.?\d+)", generated_text)
    tenScore_match = re.search(r"10-Year Safety Score Prediction:\s*(-?\d*\.?\d+)", generated_text)
    
    c_nScore_match = re.search(r"Safety Score:\s*(-?\d*\.?\d+)", crime_text)
    c_fiveScore_match = re.search(r"5-Year Safety Score Prediction:\s*(-?\d*\.?\d+)", crime_text)
    c_tenScore_match = re.search(r"10-Year Safety Score Prediction:\s*(-?\d*\.?\d+)", crime_text)
    
    if nScore_match:
        nScore = float(nScore_match.group(1))
    if fiveScore_match:
        fiveScore = float(fiveScore_match.group(1))
    if tenScore_match:
        tenScore = float(tenScore_match.group(1))

    if c_nScore_match:
        if nScore > 0:
            nScore += float(c_nScore_match.group(1))
            nScore /= 2
    if c_fiveScore_match:
        if fiveScore > 0:
            fiveScore += float(fiveScore_match.group(1))
            fiveScore /= 2
    if c_tenScore_match:
        if tenScore > 0:
            tenScore += float(tenScore_match.group(1))
            tenScore /= 2

    return render_template("neighborhood.html", nName=nName, nScore=round(nScore,1), rating=rating, fiveScore=round(fiveScore,1), tenScore=round(tenScore,1))


@routes.route('/submit-rating')
def submitRating():
    

    try:

        rating = request.args.get('rating')
        neighborhood = request.args.get('neighborhood')
        print(rating + neighborhood)
        if not rating or not neighborhood:
            return jsonify({'error': 'Missing rating or neighborhood'}), 400

       
        try:
            s3_object = s3.get_object(Bucket=bucket_name, Key='ratings.json')
            ratings_data = json.loads(s3_object['Body'].read().decode('utf-8'))
        except s3.exceptions.NoSuchKey:
            ratings_data = {}

        if neighborhood not in ratings_data:
            ratings_data[neighborhood] = []

        ratings_data[neighborhood].append(rating)

        print(ratings_data)

       
        s3.put_object(Bucket=bucket_name, Key='ratings.json', Body=json.dumps(ratings_data))
        
        return {'rating': rating, 'neighborhood': neighborhood}

    except Exception as e:
        print('Error:', str(e))  
        return jsonify({'error': str(e)}), 500
    

s3 = boto3.client('s3', region_name='us-west-2')
s3_bucket_name = 'star-rating-123'

def getNrating(nName):
     try:
        response = s3.get_object(Bucket=bucket_name, Key='ratings.json')
        data =  json.loads(response['Body'].read().decode('utf-8'))
        print(data)
        if nName in data:
            ratings = data[nName]  
            print(ratings)
            if ratings:
                sum = 0
                for r in ratings:
                    sum += int(r)
                
                avg_rating = sum / len(ratings)
                return round(avg_rating, 1)  
            else:
                print('no ratings')
                return 0  
        else:
            print('not in data')
            return 0 

     except Exception as e:
         return str(e)



