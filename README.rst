=======================
django-admin-auto-tests
=======================
Simple and automated coverage for your Django Admin pages.

Create tests to check the correct functioning of your Admin pages. Includes support for:

* Model **List** page is working.
* **Add** page is working and saves a new record.
* **Modify** page is working and saves a existing record.
* **Delete** page is working and removes a existing record.
* Add/Delete/Modify **permissions**.

Using it is as easy as:

.. code-block::python

    class MyModelAdminTestCase(ModelAdminTestCase):
        model = MyModel


That is all! But you can personalize it:

.. code-block::python

    class MyModelAdminTestCase(ModelAdminTestCase):
        # The response code to return. This is useful
        # for when you must return 403 (forbidden)
        add_status_code = 200
        changelist_status_code = 200
        change_status_code = 200
        delete_status_code = 200
        # Fields that should not be created/modified
        # when the form is submitted.
        form_data_exclude_fields = ()
        # Fixed value when submitting the form.
        form_data_update = {}
        # Skip default tests
        skip_add = False
        skip_create = False
        skip_change = False
        skip_delete = False

        model = MyModel

This module uses **django-autofixture** to create the information.
