import pymongo
from pymongo import MongoClient

rhost = "mongodb://sampada:password@cftic1.pun.seagate.com:27017,cftic2.pun.seagate.com:27017,apollojenkins.pun.seagate.com:27017/test?authSource=performance_db&replicaSet=rs0&readPreference=primary&appname=MongoDB%20Compass%20Community&ssl=false"
client = MongoClient(rhost)
db = client['performance_db']

def printData(build,bench,operation,buckets,objects,sessions,param,subparam=None):
    if subparam == None:
        operation = operation.lower()
        query = {'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '4Kb','Buckets':buckets,'Objects':objects,'Sessions':sessions}
        cursor = db.results.find(query)
        print(cursor[0])


#printData('403','Cosbench','write', 50, 100, 100, 'Throughput', None)


# cursor = db.results.find({'Build':'403','Name':'Cosbench', 'Operation':'write', 'Buckets': 50, 'Objects': 100, 'Sessions': 100})
# for doc in cursor:
#     print(doc)

def getObjectUnit(unit,bench):
    if bench == 'Cosbench':
        return ' ' + unit.upper()
    else:
        return unit

print(getObjectUnit('Kb','Cosbench'))
bench = 'S3bench'
cursor = db.results.find({'Build':'403','Name': 'S3bench', 'Operation':'Write','Object_Size': '4'+getObjectUnit('Kb',bench)})
for doc in cursor:
    print(doc['IOPS'])