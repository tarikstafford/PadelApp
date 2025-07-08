#!/usr/bin/env python3
"""
ELO Range Validation Script
This script validates and optionally fixes ELO range inconsistencies in the tournament system.
"""

import sys
from typing import Any

from sqlalchemy.orm import Session

from app.database import get_db
from app.models.tournament import (
    CATEGORY_ELO_RANGES,
    RecurringTournamentCategoryTemplate,
    TournamentCategoryConfig,
)


def check_tournament_category_configs(db: Session) -> list[dict[str, Any]]:
    """Check all tournament category configs for ELO range inconsistencies."""
    inconsistencies = []

    configs = db.query(TournamentCategoryConfig).all()

    for config in configs:
        expected_min, expected_max = CATEGORY_ELO_RANGES[config.category]

        if config.min_elo != expected_min or config.max_elo != expected_max:
            inconsistencies.append(
                {
                    "type": "tournament_category_config",
                    "id": config.id,
                    "tournament_id": config.tournament_id,
                    "category": config.category.value,
                    "current_min_elo": config.min_elo,
                    "current_max_elo": config.max_elo,
                    "expected_min_elo": expected_min,
                    "expected_max_elo": expected_max,
                }
            )

    return inconsistencies


def check_recurring_tournament_templates(db: Session) -> list[dict[str, Any]]:
    """Check all recurring tournament category templates for ELO range inconsistencies."""
    inconsistencies = []

    templates = db.query(RecurringTournamentCategoryTemplate).all()

    for template in templates:
        expected_min, expected_max = CATEGORY_ELO_RANGES[template.category]

        if template.min_elo != expected_min or template.max_elo != expected_max:
            inconsistencies.append(
                {
                    "type": "recurring_tournament_template",
                    "id": template.id,
                    "recurring_tournament_id": template.recurring_tournament_id,
                    "category": template.category.value,
                    "current_min_elo": template.min_elo,
                    "current_max_elo": template.max_elo,
                    "expected_min_elo": expected_min,
                    "expected_max_elo": expected_max,
                }
            )

    return inconsistencies


def fix_inconsistencies(
    db: Session, inconsistencies: list[dict[str, Any]], dry_run: bool = True
) -> int:
    """Fix ELO range inconsistencies."""
    fixed_count = 0

    for inconsistency in inconsistencies:
        if inconsistency["type"] == "tournament_category_config":
            config = (
                db.query(TournamentCategoryConfig)
                .filter(TournamentCategoryConfig.id == inconsistency["id"])
                .first()
            )

            if config:
                if not dry_run:
                    config.min_elo = inconsistency["expected_min_elo"]
                    config.max_elo = inconsistency["expected_max_elo"]
                    print(
                        f"✅ Fixed tournament category config {config.id}: {inconsistency['category']} -> {inconsistency['expected_min_elo']}-{inconsistency['expected_max_elo']}"
                    )
                else:
                    print(
                        f"🔍 Would fix tournament category config {config.id}: {inconsistency['category']} -> {inconsistency['expected_min_elo']}-{inconsistency['expected_max_elo']}"
                    )
                fixed_count += 1

        elif inconsistency["type"] == "recurring_tournament_template":
            template = (
                db.query(RecurringTournamentCategoryTemplate)
                .filter(RecurringTournamentCategoryTemplate.id == inconsistency["id"])
                .first()
            )

            if template:
                if not dry_run:
                    template.min_elo = inconsistency["expected_min_elo"]
                    template.max_elo = inconsistency["expected_max_elo"]
                    print(
                        f"✅ Fixed recurring tournament template {template.id}: {inconsistency['category']} -> {inconsistency['expected_min_elo']}-{inconsistency['expected_max_elo']}"
                    )
                else:
                    print(
                        f"🔍 Would fix recurring tournament template {template.id}: {inconsistency['category']} -> {inconsistency['expected_min_elo']}-{inconsistency['expected_max_elo']}"
                    )
                fixed_count += 1

    if not dry_run and fixed_count > 0:
        db.commit()
        print(f"✅ Committed {fixed_count} fixes to database")

    return fixed_count


def main():
    """Main validation script."""
    print("🏆 ELO Range Validation Script")
    print("=" * 50)

    # Print expected ranges
    print("Expected ELO Ranges (CATEGORY_ELO_RANGES):")
    for category, (min_elo, max_elo) in CATEGORY_ELO_RANGES.items():
        print(f"  {category.value}: {min_elo} - {max_elo}")
    print()

    # Check for --fix flag
    should_fix = "--fix" in sys.argv

    if should_fix:
        print("🔧 FIX MODE: Will apply fixes to database")
    else:
        print(
            "🔍 CHECK MODE: Will only report inconsistencies (use --fix to apply fixes)"
        )
    print()

    # Create database session
    db_gen = get_db()
    db = next(db_gen)

    try:
        # Check tournament category configs
        print("Checking tournament category configurations...")
        config_inconsistencies = check_tournament_category_configs(db)

        if config_inconsistencies:
            print(
                f"❌ Found {len(config_inconsistencies)} inconsistencies in tournament category configs:"
            )
            for inconsistency in config_inconsistencies:
                print(
                    f"  Tournament {inconsistency['tournament_id']}, Category {inconsistency['category']}: "
                    f"{inconsistency['current_min_elo']}-{inconsistency['current_max_elo']} "
                    f"(expected: {inconsistency['expected_min_elo']}-{inconsistency['expected_max_elo']})"
                )
        else:
            print("✅ All tournament category configs have correct ELO ranges")
        print()

        # Check recurring tournament templates
        print("Checking recurring tournament category templates...")
        template_inconsistencies = check_recurring_tournament_templates(db)

        if template_inconsistencies:
            print(
                f"❌ Found {len(template_inconsistencies)} inconsistencies in recurring tournament templates:"
            )
            for inconsistency in template_inconsistencies:
                print(
                    f"  Recurring Tournament {inconsistency['recurring_tournament_id']}, Category {inconsistency['category']}: "
                    f"{inconsistency['current_min_elo']}-{inconsistency['current_max_elo']} "
                    f"(expected: {inconsistency['expected_min_elo']}-{inconsistency['expected_max_elo']})"
                )
        else:
            print("✅ All recurring tournament templates have correct ELO ranges")
        print()

        # Apply fixes if requested
        all_inconsistencies = config_inconsistencies + template_inconsistencies

        if all_inconsistencies:
            if should_fix:
                print("Applying fixes...")
                fixed_count = fix_inconsistencies(
                    db, all_inconsistencies, dry_run=False
                )
                print(f"✅ Fixed {fixed_count} inconsistencies")
            else:
                print(f"Run with --fix to apply {len(all_inconsistencies)} fixes")
        else:
            print("🎉 No inconsistencies found! All ELO ranges are correct.")

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    finally:
        db.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
