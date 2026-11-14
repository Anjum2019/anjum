from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
vec=model.encode("a cat is sleeping on the couch") #thats the vector representation of the sentence and can do embedding for any sentence
print(vec.shape)
print(vec[:5])
#to compare two sentences we can use cosine similarity
from numpy import dot
from numpy.linalg import norm
v1 = model.encode("a cat is sleeping on the couch")
v2 = model.encode("a kitten is napping on the sofa")
similarity = dot(v1, v2)/(norm(v1)*norm(v2)) #cosine similarity formula
print(similarity) #this will give a value between 0 and 1, where 1 means the sentences are very similar and 0 means they are not similar at all     
