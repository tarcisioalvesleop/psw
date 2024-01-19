from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import Apostila, ViewApostila
from django.contrib.messages import constants
from django.contrib import messages

# Create your views here.
def adicionar_apostilas(request):
    if request.method == "GET":
        apostilas = Apostila.objects.filter(user=request.user)

        views_totais = ViewApostila.objects.filter(apostila__user=request.user).count() #apostila__user (foreignkey)
        return render(request, 'adicionar_apostilas.html', {'apostilas': apostilas, 'views_totais': views_totais})
    elif request.method == "POST":
        titulo = request.POST.get('titulo')
        arquivo = request.FILES['arquivo'] #pegando o arquivo

        apostila = Apostila(
            user = request.user,
            titulo = titulo,
            arquivo = arquivo,
        )

        apostila.save()
        messages.add_message(request, constants.SUCCESS, 'Salvo com sucesso.')
        return redirect('/apostilas/adicionar_apostilas')
        