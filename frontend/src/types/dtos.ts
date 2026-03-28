export interface SourceDto {
  id: string;
  url: string;
  name: string;
  source_type: string;
  schedule_hours: number | null;
  last_scraped_at: string | null;
  is_active: boolean;
  created_at: string;
}

export interface JobDto {
  id: string;
  source_id: string | null;
  trigger: string;
  status: string;
  chunks_stored: number;
  dupes_skipped: number;
  started_at: string;
  finished_at: string | null;
  error: string | null;
}
