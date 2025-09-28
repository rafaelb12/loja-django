from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import (
    cadastrar_usuario,
    curtir_produto,
    dashboard_usuario,
    detalhe_pedido,
    lista_produtos,
    detalhe_produto,
    adicionar_ao_carrinho,
    login_usuario,
    logout_usuario,
    perfil_usuario,
    produtos_curtidos,
    sugestoes_produtos,
    toggle_curtir_produto,
    ver_carrinho,
    remover_do_carrinho,
    atualizar_carrinho,
    checkout,
    cadastrar_produto,
    pix_pagamento,
    pix_webhook, 
    buscar
)

urlpatterns = [
    path('', lista_produtos, name='lista_produtos'),
    path('produto/<int:id>/', detalhe_produto, name='detalhe_produto'),
    path('adicionar/<int:id>/', adicionar_ao_carrinho, name='adicionar_carrinho'),
    path('carrinho/', ver_carrinho, name='ver_carrinho'),
    path('carrinho/remover/<int:id>/', remover_do_carrinho, name='remover_carrinho'),
    path('carrinho/atualizar/', atualizar_carrinho, name='atualizar_carrinho'),
    path('checkout/', checkout, name='checkout'),
    path('cadastrar/', cadastrar_produto, name='cadastrar_produto'),
    path('pix/<int:pedido_id>/', pix_pagamento, name='pix_pagamento'),
    path('pix/webhook/', pix_webhook, name='pix_webhook'),
    path("cadastro/", cadastrar_usuario, name="cadastro_usuario"),
    path("login/", login_usuario, name="login_usuario"),
    path("logout/", logout_usuario, name="logout_usuario"),
    path("perfil/", perfil_usuario, name="perfil_usuario"),
    path('buscar/', buscar, name='buscar'),
    path('sugestoes/', sugestoes_produtos, name='sugestoes_produtos'),
    path('usuario/', dashboard_usuario, name='dashboard_usuario'),
    path('usuario/pedido/<int:pedido_id>/', detalhe_pedido, name='detalhe_pedido'),
    path('curtir/<int:produto_id>/', curtir_produto, name='curtir_produto'),
    path('produtos/curtidos/', produtos_curtidos, name='produtos_curtidos'),
    path('produtos/<int:produto_id>/toggle-curtir/', toggle_curtir_produto, name='toggle_curtir_produto'),



] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



