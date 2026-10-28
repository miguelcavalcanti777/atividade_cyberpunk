"""Cria dados de exemplo (todos FICTÍCIOS) para testar o sistema.

Uso:  python manage.py popular_dados

Pode rodar mais de uma vez: usa get_or_create e não duplica registros.
Todos os usuários criados têm a senha definida em SENHA abaixo (só para estudo!).
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from cyberpunk.models import Cliente, Contrato, Mercenario, Personagem

SENHA = "cyber123"

CLIENTES = [
    ("cli_kurogane", "Diretoria Kurogane", "Kurogane Dynamics"),
    ("cli_lotus", "Madame Lótus", "Sindicato Lótus Neon"),
    ("cli_helix", "Dra. Helix-7", "Helix Biotech Σ"),
]

MERCENARIOS = [
    ("merc_kitsune", "Zero Kitsune", "NETRUNNER", 4),
    ("merc_ronin", "Ronin Pixel", "SOLO", 3),
    ("merc_hana", "Static Hana", "TECNICO", 2),
    ("merc_mikan", "Chrome Mikan", "RASTREADOR", 5),
    ("merc_kaze", "Nova Kaze", "SOLO", 1),
]

PERSONAGENS = [
    ("Dr. Vex Orochi", "O Cirurgião", "Cirurgião clandestino que instala implantes sem licença.", "Setor 9 - Neon Sprawl", 3),
    ("Lady Sable Nine", "Nove-Caudas", "Fixer que vendeu informação das duas pontas e sumiu.", "Torre Zéfiro", 4),
    ("Gaiden Kuro", "Ferro-Velho", "Chefe de uma gangue de sucateiros com exoesqueletos improvisados.", "Porto Quebrado", 4),
    ("Mimi Hologram", "Fantasma-Pop", "IA de idol virtual que escapou de um datacenter corporativo.", "Rede Aberta", 2),
    ("Jax Moreau", "Mão-de-Cromo", "Contrabandista de implantes roubados.", "Mercado Sombra", 3),
    ("Oyabun Tsuru", "O Grou", "Líder de um sindicato do crime que controla as docas flutuantes.", "Docas Flutuantes", 5),
]

# (título, descrição, local, recompensa, perigo, cliente_idx, alvo_idx, merc_idx, status)
CONTRATOS = [
    ("Caça ao Cirurgião", "Localizar e capturar o Dr. Vex Orochi com vida.", "Setor 9 - Neon Sprawl", 12000, 3, 2, 0, None, "ABERTO"),
    ("O Rastro da Raposa", "Recuperar os dados que a Lady Sable Nine vendeu duas vezes.", "Torre Zéfiro", 25000, 4, 0, 1, None, "ABERTO"),
    ("Sucata e Fúria", "Desmontar a operação de Gaiden Kuro no Porto Quebrado.", "Porto Quebrado", 18000, 4, 1, 2, 3, "ACEITO"),
    ("Desligar a Idol", "Capturar a IA Mimi Hologram antes que ela se espalhe pela rede.", "Rede Aberta", 9000, 2, 0, 3, 0, "ACEITO"),
    ("Cromo Roubado", "Interceptar o carregamento de Jax Moreau.", "Mercado Sombra", 7000, 3, 1, 4, 1, "CONCLUIDO"),
    ("Queda do Grou", "Derrubar a rede de contrabando do Oyabun Tsuru.", "Docas Flutuantes", 60000, 5, 1, 5, None, "ABERTO"),
    ("Serviço Cancelado", "Contrato retirado pelo cliente.", "Setor 9 - Neon Sprawl", 3000, 1, 2, 0, None, "CANCELADO"),
    ("Segunda Chance", "Nova tentativa de achar a Mimi Hologram, agora com isca de dados.", "Rede Aberta", 11000, 3, 2, 3, None, "ABERTO"),
]


class Command(BaseCommand):
    help = "Cria clientes, mercenários, personagens e contratos FICTÍCIOS de exemplo."

    def handle(self, *args, **options):
        User = get_user_model()

        clientes = []
        for username, nome, organizacao in CLIENTES:
            usuario, criado = User.objects.get_or_create(username=username)
            if criado:
                usuario.set_password(SENHA)
                usuario.save()
            cliente, _ = Cliente.objects.get_or_create(
                usuario=usuario, defaults={"nome": nome, "organizacao": organizacao}
            )
            clientes.append(cliente)

        mercenarios = []
        for username, codinome, especialidade, nivel in MERCENARIOS:
            usuario, criado = User.objects.get_or_create(username=username)
            if criado:
                usuario.set_password(SENHA)
                usuario.save()
            merc, _ = Mercenario.objects.get_or_create(
                usuario=usuario,
                defaults={"codinome": codinome, "especialidade": especialidade, "nivel": nivel},
            )
            mercenarios.append(merc)

        personagens = []
        for nome, apelido, descricao, distrito, perigo in PERSONAGENS:
            personagem, _ = Personagem.objects.get_or_create(
                nome=nome,
                defaults={
                    "apelido": apelido,
                    "descricao": descricao,
                    "distrito_base": distrito,
                    "periculosidade": perigo,
                    "criado_por": clientes[0],
                },
            )
            personagens.append(personagem)

        for titulo, descricao, local, recompensa, perigo, ci, pi, mi, status in CONTRATOS:
            Contrato.objects.get_or_create(
                titulo=titulo,
                defaults={
                    "descricao": descricao,
                    "local": local,
                    "recompensa": recompensa,
                    "nivel_perigo": perigo,
                    "status": status,
                    "cliente": clientes[ci],
                    "alvo": personagens[pi],
                    "mercenario": mercenarios[mi] if mi is not None else None,
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Pronto: {Cliente.objects.count()} clientes, {Mercenario.objects.count()} "
                f"mercenários, {Personagem.objects.count()} personagens, "
                f"{Contrato.objects.count()} contratos. Senha dos usuários de exemplo: {SENHA}"
            )
        )
