import os
import tempfile
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .forms import ICDForm
from .models import ICDModel

User = get_user_model()

VALID_PAYLOAD = {
    "category_code": "Z99",
    "diagnosis_code": "1",
    "full_code": "Z991",
    "abbreviated_description": "Test short",
    "full_description": "Test long description",
    "category_title": "Test category",
}


def make_icd(n, **overrides):
    data = {
        "category_code": f"A{n:02d}",
        "diagnosis_code": str(n),
        "full_code": f"A{n:02d}{n}",
        "abbreviated_description": f"short {n}",
        "full_description": f"Long description number {n}",
        "category_title": f"Category {n}",
    }
    data.update(overrides)
    return ICDModel.objects.create(**data)


class BaseAPITestCase(TestCase):
    def setUp(self):
        cache.clear()  # reset throttling counters between tests
        self.client = APIClient()
        self.staff = User.objects.create_user("staff", password="pw", is_staff=True)
        self.normal = User.objects.create_user("normal", password="pw", is_staff=False)


class ModelTests(TestCase):
    def test_str_uses_full_code(self):
        self.assertEqual(str(make_icd(1)), "A011")

    def test_default_ordering_is_by_id(self):
        a, b, c = make_icd(1), make_icd(2), make_icd(3)
        self.assertEqual(list(ICDModel.objects.all()), [a, b, c])


class ReadAPITests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        for n in range(1, 26):
            make_icd(n)

    def test_v1_list_is_paginated_with_envelope(self):
        response = self.client.get(reverse("icd_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 25)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertIsNotNone(response.data["next"])
        self.assertIsNone(response.data["previous"])

    def test_v1_list_second_page_is_stable(self):
        first = self.client.get(reverse("icd_list"), {"page": 1}).data["results"]
        second = self.client.get(reverse("icd_list"), {"page": 2}).data["results"]
        self.assertEqual(first[0]["category_code"], "A01")
        self.assertEqual(second[0]["category_code"], "A11")

    def test_v2_list_page_size_param(self):
        response = self.client.get(reverse("list_icd"), {"page_size": 5})
        self.assertEqual(len(response.data["results"]), 5)
        self.assertEqual(response.data["count"], 25)

    def test_retrieve_v1_and_v2(self):
        icd = ICDModel.objects.first()
        for url in (
            reverse("icd_retrieve", args=[icd.pk]),
            reverse("retrieve_icd", args=[icd.pk]),
        ):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["id"], icd.pk)

    def test_retrieve_missing_returns_404(self):
        self.assertEqual(self.client.get(reverse("icd_retrieve", args=[999999])).status_code, 404)
        self.assertEqual(self.client.get(reverse("retrieve_icd", args=[999999])).status_code, 404)

    def test_search_matches_title_code_and_description(self):
        make_icd(50, category_title="Cholera special")
        for url_name in ("icd_search", "search_icd"):
            response = self.client.get(reverse(url_name), {"query": "cholera"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["count"], 1)
        by_code = self.client.get(reverse("icd_search"), {"query": "a07"})
        self.assertEqual(by_code.data["count"], 1)
        by_description = self.client.get(reverse("icd_search"), {"query": "number 12"})
        self.assertEqual(by_description.data["count"], 1)

    def test_search_without_query_returns_everything(self):
        response = self.client.get(reverse("icd_search"))
        self.assertEqual(response.data["count"], 25)

    def test_list_search_view_is_reachable_and_filters(self):
        response = self.client.get(reverse("lists_icd"), {"query": "Category 7"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        # and it no longer shadows the plain list endpoint
        self.assertEqual(self.client.get(reverse("list_icd")).data["count"], 25)


class CreateAPITests(BaseAPITestCase):
    def test_anonymous_cannot_create(self):
        for url_name in ("icd_list", "list_icd"):
            response = self.client.post(reverse(url_name), VALID_PAYLOAD, format="json")
            self.assertIn(response.status_code, (401, 403))
        self.assertEqual(ICDModel.objects.count(), 0)

    def test_non_staff_cannot_create(self):
        self.client.force_authenticate(self.normal)
        response = self.client.post(reverse("icd_list"), VALID_PAYLOAD, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(ICDModel.objects.count(), 0)

    def test_staff_can_create_v1_and_v2(self):
        self.client.force_authenticate(self.staff)
        r1 = self.client.post(reverse("icd_list"), VALID_PAYLOAD, format="json")
        self.assertEqual(r1.status_code, 201)
        self.assertEqual(r1.data["full_code"], "Z991")
        payload2 = dict(VALID_PAYLOAD, full_code="Z992")
        r2 = self.client.post(reverse("list_icd"), payload2, format="json")
        self.assertEqual(r2.status_code, 201)
        self.assertEqual(ICDModel.objects.count(), 2)

    def test_create_requires_core_fields(self):
        self.client.force_authenticate(self.staff)
        response = self.client.post(reverse("icd_list"), {"category_title": "only a title"}, format="json")
        self.assertEqual(response.status_code, 400)
        for field in ("category_code", "full_code", "full_description"):
            self.assertIn(field, response.data)

    def test_create_rejects_blank_values(self):
        self.client.force_authenticate(self.staff)
        response = self.client.post(reverse("icd_list"), dict(VALID_PAYLOAD, full_code="   "), format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("full_code", response.data)

    def test_create_rejects_duplicate_full_code_case_insensitive(self):
        make_icd(1, full_code="A011")
        self.client.force_authenticate(self.staff)
        response = self.client.post(reverse("icd_list"), dict(VALID_PAYLOAD, full_code="a011"), format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("full_code", response.data)
        self.assertEqual(ICDModel.objects.count(), 1)

    def test_id_cannot_be_set_by_client(self):
        self.client.force_authenticate(self.staff)
        response = self.client.post(reverse("icd_list"), dict(VALID_PAYLOAD, id=12345), format="json")
        self.assertEqual(response.status_code, 201)
        self.assertNotEqual(response.data["id"], 12345)


class DeleteAPITests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.icd = make_icd(1)

    def test_anonymous_cannot_delete(self):
        for url_name in ("icd_retrieve", "retrieve_icd"):
            response = self.client.delete(reverse(url_name, args=[self.icd.pk]))
            self.assertIn(response.status_code, (401, 403))
        self.assertTrue(ICDModel.objects.filter(pk=self.icd.pk).exists())

    def test_non_staff_cannot_delete(self):
        self.client.force_authenticate(self.normal)
        response = self.client.delete(reverse("icd_retrieve", args=[self.icd.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(ICDModel.objects.filter(pk=self.icd.pk).exists())

    def test_staff_can_delete_v1(self):
        self.client.force_authenticate(self.staff)
        response = self.client.delete(reverse("icd_retrieve", args=[self.icd.pk]))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(ICDModel.objects.filter(pk=self.icd.pk).exists())

    def test_staff_can_delete_v2(self):
        self.client.force_authenticate(self.staff)
        response = self.client.delete(reverse("retrieve_icd", args=[self.icd.pk]))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(ICDModel.objects.filter(pk=self.icd.pk).exists())

    def test_delete_missing_returns_404(self):
        self.client.force_authenticate(self.staff)
        self.assertEqual(self.client.delete(reverse("icd_retrieve", args=[999999])).status_code, 404)
        self.assertEqual(self.client.delete(reverse("retrieve_icd", args=[999999])).status_code, 404)


class FormTests(TestCase):
    def test_form_requires_core_fields(self):
        form = ICDForm(data={})
        self.assertFalse(form.is_valid())
        for field in ("category_code", "full_code", "full_description"):
            self.assertIn(field, form.errors)

    def test_form_rejects_duplicate_code(self):
        make_icd(1, full_code="A011")
        form = ICDForm(data=dict(VALID_PAYLOAD, full_code="a011"))
        self.assertFalse(form.is_valid())
        self.assertIn("full_code", form.errors)

    def test_form_saves_valid_data(self):
        form = ICDForm(data=VALID_PAYLOAD)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().full_code, "Z991")


class WebViewTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user("staff", password="pw", is_staff=True)
        self.normal = User.objects.create_user("normal", password="pw", is_staff=False)
        self.icd = make_icd(1)

    def test_index_is_public(self):
        self.assertEqual(self.client.get(reverse("index")).status_code, 200)

    def test_index_filters_by_category_title(self):
        make_icd(2, category_title="Cholera")
        response = self.client.get(reverse("index"), {"category_title": "chol"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual([i.category_title for i in response.context["page_obj"]], ["Cholera"])

    def test_index_shows_add_and_delete_controls_only_to_staff(self):
        add_url = reverse("icd_add")
        delete_url = reverse("icd_delete", args=[self.icd.pk])

        anonymous = self.client.get(reverse("index"))
        self.assertNotContains(anonymous, add_url)
        self.assertNotContains(anonymous, delete_url)

        self.client.force_login(self.normal)
        normal = self.client.get(reverse("index"))
        self.assertNotContains(normal, add_url)
        self.assertNotContains(normal, delete_url)

        self.client.force_login(self.staff)
        staff = self.client.get(reverse("index"))
        self.assertContains(staff, add_url)
        self.assertContains(staff, delete_url)

    def test_success_messages_are_displayed(self):
        self.client.force_login(self.staff)
        added = self.client.post(reverse("icd_add"), VALID_PAYLOAD, follow=True)
        self.assertContains(added, "was added")
        deleted = self.client.post(reverse("icd_delete", args=[self.icd.pk]), follow=True)
        self.assertContains(deleted, "was deleted")

    def test_add_and_delete_pages_use_the_site_layout(self):
        self.client.force_login(self.staff)
        add_page = self.client.get(reverse("icd_add"))
        self.assertContains(add_page, "navbar")  # extends base.html
        delete_page = self.client.get(reverse("icd_delete", args=[self.icd.pk]))
        self.assertContains(delete_page, "navbar")

    def test_add_page_redirects_anonymous_and_non_staff_to_login(self):
        self.assertEqual(self.client.get(reverse("icd_add")).status_code, 302)
        self.client.force_login(self.normal)
        self.assertEqual(self.client.get(reverse("icd_add")).status_code, 302)

    def test_staff_can_open_add_form(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("icd_add"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Save")

    def test_staff_can_add_record(self):
        self.client.force_login(self.staff)
        response = self.client.post(reverse("icd_add"), VALID_PAYLOAD)
        self.assertRedirects(response, reverse("index"))
        self.assertTrue(ICDModel.objects.filter(full_code="Z991").exists())

    def test_invalid_add_shows_errors_and_saves_nothing(self):
        self.client.force_login(self.staff)
        response = self.client.post(reverse("icd_add"), {"category_title": "x"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ICDModel.objects.count(), 1)

    def test_delete_requires_staff(self):
        url = reverse("icd_delete", args=[self.icd.pk])
        self.assertEqual(self.client.post(url).status_code, 302)
        self.client.force_login(self.normal)
        self.assertEqual(self.client.post(url).status_code, 302)
        self.assertTrue(ICDModel.objects.filter(pk=self.icd.pk).exists())

    def test_delete_get_only_asks_for_confirmation(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("icd_delete", args=[self.icd.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ICDModel.objects.filter(pk=self.icd.pk).exists())

    def test_delete_post_removes_record(self):
        self.client.force_login(self.staff)
        response = self.client.post(reverse("icd_delete", args=[self.icd.pk]))
        self.assertRedirects(response, reverse("index"))
        self.assertFalse(ICDModel.objects.filter(pk=self.icd.pk).exists())

    def test_delete_unknown_record_is_404(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.post(reverse("icd_delete", args=[999999])).status_code, 404)


class ImportCommandTests(TestCase):
    CSV = (
        ",category_code,diagnosis_code,full_code,abbreviated_description,full_description,category_title\n"
        "0,A00,0,A000,Short one,Long one,Cholera\n"
        "1,NA,0010,NA0010,,Long two,\n"
    )

    def setUp(self):
        handle = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8")
        handle.write(self.CSV)
        handle.close()
        self.path = handle.name
        self.addCleanup(os.remove, self.path)

    def run_command(self, *extra):
        out = StringIO()
        call_command("import_icd_data", "--path", self.path, *extra, stdout=out)
        return out.getvalue()

    def test_import_into_empty_table(self):
        output = self.run_command()
        self.assertIn("2 rows", output)
        self.assertEqual(ICDModel.objects.count(), 2)

    def test_empty_cells_become_null_and_codes_are_kept_as_text(self):
        self.run_command()
        row = ICDModel.objects.get(full_code="NA0010")
        self.assertEqual(row.category_code, "NA")  # not turned into NaN
        self.assertEqual(row.diagnosis_code, "0010")  # leading zeros preserved
        self.assertIsNone(row.abbreviated_description)
        self.assertIsNone(row.category_title)

    def test_second_run_is_refused_instead_of_duplicating(self):
        self.run_command()
        with self.assertRaises(CommandError):
            self.run_command()
        self.assertEqual(ICDModel.objects.count(), 2)

    def test_replace_restarts_from_scratch(self):
        self.run_command()
        self.run_command("--replace")
        self.assertEqual(ICDModel.objects.count(), 2)

    def test_append_adds_rows(self):
        self.run_command()
        self.run_command("--append")
        self.assertEqual(ICDModel.objects.count(), 4)

    def test_missing_file_gives_clean_error(self):
        with self.assertRaises(CommandError):
            call_command("import_icd_data", "--path", "/no/such/file.csv", stdout=StringIO())