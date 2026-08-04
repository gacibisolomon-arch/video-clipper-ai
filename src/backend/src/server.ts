import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import clipsRouter from './routes/clips.js';

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

app.get('/health', (_req, res) => {
  res.json({ status: 'ok', service: 'video-clipper-ai' });
});

app.use('/api', clipsRouter);

const port = Number(process.env.PORT ?? 4000);
app.listen(port, () => {
  console.log(`Backend listening on http://localhost:${port}`);
});
