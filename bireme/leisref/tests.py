from django.shortcuts import resolve_url as r
from model_mommy import mommy

from utils.tests import BaseTestCase


class LeisRefFormTest(BaseTestCase):
    def setUp(self):
        self.login_admin()

    def test_help_text_in_creation_form(self):
        mommy.make("Help", source="leisref", field="status", help_text="Help message")

        response = self.client.get(r("create_legislation"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            text="""onclick="$('#help_modal_title')""",
            count=1
        )

    def test_help_text_in_edit_form(self):
        mommy.make("Act", id=1)
        mommy.make("Help", source="leisref", field="denomination", help_text="Help message")
        mommy.make("Help", source="leisref", field="fascicle_number", help_text="Help message")

        response = self.client.get(r("edit_legislation", 1))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            text="""onclick="$('#help_modal_title')""",
            count=2
        )

    def test_no_help_text_on_creation_form_when_there_is_no_help_object(self):
        response = self.client.get(r("create_legislation"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            text="""onclick="$('#help_modal_title')"""
        )

    def test_no_help_text_on_edit_form_when_there_is_no_help_object(self):
        mommy.make("Act", id=1)

        response = self.client.get(r("edit_legislation", 1))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            text="""onclick="$('#help_modal_title')"""
        )
