"""Fixtures artificiais de contrato; estes testes NÃO executam um LLM."""
import copy
import json
import unittest

from questoes.q12.spike_ollama import validate_response


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.envelope = {"model": "fixture-artificial", "done": True,
                         "message": {"role": "assistant", "content":
                                     '{"intencao":"estudar","duracao_minutos":30}'}}

    def test_known_half_hour(self):
        self.assertEqual(validate_response(self.envelope),
                         {"intencao": "estudar", "duracao_minutos": 30})

    def test_invalid_contents(self):
        for content in ["não JSON", "[]", "null", '{}',
                        '{"intencao":"estudar","duracao_minutos":30,"extra":1}',
                        '{"intencao":"dormir","duracao_minutos":30}']:
            with self.subTest(content=content), self.assertRaises(ValueError):
                self.envelope["message"]["content"] = content
                validate_response(self.envelope)

    def test_invalid_durations(self):
        for duration in [True, False, 0, -1, 30.0, "30", None, 15]:
            with self.subTest(duration=duration), self.assertRaises(ValueError):
                self.envelope["message"]["content"] = json.dumps(
                    {"intencao": "estudar", "duracao_minutos": duration})
                validate_response(self.envelope)

    def test_invalid_envelopes(self):
        cases = [None, [], {}, {**self.envelope, "done": False},
                 {**self.envelope, "model": ""}, {**self.envelope, "message": None}]
        wrong_role = copy.deepcopy(self.envelope)
        wrong_role["message"]["role"] = "user"
        cases.append(wrong_role)
        for envelope in cases:
            with self.subTest(envelope=envelope), self.assertRaises(ValueError):
                validate_response(envelope)


if __name__ == "__main__":
    unittest.main()
