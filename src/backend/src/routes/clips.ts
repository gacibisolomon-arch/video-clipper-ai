import { Router } from 'express';
import { ClippingService } from '../services/clippingService.js';

const router = Router();
const clippingService = new ClippingService();

router.post('/clip', async (req, res) => {
  try {
    const result = await clippingService.createClip(req.body);
    res.status(200).json(result);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

export default router;
