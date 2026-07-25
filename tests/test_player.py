from domain.player import Player


def test_starts_with_zero_money():
    assert Player().money == 0


def test_earn_increases_money_and_fires_listeners():
    p = Player()
    seen = []
    p.add_money_listener(seen.append)

    p.earn(100)

    assert p.money == 100
    assert seen == [100]


def test_spend_succeeds_and_decreases_money_when_affordable():
    p = Player()
    p.earn(100)
    seen = []
    p.add_money_listener(seen.append)

    ok = p.spend(40)

    assert ok is True
    assert p.money == 60
    assert seen == [60]


def test_spend_fails_and_leaves_money_unchanged_when_not_affordable():
    p = Player()
    p.earn(10)
    seen = []
    p.add_money_listener(seen.append)

    ok = p.spend(11)

    assert ok is False
    assert p.money == 10
    assert seen == []  # setter no-ops on unchanged value, no listener fire


def test_spend_exact_balance_succeeds_and_zeroes_out():
    p = Player()
    p.earn(50)
    assert p.spend(50) is True
    assert p.money == 0


def test_can_afford_is_a_pure_check_with_no_side_effects():
    p = Player()
    p.earn(20)

    assert p.can_afford(20) is True
    assert p.can_afford(21) is False
    assert p.money == 20  # unchanged


def test_setting_same_money_value_does_not_refire_listeners():
    p = Player()
    p.earn(30)
    seen = []
    p.add_money_listener(seen.append)

    p.money = 30  # explicit no-op set

    assert seen == []
