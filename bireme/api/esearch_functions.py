# funciones para la busqueda en ElasticSearch y para parsear expresion bool

from elasticsearch_dsl import Q, Search
from pyparsing import *
# from django.shortcuts import render
from django.http import Http404

def get_search_q(op_prefix, text, op=None, status=None, lang_code=None, ths=None):
	"""
	Funcion que a partir de la opcion o prefijo y el texto devuelve en que indices de ElasticSearch buscar y la expresion de
	busqueda correspondiente, expresada con la funcion Q().

	:param op_prefix: 'tree_id' para opcion tree_id
										'words' para opcion words
										 prefijo (de opcion bool) con el que se especifica el indice donde realizar la busqueda.
								     prefijos validos: 101-107 y 401-407,
	:param text: Texto a buscar
	:param op: Por defecto None, utilizado para chequear operaciones de AND NOT, cualquier otro valor se ignora
							Si op='AND NOT' utiliza la condicion must_not, en caso contrario utiliza must.
	:param status: estado del termino, 1 si esta activo, por defecto None
	:param lang_code: Idioma del texto a buscar, por defecto None
	:param ths: Thesauro en el que buscar, por defecto None
	:return: Diccionario con llaves ('index', 'query'), cuyos valores son los 'indices' donde realizar la busqueda,
					'query' a ejecutar expresada con la funcion Q(). En correspondencia con operacion o prefijo y texto de entrada.
					En caso de prefijos 105, 106, 405, 407 que involucran los 3 indices y tienen condiciones de termino autorizado
					o sinonimo. Se devuelven prefijo para consulta en indices 'descriptor_term', 'qualifier_term' y
					prefijo para consulta en 'previous_term'. Por ej: search_q['105'] = ['101', '104']

	Example::

	"""
	search_q = {}

	# filtros
	if lang_code == None and ths == None:
		#cdo se genera un solo query filter_gral (status, language_code, term_thesaurus) no se aplica en cada parte, sino al query unico
		filter_gral = []
	else:
		filter_gral = [Q('term', status=status), Q('term', language_code=lang_code), Q('term', term_thesaurus=ths)]

	filter_preferred = filter_gral + [Q('term', record_preferred_term='Y')]
	filter_synonym = filter_gral + [Q('term', record_preferred_term='N')]

	# condiciones de busqueda must para op_prefix 1## y op_prefix 4##
	if op_prefix[0] == '1':
		# texto completo
		must = [Q('match', term_string__full_field=text)]
	elif op_prefix[0] == '4':
		# palabra a palabra
		if len(text.split()) == 1:
			# si una sola palabra
			must = [Q('match', term_string={"query": text, "analyzer": "keyword_asciifolding"})]
		else:
			# en los 4** si text tiene mas de una palabra devolver None, esta indexado palabra a palabra
			must = [Q('match_none')]
	elif op_prefix == 'words':
		return dict(index=['descriptor_term', 'qualifier_term', 'previous_term'],
		            query=Q('bool', must=[Q('match', term_string={"query": text,"operator": "AND"})], filter=filter_gral)
		            )
	elif op_prefix == 'tree_id':
		return dict(index=['descriptor_treenumber', 'qualifier_treenumber'],
		            query=Q('bool', filter=[Q('term', tree_number=text), Q('match', identifier__thesaurus_id=ths)])
		            )
	else:
		# prefijo no valido
		return dict(index=['descriptor_term'],
		            query=Q('match_none'))

	# must_4_1 = [Q('match', term_string={"query": text, "operator": "AND"})]

	if op_prefix in ['101', '102', '103', '401', '402', '403']:
		# terminos preferidos o sinonimos
		search_q[op_prefix] = {'index': ['descriptor_term', 'qualifier_term']}
	elif op_prefix in ['104', '404']:
		# terminos historicos
		search_q[op_prefix] = {'index': ['previous_term']}
	elif op_prefix in ['107', '407']:
		# terminos preferidos, sinonimos o historicos
		search_q[op_prefix] = {'index': ['descriptor_term', 'qualifier_term', 'previous_term']}
	else:
		# preferidos o historicos, sinonimos o historicos (105, 106, 405, 406)
		search_q[op_prefix] = {'index': ['descriptor_term', 'qualifier_term', 'previous_term'],
		                    'filter_gral': False}

	if op_prefix in ['101', '401']:
		# 101 - campo entero, término autorizado
		# 401 - palabra a palabra, término autorizado
		search_q[op_prefix]['query'] = Q('bool', must=must, filter=filter_preferred)
	elif op_prefix in ['102', '402']:
		# 102 - campo entero, términos sinónimos
		# 402 - palabra a palabra, términos sinónimos
		search_q[op_prefix]['query'] = Q('bool', must=must, filter=filter_synonym)
	elif op_prefix in ['103', '403', '104', '404', '107', '407']:
		# 103 - campo entero, término autorizado y términos sinónimos
		# 403 - palabra a palabra, término autorizado y términos sinónimos
		# 104 - campo entero, términos históricos
		# 404 - palabra a palabra, términos históricos
		# 107 - campo entero, término autorizado, términos sinónimos y términos históricos
		# 407 - palabra a palabra, término autorizado, términos sinónimos y términos históricos
		search_q[op_prefix]['query'] = Q('bool', must=must, filter=filter_gral)
	else:
		# 105 - campo entero, término autorizado y términos históricos
		search_q['105'] = ['101', '104']

		# 106 - campo entero, término sinoimo y términos históricos
		search_q['106'] = ['102', '104']

		# 405 - palabra a palabra, término autorizado y términos históricos
		search_q['405'] = ['401', '404']

		# 406 - palabra a palabra, término sinoimo y términos históricos
		search_q['406'] = ['402', '404']

	return search_q[op_prefix]


def execute_simple_search(simple_search):
	"""
	Ejecuta una busqueda en ElasticSearch y devuelve los terminos encontrados en diferentes indices.
	Se utiliza en opcion words y tree_id

	:param simple_search: diccionario con llaves 'index', 'query'; Indices donde buscar y consulta a ejecutar expresada con Q().
												Resultado de la funcion get_search_q
	:return: listado de terminos que satisfacen la busqueda, como diccionario con llaves {'identifier', 'term_type'},
					'identifier': id del descriptor o calificador, 'term_type': tipo de termino: descriptor o calificador,
	"""
	result = []

	s = Search(index=simple_search['index']).query(simple_search['query'])
	s.execute()

	for hit in s.scan():
		if hit.meta.index == 'descriptor_term':
			item = {'identifier': hit.identifier_concept.identifier.pk,
			        'term_type': 'descriptor',
			        }
		elif hit.meta.index == 'qualifier_term':
			item = {'identifier': hit.identifier_concept.identifier.pk,
			        'term_type': 'qualifier',
			        }
		elif hit.meta.index == 'previous_term':
			item = {'identifier': hit.identifier_id,
			        'term_type': 'descriptor',
			        }
		elif hit.meta.index == 'descriptor_treenumber':
			item = {'identifier': hit.identifier.pk,
			        'term_type': 'descriptor',
			        }
		elif hit.meta.index == 'qualifier_treenumber':
			item = {'identifier': hit.identifier.pk,
			        'term_type': 'qualifier',
			        }

		if item not in result:
			result.append(item)

	return result

def complex_search(list_in, status, lang_code, ths, last_op=None):
	"""
	Funcion recursiva que ejecuta la busqueda a partir de una lista de condiciones booleanas anidadas

	:param list_in: Lista de condiciones booleanas
	:param last_op: Operador booleano que enlaza las condiciones. Valores validos: AND, OR, AND NOT, None en caso de una
									condicion de busqueda sencilla sin operadores booleanos
	:return: listado de terminos obtenidos como resultado de la busqueda, como diccionario con llaves {'identifier', 'term_type'},
					'identifier': id del descriptor o calificador, 'term_type': tipo de termino, descriptor o calificador
	"""
	len_in = len(list_in)
	type_in = type(list_in)
	r_querys = []
	result = []

	if len_in == 1:
		if type_in == list:
			search_q = get_search_q('407', list_in[0], last_op, status, lang_code, ths)
			result = execute_simple_search(search_q)
	elif len_in == 2:
		if type_in == list:
			search_q = get_search_q(list_in[0], list_in[1], last_op, status, lang_code, ths)
			if list_in[0] in ['105', '106', '405', '406']:
				# los 3 indices con condiciones de autorizado o sinonimos, llevan search independientes
				elem = [[search_q[0], list_in[1]], 'OR', [search_q[1], list_in[1]]]
				result = complex_search(elem, status, lang_code, ths)
			else:
				result = execute_simple_search(search_q)
	elif len_in >= 3:
		if type_in == list:
			op = list_in[1]
			# if list_in[1] != 'AND' and list_in[1] != 'OR' and list_in[1] != "AND NOT":
			if op not in ['AND', 'OR', "AND NOT"]:
				return result

			for elem in list_in:
				if type(elem) == list:
					# r_querys.append(complex_search(elem, lang_code, ths, list_in[1]))
					r_querys.append(complex_search(elem, status, lang_code, ths, op))

			# if list_in[1] == 'AND NOT' or list_in[1] == 'AND':
			#if op in ['AND', 'AND NOT']:
			if op == 'AND':
				# intersect arrays (intersect)
				count_querys = len(r_querys)
				for i in range(count_querys-1):
					i_querys = [x for x in r_querys[i] if x in r_querys[i+1]]
					r_querys[i + 1] = i_querys

				result = r_querys[i + 1]

			elif op == 'AND NOT':
				# difference of arrays (difference)
				count_querys = len(r_querys)
				for i in range(count_querys - 1):
					i_querys = [x for x in r_querys[i] if x not in r_querys[i + 1]]
					r_querys[i + 1] = i_querys

				result = r_querys[i + 1]

			else:
				# merge arrays (union)
				count_querys = len(r_querys)
				u_querys = r_querys[0]
				for i in range(1, count_querys):
					for x in r_querys[i]:
						if x not in u_querys:
							u_querys.append(x)

				result = u_querys

	return result

def f_parse(query_string):
	"""
	Funcion para parsear una expresion booleana, donde:
	 - los términos son conectados por operadores booleanos AND, OR y AND NOT .
	 - Se puede especificar en que índice se hará la búsqueda, mediante el uso de prefijos

	:param query_string: Expresion booleana. Admite caracteres latin1. Reconoce expresiones anidadas.
											 En la expresion no se reconocen parentesis para agrupar pq los terminos pueden contenerlos
	:return: Condiciones de la expresion booleana expresadas como listas (array of arrays)

	Example::
		query_string: '401 Supply OR (401 Rural AND 401 Water)'
		return: [['401', 'Supply'], 'OR', [['401', 'Rural'], 'AND', ['401', 'Water']]]
		query_string: '(401 Supply AND NOT 401 Water) AND 401 Rural'
		return: [[['401', 'Supply'], 'AND NOT', ['401', 'Water']], 'AND', ['401', 'Rural']]
		query_string: '101 Abdomen, Acute AND 103 Acute Abdomen'
		return: [['101', 'Abdomen, Acute'], 'AND', ['103', 'Acute Abdomen']]
	"""
	# ParserElement.enablePackrat()

	prefix = oneOf("101 102 103 104 105 106 107 401 402 403 404 405 406 407")
	intl_printables = pyparsing_unicode.Latin1.printables
	word = Word(intl_printables, excludeChars=['(', ')'])
	# word = Word(intl_printables)
	search_text = OneOrMore(word, stopOn=oneOf("AND OR")).setName("search_text")
	words = Combine(search_text("search_text"), adjacent=False, joinString=" ")
	prefix_text = prefix + words
	content = OneOrMore(prefix_text | words)
	expr = operatorPrecedence(Group(content), [('AND NOT', 2, opAssoc.RIGHT,),
	                                           ('AND', 2, opAssoc.LEFT,),
	                                           ('OR', 2, opAssoc.LEFT,)])
	try:
		result = expr.parseString(query_string, parseAll=True)[0]
	except ParseException:
		# Error analizando la expresion bool
		raise Http404("Error parsing bool expresion.")
	else:
		result_list = result.asList()
		return result_list
