# video-skills

Skill และ agent สำหรับตัดคลิปท่องเที่ยวด้วย Claude Code — รวม skill ที่คัดจาก community ไว้ที่เดียว บวกผู้กำกับ (orchestrator) และ sub-agent ที่เขียนเอง

Catalog ฉบับเต็มที่ใช้คัดเลือก: [Video Editing Skills Catalog](https://claude.ai/code/artifact/5ce12b81-8b9f-428c-85d2-c759bd4cb517)

## โครงสร้าง

```
skills/
  director/              ผู้กำกับ — เรียก sub-agent, คุม gate, รวม EDL (เขียนเอง)
  music-supervisor/      เลือกเพลงตามอารมณ์คลิป — catalog คลังเพลง + mood timeline + จับคู่ (เขียนเอง)
  ffmpeg-skill/          42 เครื่องมือ ffmpeg + MCP (kajisho5)
  video-editing-skill/   trim, jump cut, caption 3 สไตล์ (6missedcalls)
  whisper-transcription/ ถอดเสียง → srt/vtt (guia-matthieu/clawfu-skills)
  video-production/      shot list, storyboard, script template (travisjneuman)
  sfx-sources/           ค้น+โหลด SFX ฟรีจาก Mixkit/Pixabay/Kenney/Freesound ไม่ต้องมี key (sxhzju)
  color-grade-ai/        วิเคราะห์เฟรม, shot matching → .cube LUT (isaacrowntree)
  color-grading-skill/   HDR→SDR, apply LUT, primary correction แบบ typed (kajisho5)
agents/
  ingest.md              สแกน footage → inventory.md
  editor.md              shotlist → EDL → preview
  subtitler.md           whisper ไทย + cleanup
  graphics.md            Remotion / PNG overlay ตาม graphics-brief.md
  cg.md                  3D ใน Blender ผ่าน Blender MCP → .mov alpha
  colorist.md            normalize HDR + match สีข้ามกล้องต่อ scene → LUT ต่อคลิป
  upstream-agent-video-producer.md  ตัวอย่าง subagent จาก travisjneuman
install.sh / install.ps1 ติดตั้งลง ~/.claude/skills และ ~/.claude/agents
```

Remotion skills (`remotion-dev/skills`) ไม่ได้ vendor ไว้เพราะ repo ต้นทางไม่มี LICENSE file — ตัวติดตั้งจะรัน `npx skills add remotion-dev/skills` ให้แทน

## ติดตั้ง

ต้องมี: FFmpeg + ffprobe, Python 3.10+, Node 18+
สำหรับ `music-supervisor` เพิ่ม: `pip install librosa soundfile numpy` และคลังเพลงส่วนตัวที่ `D:\music-library` (โหลดจาก YouTube Audio Library / Pixabay) — รัน `python skills\music-supervisor\scripts\catalog_music.py D:\music-library` ครั้งแรก
ตัวเลือก: SoundDirector (คลัง offline 180 SFX + 80 เพลง, 220 MB, license ไฟล์เสียงไม่ระบุ — ใช้ส่วนตัว) ติดตั้งด้วย `install.ps1 -SoundDirector` หรือ `./install.sh --sounddirector`
สำหรับ agent `colorist` เพิ่ม: `pip install Pillow numpy PyYAML` และ Ruby 2.7+ (เฉพาะถ้าจะสร้าง preset LUT); `pip install -e skills/color-grading-skill`
สำหรับ agent `cg` เพิ่ม: Blender 4.2+ (ทดสอบบน 5.2 LTS), `uv`, Blender MCP (`uvx mcp-for-blender install-addon` แล้ว `claude mcp add --scope user blender -- uvx mcp-for-blender`) และ skill `animation-direction` (clone จาก DisturbedMediaGroup/claude-animation-skill) + plugin `3d-design` (`claude plugin marketplace add https://github.com/DavinciDreams/Agent-Team-Plugins` แล้ว `claude plugin install 3d-design@atlas-agents` — README ต้นทางเขียน `atlas-agents/plugins` ซึ่งไม่มีอยู่จริง)

Windows: ถ้า `.\install.ps1` ติด execution policy ให้รัน `powershell -ExecutionPolicy Bypass -File .\install.ps1`

```bash
git clone https://github.com/meatasit/video-skills
cd video-skills
./install.sh          # macOS/Linux
.\install.ps1         # Windows PowerShell
```

หรือเลือกติดตั้งทีละตัวจากเครื่องไหนก็ได้:

```bash
npx skills add meatasit/video-skills --skill director --agent claude-code
```

## ใช้งาน

เปิด Claude Code ในโฟลเดอร์โปรเจกต์วิดีโอ (แนะนำ Drive D) แล้วสั่ง:

```
/director เริ่มทริป <ชื่อทริป> footage อยู่ที่ <path บน NAS>
```

ผู้กำกับจะถามโจทย์ที่ขาด → ingest → shot list (รอ approve) → EDL + preview (รอ approve) → ซับ/กราฟิก → final render (รอ approve)

## อัปเดต skill ต้นทาง

ดู commit ที่ vendor มาใน `ATTRIBUTION.md` การอัปเดต = clone ต้นทางใหม่แล้ว copy ทับโฟลเดอร์ใน `skills/` แล้วแก้ ATTRIBUTION

## License

โค้ดที่เขียนเองในที่นี้ (director, agents, install scripts, README) — MIT
Skill ที่ vendor มา — license ของต้นทาง (MIT ทั้งหมด) อยู่ในโฟลเดอร์ของแต่ละตัว
