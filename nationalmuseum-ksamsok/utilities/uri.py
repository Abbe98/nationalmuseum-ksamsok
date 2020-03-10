def new_uri(institution, obj_id):
    return 'http://kulturarvsdata.se/{}/objekt/{}'.format(institution, obj_id)

def local_id_from_uri(uri):
    return uri.split('/')[-1]
