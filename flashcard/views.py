from django.shortcuts import render, redirect
from .models import Categoria, Flashcard
from django.http import HttpResponse
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