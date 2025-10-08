'use client';

import { useState } from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { ScoreBadge } from './ScoreBadge';
import { ArrowUpDown, ArrowUp, ArrowDown, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';

export interface Lead {
  id?: number;
  name: string;
  email: string;
  company: string;
  job_title: string;
  industry?: string;
  location?: string;
  company_size?: string;
  linkedin_url?: string;
  email_valid?: boolean;
  score: number;
  score_breakdown?: Record<string, unknown>;
  enriched?: boolean;
}

interface LeadTableProps {
  leads: Lead[];
}

type SortField = keyof Pick<Lead, 'name' | 'company' | 'job_title' | 'score' | 'industry' | 'company_size'>;
type SortDirection = 'asc' | 'desc' | null;

export function LeadTable({ leads }: LeadTableProps) {
  const [sortField, setSortField] = useState<SortField>('score');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      // Toggle direction or reset
      if (sortDirection === 'asc') {
        setSortDirection('desc');
      } else if (sortDirection === 'desc') {
        setSortDirection(null);
        setSortField('score');
      } else {
        setSortDirection('asc');
      }
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const sortedLeads = [...leads].sort((a, b) => {
    if (!sortDirection) return 0;

    let aValue = a[sortField];
    let bValue = b[sortField];

    // Handle undefined/null values
    if (aValue === undefined || aValue === null) return 1;
    if (bValue === undefined || bValue === null) return -1;

    // String comparison
    if (typeof aValue === 'string' && typeof bValue === 'string') {
      aValue = aValue.toLowerCase();
      bValue = bValue.toLowerCase();
    }

    if (sortDirection === 'asc') {
      if (aValue > bValue) return 1;
      if (aValue < bValue) return -1;
      return 0;
    } else {
      if (aValue < bValue) return 1;
      if (aValue > bValue) return -1;
      return 0;
    }
  });

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return <ArrowUpDown className="ml-2 h-4 w-4" />;
    if (sortDirection === 'asc') return <ArrowUp className="ml-2 h-4 w-4" />;
    if (sortDirection === 'desc') return <ArrowDown className="ml-2 h-4 w-4" />;
    return <ArrowUpDown className="ml-2 h-4 w-4" />;
  };

  const getEmailStatusBadge = (valid?: boolean) => {
    if (valid === undefined) return '?';
    return valid ? '✓' : '✗';
  };

  const getEmailStatusColor = (valid?: boolean) => {
    if (valid === undefined) return 'text-slate-500';
    return valid ? 'text-green-400' : 'text-red-400';
  };

  return (
    <div className="rounded-md border border-slate-800">
      <Table>
        <TableHeader>
          <TableRow className="border-slate-800 hover:bg-slate-800/50">
            <TableHead className="text-slate-300">
              <Button
                variant="ghost"
                onClick={() => handleSort('name')}
                className="font-semibold hover:bg-slate-700/50 hover:text-slate-100"
              >
                Name
                <SortIcon field="name" />
              </Button>
            </TableHead>
            <TableHead className="text-slate-300">Email</TableHead>
            <TableHead className="text-slate-300">
              <Button
                variant="ghost"
                onClick={() => handleSort('company')}
                className="font-semibold hover:bg-slate-700/50 hover:text-slate-100"
              >
                Company
                <SortIcon field="company" />
              </Button>
            </TableHead>
            <TableHead className="text-slate-300">
              <Button
                variant="ghost"
                onClick={() => handleSort('job_title')}
                className="font-semibold hover:bg-slate-700/50 hover:text-slate-100"
              >
                Job Title
                <SortIcon field="job_title" />
              </Button>
            </TableHead>
            <TableHead className="text-slate-300">
              <Button
                variant="ghost"
                onClick={() => handleSort('industry')}
                className="font-semibold hover:bg-slate-700/50 hover:text-slate-100"
              >
                Industry
                <SortIcon field="industry" />
              </Button>
            </TableHead>
            <TableHead className="text-slate-300">
              <Button
                variant="ghost"
                onClick={() => handleSort('company_size')}
                className="font-semibold hover:bg-slate-700/50 hover:text-slate-100"
              >
                Size
                <SortIcon field="company_size" />
              </Button>
            </TableHead>
            <TableHead className="text-slate-300">Location</TableHead>
            <TableHead className="text-slate-300">LinkedIn</TableHead>
            <TableHead className="text-center text-slate-300">Email Valid</TableHead>
            <TableHead className="text-slate-300">
              <Button
                variant="ghost"
                onClick={() => handleSort('score')}
                className="font-semibold hover:bg-slate-700/50 hover:text-slate-100"
              >
                Score
                <SortIcon field="score" />
              </Button>
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {sortedLeads.length === 0 ? (
            <TableRow className="border-slate-800">
              <TableCell colSpan={10} className="text-center text-slate-400">
                No leads found. Upload a CSV to get started.
              </TableCell>
            </TableRow>
          ) : (
            sortedLeads.map((lead, index) => (
              <TableRow key={lead.id || index} className="border-slate-800 hover:bg-slate-800/30">
                <TableCell className="font-medium text-slate-200">{lead.name}</TableCell>
                <TableCell className="text-sm text-slate-300">{lead.email}</TableCell>
                <TableCell className="text-slate-200">{lead.company}</TableCell>
                <TableCell className="text-sm text-slate-300">{lead.job_title}</TableCell>
                <TableCell className="text-sm capitalize text-slate-300">
                  {lead.industry || '-'}
                </TableCell>
                <TableCell className="text-sm text-slate-300">
                  {lead.company_size || '-'}
                </TableCell>
                <TableCell className="text-sm text-slate-300">{lead.location || '-'}</TableCell>
                <TableCell>
                  {lead.linkedin_url ? (
                    <a
                      href={lead.linkedin_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-400 hover:text-cyan-400 inline-flex items-center transition-colors"
                    >
                      <ExternalLink className="h-4 w-4" />
                    </a>
                  ) : (
                    <span className="text-slate-500">-</span>
                  )}
                </TableCell>
                <TableCell className="text-center">
                  <span className={`font-bold ${getEmailStatusColor(lead.email_valid)}`}>
                    {getEmailStatusBadge(lead.email_valid)}
                  </span>
                </TableCell>
                <TableCell>
                  <ScoreBadge score={lead.score} />
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  );
}
