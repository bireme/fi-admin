#!/usr/bin/python
import MySQLdb
import json
import collections
import codecs
import sqlite3
import config
import urllib2
import logging
import xmltodict

def db():
    db = config.DATABASES['cwis']
    return MySQLdb.connect(host=db['host'], user=db['user'], passwd=db['password'], db=db['db'])


def auxdb():
    db = config.DATABASES['aux']
    return MySQLdb.connect(host=db['host'], user=db['user'], passwd=db['password'], db=db['db'])



def query_db(query, args=(), one=False):
    cur = db().cursor()
    cur.execute(query, args)
    rows = cur.fetchall()

    r = [dict((cur.description[i][0], value) \
               for i, value in enumerate(row)) for row in rows]

    cur.connection.close()

    return (r[0] if r else None) if one else r


def get_aux_id(field_name, field_value):
    # map field name (cwis) and model name (fi-admin)
    aux_model_names = {}
    aux_model_names = {'Format': 'format', 'Language': 'language', 'Type': 'type',
                       'Technical Resource Type': 'tecresourcetype',
                       'Audience':'audience', 'Interactivity Level' : 'interactivitylevel',
                       'Learning Resource Type': 'learningresourcetype',
                       'Difficulty': 'difficulty', 'Rights Licenses': 'license',
                       'Contributor' : 'contributor', 'Creator': 'creator',
                       'Learning Context': 'learningcontext', 'Structure': 'structure',
                       'Interactivity Type': 'interactivitytype', 'Course Type': 'coursetype',
                       }

    aux_model = aux_model_names[field_name]

    db = auxdb()
    cur = db.cursor()

    table_name = where_field = ''
    if field_name == 'Language':
        table_name = 'main_sourcelanguage'
        where_field = 'acronym'
    else:
        table_name = 'oer_{}'.format(aux_model)
        where_field = 'name'

    # verifica na tabela principal (ingles)
    cur.execute('SELECT id FROM {0} WHERE {1}="{2}" LIMIT 1'.format(table_name, where_field, field_value))
    # executa query
    record = cur.fetchall()

    if not record:
        if field_name != 'Language':
            # verifica na tabela de traducoes
            table_name_local = '{}local'.format(table_name)
            fk_field = '{}_id'.format(aux_model)
            cur.execute('SELECT {0} FROM {1} WHERE {2}="{3}" LIMIT 1'.format(fk_field, table_name_local,
                                                                             where_field, field_value))
            translation = cur.fetchall()
            if not translation:
                aux_id = None
                logging.warning('valor nao encontrando "{0}" nas traducoes "{1}"'.format(field_value,
                                                                                         field_name))
            else:
                aux_id = translation[0][0]
        else:
            aux_id = None
            logging.warning('valor nao encontrando "{0}" na lista controlada "{1}"'.format(field_value,
                                                                                           field_name))
    else:
        aux_id = record[0][0]

    return aux_id

def get_detail(field_id, field_id_name, field_list):
    detail = None
    search = [field for field in field_list if field[field_id_name] == field_id]
    if search:
        detail = search[0]

    return detail


def get_field_detail(field_id, field_list):
    return get_detail(field_id, 'FieldId', field_list)


def get_controlled_detail(field_id, field_list):
    return get_detail(field_id, 'ControlledNameId', field_list)

def get_decs_id(string):
    lang_list = ['es', 'en', 'pt']
    search_code_list = ['101', '102', '104'] # 101 (termo autorizado) / 102 (sinonimo) / 104 (termo historico)
    decs_service_url = "http://decs.bvsalud.org/cgi-bin/mx/cgi=@vmx/decs/"
    decs_id = ''
    term_query = string.strip()
    term_query = term_query.replace(' ','+').replace('(','').replace(')','')

    # busca termo nos termos autorizados, sinonimos e no historico
    for search_code in search_code_list:
        # busca termo nos 3 idiomas
        for lang in lang_list:
            service_url = '{}?bool={}+{}&lang={}'.format(decs_service_url, search_code, term_query, lang)
            response_xml = ''
            try:
                request = urllib2.urlopen(service_url)
                response_xml = request.read()
                request.close()
            except BadStatusLine:
                logging.warning('erro "BadStatusLine" na requisicao "{0}"'.format(service_url))

            if response_xml:
                try:
                    xml_dict = xmltodict.parse(response_xml)
                except KeyError:
                    xml_dict = {'decsvmx':''}

                if 'decsws_response' in xml_dict['decsvmx']:
                    try:
                        vmx_response = xml_dict['decsvmx']['decsws_response'][0]
                    except KeyError:
                        vmx_response = xml_dict['decsvmx']['decsws_response']

                    decs_id = vmx_response['record_list']['record']['@mfn']
                    break;

    if decs_id == '':
        logging.warning('termo DeCS nao localizado "{0}"'.format(string))

    return decs_id


# ===========================================================================================

# ativa log
logging.basicConfig(filename=config.log_filename,level=logging.DEBUG)

field_import_names = {}
field_import_names = {'Format': 'format', 'Language': 'language', 'Type': 'type',
                      'Technical Resource Type': 'tec_resource_type',
                      'Audience':'audience', 'Interactivity Level' : 'interactivity_level',
                      'Learning Resource Type': 'learning_resource_type',
                      'Difficulty': 'difficulty', 'Rights Licenses': 'license',
                      'Contributor' : 'contributor', 'Creator': 'creator',
                      'Learning Context': 'learning_context', 'Structure': 'structure',
                      'Status': 'status', 'Interactivity Type': 'interactivity_type',
                      'Course Type': 'course_type', 'Aggregation Level': 'aggregation_level',
                      'Free Keywords': 'free_keywords', 'Publisher': 'publisher',
                     }

# fields that are sequences
sequence_fields = ['format', 'course_type', 'audience', 'tec_resource_type',]
# fields that are json in fi-admin
json_fields = ['creator', 'contributor']


# list of fields that are controlled list in CWIS and must be convert to string in FI-AMIN
convert_to_text_fields = ['Creator', 'Contributor', 'Publisher', 'Free Keywords',
                          'Aggregation Level', 'Status']

# load controlled lists
controlled_name_list = query_db('SELECT * FROM ControlledNames')
# load field list
field_list = query_db('SELECT * FROM MetadataFields')
# load resource list
#resource_list = query_db('SELECT * FROM Resources WHERE ResourceId=2855')
resource_list = query_db('SELECT * FROM Resources')

convert_list = []
next_id = config.START_ID

for resource in resource_list:
    r = {}
    # Only convert published resources
    if resource['ReleaseFlag'] == 1:
        resource_id = resource['ResourceId']
        logging.info('[inicio conversao] resource id:{}'.format(resource_id))

        r['model'] = 'oer.oer'
        r['pk'] = next_id
        r['fields'] = {}
        r['fields']['CVSP_resource'] = True
        r['fields']['cvsp_node'] = config.cvsp_node
        r['fields']['cooperative_center_code'] = config.cc_code
        r['fields']['title'] = resource['Title']
        r['fields']['learning_objectives'] = resource['LearningObjectives']
        r['fields']['description'] = resource['Description']
        if resource['TypicalLearningTime']:
            r['fields']['typical_learning_time'] = resource['TypicalLearningTime']
        if resource['Size']:
            r['fields']['size'] = resource['Size']
        if resource['TechnicalRequirements']:
            r['fields']['technical_requirements'] = resource['TechnicalRequirements']

        resource_created_time = resource['DateOfRecordCreation'].strftime('%Y-%m-%dT%H:%M:%S.000Z')
        resource_updated_time = resource['DateLastModified'].strftime('%Y-%m-%dT%H:%M:%S.000Z')
        r['fields']['created_time'] = resource_created_time
        r['fields']['updated_time'] = resource_updated_time
        r['fields']['created_by'] = 2

        meta_fields = query_db('SELECT * FROM `ResourceNameInts` WHERE `ResourceId`=%s', (resource_id,))

        for field in meta_fields:
            controlled_name_id = field['ControlledNameId']
            field_data = get_controlled_detail(controlled_name_id, controlled_name_list)

            if field_data:
                field_id = field_data['FieldId']
                field_detail = get_field_detail(field_id, field_list)
                field_name = field_detail['FieldName']
                field_name_import = field_import_names[field_name]
                field_value = field_data['ControlledName'].strip()

                # save id for controlled list OR value for other fields
                if field_name not in convert_to_text_fields:
                    field_value_id = get_aux_id(field_name, field_value)
                    if field_value_id:
                        if field_name_import in sequence_fields:
                            if field_name_import not in r['fields']:
                                r['fields'][field_name_import] = list()
                            r['fields'][field_name_import].append(field_value_id)
                        else:
                            r['fields'][field_name_import] = field_value_id

                else:
                    if field_name_import in json_fields:
                        json_value = {'text': field_value}
                        r['fields'][field_name_import] = list()
                        r['fields'][field_name_import].append(json_value)
                    else:
                        r['fields'][field_name_import] = field_value

        # overwrite status value for Draft
        r['fields']['status'] = -1

        # add to convertion list
        convert_list.append(r)
        if resource['Url']:
            u = {}
            u['model'] = 'oer.oerurl'
            u['pk'] = None
            u['fields'] = {}
            u['fields']['oer'] = next_id
            u['fields']['url'] = resource['Url']
            u['fields']['created_time'] = resource_created_time
            u['fields']['updated_time'] = resource_updated_time
            r['fields']['created_by'] = 2
            # add to convertion list
            convert_list.append(u)

        # DeCS
        decs_string = resource['Decs']
        decs_list = decs_string.split(', ')

        for term in decs_list:

            decs_id = get_decs_id(term)
            if decs_id:
                d = {}
                d['model'] = 'main.descriptor'
                d['pk'] = None
                d['fields'] = {}
                d['fields']['object_id'] = next_id
                d['fields']['content_type'] = config.oer_content_type_id
                d['fields']['text'] = term.strip()
                d['fields']['code'] = str(decs_id)
                d['fields']['primary'] = True
                d['fields']['status'] = '1'
                d['fields']['created_time'] = resource_created_time
                r['fields']['created_by'] = 2
                # add to convertion list
                convert_list.append(d)
        # update next_id
        next_id = next_id+1
        logging.info('[final conversao] resource id:{}'.format(resource_id))


json_result = json.dumps(convert_list, ensure_ascii=False, indent=4)
json_result = json_result.decode('iso-8859-1').encode('utf8')

file_export = open(config.export_filename, 'w')
file_export.write(json_result)
file_export.close()

# print json_result

db().close()
auxdb().close()
