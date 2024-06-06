from openai import OpenAI
client = OpenAI()

def Get_Embeddings(embedding_string):
  response = client.embeddings.create(
    input= embedding_string,
    model="text-embedding-ada-002"
  )
  feature_vector = response.data[0].embedding
  return feature_vector

def getAnswer(messages):
  
  response = client.chat.completions.create(
  model="gpt-4o",
  messages=messages
  )
  return response.choices[0].message.content