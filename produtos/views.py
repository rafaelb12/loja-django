try:
    from pybrcode.pix import generate_simple_pix
except ModuleNotFoundError:
    generate_simple_pix = None

from django.shortcuts import render, get_object_or_404, redirect
from .models import Produto, Pedido, Categoria, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import ProdutoForm, ProfileForm, CadastroUsuarioForm
from io import BytesIO
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import base64
import pyqrcode
import qrcode


def home(request):
    destaques = Produto.objects.all()[:5]  # pega os 5 primeiros só de exemplo
    return render(request, "produtos/home.html", {"destaques": destaques})


# Cadastro
def cadastrar_usuario(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        if User.objects.filter(username=username).exists():
            return render(request, "produtos/cadastro_usuario.html", {"erro": "Usuário já existe"})

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        return redirect("login_usuario")  # redireciona pelo nome da rota, não pelo HTML

    return render(request, "produtos/cadastro_usuario.html")


# Login
def login_usuario(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # cria a sessão
            return redirect("lista_produtos")  # manda pra página principal
        else:
            return render(request, "produtos/login_usuario.html", {"erro": "Usuário ou senha inválidos"})

    return render(request, "produtos/login_usuario.html")


# Logout
def logout_usuario(request):
    logout(request)  # remove a sessão
    return redirect("lista_produtos")



def lista_produtos(request):
    query = request.GET.get('q', '')  # pega o termo da barra de pesquisa
    produtos = Produto.objects.all()

    if query:
        produtos = produtos.filter(nome__icontains=query)

    return render(request, "produtos/lista.html", {
        "produtos": produtos,
        "query": query
    })

def detalhe_produto(request, id):
    produto = get_object_or_404(Produto, id=id)
    return render(request, "produtos/detalhe.html", {"produto": produto})

def buscar(request):
    query = request.GET.get('q', '')  # pega o valor do input
    categorias = Categoria.objects.all()
    
    if query:
        produtos_filtrados = Produto.objects.filter(nome__icontains=query)
    else:
        produtos_filtrados = Produto.objects.all()

    return render(request, 'produtos/lista.html', {
        'produtos': produtos_filtrados,
        'categorias': categorias,
        'categoria_selecionada': None,
        'query': query
    })
    
def categorias(request):
    return {
        "categorias": Categoria.objects.all()
    }

def sugestoes_produtos(request):
    query = request.GET.get('q', '')
    sugestoes = []

    if query:
        produtos = Produto.objects.filter(nome__icontains=query)[:5]  # limita a 5 resultados
        sugestoes = [{"id": p.id, "nome": p.nome} for p in produtos]

    return JsonResponse(sugestoes, safe=False)

def adicionar_ao_carrinho(request, id):
    produto = get_object_or_404(Produto, id=id)
    carrinho = request.session.get('carrinho', {})

    if str(produto.id) in carrinho:
        carrinho[str(produto.id)]['quantidade'] += 1
    else:
        carrinho[str(produto.id)] = {
            'nome': produto.nome,
            'preco': float(produto.preco),
            'quantidade': 1
        }
    request.session['carrinho'] = carrinho
    return redirect('ver_carrinho')

@login_required
def curtir_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    user = request.user

    if user in produto.curtido_por.all():
        produto.curtido_por.remove(user)  # descurtir
    else:
        produto.curtido_por.add(user)  # curtir

    return redirect(request.META.get('HTTP_REFERER', 'lista_produtos'))

@login_required
def produtos_curtidos(request):
    produtos = request.user.produtos_curtidos.all()
    return render(request, "produtos/curtidos.html", {"produtos": produtos})

@login_required
def toggle_curtir_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)

    if request.user in produto.curtido_por.all():
        produto.curtido_por.remove(request.user)
        curtido = False
    else:
        produto.curtido_por.add(request.user)
        curtido = True

    return JsonResponse({
        "curtido": curtido,
        "total_curtidas": produto.curtido_por.count()
    })

def remover_do_carrinho(request, id):
    carrinho = request.session.get('carrinho', {})
    if str(id) in carrinho:
        del carrinho[str(id)]
    request.session['carrinho'] = carrinho
    return redirect('ver_carrinho')

def atualizar_carrinho(request):
    if request.method == 'POST':
        carrinho = request.session.get('carrinho', {})
        for id, qtd in request.POST.items():
            if id in carrinho:
                carrinho[id]['quantidade'] = int(qtd)
        request.session['carrinho'] = carrinho
    return redirect('ver_carrinho')




def checkout(request):
    carrinho = request.session.get("carrinho", {})
    if not carrinho:
        return redirect("lista_produtos")

    total = 0
    # Calcula subtotal para cada item
    for item in carrinho.values():
        item['subtotal'] = item['preco'] * item['quantidade']
        total += item['subtotal']

    if request.method == "POST":
        user = request.user
        pedido = Pedido.objects.create(
            produtos=carrinho,
            total=total,
            nome_cliente=user.get_full_name() or user.username,
            email_cliente=user.email,
            telefone_cliente="",
        )
        request.session["carrinho"] = {}
        return redirect("pix_pagamento", pedido_id=pedido.id)

    return render(request, "produtos/checkout.html", {"carrinho": carrinho, "total": total})

def ver_carrinho(request):
    carrinho = request.session.get('carrinho', {})
    total = sum(item['preco'] * item['quantidade'] for item in carrinho.values())
    return render(request, 'produtos/carrinho.html', {'carrinho': carrinho, 'total': total})

    
def cadastrar_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_produtos')
    else:
        form = ProdutoForm()
    
    return render(request, 'produtos/cadastrar_produto.html', {'form': form})


def gerar_pix_string(chave_pix, valor, cidade, nome_cliente):
  
    payload = f"00020126360014BR.GOV.BCB.PIX0114{chave_pix}" \
              f"52040000" \
              f"5303986" \
              f"540{valor:.2f}" \
              f"5802BR" \
              f"5910{nome_cliente}" \
              f"6009{cidade}6304"

  
    return payload + "DUMMY"  

def pix_pagamento(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if not pedido.pix_qr:
        if generate_simple_pix is None:
            return HttpResponse("Pagamento Pix indisponível.", status=503)

        chave_pix = "rafaelbsantos364@gmail.com" 
        cidade = "Itapipoca"
        nome_recebedor = "Rafael Bezerra dos Santos"  
        valor = float(pedido.total)  

        pix_string = generate_simple_pix(
            key=chave_pix,
            city=cidade,
            fullname=nome_recebedor,
            value=valor
        )

        qr = qrcode.make(pix_string)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        pix_qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        pedido.pix_chave = chave_pix
        pedido.pix_qr = pix_qr_base64
        pedido.save()

    return render(request, 'produtos/pix_pagamento.html', {'pedido': pedido})

@login_required
def perfil_usuario(request):
    # Cria o profile se não existir
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        profile.telefone = request.POST.get("telefone", profile.telefone)
        profile.endereco = request.POST.get("endereco", profile.endereco)

        # Atualiza a foto se enviada
        if request.FILES.get("foto"):
            profile.foto = request.FILES["foto"]

        profile.save()

    return render(request, "produtos/perfil_usuario.html", {"profile": profile})



@login_required(login_url="/login/")
def checkout(request):
    carrinho = request.session.get("carrinho", {})
    if not carrinho:
        return redirect("lista_produtos")

    total = sum(item["preco"] * item["quantidade"] for item in carrinho.values())

    if request.method == "POST":
        # Usa dados do usuário logado
        user = request.user
        pedido = Pedido.objects.create(
            produtos=carrinho,
            total=total,
            nome_cliente=user.get_full_name() or user.username,
            email_cliente=user.email,
            telefone_cliente="",  # opcional: pode criar campo no perfil do usuário
        )
        request.session["carrinho"] = {}
        return redirect("pix_pagamento", pedido_id=pedido.id)

    return render(request, "produtos/checkout.html", {"carrinho": carrinho, "total": total})

@login_required(login_url="/login/")
def dashboard_usuario(request):
    pedidos = Pedido.objects.filter(email_cliente=request.user.email).order_by('-id')
    return render(request, "produtos/dashboard_usuario.html", {"pedidos": pedidos})

@login_required(login_url="/login/")
def detalhe_pedido(request, pedido_id):
    pedido = Pedido.objects.get(id=pedido_id, email_cliente=request.user.email)
    return render(request, "produtos/detalhe_pedido.html", {"pedido": pedido})

@csrf_exempt
def pix_webhook(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        pedido_id = data.get("pedido_id")
        status = data.get("status")  

        if pedido_id and status == "paid":
            try:
                pedido = Pedido.objects.get(id=pedido_id)
                pedido.pago = True
                pedido.save()
            except Pedido.DoesNotExist:
                pass
        return HttpResponse("OK")
    return HttpResponse("Método não permitido", status=405)


def buscar(request):
    query = request.GET.get('q', '')
    # Aqui você pode implementar a lógica de busca nos produtos
    produtos_filtrados = []  # exemplo vazio por enquanto
    return render(request, 'produtos/lista.html', {'produtos': produtos_filtrados})