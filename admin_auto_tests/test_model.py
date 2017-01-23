from unittest import SkipTest

from autofixture import AutoFixture
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.forms import model_to_dict
from django.test import TestCase

from admin_auto_tests.utils import test_base_class


class AdminTestMixIn(object):
    field_values = None
    model = None

    def create(self, commit=True, model=None, follow_fk=True, generate_fk=True, field_values=None):
        model = model or self.model
        field_values = field_values or self.field_values
        instance = AutoFixture(model, follow_fk=follow_fk, generate_fk=generate_fk,
                               field_values=field_values).create_one(commit)
        return instance

    def create_user(self, is_staff=False, is_superuser=False, is_active=True):
        return self.create(model=get_user_model(), field_values=dict(
            is_staff=is_staff, is_superuser=is_superuser, is_active=is_active
        ))

    def setUp(self):
        super(AdminTestMixIn, self).setUp()
        self.client.force_login(self.create_user(is_staff=True, is_superuser=True))


class ModelAdminTestMixIn(AdminTestMixIn):
    add_status_code = 200
    changelist_status_code = 200
    change_status_code = 200
    delete_status_code = 200
    form_data_exclude_fields = ()
    form_data_update = {}
    skip_add = False
    skip_create = False
    skip_change = False
    skip_delete = False

    def get_form_data_update(self):
        return dict(self.form_data_update)

    def get_add_url(self):
        return reverse('admin:{model._meta.app_label}_{model._meta.model_name}_add'.format(model=self.model))

    def get_changelist_url(self):
        return reverse('admin:{model._meta.app_label}_{model._meta.model_name}_changelist'.format(model=self.model))

    def get_change_url(self, instance=None):
        instance = instance or self.create()
        return reverse('admin:{model._meta.app_label}_{model._meta.model_name}_change'.format(model=self.model),
                        args=(instance.pk,))

    def get_delete_url(self, instance=None):
        instance = instance or self.create()
        return  reverse('admin:{model._meta.app_label}_{model._meta.model_name}_delete'.format(model=self.model),
                      args=(instance.pk,))

    def create_instance_data(self):
        instance = self.create(False)
        return {x: y for x, y in filter(lambda x: x[1], model_to_dict(instance).items())
                if not x in self.form_data_exclude_fields}

    def create_form_instance_data(self, response, instance_data=None):
        fields = {key: value.initial for key, value in
                  response.context_data['adminform'].form.fields.items() if value.initial is not None}
        for formset in response.context_data['inline_admin_formsets']:
            formset = list(formset)[0].formset
            for field in formset.forms[0].visible_fields() + formset.empty_form.visible_fields():
                if field.value() is not None:
                    fields[field.html_name] = field.value()
                # fields[field.html_name] = field.value() if field.value() is not None else ''
            for key, value in formset.management_form.initial.items():
                fields['{}-{}'.format(formset.prefix, key)] = value
        fields.update(instance_data or self.create_instance_data())
        return fields

    def test_changelist_view(self):
        response = self.client.get(self.get_changelist_url())
        self.assertEqual(response.status_code, self.changelist_status_code)

    def test_add_view(self):
        if self.add_status_code != 200 or self.skip_add:
            raise SkipTest('Required status code != 200' if self.add_status_code != 200 else 'Skip add is enabled')
        response = self.client.get(self.get_add_url())
        self.assertEqual(response.status_code, self.add_status_code)

    def test_add(self):
        if self.add_status_code != 200 or self.skip_add:
            raise SkipTest('Required status code != 200' if self.add_status_code != 200 else 'Skip add is enabled')
        response = self.client.get(self.get_add_url())
        instance_data = self.create_instance_data()
        data = self.create_form_instance_data(response, instance_data)
        data['_continue'] = ''
        data.update(self.get_form_data_update())
        print(data)
        response = self.client.post(self.get_add_url(), data, follow=True)
        self.assertEqual(response.status_code, self.add_status_code)
        if response.context_data.get('errors'):
            self.assertEqual(len(response.context_data['errors']), 0,
                             ' * '.join(['{}: {}'.format(x, ', '.join(y))
                                         for x, y in response.context_data['adminform'].form.errors.items()]))
        if 'original' not in response.context_data:
            self.fail('Instance is not created.')

    def test_change_view(self):
        if self.skip_change:
            raise SkipTest('Skip change is enabled')
        response = self.client.get(self.get_change_url())
        self.assertEqual(response.status_code, self.change_status_code)

    def test_change(self):
        if self.change_status_code != 200 or self.skip_change:
            raise SkipTest('Required status code != 200' if self.change_status_code != 200
                           else 'Skip change is enabled')
        instance = self.create()
        response = self.client.get(self.get_change_url(instance))
        new_data = self.create_form_instance_data(response)
        response = self.client.post(self.get_change_url(instance), new_data, follow=True)
        self.assertEqual(response.status_code, self.change_status_code)


    def test_delete_view(self):
        if self.skip_delete:
            raise SkipTest('Skip delete is enabled')
        response = self.client.get(self.get_delete_url())
        self.assertEqual(response.status_code, self.delete_status_code)


class AdminTestCase(AdminTestMixIn, TestCase):
    pass
AdminTestCase = test_base_class(AdminTestCase)


class ModelAdminTestCase(ModelAdminTestMixIn, TestCase):
    pass
ModelAdminTestCase = test_base_class(ModelAdminTestCase)