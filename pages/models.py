from django.db import models


HEADER_POSITION = (
    ('F', 'Firts'),
    ('S', 'Second'),
    ('T', 'Third'),
)


class Header(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    img = models.ImageField(upload_to='headers/')
    position = models.CharField(max_length=1, choices=HEADER_POSITION, unique=True, blank=True, null=True)
    caption_title = models.CharField(max_length=35, blank=True, null=True)
    caption_content = models.CharField(max_length=65, blank=True, null=True)
    caption_button = models.URLField(max_length=200, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class ModelBlogBase(models.Model):
	id = models.AutoField(primary_key = True)
	estado = models.BooleanField('Estado', default=True)
	fecha_creacion = models.DateField('Fecha de Creación', auto_now=False, auto_now_add=True)
	fecha_modificacion = models.DateField('Fecha de Modificación', auto_now=True, auto_now_add=False)
	fecha_eliminacion = models.DateField('Fecha de Eliminación', auto_now=True, auto_now_add=False)

	class Meta:
		abstract = True


class Web(ModelBlogBase):
	nosotros = models.TextField('Nosotros')
	telefono = models.CharField('Teléfono', max_length=10)
	email = models.EmailField('Correo Electrónico', max_length=200)
	direccion = models.CharField('Dirección', max_length=200)

	class Meta:
		verbose_name = 'Web'
		verbose_name_plural = 'Webs'

	def __str__(self):
		return self.nosotros


class RedesSociales(ModelBlogBase):
	facebook = models.URLField('Facebook')
	twitter = models.URLField('Twitter')
	instagram = models.URLField('Instagram')

	class Meta:
		verbose_name = 'Red Social'
		verbose_name_plural = 'Redes Sociales'

	def __str__(self):
		return self.facebook


class Contacto(ModelBlogBase):
	nombre = models.CharField('Nombre', max_length=100)
	correo = models.EmailField('Correo Electrónico', max_length=200)
	asunto = models.CharField('Asunto', max_length = 100)
	mensaje = models.TextField('Mensaje')

	class Meta:
		verbose_name = 'Contacto'
		verbose_name_plural = 'Contactos'

	def __str__(self):
		return self.asunto


class Suscriptor(ModelBlogBase):
	correo = models.EmailField(max_length=200)

	class Meta:
		verbose_name = 'Suscriptor'
		verbose_name_plural = 'Suscriptores'

	def __str__(self):
		return self.correo

