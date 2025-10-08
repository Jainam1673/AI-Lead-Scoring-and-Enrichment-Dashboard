'use client';

import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';

export type FilterState = {
  searchTerm: string;
  industry: string;
  location: string;
  minScore: number;
};

interface FiltersPanelProps {
  filters: FilterState;
  onFilterChange: (filters: FilterState) => void;
}

export function FiltersPanel({ filters, onFilterChange }: FiltersPanelProps) {
  const updateFilter = (key: keyof FilterState, value: FilterState[keyof FilterState]) => {
    onFilterChange({ ...filters, [key]: value });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Filters</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Label htmlFor="search">Search (Name, Company, Title)</Label>
          <Input
            id="search"
            placeholder="Search leads..."
            value={filters.searchTerm}
            onChange={(e) => updateFilter('searchTerm', e.target.value)}
            className="mt-1"
          />
        </div>

        <div>
          <Label htmlFor="industry">Industry</Label>
          <Input
            id="industry"
            placeholder="e.g., tech, finance"
            value={filters.industry}
            onChange={(e) => updateFilter('industry', e.target.value)}
            className="mt-1"
          />
        </div>

        <div>
          <Label htmlFor="location">Location</Label>
          <Input
            id="location"
            placeholder="e.g., San Francisco"
            value={filters.location}
            onChange={(e) => updateFilter('location', e.target.value)}
            className="mt-1"
          />
        </div>

        <div>
          <Label htmlFor="minScore">
            Minimum Score: {filters.minScore}
          </Label>
          <Slider
            id="minScore"
            min={0}
            max={100}
            step={5}
            value={[filters.minScore]}
            onValueChange={(value: number[]) => updateFilter('minScore', value[0])}
            className="mt-2"
          />
          <div className="flex justify-between text-xs text-muted-foreground mt-1">
            <span>0</span>
            <span>50</span>
            <span>100</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
