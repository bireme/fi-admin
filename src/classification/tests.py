# coding: utf-8
import json

from django.contrib.contenttypes.models import ContentType

from classification.models import Collection, Relationship
from utils.tests import BaseTestCase


class ClassifyTest(BaseTestCase):
    """
    Tests for the classify view
    """

    def setUp(self):
        super(ClassifyTest, self).setUp()
        self.login_admin()

        self.community = Collection.objects.create(
            name='Test Community', language='en', community_flag=True
        )
        self.collection = Collection.objects.create(
            name='Test Collection', language='en', parent=self.community
        )
        self.collection2 = Collection.objects.create(
            name='Another Collection', language='en', parent=self.community
        )

        self.ctype = ContentType.objects.get_for_model(Collection)
        self.obj_id = 999

    def get_classify_url(self):
        return '/classification/classify/{0}/{1}/'.format(self.ctype.id, self.obj_id)

    def test_classify_get(self):
        """GET request renders template with empty relations and community list"""
        response = self.client.get(self.get_classify_url())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['relation_list']), [])
        self.assertIn(self.community, response.context['community_list'])
        self.assertEqual(response.context['c_type'], str(self.ctype.id))
        self.assertEqual(response.context['object_id'], str(self.obj_id))
        self.assertFalse(response.context['updated'])

    def test_classify_set_relationship(self):
        """POST with set list creates Relationship objects"""
        response = self.client.post(
            self.get_classify_url(),
            {'set': [str(self.collection.id)]},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['updated'])
        self.assertTrue(
            Relationship.objects.filter(
                object_id=self.obj_id,
                content_type=self.ctype,
                collection=self.collection,
            ).exists()
        )
        self.assertIn(self.collection.id, response.context['relation_list_ids'])

    def test_classify_unset_relationship(self):
        """POST with unset list deletes existing Relationships"""
        Relationship.objects.create(
            object_id=self.obj_id,
            content_type=self.ctype,
            collection=self.collection,
        )

        response = self.client.post(
            self.get_classify_url(),
            {'unset': [str(self.collection.id)]},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['updated'])
        self.assertFalse(
            Relationship.objects.filter(
                object_id=self.obj_id,
                content_type=self.ctype,
                collection=self.collection,
            ).exists()
        )

    def test_classify_set_and_unset(self):
        """POST with both set and unset in same request"""
        Relationship.objects.create(
            object_id=self.obj_id,
            content_type=self.ctype,
            collection=self.collection,
        )

        response = self.client.post(
            self.get_classify_url(),
            {
                'set': [str(self.collection2.id)],
                'unset': [str(self.collection.id)],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Relationship.objects.filter(
                object_id=self.obj_id,
                content_type=self.ctype,
                collection=self.collection2,
            ).exists()
        )
        self.assertFalse(
            Relationship.objects.filter(
                object_id=self.obj_id,
                content_type=self.ctype,
                collection=self.collection,
            ).exists()
        )

    def test_classify_set_duplicates(self):
        """POST with duplicate IDs in set list creates only one Relationship"""
        col_id = str(self.collection.id)
        response = self.client.post(
            self.get_classify_url(),
            {'set': [col_id, col_id, col_id]},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Relationship.objects.filter(
                object_id=self.obj_id,
                content_type=self.ctype,
                collection=self.collection,
            ).count(),
            1,
        )

    def test_classify_unset_nonexistent(self):
        """POST with unset for non-existent relationship does not error"""
        response = self.client.post(
            self.get_classify_url(),
            {'unset': [str(self.collection.id)]},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['updated'])

    def test_classify_get_or_create_existing(self):
        """POST set with already-existing relationship does not create duplicate"""
        Relationship.objects.create(
            object_id=self.obj_id,
            content_type=self.ctype,
            collection=self.collection,
        )

        response = self.client.post(
            self.get_classify_url(),
            {'set': [str(self.collection.id)]},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Relationship.objects.filter(
                object_id=self.obj_id,
                content_type=self.ctype,
                collection=self.collection,
            ).count(),
            1,
        )


class GetChildrenListTest(BaseTestCase):
    """
    Tests for the get_children_list view
    """

    def setUp(self):
        super(GetChildrenListTest, self).setUp()
        self.login_admin()

        self.parent = Collection.objects.create(
            name='Parent', language='en', community_flag=True
        )

    def test_get_children_community(self):
        """Returns community-flagged children with type='community'"""
        child = Collection.objects.create(
            name='Community Child', language='en',
            parent=self.parent, community_flag=True,
        )

        response = self.client.get(
            '/classification/get-children-list/{0}/'.format(self.parent.id)
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['type'], 'community')
        self.assertEqual(len(data['list']), 1)
        self.assertEqual(data['list'][0]['value'], child.id)

    def test_get_children_collection(self):
        """Returns non-community children with type='collection' when no community-flagged exist"""
        child = Collection.objects.create(
            name='Regular Child', language='en',
            parent=self.parent, community_flag=False,
        )

        response = self.client.get(
            '/classification/get-children-list/{0}/'.format(self.parent.id)
        )

        data = json.loads(response.content)
        self.assertEqual(data['type'], 'collection')
        self.assertEqual(len(data['list']), 1)
        self.assertEqual(data['list'][0]['value'], child.id)

    def test_get_children_empty(self):
        """Returns empty list and empty type when no children exist"""
        response = self.client.get(
            '/classification/get-children-list/{0}/'.format(self.parent.id)
        )

        data = json.loads(response.content)
        self.assertEqual(data['type'], '')
        self.assertEqual(data['list'], [])

    def test_get_children_sorted(self):
        """Children are returned sorted by name"""
        Collection.objects.create(
            name='Zebra', language='en', parent=self.parent, community_flag=True,
        )
        Collection.objects.create(
            name='Alpha', language='en', parent=self.parent, community_flag=True,
        )
        Collection.objects.create(
            name='Middle', language='en', parent=self.parent, community_flag=True,
        )

        response = self.client.get(
            '/classification/get-children-list/{0}/'.format(self.parent.id)
        )

        data = json.loads(response.content)
        names = [item['name'] for item in data['list']]
        self.assertEqual(names, sorted(names))
