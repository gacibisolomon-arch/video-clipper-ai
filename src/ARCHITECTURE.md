# Video Clipper AI Architecture Blueprint

## 1. System Goals
- Generate high-quality short-form clips from long-form video automatically.
- Score segments for virality using transcript heuristics and structure signals.
- Render clips with smart cropping, subtitles, and platform-specific formatting.
- Scale processing through queues and background workers.

## 2. Recommended Stack
- Frontend: Next.js App Router + TailwindCSS + shadcn/ui
- Backend: Node.js + Express + TypeScript
- Video Engine: FFmpeg + fluent-ffmpeg
- AI Layer: Python service or external AI API (Whisper/Deepgram, diarization, semantic segmentation)
- Data & Queue: PostgreSQL + Prisma + Redis + BullMQ

## 3. Top-Level Structure
```text
video-clipper-ai/
  src/
    backend/
      src/
        ai/
        routes/
        services/
        workers/
        types/
      prisma/
    frontend/
      app/
      public/
```

## 4. Processing Flow
1. User submits a video URL or upload.
2. Backend creates a processing job and stores metadata in PostgreSQL.
3. BullMQ worker picks up the job and orchestrates transcription + clipping.
4. FFmpeg renders the final short video and burns subtitles.
5. Result is persisted and returned to the frontend.
