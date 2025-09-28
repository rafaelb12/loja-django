from django.contrib import admin
from .models import Produto
from .models import Categoria

admin.site.register(Categoria)


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco')
    search_fields = ('nome',)
