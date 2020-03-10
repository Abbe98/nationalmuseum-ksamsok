
import os
import time

from flask import Flask, render_template, request, Response

from sets import sets

from mappings.natmus_obj import NatmusObj
from utilities.resumption_token import parse_resumption_token

app = Flask(__name__)

try:
    base_url = os.environ['BASEURL']
    repository_name = os.environ['REPOSITORYNAME']
    admin_email = os.environ['ADMINEMAIL']
except KeyError:
    print('Missing environment variable.')
    exit()

response_date = time.strftime('%Y-%m-%d')

# TODO refactor this routing
@app.route('/', methods=['GET'])
def index():
    verb = request.args.get('verb')
    metadata_format = request.args.get('metadataPrefix')
    data_set = request.args.get('set')
    resumption_token = request.args.get('resumptionToken')
    identifier = request.args.get('identifier')

    if verb == 'Identify':
        return Response(render_template('identify.xml',
            base_url=base_url,
            repository_name=repository_name,
            admin_email=admin_email,
            response_date=response_date
        ), mimetype='text/xml')
    elif verb == 'ListMetadataFormats':
        return Response(render_template('list_metadata_formats.xml',
            base_url=base_url,
            response_date=response_date
        ), mimetype='text/xml')
    elif verb == 'ListSets':
        return Response(render_template('list_sets.xml',
            base_url=base_url,
            response_date=response_date,
            sets=sets
        ), mimetype='text/xml')
    elif verb == 'GetRecord':
        if identifier:
            record = NatmusObj.get_record_from_identifier(identifier)
            if record == None:
                return Response(render_template('errors/id_does_not_exists.xml',
                    base_url=base_url,
                    response_date=response_date,
                    uri=identifier
                ), mimetype='text/xml')
            return Response(render_template('get_record.xml',
                base_url=base_url,
                response_date=response_date,
                record=record[0],
                uri=record[1],
                set='natmus-obj',
            ), mimetype='text/xml')
    # TODO badArgument error
    elif verb == 'ListRecords':
        if resumption_token:
            resumption_token = parse_resumption_token(resumption_token)
            data_set = resumption_token['set']

        if data_set not in list(map(lambda x: x[0], sets)):
            return Response(render_template('errors/missing_set.xml',
                base_url=base_url,
                response_date=response_date
            ), mimetype='text/xml')

        if data_set == 'natmus-obj':
            if resumption_token:
                token_and_records = NatmusObj.list_records_from_cursor(cursor=resumption_token['cursor'])
            else:
                token_and_records = NatmusObj.list_records_from_cursor()

            return Response(render_template('list_records.xml',
                base_url=base_url,
                resumption_token=token_and_records[0],
                records=token_and_records[1],
                set=data_set
            ), mimetype='text/xml')

    else:
      return Response(render_template('errors/bad_verb.xml',
          base_url=base_url,
          response_date=response_date
      ), mimetype='text/xml')

if __name__ == '__main__':
    app.run()
