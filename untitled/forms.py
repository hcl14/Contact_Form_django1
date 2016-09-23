from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
import floppyforms as forms
from django.http import HttpResponse

class ContactForm(forms.Form):

    name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    subject = forms.CharField(required=forms.Textarea)

    # http://stackoverflow.com/questions/1694447/how-to-set-an-event-handler-in-a-django-form-input-field
    # https://chriskief.com/2012/12/16/override-django-form-is_valid/
    # http://stackoverflow.com/questions/30424394/django-forms-how-to-override-field-validation
    # overriding field validation


    # Creating drop-down list
    sales = "Sales"
    marketing = "Marketing"
    hr = "Recruitment"
    customer = "customers"
    it = "IT"
    other = "Other/Not Specified"

    dep_choices = {
        (sales, 'Sales'),
        (marketing, 'Marketing'),
        (hr,'Recruitment'),
        (it,'IT'),
        (customer, 'Customers'),
        (other, 'Other/Not Specified')
    }

    # choice field would be tracked
    # http://stackoverflow.com/questions/1694447/how-to-set-an-event-handler-in-a-django-form-input-field
    # http://stackoverflow.com/questions/1355150/django-when-saving-how-can-you-check-if-a-field-has-changed
    # triggering changes inside current contact form instance

    # from experiments I found that 'attrs' below executes pure javascript
    # so I just used javascript to update image
    department = forms.ChoiceField(choices=dep_choices,
        # widget=forms.Select(attrs={'onchange': "alert(this.value)"}))
        widget=forms.Select(attrs={'onchange': 'changepic(this.value)'}))

    # set initial state
    department.initial = {'other', 'Other/Not Specified'}

    # http://stackoverflow.com/questions/16076420/django-dropdownlist-onchange-submission

    message = forms.CharField(widget=forms.Textarea(attrs={'style': 'resize:allow;'}))

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))
        # self.initial['department'] = ... # possible variant here # http://herself.movielady.net/2012/12/15/initial-value-in-djangos-admin-for-a-choice-field/
        super(ContactForm, self).__init__(*args, **kwargs)

