from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image,ImageDraw
import io
from django.urls import reverse
from django.core.files.base import ContentFile
from django.contrib.auth.models import User

# Create your models here.
class CardData(models.Model):
    username=models.CharField(max_length=200,blank=True)
    fullname=models.CharField(max_length=200,blank=True)
    # middlename=models.CharField(max_length=100)
    #lastname=models.CharField(max_length=100)
    title=models.CharField(blank=True,max_length=50)
    department=models.CharField(blank=True,max_length=50)
    company=models.CharField(blank=True,max_length=100)
    phone = models.CharField(null=False, blank=False, unique=True,max_length=11)
    upload = models.FileField(blank=True,upload_to ='uploads',null=True)
    email=models.EmailField(blank=False,max_length = 254,null=False)
    cardname =models.CharField(max_length=100,blank=True)
    #qr_code = models.ImageField(upload_to='qr_codes', null=True,blank=True)
    qr_code = models.URLField(blank=True, null=True)
    alternatephone= models.CharField(null=True,  max_length=11,blank=True)
    

    # def generate_qr_code(self):
    #     qr = qrcode.QRCode(version=1, box_size=10, border=5)
    #     # generate QR code data
    #     qr.add_data(self.get_absolute_url())
    #     qr.make(fit=True)
    #     img = qr.make_image(fill_color="black", back_color="white")

    #     # Save the QR code image to the qr_code field
    #     buf = io.BytesIO()
    #     img.save(buf, format='PNG')
    #     file_name = 'qr_code_{}.png'.format(self.pk)
    #     self.qr_code.save(file_name, File(buf))
    #     buf.seek(0)

    #code = models.ImageField(upload_to='code', null=True, blank=True)

    # def save(self,*args,**kwargs):
    #     qr_image = qrcode.make(self.firstname)
    #     qr_offset = Image.new('RGB',(310,310),'white')
    #     qr_offset.paste(qr_image)
    #     files_name = f'{self.firstname}.png'
    #     stream = BytesIO()
    #     qr_offset.save(stream,'PNG')
    #     self.qr_code.save(files_name,File(stream),save=False)
    #     qr_offset.close()
    #     super().save(*args,**kwargs)

    # def save(self,*args,**kwargs):
    #     qr_image = qrcode.make(self.firstname)
    #     qr_offset = Image.new('RGB',(310,310),'white')
    #     qr_offset.paste(qr_image)
    #     files_name = f'{self.firstname}.png'
    #     stream = BytesIO()
    #     qr_offset.save(stream,'PNG')
    #     self.qr_code.save(files_name,File(stream),save=False)
    #     qr_offset.close()
    #     super().save(*args,**kwargs)

    # def save(self,*args,**kwargs):
    #     #super().save(*args, **kwargs)
    #     url = reverse('main:card', args=[self.pk])
    #     img = qrcode.make(url)
    #     qr_offset = Image.new('RGB',(310,310),'white')
    #     qr_offset.paste(img)
    #     self.qr_code.save('qr_code.jpg', ContentFile(img.tobytes()), save=True)
        #super().save(*args,**kwargs)
    

    

