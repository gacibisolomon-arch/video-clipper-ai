export interface TranscriptSegment {
  start: number;
  end: number;
  text: string;
  speaker?: string;
}

export interface ViralityAnalysis {
  score: number;
  reasons: string[];
  bestSegment: TranscriptSegment;
}

export interface ClipJobInput {
  sourceUrl: string;
  title?: string;
  targetDurationSec?: number;
  platform?: 'tiktok' | 'youtube' | 'instagram' | 'linkedin';
  enableSubtitle?: boolean;
  enableBroll?: boolean;
}

export interface ClipJobResult {
  outputPath: string;
  durationSec: number;
  viralityScore: number;
  subtitlePath?: string;
}
