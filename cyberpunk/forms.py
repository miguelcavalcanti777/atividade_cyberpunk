from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from .models import Cliente, Contrato, Mercenario, Personagem


class CadastroForm(UserCreationForm):
    """Cadastro de usuário: o visitante escolhe se entra como Mercenário ou Cliente."""

    TIPOS = [("mercenario", "Mercenário"), ("cliente", "Cliente")]

    tipo = forms.ChoiceField(label="Quem é você?", choices=TIPOS, widget=forms.RadioSelect)
    nome = forms.CharField(
        label="Codinome (mercenário) ou nome fictício (cliente)", max_length=100
    )
    especialidade = forms.ChoiceField(
        label="Especialidade (só mercenário)",
        choices=[("", "---------")] + Mercenario.ESPECIALIDADES,
        required=False,
    )
    organizacao = forms.CharField(
        label="Organização (só cliente)", max_length=100, required=False
    )

    def clean(self):
        dados = super().clean()
        tipo = dados.get("tipo")
        nome = (dados.get("nome") or "").strip()

        if tipo == "mercenario":
            if not dados.get("especialidade"):
                self.add_error("especialidade", "Escolha uma especialidade.")
            if nome and Mercenario.objects.filter(codinome__iexact=nome).exists():
                self.add_error("nome", "Esse codinome já está em uso.")
        return dados

    @transaction.atomic
    def save(self, commit=True):
        usuario = super().save(commit=True)
        nome = self.cleaned_data["nome"].strip()

        if self.cleaned_data["tipo"] == "mercenario":
            Mercenario.objects.create(
                usuario=usuario,
                codinome=nome,
                especialidade=self.cleaned_data["especialidade"],
            )
        else:
            Cliente.objects.create(
                usuario=usuario,
                nome=nome,
                organizacao=self.cleaned_data.get("organizacao", "").strip(),
            )
        return usuario


class PersonagemForm(forms.ModelForm):
    class Meta:
        model = Personagem
        fields = ["nome", "apelido", "descricao", "distrito_base", "periculosidade"]
        widgets = {"descricao": forms.Textarea(attrs={"rows": 4})}


class ContratoForm(forms.ModelForm):
    class Meta:
        model = Contrato
        fields = ["titulo", "descricao", "local", "recompensa", "nivel_perigo", "alvo"]
        widgets = {"descricao": forms.Textarea(attrs={"rows": 5})}
        help_texts = {
            "alvo": "O alvo precisa ser um personagem fictício. Não existe na lista? Crie em Personagens.",
            "nivel_perigo": "De 1 (tranquilo) a 5 (suicida).",
        }
