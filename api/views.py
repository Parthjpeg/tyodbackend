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
    if(request.data.get("filename")):
            if (request.data.get("filename")[0].lower().endswith(('.pdf'))):
                filenamelist = request.data.get("filename")
                res["files"] = filenamelist
                print("in if")
                query_vector = Get_Embeddings(request.data.get("userQuery"))
                chunks = filecontent.objects.filter(filename__in=request.data.get("filename")).annotate(distance=L2Distance('feature_vector',query_vector)).order_by('distance').values('chunk','distance')[:3]
                print(chunks)
                finalquery = "Question " + request.data.get("userQuery")
                n = 1
                for chunk in chunks:
                    finalquery += " File " + str(n) + " " + chunk.get("chunk")
                    n = n+1
                print(finalquery)
                request.data["userQuery"] = finalquery
            elif (request.data.get("filename")[0].lower().endswith(('.xlsx'))):
                filenamelist = request.data.get("filename")
                res["files"] = filenamelist
                finalquery = "Question " + request.data.get("userQuery")
                s  =""  
                userQuery = request.data.get("userQuery")
                userQuery_vector = numpy.array(Get_Embeddings(userQuery))
                data = excelfilecontent.objects.filter(filename__in=request.data.get("filename")).values('filename' , 'content')
                print(data)
                try:
                    for datapoints in data:
                        print(datapoints.get("filename"))
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
            if(updatemsg["history"][0].get("role") == 'user'):
                updatemsg["history"].insert(0, {"role": "system", "content": request.data.get("SysMsg")})
            else:
                updatemsg["history"][0] = {"role": "system", "content": request.data.get("SysMsg")}
        
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
        print(res)
        # print(dic1)
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
            print(datatosend)
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
    print(filename)
    if filename.lower().endswith(('.pdf')):
        reader = PdfReader(files)
        print(len(reader.pages))
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
            if(len(chunk)>1):
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
            print(type(feature_vector))
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
        print(datapoints.get("filename"))
        for realdata in datapoints.get("content").get('data'):
            feature_vector = numpy.array(realdata["feature_vector"])
            dist = numpy.linalg.norm(userQuery_vector-feature_vector)
            if(dist<0.7):
                s = s+ " " + realdata["alldata"]

#0.70<
    # dist = numpy.linalg.norm(a-b)
    return Response({"okay":s}) 