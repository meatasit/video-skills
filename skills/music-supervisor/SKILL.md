---
name: music-supervisor
description: เลือกเพลงประกอบให้สอดคล้องกับอารมณ์ของคลิป — catalog คลังเพลงส่วนตัว (BPM, energy, mood tag) → อ่าน mood timeline ของคลิปจาก shotlist/inventory → จับคู่เสนอ 3 ตัวเลือกต่อช่วง พร้อมจุด drop ที่ควรตรงกับ cut ใช้เมื่อผู้กำกับสั่งเลือกเพลง, ผู้ใช้ถามว่า "ใช้เพลงไหนดี", หรือเพิ่มเพลงเข้าคลัง
---

# music-supervisor

หน้าที่: ตอบว่า "ช่วงไหนของคลิปควรใช้เพลงอะไร และวาง drop ตรงไหน" — ไม่ render ไม่ mix (งานของ editor)

## ไฟล์ที่เกี่ยวข้อง
```
<music-library>/                 คลังเพลงส่วนตัว (default D:\music-library) ไฟล์ .mp3/.wav/.m4a
<music-library>/library.json     catalog ที่สคริปต์สร้าง — อย่าแก้มือ
<music-library>/tags.md          mood/instrument tag ที่ Claude เขียนต่อเพลง (แก้มือได้)
projects/<trip>/music/mood-timeline.md   อารมณ์ของคลิปต่อช่วงเวลา
projects/<trip>/music/plan.md            ผลเลือก: ช่วง · เพลง · in/out · drop → cut
```

## ขั้นตอน A — Catalog คลังเพลง (ครั้งแรก + ทุกครั้งที่เพิ่มเพลง)

1. `python scripts/catalog_music.py <music-library>` → อ่านทุกไฟล์ วัดด้วย librosa: duration, BPM, energy curve (RMS ต่อ 1 วิ), จุด drop (energy เพิ่มกระโดดมากสุด), ส่วน intro เงียบ, อ่าน metadata (title/artist/genre ถ้ามี) → เขียน `library.json` เฉพาะไฟล์ที่ยังไม่มีหรือเปลี่ยน hash
2. สำหรับเพลงที่ยังไม่มีใน `tags.md`: อ่านค่าที่วัดได้ + ชื่อไฟล์/metadata แล้ว tag ให้ตามสคีมาข้างล่าง เขียนต่อท้าย `tags.md` — **ถามผู้ใช้ถ้าชื่อไฟล์ไม่บอกอะไรเลย** (เช่น `track01.mp3`) อย่าเดาจากตัวเลขอย่างเดียว
3. รายงาน: จำนวนเพลงทั้งหมด, เพิ่มใหม่กี่เพลง, กระจาย mood เป็นยังไง, mood ไหนที่คลังยังขาด

สคีมา tag ต่อเพลง (1 บรรทัดใน tags.md):
```
| ไฟล์ | mood (1–2) | energy 1–5 | instrument | vocal | license/source | note |
```
mood ใช้คำชุดนี้: `calm` `warm` `nostalgic` `uplifting` `playful` `adventure` `epic` `tense` `melancholy` `chill`

## ขั้นตอน B — Mood timeline ของคลิป (ต่อทริป หลัง GATE 1)

อ่าน `brief.md` + `shotlist.md` + `inventory.md` แล้วเขียน `music/mood-timeline.md`:
```
| ช่วง (mm:ss) | scene | mood | energy 1–5 | pacing (cuts/นาที) | มีพูด | note |
```
กติกา:
- แบ่งช่วงตามโครงเรื่องใน shotlist ไม่ใช่ตาม scene ย่อย (ปกติ 3–6 ช่วงต่อคลิป 5 นาที)
- energy อ่านจาก pacing + เนื้อหา: drone/วิวกว้าง = ต่ำ, เดินตลาด/ขี่รถ = กลาง-สูง, hook = สูง, ending = ต่ำ-อบอุ่น
- ช่วงที่มีคนพูดมาก ให้ note ว่า "เพลงต้องเบา ไม่มี vocal"
- ถ้า brief ระบุอารมณ์รวม ให้ยึด brief ก่อน

## ขั้นตอน C — จับคู่และเสนอ

1. ต่อช่วงใน mood-timeline คัดจาก library.json + tags.md ด้วยเกณฑ์ตามลำดับ:
   - mood ตรงหรือใกล้ (ใช้ตาราง mood ข้างล่าง)
   - energy ต่างกันไม่เกิน 1
   - ความยาวเพลง ≥ ความยาวช่วง (หรือ loopable)
   - ช่วงมีพูด → vocal = no, energy ≤ 3
   - BPM สัมพันธ์กับ pacing: cuts/นาที × 4 ≈ BPM หรือครึ่ง/สองเท่า
2. เสนอ **3 ตัวเลือกต่อช่วง** เรียงตามความเหมาะ แต่ละตัวบอก: ทำไมเหมาะ 1 ประโยค, drop ของเพลงอยู่วินาทีที่เท่าไหร่ → ควรวางให้ตรง cut ไหนใน shotlist, in/out ที่แนะนำ
3. ถ้าทั้งคลิปใช้เพลงเดียวได้ (คลิป ≤ 90 วิ หรืออารมณ์ไม่เปลี่ยน) ให้เสนอแบบนั้นก่อน — เพลงน้อยกว่าดีกว่า
4. เพลงสองช่วงติดกันต้อง key/BPM ไม่ขัดกันชัด (BPM ต่างเกิน 30% ให้เตือน)
5. **รอผู้ใช้เลือก** แล้วเขียน `music/plan.md`:
```
| ช่วง | ไฟล์เพลง | music in | music out | drop ที่ (วินาทีในเพลง) | ให้ตรง cut (timecode ในคลิป) | fade in/out | ducking |
```
6. ส่ง plan.md ให้ editor — editor วางเพลงโดยเลื่อนให้ drop ตรง cut ที่ระบุ ไม่ใช่เริ่มเพลงที่ 0:00 ของช่วง

ตาราง mood ใกล้เคียง (ใช้เมื่อไม่มีตรงตัว):
- calm ↔ chill ↔ warm
- warm ↔ nostalgic ↔ melancholy
- uplifting ↔ playful ↔ adventure
- adventure ↔ epic ↔ tense

## ถ้าคลังยังว่างหรือไม่มีเพลงที่เข้า
บอกผู้ใช้ตรงๆ ว่าขาด mood อะไร แล้วแนะนำให้ไปหาใน YouTube Audio Library (filter: Mood + Attribution not required) หรือ Pixabay Music ด้วยคำค้นที่ระบุให้ (เช่น "warm acoustic travel 90 bpm") — ไม่ generate เพลงด้วย API และไม่แนะนำเพลงที่ license ไม่ชัด

## ข้อห้าม
- ไม่แก้ library.json ด้วยมือ (รัน catalog ใหม่แทน)
- ไม่ copy เพลงเข้า projects/ จนกว่าผู้ใช้จะเลือก
- ไม่ตัดสินใจแทนผู้ใช้ในขั้น C — เสนอแล้วรอ
