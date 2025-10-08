'use client';

import { useState, useMemo } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { LeadTable, Lead } from '@/components/LeadTable';
import { FiltersPanel, FilterState } from '@/components/FiltersPanel';
import { Upload, Download, RefreshCw, BarChart3, Trash2 } from 'lucide-react';
import { toast, Toaster } from 'sonner';

export default function Home() {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
  const [leads, setLeads] = useState<Lead[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState<FilterState>({
    searchTerm: '',
    industry: '',
    location: '',
    minScore: 0,
  });

  const handleFiltersChange = (next: FilterState) => {
    setFilters(next);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const uploadFile = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      toast.loading('Uploading and processing leads...', { id: 'upload' });
      const response = await fetch(`${apiBaseUrl}/api/upload-leads`, {
        method: 'POST',
        body: formData,
      });
      if (response.ok) {
        const data: Lead[] = await response.json();
        setLeads(data);
        toast.success(`Successfully processed ${data.length} leads!`, { id: 'upload' });
      } else {
        const error = await response.json();
        toast.error(`Upload failed: ${error.detail || 'Unknown error'}`, { id: 'upload' });
      }
    } catch (error) {
      console.error(error);
      toast.error('Error uploading file. Make sure the backend is running.', { id: 'upload' });
    }
    setLoading(false);
  };

  const fetchLeads = async () => {
    setLoading(true);
    try {
      toast.loading('Loading sample leads...', { id: 'fetch' });
      const response = await fetch(`${apiBaseUrl}/api/leads`);
      if (response.ok) {
        const data: Lead[] = await response.json();
        setLeads(data);
        toast.success(`Loaded ${data.length} sample leads!`, { id: 'fetch' });
      } else {
        toast.error('Failed to load leads', { id: 'fetch' });
      }
    } catch (error) {
      console.error(error);
      toast.error('Error fetching leads. Make sure the backend is running.', { id: 'fetch' });
    }
    setLoading(false);
  };

  const exportLeads = async () => {
    try {
      toast.loading('Exporting leads...', { id: 'export' });
      const response = await fetch(`${apiBaseUrl}/api/export`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'scored_leads.csv';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        toast.success('Leads exported successfully!', { id: 'export' });
      } else {
        toast.error('No leads to export', { id: 'export' });
      }
    } catch (error) {
      console.error(error);
      toast.error('Error exporting leads', { id: 'export' });
    }
  };

  const clearLeads = async () => {
    if (!confirm('Are you sure you want to clear all leads?')) return;
    
    try {
      toast.loading('Clearing leads...', { id: 'clear' });
      const response = await fetch(`${apiBaseUrl}/api/leads`, {
        method: 'DELETE',
      });
      if (response.ok) {
        setLeads([]);
        toast.success('All leads cleared!', { id: 'clear' });
      } else {
        toast.error('Failed to clear leads', { id: 'clear' });
      }
    } catch (error) {
      console.error(error);
      toast.error('Error clearing leads', { id: 'clear' });
    }
  };

  // Apply filters
  const filteredLeads = useMemo(() => {
    return leads.filter((lead) => {
      // Search term filter
      const searchLower = filters.searchTerm.toLowerCase();
      const matchesSearch =
        !filters.searchTerm ||
        lead.name.toLowerCase().includes(searchLower) ||
        lead.company.toLowerCase().includes(searchLower) ||
        lead.job_title.toLowerCase().includes(searchLower);

      // Industry filter
      const matchesIndustry =
        !filters.industry ||
        (lead.industry?.toLowerCase().includes(filters.industry.toLowerCase()) ?? false);

      // Location filter
      const matchesLocation =
        !filters.location ||
        (lead.location?.toLowerCase().includes(filters.location.toLowerCase()) ?? false);

      // Score filter
      const matchesScore = lead.score >= filters.minScore;

      return matchesSearch && matchesIndustry && matchesLocation && matchesScore;
    });
  }, [leads, filters]);

  // Statistics
  const stats = useMemo(() => {
    if (filteredLeads.length === 0) {
      return { total: 0, avgScore: 0, highQuality: 0, validEmails: 0 };
    }

    const total = filteredLeads.length;
    const avgScore =
      filteredLeads.reduce((sum, lead) => sum + lead.score, 0) / total;
    const highQuality = filteredLeads.filter((lead) => lead.score >= 70).length;
    const validEmails = filteredLeads.filter((lead) => lead.email_valid === true).length;

    return { total, avgScore, highQuality, validEmails };
  }, [filteredLeads]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <Toaster position="top-right" richColors />
      <div className="container mx-auto p-6 space-y-6">
        {/* Header */}
        <div className="space-y-2">
          <h1 className="text-4xl font-bold tracking-tight bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
            AI Lead Scoring & Enrichment Dashboard
          </h1>
          <p className="text-slate-400">
            Upload leads, enrich with company data, and prioritize with AI-powered scoring
          </p>
        </div>

        {/* Upload Section */}
        <Card className="border-slate-800 bg-slate-900/50 backdrop-blur">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-slate-100">
              <Upload className="h-5 w-5 text-blue-400" />
              Upload & Process Leads
            </CardTitle>
            <CardDescription className="text-slate-400">
              Upload a CSV file with columns: name, email, company, job_title, location (optional), industry (optional)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4 items-end">
              <div className="flex-1">
                <Input
                  type="file"
                  accept=".csv"
                  onChange={handleFileChange}
                  disabled={loading}
                />
              </div>
              <Button onClick={uploadFile} disabled={!file || loading} className="gap-2">
                <Upload className="h-4 w-4" />
                {loading ? 'Processing...' : 'Upload & Score'}
              </Button>
              <Button onClick={fetchLeads} variant="outline" disabled={loading} className="gap-2">
                <RefreshCw className="h-4 w-4" />
                Load Sample
              </Button>
              <Button
                onClick={exportLeads}
                variant="outline"
                disabled={leads.length === 0}
                className="gap-2"
              >
                <Download className="h-4 w-4" />
                Export CSV
              </Button>
              <Button
                onClick={clearLeads}
                variant="outline"
                disabled={leads.length === 0}
                className="gap-2 border-red-800 text-red-400 hover:bg-red-950/50 hover:text-red-300"
              >
                <Trash2 className="h-4 w-4" />
                Clear Leads
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Statistics Cards */}
        {leads.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="border-slate-800 bg-slate-900/50 backdrop-blur">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-slate-400">
                  Total Leads
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-slate-100">{stats.total}</div>
              </CardContent>
            </Card>
            <Card className="border-slate-800 bg-slate-900/50 backdrop-blur">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-slate-400">
                  Average Score
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-slate-100">{stats.avgScore.toFixed(1)}</div>
              </CardContent>
            </Card>
            <Card className="border-slate-800 bg-slate-900/50 backdrop-blur">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-slate-400">
                  High Quality (≥70)
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-400">{stats.highQuality}</div>
              </CardContent>
            </Card>
            <Card className="border-slate-800 bg-slate-900/50 backdrop-blur">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-slate-400">
                  Valid Emails
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-blue-400">{stats.validEmails}</div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Main Content: Filters + Table */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Filters Sidebar */}
          <div className="lg:col-span-1">
            <FiltersPanel filters={filters} onFilterChange={handleFiltersChange} />
          </div>

          {/* Leads Table */}
          <div className="lg:col-span-3">
            <Card className="border-slate-800 bg-slate-900/50 backdrop-blur">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-slate-100">
                  <BarChart3 className="h-5 w-5 text-cyan-400" />
                  Enriched & Scored Leads ({filteredLeads.length})
                </CardTitle>
                <CardDescription className="text-slate-400">
                  Click column headers to sort. All leads are enriched with company size, industry, and LinkedIn profiles.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <LeadTable leads={filteredLeads} />
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
