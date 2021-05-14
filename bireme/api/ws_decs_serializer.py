from tastypie.serializers import Serializer, get_type_string
import datetime

try:
    import defusedxml.lxml as lxml
    from defusedxml.common import DefusedXmlException
    from defusedxml.lxml import parse as parse_xml
    from lxml.etree import Element, tostring, LxmlError, XMLParser
except ImportError:
    lxml = None
from django.core.exceptions import ImproperlyConfigured
from django.utils import six
from django.utils.encoding import force_text, smart_bytes


class WsDecsSerializer(Serializer):
    """
    A class for serialization xml response of decs ws.
    """

    formats = ['json', 'xml']

    content_types = {'json': 'application/json',
                     'xml': 'application/xml'}

    def to_etree(self, data, options=None, name=None, depth=0):
        """
        Given some data, converts that data to an ``etree.Element`` suitable
        for use in the XML output.
        Se eliminan los atributos type y el orden de los atributos.
        Si un object tiene una key='attr' se agrega como atributo al Element y no como nuevos Element
        """
        if isinstance(data, (list, tuple)):
            if name:
                element = Element(name)
            else:
                element = Element('objects')
            for item in data:
                element.append(self.to_etree(item, options, depth=depth+1))
                element[:] = sorted(element, key=lambda x: x.tag)
        elif isinstance(data, dict):
            if depth == 0:
                if name:
                    element = Element(name)
                else:
                    element = Element('decsvmx', date=datetime.datetime.now().__format__('%Y%m%d %H%M%S'),
                                      version="2.0")
            else:
                element = Element(name or 'object')
            for (key, value) in data.items():
                if key == 'attr':
                    for (k_attr, v_attr) in value.items():
                        element.set(k_attr, v_attr)
                else:
                    element.append(self.to_etree(value, options, name=key, depth=depth+1))
                    element[:] = sorted(element, key=lambda x: x.tag)
        else:
            element = Element(name or 'value')
            simple_data = self.to_simple(data, options)
            data_type = get_type_string(simple_data)

            if data_type != 'null':
                if isinstance(simple_data, six.text_type):
                    element.text = simple_data
                else:
                    element.text = force_text(simple_data)

        return element

    def to_xml(self, data, options=None):
        """
        Given some Python data, produces XML output.
        """
        options = options or {}

        if lxml is None:
            raise ImproperlyConfigured("Usage of the XML aspects requires lxml and defusedxml.")

        data = self.to_simple(data, options)

        etree = self.to_etree(data, options)

        # eliminar tag 'response', no hace falta se reasigna en to_etree
        # etree = etree[0]

        # eliminar el tag 'objects', sus hijos se asignan al padre y 'objects' se elimina
        for element in etree.iter('objects'):
            parent = element.getparent()
            for child in element.getchildren():
                # agrega hijo de 'objects' a su parent
                parent.append(child)
            # elimina 'objects' de su parent
            parent.remove(element)

        # list() para q funcione ok cdo son varios resultados
        object_list = list(etree.iter("object"))
        for element in object_list:
            parent = element.getparent()
            for child in element.getchildren():
                for k_attr, v_attr in element.attrib.items():
                    # si 'object' tiene atributos se asignan a sus hijos
                    child.set(k_attr, v_attr)
                # agrega hijo de 'object' a su parent
                parent.append(child)
            # elimina 'object' de su parent
            parent.remove(element)

        query = None
        # eliminar el tag 'query' y asignar como atributo a la raiz (su padre)
        for element in etree.iter('query'):
            parent = element.getparent()
            if not query:
                query = 1
                parent.set(element.tag, element.text)
            parent.remove(element)

        # asignar a 'term_list' atributo 'lang' q esta en su padre y quitar 'lang' del padre
        for element in etree.iter('term_list'):
            parent = element.getparent()
            p_attr = parent.attrib.items()
            for k_attr, v_attr in p_attr:
                element.set(k_attr, v_attr)
                parent.attrib.pop(k_attr)

        return tostring(etree, xml_declaration=True, encoding='utf-8')
