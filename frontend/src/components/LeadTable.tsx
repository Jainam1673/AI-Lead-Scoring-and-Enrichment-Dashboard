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
    if (valid === undefined) return 'text-gray-500';
    return valid ? 'text-green-600' : 'text-red-600';
  };

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>
              <Button
                variant="ghost"
                onClick={() => handleSort('name')}
                className="font-semibold"
              >
                Name
                <SortIcon field="name" />
              </Button>
            </TableHead>
            <TableHead>Email</TableHead>
            <TableHead>
              <Button
                variant="ghost"
                onClick={() => handleSort('company')}
                className="font-semibold"
              >
                Company
                <SortIcon field="company" />
              </Button>
            </TableHead>
            <TableHead>
              <Button
                variant="ghost"
                onClick={() => handleSort('job_title')}
                className="font-semibold"
              >
                Job Title
                <SortIcon field="job_title" />
              </Button>
            </TableHead>
            <TableHead>
              <Button
                variant="ghost"
                onClick={() => handleSort('industry')}
                className="font-semibold"
              >
                Industry
                <SortIcon field="industry" />
              </Button>
            </TableHead>
            <TableHead>
              <Button
                variant="ghost"
                onClick={() => handleSort('company_size')}
                className="font-semibold"
              >
                Size
                <SortIcon field="company_size" />
              </Button>
            </TableHead>
            <TableHead>Location</TableHead>
            <TableHead>LinkedIn</TableHead>
            <TableHead className="text-center">Email Valid</TableHead>
            <TableHead>
              <Button
                variant="ghost"
                onClick={() => handleSort('score')}
                className="font-semibold"
              >
                Score
                <SortIcon field="score" />
              </Button>
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {sortedLeads.length === 0 ? (
            <TableRow>
              <TableCell colSpan={10} className="text-center text-muted-foreground">
                No leads found. Upload a CSV to get started.
              </TableCell>
            </TableRow>
          ) : (
            sortedLeads.map((lead, index) => (
              <TableRow key={lead.id || index}>
                <TableCell className="font-medium">{lead.name}</TableCell>
                <TableCell className="text-sm">{lead.email}</TableCell>
                <TableCell>{lead.company}</TableCell>
                <TableCell className="text-sm">{lead.job_title}</TableCell>
                <TableCell className="text-sm capitalize">
                  {lead.industry || '-'}
                </TableCell>
                <TableCell className="text-sm">
                  {lead.company_size || '-'}
                </TableCell>
                <TableCell className="text-sm">{lead.location || '-'}</TableCell>
                <TableCell>
                  {lead.linkedin_url ? (
                    <a
                      href={lead.linkedin_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 inline-flex items-center"
                    >
                      <ExternalLink className="h-4 w-4" />
                    </a>
                  ) : (
                    '-'
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
