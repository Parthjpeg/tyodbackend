from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import *
from .serializer import *
from .helpers import *
from rest_framework import status
from .tvsmhelpers import *
from django.http import JsonResponse , FileResponse
from .parameterfromnlp import *
from pgvector.django import L2Distance

@api_view(['Post'])
def Add_product(request):
    if(request.data):
        vehicle_type = request.data.get('vehicle_type')
        vehicle_fuel_type = request.data.get('vehicle_fuel_type')
        vehicle_prime_users = request.data.get('vehicle_prime_users')
        vehicle_price = request.data.get('vehicle_price')
        vehicle_daily_commute = request.data.get('vehicle_daily_commute')
        vehicle_description = request.data.get('vehicle_description')
        embedding_string = "This is a "+ vehicle_type + " which runs on "+vehicle_fuel_type+" which is best suited for  "+  vehicle_prime_users + " whose daily commute is " +vehicle_daily_commute+". The price of this vehical is "+ vehicle_price+ ". This vehical can be best described as "+ vehicle_description
        feature_vector = Get_Embeddings(embedding_string)
        request.data['feature_vector'] = feature_vector
        serializers = tvsmSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data,status=status.HTTP_201_CREATED)
        else:
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['Post'])      
def tvsmchat(request):
    audio_flag = False
    sys_msg = "you are a helpful assistant"
    chain = ["greet the user and ask them weather they want an electric vehical or a petrol one" , "do you prefer a scooter or a motorcycle" , "What is your budget", "Are you going to use it for city rides or long rides" ]
    messages = request.data.get("history")
    sourceLang = request.data.get("sourceLang")
    userQuery = request.data.get("userQuery") 
    conversation_length = len(messages)-1
    currentchain = int((conversation_length) - (conversation_length/2))
    if(len(messages)==0):
        if(sourceLang == "en"):
            messages.append({"role": "system","content": "you are a helpful assistant"})
            messages.append({"role": "user","content": f"UserQuery - hello, ask the user - {chain[0]}"})
            assistant_resp = naturallm(messages)
            messages.append({"role": "assistant","content": assistant_resp})
            print(messages)
            return Response({"history":messages , "question": assistant_resp})
        else:
            messages.append({"role": "system","content": "you are a helpful assistant"})
            messages.append({"role": "user","content": f"UserQuery - hello, ask the user - {chain[0]}"})
            assistant_resp = naturallm(messages)
            messages.append({"role": "assistant","content": assistant_resp})
            resp_in_native_language = translatetext(assistant_resp , "en" , sourceLang)
            return Response({"history":messages , "question": resp_in_native_language})
    elif(currentchain<4):
        print(currentchain)
        if(sourceLang == "en"):
            if(request.data.get("bs64audio")):
                audio_flag = True
                bytes = base64.b64decode(request.data.get("bs64audio"), validate=True)
                temp1 = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                speech_file_path = temp1.name
                f = open(speech_file_path, 'wb')
                f.write(bytes)
                f.close()
                audio_file= open(speech_file_path, "rb")
                userQuery = speechtotext(audio_file)
                print(userQuery)
            messages.append({"role": "user","content": f"UserQuery - {userQuery} , ask the user - {chain[currentchain]}"})
            assistant_resp = naturallm(messages)
            messages.append({"role": "assistant","content": assistant_resp})
            print(messages)
            if(currentchain == 1):
                fuel_type = electricorpetrol(userQuery)
                response =  {"history":messages , "question": assistant_resp , "fuel_type":fuel_type}
            elif(currentchain == 2):
                vehical_type = bikeorscooter(userQuery)
                response = {"history":messages , "question": assistant_resp , "vehical_type":vehical_type}
            else:
                response = {"history":messages , "question": assistant_resp}
            if(audio_flag):
                filepath = texttospeechtvsm(assistant_resp)
                file = open(filepath, 'rb')
                bs64 = Get_Base64_tvsm(file)
                response["audio_base64"] = bs64
            return Response(response)
        else:
            if(request.data.get("bs64audio")):
                audio_flag = True
                engquery = translateAudioToEnglishTvsm(request.data.get("bs64audio") , sourceLang , "en")
                print(engquery)
            else:
                engquery = translatetext(userQuery , sourceLang , "en")
            messages.append({"role": "user","content": f"UserQuery - {engquery} , ask the user - {chain[currentchain]}"})
            assistant_resp = naturallm(messages)
            messages.append({"role": "assistant","content": assistant_resp})
            print(messages)
            resp_in_native_language = translatetext(assistant_resp , "en" , sourceLang)
            if(currentchain == 1):
                fuel_type = electricorpetrol(engquery)
                response = {"history":messages , "question": resp_in_native_language , "fuel_type":fuel_type}
            elif(currentchain == 2):
                vehical_type = bikeorscooter(engquery)
                response = {"history":messages , "question": resp_in_native_language , "vehical_type":vehical_type}
            else:
                response = {"history":messages , "question": resp_in_native_language}
            if(audio_flag):
                bs64 = texttospeechtvsm(resp_in_native_language , sourceLang)
                response["audio_base64"] = bs64
            return Response(response)

    else:
        #mydata = Member.objects.filter(firstname='Emil').values()
        text = messages[7].get("content")
        start = text.find("UserQuery - ") + len("UserQuery - ")
        end = text.find("ask the user")
        substring = text[start:end].strip()
        if(sourceLang == "en"):
            if(request.data.get("bs64audio")):
                audio_flag = True
                bytes = base64.b64decode(request.data.get("bs64audio"), validate=True)
                temp1 = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                speech_file_path = temp1.name
                f = open(speech_file_path, 'wb')
                f.write(bytes)
                f.close()
                audio_file= open(speech_file_path, "rb")
                userQuery = speechtotext(audio_file)
                print(userQuery)
            stringtovector = "the budget of the user is " + substring + "The user will use it for - " + userQuery
        else:
            if(request.data.get("bs64audio")):
                audio_flag = True
                engquery = translateAudioToEnglishTvsm(request.data.get("bs64audio") , sourceLang , "en")
                print(engquery)
            else:
                engquery = translatetext(userQuery , sourceLang , "en")
            stringtovector = "the budget of the user is " + substring + "The user will use it for - " + engquery
        query_vector = Get_Embeddings(stringtovector)
        queryset = Tvsm_Vehicles.objects.filter(vehicle_fuel_type = request.data.get("fuel_type")).filter(vehicle_type = request.data.get("vehical_type")).annotate(distance=L2Distance('feature_vector',query_vector)).order_by('distance').values('vehicle_name', 'vehicle_type' , 'vehicle_price' , 'distance' , 'vehicle_description' , 'vehicle_fuel_type' , 'vehicle_prime_users')[:1]
        print(queryset[0].get("vehicle_description"))
        sys_msg = "you provide information about vehicles the information you need to provide is already present in the userQuery what you need to do is take that information and create an awesome summary about why the user needs to buy that vehical, Whenever you use the vehical name make sure its in all CAPS. eg if the name is tvs jupyter make it TVS JUPYTER."
        messages = [{"role":"system" , "content":sys_msg}]
        userq = f"""The name of this vehical is{queryset[0].get("vehicle_name")} , the cost of this vehical is {queryset[0].get("vehicle_price")} , type of vehical is {queryset[0].get("vehicle_type")} the fuel which the vehical uses is {queryset[0].get("vehicle_fuel_type")}, this vehical is mostly used for {queryset[0].get("vehicle_prime_users")}"""
        messages.append({"role":"user" , "content":userq})
        assistant_resp = naturallm(messages)
        if(sourceLang == "en"):
            response = {"vehical":queryset[0] , "description":assistant_resp}
            if(audio_flag):
                filepath = texttospeechtvsm(assistant_resp)
                file = open(filepath, 'rb')
                bs64 = Get_Base64_tvsm(file)
                response["audio_base64"] = bs64
            return Response(response)
        else:
            resp_in_native_language = translatetext(assistant_resp , "en" , sourceLang)
            response = {"vehical":queryset[0] , "description":resp_in_native_language}
            if(audio_flag):
                bs64 = texttospeechtvsm(resp_in_native_language , sourceLang)
                response["audio_base64"] = bs64
            return Response(response)
            
@api_view(['Post'])
def fileresptest(request):
    filepath = "C:/personal/extentia/tyod/api/test.wav"
    file = open(filepath, 'rb')
    file_base_64 = Get_Base64_tvsm(file)
    bytes = base64.b64decode(file_base_64, validate=True)
    temp1 = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    speech_file_path = temp1.name
    f = open(speech_file_path, 'wb')
    f.write(bytes)
    f.close()
    return FileResponse(open(speech_file_path, 'rb'))
# electric or petrol
# geared or non geared
# budget
# City use or long rides

@api_view(['Post'])
def audiotobs64(request):
    bs64audio = Get_Base64(request)
    return Response({"bs64audio":bs64audio})
        
@api_view(['Post'])
def bs64toaudio(request):
    bytes = base64.b64decode(request.data.get("audio_base64"), validate=True)
    temp1 = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    speech_file_path = temp1.name
    f = open(speech_file_path, 'wb')
    f.write(bytes)
    f.close()
    return FileResponse(open(speech_file_path, 'rb'))