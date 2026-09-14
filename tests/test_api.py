"""The HTTP surface, end to end against a seeded in-memory database."""

import json

import pytest

from tarrasque import seed
from tarrasque.http import dispatch, match

MIRA = "Bearer tk_live_mira_0001"      # dungeon master at tbl_ashfall
JONAH = "Bearer tk_live_jonah_001"     # player, owns chr_brann
PILAR = "Bearer tk_live_pilar_001"     # player, owns chr_sable
DEV = "Bearer tk_live_dev_00001"       # dungeon master at tbl_saltmarsh

ASHFALL = "enc_ashfall_001"
SALTMARSH = "enc_saltmarsh_01"


@pytest.fixture()
def connection():
    return seed.build()


def call(connection, method, path, query=None, body="", auth=None):
    status, _, payload = dispatch(connection, method, path, query or {}, body, auth)
    return status, json.loads(payload)


class TestRouting:
    def test_binds_path_parameters(self):
        assert match("/v2/encounters/:encounter_id", "/v2/encounters/enc_1") == {
            "encounter_id": "enc_1"
        }

    def test_rejects_a_length_mismatch(self):
        assert match("/v2/encounters/:id", "/v2/encounters") is None

    def test_unknown_route_is_a_404(self, connection):
        assert call(connection, "GET", "/nope")[0] == 404


class TestV1:
    def test_health(self, connection):
        assert call(connection, "GET", "/healthz") == (200, {"status": "ok"})

    def test_rolls_for_a_character(self, connection):
        status, body = call(
            connection, "POST", "/v1/roll",
            body=json.dumps({"character_id": "chr_brann", "modifier": 3}),
        )
        assert status == 200
        assert 4 <= body["total"] <= 23

    def test_refuses_an_unknown_character(self, connection):
        status, _ = call(
            connection, "POST", "/v1/roll",
            body=json.dumps({"character_id": "chr_nobody"}),
        )
        assert status == 404

    def test_draws_from_the_loot_table(self, connection):
        status, body = call(connection, "GET", "/v1/tables/loot")
        assert status == 200
        assert isinstance(body["item"], str)


class TestAuthentication:
    def test_requires_a_bearer_token(self, connection):
        assert call(connection, "GET", f"/v2/encounters/{ASHFALL}")[0] == 401

    def test_rejects_an_unknown_key(self, connection):
        status, _ = call(
            connection, "GET", f"/v2/encounters/{ASHFALL}", auth="Bearer nope"
        )
        assert status == 401

    def test_a_missing_encounter_is_a_404_before_authentication(self, connection):
        assert call(connection, "GET", "/v2/encounters/enc_nope")[0] == 404


class TestAuthority:
    def test_a_member_may_read_their_own_table(self, connection):
        assert call(connection, "GET", f"/v2/encounters/{ASHFALL}", auth=JONAH)[0] == 200

    def test_a_non_member_may_not_read_another_table(self, connection):
        status, _ = call(connection, "GET", f"/v2/encounters/{SALTMARSH}", auth=PILAR)
        assert status == 403

    def test_a_player_may_act_for_their_own_character(self, connection):
        status, _ = call(
            connection,
            "POST",
            f"/v2/encounters/{ASHFALL}/characters/chr_brann/check",
            auth=JONAH,
        )
        assert status == 200

    def test_a_player_may_not_act_for_another_player_s_character(self, connection):
        status, body = call(
            connection,
            "POST",
            f"/v2/encounters/{ASHFALL}/characters/chr_brann/check",
            auth=PILAR,
        )
        assert status == 403
        assert "does not control" in body["error"]

    def test_the_dungeon_master_may_act_for_any_combatant_at_their_table(
        self, connection
    ):
        status, _ = call(
            connection,
            "POST",
            f"/v2/encounters/{ASHFALL}/characters/npc_cinderwyrm/check",
            auth=MIRA,
        )
        assert status == 200

    def test_a_dungeon_master_has_no_authority_at_another_table(self, connection):
        status, _ = call(
            connection, "POST", f"/v2/encounters/{ASHFALL}/initiative", auth=DEV
        )
        assert status == 403

    def test_only_the_dungeon_master_rolls_initiative(self, connection):
        status, _ = call(
            connection, "POST", f"/v2/encounters/{ASHFALL}/initiative", auth=JONAH
        )
        assert status == 403


class TestInitiative:
    def test_rolls_the_whole_table_into_order(self, connection):
        status, body = call(
            connection, "POST", f"/v2/encounters/{ASHFALL}/initiative", auth=MIRA
        )
        assert status == 200
        assert len(body["order"]) == 5
        scores = [entry["score"] for entry in body["order"]]
        assert scores == sorted(scores, reverse=True)

    def test_every_entry_carries_its_roll(self, connection):
        _, body = call(
            connection, "POST", f"/v2/encounters/{ASHFALL}/initiative", auth=MIRA
        )
        for entry in body["order"]:
            assert entry["roll"]["seed"].startswith(ASHFALL)
            assert entry["roll"]["total"] == entry["score"]

    def test_is_reproducible(self, connection):
        _, first = call(
            connection, "POST", f"/v2/encounters/{ASHFALL}/initiative", auth=MIRA
        )
        _, second = call(
            connection, "POST", f"/v2/encounters/{ASHFALL}/initiative", auth=MIRA
        )
        assert [e["score"] for e in first["order"]] == [
            e["score"] for e in second["order"]
        ]


class TestLog:
    def test_opens_with_the_encounter(self, connection):
        _, body = call(connection, "GET", f"/v2/encounters/{ASHFALL}/log", auth=MIRA)
        assert body["entries"][0]["kind"] == "encounter_opened"

    def test_every_action_appends(self, connection):
        _, before = call(connection, "GET", f"/v2/encounters/{ASHFALL}/log", auth=MIRA)
        call(
            connection,
            "POST",
            f"/v2/encounters/{ASHFALL}/characters/chr_brann/check",
            auth=JONAH,
        )
        _, after = call(connection, "GET", f"/v2/encounters/{ASHFALL}/log", auth=MIRA)
        assert len(after["entries"]) == len(before["entries"]) + 1

    def test_sequences_have_no_gaps(self, connection):
        call(connection, "POST", f"/v2/encounters/{ASHFALL}/initiative", auth=MIRA)
        call(
            connection,
            "POST",
            f"/v2/encounters/{ASHFALL}/characters/chr_sable/check",
            auth=PILAR,
        )
        _, body = call(connection, "GET", f"/v2/encounters/{ASHFALL}/log", auth=MIRA)
        sequences = [entry["sequence"] for entry in body["entries"]]
        assert sequences == list(range(1, len(sequences) + 1))

    def test_a_logged_check_can_be_replayed_from_its_seed(self, connection):
        from tarrasque.domain.dice import roll
        from tarrasque.domain.rng import SeededRng

        call(
            connection,
            "POST",
            f"/v2/encounters/{ASHFALL}/characters/chr_brann/check",
            auth=JONAH,
        )
        _, body = call(connection, "GET", f"/v2/encounters/{ASHFALL}/log", auth=MIRA)
        recorded = body["entries"][-1]["payload"]["roll"]
        replayed = roll(SeededRng(recorded["seed"]), recorded["notation"])
        assert replayed.total == recorded["total"]
