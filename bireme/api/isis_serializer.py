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
        record_lines = []
        data = self.to_simple(data, options)

        objects = data.get('objects', [])

        for item in objects:
            # Add line that represent new record
            mfn_line = "!ID 00000\n"
            id_lines.append(mfn_line)

            record_lines = []
            for field_name in item:
                field = item.get(field_name)
                # check if field is not empty
                if field:
                    if isinstance(field, list):
                        # create a temp str field_value with all subfields of current occ
                        for field_occ in field:
                            field_value = ''
                            if isinstance(field_occ, dict):
                                for key, value in field_occ.items():
                                    subfield_id = "^{0}".format(key[1]) if key.startswith('_') else ''
                                    # skip subfields with False values. ex. ^g of electronic_address
                                    if isinstance(value, bool) and value is False:
                                        continue
                                    # skip empty attributes
                                    if not value:
                                        continue

                                    if not isinstance(value, str):
                                        value = str(value)

                                    subfield = u''.join((subfield_id, value)).strip()
                                    field_value = ''.join((field_value, subfield))
                                # format out line in ID format
                                id_field = self.id_field(field_name, field_value)
                                record_lines.append(id_field)
                            else:
                                id_field = self.id_field(field_name, field_occ)
                                record_lines.append(id_field)

                    else:
                        # check for fields with multiples lines as occurrences
                        if isinstance(field, str) and "\n" in field:
                            for field_line in field.split('\n'):
                                id_field = self.id_field(field_name, field_line)
                                record_lines.append(id_field)
                        else:
                            id_field = self.id_field(field_name, field)
                            record_lines.append(id_field)

            # add control fields
            export_control_1 = self.id_field('export_control_1', 'FI-ADMIN^i%s^bLILACS' % item['id'])
            record_lines.append(export_control_1)
            if item.get('LILACS_original_id'):
                export_control_2 = self.id_field('export_control_2', item['LILACS_original_id'])
                record_lines.append(export_control_2)

            # add lines of record at id export list
            id_lines.extend(record_lines)
            id_lines.append("\n")

        return ''.join(id_lines)

    def id_field(self, field, value):
        id_field = ''
        field_number = self.field_tag.get(field, None)
        if field_number:
            field_value = str(value)

            id_field = "!v{0:03d}!{1} \n".format(int(field_number), field_value)

        return id_field
