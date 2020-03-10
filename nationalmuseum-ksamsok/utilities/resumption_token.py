def parse_resumption_token(resumption_token):
    '''
    <set-name>_<cursor>
    '''

    parsed_token = {}
    parsed_token['set'], parsed_token['cursor'] = resumption_token.split('_')
    return parsed_token
