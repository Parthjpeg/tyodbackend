from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import *
from .serializer import *
from .helpers import *
from pypdf import PdfReader
from pgvector.django import L2Distance
import pandas as pd
import numpy
import threading


def getfiledata(filelist , userQuery):
    if (filelist[0].lower().endswith(('.pdf'))):
        filenamelist = filelist
        query_vector = Get_Embeddings(userQuery)
        chunks = filecontent.objects.filter(filename__in=filelist).annotate(distance=L2Distance('feature_vector',query_vector)).order_by('distance').values('chunk','distance')[:3]
        finalquery = "Question " + userQuery
        n = 1
        for chunk in chunks:
            finalquery += " File " + str(n) + " " + chunk.get("chunk")
            n = n+1
        userQuery = finalquery
        return userQuery
    elif (filelist[0].lower().endswith(('.xlsx'))):
            filenamelist = filelist
            finalquery = "Question " + userQuery
            s  =""  
            userQuery_vector = numpy.array(Get_Embeddings(userQuery))
            data = excelfilecontent.objects.filter(filename__in=filelist).values('filename' , 'content')
            try:
                for datapoints in data:
                    for realdata in datapoints.get("content").get('data'):
                        feature_vector = numpy.array(realdata["feature_vector"])
                        dist = numpy.linalg.norm(userQuery_vector-feature_vector)
                        if(dist<0.7):
                            s = s+ " " + realdata["alldata"]
            except:
                pass
            finalquery = finalquery+ " Data " + s
            return finalquery   


def getGoogleSearch(userQuery):
    print("in google search")
    res = getUrls(userQuery)
    all_texts = []
    for i in res:
        print(i)
        gettextfromwebsite(i.get('url') , all_texts)
        if (len(all_texts)>2):
            break
    return all_texts

@api_view(["POSt"])
def getchatnames(request):
    chatname = Chat.objects.all().values("name")
    return Response(chatname)

@api_view(["POSt"])
def getfilenames(request):
    filenames = files.objects.all().values("filename")
    return Response(filenames)

@api_view(["POSt"])
def getchathistory(request):
    chathistory = Chat.objects.filter(name = request.data.get("chatname")).values("name" , "messages" , "files")
    return Response(chathistory[0])

@api_view(["POST"])
def deletechat(request):
    try:
        chattodelete = Chat.objects.get(name = request.data.get("chatname"))
        chattodelete.delete()
        return Response({"message":"Chat Deleted"})
    except:
        return Response({"message":"Something went wrong"})
    
@api_view(["POST"])
def renamechat(request):
    try:
        chattodelete = Chat.objects.get(name = request.data.get("prevchatname"))
        chattodelete.name = request.data.get("newchatname")
        chattodelete.save()
        chattodelete = Chat.objects.get(name = request.data.get("prevchatname"))
        chattodelete.delete()
        return Response({"message":"chat renamed"})
    except:
        return Response({"message":"Something went wrong"})

@api_view(["POSt"])
def chat(request):
    res = {}
    filenamelist = []
    chatname = request.data.get("name")
    getchat = Chat.objects.filter(name=chatname)
    try:
        print(getchat[0].function)
        request.data["Function"] = getchat[0].function
    except:
        print("in pass")
    print(request.data["Function"])
    if(request.data.get("Function")):
        if(request.data.get("Function") == "TyodAmc"):
            if(len(getchat)>0):
                res = {}
                s = ""
                answer = ""
                updatemsg = getchat[0].messages
                query_vector = Get_Embeddings(request.data.get("userQuery"))
                data = excelfilecontent.objects.filter(filename="Amc.xlsx").values('filename' , 'content')
                query_vector = Get_Embeddings(request.data.get("userQuery"))
                for datapoints in data:
                    for realdata in datapoints.get("content").get('data'):
                        feature_vector = numpy.array(realdata["feature_vector"])
                        dist = numpy.linalg.norm(query_vector-feature_vector)
                        if(dist<0.75):
                            s = s+ " " + realdata["alldata"]
                request.data["userQuery"] = "UserQuery - "+request.data["userQuery"] + " Data " + s
                updatemsg["history"].append({"role": "user", "content": request.data.get("userQuery")})
                answer = getAnswer(updatemsg["history"])
                updatemsg["history"].append({"role": "assistant", "content": answer})
                res["messages"] = updatemsg
                serializer = ChatSerializer(getchat[0], data=res, partial=True)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(serializer.errors)
                return Response({"answer":answer})
            else:
                print("in else")
                answer = "TyodAmc Chat created"
                s = ""
                datatosend = {"name":request.data.get("name")}
                print(datatosend)
                datatosend["function"] = request.data.get("Function")
                datatosend["files"] = []
                datatosend["messages"] = {"history":[]}
                datatosend["messages"]["history"].append({"role": "system", "content": "you are a expert who will give insights on the data provided with the user query based on the data provided within the user query answer the questions. answer according to the question the user is asking IF THE QUESTION CANNOT BE ANSWERED WITH THE DATA PROVIDED DONT ANSWER. If the user Query isnt supported with data that means we could not find data in the excel sheet.  The fromat will be User Query - (user query) data to refer to -  (data). Your job is to only answer according to the user query."})
                if(request.data.get("userQuery")):
                    data = excelfilecontent.objects.filter(filename="Amc.xlsx").values('filename' , 'content')
                    query_vector = Get_Embeddings(request.data.get("userQuery"))
                    for datapoints in data:
                        for realdata in datapoints.get("content").get('data'):
                            feature_vector = numpy.array(realdata["feature_vector"])
                            dist = numpy.linalg.norm(query_vector-feature_vector)
                            if(dist<0.75):
                                s = s+ " " + realdata["alldata"]
                    request.data["userQuery"] = "UserQuery - "+request.data["userQuery"] + " Data " + s
                    datatosend["messages"]["history"].append({"role": "user", "content":request.data.get("userQuery")})
                    answer = getAnswer(datatosend["messages"]["history"])
                    datatosend["messages"]["history"].append({"role": "assistant", "content":answer})
                serializer = ChatSerializer(data=datatosend , partial=True)
                if(serializer.is_valid()):
                    serializer.save()
                else:
                    return Response(serializer.errors)
                return Response({"answer":answer})
        elif(request.data.get("Function") == "TyodMis"):
            if(len(getchat)>0):
                res = {}
                s = ""
                answer = ""
                updatemsg = getchat[0].messages
                query_vector = Get_Embeddings(request.data.get("userQuery"))
                data = excelfilecontent.objects.filter(filename="Mis.xlsx").values('filename' , 'content')
                query_vector = Get_Embeddings(request.data.get("userQuery"))
                for datapoints in data:
                    for realdata in datapoints.get("content").get('data'):
                        feature_vector = numpy.array(realdata["feature_vector"])
                        dist = numpy.linalg.norm(query_vector-feature_vector)
                        if(dist<0.7):
                            s = s+ " " + realdata["alldata"]
                request.data["userQuery"] =  "UserQuery - "+request.data["userQuery"] + " Data " + s
                updatemsg["history"].append({"role": "user", "content": request.data.get("userQuery")})
                answer = getAnswer(updatemsg["history"])
                updatemsg["history"].append({"role": "assistant", "content": answer})
                res["messages"] = updatemsg
                serializer = ChatSerializer(getchat[0], data=res, partial=True)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(serializer.errors)
                return Response({"answer":answer})

            else:
                answer = "TyodMis Chat created"
                s = ""
                datatosend = {"name":request.data.get("name")}
                datatosend["function"] = request.data.get("Function")
                datatosend["files"] = []
                datatosend["messages"] = {"history":[]}
                datatosend["messages"]["history"].append({"role": "system", "content": "You are a workforce management expert who provides responses to user queries based on search results from an MIS database. Users who interact with you are usually looking for human resources with specific skillset, experience, availability etc. You job is to look at the user query and use provided data to answer the questions. Sometimes the user might ask for. the data to be published in specific formats which you should address.   CONVERSATION FLOW:  The format of the chat sessions would be: User Query: (user query); Data to refer to: (data)    TASKS: Your primary task is to look at the conversation history, look at the current user query, and then respond appropriately based on the provided data from MIS database and in context of the conversation, derived from chat history.  If the user query has a greeting message, then irrespective of what the provided data is, you job is to greet back and inform the user about your role and what you can help with While responding to user queries you must use the provided data from MIS while taking into account the chat history provided If the user asks for a detailed report on a specific resource then you must provide tabular data including all available data points on the resource For any given user query, If the data provided to answer the query is not adequate then your response should be appropriately designed to address that lack of information within the MIS RESTRICTIONS: If the user query is about anything outside of your area of expertise, as defined, you must not engage the user further but politely remind the user of your role and purpose"})
                if(request.data.get("userQuery")):
                    data = excelfilecontent.objects.filter(filename="Mis.xlsx").values('filename' , 'content')
                    query_vector = Get_Embeddings(request.data.get("userQuery"))
                    for datapoints in data:
                        for realdata in datapoints.get("content").get('data'):
                            feature_vector = numpy.array(realdata["feature_vector"])
                            dist = numpy.linalg.norm(query_vector-feature_vector)
                            if(dist<0.7):
                                s = s+ " " + realdata["alldata"]
                    request.data["userQuery"] = "UserQuery - "+request.data["userQuery"] + " Data to refer to " + s
                    datatosend["messages"]["history"].append({"role": "user", "content":request.data.get("userQuery")})
                    answer = getAnswer(datatosend["messages"]["history"])
                    datatosend["messages"]["history"].append({"role": "assistant", "content":answer})
                serializer = ChatSerializer(data=datatosend , partial=True)
                if(serializer.is_valid()):
                    serializer.save()
                else:
                    return Response(serializer.errors)
                return Response({"answer":answer})
        elif(request.data.get("Function") == "TyodDoc"):
            if(len(getchat)>0):
                res = {}
                updatemsg = getchat[0].messages
                query_vector = Get_Embeddings(request.data.get("userQuery"))
                chunks = filecontent.objects.filter(filename="Extentia MSA - IQVIA_FullyExecuted.pdf").annotate(distance=L2Distance('feature_vector',query_vector)).order_by('distance').values('chunk','distance')[:3]
                request.data["userQuery"] = "User Query - " + request.data.get("userQuery") + " "+ "Data to refer to - " +  chunks[0].get("chunk") + " " + chunks[1].get("chunk") + " " + chunks[1].get("chunk")
                updatemsg["history"].append({"role": "user", "content": request.data.get("userQuery")})
                answer = getAnswer(updatemsg["history"])
                updatemsg["history"].append({"role": "assistant", "content": answer})
                res["messages"] = updatemsg
                serializer = ChatSerializer(getchat[0], data=res, partial=True)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(serializer.errors)
                return Response({"answer":answer})
            else:
                answer = "TyodDoc Chat Created"
                datatosend = {"name":request.data.get("name")}
                datatosend["function"] = request.data.get("Function")
                datatosend["files"] = []
                datatosend["messages"] = {"history":[]}
                datatosend["messages"]["history"].append({"role": "system", "content": "you summarize and answer questions based on the data provided in the user query. answer according to the question the user is asking IF THE QUESTION CANNOT BE ANSWERED WITH THE DATA PROVIDED DONT ANSWER. If the user Query isnt supported with data that means we could not find data in the document.  The fromat will be User Query - (user query) data to refer to -  (data). Your job is to only answer according to the user query."})
                if(request.data.get("userQuery")):
                    query_vector = Get_Embeddings(request.data.get("userQuery"))
                    chunks = filecontent.objects.filter(filename="Extentia MSA - IQVIA_FullyExecuted.pdf").annotate(distance=L2Distance('feature_vector',query_vector)).order_by('distance').values('chunk','distance')[:3]
                    request.data["userQuery"] = "User Query - " + request.data.get("userQuery") + " "+ "Data to refer to - " +  chunks[0].get("chunk") + " " + chunks[1].get("chunk") + " " + chunks[1].get("chunk")
                    print(type(request.data["userQuery"]))
                    datatosend["messages"]["history"].append({"role": "user", "content":request.data.get("userQuery")})
                    answer = getAnswer(datatosend["messages"]["history"])
                    datatosend["messages"]["history"].append({"role": "assistant", "content":answer})
                serializer = ChatSerializer(data=datatosend , partial=True)
                if(serializer.is_valid()):
                    serializer.save()
                else:
                    return Response(serializer.errors)
                return Response({"answer":answer})
            



        elif(request.data.get("Function") == "Tyod"):
            if(len(getchat)>0):
                updatemsg = getchat[0].messages
                res["files"] = request.data.get("filename")
                if(request.data.get("SysMsg")):
                    updatemsg["history"][0] = {"role": "system", "content": request.data.get("SysMsg")}
                else:
                    updatemsg["history"][0] = {"role": "system", "content": "you are a helpful assistant"}
                
                request.data["userQuery"] = getfiledata(request.data.get("filename") , request.data.get("userQuery"))
                updatemsg["history"].append({"role": "user", "content":request.data.get("userQuery")})
                answer = getAnswer(updatemsg["history"])
                updatemsg["history"].append({"role": "assistant", "content":answer})
                res["messages"] = updatemsg
                serializer = ChatSerializer(getchat[0], data=res, partial=True)
                if serializer.is_valid():
                    serializer.save()
                else:
                        return Response(serializer.errors)
                return Response({"answer":answer})
            
            else:
                answer = "Tyod Chat Created"
                datatosend = {"name":request.data.get("name")}
                datatosend["function"] = request.data.get("Function")
                datatosend["files"] = request.data.get("filename")
                datatosend["messages"] = {"history":[]}
                if(request.data.get("SysMsg")):
                    datatosend["messages"]["history"].append({"role": "system", "content": request.data.get("SysMsg")})
                else:
                    datatosend["messages"]["history"].append({"role": "system", "content": "you are a helpful assistant"})
                if(request.data.get("userQuery")):
                    request.data["userQuery"] = getfiledata(request.data.get("filename") , request.data.get("userQuery"))
                    datatosend["messages"]["history"].append({"role": "user", "content":request.data.get("userQuery")})
                    answer = getAnswer(datatosend["messages"]["history"])
                serializer = ChatSerializer(data=datatosend , partial=True)
                if(serializer.is_valid()):
                    serializer.save()
                else:
                    return Response(serializer.errors)
                return Response({"answer":answer})
                







        elif(request.data.get("Function") == "intSearch"):
            if(len(getchat)>0):
                res = {}
                s = ""
                answer = ""
                updatemsg = getchat[0].messages
                request.data["userQuery"] = "User Query "+ request.data["userQuery"] + " " +str(getGoogleSearch(request.data.get("userQuery")))
                updatemsg["history"].append({"role": "user", "content":request.data.get("userQuery")})
                answer = getAnswer(updatemsg["history"])
                updatemsg["history"].append({"role": "assistant", "content":answer})
                res["messages"] = updatemsg
                serializer = ChatSerializer(getchat[0], data=res, partial=True)
                if serializer.is_valid():
                    serializer.save()
                else:
                        return Response(serializer.errors)
                return Response({"answer":answer})
            else:
                print("in else")
                answer = "Internet Chat created"
                s = ""
                datatosend = {"name":request.data.get("name")}
                print(datatosend)
                datatosend["function"] = request.data.get("Function")
                datatosend["files"] = []
                datatosend["messages"] = {"history":[]}
                datatosend["messages"]["history"].append({"role": "system", "content": """you are an internet search bot the user will ask a query and your job is to answer that query. The data required to answer that query will be provided within the query in the following format UserQuery : UserQuery , Data : [url:url , data:data , url2:url2 , data2:data2]."""})
                if(request.data.get("userQuery")):
                    request.data["userQuery"] = "USER QUERY - {"+ request.data["userQuery"] + "} Data " +str(getGoogleSearch(request.data.get("userQuery")))
                    print(request.data["userQuery"])
                    datatosend["messages"]["history"].append({"role": "user", "content":request.data.get("userQuery")})
                    answer = getAnswer(datatosend["messages"]["history"])
                serializer = ChatSerializer(data=datatosend , partial=True)
                if(serializer.is_valid()):
                    serializer.save()
                else:
                    return Response(serializer.errors)
                print(answer)
                return Response({"answer":answer})

        else:
            if(len(getchat)>0):
                res = {}
                updatemsg = getchat[0].messages
                if(request.data.get("SysMsg")):
                    updatemsg["history"][0] = {"role": "system", "content": request.data.get("SysMsg")}
                else:
                    updatemsg["history"][0] = {"role": "system", "content": "you are a helpful assistant"}
                updatemsg["history"].append({"role": "user", "content": request.data.get("userQuery")})
                answer = getAnswer(updatemsg["history"])
                updatemsg["history"].append({"role": "assistant", "content": answer})
                res["messages"] = updatemsg
                serializer = ChatSerializer(getchat[0], data=res, partial=True)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(serializer.errors)
                return Response({"answer":answer})
            else:
                answer = "Chat Created"
                datatosend = {"name":request.data.get("name")}
                datatosend["function"] = request.data.get("Function")
                datatosend["files"] = []
                datatosend["messages"] = {"history":[]}
                if(request.data.get("SysMsg")):
                    datatosend["messages"]["history"].append({"role": "system", "content":request.data.get("SysMsg")})
                else:
                    datatosend["messages"]["history"].append({"role": "system", "content":"you are a helpful assistant"})
                if(request.data.get("userQuery")):
                    datatosend["messages"]["history"].append({"role": "user", "content":request.data.get("userQuery")})
                    answer = getAnswer(datatosend["messages"]["history"])
                    datatosend["messages"]["history"].append({"role": "assistant", "content":answer})
                serializer = ChatSerializer(data=datatosend , partial=True)
                if(serializer.is_valid()):
                    serializer.save()
                else:
                    return Response(serializer.errors)
                return Response({"answer":answer})
                
    if(request.data.get("filename")):
            if (request.data.get("filename")[0].lower().endswith(('.pdf'))):
                filenamelist = request.data.get("filename")
                res["files"] = filenamelist
                query_vector = Get_Embeddings(request.data.get("userQuery"))
                chunks = filecontent.objects.filter(filename__in=request.data.get("filename")).annotate(distance=L2Distance('feature_vector',query_vector)).order_by('distance').values('chunk','distance')[:3]
                finalquery = "Question " + request.data.get("userQuery")
                n = 1
                for chunk in chunks:
                    finalquery += " File " + str(n) + " " + chunk.get("chunk")
                    n = n+1
                request.data["userQuery"] = finalquery
            elif (request.data.get("filename")[0].lower().endswith(('.xlsx'))):
                
                filenamelist = request.data.get("filename")
                res["files"] = filenamelist
                finalquery = "Question " + request.data.get("userQuery")
                s  =""  
                userQuery = request.data.get("userQuery")
                userQuery_vector = numpy.array(Get_Embeddings(userQuery))
                data = excelfilecontent.objects.filter(filename__in=request.data.get("filename")).values('filename' , 'content')
                try:
                    for datapoints in data:
                        for realdata in datapoints.get("content").get('data'):
                            feature_vector = numpy.array(realdata["feature_vector"])
                            dist = numpy.linalg.norm(userQuery_vector-feature_vector)
                            if(dist<0.7):
                                s = s+ " " + realdata["alldata"]
                except:
                    pass
                finalquery = finalquery+ " Data " + s
                request.data["userQuery"] = finalquery    
    else:
        res["files"] = []
    if(len(getchat)>0):
        updatemsg = getchat[0].messages

        if(request.data.get("SysMsg")):
            try:
                if(updatemsg["history"][0].get("role") == 'user'):
                    updatemsg["history"].insert(0, {"role": "system", "content": request.data.get("SysMsg")})
                else:
                    updatemsg["history"][0] = {"role": "system", "content": request.data.get("SysMsg")}
            except:
                updatemsg["history"].append({"role": "system", "content": request.data.get("SysMsg")})
        
        if(not request.data.get("SysMsg")):
            if(request.data.get("Function") == "TYOD"):
                try:
                    if(updatemsg["history"][0].get("role") == 'user'):
                        updatemsg["history"].insert(0, {"role": "system", "content": "you are a file summarizer"})
                    else:
                        updatemsg["history"][0] = {"role": "system", "content": "you are a file summarizer"}
                except:
                    updatemsg["history"].append({"role": "system", "content": "you are a file summarizer"})
            else:
                try:
                    if(updatemsg["history"][0].get("role") == 'user'):
                        updatemsg["history"].insert(0, {"role": "system", "content": "you are a helpful assistant"})
                    else:
                        updatemsg["history"][0] = {"role": "system", "content": "you are a helpful assistant"}
                except:
                    updatemsg["history"].append({"role": "system", "content": "you are a file summarizer"})
        updatemsg["history"].append({"role": "user", "content": request.data.get("userQuery")})
        answer = getAnswer(updatemsg["history"])
        updatemsg["history"].append({"role": "assistant", "content": answer})

        res["messages"] = updatemsg
        serializer = ChatSerializer(getchat[0], data=res, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors)
        return Response({"answer":answer})
    else:
        datatosend = {"name":request.data.get("name")}
        if(request.data.get("filename")):
            datatosend["files"] = request.data.get("filename")
        else:
            datatosend["files"] = []
        datatosend["messages"] = {"history":[]}

        if(not request.data.get("userQuery")):
            serializer = ChatSerializer(data=datatosend , partial=True)
            if(serializer.is_valid()):
                serializer.save()
            else:
                return Response(serializer.errors)
            return Response({"answer":"chat updated"})
        if(request.data.get("SysMsg")):
            datatosend["messages"]["history"].append({"role": "system", "content": request.data.get("SysMsg")})

        
        if(not request.data.get("SysMsg")):
            if(request.data.get("Function") == "TYOD"):
               datatosend["messages"]["history"].append({"role": "system", "content": "you are a file summarizer"})
            else:
                datatosend["messages"]["history"].append({"role": "system", "content": "you are a helpful assistant"})
        
        if(request.data.get("userQuery")):
            datatosend["messages"]["history"].append({"role": "user", "content": request.data.get("userQuery")})
            answer = getAnswer(datatosend["messages"]["history"])
            datatosend["messages"]["history"].append({"role": "assistant", "content": answer})
        serializer = ChatSerializer(data=datatosend , partial=True)
        if(serializer.is_valid()):
            serializer.save()
        else:
            return Response(serializer.errors)
        
        return Response({"answer":answer})
# Create your views here.


@api_view(["POSt"])
def uploadfile(request):
    cnt = 0
    chunk = ""
    words = ""
    files = request.FILES['file']
    filename = str(files)
    if filename.lower().endswith(('.pdf')):
        reader = PdfReader(files)
        #get filename
        filenamedata = {"filename":filename}
        serializer = fileSerializer(data=filenamedata)
        if(serializer.is_valid()):
                serializer.save()
        else:
                return Response(serializer.errors)
        for page in reader.pages:
            words = page.extract_text()
            cnt = 0
            chunk = ""
            for i in words:
                if(cnt<2500):
                    chunk = chunk+i
                    cnt = cnt+1
                elif (cnt>=2500 and i ==".") or cnt>=3200:
                    chunk = chunk+i
                    data = {"filename":filename}
                    data["chunk"] = chunk
                    data["feature_vector"] = Get_Embeddings(chunk)
                    serializer = filecontentSerializer(data=data)
                    if(serializer.is_valid()):
                        serializer.save()
                    else:
                        return Response(serializer.errors)
                    cnt = 0
                    chunk = ""
                else:
                    chunk = chunk+i
                    cnt = cnt+1
            if(len(chunk)>=1):
                data = {"filename":filename}
                data["chunk"] = chunk
                data["feature_vector"] = Get_Embeddings(chunk)
                serializer = filecontentSerializer(data=data)
                if(serializer.is_valid()):
                    serializer.save()
                else:
                    return Response(serializer.errors)
        return Response({"status":"file uploaded"})
    elif filename.lower().endswith(('.xlsx')):
        filenamedata = {"filename":filename}
        serializer = fileSerializer(data=filenamedata)
        if(serializer.is_valid()):
                serializer.save()
        else:
                return Response(serializer.errors)
        finaldic = {}
        dfs = pd.read_excel(files, sheet_name=None)
        dic = dfs.get("Sheet1").to_dict('records')
        for data in dic:
            x = data.keys()
            s = ""
            for key in x:
                if type(data[key]) is not str:
                    data[key] = str(data[key])
                s = s+" "+key +" " + str(data[key])
            feature_vector = Get_Embeddings(s)
            data["feature_vector"] = feature_vector
            data["alldata"] = s
        finaldic["filename"] = filename
        finaldic["content"] = {"data":[]}
        finaldic["content"]["data"] = dic
        serializer = exexcelfilecontentSerializer(data=finaldic)
        if(serializer.is_valid()):
                serializer.save()
        else:
                return Response(serializer.errors)
        

        return Response(finaldic)
    else:
        return Response({"status":"please upload pdf file"})


@api_view(["POST"])
def searchxls(request):
    s  =""  
    userQuery = request.data.get("userQuery")
    userQuery_vector = numpy.array(Get_Embeddings(userQuery))
    data = excelfilecontent.objects.filter(filename__in=request.data.get("filenames")).values('filename' , 'content')
    for datapoints in data:
        for realdata in datapoints.get("content").get('data'):
            feature_vector = numpy.array(realdata["feature_vector"])
            dist = numpy.linalg.norm(userQuery_vector-feature_vector)
            if(dist<0.7):
                s = s+ " " + realdata["alldata"]

#0.70<
    # dist = numpy.linalg.norm(a-b)
    return Response({"okay":s}) 