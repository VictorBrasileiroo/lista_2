"""Testes determinísticos e de integração simulada, sem chave ou chamadas reais.

Execute o teste REAL separadamente: python agente.py --demo.
As respostas simuladas abaixo não são evidência de execução do Gemini.
"""

from contextlib import redirect_stdout
from dataclasses import replace
from io import BytesIO, StringIO
from itertools import permutations, product
import json
import http.client
import random
import socket
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch
import urllib.error

import agente
from planejador import (
    Atividade, DadosInvalidos, EsclarecimentoNecessario, RecursoNaoSuportado,
    Intervalo, Pendencia, Plano, Problema, horario, minutos, planejar,
    validar_agenda, validar_dados,
)


def tarefa(identificador, duracao, prioridade="media", prazo="hoje", fixo=None):
    return Atividade(identificador, f"Atividade {identificador}", duracao, prioridade, prazo,
                     *(fixo if fixo else (None, None)))


def cenario_q11():
    return {
        "janela": {"inicio": "14:00", "fim": "18:00"},
        "atividades": [
            {"id": "A", "nome": "Preparar aula de IA", "duracao_minutos": 90,
             "prioridade": "alta", "prazo": "hoje", "inicio_fixo": None, "fim_fixo": None},
            {"id": "B", "nome": "Corrigir trabalhos", "duracao_minutos": 120,
             "prioridade": "media", "prazo": "amanha", "inicio_fixo": None, "fim_fixo": None},
            {"id": "C", "nome": "Reunião de pesquisa", "duracao_minutos": 60,
             "prioridade": "alta", "prazo": "hoje", "inicio_fixo": "16:00", "fim_fixo": "17:00"},
            {"id": "D", "nome": "Revisar artigo", "duracao_minutos": 60,
             "prioridade": "baixa", "prazo": "proxima_semana", "inicio_fixo": None, "fim_fixo": None},
        ],
        "esclarecimentos": [], "recursos_nao_suportados": [],
    }


def metadados_simulados():
    return {"provedor": "Gemini", "modelo_configurado": agente.MODELO_PADRAO,
            "versao_resposta": "simulada", "id_resposta": "simulado", "criado_em": "simulado"}


class TestPlanejador(unittest.TestCase):
    """Unidade: algoritmo e verificador, sem HTTP e sem LLM."""

    def test_agenda_valida_sem_fixos(self):
        problema = Problema(480, 600, (tarefa("B", 40), tarefa("A", 60)))
        plano = planejar(problema)
        self.assertEqual(plano.agenda, (Intervalo("A", 480, 540), Intervalo("B", 540, 580)))
        self.assertFalse(plano.pendentes)
        self.assertEqual(validar_agenda(problema, plano), [])

    def test_compromisso_fixo_e_preservado(self):
        problema = Problema(480, 660, (tarefa("A", 45), tarefa("F", 60, fixo=(540, 600))))
        plano = planejar(problema)
        self.assertIn(Intervalo("F", 540, 600), plano.agenda)
        self.assertEqual(validar_agenda(problema, plano), [])

    def test_rejeita_sobreposicao(self):
        problema = Problema(480, 600, (tarefa("A", 60), tarefa("B", 60)))
        adulterado = Plano((Intervalo("A", 480, 540), Intervalo("B", 510, 570)), ())
        self.assertTrue(any("Sobreposição" in erro for erro in validar_agenda(problema, adulterado)))

    def test_tarefa_maior_que_janela_fica_pendente(self):
        problema = Problema(480, 540, (tarefa("A", 90),))
        plano = planejar(problema)
        self.assertEqual(plano.agenda, ())
        self.assertEqual(plano.pendentes[0].id, "A")
        self.assertIn("excede toda a janela", plano.pendentes[0].motivo)

    def test_nao_divide_tarefa_entre_lacunas(self):
        problema = Problema(480, 660, (tarefa("A", 90), tarefa("F", 60, fixo=(540, 600))))
        plano = planejar(problema)
        self.assertEqual(tuple(i.id for i in plano.agenda), ("F",))
        self.assertIn("nenhum intervalo contínuo", plano.pendentes[0].motivo)

    def test_prazo_hoje_precede_prioridade_alta_amanha(self):
        problema = Problema(480, 540, (tarefa("A", 60, "alta", "amanha"), tarefa("B", 60, "baixa", "hoje")))
        self.assertEqual(planejar(problema).agenda[0].id, "B")

    def test_prioridade_alta_precede_media_no_mesmo_prazo(self):
        problema = Problema(480, 540, (tarefa("A", 60, "media"), tarefa("B", 60, "alta")))
        self.assertEqual(planejar(problema).agenda[0].id, "B")

    def test_duas_da_mesma_categoria_precedem_uma_longa(self):
        problema = Problema(480, 540, (tarefa("A", 60), tarefa("B", 30), tarefa("C", 30)))
        self.assertEqual({i.id for i in planejar(problema).agenda}, {"B", "C"})

    def test_desempate_por_minutos(self):
        problema = Problema(480, 540, (tarefa("A", 40), tarefa("B", 50)))
        self.assertEqual(planejar(problema).agenda[0].id, "B")

    def test_desempate_por_id(self):
        problema = Problema(480, 540, (tarefa("B", 60), tarefa("A", 60)))
        self.assertEqual(planejar(problema).agenda[0].id, "A")

    def test_contagens_nao_sao_utilidade_aditiva(self):
        problema = Problema(480, 600, (tarefa("A", 120, "alta"), tarefa("B", 60, "media"), tarefa("C", 60, "media")))
        self.assertEqual({i.id for i in planejar(problema).agenda}, {"A"})

    def test_busca_reordena_para_encontrar_combinacao_viavel(self):
        # Inserir A primeiro desperdiçaria a lacuna de 60 min e impediria B.
        problema = Problema(480, 720, (tarefa("A", 90, "alta"), tarefa("B", 60, "baixa"),
                                      tarefa("F", 60, fixo=(540, 600))))
        plano = planejar(problema)
        self.assertEqual(plano.agenda, (Intervalo("B", 480, 540), Intervalo("F", 540, 600), Intervalo("A", 600, 690)))

    def test_pendentes_cobrem_exatamente_as_nao_agendadas(self):
        problema = validar_dados(cenario_q11())
        plano = planejar(problema)
        agendadas = {i.id for i in plano.agenda}
        pendentes = {i.id for i in plano.pendentes}
        self.assertFalse(agendadas & pendentes)
        self.assertEqual(agendadas | pendentes, {"A", "B", "C", "D"})

    def test_duracao_incorreta_detectada(self):
        problema = Problema(480, 600, (tarefa("A", 60),))
        self.assertTrue(any("duração incorreta" in e for e in validar_agenda(problema, Plano((Intervalo("A", 480, 530),), ()))))

    def test_reprodutibilidade_e_independencia_da_ordem_textual(self):
        problema = validar_dados(cenario_q11())
        esperado = planejar(problema)
        for ordem in permutations(problema.atividades):
            self.assertEqual(planejar(replace(problema, atividades=ordem)), esperado)

    def test_melhor_vetor_confere_com_enumeracao_independente(self):
        # Oráculo por alocação em recipientes: enumera tarefas pendentes e
        # atribuições às lacunas, sem usar a programação dinâmica da aplicação.
        gerador = random.Random(12)
        prazos = ("hoje", "amanha", "proxima_semana", "sem_prazo")
        prioridades = ("alta", "media", "baixa")
        for caso in range(15):
            flexiveis = tuple(tarefa(chr(65 + i), gerador.randrange(20, 151, 10),
                                      gerador.choice(prioridades), gerador.choice(prazos)) for i in range(5))
            quantidade_fixos = caso % 3
            fixos = (tarefa("F", 30, fixo=(540, 570)), tarefa("G", 30, fixo=(660, 690)))[:quantidade_fixos]
            capacidades = ((300,), (60, 210), (60, 90, 90))[quantidade_fixos]
            melhor_vetor, melhores_ids = None, None
            for alocacao in product(range(-1, len(capacidades)), repeat=len(flexiveis)):
                if any(sum(a.duracao_minutos for a, destino in zip(flexiveis, alocacao) if destino == j) > capacidade
                       for j, capacidade in enumerate(capacidades)):
                    continue
                escolhidas = [a for a, destino in zip(flexiveis, alocacao) if destino >= 0]
                vetor = tuple(sum(a.prazo == prazo and a.prioridade == prioridade for a in escolhidas)
                              for prazo in prazos for prioridade in prioridades)
                vetor += (sum(a.duracao_minutos for a in escolhidas),)
                vetor += tuple(int(destino >= 0) for destino in alocacao)
                if melhor_vetor is None or vetor > melhor_vetor:
                    melhor_vetor, melhores_ids = vetor, {a.id for a in escolhidas}
            problema = Problema(480, 780, flexiveis + fixos)
            plano = planejar(problema)
            with self.subTest(caso=caso):
                self.assertEqual({i.id for i in plano.agenda} - {a.id for a in fixos}, melhores_ids)
                self.assertEqual(validar_agenda(problema, plano), [])

    def test_cenario_completo_q11(self):
        problema = validar_dados(cenario_q11())
        self.assertEqual(sum(a.duracao_minutos for a in problema.atividades), 330)
        self.assertEqual(problema.fim - problema.inicio, 240)
        plano = planejar(problema)
        self.assertEqual(plano.agenda, (Intervalo("A", 840, 930), Intervalo("C", 960, 1020), Intervalo("D", 1020, 1080)))
        self.assertEqual(tuple(p.id for p in plano.pendentes), ("B",))
        self.assertIn("maior intervalo contínuo é de 30 min", plano.pendentes[0].motivo)
        self.assertEqual(validar_agenda(problema, plano), [])

    def test_atividades_inventadas_detectadas(self):
        problema = Problema(480, 600, (tarefa("A", 60),))
        casos = [Plano((Intervalo("X", 480, 540),), (Pendencia("A", "teste"),)),
                 Plano((Intervalo("A", 480, 540),), (Pendencia("X", "teste"),))]
        for caso in casos:
            with self.subTest(caso=caso):
                self.assertTrue(any("inventada" in e for e in validar_agenda(problema, caso)))

    def test_intervalos_fora_da_janela_invertidos_e_nao_inteiros(self):
        problema = Problema(480, 600, (tarefa("A", 60),))
        for intervalo in (Intervalo("A", 460, 520), Intervalo("A", 590, 650),
                          Intervalo("A", 540, 480), Intervalo("A", 480, 480), Intervalo("A", True, 540)):
            with self.subTest(intervalo=intervalo):
                self.assertTrue(validar_agenda(problema, Plano((intervalo,), ())))

    def test_atividade_dividida_repetida_detectada(self):
        problema = Problema(480, 600, (tarefa("A", 60),))
        plano = Plano((Intervalo("A", 480, 510), Intervalo("A", 540, 570)), ())
        self.assertTrue(any("indivisível" in e for e in validar_agenda(problema, plano)))

    def test_fixo_deslocado_ou_pendente_detectado(self):
        problema = Problema(480, 600, (tarefa("F", 30, fixo=(540, 570)),))
        self.assertTrue(any("deslocado" in e for e in validar_agenda(problema, Plano((Intervalo("F", 480, 510),), ()))))
        self.assertTrue(any("não foi reservado" in e for e in validar_agenda(problema, Plano((), (Pendencia("F", "teste"),)))))

    def test_ausencia_e_duplicacao_de_pendencias_detectadas(self):
        problema = Problema(480, 600, (tarefa("A", 60),))
        self.assertTrue(any("ausente" in e for e in validar_agenda(problema, Plano((), ()))))
        casos = [Plano((), (Pendencia("A", "x"), Pendencia("A", "x"))),
                 Plano((Intervalo("A", 480, 540),), (Pendencia("A", "x"),)),
                 Plano((), (Pendencia("A", ""),))]
        for caso in casos:
            with self.subTest(caso=caso):
                self.assertTrue(validar_agenda(problema, caso))

    def test_limites_adjacentes_sao_permitidos(self):
        problema = Problema(480, 600, (tarefa("A", 60), tarefa("F", 60, fixo=(540, 600))))
        self.assertEqual(validar_agenda(problema, planejar(problema)), [])

    def test_fixo_preenche_janela_inteira(self):
        problema = Problema(480, 540, (tarefa("F", 60, fixo=(480, 540)), tarefa("A", 10)))
        plano = planejar(problema)
        self.assertEqual(plano.agenda, (Intervalo("F", 480, 540),))
        self.assertEqual(plano.pendentes[0].id, "A")

    def test_entrada_direta_tambem_e_validada(self):
        casos = [Problema(540, 480, (tarefa("A", 60),)), Problema(480, 600, (tarefa("A", 0),)),
                 Problema(480, 600, (tarefa("A", 30), tarefa("A", 30))),
                 Problema(480, 600, (tarefa("A", 30, fixo=(450, 480)),)),
                 Problema(480, 600, (tarefa("A", 30, fixo=(480, 540)),))]
        for problema in casos:
            with self.subTest(problema=problema), self.assertRaises(DadosInvalidos):
                planejar(problema)


class TestValidacaoDados(unittest.TestCase):
    """Unidade: contrato de extração e restrições de entrada."""

    def test_duracao_ausente_pede_esclarecimento(self):
        dados = cenario_q11()
        dados["atividades"][0]["duracao_minutos"] = None
        with self.assertRaises(EsclarecimentoNecessario) as contexto:
            validar_dados(dados)
        self.assertIn("duração", str(contexto.exception))

    def test_campos_essenciais_nulos_nao_recebem_padrao(self):
        for campo in ("prioridade", "prazo"):
            dados = cenario_q11()
            dados["atividades"][0][campo] = None
            with self.subTest(campo=campo), self.assertRaises(EsclarecimentoNecessario):
                validar_dados(dados)
        dados = cenario_q11()
        dados["janela"]["inicio"] = None
        with self.assertRaises(EsclarecimentoNecessario):
            validar_dados(dados)

    def test_ambiguidades_do_llm_bloqueiam_planejamento(self):
        dados = cenario_q11()
        dados["esclarecimentos"] = ["A reunião é hoje ou amanhã?"]
        with self.assertRaises(EsclarecimentoNecessario):
            validar_dados(dados)

    def test_divisao_solicitada_recebe_erro_claro(self):
        dados = cenario_q11()
        dados["recursos_nao_suportados"] = ["Dividir A em três blocos."]
        with self.assertRaises(RecursoNaoSuportado) as contexto:
            validar_dados(dados)
        self.assertIn("não estão implementados", str(contexto.exception))

    def test_horarios_invalidos(self):
        for valor in ("25:00", "14:60", "14h", "9:00", 1400, True, "14:00\n"):
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                minutos(valor)
        self.assertEqual(horario(minutos("09:05")), "09:05")

    def test_duracoes_invalidas(self):
        for valor in (-1, 0, 1.5, True, "60"):
            dados = cenario_q11()
            dados["atividades"][0]["duracao_minutos"] = valor
            with self.subTest(valor=valor), self.assertRaises(DadosInvalidos):
                validar_dados(dados)

    def test_estrutura_chaves_e_dominios_invalidos(self):
        casos = [[], {}, {**cenario_q11(), "extra": 1}, {**cenario_q11(), "atividades": "A"},
                 {**cenario_q11(), "janela": {}}, {**cenario_q11(), "esclarecimentos": [1]}]
        for campo, valor in (("prioridade", "urgente"), ("prazo", "ontem"), ("nome", ""), ("id", [])):
            dados = cenario_q11()
            dados["atividades"][0][campo] = valor
            casos.append(dados)
        dados = cenario_q11()
        del dados["atividades"][0]["duracao_minutos"]
        casos.append(dados)
        for dados in casos:
            with self.subTest(dados=dados), self.assertRaises(DadosInvalidos):
                validar_dados(dados)

    def test_sem_atividades_pede_esclarecimento(self):
        dados = cenario_q11()
        dados["atividades"] = []
        with self.assertRaises(EsclarecimentoNecessario):
            validar_dados(dados)

    def test_excesso_de_atividades_nao_trunca(self):
        dados = cenario_q11()
        modelo = dados["atividades"][0]
        dados["atividades"] = [{**modelo, "id": f"T{i}"} for i in range(11)]
        with self.assertRaisesRegex(DadosInvalidos, "máximo 10"):
            validar_dados(dados)

    def test_ids_repetidos(self):
        dados = cenario_q11()
        dados["atividades"][1]["id"] = "A"
        with self.assertRaisesRegex(DadosInvalidos, "ID repetido"):
            validar_dados(dados)

    def test_janelas_invalidas(self):
        for inicio, fim in (("18:00", "14:00"), ("14:00", "14:00"), ("14:00", "24:00")):
            dados = cenario_q11()
            dados["janela"] = {"inicio": inicio, "fim": fim}
            with self.subTest(inicio=inicio, fim=fim), self.assertRaises(DadosInvalidos):
                validar_dados(dados)

    def test_fixo_incompleto_incompativel_ou_fora_da_janela(self):
        dados = cenario_q11()
        dados["atividades"][2]["fim_fixo"] = None
        with self.assertRaises(EsclarecimentoNecessario):
            validar_dados(dados)
        for inicio, fim in (("13:00", "14:00"), ("17:00", "16:00"), ("16:00", "16:30")):
            dados = cenario_q11()
            dados["atividades"][2].update(inicio_fixo=inicio, fim_fixo=fim)
            with self.subTest(inicio=inicio, fim=fim), self.assertRaises(DadosInvalidos):
                validar_dados(dados)

    def test_fixos_em_conflito_rejeitados(self):
        dados = cenario_q11()
        dados["atividades"][0].update(inicio_fixo="15:00", fim_fixo="16:30")
        with self.assertRaisesRegex(DadosInvalidos, "se sobrepõem"):
            validar_dados(dados)


class TestConfiguracaoEnv(unittest.TestCase):
    """Configuração local com credenciais fictícias, sem chamadas de rede."""

    def test_formato_bom_comentarios_e_aspas(self):
        with TemporaryDirectory() as pasta, patch.dict("os.environ", {}, clear=True):
            arquivo = Path(pasta) / ".env"
            arquivo.write_text("# comentário\n\nGEMINI_API_KEY = 'chave-ficticia' # comentário\n"
                               'GEMINI_MODEL="modelo-teste"\nGOOGLE_API_KEY=alternativa # comentário\n',
                               encoding="utf-8-sig")
            agente.carregar_env(arquivo)
            self.assertEqual(agente.ClienteGemini()._chave, "chave-ficticia")
            self.assertEqual(agente.ClienteGemini().modelo, "modelo-teste")
            self.assertEqual(agente.os.environ["GOOGLE_API_KEY"], "alternativa")

    def test_env_preenchido_tem_preferencia_sobre_terminal(self):
        with TemporaryDirectory() as pasta, patch.dict("os.environ", {"GEMINI_API_KEY": "terminal"}, clear=True):
            arquivo = Path(pasta) / ".env"
            arquivo.write_text("GEMINI_API_KEY=arquivo\nGEMINI_MODEL=modelo-teste\n", encoding="utf-8")
            agente.carregar_env(arquivo)
            self.assertEqual(agente.ClienteGemini()._chave, "arquivo")
            self.assertEqual(agente.ClienteGemini().modelo, "modelo-teste")

    def test_env_vazio_preserva_chave_do_terminal(self):
        with TemporaryDirectory() as pasta, patch.dict("os.environ", {"GEMINI_API_KEY": "terminal"}, clear=True):
            arquivo = Path(pasta) / ".env"
            arquivo.write_text("GEMINI_API_KEY=\n", encoding="utf-8")
            agente.carregar_env(arquivo)
            self.assertEqual(agente.ClienteGemini()._chave, "terminal")

    def test_arquivo_ausente_e_opcional(self):
        with TemporaryDirectory() as pasta, patch.dict("os.environ", {}, clear=True):
            arquivo = Path(pasta) / ".env"
            agente.carregar_env(arquivo)
            self.assertFalse(arquivo.exists())
            self.assertNotIn("GEMINI_API_KEY", agente.os.environ)

    def test_formato_invalido_nao_exibe_conteudo_nem_carrega_parcialmente(self):
        with TemporaryDirectory() as pasta, patch.dict("os.environ", {}, clear=True):
            arquivo = Path(pasta) / ".env"
            for linha in ("conteudo-confidencial", "GEMINI_MODEL='conteudo-confidencial"):
                arquivo.write_text("GEMINI_API_KEY=chave-ficticia\n" + linha, encoding="utf-8")
                with self.subTest(linha=linha), self.assertRaises(agente.ErroLLM) as contexto:
                    agente.carregar_env(arquivo)
                self.assertNotIn("conteudo-confidencial", str(contexto.exception))
                self.assertNotIn("GEMINI_API_KEY", agente.os.environ)

    def test_cli_carrega_env_ao_lado_do_script(self):
        with TemporaryDirectory() as pasta, patch.dict("os.environ", {}, clear=True):
            (Path(pasta) / ".env").write_text("GEMINI_API_KEY=chave-ficticia\n", encoding="utf-8")
            cliente = Mock()
            cliente.verificar.return_value = {"provedor": "simulado"}
            with patch("agente.__file__", str(Path(pasta) / "agente.py")), \
                    patch("agente.ClienteGemini", return_value=cliente), redirect_stdout(StringIO()):
                self.assertEqual(agente.main(["--diagnostico"]), 0)
            self.assertEqual(agente.os.environ["GEMINI_API_KEY"], "chave-ficticia")
            cliente.verificar.assert_called_once()


class TestIntegracaoSimulada(unittest.TestCase):
    """Fluxo real do programa com HTTP simulado. Não executa um modelo."""

    def setUp(self):
        ambiente = patch.dict("os.environ", {"GEMINI_API_KEY": "chave-simulada", "GEMINI_MODEL": agente.MODELO_PADRAO})
        ambiente.start()
        self.addCleanup(ambiente.stop)
        arquivo_local = patch("agente.carregar_env")
        arquivo_local.start()
        self.addCleanup(arquivo_local.stop)

    @staticmethod
    def resposta_http(objeto):
        resposta = Mock()
        resposta.__enter__ = Mock(return_value=resposta)
        resposta.__exit__ = Mock(return_value=False)
        resposta.read.return_value = json.dumps(objeto, ensure_ascii=False).encode("utf-8")
        return resposta

    @staticmethod
    def envelope(dados=None):
        return {
            "modelVersion": "versao-simulada", "responseId": "id-simulado",
            "candidates": [{"finishReason": "STOP", "content": {"role": "model", "parts": [
                {"text": json.dumps(cenario_q11() if dados is None else dados)}]}}],
        }

    def configurar_http(self, dados=None):
        return [
            self.resposta_http({"name": "models/" + agente.MODELO_PADRAO, "version": "catalogo-simulado",
                                "supportedGenerationMethods": ["generateContent"]}),
            self.resposta_http(self.envelope(dados)),
        ]

    @patch("agente.urllib.request.urlopen")
    def test_fluxo_http_extracao_ferramenta_validacao_e_explicacao(self, abrir):
        abrir.side_effect = self.configurar_http()
        problema, plano, meta = agente.processar(agente.TEXTO_DEMO, agente.ClienteGemini())
        self.assertEqual(validar_agenda(problema, plano), [])
        self.assertEqual(meta["versao_resposta"], "versao-simulada")
        self.assertEqual(meta["id_resposta"], "id-simulado")
        texto = agente.apresentar(problema, plano, meta)
        self.assertIn("14:00 a 15:30 | A. Preparar aula de IA", texto)
        self.assertIn("30 min", texto)
        requisicao = abrir.call_args_list[-1].args[0]
        self.assertEqual(requisicao.full_url, agente.API_URL + "/models/" + agente.MODELO_PADRAO + ":generateContent")
        self.assertEqual(requisicao.get_method(), "POST")
        corpo = json.loads(requisicao.data)
        self.assertEqual(corpo["generationConfig"]["responseJsonSchema"], agente.SCHEMA)
        self.assertEqual(corpo["generationConfig"]["responseMimeType"], "application/json")
        self.assertEqual(corpo["generationConfig"]["temperature"], 0)
        self.assertIn(agente.TEXTO_DEMO, corpo["contents"][0]["parts"][0]["text"])
        self.assertIn(agente.PROMPT_SISTEMA, corpo["systemInstruction"]["parts"][0]["text"])
        self.assertEqual(requisicao.get_header("X-goog-api-key"), "chave-simulada")
        self.assertNotIn("chave-simulada", requisicao.full_url)
        self.assertNotIn("chave-simulada", requisicao.data.decode("utf-8"))
        self.assertEqual(abrir.call_count, 2)

    def test_apresentacao_rejeita_agenda_adulterada(self):
        problema = validar_dados(cenario_q11())
        plano = replace(planejar(problema), agenda=(Intervalo("X", 840, 900),))
        with self.assertRaises(DadosInvalidos):
            agente.apresentar(problema, plano, metadados_simulados())

    def test_nao_chama_ferramenta_com_dados_incompletos(self):
        dados = cenario_q11()
        dados["atividades"][0]["duracao_minutos"] = None
        cliente = Mock()
        cliente.extrair.return_value = (dados, metadados_simulados())
        with patch("agente.planejar") as ferramenta, self.assertRaises(EsclarecimentoNecessario):
            agente.processar("Duração não informada", cliente)
        ferramenta.assert_not_called()

    def test_esclarecimento_interativo_preserva_solicitacao(self):
        incompleto = cenario_q11()
        incompleto["atividades"][0]["duracao_minutos"] = None
        cliente = Mock()
        cliente.extrair.side_effect = [(incompleto, metadados_simulados()), (cenario_q11(), metadados_simulados())]
        with patch("builtins.input", return_value="A dura 90 minutos"), redirect_stdout(StringIO()) as saida:
            self.assertEqual(agente.executar("pedido original", cliente, interativo=True), 0)
        segundo_texto = cliente.extrair.call_args_list[1].args[0]
        self.assertIn("pedido original", segundo_texto)
        self.assertIn("A dura 90 minutos", segundo_texto)
        self.assertIn("São necessários esclarecimentos", saida.getvalue())

    def test_esclarecimentos_limitados_a_tres_chamadas(self):
        incompleto = cenario_q11()
        incompleto["atividades"][0]["duracao_minutos"] = None
        cliente = Mock()
        cliente.extrair.return_value = (incompleto, metadados_simulados())
        with patch("builtins.input", return_value="Não sei"), redirect_stdout(StringIO()):
            self.assertEqual(agente.executar("pedido", cliente, interativo=True), 2)
        self.assertEqual(cliente.extrair.call_count, 3)

    def test_json_malformado_duplicado_e_constante_invalida(self):
        for texto in ("{", '```json\n{}\n```', '{"a": 1, "a": 2}', '{"a": NaN}'):
            with self.subTest(texto=texto), self.assertRaises(agente.ErroLLM):
                agente.carregar_json(texto)

    @patch("agente.urllib.request.urlopen")
    def test_api_indisponivel(self, abrir):
        abrir.side_effect = urllib.error.URLError("conexão recusada")
        with self.assertRaisesRegex(agente.ErroLLM, "indisponível"):
            agente.ClienteGemini().verificar()

    @patch("agente.urllib.request.urlopen")
    def test_modelo_nao_encontrado(self, abrir):
        abrir.side_effect = urllib.error.HTTPError(agente.API_URL, 404, "ausente", {}, BytesIO())
        with self.assertRaisesRegex(agente.ErroLLM, "não encontrado"):
            agente.ClienteGemini(modelo="modelo-ausente").verificar()

    @patch("agente.urllib.request.urlopen")
    def test_timeout_controlado(self, abrir):
        for erro in (socket.timeout("demorou"), urllib.error.URLError(socket.timeout("demorou"))):
            abrir.side_effect = erro
            with self.subTest(erro=erro), self.assertRaisesRegex(agente.ErroLLM, "Timeout"):
                agente.ClienteGemini().verificar()

    @patch("agente.urllib.request.urlopen")
    def test_erro_http_controlado(self, abrir):
        abrir.side_effect = urllib.error.HTTPError("http://localhost", 500, "falha", {}, BytesIO())
        with self.assertRaisesRegex(agente.ErroLLM, "HTTP 500"):
            agente.ClienteGemini().verificar()

    @patch("agente.urllib.request.urlopen")
    def test_protocolo_http_invalido_controlado(self, abrir):
        abrir.side_effect = http.client.BadStatusLine("resposta inválida")
        with self.assertRaisesRegex(agente.ErroLLM, "Falha HTTP"):
            agente.ClienteGemini().verificar()

    @patch("agente.urllib.request.urlopen")
    def test_resposta_incompleta_bloqueada_ou_json_invalido(self, abrir):
        for candidato in ({"finishReason": "MAX_TOKENS"}, {"finishReason": "SAFETY"}, {},
                          {"finishReason": "STOP", "content": None},
                          {"finishReason": "STOP", "content": {"role": "model", "parts": [{"text": "{invalido"}]}},
                          {"finishReason": "STOP", "content": {"role": "model", "parts": [{"functionCall": {}}]}}):
            respostas = self.configurar_http()
            respostas[-1] = self.resposta_http({"candidates": [candidato]})
            abrir.side_effect = respostas
            with self.subTest(candidato=candidato), self.assertRaises(agente.ErroLLM):
                agente.ClienteGemini().extrair("pedido")

    def test_configuracao_por_ambiente_e_padrao(self):
        with patch.dict("os.environ", {"GEMINI_API_KEY": "simulada"}, clear=True):
            self.assertEqual(agente.ClienteGemini().modelo, agente.MODELO_PADRAO)
        with patch.dict("os.environ", {"GEMINI_API_KEY": "simulada", "GEMINI_MODEL": "outro-modelo"}):
            self.assertEqual(agente.ClienteGemini().modelo, "outro-modelo")
        self.assertEqual(agente.ClienteGemini(modelo="models/" + agente.MODELO_PADRAO).modelo, agente.MODELO_PADRAO)

    def test_configuracoes_invalidas(self):
        for configuracao in ({"modelo": ""}, {"modelo": "../modelo"}, {"modelo": "gemini?key=x"},
                             {"timeout": 0}, {"timeout": 601}, {"chave": " "}, {"chave": "chave\ninvalida"}):
            with self.subTest(configuracao=configuracao), self.assertRaises(agente.ErroLLM):
                agente.ClienteGemini(**configuracao)

    @patch("agente.urllib.request.urlopen")
    def test_chave_ausente_nao_acessa_rede(self, abrir):
        with patch.dict("os.environ", {}, clear=True), self.assertRaisesRegex(agente.ErroLLM, "Chave ausente"):
            agente.ClienteGemini()
        abrir.assert_not_called()

    def test_chave_alternativa_e_precedencia_explicita(self):
        with patch.dict("os.environ", {"GOOGLE_API_KEY": "alternativa"}, clear=True):
            self.assertEqual(agente.ClienteGemini()._chave, "alternativa")
        with patch.dict("os.environ", {"GEMINI_API_KEY": "principal", "GOOGLE_API_KEY": "alternativa"}, clear=True):
            self.assertEqual(agente.ClienteGemini()._chave, "principal")

    @patch("agente.urllib.request.urlopen")
    def test_chave_invalida_acesso_negado_e_cota_excedida(self, abrir):
        for codigo in (400, 401, 403, 429):
            abrir.side_effect = urllib.error.HTTPError(agente.API_URL, codigo, "chave-simulada", {}, BytesIO(b'chave-simulada'))
            with self.subTest(codigo=codigo), self.assertRaisesRegex(agente.ErroLLM, f"HTTP {codigo}") as contexto:
                agente.ClienteGemini().verificar()
            self.assertNotIn("chave-simulada", str(contexto.exception))
        self.assertEqual(abrir.call_count, 4)

    @patch("agente.urllib.request.urlopen")
    def test_http_400_exibe_causa_e_etapa_sem_culpar_chave(self, abrir):
        mensagem = "Invalid JSON payload received. Unknown name responseJsonSchema."
        erro = urllib.error.HTTPError(agente.API_URL, 400, "Bad Request", {},
                                      BytesIO(json.dumps({"error": {"message": mensagem}}).encode()))
        abrir.side_effect = [self.configurar_http()[0], erro]
        with self.assertRaises(agente.ErroLLM) as contexto:
            agente.ClienteGemini().extrair("pedido")
        self.assertIn("HTTP 400 na extração JSON", str(contexto.exception))
        self.assertIn(mensagem, str(contexto.exception))
        self.assertNotIn("chave inválida", str(contexto.exception))

    @patch("agente.urllib.request.urlopen")
    def test_erro_de_chave_identificado_sem_expor_credencial(self, abrir):
        corpo = {"error": {"message": "API key not valid: chave-simulada e AIzaCHAVEFICTICIA",
                            "details": [{"reason": "API_KEY_INVALID"}]}}
        abrir.side_effect = urllib.error.HTTPError(agente.API_URL, 400, "Bad Request", {},
                                                   BytesIO(json.dumps(corpo).encode()))
        with self.assertRaises(agente.ErroLLM) as contexto:
            agente.ClienteGemini().verificar()
        texto = str(contexto.exception)
        self.assertIn("a API recusou a chave", texto)
        self.assertIn("[CHAVE OCULTA]", texto)
        self.assertNotIn("chave-simulada", texto)
        self.assertNotIn("AIzaCHAVEFICTICIA", texto)

    @patch("agente.urllib.request.urlopen")
    def test_resposta_sem_candidatos_ou_bloqueada(self, abrir):
        for resposta in ({}, {"candidates": []}, {"promptFeedback": {"blockReason": "SAFETY"}}):
            respostas = self.configurar_http()
            respostas[-1] = self.resposta_http(resposta)
            abrir.side_effect = respostas
            with self.subTest(resposta=resposta), self.assertRaises(agente.ErroLLM):
                agente.ClienteGemini().extrair("pedido")

    @patch("agente.urllib.request.urlopen")
    def test_partes_de_thinking_sao_ignoradas(self, abrir):
        envelope = self.envelope()
        envelope["candidates"][0]["content"]["parts"].insert(0, {"thought": True, "text": "Não é JSON nem explicação."})
        respostas = self.configurar_http()
        respostas[-1] = self.resposta_http(envelope)
        abrir.side_effect = respostas
        problema, plano, meta = agente.processar("pedido", agente.ClienteGemini())
        self.assertNotIn("Não é JSON nem explicação", agente.apresentar(problema, plano, meta))

    @patch("agente.urllib.request.urlopen")
    def test_metadados_de_modelo_invalidos(self, abrir):
        for registro in ({}, {"name": "models/outro", "supportedGenerationMethods": ["generateContent"]},
                         {"name": "models/" + agente.MODELO_PADRAO, "supportedGenerationMethods": ["embedContent"]}):
            abrir.side_effect = [self.resposta_http(registro)]
            with self.subTest(registro=registro), self.assertRaises(agente.ErroLLM):
                agente.ClienteGemini().verificar()

    @patch("agente.urllib.request.urlopen")
    def test_diagnostico_nao_faz_inferencia_nem_exibe_chave(self, abrir):
        abrir.side_effect = self.configurar_http()[:1]
        with redirect_stdout(StringIO()) as saida:
            self.assertEqual(agente.main(["--diagnostico"]), 0)
        self.assertEqual(abrir.call_count, 1)
        self.assertEqual(abrir.call_args.args[0].get_method(), "GET")
        self.assertNotIn("chave-simulada", saida.getvalue())
        self.assertIn("não comprova cota", saida.getvalue())

    @patch("agente.urllib.request.urlopen")
    def test_cli_demo_usa_extracao_em_vez_de_agenda_fixa(self, abrir):
        dados = cenario_q11()
        dados["atividades"] = [dados["atividades"][3]]
        abrir.side_effect = self.configurar_http(dados)
        with redirect_stdout(StringIO()) as saida:
            self.assertEqual(agente.main(["--demo"]), 0)
        self.assertIn("14:00 a 15:00 | D. Revisar artigo", saida.getvalue())
        self.assertNotIn("14:00 a 15:30 | A.", saida.getvalue())

    def test_cli_falha_sem_mensagem_de_sucesso(self):
        cliente = Mock()
        cliente.extrair.side_effect = agente.ErroLLM("API indisponível")
        with patch("agente.ClienteGemini", return_value=cliente), redirect_stdout(StringIO()) as saida:
            self.assertEqual(agente.main(["--texto", "pedido"]), 1)
        self.assertIn("Falha de integração", saida.getvalue())
        self.assertNotIn("Agenda proposta", saida.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
