from django.shortcuts import render, redirect
from .models import Categoria, Flashcard, Desafio, FlashcardDesafio
from django.http import HttpResponse, Http404
from django.contrib.messages import constants
from django.contrib import messages

def novo_flashcard(request):
    # verificando se usuário está logado.
    if not request.user.is_authenticated:
        return redirect('/usuarios/logar/')
    
    if request.method == "GET": # user acessa a página no navegador
        categorias = Categoria.objects.all()
        dificuldades = Flashcard.DIFICULDADE_CHOICES
        flashcards = Flashcard.objects.filter(user=request.user) #retorna os cards do user logado

        categoria_filtrar = request.GET.get('categoria')
        dificuldade_filtrar = request.GET.get('dificuldade')

        if categoria_filtrar:
            flashcards = flashcards.filter(categoria__id=categoria_filtrar) # por ser chave estrangeira (foreign key) 

        if dificuldade_filtrar:
            flashcards = flashcards.filter(dificuldade=dificuldade_filtrar)

        # direcionando e passando os dados categoria para o front{}
        return render(request, 'novo_flashcard.html', {'categorias': categorias, 
                                                       'dificuldades': dificuldades,
                                                       'flashcards': flashcards})
    
    elif request.method =="POST":
        pergunta = request.POST.get('pergunta')
        resposta = request.POST.get('resposta')
        categoria = request.POST.get('categoria')
        dificuldade = request.POST.get('dificuldade')
        
        if len(pergunta.strip()) == 0 or len(resposta.strip()) == 0: # apaga espaço em branco no inicio
            messages.add_message(request, constants.ERROR, "Preencha os campos pergunta e resposta.")
            return redirect('/flashcard/novo_flashcard/')
        
        flashcard = Flashcard(
            user = request.user,
            pergunta = pergunta,
            resposta = resposta,
            categoria_id = categoria,
            dificuldade = dificuldade,
        )

        flashcard.save()

        messages.add_message(request, constants.SUCCESS, "Flascard cadastrado com sucesso.")
        return redirect('/flashcard/novo_flashcard')
    
def deletar_flashcard(request, id):
    # Fazer a validação de segurança (request.user)
    flashcard = Flashcard.objects.get(id=id) # get usa para chave primária retorna apenas um valor
    flashcard.delete()
    messages.add_message(
        request, constants.SUCCESS, 'Flashcard deletado com sucesso!'
    )
    return redirect('/flashcard/novo_flashcard/')

def iniciar_desafio(request):
    if request.method =="GET":
        categorias = Categoria.objects.all()
        dificuldades = Flashcard.DIFICULDADE_CHOICES
        return render(request, 'iniciar_desafio.html', {'categorias':categorias,
                                                         'dificuldades':dificuldades})
    elif request.method == "POST":
        titulo = request.POST.get('titulo')
        categorias = request.POST.getlist('categoria') # lista de categoria
        dificuldade = request.POST.get('dificuldade')
        qtd_perguntas = request.POST.get('qtd_perguntas')

        desafio = Desafio(
            user = request.user,
            titulo = titulo,
            quantidade_perguntas = qtd_perguntas,
            dificuldade = dificuldade,
        )

        desafio.save()

        desafio.categoria.add(*categorias) # add todas categorias da lista acima
        # for categoria in categorias:
        #     desafio.categoria.add(categoria)

        flashcards = (
        Flashcard.objects.filter(user=request.user)
            .filter(dificuldade=dificuldade)
            .filter(categoria_id__in=categorias) # filtra as categorias daa lista de categorias
            .order_by('?') # colocando forma aleatório
        )
        
        if flashcards.count() < int(qtd_perguntas):
            # Tratar para escolher depois
            return redirect('/flashcard/iniciar_desafio/')
        
        flashcards = flashcards[:int(qtd_perguntas)] # pegando a quantidade de perguntas desejadas

        for f in flashcards:
            flashcard_desafio = FlashcardDesafio(
                flashcard = f,
            )
            flashcard_desafio.save()
            desafio.flashcards.add(flashcard_desafio)
        
        desafio.save()

        return redirect(f'/flashcard/listar_desafio/')
    
def listar_desafio(request):
    desafios = Desafio.objects.filter(user=request.user)
    # Desenvolver os status (fazer)
    # Desenvolver os filtros (fazer)
    return render(request, 'listar_desafio.html', {'desafios': desafios})
    
def desafio(request, id):    
    desafio = Desafio.objects.get(id=id)
    
    if not desafio.user == request.user:
        raise Http404 # página de erro
    
    if request.method == "GET":
        acertos = desafio.flashcards.filter(respondido=True).filter(acertou=True).count()
        erros = desafio.flashcards.filter(respondido=True).filter(acertou=False).count()
        faltantes = desafio.flashcards.filter(respondido=False).count()
        return render(request, 'desafio.html', {'desafio': desafio, 'acertos': acertos,
                                                 'erros': erros, 'faltantes': faltantes})
    
    return HttpResponse(id)

def responder_flashcard(request, id):
    flashcard_desafio = FlashcardDesafio.objects.get(id=id)
    acertou = request.GET.get('acertou')
    desafio_id = request.GET.get('desafio_id')
    # Verificação de user
    if not flashcard_desafio.flashcard.user == request.user:
        raise Http404() # Página não encontrada

    flashcard_desafio.respondido = True
    flashcard_desafio.acertou = True if acertou == '1' else False
    flashcard_desafio.save()

    return redirect(f'/flashcard/desafio/{desafio_id}/')

def relatorio(request, id):
    desafio = Desafio.objects.get(id=id)
    # filtrando os acertos e erros
    acertos = desafio.flashcards.filter(acertou=True).count()
    erros = desafio.flashcards.filter(acertou=False).count()

    dados = [acertos, erros] # tornando uma lista

    # Gráfico radar
    # buscando as categorias selecionadas
    categorias = desafio.categoria.all()
    name_categoria = [i.nome for i in categorias] # percorre categorias e faz um lista com os elementos
    
    dados2 = []
    for categoria in categorias:
        dados2.append(desafio.flashcards.filter(flashcard__categoria=categoria).filter(acertou=True).count())

    # TODO: Fazer o Ranking

    return render(request, 'relatorio.html', {'desafio': desafio, 'dados': dados, 'categorias':name_categoria, 'dados2': dados2})