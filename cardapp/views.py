import io
from pathlib import Path
from django.core.files import File
from django.core.files.storage import default_storage
import qrcode
from datetime import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import SetPasswordForm
from django.urls import reverse_lazy
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import login
from django.contrib import messages
from project_django.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, BASE_DIR
from .forms import NewUserForm
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.template import loader
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail, BadHeaderError, EmailMultiAlternatives
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from .token import account_activation_token
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from .forms import sendForm
from .models import CardData
from email.mime.image import MIMEImage
from vobject import vCard
import base64
from django.contrib.auth import views as auth_views
from qrcode import QRCode, constants
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from smtplib import SMTPDataError
from django.views.generic import FormView
from django.http import Http404, HttpResponse
import os
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from io import BytesIO
from mixpanel import Mixpanel
import tempfile
mp = Mixpanel("36cbd6f0b92d0588b757298c93c7a733")
import boto3
from botocore.exceptions import NoCredentialsError
from tempfile import NamedTemporaryFile
from django.utils.crypto import get_random_string
from storages.backends.s3boto3 import S3Boto3Storage
s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

# Create your views here.

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(
            request, '\nThank you for your email confirmation. Now you can login your account.')
        return redirect('/login')
    else:
        messages.error(request, 'Activation link is invalid!')

    return redirect('/login')


# def register(request):
#     if request.method == "POST":
#         username = request.POST.get('username')
#         email = request.POST.get('email')
#         password = request.POST.get('password1')
#         confirm_password = request.POST.get('password2')

#         # Validate form data
#         if not username or not email or not password or not confirm_password:
#             messages.error(request, 'All fields are required.')
#             return render(request, 'register.html')
#         elif password != confirm_password:
#             messages.error(request, 'Passwords do not match.')
#             return render(request, 'register.html')
#         elif User.objects.filter(username=username).exists():
#             messages.error(request, 'Username is already taken.')
#             return render(request, 'register.html')
#         elif User.objects.filter(email=email).exists():
#             messages.error(request, 'Email address is already registered.')
#             return render(request, 'register.html')
#         else:
#             # Create new user instance
#             user = User.objects.create_user(
#                 username=username,
#                 email=email,
#                 password=password
#             )

#             # Set user as inactive until email confirmation
#             user.is_active = False

#             user.save()
#             mp.people_set(request.user.id, {
#                 '$email': request.user.email,
#                 '$created': '2013-04-01T13:20:00',
#                 '$last_login': datetime.now()
#             })
#             mp.track(request.user.id, 'Signed Up')

#             activateEmail(request, user, email)
#             messages.success(
#                 request, '\nYour account has been created. Please check your email to activate your account.')
#             return redirect('main:login')
#     return render(request, 'register.html')

def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password1')
        confirm_password = request.POST.get('password2')

        # Validate form data
        if not username or not email or not password or not confirm_password:
            messages.error(request, 'All fields are required.')
            return render(request, 'register.html')
        elif password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'register.html')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken.')
            return render(request, 'register.html')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email address is already registered.')
            return render(request, 'register.html')
        else:
            # Create new user instance
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            # Set user as inactive until email confirmation
            user.is_active = False

            user.save()
            if not isinstance(request.user, AnonymousUser):
                mp.people_set(request.user.id, {
                    '$email': request.user.email,
                    '$created': '2013-04-01T13:20:00',
                    '$last_login': datetime.now()
                })
                mp.track(request.user.id, 'Signed Up')

            activateEmail(request, user, email)
            messages.success(
                request, '\nYour account has been created. Please check your email to activate your account.')
            return redirect('main:login')
    return render(request, 'register.html')

def activateEmail(request, user, to_email):
    mail_subject = 'Activate your user account.'
    message = render_to_string('template_activate_account.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(
            request, f'Dear {user}, please go to you email {to_email} inbox and click on received activation link to confirm and complete the registration. Note: Check your spam folder.')
    else:
        messages.error(
            request, f'Problem sending confirmation email to {to_email}, check if you typed it correctly.')


def register_request(request):

    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            # save form in the memory not in database
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account till it is confirmed
            user.save()

            current_site = get_current_site(request)
            subject = 'Activate Your Account'
            message = render_to_string('emails/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            messages.success(request, ('Please Confirm your email to complete registration.'))
            return redirect('login')
        return render(request, 'register.html', {'register_form': form})


# @user_passes_test(lambda u: not u.is_authenticated, login_url='main:form')
# def login_request(request):
#     mp.track(request.user.id, 'Viewed Login Page')
#     if request.method == "POST":
#         username = request.POST['username']
#         password = request.POST['password']
#         remember_me = request.POST.get('remember_me')

#         user = authenticate(request, username=username, password=password)
#         if user is not None:

#             login(request, user)
#             if not remember_me:
#                 request.session.set_expiry(0)
#                 return redirect('main:form')
#             mp.people_set(request.user.id, {
#                 '$name': request.user.get_full_name(),
#                 '$email':request.user.email,
#                 '$last_login': datetime.now()
#             })
#             mp.track(request.user.id, 'Login')
#             messages.success(request, f"You are now logged in as {username}.")
#             return redirect("main:form")
#         else:
#             messages.error(request,"Invalid username or password.")

#     return render(request=request, template_name="login.html")

@never_cache
@user_passes_test(lambda u: not u.is_authenticated, login_url='main:form')
def login_request(request):
    mp.track(request.user.id, 'Viewed Login Page')
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        remember_me = request.POST.get('remember_me')

        user = User.objects.filter(username=username).first()

        if user is not None and not user.is_active:
            messages.error(request, "Your account is not activated. Please activate your account from your email.")
            return redirect("main:form")

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_active:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            mp.people_set(request.user.id, {
                '$name': request.user.get_full_name(),
                '$email': request.user.email,
                '$last_login': datetime.now()
            })
            mp.track(request.user.id, 'Login')
            messages.success(request, f"You are now logged in as {username}.")
            return redirect("main:form")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request=request, template_name="login.html")


@never_cache
def logout_request(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect("main:login")


@login_required
@never_cache
def homepage(request):
    mp.track(request.user.id, 'Viewed HomePage')
    if request.method == 'GET':

        mydata = CardData.objects.filter(username=request.user.username)

       
        print(mydata)
        return render(request=request, template_name='homepage.html', context={'mydata': mydata})
    else:
        return redirect('main:login')

 
# @login_required
# @never_cache
# def addcard(request):
#     mp.track(request.user.id, 'Viewed Add card Page')
#     if request.method == 'POST':
#         # Handle the POST request
#         fullname = request.POST.get('fullname')
#         cardname = request.POST.get('cardname')
#         department = request.POST.get('department')
#         company = request.POST.get('company')
#         phone = request.POST.get('phone')
#         alternatephone = request.POST.get('alternatephone')
#         email = request.POST.get('email')
#         upload = request.FILES.get('upload')

#         my_model_instance = CardData()
#         my_model_instance.fullname = fullname
#         my_model_instance.cardname = cardname
#         my_model_instance.department = department
#         my_model_instance.company = company
#         my_model_instance.phone = phone
#         my_model_instance.alternatephone = alternatephone
#         my_model_instance.email = email
#         my_model_instance.upload = upload

#         if not fullname or not email or not cardname or not department or not company or not phone or not email:
#             messages.error(request, 'Please enter all details!')
#         else:
#             # Check if phone number already exists
#             if CardData.objects.filter(phone=phone).exists():
#                 messages.error(request, 'Phone number already exists!')
#             else:
#                 try:
#                     my_model_instance.full_clean()
#                 except ValidationError as e:
#                     messages.error(request, e.message_dict)
#                 else:
#                     my_model_instance.save()

#                     # url = request.build_absolute_uri(reverse('main:qrcard', args=[my_model_instance.id]))
#                     # qr = QRCode(version=1, error_correction=constants.ERROR_CORRECT_L)
#                     # qr.add_data(url)
#                     # qr.make()
#                     # img = qr.make_image()
#                     # img.save("media/qr_codes/qr_code_{}.png".format(my_model_instance.id))
#                     # my_model_instance.qr_code = "media/qr_codes/qr_code_{}.png".format(my_model_instance.id)
#                     # my_model_instance.save()

#                     messages.success(request, 'Saved Successfully!')
#                     return redirect("main:form")
#         return redirect("main:addcard")
#     else:
#         # Render the form for the GET request

#         return render(request, 'addcard.html')




@login_required
@never_cache
def addcard(request):
    if request.method == 'POST':
    # Handle the POST request
        fullname = request.POST.get('fullname')
        cardname = request.POST.get('cardname')
        department = request.POST.get('department')
        company = request.POST.get('company')
        phone = request.POST.get('phone')
        alternatephone = request.POST.get('alternatephone')
        email = request.POST.get('email')
        upload = request.FILES.get('upload')
        username = request.POST.get('username')

        my_model_instance = CardData()
        my_model_instance.fullname = fullname
        my_model_instance.cardname = cardname
        my_model_instance.department = department
        my_model_instance.company = company
        my_model_instance.phone = phone
        my_model_instance.alternatephone = alternatephone
        my_model_instance.email = email
        my_model_instance.username = username


        if not fullname or not email or not cardname or not department or not company or not phone or not email:
            messages.error(request, 'Please enter all details!')
        else:
            # Check if phone number already exists
            if CardData.objects.filter(phone=phone).exists():
                messages.error(request, 'Phone number already exists!')
            else:
                try:
                    my_model_instance.full_clean()
                except ValidationError as e:
                    messages.error(request, e.message_dict)
                else:
                    if upload:
                        # Save the uploaded file to a temporary file
                        with NamedTemporaryFile(delete=False) as temp_file:
                            for chunk in upload.chunks():
                                temp_file.write(chunk)
                        temp_file_path = temp_file.name

                        # Upload the file to S3
                        folder_name = 'uploads'
                        s3_path = f'{folder_name}/{upload.name}'
                        try:
                            s3.upload_file(temp_file_path, 'quickshare-bucket', s3_path)
                        except NoCredentialsError:
                            messages.error(request, 'Credentials not available')
                        else:
                            print(f"File uploaded to S3: {upload.name}")
                            my_model_instance.upload = upload
                            my_model_instance.upload_url = f'https://quickshare-bucket.s3.amazonaws.com/{s3_path}'

                            # Delete the temporary file
                            os.unlink(temp_file_path)
                    else:
                        # If no image is uploaded, use a default image
                        default_image_path = os.path.join(settings.BASE_DIR, 'cardapp/static/images/sample.png')
                        with open(default_image_path, 'rb') as f:
                            default_image = File(f)
                            default_image_name = 'sample.png'
                            my_model_instance.upload.save(default_image_name, default_image, save=True)
                            my_model_instance.upload_url = default_image_name
                    my_model_instance.save()
                    messages.success(request, 'Saved Successfully!')
                    mp.track(request.user.id, 'Card Added', {
                        'Full Name': fullname,
                        'Card Name': cardname,
                        'Department': department,
                        'Company': company,
                        'Phone': phone,
                        'Email': email
                    })

                    return redirect("main:form")
    return render(request, 'addcard.html')

# def addcard(request):
#     mp.track(request.user.id, 'Viewed Add card Page')
#     if request.method == 'POST':
#         # Handle the POST request
#         fullname = request.POST.get('fullname')
#         cardname = request.POST.get('cardname')
#         department = request.POST.get('department')
#         company = request.POST.get('company')
#         phone = request.POST.get('phone')
#         alternatephone = request.POST.get('alternatephone')
#         email = request.POST.get('email')
#         upload = request.FILES.get('upload')

#         my_model_instance = CardData()
#         my_model_instance.fullname = fullname
#         my_model_instance.cardname = cardname
#         my_model_instance.department = department
#         my_model_instance.company = company
#         my_model_instance.phone = phone
#         my_model_instance.alternatephone = alternatephone
#         my_model_instance.email = email

#         if not fullname or not email or not cardname or not department or not company or not phone or not email:
#             messages.error(request, 'Please enter all details!')
#         else:
#             # Check if phone number already exists
#             if CardData.objects.filter(phone=phone).exists():
#                 messages.error(request, 'Phone number already exists!')
#             else:
#                 try:
#                     my_model_instance.full_clean()
#                 except ValidationError as e:
#                     messages.error(request, e.message_dict)
#                 else:
#                     # Save the uploaded file to a temporary file
#                     with NamedTemporaryFile(delete=False) as temp_file:
#                         for chunk in upload.chunks():
#                             temp_file.write(chunk)
#                     temp_file_path = temp_file.name

#                     # Upload the file to S3
#                     folder_name = 'uploads'
#                     s3_path = f'{folder_name}/{upload.name}'
#                     try:
#                         s3.upload_file(temp_file_path, 'quickshare-bucket', s3_path)
#                     except NoCredentialsError:
#                         messages.error(request, 'Credentials not available')
#                     else:
#                         print(f"File uploaded to S3: {upload.name}")
#                         my_model_instance.upload = upload
#                         my_model_instance.upload_url = f'https://quickshare-bucket.s3.amazonaws.com/{s3_path}'
#                         my_model_instance.save()

#                         # Delete the temporary file
#                         os.unlink(temp_file_path)

#                         messages.success(request, 'Saved Successfully!')
#                         return redirect("main:form")
#         return redirect("main:addcard")
#     else:
#         return render(request, 'addcard.html')



@login_required
@never_cache
def card(request, id):
    mydata = CardData.objects.get(id=id)
    if request.method == 'GET':
        mp.track(request.user.id, 'Viewed Get all card page')
        url = request.build_absolute_uri(
            reverse('main:qrcard', args=[mydata.id]))
        qr = QRCode(version=1, error_correction=constants.ERROR_CORRECT_L)
        qr.add_data(url)
        qr.make()
        img = qr.make_image()
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        img_base64 = base64.b64encode(img_io.getvalue()).decode()
        return render(request=request, template_name='card.html', context={'x': mydata, 'qr_code': img_base64})
    return render(request=request, template_name='card.html', context={'x': mydata})


def qrcard(request, id):
    if request.method == 'GET':
        mp.track(request.user.id, 'Viewed Qr card')
        mydata = CardData.objects.get(id=id)
        print(mydata)
        return render(request=request, template_name='qr_card.html', context={'mydata': mydata})




@login_required
@never_cache
def update(request, id):
    mp.track(request.user.id, 'Update Card Page')
    # Get the existing CardData instance by id
    card_data = CardData.objects.get(id=id)
    print(card_data)
    if request.method == 'POST':
        # Handle the POST request to update the CardData instance
        fullname = request.POST.get('fullname')
        cardname = request.POST.get('cardname')
        department = request.POST.get('department')
        company = request.POST.get('company')
        phone = request.POST.get('phone')
        alternatephone = request.POST.get('alternatephone')
        email = request.POST.get('email')
        upload = request.FILES.get('upload')

        # Update the attributes of the CardData instance
        card_data.fullname = fullname
        card_data.cardname = cardname
        card_data.department = department
        card_data.company = company
        card_data.phone = phone
        card_data.alternatephone = alternatephone
        card_data.email = email

        if upload:
            card_data.upload = upload

        card_data.save()

        # Update the QR code image
        # url = request.build_absolute_uri(reverse('main:qrcard', args=[card_data.id]))
        # qr = QRCode(version=1, error_correction=constants.ERROR_CORRECT_L)
        # qr.add_data(url)
        # qr.make()
        # img = qr.make_image()
        # img.save(f"media/qr_codes/qr_code_{card_data.id}.png")
        # card_data.qr_code = f"media/qr_codes/qr_code_{card_data.id}.png"
        card_data.save()

        messages.success(request, 'Updated Successfully!')
        return redirect("main:form")
    else:
        # Render the form for the GET request to update the CardData instance
        context = {
            'card_data': card_data
        }

        return render(request, 'addcard.html', context)


# def delete(request, id):

#     mydata = CardData.objects.get(id=id)

#     # Delete the image file
#     if mydata.upload:
#         path = os.path.join(settings.MEDIA_ROOT, str(mydata.upload))
#         if os.path.isfile(path):
#             os.remove(path)

#     mydata.delete()

#     return redirect('main:form')
@never_cache
def delete(request, id):
    mydata = CardData.objects.get(id=id)

    # Delete the image file from S3
    if mydata.upload:
        bucket_name = 'quickshare-bucket'
        print(mydata.upload.url)
        s3_key = mydata.upload.url[54:]
        print("key:   --> ",s3_key)
        try:
            s3.delete_object(Bucket=bucket_name, Key=s3_key)
        except Exception as e:
            print("Error", e)

    # Delete the image file from local
    # if mydata.upload:
    #     path = os.path.join(settings.MEDIA_ROOT, str(mydata.upload))
    #     if os.path.isfile(path):
    #         os.remove(path)

    mydata.delete()
    mp.track(request.user.id, 'Card Deleted', {
        'card_id': id
    })

    return redirect('main:form')



@login_required
def delete_account(request):

    if request.method == 'GET':
        user = request.user
        print(user)
        username = user.username
        print(username)
        if CardData.objects.filter(email=request.user.email).exists():
            CardData.objects.filter(email=request.user.email).delete()

        user.delete()
        mp.people_set(username, {
            '$username': username,
            'Account Status': 'Deleted'
        })
        messages.success(
            request, f"Your account ({username}) has been deleted.")
        logout(request)
        return redirect('main:login')

    return render(request, 'setting.html')


def password_reset_request(request):
    if request.method == "GET": 
        password_reset_form = PasswordResetForm(request.GET)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():

                    for user in associated_users:
                        subject = "Password Reset Requested"
                        email_template_name = "password/password_reset_email.txt"
                        c = {


                            'user': user.email,
                            'domain': get_current_site(request).domain,
                            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                            'token': default_token_generator.make_token(user),
                            'protocol': 'https' if request.is_secure() else 'http',

                        }
                        email = render_to_string(email_template_name, c)

                        try:
                            send_mail(
                                subject, email, 'architashah27@gmail.com', [user.email], fail_silently=False)
                        except BadHeaderError:
                            return HttpResponse('Invalid header found.')

                        messages.success(
                            request, 'A message with reset password instructions has been sent to your inbox.')
                        return redirect("main:login")
            messages.error(request, 'An invalid email has been entered.')
        password_reset_form = PasswordResetForm()
        return render(request=request, template_name="password/password_reset.html", context={"password_reset_form": password_reset_form})
    


@never_cache
def password_reset_confirm(request, uidb64, token):
    UserModel = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UserModel.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('password1')
            confirm_new_password = request.POST.get('password2')
            if new_password == confirm_new_password:
                user.set_password(new_password)
                user.save()
                messages.success(
                    request, 'Your password has been successfully reset. You can now log in with your new password.')
                return redirect(reverse('main:login'))
            else:
                messages.error(request, 'New passwords do not match.')
        return render(request, 'password/password_reset_confirm.html')
    else:
        messages.error(
            request, 'The password reset link is invalid or has expired.')
        return redirect(reverse('main:password_reset'))


@never_cache
@login_required
def send(request, id):
    mydata = CardData.objects.get(id=id)
    if request.method == "POST":
        email = request.POST.get('email')
        message = request.POST.get('message')
        fullname = request.POST.get('name')

        vcard = vCard()
        vcard.add('fn')
        vcard.fn.value = mydata.fullname
        vcard.add('ph').value = mydata.phone
        vcard.add('email')
        vcard.email.value = mydata.email
        vcard.add('tel')
        vcard.tel.value = mydata.phone

        with mydata.upload.open('rb') as img:
            image_data = base64.b64encode(img.read()).decode()
        vcard.add('PHOTO;ENCODING=b').value = image_data

        vcard_string = vcard.serialize()

        html_content = render_to_string(
            'template_card.html',  {'data': mydata})
        email_content = '{}\n\n{}'.format(message, html_content)
        msg = EmailMultiAlternatives(
            'Card',
            email_content,
            'architashah27@gmail.com',
            [email],
            headers={'Content-Type': 'text/html'},
        )

        with mydata.upload.open('rb') as img:
            msg_img = MIMEImage(img.read())
            msg_img.add_header('Content-ID', '<{}>'.format(mydata.upload))
            msg.attach(msg_img)

        msg.content_subtype = "html"
        msg.attach(mydata.fullname+'.vcf', vcard_string, 'text/vcard')
        #msg.attach(mydata.upload.name, img.read(), 'image/png')
        image_data = base64.b64decode(image_data)
        msg.attach(mydata.upload.name, image_data, 'image/png')


        msg.send()
        mp.track(request.user.id, 'Sent Email', {
            'recipient': email,
            'subject': 'Card',
            'date': datetime.now()
        })
        messages.success(request, "Please Check your mailbox.")
        return redirect('main:form')
    else:
        messages.error(request, "Something went wrong")

    return render(request=request, template_name="homepage.html", context={'form': mydata})


@never_cache
@login_required
def sendmail(request, id):
    mydata = CardData.objects.get(id=id)
    if request.method == "POST":
        email = request.POST.get('email')
        message = request.POST.get('message')
        fullname = request.POST.get('name')

        vcard = vCard()
        vcard.add('fn')
        vcard.fn.value = mydata.fullname
        vcard.add('ph').value = mydata.phone
        vcard.add('email')
        vcard.email.value = mydata.email
        vcard.add('tel')
        vcard.tel.value = mydata.phone

        with mydata.upload.open('rb') as img:
            image_data = base64.b64encode(img.read()).decode()
        vcard.add('PHOTO;ENCODING=b').value = image_data

        vcard_string = vcard.serialize()

        html_content = render_to_string(
            'template_card.html',  {'data': mydata})
        email_content = '{}\n\n{}'.format(message, html_content)
        msg = EmailMultiAlternatives(
            'Card',
            email_content,
            'architashah27@gmail.com',
            [email],
            headers={'Content-Type': 'text/html'},
        )

        with mydata.upload.open('rb') as img:
            msg_img = MIMEImage(img.read())
            msg_img.add_header('Content-ID', '<{}>'.format(mydata.upload))
            msg.attach(msg_img)

        msg.content_subtype = "html"
        msg.attach(mydata.fullname+'.vcf', vcard_string, 'text/vcard')
        #msg.attach(mydata.upload.name, img.read(), 'image/png')
        image_data = base64.b64decode(image_data)
        msg.attach(mydata.upload.name, image_data, 'image/png')


        msg.send()
        mp.track(request.user.id, 'Sent Email', {
            'recipient': email,
            'subject': 'Card',
            'date': datetime.now()
        })
        messages.success(request, "Please Check your mailbox.")
        return redirect('main:form')
    else:
        messages.error(request, "Something went wrong")

    return render(request=request, template_name="homepage.html", context={'form': mydata})


def sendmailqr(request, id):

    mydataa = CardData.objects.filter(email=request.user.email)
    print(mydataa)
    if request.method == "GET":
        mydata = CardData.objects.get(id=id)
        email = mydata.email

        vcard = vCard()
        vcard.add('fn')
        vcard.fn.value = mydata.fullname
        vcard.add('ph').value = mydata.phone
        vcard.add('email')
        vcard.email.value = mydata.email
        vcard.add('tel')
        vcard.tel.value = mydata.phone

        with open(mydata.upload.path, 'rb') as img:
            print(img)
            image_data = base64.b64encode(img.read()).decode()
        vcard.add('PHOTO;ENCODING=b').value = image_data
        # vcard.add('photo').value = image_data

        vcard_string = vcard.serialize()

        html_content = render_to_string('template_card.html', {'data': mydata})
        msg = EmailMultiAlternatives(
            'Card',
            html_content,
            'architashah27@gmail.com',
            [email],
            headers={'Content-Type': 'text/html'},
        )

        image = MIMEImage(mydata.upload.read())
        image.add_header('Content-ID', '<{}>'.format(mydata.upload))
        msg.attach(image)
        msg.content_subtype = "html"

        msg.attach(mydata.fullname+'.vcf', vcard_string, 'text/vcard')

        msg.send()
        mp.track(request.user.id, 'Sent Email', {
            'recipient': email,
            'subject': 'Card',
            'date': datetime.now()
        })
        print(request.user.id)
        messages.success(request, "Please Check your mailbox.")
        return redirect(reverse('main:qrcard', args=[id]))
    else:
        messages.error(request, "Something went wrong")

    return render(request=request, template_name="homepage.html", context={'form': mydataa})


@never_cache
def qrcard(request, id):
    if request.method == "GET":
        mydata = CardData.objects.get(id=id)
        vcard = vCard()
        vcard.add('fn')
        vcard.fn.value = mydata.fullname
        vcard.add('ph').value = mydata.phone
        vcard.add('email')
        vcard.email.value = mydata.email
        vcard.add('tel')
        vcard.tel.value = mydata.phone

        with default_storage.open(mydata.upload.name, 'rb') as img:
            image_data = base64.b64encode(img.read()).decode()

        vcard.add('PHOTO;ENCODING=b').value = image_data
        response = HttpResponse(vcard.serialize(), content_type='text/vcard')
        response['Content-Disposition'] = 'attachment; filename=' + \
            mydata.fullname + '.vcf'
        mp.track(request.user.id, 'QR Code Scanned', {
            'card_id': id,
        })
    return render(request=request, template_name="qr_card.html", context={'mydata': mydata})


@never_cache
def qr_card(request, id):
    if request.method == "GET":
        mydata = CardData.objects.get(id=id)
        vcard = vCard()
        vcard.add('fn')
        vcard.fn.value = mydata.fullname
        vcard.add('ph').value = mydata.phone
        vcard.add('email')
        vcard.email.value = mydata.email
        vcard.add('tel')
        vcard.tel.value = mydata.phone

        with default_storage.open(mydata.upload.name, 'rb') as img:
            image_data = base64.b64encode(img.read()).decode() 

        vcard.add('PHOTO;ENCODING=b').value = image_data
        response = HttpResponse(vcard.serialize(), content_type='text/vcard')
        response['Content-Disposition'] = 'attachment; filename=' + \
            mydata.fullname + '.vcf'
        mp.track(request.user.id, 'QR Code Downloaded', {
            'card_id': id,
            'download_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    return response


@login_required
@never_cache
def setting(request):
    mp.track(request.user.id, 'Settings Page')
    return render(request=request, template_name="setting.html")


def handler404(request, exception):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)


@login_required
@never_cache
def change_password_view(request):
    if request.method == 'POST':
        new_password1 = request.POST['password1']
        new_password2 = request.POST['password2']

        if new_password1 != new_password2:
            messages.error(request, 'New passwords do not match')
        else:
            user = request.user
            user.set_password(new_password1)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully')
            return redirect('/setting')

    return render(request, 'setting.html')


def resend_activation(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()

        if user:
            if not user.is_active:
                activateEmail(request, user, email)
                return redirect('main:login')
            else:
                messages.error(request, 'Your account has already been activated.')
        else:
            messages.error(request, 'User with this email does not exist.')

    return render(request, 'resend_activation.html')