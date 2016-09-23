from django.core.mail import send_mail
from django.views.generic import FormView
import ctypes  # Library for notifications
from untitled.forms import ContactForm
import mysql.connector   # https://github.com/sanpingz/mysql-connector
from mysql.connector import errorcode   # could not install any other mysql driver
import datetime
from django.http import HttpResponse
# When SessionMiddleware is activated, each HttpRequest object –
# the first argument to any Django view function – will have a session attribute, which is a dictionary-like object.
from django.template.loader import render_to_string

# source http://www.pydanny.com/simple-django-email-form-using-cbv.html


class ContactFormView(FormView):

    form_class = ContactForm
    template_name = "email_form.html"
    success_url = '/result/'

    def form_valid(self, form):

        # message = "{name} / {email} said: ".format(
        #    name=form.cleaned_data.get('name'),
        #    email=form.cleaned_data.get('email'))
        # message += "\n\n{0}".format(form.cleaned_data.get('message'))

        # below I'm just replacing send_mail with my custom functions

        # https://dev.mysql.com/doc/connector-python/en/connector-python-connectargs.html
        # MySQL server connection parameters
        config = {
            'user': 'sql7136992',
            'password': '1wWTvGL5H8',
            'host': 'sql7.freesqldatabase.com',
            'port': '3306',
            'database': 'sql7136992'
        }

        # connecting
        cnx = cur = None
        try:
            cnx = mysql.connector.connect(**config)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                # sending information to the second form
                # http://stackoverflow.com/questions/9899113/get-request-session-from-a-class-based-generic-view
                self.request.session['result'] = "ACCESS DENIED: {}".format(err)
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                # sending information to the second form
                self.request.session['result'] = "BAD_DB_ERROR: {}".format(err)
            else:
                self.request.session['result'] = "Error: {}".format(err)
        else:
            cur = cnx.cursor()

            # Sending our data to database
            # https://dev.mysql.com/doc/connector-python/en/connector-python-example-cursor-transaction.html
            query = ("INSERT INTO table1 (Date, Name, email, department, subject, message)"
                     " VALUES(%(Date)s, %(Name)s, %(email)s, %(department)s, %(subject)s, %(message)s)"
                     )

            query_data = {
                'Date': datetime.datetime.now(),
                'Name': form.cleaned_data.get('name'),
                'email': form.cleaned_data.get('email'),
                'department': form.cleaned_data.get('department'),
                'subject': form.cleaned_data.get('subject'),
                'message': form.cleaned_data.get('message')
            }

            cur.execute(query, query_data)

            # Make sure data is committed to the database
            cnx.commit()

            # http://stackoverflow.com/questions/9899113/get-request-session-from-a-class-based-generic-view
            # sending information to the second form
            self.request.session['result'] = 'Message submitted! Thank you.'

        finally:
            if cur:
                cur.close()
            if cnx:
                cnx.close()

        # send_mail(
        #    subject=form.cleaned_data.get('subject').strip(),
        #    message=message,
        #    from_email='contact-form@myapp.com',
        #    # recipient_list=[settings.LIST_OF_EMAIL_RECIPIENTS],
        #    recipient_list=[form.cleaned_data.get('email').strip()],
        # )
        print(self.request.session['result'])

        return super(ContactFormView, self).form_valid(form)

# result page


def result(request):

    # getting information:
    if 'result' in request.session:
        res = HttpResponse(render_to_string('main.html', {"title": "Result", "pic": "/media/db.png"}))
        res.write("<div style='position: relative;float:left'><h2>Result: %s </h2></div>" % request.session['result'])
        return res
    else:
        return HttpResponse(render_to_string('main.html', {"title": "This should be called from ContactFormView", "pic": "/media/db.png"}))


def printform(response):

    # wrapping HttpResponse in our main template
    res = HttpResponse(render_to_string('main.html', {"title": "Inbox", "pic": "/media/email.ico"}))

    # https://dev.mysql.com/doc/connector-python/en/connector-python-connectargs.html
    # MySQL server connection parameters
    config = {
        'user': 'sql7136992',
        'password': '1wWTvGL5H8',
        'host': 'sql7.freesqldatabase.com',
        'port': '3306',
        'database': 'sql7136992'
    }

    # connecting
    cnx = cur = None
    try:
        cnx = mysql.connector.connect(**config)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            res.write("<div style='position: relative;float:left'>ACCESS DENIED: {}</div>".format(err))
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            res.write("<div style='position: relative;float:left'>BAD_DB_ERROR: {}</div>".format(err))
        else:
            res.write(err)
    else:
        cur = cnx.cursor()

        # res.write('<h1>Inbox:</h1><br>')

        # https://dev.mysql.com/doc/connector-python/en/connector-python-example-cursor-select.html

        # fetching database records, sorting in descending order
        query = ("SELECT Date, Name, email, department, subject, message FROM table1 ORDER BY Date DESC"
             )
        cur.execute(query)

        # printing database
        for (Date, Name, email, department, subject, message) in cur:
             res.write("<table><tr><td style='text-align:left;width:20%'>Date: &nbsp;</td><td style='text-align:left'> {}</td></tr>"
                  "<tr><td style='text-align:left;width:20%;'>Name: &nbsp;</td><td style='text-align:left;font-weight:bold'> {}</td></tr>"
                  "<tr><td style='text-align:left;width:20%'>Email: &nbsp;</td><td style='text-align:left'> {}</td></tr>"
                  "<tr><td style='text-align:left;width:20%'>Department: &nbsp;</td><td style='text-align:left'> {}</td></tr>"
                  "<tr><td style='text-align:left;width:20%;'>Subject: &nbsp;</td><td style='text-align:left;font-weight:bold'> {}</td></tr>"
                  "</table><table>"
                  "<tr><td style='text-align:left;width:100%'>Message:</td></tr><tr>"
                  "<td style='text-align:left;width:100%'>{}</tr></td></table><hr><br>".format(Date, Name, email, department, subject, message))

    return res

