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
    <Card className="border-slate-800 bg-slate-900/50 backdrop-blur">
      <CardHeader>
        <CardTitle className="text-slate-100">Filters</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Label htmlFor="search" className="text-slate-300">Search (Name, Company, Title)</Label>
          <Input
            id="search"
            placeholder="Search leads..."
            value={filters.searchTerm}
            onChange={(e) => updateFilter('searchTerm', e.target.value)}
            className="mt-1 bg-slate-800/50 border-slate-700 text-slate-100 placeholder:text-slate-500"
          />
        </div>

        <div>
          <Label htmlFor="industry" className="text-slate-300">Industry</Label>
          <Input
            id="industry"
            placeholder="e.g., tech, finance"
            value={filters.industry}
            onChange={(e) => updateFilter('industry', e.target.value)}
            className="mt-1 bg-slate-800/50 border-slate-700 text-slate-100 placeholder:text-slate-500"
          />
        </div>

        <div>
          <Label htmlFor="location" className="text-slate-300">Location</Label>
          <Input
            id="location"
            placeholder="e.g., San Francisco"
            value={filters.location}
            onChange={(e) => updateFilter('location', e.target.value)}
            className="mt-1 bg-slate-800/50 border-slate-700 text-slate-100 placeholder:text-slate-500"
          />
        </div>

        <div>
          <Label htmlFor="minScore" className="text-slate-300">
            Minimum Score: <span className="text-cyan-400 font-semibold">{filters.minScore}</span>
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
          <div className="flex justify-between text-xs text-slate-500 mt-1">
            <span>0</span>
            <span>50</span>
            <span>100</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
