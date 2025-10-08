"""
ML Pipeline Manager
Orchestrates all data processing stages with progress tracking and error handling
"""
import pandas as pd
from typing import List, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class ProcessingStage(str, Enum):
    """Processing pipeline stages"""
    UPLOAD = "upload"
    VALIDATION = "validation"
    CLEANING = "cleaning"
    FEATURE_EXTRACTION = "feature_extraction"
    ENRICHMENT = "enrichment"
    SCORING = "scoring"
    QUALITY_CHECK = "quality_check"
    COMPLETE = "complete"


class StageStatus(str, Enum):
    """Status of a processing stage"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StageResult:
    """Result of a processing stage"""
    stage: ProcessingStage
    status: StageStatus
    message: str
    duration_seconds: float
    records_processed: int
    records_succeeded: int
    records_failed: int
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineProgress:
    """Current pipeline progress"""
    current_stage: ProcessingStage
    current_stage_status: StageStatus
    total_stages: int
    completed_stages: int
    progress_percentage: int
    total_records: int
    processed_records: int
    successful_records: int
    failed_records: int
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    stage_results: List[StageResult] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    estimated_completion_time: float | None = None


@dataclass
class PipelineResult:
    """Final result of pipeline execution"""
    success: bool
    total_duration_seconds: float
    input_records: int
    output_records: int
    success_rate: float
    stage_results: List[StageResult]
    progress: PipelineProgress
    data: Any  # Processed data (DataFrame or list of leads)
    quality_report: Dict[str, Any]


class ProcessingPipeline:
    """
    ML Pipeline Manager
    Handles all data processing stages with progress tracking and error recovery
    """
    
    def __init__(self):
        self.progress = PipelineProgress(
            current_stage=ProcessingStage.UPLOAD,
            current_stage_status=StageStatus.PENDING,
            total_stages=7,  # Total processing stages
            completed_stages=0,
            progress_percentage=0,
            total_records=0,
            processed_records=0,
            successful_records=0,
            failed_records=0
        )
        self.stage_results: List[StageResult] = []
        self.started_at = time.time()
        
    def get_progress(self) -> PipelineProgress:
        """Get current pipeline progress"""
        return self.progress
    
    def _update_stage(self, stage: ProcessingStage, status: StageStatus):
        """Update current stage and status"""
        self.progress.current_stage = stage
        self.progress.current_stage_status = status
        self.progress.completed_stages = len([r for r in self.stage_results if r.status == StageStatus.COMPLETED])
        self.progress.progress_percentage = int((self.progress.completed_stages / self.progress.total_stages) * 100)
        
    def _record_stage_result(self, result: StageResult):
        """Record stage result and update progress"""
        self.stage_results.append(result)
        self.progress.stage_results.append(result)
        
        if result.warnings:
            self.progress.warnings.extend(result.warnings)
        if result.errors:
            self.progress.errors.extend(result.errors)
        
        self.progress.successful_records = sum(r.records_succeeded for r in self.stage_results)
        self.progress.failed_records = sum(r.records_failed for r in self.stage_results)
        
    def _execute_stage(
        self,
        stage: ProcessingStage,
        stage_function: Callable,
        data: Any,
        stage_name: str
    ) -> tuple[Any, StageResult]:
        """
        Execute a processing stage with error handling
        
        Args:
            stage: Processing stage enum
            stage_function: Function to execute
            data: Input data
            stage_name: Human-readable stage name
            
        Returns:
            Tuple of (processed_data, stage_result)
        """
        self._update_stage(stage, StageStatus.RUNNING)
        logger.info(f"Starting stage: {stage_name}")
        
        stage_start = time.time()
        
        try:
            # Execute the stage function
            result_data, stage_metadata = stage_function(data)
            
            duration = time.time() - stage_start
            
            # Extract metrics from metadata
            records_processed = stage_metadata.get('records_processed', 0)
            records_succeeded = stage_metadata.get('records_succeeded', 0)
            records_failed = stage_metadata.get('records_failed', 0)
            warnings = stage_metadata.get('warnings', [])
            errors = stage_metadata.get('errors', [])
            
            # Create stage result
            stage_result = StageResult(
                stage=stage,
                status=StageStatus.COMPLETED,
                message=f"{stage_name} completed successfully",
                duration_seconds=duration,
                records_processed=records_processed,
                records_succeeded=records_succeeded,
                records_failed=records_failed,
                warnings=warnings,
                errors=errors,
                metadata=stage_metadata
            )
            
            self._record_stage_result(stage_result)
            self._update_stage(stage, StageStatus.COMPLETED)
            
            logger.info(f"Completed stage: {stage_name} ({duration:.2f}s)")
            
            return result_data, stage_result
            
        except Exception as e:
            duration = time.time() - stage_start
            error_msg = f"{stage_name} failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            stage_result = StageResult(
                stage=stage,
                status=StageStatus.FAILED,
                message=error_msg,
                duration_seconds=duration,
                records_processed=0,
                records_succeeded=0,
                records_failed=self.progress.total_records,
                errors=[error_msg]
            )
            
            self._record_stage_result(stage_result)
            self._update_stage(stage, StageStatus.FAILED)
            
            raise Exception(f"Pipeline failed at {stage_name}: {str(e)}")
    
    def execute(
        self,
        df: pd.DataFrame,
        validation_func: Callable,
        cleaning_func: Callable,
        feature_extraction_func: Callable,
        enrichment_func: Callable,
        scoring_func: Callable,
        quality_check_func: Callable
    ) -> PipelineResult:
        """
        Execute the full ML pipeline
        
        Args:
            df: Input DataFrame
            validation_func: Validation function
            cleaning_func: Cleaning function
            feature_extraction_func: Feature extraction function
            enrichment_func: Enrichment function
            scoring_func: Scoring function
            quality_check_func: Quality check function
            
        Returns:
            PipelineResult with processed data and metrics
        """
        self.progress.total_records = len(df)
        pipeline_start = time.time()
        
        try:
            # Stage 1: Validation
            validated_df, validation_result = self._execute_stage(
                ProcessingStage.VALIDATION,
                validation_func,
                df,
                "Data Validation"
            )
            
            # Stage 2: Cleaning
            cleaned_df, cleaning_result = self._execute_stage(
                ProcessingStage.CLEANING,
                cleaning_func,
                validated_df,
                "Data Cleaning"
            )
            
            # Stage 3: Feature Extraction
            extracted_df, extraction_result = self._execute_stage(
                ProcessingStage.FEATURE_EXTRACTION,
                feature_extraction_func,
                cleaned_df,
                "Feature Extraction"
            )
            
            # Stage 4: Enrichment
            enriched_df, enrichment_result = self._execute_stage(
                ProcessingStage.ENRICHMENT,
                enrichment_func,
                extracted_df,
                "Data Enrichment"
            )
            
            # Stage 5: Scoring
            scored_data, scoring_result = self._execute_stage(
                ProcessingStage.SCORING,
                scoring_func,
                enriched_df,
                "Lead Scoring"
            )
            
            # Stage 6: Quality Check
            final_data, quality_result = self._execute_stage(
                ProcessingStage.QUALITY_CHECK,
                quality_check_func,
                scored_data,
                "Quality Check"
            )
            
            # Mark as complete
            self._update_stage(ProcessingStage.COMPLETE, StageStatus.COMPLETED)
            
            total_duration = time.time() - pipeline_start
            output_records = len(final_data) if hasattr(final_data, '__len__') else 0
            success_rate = (output_records / self.progress.total_records * 100) if self.progress.total_records > 0 else 0
            
            # Generate quality report
            quality_report = self._generate_quality_report(final_data, quality_result)
            
            logger.info(f"Pipeline completed successfully in {total_duration:.2f}s")
            
            return PipelineResult(
                success=True,
                total_duration_seconds=total_duration,
                input_records=self.progress.total_records,
                output_records=output_records,
                success_rate=success_rate,
                stage_results=self.stage_results,
                progress=self.progress,
                data=final_data,
                quality_report=quality_report
            )
            
        except Exception as e:
            total_duration = time.time() - pipeline_start
            logger.error(f"Pipeline failed: {str(e)}")
            
            return PipelineResult(
                success=False,
                total_duration_seconds=total_duration,
                input_records=self.progress.total_records,
                output_records=0,
                success_rate=0.0,
                stage_results=self.stage_results,
                progress=self.progress,
                data=None,
                quality_report={}
            )
    
    def _generate_quality_report(self, data: Any, quality_result: StageResult) -> Dict[str, Any]:
        """Generate comprehensive quality report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_records': self.progress.total_records,
            'processed_records': self.progress.processed_records,
            'successful_records': self.progress.successful_records,
            'failed_records': self.progress.failed_records,
            'success_rate': (self.progress.successful_records / self.progress.total_records * 100) if self.progress.total_records > 0 else 0,
            'total_warnings': len(self.progress.warnings),
            'total_errors': len(self.progress.errors),
            'stage_summary': [
                {
                    'stage': result.stage,
                    'status': result.status,
                    'duration': result.duration_seconds,
                    'records_processed': result.records_processed,
                    'success_rate': (result.records_succeeded / result.records_processed * 100) if result.records_processed > 0 else 0
                }
                for result in self.stage_results
            ]
        }
        
        # Add quality metrics from quality_result metadata
        if quality_result.metadata:
            report['quality_metrics'] = quality_result.metadata
        
        return report
