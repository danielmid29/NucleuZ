from pymongo import MongoClient

client = MongoClient("ec2-51-20-251-66.eu-north-1.compute.amazonaws.com",27017)

db = client['nucleuz']
    