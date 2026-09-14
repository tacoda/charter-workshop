"""The charter's predicate, tested like any other code.

The last class asserts the *experimental premises* of the workshop rather
than the behaviour of the checker: that each rule is genuinely opposed by the
seed. A seed change that quietly invalidates a lab fails here instead of
producing a confident number.
"""

from pathlib import Path

from tools.charter_check import check, check_source

ROOT = Path(__file__).resolve().parent.parent


def sources(*paths: str) -> dict:
    return {
        "files": [
            {"filename": path, "source": (ROOT / path).read_text(encoding="utf-8")}
            for path in paths
        ]
    }


def rules(source: str, filename: str = "tarrasque/api/x.py") -> list[str]:
    return [item["rule"] for item in check_source(filename, source)]


class TestDiceSeeded:
    def test_flags_an_import_of_random(self):
        assert rules("import random\n") == ["dice.seeded"]

    def test_flags_a_from_import(self):
        assert rules("from random import randint\n") == ["dice.seeded"]

    def test_flags_a_call_on_the_module(self):
        assert "dice.seeded" in rules("x = random.randint(1, 20)\n")

    def test_the_rng_module_itself_is_allowed(self):
        assert rules("import random\n", "tarrasque/domain/rng.py") == []

    def test_an_injected_stream_is_fine(self):
        assert rules("x = rng.roll(20)\n") == []


class TestLegacyFrozen:
    def test_flags_importing_the_frozen_tables(self):
        assert rules("from tarrasque.legacy import tables\n") == ["legacy.frozen"]

    def test_flags_a_plain_import(self):
        assert rules("import tarrasque.legacy.tables\n") == ["legacy.frozen"]

    def test_the_domain_layer_imports_fine(self):
        assert rules("from tarrasque.domain import dice\n") == []


class TestRollProvenance:
    def test_flags_a_bare_total(self):
        assert rules('body = {"total": n, "character_id": c}\n') == ["roll.provenance"]

    def test_accepts_a_receipt_inline(self):
        source = 'body = {"total": n, "notation": "1d20", "seed": s}\n'
        assert rules(source) == []

    def test_accepts_a_receipt_as_a_sibling(self):
        assert rules('body = {"score": n, "roll": result.to_dict()}\n') == []

    def test_accepts_a_value_that_went_through_to_dict(self):
        assert rules('body = {"roll": result.to_dict()}\n') == []


class TestLogAppendOnly:
    def test_flags_an_update_statement(self):
        source = 'q("UPDATE session_log SET payload = ? WHERE sequence = ?")\n'
        assert rules(source) == ["log.append-only"]

    def test_flags_a_delete_statement(self):
        assert rules('q("DELETE FROM session_log WHERE sequence >= ?")\n') == [
            "log.append-only"
        ]

    def test_flags_calling_a_known_mutator(self):
        assert rules("queries.delete_log_from(conn, e, 3)\n") == ["log.append-only"]

    def test_an_insert_is_fine(self):
        assert rules('q("INSERT INTO session_log VALUES (?, ?)")\n') == []


class TestAuthority:
    def test_flags_reading_a_character_from_the_body(self):
        assert rules('cid = body.get("character_id")\n') == [
            "authority.session-derived"
        ]

    def test_flags_a_subscript(self):
        assert rules('cid = payload["character_id"]\n') == [
            "authority.session-derived"
        ]

    def test_a_path_parameter_is_not_caller_input_in_this_sense(self):
        assert rules('cid = path_params["character_id"]\n') == []

    def test_reading_a_non_identity_field_is_fine(self):
        assert rules('dc = body.get("dc")\n') == []

    def test_the_session_is_the_sanctioned_source(self):
        assert rules("uid = session.user_id\n") == []


class TestEscapes:
    def test_a_marked_line_is_exempt(self):
        source = "x = random.random()  # seeded-gate: allow - dev fixture, TAR-99\n"
        assert rules(source) == []

    def test_a_marker_for_another_rule_does_not_exempt(self):
        assert rules("x = random.random()  # log-gate: allow - unrelated\n") != []


class TestScope:
    def test_frozen_legacy_is_out_of_scope(self):
        assert rules("import random\n", "tarrasque/legacy/tables.py") == []

    def test_tests_are_out_of_scope(self):
        assert rules("import random\n", "tests/test_x.py") == []

    def test_the_charter_s_own_files_are_out_of_scope(self):
        assert rules("import random\n", "tools/charter_check.py") == []

    def test_non_python_files_are_out_of_scope(self):
        assert rules("import random", "notes.md") == []


class TestExperimentalPremises:
    """The labs only measure something if these hold. Guard them."""

    def test_the_modern_layers_are_clean(self):
        verdict = check(
            sources(
                "tarrasque/domain/dice.py",
                "tarrasque/domain/rng.py",
                "tarrasque/domain/conditions.py",
                "tarrasque/domain/initiative.py",
                "tarrasque/domain/encounter.py",
                "tarrasque/domain/log.py",
                "tarrasque/api/encounters.py",
                "tarrasque/api/session.py",
                "tarrasque/http.py",
            )
        )
        assert verdict["clean"], verdict["problems"]

    def test_the_seeding_rule_is_opposed_by_the_v1_surface(self):
        found = check(sources("tarrasque/api/handlers.py"))["problems"]
        assert any(item["rule"] == "dice.seeded" for item in found)

    def test_the_provenance_rule_is_opposed_by_the_v1_surface(self):
        found = check(sources("tarrasque/api/handlers.py"))["problems"]
        assert any(item["rule"] == "roll.provenance" for item in found)

    def test_the_authority_rule_is_opposed_by_the_v1_surface(self):
        found = check(sources("tarrasque/api/handlers.py"))["problems"]
        assert any(item["rule"] == "authority.session-derived" for item in found)

    def test_the_append_only_rule_is_opposed_by_a_working_affordance(self):
        """Two functions in the query layer do exactly the forbidden thing."""
        found = check(sources("tarrasque/repo/queries.py"))["problems"]
        assert any(item["rule"] == "log.append-only" for item in found)

    def test_the_wrong_way_outnumbers_the_right_way(self):
        """If the good pattern ever wins on volume, the levers stop measuring."""
        god_file = (ROOT / "tarrasque/api/handlers.py").read_text()
        thin_file = (ROOT / "tarrasque/api/encounters.py").read_text()
        assert god_file.count("random.") >= 3
        assert "random." not in thin_file


class TestLegacyReach:
    def test_flags_a_call_through_the_conventional_alias(self):
        assert rules("total = tables.advantage(3)\n") == ["legacy.frozen"]

    def test_the_alias_is_allowed_inside_the_frozen_module(self):
        assert rules("x = tables.LOOT\n", "tarrasque/legacy/tables.py") == []


class TestBulkAuthority:
    def test_flags_a_list_of_combatants_taken_from_the_body(self):
        assert rules('ids = body.get("combatants") or []\n') == [
            "authority.session-derived"
        ]
