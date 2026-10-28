from django.contrib import admin

from .models import Cliente, Contrato, Mercenario, Personagem


@admin.register(Mercenario)
class MercenarioAdmin(admin.ModelAdmin):
    list_display = ("codinome", "especialidade", "nivel", "disponivel", "usuario")
    list_filter = ("especialidade", "disponivel")
    search_fields = ("codinome",)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nome", "organizacao", "usuario")
    search_fields = ("nome", "organizacao")


@admin.register(Personagem)
class PersonagemAdmin(admin.ModelAdmin):
    list_display = ("nome", "apelido", "distrito_base", "periculosidade")
    list_filter = ("periculosidade",)
    search_fields = ("nome", "apelido")


@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "cliente", "alvo", "mercenario", "recompensa", "status")
    list_filter = ("status", "nivel_perigo")
    search_fields = ("titulo", "local")
