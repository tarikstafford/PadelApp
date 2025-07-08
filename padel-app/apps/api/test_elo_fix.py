#!/usr/bin/env python3
"""
Test script to verify ELO range fixes
"""

from app.crud.tournament_crud import tournament_crud
from app.database import get_db
from app.models.tournament import CATEGORY_ELO_RANGES, TournamentCategory


def test_category_elo_ranges():
    """Test that CATEGORY_ELO_RANGES has correct values."""
    print("Testing CATEGORY_ELO_RANGES...")

    expected_ranges = {
        TournamentCategory.BRONZE: (1.0, 2.0),
        TournamentCategory.SILVER: (2.0, 3.0),
        TournamentCategory.GOLD: (3.0, 5.0),
        TournamentCategory.PLATINUM: (5.0, 10.0),
    }

    for category, expected_range in expected_ranges.items():
        actual_range = CATEGORY_ELO_RANGES[category]
        if actual_range == expected_range:
            print(f"✅ {category.value}: {actual_range}")
        else:
            print(f"❌ {category.value}: expected {expected_range}, got {actual_range}")


def test_elo_eligibility_logic():
    """Test the ELO eligibility logic."""
    print("\nTesting ELO eligibility logic...")

    # Create a mock category config for testing
    class MockCategoryConfig:
        def __init__(self, category, min_elo, max_elo):
            self.category = category
            self.min_elo = min_elo
            self.max_elo = max_elo

    crud = tournament_crud

    # Test GOLD category (3.0 - 5.0)
    gold_config = MockCategoryConfig(TournamentCategory.GOLD, 3.0, 5.0)

    test_cases = [
        (2.9, False, "Below range"),
        (3.0, True, "At lower bound"),
        (3.4, True, "Within range"),  # This is the key test case!
        (4.9, True, "Within range"),
        (5.0, False, "At upper bound (exclusive)"),
        (5.1, False, "Above range"),
    ]

    print("GOLD category tests (range: 3.0 - 5.0):")
    for elo, expected, description in test_cases:
        result = crud._is_elo_eligible_for_category(elo, gold_config)
        status = "✅" if result == expected else "❌"
        print(f"  {status} ELO {elo}: {result} ({description})")

    # Test PLATINUM category (5.0+)
    platinum_config = MockCategoryConfig(TournamentCategory.PLATINUM, 5.0, 10.0)

    platinum_test_cases = [
        (4.9, False, "Below range"),
        (5.0, True, "At lower bound"),
        (7.0, True, "Above stored max (should still work)"),
        (15.0, True, "Way above stored max (should still work)"),
    ]

    print("\nPLATINUM category tests (range: 5.0+):")
    for elo, expected, description in platinum_test_cases:
        result = crud._is_elo_eligible_for_category(elo, platinum_config)
        status = "✅" if result == expected else "❌"
        print(f"  {status} ELO {elo}: {result} ({description})")


def test_with_database():
    """Test with actual database if available."""
    print("\nTesting with database...")

    try:
        db_gen = get_db()
        db = next(db_gen)

        # Test the debug function
        result = tournament_crud.debug_elo_eligibility(db, 3.4, TournamentCategory.GOLD)

        print("Debug result for ELO 3.4 in GOLD category:")
        print(f"  Expected range: {result['expected_range']}")
        print(f"  Total open tournaments: {result['total_open_tournaments']}")
        print(f"  Can join any: {result['summary']['can_join_any']}")

        db.close()

    except Exception as e:
        print(f"❌ Database test failed: {e}")


def main():
    """Run all tests."""
    print("🏆 ELO Range Fix Verification")
    print("=" * 50)

    test_category_elo_ranges()
    test_elo_eligibility_logic()
    test_with_database()

    print("\n🎯 Key Test: User with 3.4 ELO should be eligible for GOLD tournaments!")


if __name__ == "__main__":
    main()
