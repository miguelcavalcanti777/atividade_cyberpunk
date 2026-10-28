from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Mercenario(models.Model):
    """Perfil de quem aceita contratos. Ligado 1:1 a um usuário de login."""

    ESPECIALIDADES = [
        ("NETRUNNER", "Netrunner"),
        ("SOLO", "Solo"),
        ("TECNICO", "Técnico"),
        ("RASTREADOR", "Rastreador"),
    ]

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mercenario"
    )
    codinome = models.CharField(max_length=50, unique=True)
    especialidade = models.CharField(max_length=20, choices=ESPECIALIDADES)
    nivel = models.IntegerField(default=1)
    disponivel = models.BooleanField(default=True)
    data_cadastro = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["codinome"]

    def __str__(self):
        return f"{self.codinome} ({self.get_especialidade_display()})"


class Cliente(models.Model):
    """Perfil de quem publica contratos (corporação, gangue ou fixer FICTÍCIO)."""

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cliente"
    )
    nome = models.CharField("nome fictício", max_length=100)
    organizacao = models.CharField("organização", max_length=100, blank=True)
    descricao = models.TextField("descrição", blank=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        if self.organizacao:
            return f"{self.nome} ({self.organizacao})"
        return self.nome


class Personagem(models.Model):
    """Alvo de um contrato. Sempre um personagem INVENTADO do universo do jogo."""

    nome = models.CharField(max_length=100)
    apelido = models.CharField(max_length=50, blank=True)
    descricao = models.TextField("descrição")
    distrito_base = models.CharField("distrito base", max_length=100)
    periculosidade = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    criado_por = models.ForeignKey(
        Cliente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="personagens_criados",
    )

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        if self.apelido:
            return f'{self.nome} "{self.apelido}"'
        return self.nome


class Contrato(models.Model):
    ABERTO = "ABERTO"
    ACEITO = "ACEITO"
    CONCLUIDO = "CONCLUIDO"
    CANCELADO = "CANCELADO"
    STATUS = [
        (ABERTO, "Aberto"),
        (ACEITO, "Aceito"),
        (CONCLUIDO, "Concluído"),
        (CANCELADO, "Cancelado"),
    ]

    titulo = models.CharField("título", max_length=150)
    descricao = models.TextField("descrição")
    local = models.CharField(max_length=100)
    recompensa = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]
    )
    nivel_perigo = models.IntegerField(
        "nível de perigo", default=1, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    status = models.CharField(max_length=15, choices=STATUS, default=ABERTO)
    data_criacao = models.DateTimeField(auto_now_add=True)

    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="contratos")
    alvo = models.ForeignKey(Personagem, on_delete=models.PROTECT, related_name="contratos")
    mercenario = models.ForeignKey(
        Mercenario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contratos",
    )

    class Meta:
        ordering = ["-data_criacao"]

    def __str__(self):
        return f"{self.titulo} [{self.get_status_display()}]"
