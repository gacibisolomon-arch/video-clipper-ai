import fs from 'fs/promises';
import path from 'path';
import ffmpeg from 'fluent-ffmpeg';
import { ViralityService } from '../ai/viralityService.js';
import { ClipJobInput, ClipJobResult, TranscriptSegment } from '../types/index.js';

export class ClippingService {
  private readonly viralityService = new ViralityService();
  private readonly outputDir = path.resolve(process.cwd(), '..', 'output');
  private readonly tempDir = path.resolve(process.cwd(), '..', 'downloads');

  constructor() {
    this.ensureDirectories();
  }

  public async createClip(job: ClipJobInput): Promise<ClipJobResult> {
    const transcript: TranscriptSegment[] = [
      { start: 0, end: 6, text: 'This is the strongest hook from the source video because it creates curiosity and momentum.' },
      { start: 6, end: 12, text: 'You can use this segment to frame the narrative around a surprising outcome or lesson.' },
      { start: 12, end: 18, text: 'The final beat delivers a clear payoff and makes the clip feel complete and shareable.' }
    ];

    const analysis = this.viralityService.analyzeTranscript(transcript);
    const best = analysis.bestSegment;
    const start = Math.max(0, best.start);
    const end = Math.min(30, Math.max(best.end, start + (job.targetDurationSec ?? 20)));

    const outputPath = path.join(this.outputDir, `${this.slugify(job.title ?? 'clip')}-${Date.now()}.mp4`);
    const subtitlePath = path.join(this.outputDir, `${this.slugify(job.title ?? 'clip')}-${Date.now()}.srt`);

    await this.generateSubtitleFile(subtitlePath, transcript, start, end);
    await this.renderVideo(job.sourceUrl, start, end, outputPath, subtitlePath, job.platform ?? 'youtube');

    return {
      outputPath,
      durationSec: Math.max(1, end - start),
      viralityScore: analysis.score,
      subtitlePath,
    };
  }

  private async renderVideo(
    sourceUrl: string,
    start: number,
    end: number,
    outputPath: string,
    subtitlePath: string,
    platform: string
  ): Promise<void> {
    const input = path.resolve(this.tempDir, 'source.mp4');

    await this.ensureSourceFile(sourceUrl, input);

    await new Promise<void>((resolve, reject) => {
      ffmpeg(input)
        .setStartTime(start)
        .setDuration(Math.max(1, end - start))
        .videoFilters([
          this.platformCropFilter(platform),
          'scale=1080:1920:force_original_aspect_ratio=decrease',
          'pad=1080:1920:(ow-iw)/2:(oh-ih)/2'
        ])
        .outputOptions([
          '-c:v libx264',
          '-pix_fmt yuv420p',
          '-crf 20',
          '-c:a aac',
          '-b:a 192k',
          '-movflags +faststart',
          '-vf', `subtitles=${subtitlePath}:force_style='FontName=Arial,FontSize=34,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H00000000,Alignment=2,MarginV=40'`
        ])
        .save(outputPath)
        .on('end', resolve)
        .on('error', reject);
    });
  }

  private platformCropFilter(platform: string): string {
    switch (platform) {
      case 'tiktok':
      case 'instagram':
        return 'crop=1080:1920:iw/2-540:ih/2-960';
      case 'linkedin':
        return 'scale=1280:720';
      case 'youtube':
      default:
        return 'scale=1280:720';
    }
  }

  private async ensureSourceFile(sourceUrl: string, destination: string): Promise<void> {
    await fs.mkdir(path.dirname(destination), { recursive: true });
    if (await this.fileExists(destination)) return;

    await new Promise<void>((resolve, reject) => {
      ffmpeg()
        .input(sourceUrl)
        .output(destination)
        .on('end', resolve)
        .on('error', reject)
        .run();
    });
  }

  private async generateSubtitleFile(subtitlePath: string, segments: TranscriptSegment[], start: number, end: number): Promise<void> {
    const relevant = segments.filter((segment) => segment.start >= start && segment.end <= end);
    const lines = relevant.map((segment, index) => {
      const startTs = this.formatSrtTime(segment.start);
      const endTs = this.formatSrtTime(segment.end);
      return `${index + 1}\n${startTs} --> ${endTs}\n${segment.text}\n`;
    });

    await fs.writeFile(subtitlePath, lines.join('\n'), 'utf8');
  }

  private formatSrtTime(seconds: number): string {
    const hrs = String(Math.floor(seconds / 3600)).padStart(2, '0');
    const mins = String(Math.floor((seconds % 3600) / 60)).padStart(2, '0');
    const secs = String(Math.floor(seconds % 60)).padStart(2, '0');
    const millis = String(Math.round((seconds % 1) * 1000)).padStart(3, '0');
    return `${hrs}:${mins}:${secs},${millis}`;
  }

  private async ensureDirectories(): Promise<void> {
    await fs.mkdir(this.outputDir, { recursive: true });
    await fs.mkdir(this.tempDir, { recursive: true });
  }

  private async fileExists(filePath: string): Promise<boolean> {
    try {
      await fs.access(filePath);
      return true;
    } catch {
      return false;
    }
  }

  private slugify(value: string): string {
    return value.toLowerCase().trim().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
  }
}
