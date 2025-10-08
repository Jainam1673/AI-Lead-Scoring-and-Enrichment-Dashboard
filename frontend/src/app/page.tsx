'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface Lead {
  id?: number;
  name: string;
  email: string;
  company: string;
  job_title: string;
  industry?: string;
  location?: string;
  score?: number;
  enriched_data?: object;
}

export default function Home() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

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
      const response = await fetch('http://localhost:8000/api/upload-leads', {
        method: 'POST',
        body: formData,
      });
      if (response.ok) {
        const data = await response.json();
        setLeads(data);
      } else {
        alert('Upload failed');
      }
    } catch (error) {
      console.error(error);
      alert('Error uploading file');
    }
    setLoading(false);
  };

  const fetchLeads = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/leads');
      if (response.ok) {
        const data = await response.json();
        setLeads(data);
      }
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">AI Lead Scoring Dashboard</h1>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Upload Leads CSV</CardTitle>
        </CardHeader>
        <CardContent>
          <Input type="file" accept=".csv" onChange={handleFileChange} className="mb-4" />
          <Button onClick={uploadFile} disabled={!file || loading}>
            {loading ? 'Uploading...' : 'Upload and Score'}
          </Button>
        </CardContent>
      </Card>

      <Button onClick={fetchLeads} className="mb-4">Load Sample Leads</Button>

      <Card>
        <CardHeader>
          <CardTitle>Scored Leads</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Company</TableHead>
                <TableHead>Job Title</TableHead>
                <TableHead>Score</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {leads.map((lead, index) => (
                <TableRow key={lead.id || index}>
                  <TableCell>{lead.name}</TableCell>
                  <TableCell>{lead.email}</TableCell>
                  <TableCell>{lead.company}</TableCell>
                  <TableCell>{lead.job_title}</TableCell>
                  <TableCell>{lead.score?.toFixed(2)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
