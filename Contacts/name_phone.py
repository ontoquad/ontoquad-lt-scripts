import android,urllib

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
    concept_uri = 'http://www.ontos.com/ontobase#Contacts'
    executeDelete(concept_uri)	

    for cid in droid.contactsGetIds().result:
        subj_uri = 'http://contact'+str(cid)
        filter = 'contact_id='+str(cid)

        # add type triple
        triples = [Triple(subj_uri, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type', concept_uri)]

        # add label triple
        content = droid.queryContent('content://com.android.contacts/data',['display_name'], filter).result	
        if len(content)==0:
            content = [{'display_name':str(cid)}] # must add at least one label
	for row in content:	
	    triples += map2triples(subj_uri, row, {'display_name':'http://www.w3.org/2000/01/rdf-schema#label'} )

        # add phones
        for row in droid.queryContent('content://com.android.contacts/data/phones',['data1'], filter).result:
	    triples += map2triples(subj_uri, row, {'data1':'http://www.ontos.com/ontobase#phone'} )

        # add emails
        for row in droid.queryContent('content://com.android.contacts/data/emails',['data1'], filter).result:
	    triples += map2triples(subj_uri, row, {'data1':'http://www.ontos.com/ontobase#email'} )

        executeInsert(triples)
        

main()
