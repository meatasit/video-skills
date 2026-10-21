# Attribution — skill ที่ vendor มา

| โฟลเดอร์ | ต้นทาง | commit (vendor เมื่อ 2026-10-20) | license |
| --- | --- | --- | --- |
| skills/ffmpeg-skill | https://github.com/kajisho5/ffmpeg-skill | f02bab4 (2026-10-20) | MIT |
| skills/video-editing-skill | https://github.com/6missedcalls/video-editing-skill | 7dc6e1d (2026-02-27) | MIT |
| skills/whisper-transcription | https://github.com/guia-matthieu/clawfu-skills (skills/automation/whisper-transcription) | 4108f5c (2026-10-01) | MIT |
| skills/video-production | https://github.com/travisjneuman/.claude (skills/video-production) | 7a2b5ca (2026-10-19) | MIT |
| skills/color-grade-ai | https://github.com/isaacrowntree/color-grade-ai | a6eef94 (2026-08-03) | MIT |
| skills/color-grading-skill | https://github.com/kajisho5/color-grading-skill | 6c45c9f (2026-10-17) | MIT |
| agents/upstream-agent-video-producer.md | https://github.com/travisjneuman/.claude (skills/agent-video-producer) | 7a2b5ca | MIT |

ไม่ vendor (ติดตั้งผ่าน `npx skills add` แทน):
- https://github.com/remotion-dev/skills — ไม่มี LICENSE file ใน repo

จาก ffmpeg-skill vendor เฉพาะ SKILL.md, scripts/, references/, mcp/, bin/, templates/ (ตัด tests/, demos/, evals/, brand/ ออก)

จาก color-grade-ai ตัด test_*, correction_luts/ (26 MB, regenerate ได้) ออก; จาก color-grading-skill ตัด tests/, brand/ ออก
