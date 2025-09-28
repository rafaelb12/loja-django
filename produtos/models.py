from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Categoria(models.Model):
    nome = models.CharField(max_length=50)

    def __str__(self):
        return self.nome

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    imagem = models.ImageField(upload_to='produtos/')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    curtido_por = models.ManyToManyField(User, related_name='produtos_curtidos', blank=True)

    def __str__(self):
        return self.nome

class Pedido(models.Model):
    produtos = models.JSONField()
    total = models.FloatField()
    nome_cliente = models.CharField(max_length=200)
    email_cliente = models.EmailField()
    telefone_cliente = models.CharField(max_length=50)
    pago = models.BooleanField(default=False)  
    pix_chave = models.CharField(max_length=100, blank=True, null=True)
    pix_qr = models.TextField(blank=True, null=True) 

    def __str__(self):
        return f"Pedido {self.id} - {self.nome_cliente}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    foto = models.ImageField(upload_to="fotos_perfil/", blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    endereco = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.user.username
    
@receiver(post_save, sender=User)
def criar_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def salvar_profile(sender, instance, **kwargs):
    instance.profile.save()
    
    