import { TranscriptSegment, ViralityAnalysis } from '../types/index.js';

export class ViralityService {
  public analyzeTranscript(segments: TranscriptSegment[]): ViralityAnalysis {
    const scoredSegments = segments.map((segment) => {
      const wordCount = segment.text.trim().split(/\s+/).filter(Boolean).length;
      const words = segment.text.toLowerCase().split(/\s+/).filter(Boolean);
      const emotionalWords = words.filter((word) => this.emotionalLexicon.has(word));
      const hookSignals = words.filter((word) => this.hookWords.has(word));
      const density = (emotionalWords.length + hookSignals.length * 1.5) / Math.max(1, wordCount);
      const pacing = this.scorePacing(segment.start, segment.end, wordCount);
      const structure = this.scoreStructure(segment.text);
      const score = Math.min(100, Math.round((density * 45 + pacing * 25 + structure * 30) * 100));

      return { segment, score };
    });

    const best = scoredSegments.sort((a, b) => b.score - a.score)[0];

    return {
      score: best.score,
      reasons: this.explain(best.score, best.segment),
      bestSegment: best.segment,
    };
  }

  private scorePacing(start: number, end: number, wordCount: number): number {
    const duration = Math.max(1, end - start);
    const wordsPerSecond = wordCount / duration;
    return Math.max(0, Math.min(1, wordsPerSecond / 2.3));
  }

  private scoreStructure(text: string): number {
    const questionMarks = (text.match(/\?/g) ?? []).length;
    const exclamations = (text.match(/!/g) ?? []).length;
    const uppercaseRatio = (text.match(/[A-Z]{3,}/g) ?? []).length > 0 ? 0.2 : 0;
    return Math.min(1, 0.4 + questionMarks * 0.1 + exclamations * 0.1 + uppercaseRatio);
  }

  private explain(score: number, segment: TranscriptSegment): string[] {
    const reasons: string[] = [];

    if (score >= 80) reasons.push('High emotional intensity and strong curiosity hook');
    if (segment.text.length > 80) reasons.push('The segment has substantial narrative depth');
    reasons.push('Good pacing for short-form retention');
    return reasons;
  }

  private readonly emotionalLexicon = new Set([
    'amazing', 'incredible', 'crazy', 'shocking', 'unexpected', 'terrible', 'beautiful',
    'powerful', 'surprising', 'honestly', 'wow', 'must', 'never', 'always', 'finally',
    'secret', 'truth', 'disaster', 'breakthrough', 'game-changing', 'dangerous'
  ]);

  private readonly hookWords = new Set([
    'why', 'how', 'when', 'what', 'stop', 'secret', 'truth', 'mistake', 'mistakes',
    'best', 'worst', 'failed', 'succeed', 'real', 'hack', 'today', 'now', 'before'
  ]);
}
