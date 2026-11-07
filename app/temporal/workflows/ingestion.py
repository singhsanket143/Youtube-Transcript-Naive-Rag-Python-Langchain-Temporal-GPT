
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

from temporalio import workflow


DEFAULT_INDEX_BATCH_SIZE = 100

with workflow.unsafe.imports_passed_through():
    from app.temporal.activities.ingestion import (
        parse_documents_activity,
        chunk_documents_activity,
        index_documents_activity,
        ingest_file_activity,
        parse_documents_to_jsonl_activity,
        chunk_documents_from_jsonl_activity,
        index_documents_from_jsonl_activity,
    )

@dataclass
class FileIngestInput:
    filename: str 
    local_path: str

@dataclass
class BatchIngestProgress:
    status: str = "RUNNING"
    files_total: int = 0
    files_completed: int = 0
    current_filename: str | None = None 
    file_results: list[dict[str, Any]] = field(default_factory=list)


@workflow.defn(name="batch-ingestion-workflow")
class BatchIngestionWorkflow:
    """Workflow to ingest a batch of files into the vector store."""

    def __init__(self) -> None:
        self.progress = BatchIngestProgress()

    @workflow.query
    def get_progress(self) -> BatchIngestProgress:
        return self.progress

    @workflow.run
    async def run(self, files: list[FileIngestInput]) -> BatchIngestProgress:
        """Workflow to ingest a batch of files into the vector store."""

        batch_size = DEFAULT_INDEX_BATCH_SIZE
        self.progress.files_total = len(files)
        self.progress.status = "RUNNING" 

        for file_input in files:  # if we are processing everything as one activity , then we can do parallel processing also
            self.progress.current_filename = file_input.filename

            parsed = await workflow.execute_activity(
                parse_documents_to_jsonl_activity,
                args=[file_input.local_path, file_input.filename],
                start_to_close_timeout=timedelta(minutes=30),
            )

            chunks = await workflow.execute_activity(
                chunk_documents_from_jsonl_activity,
                args=[parsed["write_path"], file_input.filename],
                start_to_close_timeout=timedelta(minutes=30),
            )

            chunks_count = chunks["chunks_count"]
            chunks_path = chunks["chunks_path"]

            indexed = 0

            for start in range(0, chunks_count, batch_size):
                count = await workflow.execute_activity(
                    index_documents_from_jsonl_activity,
                    args=[chunks_path, start, batch_size],
                    start_to_close_timeout=timedelta(minutes=30),
                    heartbeat_timeout=timedelta(minutes=5),
                )
                indexed += count

            # todo: write a cleanup activity to delete the parsed and chunks files

            
            
            self.progress.files_completed += 1
            self.progress.file_results.append({
                "filename": file_input.filename,
                "chunks_created": indexed,
                "document_ids": []
            })

        self.progress.status = "COMPLETED"
        self.progress.current_filename = None 
        return self.progress


