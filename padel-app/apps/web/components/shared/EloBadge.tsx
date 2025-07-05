"use client";

import React from 'react';
import { Badge } from '@workspace/ui/components/badge';
import { cn } from '@/lib/utils';

export interface EloCategory {
  name: string;
  range: string;
  minElo: number;
  maxElo: number;
  color: string;
  bgColor: string;
  borderColor: string;
  icon: string;
}

export const ELO_CATEGORIES: EloCategory[] = [
  {
    name: 'Bronze',
    range: '1.0-2.0',
    minElo: 1.0,
    maxElo: 2.0,
    color: 'text-amber-700',
    bgColor: 'bg-amber-100',
    borderColor: 'border-amber-300',
    icon: '🥉'
  },
  {
    name: 'Silver',
    range: '2.0-3.0',
    minElo: 2.0,
    maxElo: 3.0,
    color: 'text-gray-700',
    bgColor: 'bg-gray-100',
    borderColor: 'border-gray-300',
    icon: '🥈'
  },
  {
    name: 'Gold',
    range: '3.0-4.0',
    minElo: 3.0,
    maxElo: 4.0,
    color: 'text-yellow-700',
    bgColor: 'bg-yellow-100',
    borderColor: 'border-yellow-300',
    icon: '🥇'
  },
  {
    name: 'Platinum',
    range: '4.0+',
    minElo: 4.0,
    maxElo: 7.0,
    color: 'text-blue-700',
    bgColor: 'bg-blue-100',
    borderColor: 'border-blue-300',
    icon: '💎'
  }
];

export function getEloCategory(eloRating: number): EloCategory {
  const found = ELO_CATEGORIES.find(
    category => eloRating >= category.minElo && (
      category.name === 'Platinum' ? true : eloRating < category.maxElo
    )
  );
  return found ?? ELO_CATEGORIES[0]!; // Default to Bronze if not found
}

interface EloBadgeProps {
  eloRating: number;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
  showRange?: boolean;
  className?: string;
}

export function EloBadge({ 
  eloRating, 
  size = 'md', 
  showIcon = true,
  showRange = false,
  className 
}: EloBadgeProps) {
  const category = getEloCategory(eloRating);
  
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-2'
  };
  
  const iconSizes = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg'
  };

  return (
    <Badge
      variant="outline"
      className={cn(
        sizeClasses[size],
        category.color,
        category.bgColor,
        category.borderColor,
        'font-semibold',
        className
      )}
    >
      {showIcon && (
        <span className={cn('mr-1', iconSizes[size])}>
          {category.icon}
        </span>
      )}
      {category.name}
      {showRange && (
        <span className="ml-1 opacity-75">
          ({category.range})
        </span>
      )}
    </Badge>
  );
}

interface EloRatingWithBadgeProps {
  eloRating: number;
  showBadge?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function EloRatingWithBadge({ 
  eloRating, 
  showBadge = true,
  size = 'md',
  className 
}: EloRatingWithBadgeProps) {
  const textSizes = {
    sm: 'text-lg',
    md: 'text-2xl',
    lg: 'text-3xl'
  };

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <span className={cn('font-bold', textSizes[size])}>
        {eloRating.toFixed(1)}
      </span>
      {showBadge && <EloBadge eloRating={eloRating} size={size} />}
    </div>
  );
}