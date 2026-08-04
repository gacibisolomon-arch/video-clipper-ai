import { ClippingService } from '../services/clippingService.js';

export async function processClipJob(jobPayload: unknown): Promise<void> {
  const clippingService = new ClippingService();
  await clippingService.createClip(jobPayload as any);
}
