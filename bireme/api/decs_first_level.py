# coding: utf-8

from django.utils import translation
from django.utils.translation import ugettext_lazy as _


def category_translated(category, language):
	with translation.override(language):
		return translation.ugettext(category)


def first_level_list(language):
	tree = []
	for tree_number, category in first_level_categories.items():
		tree.append({'attr': {'tree_id': tree_number}, 'term': category_translated(category, language)})
		tree[:] = sorted(tree, key=lambda k: k['attr']['tree_id'])
	return tree


# DeCS First Level
first_level_categories = {
	'A': _("ANATOMY"),
	'B': _("ORGANISMS"),
	'C': _("DISEASES"),
	'D': _("CHEMICALS AND DRUGS"),
	'E': _("ANALYTICAL, DIAGNOSTIC AND THERAPEUTIC TECHNIQUES, AND EQUIPMENT"),
	'F': _("PSYCHIATRY AND PSYCHOLOGY"),
	'G': _("PHENOMENA AND PROCESSES"),
	'H': _("DISCIPLINES AND OCCUPATIONS"),
	'HP': _("HOMEOPATHY"),
	'I': _("ANTHROPOLOGY, EDUCATION, SOCIOLOGY, AND SOCIAL PHENOMENA"),
	'J': _("ATECHNOLOGY, INDUSTRY, AND AGRICULTURE"),
	'K': _("HUMANITIES"),
	'L': _("INFORMATION SCIENCE"),
	'M': _("NAMED GROUPS"),
	'N': _("HEALTH CARE"),
	'SH': _("SCIENCE AND HEALTH"),
	'SP': _("PUBLIC HEALTH"),
	'V': _("PUBLICATION CHARACTERISTICS"),
	'VS': _("HEALTH SURVEILLANCE"),
	'Z': _("GEOGRAPHICALS"),
}
