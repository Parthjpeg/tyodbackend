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
from .checkforinvalidinput import *
from ffmpeg import FFmpeg
import json


def getreadableaudio(request):
    bytes = base64.b64decode(request.data.get("bs64audio"), validate=True)
    temp1 = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    speech_file_path = temp1.name
    f = open(speech_file_path, 'wb')
    f.write(bytes)
    f.close()

    # audioFileName = str(request.data.get("audio"))
    # filename, file_extension = os.path.splitext(audioFileName)
    # audiofile = request.FILES["audio"]
    # temp = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
    # filepath = temp.name
    # for chunk in audiofile.chunks():
    #     temp.write(chunk)
    # temp.close()

    temp2 = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    filepath2 = temp2.name
    ffmpeg = (
        FFmpeg()
        .option("y")
        .input(speech_file_path)
        .output(
            filepath2,
            {"codec:v": "libx264"},
            vf="scale=1280:-1",
            preset="veryslow",
            crf=24,
        )
    )

    ffmpeg.execute()
    base64rewamped = base64.b64encode(BytesIO(open(filepath2 , 'rb').read()).getvalue()).decode('utf-8')
    return base64rewamped

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
                request.data["bs64audio"] = getreadableaudio(request)
                bytes = base64.b64decode(request.data.get("bs64audio"), validate=True)
                temp1 = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                speech_file_path = temp1.name
                f = open(speech_file_path, 'wb')
                f.write(bytes)
                f.close()
                audio_file= open(speech_file_path, "rb")
                userQuery = speechtotext(audio_file)
                print(userQuery)
            testmessage = [{"role":"system" , "content":"you are a bot who checks wheather or not the user has answered a question correctly if the user has answered the question correctly respond with - the answer is correct if the user has anwered the question incorrectly respond with the answer is incorrect. certain lingo to refer to if the user says bike it means motorcycle , a scooter also has a similar meaning to a scooty or a moped , vehicals cars bikes motercycle mean the same thing be a bit lenient check not for the words but for the semantic meaning. "},
                           {"role":"user" , "content" : f""" Question {chain[currentchain - 1]} , User Answer - {userQuery} """}]
            print(testmessage)
            assistant_resp = naturallm(testmessage)
            print(assistant_resp)
            invalidflag = checkforinvalid(assistant_resp)
            if(invalidflag):
                testmessage = [{"role":"system" , "content":f"""The user has gotten a bit offtracked your job is to ask the user {chain[currentchain - 1]} , and dont answer the user question but use elements from the user answer to make the reframing fun. Dont start with a greeting the greetings are already done, do not imply that we would circle back to it"""},
                           {"role":"user" , "content" : f""" Question {chain[currentchain - 1]} , User Answer - {userQuery} """}]
                assistant_resp = naturallm(testmessage)
                response = {"history":messages , "question": assistant_resp}
                if(audio_flag):
                    filepath = texttospeechtvsmwhisper(assistant_resp)
                    file = open(filepath, 'rb')
                    bs64 = Get_Base64_tvsm(file)
                    response["audio_base64"] = bs64
                return Response(response)
            else:
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
                    filepath = texttospeechtvsmwhisper(assistant_resp)
                    file = open(filepath, 'rb')
                    bs64 = Get_Base64_tvsm(file)
                    response["audio_base64"] = bs64
                return Response(response)
        else:
            if(request.data.get("bs64audio")):
                audio_flag = True
                request.data["bs64audio"] = getreadableaudio(request)
                engquery = translateAudioToEnglishTvsm(request.data.get("bs64audio") , sourceLang , "en")
                print(engquery)
            else:
                engquery = translatetext(userQuery , sourceLang , "en")
            testmessage = [{"role":"system" , "content":"you are a bot who checks wheather or not the user has answered a question correctly if the user has answered the question correctly respond with - the answer is correct if the user has anwered the question incorrectly respond with the answer is incorrect. certain lingo to refer to if the user says bike it means motorcycle , a scooter also has a similar meaning to a scooty or a moped , vehicals cars bikes motercycle mean the same thing be a bit lenient check not for the words but for the semantic meaning."},
                           {"role":"user" , "content" : f""" Question {chain[currentchain - 1]} , User Answer - {engquery} """}]
            print(testmessage)
            assistant_resp = naturallm(testmessage)
            print(assistant_resp)
            invalidflag = checkforinvalid(assistant_resp)
            if(invalidflag):
                testmessage = [{"role":"system" , "content":f"""The user has gotten a bit offtracked your job is to ask the user {chain[currentchain - 1]} , and dont answer the user question but use elements from the user answer to make the reframing fun. Dont start with a greeting the greetings are already done, do not imply that we would circle back to it"""},
                           {"role":"user" , "content" : f""" Question {chain[currentchain - 1]} , User Answer - {engquery} """}]
                assistant_resp = naturallm(testmessage)
                resp_in_native_language = translatetext(assistant_resp , "en" , sourceLang)
                response = {"history":messages , "question": resp_in_native_language}
                if(audio_flag):
                    bs64 = texttospeechtvsm(resp_in_native_language , sourceLang)
                    response["audio_base64"] = bs64
                return Response(response)
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
                request.data["bs64audio"] = getreadableaudio(request)
                bytes = base64.b64decode(request.data.get("bs64audio"), validate=True)
                temp1 = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                speech_file_path = temp1.name
                f = open(speech_file_path, 'wb')
                f.write(bytes)
                f.close()
                audio_file= open(speech_file_path, "rb")
                userQuery = speechtotext(audio_file)
                print(userQuery)
            testmessage = [{"role":"system" , "content":"you are a bot who checks wheather or not the user has answered a question correctly if the user has answered the question correctly respond with - the answer is correct if the user has anwered the question incorrectly respond with the answer is incorrect. certain lingo to refer to if the user says bike it means motorcycle , a scooter also has a similar meaning to a scooty or a moped"},
                           {"role":"user" , "content" : f""" Question {chain[currentchain - 1]} , User Answer - {userQuery} """}]
            print(testmessage)
            assistant_resp = naturallm(testmessage)
            print(assistant_resp)
            invalidflag = checkforinvalid(assistant_resp)
            if(invalidflag):
                testmessage = [{"role":"system" , "content":f"""The user has gotten a bit offtracked your job is to ask the user {chain[currentchain - 1]} , and dont answer the user question but use elements from the user answer to make the reframing fun. Dont start with a greeting the greetings are already done, do not imply that we would circle back to it"""},
                           {"role":"user" , "content" : f""" Question {chain[currentchain - 1]} , User Answer - {userQuery} """}]
                assistant_resp = naturallm(testmessage)
                response = {"history":messages , "question": assistant_resp}
                if(audio_flag):
                    filepath = texttospeechtvsmwhisper(assistant_resp)
                    file = open(filepath, 'rb')
                    bs64 = Get_Base64_tvsm(file)
                    response["audio_base64"] = bs64
                return Response(response)
            else:
                stringtovector = "the budget of the user is " + substring + "The user will use it for - " + userQuery
        else:
            if(request.data.get("bs64audio")):
                audio_flag = True
                request.data["bs64audio"] = getreadableaudio(request)
                engquery = translateAudioToEnglishTvsm(request.data.get("bs64audio") , sourceLang , "en")
                print(engquery)
            else:
                engquery = translatetext(userQuery , sourceLang , "en")
    
            if(invalidflag):
                testmessage = [{"role":"system" , "content":f"""The user has gotten a bit offtracked your job is to ask the user {chain[currentchain - 1]} , and dont answer the user question but use elements from the user answer to make the reframing fun. Dont start with a greeting the greetings are already done, do not imply that we would circle back to it"""},
                           {"role":"user" , "content" : f""" Question {chain[currentchain - 1]} , User Answer - {engquery} """}]
                assistant_resp = naturallm(testmessage)
                resp_in_native_language = translatetext(assistant_resp , "en" , sourceLang)
                response = {"history":messages , "question": resp_in_native_language}
                if(audio_flag):
                    bs64 = texttospeechtvsm(resp_in_native_language , sourceLang)
                    response["audio_base64"] = bs64
                return Response(response)
            
            stringtovector = "the budget of the user is " + substring + "The user will use it for - " + engquery
        query_vector = Get_Embeddings(stringtovector)
        queryset = Tvsm_Vehicles.objects.filter(vehicle_fuel_type = request.data.get("fuel_type")).filter(vehicle_type = request.data.get("vehical_type")).annotate(distance=L2Distance('feature_vector',query_vector)).order_by('distance').values('vehicle_name', 'vehicle_type' , 'vehicle_price' , 'distance' , 'vehicle_description' , 'vehicle_fuel_type' , 'vehicle_prime_users' , 'vehical_link' , 'vehical_img_link' , 'vehical_testdrive_link' , 'vehical_booking_link')[:1]
        print(queryset[0].get("vehicle_description"))
        sys_msg = "you provide information about vehicles the information you need to provide is already present in the userQuery what you need to do is take that information and create an awesome summary about why the user needs to buy that vehical, Whenever you use the vehical name make sure its in all CAPS. eg if the name is tvs jupyter make it TVS JUPYTER. Also always end with click on the button below to book the vehical or you can also book a test ride"
        messages = [{"role":"system" , "content":sys_msg}]
        userq = f"""The name of this vehical is{queryset[0].get("vehicle_name")} , the cost of this vehical is {queryset[0].get("vehicle_price")} , type of vehical is {queryset[0].get("vehicle_type")} the fuel which the vehical uses is {queryset[0].get("vehicle_fuel_type")}, this vehical is mostly used for {queryset[0].get("vehicle_prime_users")}"""
        messages.append({"role":"user" , "content":userq})
        assistant_resp = naturallm(messages)
        if(sourceLang == "en"):
            response = {"vehical":queryset[0] , "description":assistant_resp}
            if(audio_flag):
                filepath = texttospeechtvsmwhisper(assistant_resp)
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


@api_view(['Post'])
def Add_Tvsm_Accessories(request):
    if(request.data):
        product_name = request.data.get('product_name')
        vehicle_name = request.data.get('vehicle_name')
        product_price = request.data.get('product_price')
        product_primary_color = request.data.get('product_primary_color')
        product_accent_color = request.data.get('product_accent_color')
        product_description = request.data.get('product_description')
        product_user = request.data.get('product_user')
        embedding_string = f"""{product_name} this helmet is best suited for the vehical {vehicle_name}, the primary color of this helmet is {product_primary_color} with accents of {product_accent_color}, this helmet is intended for {product_user}. The cost of this helmet is {product_price}. This helmet is best described as {product_description}"""
        feature_vector = Get_Embeddings(embedding_string)
        request.data['feature_vector'] = feature_vector
        serializers = tvsmAccessoriesSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data,status=status.HTTP_201_CREATED)
        else:
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['Post'])
def chatAccessories(request):
    engqueryacc = ""
    message = []
    userQuery = request.data.get("userQuery") 
    audio_flag = False
    sys_msg = "Your job is to write custom product descriptions based on the user query and some information about the product. Make the descriptions compelling."
    err_sysmsg = "The user has asked a query which is not related to helmets please write a message in which we would decline to answer and bring the conversation back to helmets"
    sourceLang = request.data.get("sourceLang")
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
        query_vector = Get_Embeddings(userQuery)
        queryset = Tvsm_Accessories.objects.annotate(distance=L2Distance('feature_vector',query_vector)).order_by('distance').values("product_name" , "vehicle_name", "product_price", "product_description", "distance" , "product_link" , "product_img_link")[:1]
        print(queryset[0].get("distance"))
        if(queryset[0].get("distance")>0.65):
            message.append({"role":"system" , "content":err_sysmsg})
            message.append({"role":"user" , "content":userQuery})
            assistant_response = naturallm(message)
            return Response({"err":assistant_response})
        product_description = queryset[0].get("product_description")
        product_name = queryset[0].get("product_name")
        product_price = queryset[0].get("product_price")
        vehicle_name = queryset[0].get("vehicle_name")
        product_user = queryset[0].get("product_user")
        finalinput = f"""User Query - {userQuery} , Information about the helmet - This helmet is described as {product_description} the name of this helmet is {product_name}. This helmet costs {product_price}. This helmet is best suited for the vehical {vehicle_name}. This product is made for {product_user}"""
        message.append({"role":"system" , "content":sys_msg})
        message.append({"role":"user" , "content":finalinput})
        assistant_response = naturallm(message)
        response = {"Product" : queryset[0] , "Description": assistant_response}
        if(audio_flag):
            # filepath = texttospeechtvsmwhisper(assistant_response)
            # file = open(filepath, 'rb')
            # bs64 = Get_Base64_tvsm(file)
            bs64 = texttospeechtvsm(assistant_response , sourceLang)
            response["audio_base64"] = bs64
        return Response(response)
    else:
        if(request.data.get("bs64audio")):
            print("in if")
            audio_flag = True
            engqueryacc = translateAudioToEnglishTvsm(request.data.get("bs64audio") , sourceLang , "en")
            print(engqueryacc)
        else:
            engqueryacc = translatetext(userQuery , sourceLang , "en")
        print(engqueryacc)
        query_vector = Get_Embeddings(engqueryacc)
        print(engqueryacc)
        queryset = Tvsm_Accessories.objects.annotate(distance=L2Distance('feature_vector',query_vector)).order_by('distance').values("product_name" , "vehicle_name", "product_price", "product_description", "product_user","distance", "product_link" , "product_img_link")[:1]
        if(queryset[0].get("distance")>0.65):
            message.append({"role":"system" , "content":err_sysmsg})
            message.append({"role":"user" , "content":userQuery})
            assistant_response = naturallm(message)
            resp_in_native_language = translatetext(assistant_response , "en" , sourceLang)
            return Response({"err":resp_in_native_language})
        product_description = queryset[0].get("product_description")
        product_name = queryset[0].get("product_name")
        product_price = queryset[0].get("product_price")
        vehicle_name = queryset[0].get("vehicle_name")
        product_user = queryset[0].get("product_user")
        finalinput = f"""User Query - {engqueryacc} , Information about the helmet - This helmet is described as {product_description} the name of this helmet is {product_name}. This helmet costs {product_price}. This helmet is best suited for the vehical {vehicle_name}. This product is made for {product_user}"""
        message.append({"role":"system" , "content":sys_msg})
        message.append({"role":"user" , "content":finalinput})
        assistant_response = naturallm(message)
        resp_in_native_language = translatetext(assistant_response , "en" , sourceLang)
        response = {"Product" : queryset[0] , "Description": resp_in_native_language}
        if(audio_flag):
            bs64 = texttospeechtvsm(resp_in_native_language , sourceLang)
            response["audio_base64"] = bs64
        return Response(response)   
    


@api_view(["POST"])
def jsontest(request):
        request.data["history"] = json.loads(request.data.get("history"))
        print(str(request.data["history"]))
        print(type(request.data["history"]))
        file_path = 'C:/personal/extentia/tyod/test.wav'
        response = FileResponse(open(file_path, 'rb'))
        history = [{"role":"system", "content":"hello"}]
        # Add JSON data to headers
        response['history'] = request.data["history"]
        return response
    

@api_view(['Post'])
def tvsmchatwithoutbase64(request):
    pass