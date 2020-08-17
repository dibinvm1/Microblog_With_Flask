from flask import current_app

def addToIndex(index,model):
    if not current_app.elasticsearch:
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, id=model.id, body=payload)

def removeFromIndex(index, model):
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)

def queryIndex(index, query, page, perPage):
    if not current_app.elasticsearch:
        return
    search = current_app.elasticsearch.search(index = index, body=
    {'query' : {'multi_match':{'query': query, 'fields' : ['*']}},
    'from': (page -1) * perPage,'size': perPage})
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']['value']