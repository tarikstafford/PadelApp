import { useMemo } from 'react';
import { TournamentCategory } from '@/lib/types';

export interface EligibilityResult {
  isEligible: boolean;
  eligibleCategories: TournamentCategory[];
  borderlineCategories: TournamentCategory[];
  ineligibleCategories: TournamentCategory[];
  reasons: Record<TournamentCategory, string>;
}

export interface CategoryEligibilityData {
  category: TournamentCategory;
  min_elo: number;
  max_elo: number;
  max_participants: number;
  current_participants?: number;
}

export function useTournamentEligibility(
  categories: CategoryEligibilityData[],
  userEloRating?: number,
  bufferRange: number = 0.2
): EligibilityResult {
  return useMemo(() => {
    const result: EligibilityResult = {
      isEligible: false,
      eligibleCategories: [],
      borderlineCategories: [],
      ineligibleCategories: [],
      reasons: {} as Record<TournamentCategory, string>
    };

    if (!userEloRating) {
      // If no user ELO rating, mark all as ineligible with a general reason
      categories.forEach(cat => {
        result.ineligibleCategories.push(cat.category);
        result.reasons[cat.category] = 'Login required to check eligibility';
      });
      return result;
    }

    categories.forEach(categoryData => {
      const { category, min_elo, max_elo, max_participants, current_participants = 0 } = categoryData;
      
      // Check if category is full
      if (current_participants >= max_participants) {
        result.ineligibleCategories.push(category);
        result.reasons[category] = 'Category is full';
        return;
      }

      // Check ELO eligibility
      if (userEloRating >= min_elo && userEloRating <= max_elo) {
        result.eligibleCategories.push(category);
        result.reasons[category] = 'Eligible to register';
        result.isEligible = true;
      } else if (
        (userEloRating >= min_elo - bufferRange && userEloRating < min_elo) ||
        (userEloRating > max_elo && userEloRating <= max_elo + bufferRange)
      ) {
        result.borderlineCategories.push(category);
        result.reasons[category] = `ELO rating (${userEloRating.toFixed(1)}) is close to range (${min_elo}-${max_elo})`;
      } else {
        result.ineligibleCategories.push(category);
        if (userEloRating < min_elo) {
          result.reasons[category] = `ELO rating too low (need ${min_elo}+, have ${userEloRating.toFixed(1)})`;
        } else {
          result.reasons[category] = `ELO rating too high (max ${max_elo}, have ${userEloRating.toFixed(1)})`;
        }
      }
    });

    return result;
  }, [categories, userEloRating, bufferRange]);
}

export function getEligibilityStatus(
  categoryData: CategoryEligibilityData,
  userEloRating?: number,
  bufferRange: number = 0.2
): 'eligible' | 'ineligible' | 'borderline' | null {
  if (!userEloRating) return null;

  const { min_elo, max_elo, max_participants, current_participants = 0 } = categoryData;
  
  // Check if category is full
  if (current_participants >= max_participants) {
    return 'ineligible';
  }

  // Check ELO eligibility
  if (userEloRating >= min_elo && userEloRating <= max_elo) {
    return 'eligible';
  } else if (
    (userEloRating >= min_elo - bufferRange && userEloRating < min_elo) ||
    (userEloRating > max_elo && userEloRating <= max_elo + bufferRange)
  ) {
    return 'borderline';
  } else {
    return 'ineligible';
  }
}