from helpers import *
import numpy
import json
def electricorpetrol():
    vectors = []
    wants_scooter_scooty_moped  = [
    "The answer is incorrect.",
    "That's wrong.",
    "Unfortunately, that's not right.",
    "Incorrect.",
    "You've missed it.",
    "That's not quite right.",
    "Sorry, that's not correct.",
    "That's not the answer.",
    "No, that's incorrect.",
    "That's a mistake.",
    "That's not accurate."
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