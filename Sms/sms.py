import android,urllib, datetime

class Triple:
    def __init__(self, s, p, o):
        self.ss = s
        self.pp = p
        self.oo = o
    def toString(self):
        return '<' + self.ss + '> <' + self.pp + '> ' + ('<' + self.oo + '>' if self.oo.startswith('http://') else '"' + self.oo + '"')

def executeInsert(triples):
    endpoint = 'http://127.0.0.1:8080/sparql'

    query = 'INSERT DATA {\n'
    for triple in triples:
        query += triple.toString()
        query += '.\n'
    query += '\n}'
	
    query = query.encode('utf8')
    
    print query
    params = urllib.urlencode({'query':query})    
    urllib.urlopen(endpoint, params)

def executeDelete(concept_uri):
    endpoint = 'http://127.0.0.1:8080/sparql'

    query = 'DELETE WHERE {\n'
    query += '?s ?p ?o.\n'
    query += ('?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <' + concept_uri + '>.\n')
    query += '}'
	
    query = query.encode('utf8')
    
    print query
    params = urllib.urlencode({'query':query})    
    urllib.urlopen(endpoint, params)


def map2triples(subj_uri, data_map, attr_map):
    res = []
    for item in data_map.items():
        predicate = 'http://www.ontos.com/ontobase#'+item[0] if (attr_map==None or not attr_map.has_key(item[0])) else attr_map[item[0]]
        res.append( Triple(subj_uri, predicate, item[1]) )        
    return res
                    
def main():
    droid = android.Android()
    concept_uri = 'http://www.ontos.com/ontobase#Sms'
    executeDelete(concept_uri)

    for cid in droid.smsGetMessageIds(False).result:
        subj_uri = 'http://sms'+str(cid)

        # add type triple
        triples = [Triple(subj_uri, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type', concept_uri)]

	# body, address
	sms = droid.smsGetMessageById(cid,['address','body']).result
	address = sms['address']
	triples += map2triples(subj_uri, sms, None)

	#date - needs convertion to string
	sms = droid.smsGetMessageById(cid,['date']).result
	timestamp = sms['date']
	date = datetime.datetime.fromtimestamp(long(timestamp)/1000)
	sms['date'] = date.strftime('%Y/%m/%d %H:%M:%S')	
	triples += map2triples(subj_uri, sms, None)
		
        # add label triple
	label = sms['date'] + ' ' + address
        triples.append(Triple(subj_uri, 'http://www.w3.org/2000/01/rdf-schema#label', label))

        executeInsert(triples)
        

main()
