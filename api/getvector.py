from helpers import *
import numpy
import json
def electricorpetrol():
    vectors = []
    wants_scooter_scooty_moped = [
    "I want a scooter.",
    "I would like to have a scooter.",
    "I need a scooter.",
    "I'm looking to get a scooter.",
    "I desire a scooter.",
    "I wish to own a scooter.",
    "I plan to buy a scooter.",
    "I'm interested in getting a scooter.",
    "I hope to acquire a scooter.",
    "I'd love to have a scooter.",
    "I want a scooty.",
    "I would like to have a scooty.",
    "I need a scooty.",
    "I'm looking to get a scooty.",
    "I desire a scooty.",
    "I wish to own a scooty.",
    "I plan to buy a scooty.",
    "I'm interested in getting a scooty.",
    "I hope to acquire a scooty.",
    "I'd love to have a scooty.",
    "I want a moped.",
    "I would like to have a moped.",
    "I need a moped.",
    "I'm looking to get a moped.",
    "I desire a moped.",
    "I wish to own a moped.",
    "I plan to buy a moped.",
    "I'm interested in getting a moped.",
    "I hope to acquire a moped.",
    "I'd love to have a moped."
]


    for sentence in wants_scooter_scooty_moped:
        vectors.append(numpy.array(Get_Embeddings(sentence)))
        print(sentence)
    print(len(vectors))
    vector_array = numpy.array(vectors)
    average_vector = numpy.mean(vector_array, axis=0)
    print(average_vector)
    return average_vector



average_vector = electricorpetrol()
average_vector_list = average_vector.tolist()

# Save the average vector list to a file
file_path = 'average_vector.json'
with open(file_path, 'w') as file:
    json.dump(average_vector_list, file)