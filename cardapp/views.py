from datetime import datetime
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.forms import SetPasswordForm
from django.urls import reverse_lazy
from django.views.decorators.cache import never_cache
from django.shortcuts import render,redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import login
from django.contrib import messages
from .forms import NewUserForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm 
from django.template import loader
from django.urls import reverse
from django.http import HttpResponse,HttpResponseRedirect
from django.core.mail import send_mail, BadHeaderError,EmailMultiAlternatives
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
from qrcode import QRCode,constants
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from smtplib import SMTPDataError
from django.views.generic import FormView
from django.http import Http404, HttpResponse
import os
from django.conf import settings
from mixpanel import Mixpanel
mp = Mixpanel("36cbd6f0b92d0588b757298c93c7a733")







# Create your views here.
# def register_request(request):
# 	if request.method == "POST":
# 		form = NewUserForm(request.POST)
# 		if form.is_valid():
# 			user = form.save()
# 			login(request, user)
# 			messages.success(request, "Registration successful." )
# 			return redirect("main:login")
# 		messages.error(request, "Unsuccessful registration. Invalid information.")
# 	form = NewUserForm()
# 	return render (request=request, template_name="register.html", context={"register_form":form})
def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, '\nThank you for your email confirmation. Now you can login your account.')
        return redirect('/login')
    else:
        messages.error(request, 'Activation link is invalid!')
    
    return redirect('/login')

# def register(request):
#     if request.method == "POST":
#         mp.track(request.user.id, 'Viewed Register Page')
#         form = NewUserForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.is_active = False
#             mp.people_set(request.user.id, {
#                 '$email': request.user.email,
#                 '$created': '2013-04-01T13:20:00',
#                 '$last_login': datetime.now()
#             })
#             mp.track(request.user.id, 'Signed Up')
#             user.save()
#             activateEmail(request, user, request.POST.get('email'))
            
#             #mp.track("User Registered", {"user_id": user.id})

#         else:
#             for error in list(form.errors.values()):
#                 messages.error(request, error)

#     else:
#         form = NewUserForm()
        

#     return render(request=request,template_name="register.html",context={"register_form":form})



def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password1')
        confirm_password = request.POST.get('password2')
        
        # Validate form data
        if not username or not email or not password or not confirm_password:
            messages.error(request, 'All fields are required.')
        elif password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email address is already registered.')
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
            # mp.people_set(request.user.id, {
            #     '$email': request.user.email,
            #     '$created': '2013-04-01T13:20:00',
            #     '$last_login': datetime.now()
            # })
            mp.track(request.user.id, 'Signed Up')
         
            activateEmail(request, user, email)
            messages.success(request, '\nYour account has been created. Please check your email to activate your account.')
            
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
        messages.success(request, f'Dear {user}, please go to you email {to_email} inbox and click on received activation link to confirm and complete the registration. Note: Check your spam folder.')
    else:
        messages.error(request, f'Problem sending confirmation email to {to_email}, check if you typed it correctly.')


def register_request(request):  
   
    if request.method == 'POST':  
        form = NewUserForm(request.POST)  
        if form.is_valid():
            # save form in the memory not in database  
            user = form.save(commit=False)
            user.is_active = False # Deactivate account till it is confirmed
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




# def login_request(request):
#         mp.track(request.user.id, 'Viewed Login Page')
#         if request.method == "POST":
#             form = AuthenticationForm(request, data=request.POST)
           
#             if form.is_valid():
#                 username = form.cleaned_data.get('username') 
#                 password = form.cleaned_data.get('password')
#                 user = authenticate(username=username, password=password)
                
#                 if user is not None:
#                     login(request, user)
#                     mp.people_set(request.user.id, {
#                         '$name': request.user.get_full_name(),
#                         '$email':request.user.email,
#                         '$last_login': datetime.now()
#                     })
#                     mp.track(request.user.id, 'Login')
#                     messages.success(request, f"You are now logged in as {username}.")
#                     return redirect("main:addcard")
#                 else:
#                     messages.error(request,"Invalid username or password.")
#             else:
#                 messages.error(request,"Invalid username or password.")
                            
#         form = AuthenticationForm()
       
#         return render(request=request, template_name="login.html", context={"login_form":form})

@user_passes_test(lambda u: not u.is_authenticated, login_url='main:form')
def login_request(request):
    mp.track(request.user.id, 'Viewed Login Page')
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        remember_me = request.POST.get('remember_me')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
                return redirect('main:form')
            mp.people_set(request.user.id, {
                '$name': request.user.get_full_name(),
                '$email':request.user.email,
                '$last_login': datetime.now()
            })
            mp.track(request.user.id, 'Login')
            messages.success(request, f"You are now logged in as {username}.")
            return redirect("main:form")
        else:
            messages.error(request,"Invalid username or password.")
            
    return render(request=request, template_name="login.html")


def logout_request(request):
        logout(request)
        messages.success(request, "You have successfully logged out.") 
        return redirect("main:login")

@login_required
@never_cache
def homepage(request):
    mp.track(request.user.id, 'Viewed HomePage')
    if request.method == 'GET':
        mydata = CardData.objects.filter(email=request.user.email)
        print(request.user.email)
        #mydata = CardData.objects.all()
        print(mydata)
        return render(request=request, template_name='homepage.html',context={'mydata': mydata})
    else:
        return redirect('main:login')
    


########ADD CARD FORM
# def addcard(request):
#     mp.track(request.user.id, 'Viewed Add card Page')
#     if request.method == 'POST':
#         form = CardForm(request.POST,request.FILES)
#         if form.is_valid():
#             card=form.save()
#             print(card.id)
#             url = request.build_absolute_uri(reverse('main:qrcard', args=[card.id]))
            
           
#             qr = QRCode(version=1, error_correction=constants.ERROR_CORRECT_L)
#             qr.add_data(url)
#             qr.make()
#             img = qr.make_image()
#             # Save the QR code to a file
#             img.save("media/qr_codes/qr_code_{}.png".format(card.id))
#             # Update the QR code field of the contact with the URL of the image
#             card.qr_code = "media/qr_codes/qr_code_{}.png".format(card.id)
#             mp.track(request.user.id, 'Card Saved')
#             card.save()
#             mp.track(request.user.id, 'Card Added')
#             messages.success(request, 'Saved Successfully!')
#             return redirect("main:card")
#         else:
#             messages.error(request, 'Something went wong')
#     else:
#         form = CardForm()
#     return render (request=request, template_name="addcard.html", context={"form":form})


# def addcard(request):
#     mp.track(request.user.id, 'Viewed Add card Page')
#     if request.method == 'POST':
#         # Handle the POST request
#         fullname=request.POST.get('fullname')
#         cardname=request.POST.get('cardname')
#         department=request.POST.get('department')
#         company=request.POST.get('company')
#         phone=request.POST.get('phone')
#         alternatephone=request.POST.get('alternatephone')
#         email=request.POST.get('email')
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

#         if not fullname or not email or not cardname or not department or not company or not phone or not email or not upload:
#                messages.error(request, 'Please enter all details!')
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
      
#                     url = request.build_absolute_uri(reverse('main:qrcard', args=[my_model_instance.id]))
#                     qr = QRCode(version=1, error_correction=constants.ERROR_CORRECT_L)
#                     qr.add_data(url)
#                     qr.make()
#                     img = qr.make_image()
#                     img.save("media/qr_codes/qr_code_{}.png".format(my_model_instance.id))
#                     my_model_instance.qr_code = "media/qr_codes/qr_code_{}.png".format(my_model_instance.id)
#                     my_model_instance.save()

#                     messages.success(request, 'Saved Successfully!')
                
                
#                     return redirect("main:form")
#     else:
        
        
      
#         return render(request, 'addcard.html')
    

   
@login_required
@never_cache
def addcard(request):
    mp.track(request.user.id, 'Viewed Add card Page')
    if request.method == 'POST':
        # Handle the POST request
        fullname=request.POST.get('fullname')
        cardname=request.POST.get('cardname')
        department=request.POST.get('department')
        company=request.POST.get('company')
        phone=request.POST.get('phone')
        alternatephone=request.POST.get('alternatephone')
        email=request.POST.get('email')
        upload = request.FILES.get('upload')

        my_model_instance = CardData()
        my_model_instance.fullname = fullname
        my_model_instance.cardname = cardname
        my_model_instance.department = department
        my_model_instance.company = company
        my_model_instance.phone = phone
        my_model_instance.alternatephone = alternatephone
        my_model_instance.email = email
        my_model_instance.upload = upload

        if not fullname or not email or not cardname or not department or not company or not phone or not email or not upload:
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
                    my_model_instance.save()

                    url = request.build_absolute_uri(reverse('main:qrcard', args=[my_model_instance.id]))
                    qr = QRCode(version=1, error_correction=constants.ERROR_CORRECT_L)
                    qr.add_data(url)
                    qr.make()
                    img = qr.make_image()
                    img.save("media/qr_codes/qr_code_{}.png".format(my_model_instance.id))
                    my_model_instance.qr_code = "media/qr_codes/qr_code_{}.png".format(my_model_instance.id)
                    my_model_instance.save()

                    messages.success(request, 'Saved Successfully!')
                    return redirect("main:form")
        return redirect("main:addcard")
    else:
        # Render the form for the GET request
        return render(request, 'addcard.html')
 


@login_required
@never_cache
def card(request,id):
    mydata = CardData.objects.get(id=id)
    if request.method == 'GET':
        mp.track(request.user.id, 'Viewed Get all card page')
        print(mydata.qr_code)
        return render(request=request, template_name='card.html',context={'x': mydata})
    return render(request=request, template_name='card.html',context={'x': mydata})

def qrcard(request,id):
    if request.method == 'GET':
        mp.track(request.user.id, 'Viewed Qr card')
        mydata = CardData.objects.get(id=id)
        print(mydata)
        return render(request=request, template_name='qr_card.html',context={'mydata': mydata})
     
##### UPDSTEEEEE
# def update(request,id):
#     mydata = CardData.objects.get(id=id)
#     form=CardForm(instance=mydata)
#     if request.method == 'POST':
#         form = CardForm(request.POST,request.FILES,instance=mydata)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Updated Successfully!')
#             return redirect("main:card")
#         else:
#             messages.error(request,"Something went wrong")
#     context = {
#         'form': form,
#     }
#     return render(request,"addcard.html", context)

@login_required
@never_cache
def update(request,id):
    mp.track(request.user.id, 'Viewed Add card Page')
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
        url = request.build_absolute_uri(reverse('main:qrcard', args=[card_data.id]))
        qr = QRCode(version=1, error_correction=constants.ERROR_CORRECT_L)
        qr.add_data(url)
        qr.make()
        img = qr.make_image()
        img.save(f"media/qr_codes/qr_code_{card_data.id}.png")
        card_data.qr_code = f"media/qr_codes/qr_code_{card_data.id}.png"
        card_data.save()

        messages.success(request, 'Updated Successfully!')
        return redirect("main:form")
    else:
        # Render the form for the GET request to update the CardData instance
        context = {
            'card_data': card_data
        }
        
        return render(request, 'addcard.html', context)

def delete(request,id):
   
    mydata = CardData.objects.get(id=id)
    
    # Delete the image file
    if mydata.upload:
        path = os.path.join(settings.MEDIA_ROOT, str(mydata.upload))
        if os.path.isfile(path):
            os.remove(path)

    # Delete the QR code file
    if mydata.qr_code:
        path1 = os.path.join(settings.MEDIA_ROOT, str(mydata.qr_code))
        if os.path.isfile(path1):
            os.remove(path1)
            
    mydata.delete()

    
    return redirect('main:form')

# def delete(request, id):
#     mydata = CardData.objects.get(id=id)
#     qr_code_path = mydata.qr_code.path  # Get the path of the QR code image
#     if os.path.exists(qr_code_path):  # Check if the file exists
#         os.remove(qr_code_path)  # Delete the file
#     mydata.delete()
#     messages.success(request, 'Deleted Successfully!')
#     return redirect("main:form")

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
        messages.success(request, f"Your account ({username}) has been deleted.")
        logout(request)
        return redirect('main:login')

    return render(request, 'setting.html')
   
@never_cache
def password_reset_request(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = User.objects.filter(Q(email=data))
			if associated_users.exists():
                                
				for user in associated_users:
					subject = "Password Reset Requested"
					email_template_name = "password/password_reset_email.txt"
					c = {
					# "email":user.email,
					# 'domain':'127.0.0.1:8000',
					# 'site_name': 'Website',
					# "uid": urlsafe_base64_encode(force_bytes(user.pk)),
					# 'token': default_token_generator.make_token(user),
					# 'protocol': 'http',
                    
                    'user': user.email,
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                    'protocol': 'https' if request.is_secure() else 'http',
                    
					}
					email = render_to_string(email_template_name, c)
                    
					try:
						send_mail(subject, email, 'architashah27@gmail.com' , [user.email], fail_silently=False)
					except BadHeaderError:
						return HttpResponse('Invalid header found.')
                    
                                        
					messages.success(request, 'A message with reset password instructions has been sent to your inbox.')
					return redirect ("main:login")
			messages.error(request, 'An invalid email has been entered.')
	password_reset_form = PasswordResetForm()
	return render(request=request, template_name="password/password_reset.html", context={"password_reset_form":password_reset_form})


# def send(request,id):
#     sendEmail = sendForm(request.POST)   
#     subject="Card"
#     if request.method == "POST":
#         if sendEmail.is_valid():
#             mydata = CardData.objects.get(id=id)
#             email=sendEmail.cleaned_data.get('email')
#             print(email)
#             message = render_to_string('template_card.html', {'data': mydata})
#             send_mail(subject,message,'architashah27@gmail.com',[email])
#     return render(request=request,template_name="send.html",context={'form':sendEmail})

# def b64_image(filename):
#      with open(filename, 'rb') as img:
#         image_data = base64.b64encode(img.read())
#         return image_data.decode('utf-8')

# def create_vcard(first_name, last_name, email, phone):
#     vcard = vCard()
    
#     vcard.add('fn')
#     vcard.fn.value = first_name + " " + last_name
#     vcard.add('email')
#     vcard.email.value = email
#     vcard.email.type_param = 'INTERNET'
#     vcard.add('tel')
#     vcard.tel.value = phone
#     return vcard.serialize()

# def create_qr_code(vcard_file):
#     img = qrcode.make(vcard_file)
#     return ContentFile(img.getvalue())

# def save_qr_code(qr_code_image, instance):
#     instance.qr_code.save('qr_code.jpg', qr_code_image, save=True)



######################################SEND
# def send(request, id):
#     sendEmail = sendForm(request.POST)   
#     if request.method == "POST":
#         if sendEmail.is_valid():
#             mydata = CardData.objects.get(id=id)
           
#             vcard = vCard()
#             vcard.add('fn')
#             vcard.fn.value = mydata.firstname + ' '+ mydata.lastname
#             vcard.add('ph').value= mydata.phone
#             vcard.add('email')
#             vcard.email.value = mydata.email
#             vcard.add('tel')
#             vcard.tel.value = mydata.phone
            
#             with open(mydata.upload.path, 'rb') as img:
#                 print(img)
#                 image_data = base64.b64encode(img.read()).decode()
#             vcard.add('PHOTO;ENCODING=b').value=image_data
#             #vcard.add('photo').value = image_data
            

#             vcard_string = vcard.serialize()


#             email=sendEmail.cleaned_data.get('email')
            
#             html_content = render_to_string('template_card.html', {'data': mydata}) 
#             msg = EmailMultiAlternatives (
#             'Card',
#             html_content,
#             'architashah27@gmail.com',
#             [email],
#             headers={'Content-Type':'text/html'},
#             )

           
#             image = MIMEImage(mydata.upload.read())
#             image.add_header('Content-ID', '<{}>'.format(mydata.upload))
#             msg.attach(image)
#             msg.content_subtype = "html"

#             msg.attach(mydata.firstname+'.vcf',vcard_string,'text/vcard')

#             msg.send()
#             mp.track(request.user.id, 'Sent Email', {
#                 'recipient': email,
#                 'subject': 'Card',
#                 'date': datetime.now()
#             })
#             print(request.user.id)
#             messages.success(request,"Please Check your mailbox.")
#         else:
#             messages.error(request,"Something went wrong")

#     return render(request=request,template_name="send.html",context={'form':sendEmail})
 



def send(request, id):
    mydata = CardData.objects.get(id=id)
    if request.method == "POST":
        email=request.POST.get('email')
        message = request.POST.get('message')
        fullname=request.POST.get('name')
           
        vcard = vCard()
        vcard.add('fn')
        vcard.fn.value = mydata.fullname
        vcard.add('ph').value= mydata.phone
        vcard.add('email')
        vcard.email.value = mydata.email
        vcard.add('tel')
        vcard.tel.value = mydata.phone
        
        with open(mydata.upload.path, 'rb') as img:
            print(img)
            image_data = base64.b64encode(img.read()).decode()
        vcard.add('PHOTO;ENCODING=b').value=image_data
        #vcard.add('photo').value = image_data
        

        vcard_string = vcard.serialize()


        
        
        html_content = render_to_string('template_card.html',  {'data': mydata}) 
        msg = EmailMultiAlternatives (
        fullname,
        html_content,
       
        'architashah27@gmail.com',
        [email],
       
        headers={'Content-Type':'text/html'},
       
        )

        
        image = MIMEImage(mydata.upload.read())
        image.add_header('Content-ID', '<{}>'.format(mydata.upload))
        msg.attach(image)
        msg.content_subtype = "html"

        msg.attach(mydata.fullname+'.vcf',vcard_string,'text/vcard')
      
        msg.send()
        mp.track(request.user.id, 'Sent Email', {
            'recipient': email,
            'subject': 'Card',
            'date': datetime.now()
        })
        print(request.user.id)
        messages.success(request,"Please Check your mailbox.")
        return redirect(reverse('main:card', args=[id]))
    else:
        messages.error(request,"Something went wrong")

    return render(request=request,template_name="card.html",context={'form':mydata})
           

def sendmail(request, id):
   
    
    mydataa = CardData.objects.filter(email=request.user.email)
    print(mydataa)
    if request.method == "GET":
        mydata= CardData.objects.get(id=id)
        email=mydata.email
        
           
        vcard = vCard()
        vcard.add('fn')
        vcard.fn.value = mydata.fullname
        vcard.add('ph').value= mydata.phone
        vcard.add('email')
        vcard.email.value = mydata.email
        vcard.add('tel')
        vcard.tel.value = mydata.phone
        
        with open(mydata.upload.path, 'rb') as img:
            print(img)
            image_data = base64.b64encode(img.read()).decode()
        vcard.add('PHOTO;ENCODING=b').value=image_data
        #vcard.add('photo').value = image_data
        

        vcard_string = vcard.serialize()


        
        
        html_content = render_to_string('template_card.html', {'data': mydata}) 
        msg = EmailMultiAlternatives (
        'Card',
        html_content,
        'architashah27@gmail.com',
        [email],
        headers={'Content-Type':'text/html'},
        )

        
        image = MIMEImage(mydata.upload.read())
        image.add_header('Content-ID', '<{}>'.format(mydata.upload))
        msg.attach(image)
        msg.content_subtype = "html"

        msg.attach(mydata.fullname+'.vcf',vcard_string,'text/vcard')

        msg.send()
        mp.track(request.user.id, 'Sent Email', {
            'recipient': email,
            'subject': 'Card',
            'date': datetime.now()
        })
        print(request.user.id)
        messages.success(request,"Please Check your mailbox.")
        return redirect('main:form')
    else:
        messages.error(request,"Something went wrong")

    return render(request=request,template_name="homepage.html",context={'form':mydataa})

def qrcard(request,id):
    if request.method == "GET":
        mydata = CardData.objects.get(id=id)
        vcard = vCard()
        vcard.add('fn')
        vcard.fn.value = mydata.fullname
        vcard.add('ph').value= mydata.phone
        vcard.add('email')
        vcard.email.value = mydata.email
        vcard.add('tel')
        vcard.tel.value = mydata.phone
                
        with open(mydata.upload.path, 'rb') as img:
                    
            image_data = base64.b64encode(img.read()).decode()
        vcard.add('PHOTO;ENCODING=b').value=image_data
        response = HttpResponse(vcard.serialize(), content_type='text/vcard')
        response['Content-Disposition'] = 'attachment; filename='+ mydata.firstname +'.vcf'
    return render(request=request,template_name="qr_card.html",context={'mydata':mydata})

def qr_card(request,id):
    if request.method == "GET":
        mydata = CardData.objects.get(id=id)
        vcard = vCard()
        vcard.add('fn')
        vcard.fn.value = mydata.fullname
        vcard.add('ph').value= mydata.phone
        vcard.add('email')
        vcard.email.value = mydata.email
        vcard.add('tel')
        vcard.tel.value = mydata.phone
                
        with open(mydata.upload.path, 'rb') as img:
                    
            image_data = base64.b64encode(img.read()).decode()
        vcard.add('PHOTO;ENCODING=b').value=image_data
        response = HttpResponse(vcard.serialize(), content_type='text/vcard')
        response['Content-Disposition'] = 'attachment; filename='+ mydata.firstname +'.vcf'
    return response

@login_required
@never_cache
def setting(request):
      return render(request=request,template_name="setting.html")

def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)