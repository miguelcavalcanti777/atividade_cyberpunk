from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Cliente, Contrato, Mercenario, Personagem

User = get_user_model()


class BaseTeste(TestCase):
    def setUp(self):
        self.u_cliente = User.objects.create_user("cli", password="x12345678")
        self.cliente = Cliente.objects.create(usuario=self.u_cliente, nome="Corp Teste")

        self.u_merc1 = User.objects.create_user("m1", password="x12345678")
        self.merc1 = Mercenario.objects.create(
            usuario=self.u_merc1, codinome="Alfa", especialidade="SOLO"
        )
        self.u_merc2 = User.objects.create_user("m2", password="x12345678")
        self.merc2 = Mercenario.objects.create(
            usuario=self.u_merc2, codinome="Beta", especialidade="NETRUNNER"
        )

        self.alvo = Personagem.objects.create(
            nome="Alvo Fictício", descricao="Inventado.", distrito_base="Setor 1"
        )
        self.contrato = Contrato.objects.create(
            titulo="Teste",
            descricao="desc",
            local="Setor 1",
            recompensa=1000,
            cliente=self.cliente,
            alvo=self.alvo,
        )


class PaginasPublicasTest(BaseTeste):
    def test_paginas_publicas_abrem(self):
        for nome, args in [
            ("cyberpunk:home", []),
            ("cyberpunk:contrato_lista", []),
            ("cyberpunk:contrato_detalhe", [self.contrato.pk]),
            ("cyberpunk:personagem_lista", []),
            ("cyberpunk:cadastro", []),
            ("cyberpunk:login", []),
        ]:
            resposta = self.client.get(reverse(nome, args=args))
            self.assertEqual(resposta.status_code, 200, nome)

    def test_lista_mostra_contrato_aberto(self):
        resposta = self.client.get(reverse("cyberpunk:contrato_lista"))
        self.assertContains(resposta, "Teste")


class AceitarConcluirTest(BaseTeste):
    def test_visitante_nao_aceita(self):
        url = reverse("cyberpunk:contrato_aceitar", args=[self.contrato.pk])
        resposta = self.client.post(url)
        self.assertEqual(resposta.status_code, 302)
        self.assertIn("login", resposta.url)
        self.contrato.refresh_from_db()
        self.assertEqual(self.contrato.status, Contrato.ABERTO)

    def test_cliente_nao_aceita(self):
        self.client.login(username="cli", password="x12345678")
        url = reverse("cyberpunk:contrato_aceitar", args=[self.contrato.pk])
        self.assertEqual(self.client.post(url).status_code, 403)

    def test_aceitar_por_get_nao_funciona(self):
        self.client.login(username="m1", password="x12345678")
        url = reverse("cyberpunk:contrato_aceitar", args=[self.contrato.pk])
        self.assertEqual(self.client.get(url).status_code, 405)

    def test_mercenario_aceita_e_segundo_nao_consegue(self):
        url = reverse("cyberpunk:contrato_aceitar", args=[self.contrato.pk])

        self.client.login(username="m1", password="x12345678")
        self.client.post(url)
        self.contrato.refresh_from_db()
        self.assertEqual(self.contrato.status, Contrato.ACEITO)
        self.assertEqual(self.contrato.mercenario, self.merc1)

        self.client.logout()
        self.client.login(username="m2", password="x12345678")
        self.client.post(url)
        self.contrato.refresh_from_db()
        self.assertEqual(self.contrato.mercenario, self.merc1)  # continua sendo do primeiro

    def test_concluir_muda_so_o_status(self):
        self.contrato.mercenario = self.merc1
        self.contrato.status = Contrato.ACEITO
        self.contrato.save()

        self.client.login(username="m1", password="x12345678")
        self.client.post(reverse("cyberpunk:contrato_concluir", args=[self.contrato.pk]))
        self.contrato.refresh_from_db()
        self.assertEqual(self.contrato.status, Contrato.CONCLUIDO)
        self.assertEqual(self.contrato.mercenario, self.merc1)

    def test_outro_mercenario_nao_conclui(self):
        self.contrato.mercenario = self.merc1
        self.contrato.status = Contrato.ACEITO
        self.contrato.save()

        self.client.login(username="m2", password="x12345678")
        resposta = self.client.post(
            reverse("cyberpunk:contrato_concluir", args=[self.contrato.pk])
        )
        self.assertEqual(resposta.status_code, 403)
        self.contrato.refresh_from_db()
        self.assertEqual(self.contrato.status, Contrato.ACEITO)

    def test_nao_conclui_contrato_aberto(self):
        self.contrato.mercenario = self.merc1
        self.contrato.save()  # continua ABERTO

        self.client.login(username="m1", password="x12345678")
        self.client.post(reverse("cyberpunk:contrato_concluir", args=[self.contrato.pk]))
        self.contrato.refresh_from_db()
        self.assertEqual(self.contrato.status, Contrato.ABERTO)


class ClienteTest(BaseTeste):
    def test_cliente_publica_contrato(self):
        self.client.login(username="cli", password="x12345678")
        resposta = self.client.post(
            reverse("cyberpunk:contrato_criar"),
            {
                "titulo": "Novo",
                "descricao": "desc",
                "local": "Setor 2",
                "recompensa": "500.00",
                "nivel_perigo": 2,
                "alvo": self.alvo.pk,
            },
        )
        self.assertEqual(resposta.status_code, 302)
        novo = Contrato.objects.get(titulo="Novo")
        self.assertEqual(novo.cliente, self.cliente)
        self.assertEqual(novo.status, Contrato.ABERTO)

    def test_mercenario_nao_publica(self):
        self.client.login(username="m1", password="x12345678")
        self.assertEqual(self.client.get(reverse("cyberpunk:contrato_criar")).status_code, 403)

    def test_cliente_cancela_contrato_aberto(self):
        self.client.login(username="cli", password="x12345678")
        self.client.post(reverse("cyberpunk:contrato_cancelar", args=[self.contrato.pk]))
        self.contrato.refresh_from_db()
        self.assertEqual(self.contrato.status, Contrato.CANCELADO)


class CadastroTest(TestCase):
    def test_cadastro_de_mercenario_cria_perfil(self):
        resposta = self.client.post(
            reverse("cyberpunk:cadastro"),
            {
                "username": "novo",
                "password1": "senhaForte#2026",
                "password2": "senhaForte#2026",
                "tipo": "mercenario",
                "nome": "Sombra",
                "especialidade": "SOLO",
            },
        )
        self.assertEqual(resposta.status_code, 302)
        self.assertTrue(Mercenario.objects.filter(codinome="Sombra").exists())

    def test_cadastro_de_cliente_cria_perfil(self):
        self.client.post(
            reverse("cyberpunk:cadastro"),
            {
                "username": "novocli",
                "password1": "senhaForte#2026",
                "password2": "senhaForte#2026",
                "tipo": "cliente",
                "nome": "Corp Nova",
                "organizacao": "Nova Inc.",
            },
        )
        self.assertTrue(Cliente.objects.filter(nome="Corp Nova").exists())

    def test_mercenario_exige_especialidade(self):
        self.client.post(
            reverse("cyberpunk:cadastro"),
            {
                "username": "semesp",
                "password1": "senhaForte#2026",
                "password2": "senhaForte#2026",
                "tipo": "mercenario",
                "nome": "SemEsp",
            },
        )
        self.assertFalse(User.objects.filter(username="semesp").exists())


class MeusContratosTest(BaseTeste):
    def test_mercenario_ve_so_os_seus(self):
        self.contrato.mercenario = self.merc1
        self.contrato.status = Contrato.ACEITO
        self.contrato.save()

        self.client.login(username="m1", password="x12345678")
        self.assertContains(self.client.get(reverse("cyberpunk:meus_contratos")), "Teste")

        self.client.logout()
        self.client.login(username="m2", password="x12345678")
        self.assertNotContains(self.client.get(reverse("cyberpunk:meus_contratos")), "Teste")
