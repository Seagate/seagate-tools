
from pymongo import MongoClient

rhost = "mongodb://sampada:password@cftic1.pun.seagate.com:27017,cftic2.pun.seagate.com:27017,apollojenkins.pun.seagate.com:27017/test?authSource=performance_db&replicaSet=rs0&readPreference=primary&appname=MongoDB%20Compass%20Community&ssl=false"
client = MongoClient(rhost)
db = client['performance_db']

collection = db.results
# cursor = collection.find({'Build':'NA'})

# for doc in cursor:
#     print(doc)
#     collection.update_one(doc,
#     {
#         "$set": {
#             'Build' : 'r2-568-custom'
#         }
#     })

cursor = collection.find({'Title': 'Main Chain'})
for doc in cursor:
    print(doc)
    collection.update_one(doc,
    {
        "$set": {
            'release': ['RHEL-2790', 'RHEL-2798', 'RHEL-2801', 'RHEL-2801-ssd', 'RHEL-2809'],
            'cortx1': ['RHEL-cortx-1.0.0-rc1', 'RHEL-cortx-1.0.0-rc3', '19', 'RHEL-52', 'RHEL-108', 'RHEL-113', 'RHEL-120', 'RHEL-144', 'RHEL-146', 'RHEL-211', '216', 'RHEL-270', 'RHEL-304', '304', '394', '398', '403', '403-90%-PC5', '463', '515', '515-70%-PC5', '515-80%-PC5', '515-90%-PC5', '531-6019p', '515-99%-PC5', '573-6019p'],
            'custom': ['r2-568-custom']
        }
    })

# cursor = collection.find({'Build':'r2-568-custom','Name':'Cosbench'})

# for doc in cursor:
#     collection.delete_one(doc)