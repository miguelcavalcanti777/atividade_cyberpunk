from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "cyberpunk"

urlpatterns = [
    path("", views.home, name="home"),
    # contratos
    path("contratos/", views.contrato_lista, name="contrato_lista"),
    path("contratos/novo/", views.contrato_criar, name="contrato_criar"),
    path("contratos/<int:pk>/", views.contrato_detalhe, name="contrato_detalhe"),
    path("contratos/<int:pk>/aceitar/", views.contrato_aceitar, name="contrato_aceitar"),
    path("contratos/<int:pk>/concluir/", views.contrato_concluir, name="contrato_concluir"),
    path("contratos/<int:pk>/cancelar/", views.contrato_cancelar, name="contrato_cancelar"),
    path("meus-contratos/", views.meus_contratos, name="meus_contratos"),
    # personagens (alvos fictícios)
    path("personagens/", views.personagem_lista, name="personagem_lista"),
    path("personagens/novo/", views.personagem_criar, name="personagem_criar"),
    # contas
    path("cadastro/", views.cadastro, name="cadastro"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="cyberpunk/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
