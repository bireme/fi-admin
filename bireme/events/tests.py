# coding: utf-8
from django.test.client import Client
from django.contrib.contenttypes.models import ContentType

from utils.models import Country
from main.models import ThematicArea, Descriptor, Keyword, ResourceThematic

from utils.tests import BaseTestCase
from events.models import *

def minimal_form_data():
    """
    Define a minimal fields for submit a form
    """

    form_data = {
        'status': '0',
        'title': 'Evento de teste',
        'event_type': 1,

        'main-descriptor-content_type-object_id-TOTAL_FORMS': '0',
        'main-descriptor-content_type-object_id-INITIAL_FORMS': '0',

        'main-keyword-content_type-object_id-TOTAL_FORMS': '0',
        'main-keyword-content_type-object_id-INITIAL_FORMS': '0',

        'main-resourcethematic-content_type-object_id-TOTAL_FORMS': '0',
        'main-resourcethematic-content_type-object_id-INITIAL_FORMS': '0',
    }

    return form_data

def complete_form_data():
    """
    Define missing fields for a valid submission form
    """

    missing_fields = {
        'start_date' : '01/01/2014',
        'end_date'  : '01/05/2014',

        'main-descriptor-content_type-object_id-TOTAL_FORMS' : '1',

        'main-descriptor-content_type-object_id-0-id' : '',
        'main-descriptor-content_type-object_id-0-text' : 'malaria',
        'main-descriptor-content_type-object_id-0-code' : '^d8462',
        'main-descriptor-content_type-object_id-0-status' : '0',

        'main-resourcethematic-content_type-object_id-TOTAL_FORMS' : '1',
        'main-resourcethematic-content_type-object_id-0-thematic_area' : '1',
        'main-resourcethematic-content_type-object_id-0-status' : '0',
    }

    complete_form_data = minimal_form_data()
    complete_form_data.update(missing_fields)

    return complete_form_data


def create_test_objects():
    """
    Create objects for tests
    """

    # Create two objects of different users and same center code
    event_1 = Event.objects.create(status=0, title='Evento de teste (BR1.1)',
                            start_date='2014-01-01', end_date='2014-01-05',
                            created_by_id=1, cooperative_center_code='BR1.1')

    Event.objects.create(status=0, title='Evento de teste (BR1.1)',
                            start_date='2014-01-01', end_date='2014-01-05',
                            created_by_id=2, cooperative_center_code='BR1.1')

    # Create one object of diffent center code
    Event.objects.create(status=0, title='Evento de teste (PY3.1)',
                            start_date='2014-01-01', end_date='2014-01-05',
                            created_by_id=3, cooperative_center_code='PY3.1')


    # add descriptor and thematic area for event_1
    object_ct = ContentType.objects.get_for_model(Event)
    descriptor = Descriptor.objects.create(object_id=1, content_type=object_ct, text='descritor 1')
    keyword = Keyword.objects.create(object_id=1, content_type=object_ct, text='keyword 1')
    thematic = ResourceThematic.objects.create(object_id=1, content_type=object_ct, thematic_area_id=1)


class EventTest(BaseTestCase):
    """
    Tests for event app
    """
    def setUp(self):
        super(EventTest, self).setUp()

        # create auxiliary models used on tests
        EventType.objects.create(acronym='congress', name='Congresso')
        Country.objects.create(code='BR', name='Brasil')
        ThematicArea.objects.create(acronym='LISBR1.1', name='Enfermagem')


    def test_list_event(self):
        """
        Test list view
        """
        self.login_editor()
        create_test_objects()

        # check for default list (list events of current user = 1)
        response = self.client.get('/events/')
        self.assertContains(response, "Evento de teste (BR1.1)")
        self.assertEquals(response.context['events'].count(), 1)

        # default list don't show events from other users
        self.assertNotContains(response, "Evento de teste (PY3.1)")

        # check for list of all events
        response = self.client.get('/events/?filter_owner=*')
        total_of_events = Event.objects.all().count()
        self.assertEquals(response.context['events'].count(), total_of_events)

    def test_add_event(self):
        """
        Test create view
        """
        self.login_editor()

        # invalid submission with missing required fields
        form_data = minimal_form_data()
        response = self.client.post('/event/new', form_data )

        self.assertContains(response,'Por favor verifique os campos obrigatórios')
        self.assertContains(response,'Você precisa inserir pelo menos um descritor de assunto')
        self.assertContains(response,'Você precisa selecionar pelo menos uma área temática')

        # complete form_data with required fields and re-submit form
        form_data = complete_form_data()

        # test valid submission
        # after submit a valid content the view will redirect to /events and list the objects
        # follow=True will allow check if the new data is on the list
        response = self.client.post('/event/new', form_data, follow=True)

        self.assertRedirects(response, '/events')
        self.assertContains(response, "Evento de teste")

        # check if is set cooperative center code of user (editor = BR1.1)
        self.assertEquals(Event.objects.all()[0].cooperative_center_code, "BR1.1")


    def test_edit_event(self):
        """
        Test edit view
        """
        self.login_editor()
        create_test_objects()

        event_test = Event.objects.all()[0]
        url = '/event/edit/{0}'.format(event_test.id)
        response = self.client.get(url)

        # Test if return form with fields
        self.assertContains(response, event_test.title)

        # Test changes values and submit
        form_data = complete_form_data()

        response = self.client.post(url, form_data, follow=True)
        self.assertRedirects(response, '/events')
        self.assertContains(response, "Evento de teste")

    def test_delete_event(self):
        """
        Tests delete event
        """
        self.login_editor()
        create_test_objects()

        form_data = {'delete_id': '1'}

        response = self.client.post('/events', form_data, follow=True)
        self.assertTrue(Event.objects.filter(id=1).count() == 0)


        # check delete of related objects (descriptors, thematic_area, keywords)
        object_ct = ContentType.objects.get_for_model(Event)

        self.assertTrue(Descriptor.objects.filter(object_id=1, content_type=object_ct).count() == 0)
        self.assertTrue(Keyword.objects.filter(object_id=1, content_type=object_ct).count() == 0)
        self.assertTrue(ResourceThematic.objects.filter(object_id=1, content_type=object_ct).count() == 0)


    def test_event_type(self):
        """
        Test list event type
        """

        # check if documentalist has access to list view
        self.login_documentalist()
        response = self.client.get('/event-types/' )

        # 403 = unauthorized
        self.assertEqual(response.status_code, 403)

        self.client.logout()
        self.login_admin()

        response = self.client.get('/event-types/')
        self.assertContains(response, "Congresso")


    def test_add_event_type(self):
        """
        Test create event type
        """
        # check if documentalist has access to create form
        self.login_documentalist()
        response = self.client.get('/event-type/new' )

        # 403 = unauthorized
        self.assertEqual(response.status_code, 403)

        self.client.logout()
        self.login_admin()

        form_data = {
            'status': '0',
            'acronym': 'course',
            'name': 'Curso',
            'language' : 'pt-br',
            'eventtypelocal_set-TOTAL_FORMS': '0',
            'eventtypelocal_set-INITIAL_FORMS': '0',
        }

        response = self.client.post('/event-type/new', form_data, follow=True )

        self.assertRedirects(response, '/event-types')
        self.assertContains(response, "Curso")
