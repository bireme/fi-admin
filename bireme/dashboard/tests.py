#-*- coding: utf-8 -*-
import requests_mock
from django.contrib.auth import get_user_model
from requests.exceptions import ConnectionError

from utils.tests import BaseTestCase

User = get_user_model()


class DashboardGet(BaseTestCase):
    def setUp(self):
        super(DashboardGet, self).setUp()

        self.login_editor()

        with requests_mock.mock() as m:
            m.get(requests_mock.ANY, status_code=200)
            self.resp = self.client.get("/")

    def test_get(self):
        self.assertEqual(self.resp.status_code, 200)

    def test_template(self):
        self.assertTemplateUsed(self.resp, "dashboard/index.html")

    def test_alert_dedup_unavailable_br11(self):
        self.assertNotContains(self.resp, "O serviço DeDup está indisponível!")

        with requests_mock.mock() as m:
            m.get(requests_mock.ANY, status_code=500)
            resp = self.client.get("/")
            self.assertContains(resp, "O serviço DeDup está indisponível!")

        with requests_mock.mock() as m:
            m.get(requests_mock.ANY, exc=ConnectionError)
            resp = self.client.get("/")
            self.assertContains(resp, "O serviço DeDup está indisponível!")

    def test_alert_dedup_unavailable_not_br11(self):
        for user in User.objects.all():
            user.delete()

        self.login_editor_llxp()

        with requests_mock.mock() as m:
            m.get(requests_mock.ANY, status_code=500)
            response = self.client.get("/")
            self.assertNotContains(response, "O serviço DeDup está indisponível!")

        with requests_mock.mock() as m:
            m.get(requests_mock.ANY, status_code=200)
            response = self.client.get("/")
            self.assertNotContains(response, "O serviço DeDup está indisponível!")
