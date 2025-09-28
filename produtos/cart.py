def adicionar_ao_carrinho(request, id):
    produto = get_object_or_404(Produto, id=id)
    carrinho = request.session.get('carrinho', {})
    
    if str(produto.id) in carrinho:
        carrinho[str(produto.id)]['quantidade'] += 1
    else:
        carrinho[str(produto.id)] = {'nome': produto.nome, 'preco': float(produto.preco), 'quantidade': 1}
    
    request.session['carrinho'] = carrinho
    return redirect('lista_produtos')

def ver_carrinho(request):
    carrinho = request.session.get('carrinho', {})
    total = sum(item['preco'] * item['quantidade'] for item in carrinho.values())
    return render(request, 'produtos/carrinho.html', {'carrinho': carrinho, 'total': total})
