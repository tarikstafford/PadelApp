"use client";

import React from 'react';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { TournamentCategory } from '@/lib/types';
import { Check, X, AlertCircle } from 'lucide-react';

export interface CategoryInfo {
  name: string;
  range: string;
  minElo: number;
  maxElo: number;
  color: string;
  bgColor: string;
  borderColor: string;
  icon: string;
}

export const CATEGORY_INFO: Record<TournamentCategory, CategoryInfo> = {
  [TournamentCategory.BRONZE]: {
    name: 'Bronze',
    range: '1.0-2.0',
    minElo: 1.0,
    maxElo: 2.0,
    color: 'text-amber-700',
    bgColor: 'bg-amber-50',
    borderColor: 'border-amber-300',
    icon: '🥉'
  },
  [TournamentCategory.SILVER]: {
    name: 'Silver',
    range: '2.0-3.0',
    minElo: 2.0,
    maxElo: 3.0,
    color: 'text-gray-700',
    bgColor: 'bg-gray-50',
    borderColor: 'border-gray-300',
    icon: '🥈'
  },
  [TournamentCategory.GOLD]: {
    name: 'Gold',
    range: '3.0-5.0',
    minElo: 3.0,
    maxElo: 5.0,
    color: 'text-yellow-700',
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-300',
    icon: '🥇'
  },
  [TournamentCategory.PLATINUM]: {
    name: 'Platinum',
    range: '5.0+',
    minElo: 5.0,
    maxElo: 10.0,
    color: 'text-blue-700',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-300',
    icon: '💎'
  }
};

export interface CategoryBadgeProps {
  category: TournamentCategory;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
  showRange?: boolean;
  eligibilityStatus?: 'eligible' | 'ineligible' | 'borderline' | null;
  showEligibilityIndicator?: boolean;
  currentParticipants?: number;
  maxParticipants?: number;
  showParticipantCount?: boolean;
  className?: string;
}

export function CategoryBadge({
  category,
  size = 'md',
  showIcon = true,
  showRange = true,
  eligibilityStatus = null,
  showEligibilityIndicator = false,
  currentParticipants,
  maxParticipants,
  showParticipantCount = false,
  className
}: CategoryBadgeProps) {
  const categoryInfo = CATEGORY_INFO[category];
  
  const sizeClasses = {
    sm: 'text-xs px-2 py-1 gap-1',
    md: 'text-sm px-3 py-1.5 gap-1.5',
    lg: 'text-base px-4 py-2 gap-2'
  };
  
  const iconSizes = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base'
  };

  const getEligibilityIcon = () => {
    if (!showEligibilityIndicator || !eligibilityStatus) return null;
    
    const iconClasses = cn('w-3 h-3', {
      'text-green-600': eligibilityStatus === 'eligible',
      'text-red-600': eligibilityStatus === 'ineligible',
      'text-orange-600': eligibilityStatus === 'borderline'
    });
    
    switch (eligibilityStatus) {
      case 'eligible':
        return <Check className={iconClasses} />;
      case 'ineligible':
        return <X className={iconClasses} />;
      case 'borderline':
        return <AlertCircle className={iconClasses} />;
      default:
        return null;
    }
  };

  const getParticipantInfo = () => {
    if (!showParticipantCount || typeof currentParticipants !== 'number' || typeof maxParticipants !== 'number') {
      return null;
    }
    
    const spotsLeft = maxParticipants - currentParticipants;
    const isFull = spotsLeft === 0;
    const isAlmostFull = spotsLeft <= 2 && spotsLeft > 0;
    
    return (
      <span className={cn('text-xs font-medium', {
        'text-red-600': isFull,
        'text-orange-600': isAlmostFull,
        'text-green-600': !isFull && !isAlmostFull
      })}>
        {currentParticipants}/{maxParticipants}
      </span>
    );
  };

  return (
    <Badge
      variant="outline"
      className={cn(
        'flex items-center justify-between font-semibold transition-all',
        sizeClasses[size],
        categoryInfo.color,
        categoryInfo.bgColor,
        categoryInfo.borderColor,
        {
          'ring-2 ring-green-400 ring-opacity-50': eligibilityStatus === 'eligible',
          'ring-2 ring-red-400 ring-opacity-50': eligibilityStatus === 'ineligible',
          'ring-2 ring-orange-400 ring-opacity-50': eligibilityStatus === 'borderline'
        },
        className
      )}
    >
      <div className="flex items-center gap-1">
        {showIcon && (
          <span className={cn('shrink-0', iconSizes[size])}>
            {categoryInfo.icon}
          </span>
        )}
        <span className="font-semibold">{categoryInfo.name}</span>
        {showRange && (
          <span className="opacity-75 font-normal">
            ({categoryInfo.range})
          </span>
        )}
      </div>
      
      <div className="flex items-center gap-1 ml-2">
        {getParticipantInfo()}
        {getEligibilityIcon()}
      </div>
    </Badge>
  );
}

interface CategoryBadgeGridProps {
  categories: {
    category: TournamentCategory;
    max_participants: number;
    min_elo: number;
    max_elo: number;
    current_participants?: number;
    current_teams?: number;
    current_individuals?: number;
  }[];
  userEloRating?: number;
  size?: 'sm' | 'md' | 'lg';
  showEligibilityIndicator?: boolean;
  showParticipantCount?: boolean;
  className?: string;
}

export function CategoryBadgeGrid({
  categories,
  userEloRating,
  size = 'md',
  showEligibilityIndicator = false,
  showParticipantCount = false,
  className
}: CategoryBadgeGridProps) {
  const checkEligibility = (category: { min_elo: number; max_elo: number }) => {
    if (typeof userEloRating !== 'number') return null;
    
    const { min_elo, max_elo } = category;
    const buffer = 0.2; // 0.2 ELO buffer for borderline cases
    
    if (userEloRating >= min_elo && userEloRating <= max_elo) {
      return 'eligible';
    } else if (
      (userEloRating >= min_elo - buffer && userEloRating < min_elo) ||
      (userEloRating > max_elo && userEloRating <= max_elo + buffer)
    ) {
      return 'borderline';
    } else {
      return 'ineligible';
    }
  };

  return (
    <div className={cn('flex flex-wrap gap-2', className)}>
      {categories.map((categoryData) => {
        const eligibilityStatus = checkEligibility(categoryData);
        const currentParticipants = categoryData.current_participants || 
          categoryData.current_teams || 
          categoryData.current_individuals || 0;
        
        return (
          <CategoryBadge
            key={categoryData.category}
            category={categoryData.category}
            size={size}
            eligibilityStatus={eligibilityStatus}
            showEligibilityIndicator={showEligibilityIndicator}
            currentParticipants={currentParticipants}
            maxParticipants={categoryData.max_participants}
            showParticipantCount={showParticipantCount}
          />
        );
      })}
    </div>
  );
}

interface CategoryEligibilityLegendProps {
  className?: string;
}

export function CategoryEligibilityLegend({ className }: CategoryEligibilityLegendProps) {
  return (
    <div className={cn('flex flex-wrap gap-4 text-xs text-muted-foreground', className)}>
      <div className="flex items-center gap-1">
        <Check className="w-3 h-3 text-green-600" />
        <span>Eligible</span>
      </div>
      <div className="flex items-center gap-1">
        <AlertCircle className="w-3 h-3 text-orange-600" />
        <span>Borderline (±0.2 ELO)</span>
      </div>
      <div className="flex items-center gap-1">
        <X className="w-3 h-3 text-red-600" />
        <span>Not Eligible</span>
      </div>
    </div>
  );
}