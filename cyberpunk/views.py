from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CadastroForm, ContratoForm, PersonagemForm
from .models import Contrato, Mercenario, Personagem


def apenas(tipo):
    """Exige login E um perfil do tipo certo ("mercenario" ou "cliente").

    Quem está logado mas é do tipo errado recebe 403 (acesso negado).
    """

    def decorator(view):
        @login_required
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if not hasattr(request.user, tipo):
                raise PermissionDenied
            return view(request, *args, **kwargs)

        return wrapper

    return decorator


# ---------------------------------------------------------------- páginas públicas


def home(request):
    contexto = {
        "total_abertos": Contrato.objects.filter(status=Contrato.ABERTO).count(),
        "total_concluidos": Contrato.objects.filter(status=Contrato.CONCLUIDO).count(),
        "total_mercenarios": Mercenario.objects.count(),
        "destaques": Contrato.objects.filter(status=Contrato.ABERTO)
        .select_related("cliente", "alvo")
        .order_by("-recompensa")[:3],
    }
    return render(request, "cyberpunk/home.html", contexto)


def contrato_lista(request):
    status = request.GET.get("status", Contrato.ABERTO)
    contratos = Contrato.objects.select_related("cliente", "alvo", "mercenario")
    if status in dict(Contrato.STATUS):
        contratos = contratos.filter(status=status)
    else:
        status = "TODOS"

    contexto = {
        "contratos": contratos,
        "status_atual": status,
        "opcoes_status": [("TODOS", "Todos")] + Contrato.STATUS,
    }
    return render(request, "cyberpunk/contrato_lista.html", contexto)


def contrato_detalhe(request, pk):
    contrato = get_object_or_404(
        Contrato.objects.select_related("cliente", "alvo", "mercenario"), pk=pk
    )
    return render(request, "cyberpunk/contrato_detalhe.html", {"contrato": contrato})


def personagem_lista(request):
    personagens = Personagem.objects.all()
    return render(request, "cyberpunk/personagem_lista.html", {"personagens": personagens})


def cadastro(request):
    if request.user.is_authenticated:
        return redirect("cyberpunk:home")

    if request.method == "POST":
        form = CadastroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, "Cadastro concluído. Bem-vindo à rede.")
            return redirect("cyberpunk:home")
    else:
        form = CadastroForm()
    return render(request, "cyberpunk/cadastro.html", {"form": form})


# ---------------------------------------------------------------- cliente


@apenas("cliente")
def contrato_criar(request):
    if request.method == "POST":
        form = ContratoForm(request.POST)
        if form.is_valid():
            contrato = form.save(commit=False)
            contrato.cliente = request.user.cliente
            contrato.save()
            messages.success(request, "Contrato publicado.")
            return redirect("cyberpunk:contrato_detalhe", pk=contrato.pk)
    else:
        form = ContratoForm()
    return render(
        request,
        "cyberpunk/formulario.html",
        {"form": form, "titulo": "Publicar contrato", "botao": "Publicar"},
    )


@apenas("cliente")
def personagem_criar(request):
    if request.method == "POST":
        form = PersonagemForm(request.POST)
        if form.is_valid():
            personagem = form.save(commit=False)
            personagem.criado_por = request.user.cliente
            personagem.save()
            messages.success(request, "Personagem fictício criado.")
            return redirect("cyberpunk:personagem_lista")
    else:
        form = PersonagemForm()
    return render(
        request,
        "cyberpunk/formulario.html",
        {
            "form": form,
            "titulo": "Novo personagem",
            "aviso": "Crie apenas personagens inventados do universo do jogo.",
            "botao": "Criar personagem",
        },
    )


@require_POST
@apenas("cliente")
def contrato_cancelar(request, pk):
    contrato = get_object_or_404(Contrato, pk=pk)
    if contrato.cliente != request.user.cliente:
        raise PermissionDenied
    if contrato.status != Contrato.ABERTO:
        messages.error(request, "Só é possível cancelar contratos abertos.")
    else:
        contrato.status = Contrato.CANCELADO
        contrato.save(update_fields=["status"])
        messages.success(request, "Contrato cancelado.")
    return redirect("cyberpunk:meus_contratos")


# ---------------------------------------------------------------- mercenário


@require_POST
@apenas("mercenario")
def contrato_aceitar(request, pk):
    # transaction + select_for_update: se dois mercenários clicarem ao mesmo tempo,
    # só um consegue (o outro vê o contrato já aceito).
    with transaction.atomic():
        contrato = get_object_or_404(Contrato.objects.select_for_update(), pk=pk)
        if contrato.status != Contrato.ABERTO:
            messages.error(request, "Este contrato não está mais aberto.")
            return redirect("cyberpunk:contrato_detalhe", pk=pk)
        contrato.mercenario = request.user.mercenario
        contrato.status = Contrato.ACEITO
        contrato.save(update_fields=["mercenario", "status"])
    messages.success(request, "Contrato aceito. Boa caçada, mercenário.")
    return redirect("cyberpunk:meus_contratos")


@require_POST
@apenas("mercenario")
def contrato_concluir(request, pk):
    contrato = get_object_or_404(Contrato, pk=pk)
    if contrato.mercenario != request.user.mercenario:
        raise PermissionDenied
    if contrato.status != Contrato.ACEITO:
        messages.error(request, "Só contratos aceitos podem ser concluídos.")
    else:
        contrato.status = Contrato.CONCLUIDO
        contrato.save(update_fields=["status"])
        messages.success(request, "Missão concluída.")
    return redirect("cyberpunk:meus_contratos")


# ---------------------------------------------------------------- área logada


@login_required
def meus_contratos(request):
    base = Contrato.objects.select_related("cliente", "alvo", "mercenario")
    if hasattr(request.user, "mercenario"):
        tipo = "mercenario"
        contratos = base.filter(mercenario=request.user.mercenario)
    elif hasattr(request.user, "cliente"):
        tipo = "cliente"
        contratos = base.filter(cliente=request.user.cliente)
    else:
        tipo = None  # ex.: superusuário sem perfil
        contratos = base.none()
    return render(
        request, "cyberpunk/meus_contratos.html", {"contratos": contratos, "tipo": tipo}
    )
