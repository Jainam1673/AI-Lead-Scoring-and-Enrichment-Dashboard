'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { CheckCircle2, Circle, XCircle, Loader2, AlertTriangle } from 'lucide-react';

interface StageResult {
  stage: string;
  status: string;
  duration: number;
  records_processed: number;
}

interface ProcessingProgressProps {
  currentStage: string;
  currentStageStatus: string;
  progressPercentage: number;
  totalRecords: number;
  processedRecords: number;
  successfulRecords: number;
  failedRecords: number;
  warningsCount: number;
  errorsCount: number;
  stageResults: StageResult[];
}

const stageNames: Record<string, string> = {
  'upload': '📤 Upload',
  'validation': '✓ Validation',
  'cleaning': '🧹 Cleaning',
  'feature_extraction': '🔍 Feature Extraction',
  'enrichment': '✨ Enrichment',
  'scoring': '🎯 Scoring',
  'quality_check': '✔️ Quality Check',
  'complete': '🎉 Complete'
};

const stageDescriptions: Record<string, string> = {
  'upload': 'Uploading file to server',
  'validation': 'Validating data format and required fields',
  'cleaning': 'Cleaning and normalizing data',
  'feature_extraction': 'Extracting features from raw data',
  'enrichment': 'Enriching leads with additional data',
  'scoring': 'Scoring leads using ML algorithm',
  'quality_check': 'Performing final quality checks',
  'complete': 'Processing complete!'
};

export function ProcessingProgress({
  currentStage,
  currentStageStatus,
  progressPercentage,
  totalRecords,
  processedRecords,
  successfulRecords,
  failedRecords,
  warningsCount,
  errorsCount,
  stageResults
}: ProcessingProgressProps) {
  
  const getStageIcon = (stageName: string, status: string) => {
    if (status === 'completed') {
      return <CheckCircle2 className="w-5 h-5 text-green-500" />;
    } else if (status === 'failed') {
      return <XCircle className="w-5 h-5 text-red-500" />;
    } else if (status === 'running') {
      return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
    } else {
      return <Circle className="w-5 h-5 text-gray-300" />;
    }
  };

  const stages = [
    'validation',
    'cleaning',
    'feature_extraction',
    'enrichment',
    'scoring',
    'quality_check',
    'complete'
  ];

  const getStageStatus = (stage: string): string => {
    const result = stageResults.find(r => r.stage === stage);
    if (result) return result.status;
    if (stage === currentStage) return currentStageStatus;
    return 'pending';
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Loader2 className="w-5 h-5 animate-spin text-blue-500" />
          Processing Your Leads
        </CardTitle>
        <CardDescription>
          Running ML pipeline to validate, clean, enrich, and score your leads
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Overall Progress Bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm text-gray-600">
            <span>Overall Progress</span>
            <span className="font-medium">{progressPercentage}%</span>
          </div>
          <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-500 transition-all duration-500 ease-out"
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
          <div className="text-sm text-gray-500">
            {stageDescriptions[currentStage] || 'Processing...'}
          </div>
        </div>

        {/* Stage Progress */}
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-gray-700">Processing Stages</h4>
          <div className="space-y-2">
            {stages.map((stage, index) => {
              const status = getStageStatus(stage);
              const result = stageResults.find(r => r.stage === stage);
              const isActive = stage === currentStage;
              
              return (
                <div
                  key={stage}
                  className={`flex items-center gap-3 p-3 rounded-lg border transition-all ${
                    isActive
                      ? 'bg-blue-50 border-blue-200'
                      : status === 'completed'
                      ? 'bg-green-50 border-green-200'
                      : status === 'failed'
                      ? 'bg-red-50 border-red-200'
                      : 'bg-gray-50 border-gray-200'
                  }`}
                >
                  <div className="flex-shrink-0">
                    {getStageIcon(stage, status)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-900">
                        {stageNames[stage] || stage}
                      </span>
                      {result && (
                        <span className="text-xs text-gray-500">
                          {result.duration.toFixed(2)}s
                        </span>
                      )}
                    </div>
                    {isActive && status === 'running' && (
                      <div className="text-xs text-gray-600 mt-1">
                        {stageDescriptions[stage]}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{totalRecords}</div>
            <div className="text-xs text-gray-600">Total Records</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{successfulRecords}</div>
            <div className="text-xs text-gray-600">Successful</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">{failedRecords}</div>
            <div className="text-xs text-gray-600">Failed</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-600">{warningsCount}</div>
            <div className="text-xs text-gray-600">Warnings</div>
          </div>
        </div>

        {/* Warnings/Errors Display */}
        {(warningsCount > 0 || errorsCount > 0) && (
          <div className="space-y-2">
            {warningsCount > 0 && (
              <div className="flex items-start gap-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <AlertTriangle className="w-4 h-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                <div className="text-sm text-yellow-800">
                  <strong>{warningsCount} warning{warningsCount > 1 ? 's' : ''}</strong> detected during processing.
                  Some data may need review.
                </div>
              </div>
            )}
            {errorsCount > 0 && (
              <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
                <XCircle className="w-4 h-4 text-red-600 mt-0.5 flex-shrink-0" />
                <div className="text-sm text-red-800">
                  <strong>{errorsCount} error{errorsCount > 1 ? 's' : ''}</strong> occurred during processing.
                  Some records may have been skipped.
                </div>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
