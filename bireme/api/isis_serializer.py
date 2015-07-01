from tastypie.serializers import Serializer


class ISISSerializer(Serializer):
    formats = ['json', 'xml', 'isis_id']
    content_types = {
        'json': 'application/json',
        'xml': 'application/xml',
        'isis_id': 'text/plain',
    }

    def __init__(self, formats=None, content_types=None, datetime_formatting=None, field_tag=[]):
        # field_tag dict with the mapping of field name and field number. ex. field_tag['database'] = '04'
        self.field_tag = field_tag

        return super(ISISSerializer, self).__init__(formats, content_types, datetime_formatting)

    def to_isis_id(self, data, options=None):
        options = options or {}
        context = {}
        id_lines = []
        data = self.to_simple(data, options)

        objects = data.get('objects', [])

        for item in objects:
            for field_name in item:
                field = item[field_name]
                # check if field is not empty
                if field:
                    if field_name == 'MFN':
                        mfn_line = "!ID {0}\n".format(field)
                        id_lines.append(mfn_line)

                    # JSONField is returned as list from tastypie_custom class
                    elif type(field) is list:
                        # create a temp str field_value with all subfields of current occ
                        for field_occ in field:
                            field_value = ''
                            for key, value in field_occ.iteritems():
                                subfield_id = "^{0}".format(key[1]) if key.startswith('_') else ''
                                subfield = u''.join((subfield_id, value)).encode('utf-8').strip()
                                field_value = ''.join((field_value, subfield))

                            # format out line in ID format
                            id_field = self.id_field(field_name, field_value)
                            id_lines.append(id_field)
                    else:
                        # check for fields with multiples lines as occurrences
                        if isinstance(field, basestring) and "\n" in field:
                            for field_line in field.split('\n'):
                                id_field = self.id_field(field_name, field_line)
                                id_lines.append(id_field)
                        else:
                            id_field = self.id_field(field_name, field)
                            id_lines.append(id_field)

        id_lines.sort()
        return ''.join(id_lines)

    def id_field(self, field, value):
        id_field = ''
        field_number = self.field_tag.get(field, None)
        if field_number:
            if type(value) is unicode:
                field_value = value.encode('utf-8').strip()
            else:
                field_value = str(value)

            id_field = "!v{0}!{1} \n".format(field_number, field_value)

        return id_field
