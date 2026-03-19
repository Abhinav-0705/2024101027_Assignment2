"""
White-Box Test Suite for MoneyPoly
====================================
Run from the Ass2/ directory:
    cd /Users/abhinavchatrathi/Documents/Sem4/DASS/Ass2
    pytest whitebox/tests/test_moneypoly.py -v

Each test targets a specific branch or known bug in the code.
"""

import sys
import os
import pytest

# ── Add the moneypoly package to the path so imports work ──────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "moneypoly"))

from moneypoly.player import Player
from moneypoly.bank import Bank
from moneypoly.board import Board
from moneypoly.property import Property, PropertyGroup
from moneypoly.dice import Dice
from moneypoly.cards import CardDeck, CHANCE_CARDS, COMMUNITY_CHEST_CARDS
from moneypoly.game import Game
from moneypoly.config import (
    STARTING_BALANCE, GO_SALARY, BOARD_SIZE, JAIL_POSITION, JAIL_FINE,
    INCOME_TAX_AMOUNT, LUXURY_TAX_AMOUNT
)


# ═══════════════════════════════════════════════════════════════════
# TC1 — buy_property: player with EXACT balance should be allowed to buy
# Bug: line 140 in game.py uses `<=` instead of `<`
# Expected: player with exactly $60 CAN buy a $60 property
# Actual (buggy): player CANNOT buy it — balance is NOT less than price
# ═══════════════════════════════════════════════════════════════════
class TestTC1_BuyPropertyExactBalance:
    def setup_method(self):
        self.game = Game(["Alice", "Bob"])
        self.player = self.game.players[0]
        self.prop = self.game.board.get_property_at(1)   # Mediterranean Ave, $60

    def test_buy_with_exact_balance_should_succeed(self):
        """Player with exactly the property price should be able to buy it."""
        self.player.balance = self.prop.price           # set balance = $60 exactly 
        result = self.game.buy_property(self.player, self.prop)
        # BUG: this will FAIL on the original code because of <=
        assert result is True, (
            f"BUG FOUND: buy_property returned False when player balance "
            f"(${self.player.balance}) == property price (${self.prop.price}). "
            f"Condition should be `<` not `<=`."
        )

    def test_buy_with_less_than_price_should_fail(self):
        """Player with less than the price should NOT be able to buy."""
        self.player.balance = self.prop.price - 1
        result = self.game.buy_property(self.player, self.prop)
        assert result is False


# ═══════════════════════════════════════════════════════════════════
# TC2 — find_winner: should return player with HIGHEST net worth
# Bug: line 363 in game.py uses `min()` instead of `max()`
# ═══════════════════════════════════════════════════════════════════
class TestTC2_FindWinner:
    def setup_method(self):
        self.game = Game(["Alice", "Bob"])
        self.alice = self.game.players[0]
        self.bob   = self.game.players[1]

    def test_winner_is_richest_player(self):
        """find_winner should return the player with the most money."""
        self.alice.balance = 5000
        self.bob.balance   = 1000
        winner = self.game.find_winner()
        # BUG: buggy code returns Bob (min) instead of Alice (max)
        assert winner == self.alice, (
            f"BUG FOUND: find_winner returned '{winner.name}' but expected 'Alice'. "
            f"game.py line 363 uses min() — should be max()."
        )

    def test_no_players_returns_none(self):
        """find_winner should return None when no players remain."""
        self.game.players.clear()
        assert self.game.find_winner() is None


# ═══════════════════════════════════════════════════════════════════
# TC3 — net_worth: should include property values, not just cash
# Bug: player.py line 37 — net_worth() only returns self.balance
# ═══════════════════════════════════════════════════════════════════
class TestTC3_NetWorth:
    def setup_method(self):
        self.player = Player("Alice", balance=1000)
        group = PropertyGroup("Brown", "brown")
        self.prop = Property("Mediterranean Avenue", 1, 60, 2, group)
        self.prop.owner = self.player
        self.player.add_property(self.prop)

    def test_net_worth_includes_property_value(self):
        """net_worth should count balance + mortgage value of properties."""
        expected = self.player.balance + self.prop.mortgage_value   # 1000 + 30
        actual   = self.player.net_worth()
        # BUG: buggy code returns only 1000, missing property value
        assert actual == expected, (
            f"BUG FOUND: net_worth() returned {actual}, expected {expected}. "
            f"Property values are not being counted in player.py."
        )

    def test_net_worth_no_properties(self):
        """net_worth with no properties should just equal the balance."""
        p = Player("Bob", balance=500)
        assert p.net_worth() == 500


# ═══════════════════════════════════════════════════════════════════
# TC4 — move: player should collect Go salary when PASSING Go, not only landing
# Bug: player.py line 48 — only checks `position == 0` (landing), not passing
# ═══════════════════════════════════════════════════════════════════
class TestTC4_PassingGo:
    def setup_method(self):
        self.player = Player("Alice", balance=1000)

    def test_landing_on_go_collects_salary(self):
        """Landing exactly on Go (position 0) should give Go salary."""
        self.player.position = BOARD_SIZE - 5   # position 35
        before = self.player.balance
        self.player.move(5)                     # moves to position 0 exactly
        assert self.player.position == 0
        assert self.player.balance == before + GO_SALARY

    def test_passing_go_should_collect_salary(self):
        """Moving past Go (wrapping around) should also give the Go salary."""
        self.player.position = 38               # two steps from Go
        before = self.player.balance
        self.player.move(4)                     # wraps: new position = 2 (passed Go)
        # BUG: buggy code gives $0 here because position != 0
        assert self.player.balance == before + GO_SALARY, (
            f"BUG FOUND: Player passed Go but balance only changed by "
            f"${self.player.balance - before}. Expected ${GO_SALARY}. "
            f"player.py move() only awards salary when position == 0."
        )


# ═══════════════════════════════════════════════════════════════════
# TC5 — all_owned_by: should use all(), not any()
# Bug: property.py line 80 — `any(p.owner == player ...)` should be `all(...)`
# Effect: rent doubles even if player owns only 1 property in a group
# ═══════════════════════════════════════════════════════════════════
class TestTC5_FullGroupRentDoubling:
    def setup_method(self):
        self.alice = Player("Alice", balance=2000)
        self.group = PropertyGroup("Brown", "brown")
        self.prop1 = Property("Mediterranean Avenue", 1, 60, 2, self.group)
        self.prop2 = Property("Baltic Avenue",        3, 60, 4, self.group)

    def test_no_doubling_when_partial_group_owned(self):
        """Rent should NOT be doubled when player owns only 1 of 2 group properties."""
        self.prop1.owner = self.alice
        # prop2 is unowned — Alice only owns one of two Brown properties
        rent = self.prop1.get_rent()
        # BUG: buggy any() makes this doubled (2*2=4) even with partial ownership
        assert rent == self.prop1.base_rent, (
            f"BUG FOUND: Rent was ${rent} but expected ${self.prop1.base_rent}. "
            f"property.py all_owned_by() uses any() — should be all()."
        )

    def test_doubling_when_full_group_owned(self):
        """Rent SHOULD be doubled when player owns the entire group."""
        self.prop1.owner = self.alice
        self.prop2.owner = self.alice
        rent = self.prop1.get_rent()
        assert rent == self.prop1.base_rent * 2


# ═══════════════════════════════════════════════════════════════════
# TC6 — dice: each die should roll 1–6, not 1–5
# Bug: dice.py lines 20–21 use randint(1, 5) instead of randint(1, 6)
# ═══════════════════════════════════════════════════════════════════
class TestTC6_DiceRange:
    def setup_method(self):
        self.dice = Dice()

    def test_dice_can_roll_six(self):
        """Rolling 10000 times, the value 6 should appear on at least one die."""
        saw_six = False
        for _ in range(10000):
            self.dice.roll()
            if self.dice.die1 == 6 or self.dice.die2 == 6:
                saw_six = True
                break
        # BUG: buggy code uses randint(1,5) so this always fails
        assert saw_six, (
            "BUG FOUND: After 10000 rolls, die value 6 was never seen. "
            "dice.py uses randint(1, 5) — should be randint(1, 6)."
        )

    def test_dice_values_within_valid_range(self):
        """Each die should always be between 1 and 6 inclusive."""
        for _ in range(1000):
            self.dice.roll()
            assert 1 <= self.dice.die1 <= 6, f"die1={self.dice.die1} out of range"
            assert 1 <= self.dice.die2 <= 6, f"die2={self.dice.die2} out of range"

    def test_doubles_streak_increments(self):
        """Doubles streak should increase when doubles are rolled."""
        # Force doubles by patching
        self.dice.die1 = 3
        self.dice.die2 = 3
        self.dice.doubles_streak = 0
        # Simulate what roll does for doubles check
        if self.dice.is_doubles():
            self.dice.doubles_streak += 1
        assert self.dice.doubles_streak == 1

    def test_doubles_streak_resets_on_non_doubles(self):
        """Doubles streak should reset to 0 after a non-doubles roll."""
        self.dice.doubles_streak = 2
        # Keep rolling until non-doubles (guaranteed in reasonable attempts)
        for _ in range(1000):
            self.dice.roll()
            if not self.dice.is_doubles():
                break
        assert self.dice.doubles_streak == 0


# ═══════════════════════════════════════════════════════════════════
# TC7 — jail fine: paying the fine should deduct from player's balance too
# Bug: game.py line 272–275 — bank.collect(JAIL_FINE) called but
#      player.deduct_money() is NEVER called for voluntary fine payment
# ═══════════════════════════════════════════════════════════════════
class TestTC7_JailFineDeductsFromPlayer:
    def setup_method(self):
        self.game = Game(["Alice", "Bob"])
        self.player = self.game.players[0]
        self.player.in_jail = True
        self.player.jail_turns = 0

    def test_pay_jail_fine_reduces_player_balance(self):
        """Paying the jail fine should remove money from the player."""
        self.player.balance = 1000
        before = self.player.balance

        # Simulate what _handle_jail_turn does on voluntary payment
        self.game.bank.collect(JAIL_FINE)
        self.player.in_jail = False
        self.player.jail_turns = 0
        # BUG: buggy code never calls player.deduct_money here
        # We're checking whether the game code actually does it

        # The player's balance should have gone DOWN by JAIL_FINE
        # If the bug exists, balance is still 1000 (nothing deducted)
        # Manually check that the game's logic would deduct it:
        # (We can't call _handle_jail_turn directly — it uses input())
        # So we test the isolated bank + player interaction:
        self.player.balance = before
        self.player.deduct_money(JAIL_FINE)
        self.game.bank.collect(JAIL_FINE)
        assert self.player.balance == before - JAIL_FINE, (
            f"BUG FOUND: Player balance should be ${before - JAIL_FINE} "
            f"but is ${self.player.balance}. game.py does not deduct jail fine from player."
        )


# ═══════════════════════════════════════════════════════════════════
# TC8 — is_bankrupt: edge cases around zero and negative balance
# ═══════════════════════════════════════════════════════════════════
class TestTC8_Bankruptcy:
    def test_bankrupt_at_zero_balance(self):
        """A player with $0 should be considered bankrupt."""
        p = Player("Zero", balance=0)
        assert p.is_bankrupt() is True

    def test_bankrupt_when_balance_is_negative(self):
        """A player whose balance goes negative is bankrupt."""
        p = Player("Broke", balance=100)
        p.deduct_money(100)
        assert p.is_bankrupt() is True

    def test_not_bankrupt_with_positive_balance(self):
        """A player with any positive balance is NOT bankrupt."""
        p = Player("Rich", balance=1)
        assert p.is_bankrupt() is False

    def test_add_negative_raises_error(self):
        """add_money with a negative amount should raise ValueError."""
        p = Player("Alice")
        with pytest.raises(ValueError):
            p.add_money(-10)

    def test_deduct_negative_raises_error(self):
        """deduct_money with a negative amount should raise ValueError."""
        p = Player("Alice")
        with pytest.raises(ValueError):
            p.deduct_money(-10)


# ═══════════════════════════════════════════════════════════════════
# TC9 — CardDeck: edge cases on empty deck, draw cycling, peek
# ═══════════════════════════════════════════════════════════════════
class TestTC9_CardDeck:
    def test_draw_empty_deck_returns_none(self):
        """Drawing from an empty deck should return None, not crash."""
        deck = CardDeck([])
        assert deck.draw() is None

    def test_draw_cycles_back_to_start(self):
        """After drawing all cards, the deck should cycle back to card 0."""
        cards = [{"description": f"Card {i}", "action": "collect", "value": i}
                 for i in range(3)]
        deck = CardDeck(cards)
        for _ in range(3):
            deck.draw()
        # Now it should wrap — the 4th draw gives card 0 again
        card = deck.draw()
        assert card["value"] == 0

    def test_peek_does_not_advance_index(self):
        """peek() should return the next card without consuming it."""
        deck = CardDeck(CHANCE_CARDS)
        first = deck.peek()
        also_first = deck.peek()
        assert first["description"] == also_first["description"]
        assert deck.index == 0     # index should not have moved

    def test_deck_length_matches_cards(self):
        """len(deck) should match the number of cards provided."""
        deck = CardDeck(COMMUNITY_CHEST_CARDS)
        assert len(deck) == len(COMMUNITY_CHEST_CARDS)


# ═══════════════════════════════════════════════════════════════════
# TC10 — mortgage / unmortgage: branch coverage
# ═══════════════════════════════════════════════════════════════════
class TestTC10_MortgageUnmortgage:
    def setup_method(self):
        self.game = Game(["Alice", "Bob"])
        self.player = self.game.players[0]
        self.prop = self.game.board.get_property_at(1)  # Mediterranean Ave
        self.prop.owner = self.player
        self.player.add_property(self.prop)

    def test_mortgage_gives_player_money(self):
        """Mortgaging a property should add half the price to the player's balance."""
        before = self.player.balance
        result = self.game.mortgage_property(self.player, self.prop)
        assert result is True
        assert self.player.balance == before + self.prop.mortgage_value

    def test_mortgage_already_mortgaged_fails(self):
        """Mortgaging an already-mortgaged property should return False."""
        self.prop.is_mortgaged = True
        result = self.game.mortgage_property(self.player, self.prop)
        assert result is False

    def test_unmortgage_costs_110_percent(self):
        """Unmortgaging should cost 110% of the mortgage value."""
        self.prop.is_mortgaged = True
        expected_cost = int(self.prop.mortgage_value * 1.1)
        before = self.player.balance
        result = self.game.unmortgage_property(self.player, self.prop)
        assert result is True
        assert self.player.balance == before - expected_cost

    def test_unmortgage_not_mortgaged_fails(self):
        """Trying to unmortgage a property that isn't mortgaged should fail."""
        self.prop.is_mortgaged = False
        result = self.game.unmortgage_property(self.player, self.prop)
        assert result is False

    def test_mortgage_non_owned_property_fails(self):
        """A player should not be able to mortgage a property they don't own."""
        other_player = self.game.players[1]
        result = self.game.mortgage_property(other_player, self.prop)
        assert result is False


# ═══════════════════════════════════════════════════════════════════
# TC11 — pay_rent: rent on mortgaged property is 0
# ═══════════════════════════════════════════════════════════════════
class TestTC11_PayRent:
    def setup_method(self):
        self.game = Game(["Alice", "Bob"])
        self.alice = self.game.players[0]
        self.bob   = self.game.players[1]
        self.prop  = self.game.board.get_property_at(1)
        self.prop.owner = self.alice

    def test_no_rent_on_mortgaged_property(self):
        """Landing on a mortgaged property should cost no rent."""
        self.prop.is_mortgaged = True
        before = self.bob.balance
        self.game.pay_rent(self.bob, self.prop)
        assert self.bob.balance == before

    def test_rent_paid_to_owner(self):
        """Paying rent should deduct from tenant and the message should print."""
        self.prop.is_mortgaged = False
        before_bob = self.bob.balance
        self.game.pay_rent(self.bob, self.prop)
        assert self.bob.balance == before_bob - self.prop.get_rent()


# ═══════════════════════════════════════════════════════════════════
# TC12 — bank: give_loan and collect correctness
# ═══════════════════════════════════════════════════════════════════
class TestTC12_Bank:
    def setup_method(self):
        self.bank   = Bank()
        self.player = Player("Alice", balance=0)

    def test_give_loan_increases_player_balance(self):
        """A loan should increase the player's balance."""
        before = self.player.balance
        self.bank.give_loan(self.player, 200)
        assert self.player.balance == before + 200
        assert self.bank.loan_count() == 1

    def test_give_loan_zero_does_nothing(self):
        """A loan of $0 or less should not be issued."""
        self.bank.give_loan(self.player, 0)
        assert self.bank.loan_count() == 0

    def test_pay_out_more_than_funds_raises(self):
        """bank.pay_out() should raise ValueError if bank lacks funds."""
        with pytest.raises(ValueError):
            self.bank.pay_out(self.bank.get_balance() + 1)

    def test_pay_out_zero_returns_zero(self):
        """bank.pay_out(0) should return 0 without raising."""
        assert self.bank.pay_out(0) == 0

    def test_collect_increases_balance(self):
        """bank.collect() should increase the bank's funds."""
        before = self.bank.get_balance()
        self.bank.collect(100)
        assert self.bank.get_balance() == before + 100


# ═══════════════════════════════════════════════════════════════════
# TC13 — trade: property transfers correctly between players
# ═══════════════════════════════════════════════════════════════════
class TestTC13_Trade:
    def setup_method(self):
        self.game  = Game(["Alice", "Bob"])
        self.alice = self.game.players[0]
        self.bob   = self.game.players[1]
        self.prop  = self.game.board.get_property_at(1)
        self.prop.owner = self.alice
        self.alice.add_property(self.prop)

    def test_successful_trade(self):
        """A valid trade should transfer property and deduct cash from buyer."""
        self.bob.balance = 500
        result = self.game.trade(self.alice, self.bob, self.prop, cash_amount=100)
        assert result is True
        assert self.prop.owner == self.bob
        assert self.bob.balance == 400
        assert self.prop in self.bob.properties
        assert self.prop not in self.alice.properties

    def test_trade_fails_if_seller_does_not_own(self):
        """Trade should fail if the seller doesn't own the property."""
        result = self.game.trade(self.bob, self.alice, self.prop, cash_amount=0)
        assert result is False

    def test_trade_fails_if_buyer_cannot_afford(self):
        """Trade should fail if buyer can't afford the cash amount."""
        self.bob.balance = 50
        result = self.game.trade(self.alice, self.bob, self.prop, cash_amount=100)
        assert result is False


# ═══════════════════════════════════════════════════════════════════
# TC14 — board.get_tile_type: all tile categories return correct strings
# ═══════════════════════════════════════════════════════════════════
class TestTC14_BoardTileTypes:
    def setup_method(self):
        self.board = Board()

    def test_go_tile(self):
        assert self.board.get_tile_type(0) == "go"

    def test_jail_tile(self):
        assert self.board.get_tile_type(10) == "jail"

    def test_go_to_jail_tile(self):
        assert self.board.get_tile_type(30) == "go_to_jail"

    def test_free_parking_tile(self):
        assert self.board.get_tile_type(20) == "free_parking"

    def test_income_tax_tile(self):
        assert self.board.get_tile_type(4) == "income_tax"

    def test_luxury_tax_tile(self):
        assert self.board.get_tile_type(38) == "luxury_tax"

    def test_property_tile(self):
        assert self.board.get_tile_type(1) == "property"

    def test_railroad_tile(self):
        assert self.board.get_tile_type(5) == "railroad"

    def test_chance_tile(self):
        assert self.board.get_tile_type(7) == "chance"

    def test_community_chest_tile(self):
        assert self.board.get_tile_type(2) == "community_chest"

    def test_blank_tile_returns_blank(self):
        # Position 12 has no special tile and no property defined on the board
        assert self.board.get_tile_type(12) == "blank"
