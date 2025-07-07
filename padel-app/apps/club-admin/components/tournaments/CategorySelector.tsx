'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Trash2, Plus } from 'lucide-react';
import { TournamentCategory } from '@/lib/types';

export interface CategoryConfig {
  category: TournamentCategory;
  max_participants: number;
  min_elo?: number;
  max_elo?: number;
}

interface CategorySelectorProps {
  categories: CategoryConfig[];
  onChange: (categories: CategoryConfig[]) => void;
  showEloRanges?: boolean;
  requireEloRanges?: boolean;
}

const CATEGORY_INFO = {
  [TournamentCategory.BRONZE]: { label: 'Bronze', defaultMinElo: 1.0, defaultMaxElo: 2.0 },
  [TournamentCategory.SILVER]: { label: 'Silver', defaultMinElo: 2.0, defaultMaxElo: 3.0 },
  [TournamentCategory.GOLD]: { label: 'Gold', defaultMinElo: 3.0, defaultMaxElo: 4.0 },
  [TournamentCategory.PLATINUM]: { label: 'Platinum', defaultMinElo: 4.0, defaultMaxElo: 5.0 },
};

export default function CategorySelector({ 
  categories, 
  onChange, 
  showEloRanges = false,
  requireEloRanges = false 
}: CategorySelectorProps) {
  const addCategory = () => {
    const newCategory: CategoryConfig = {
      category: TournamentCategory.BRONZE,
      max_participants: 16,
      ...(requireEloRanges && {
        min_elo: CATEGORY_INFO[TournamentCategory.BRONZE].defaultMinElo,
        max_elo: CATEGORY_INFO[TournamentCategory.BRONZE].defaultMaxElo,
      }),
    };
    onChange([...categories, newCategory]);
  };

  const updateCategory = (index: number, field: keyof CategoryConfig, value: any) => {
    const updated = categories.map((cat, i) => {
      if (i === index) {
        const updatedCat = { ...cat, [field]: value };
        
        // Update default ELO ranges when category changes
        if (field === 'category' && requireEloRanges) {
          const categoryInfo = CATEGORY_INFO[value as TournamentCategory];
          updatedCat.min_elo = categoryInfo.defaultMinElo;
          updatedCat.max_elo = categoryInfo.defaultMaxElo;
        }
        
        return updatedCat;
      }
      return cat;
    });
    onChange(updated);
  };

  const removeCategory = (index: number) => {
    onChange(categories.filter((_, i) => i !== index));
  };

  const getAvailableCategories = (currentCategory?: TournamentCategory) => {
    const usedCategories = categories.map(c => c.category).filter(c => c !== currentCategory);
    return Object.values(TournamentCategory).filter(cat => !usedCategories.includes(cat));
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Tournament Categories</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {categories.map((category, index) => (
          <div key={index} className="space-y-4 p-4 border rounded-lg">
            <div className="flex gap-4 items-end">
              <div className="flex-1">
                <Label>Category</Label>
                <Select 
                  value={category.category}
                  onValueChange={(value) => updateCategory(index, 'category', value as TournamentCategory)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    {getAvailableCategories(category.category).map((cat) => (
                      <SelectItem key={cat} value={cat}>
                        {CATEGORY_INFO[cat].label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="w-32">
                <Label>Max Participants</Label>
                <Input
                  type="number"
                  value={category.max_participants}
                  onChange={(e) => updateCategory(index, 'max_participants', parseInt(e.target.value))}
                  min="2"
                  max="128"
                />
              </div>
              <Button 
                type="button" 
                variant="outline" 
                size="sm"
                onClick={() => removeCategory(index)}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
            
            {showEloRanges && (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Min ELO</Label>
                  <Input
                    type="number"
                    step="0.1"
                    value={category.min_elo || ''}
                    onChange={(e) => updateCategory(index, 'min_elo', parseFloat(e.target.value))}
                    min="1.0"
                    max="5.0"
                    placeholder="1.0"
                  />
                </div>
                <div>
                  <Label>Max ELO</Label>
                  <Input
                    type="number"
                    step="0.1"
                    value={category.max_elo || ''}
                    onChange={(e) => updateCategory(index, 'max_elo', parseFloat(e.target.value))}
                    min="1.0"
                    max="5.0"
                    placeholder="5.0"
                  />
                </div>
              </div>
            )}
          </div>
        ))}
        
        {categories.length < Object.values(TournamentCategory).length && (
          <Button 
            type="button" 
            variant="outline" 
            onClick={addCategory}
            className="w-full"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Category
          </Button>
        )}
        
        {categories.length === 0 && (
          <p className="text-sm text-muted-foreground text-center py-4">
            Add at least one category to your tournament
          </p>
        )}
      </CardContent>
    </Card>
  );
}