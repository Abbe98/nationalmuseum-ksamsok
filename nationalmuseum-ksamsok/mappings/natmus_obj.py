import os
import time

import requests

from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, FOAF, NamespaceManager
from utilities import iiif, licensing
from utilities.uri import new_uri, local_id_from_uri
from mappings.presentation_generic import presentation_template

class NatmusObj:
    natmus_endpoint = None
    try:
        natmus_endpoint = os.environ['NATMUS_ENDPOINT']
    except KeyError:
        print('Missing environment variable.')
        exit()

    endpoint = '{}objects?limit=100'.format(natmus_endpoint)
    set_name = 'natmus-obj'
    source_endpoint = 'http://collection.nationalmuseum.se/eMP/eMuseumPlus?service=ExternalInterface&module=collection&objectId='

    @staticmethod
    def list_records_from_cursor(cursor='1'):
        resumption_token = '{}_{}'.format(NatmusObj.set_name, int(cursor) + 1)

        r = requests.get(NatmusObj.endpoint + '&page=' + cursor)
        data = r.json()

        if data['data']['paging']['current_page'] == data['data']['paging']['total_pages']:
            resumption_token = ''
        #resumption_token = ''

        records = list()
        for item in data['data']['items']:
            records.append(NatmusObj.write_soch_rdf(item))
        return [resumption_token, records]

    @staticmethod
    def get_record_from_identifier(identifier):
        r = requests.get('{}objects/{}'.format(NatmusObj.natmus_endpoint, local_id_from_uri(identifier)))
        data = r.json()

        # The API does not use http status codes...
        if not data['data']:
            return None

        return NatmusObj.write_soch_rdf(data['data'][0])

    @staticmethod
    def write_soch_rdf(item):
        graph = Graph()
        SOCH = Namespace('http://kulturarvsdata.se/ksamsok#')
        PRES = Namespace('http://kulturarvsdata.se/presentation#')
        graph.bind('ksam', SOCH)
        graph.bind('pres', PRES)

        uri = new_uri('natmus', item['id'])
        record = URIRef(uri)
        graph.add((record, SOCH.ksamsokVersion, Literal('1.11'))) # TODO should be 1.2.0 but does not work in SOCH for now
        graph.add((record, RDF.type, URIRef('http://kulturarvsdata.se/ksamsok#Entity')))
        graph.add((record, SOCH.serviceName, Literal('objekt')))
        graph.add((record, SOCH.serviceOrganization, Literal('natmus')))
        graph.add((record, SOCH.serviceOrganizationFull, Literal('Nationalmuseum')))
        graph.add((record, SOCH.url, Literal('{}{}'.format(NatmusObj.source_endpoint, item['id']))))
        graph.add((record, SOCH.subject, URIRef('http://kulturarvsdata.se/resurser/subject#art')))
        graph.add((record, SOCH.itemSuperType, URIRef('http://kulturarvsdata.se/resurser/entitysupertype#object')))
        graph.add((record, SOCH.itemType, URIRef('http://kulturarvsdata.se/resurser/entitytype#object')))
        graph.add((record, SOCH.dataQuality, URIRef('http://kulturarvsdata.se/resurser/dataquality#raw')))

        graph.add((record, SOCH.itemLicense, URIRef('http://kulturarvsdata.se/resurser/license#cc0')))
        graph.add((record, SOCH.itemLicenseUrl, URIRef('http://creativecommons.org/publicdomain/zero/1.0/')))

        p_label = None
        if item['title']['sv']:
            graph.add((record, SOCH.itemLabel, Literal(item['title']['sv'], lang='sv')))
            p_label = item['title']['sv']
        else:
            p_label = 'Objekt'

        if item['category']['sv']:
            graph.add((record, SOCH.itemClassName, Literal(item['category']['sv'], lang='sv')))

        for tag in item['material_tags']:
            graph.add((record, SOCH.itemKeyWord, Literal(tag)))

        for tag in item['technique_tags']:
            graph.add((record, SOCH.itemKeyWord, Literal(tag)))

        p_description = None
        if item['descriptions']['sv']:
            des = BNode('des')
            graph.add((record, SOCH.itemDescription, des))
            graph.add((des, SOCH.type, Literal('Beskrivning', lang='sv')))
            graph.add((des, SOCH.desc, Literal(item['descriptions']['sv'].replace('', ''), lang='sv'))) # replaces unicode x0c
            p_description = item['descriptions']['sv'].replace('', '')

        if item['inscription']:
            ins = BNode('ins')
            graph.add((record, SOCH.itemInscription, ins))
            graph.add((ins, SOCH.type, Literal('Inskription', lang='sv')))
            graph.add((ins, SOCH.text, Literal(item['inscription'], lang='sv')))

        #if item['motive_category']:
        #if item['signature']:
        #if item['style']:

        # actors

        if item['technique_material']['sv']:
            mat = BNode('mat1')
            graph.add((record, SOCH.itemMaterial, mat))
            graph.add((mat, SOCH.type, Literal('Material', lang='sv')))
            graph.add((mat, SOCH.material, Literal(item['technique_material']['sv'], lang='sv')))

        if item['acquisition_year']:
            acq_evt = BNode('acq_evt')
            graph.add((record, SOCH.context, acq_evt))
            graph.add((acq_evt, SOCH.contextSuperType, URIRef('http://kulturarvsdata.se/resurser/ContextSuperType#interact')))
            graph.add((acq_evt, SOCH.contextType, URIRef('http://kulturarvsdata.se/resurser/ContextType#transact')))
            graph.add((acq_evt, SOCH.fromTime, Literal(item['acquisition_year'])))
            graph.add((acq_evt, SOCH.toTime, Literal(item['acquisition_year'])))
            if item['acquisition']['sv']: graph.add((acq_evt, SOCH.eventName, Literal(item['acquisition']['sv'], lang='sv')))

        if item['inventory_number']:
            num = BNode('num1')
            graph.add((record, SOCH.itemNumber, num))
            graph.add((num, SOCH.type, Literal('Inventarienummer', lang='sv')))
            graph.add((num, SOCH.number, Literal(item['inventory_number'])))

        p_image = dict()
        if item['iiif']:
            img = BNode('img')
            graph.add((record, SOCH.image, img))
            graph.add((img, SOCH.mediaType, Literal('image/jpeg')))
            graph.add((img, SOCH.thumbnailSource, Literal(iiif.get_thumbnail(item['iiif']))))
            graph.add((img, SOCH.lowresSource, Literal(iiif.get_medium(item['iiif']))))
            graph.add((img, SOCH.highresSource, Literal(iiif.get_max(item['iiif']))))

            license = licensing.resolve_license(item['iiif_license']['license'])
            graph.add((img, SOCH.mediaLicense, URIRef(license[0])))
            graph.add((img, SOCH.mediaLicenseUrl, URIRef(license[1])))
            if item['iiif_license']['copyright']: graph.add((img, SOCH.copyright, Literal(item['iiif_license']['copyright'])))
            if item['iiif_license']['creditline']: graph.add((img, SOCH.byline, Literal(item['iiif_license']['creditline'])))

            p_image['src'] = iiif.get_max(item['iiif'])
            p_image['license'] = license[0]
            if item['iiif_license']['copyright']: p_image['copyright'] = item['iiif_license']['copyright']
            if item['iiif_license']['creditline']: p_image['byline'] = item['iiif_license']['creditline']


            graph.add((record, SOCH.thumbnail, Literal(iiif.get_thumbnail(item['iiif']))))
            graph.add((record, SOCH.isVisualizedBy, URIRef(item['iiif'])))

        # TODO move to URI utilities
        format_index = uri.rindex('/')
        html_url = uri[:format_index] + '/html' + uri[format_index:]
        presenation_url = uri[:format_index] + '/xml' + uri[format_index:]

        presenation = presentation_template.render(
            uri=uri,
            id=item['id'],
            label=p_label,
            description=p_description,
            image=p_image,
            html=html_url,
            xml=presenation_url,
            org='Nationalmuseum',
            org_short='natmus',
            service='objekt'
            )
        # Hack both for sterilization and https://github.com/RDFLib/rdflib/issues/965
        presentation = '<ksam:presentation xmlns:pres="http://kulturarvsdata.se/presentation#" rdf:parseType="Literal">{}</ksam:presentation>'.format(presenation)
        graph.add((record, SOCH.presentation, PRES.tmp)) # hack to avoid sterilization of presentation XML (injected later)

        for dimension in item['dimensions']:
            mea = BNode()
            graph.add((record, SOCH.itemMeasurement, mea))
            graph.add((mea, SOCH.type, Literal(dimension['type'])))
            graph.add((mea, SOCH.unit, Literal(dimension['unit'])))

            value = str(dimension['value_1'])
            if dimension['value_2'] is not None:
                value = value + ', {}'.format(str(dimension['value_2']))
            if dimension['value_3'] is not None:
                value = value + ', {}'.format(str(dimension['value_3']))
            graph.add((mea, SOCH.value, Literal(value)))

        for exhibition in item['exhibitions']:
            exh = BNode()
            graph.add((record, SOCH.context, exh))
            graph.add((exh, SOCH.eventName, Literal(exhibition['title'], lang='sv')))
            graph.add((exh, SOCH.contextSuperType, URIRef('http://kulturarvsdata.se/resurser/ContextSuperType#interact')))
            graph.add((exh, SOCH.contextType, URIRef('http://kulturarvsdata.se/resurser/ContextType#display')))
            if exhibition['start']:
                graph.add((exh, SOCH.fromTime, Literal(exhibition['start'][:10])))
            if exhibition['end']:
                graph.add((exh, SOCH.toTime, Literal(exhibition['end'][:10])))

        created_date = None
        designed_date = None
        for dating in item['dating']:
            if dating['date_type'] == 'Utförd' or dating['date_type'] == 'Tillverkad':
                created_date = [dating['date_earliest'], dating['date_latest'], dating['date']['sv']]
            if dating['date_type'] == 'Formgiven':
                designed_date = [dating['date_earliest'], dating['date_latest'], dating['date']['sv']]


        for actor in item['actors']:
            if actor['actor_role'] == 'Konstnär' or actor['actor_role'] == 'Utförd av':
                evt = BNode()
                graph.add((record, SOCH.context, evt))
                graph.add((evt, SOCH.contextSuperType, URIRef('http://kulturarvsdata.se/resurser/ContextSuperType#interact')))
                graph.add((evt, SOCH.contextType, URIRef('http://kulturarvsdata.se/resurser/ContextType#produce')))

                if created_date:
                    graph.add((evt, SOCH.fromTime, Literal(created_date[0])))
                    graph.add((evt, SOCH.toTime, Literal(created_date[1])))
                    graph.add((evt, SOCH.eventName, Literal(created_date[2])))

                if actor['actor_full_name'] == 'Okänd':
                    graph.add((evt, SOCH.actor, URIRef('http://www.wikidata.org/entity/Q4233718')))
                else:
                    graph.add((evt, FOAF.fullName, Literal(actor['actor_full_name'])))
                    for link in actor['links']:
                        if link['link']: # TODO this in needed bacause sometimes link is set but to NoneType?
                            graph.add((evt, SOCH.actor, URIRef(link['link'])))

        rdf_xml = graph.serialize(format='xml').decode('utf-8').replace('<?xml version="1.0" encoding="UTF-8"?>', '').replace('<ksam:presentation rdf:resource="http://kulturarvsdata.se/presentation#tmp"/>', presentation)
        return [rdf_xml, uri]
