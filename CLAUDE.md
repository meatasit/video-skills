# video-skills

Repo นี้เป็นคลัง skill/agent สำหรับงานตัดคลิป ไม่ใช่โปรเจกต์วิดีโอ

- จะตัดคลิป → เปิด Claude Code ในโฟลเดอร์โปรเจกต์วิดีโอแล้วใช้ `/director` (ต้องรัน install ก่อน)
- จะแก้ผู้กำกับหรือ sub-agent → แก้ที่ `skills/director/SKILL.md` และ `agents/*.md` แล้วรัน install ใหม่
- จะเพิ่ม skill จาก community → copy โฟลเดอร์ลง `skills/` + เพิ่มแถวใน `ATTRIBUTION.md` + LICENSE ของต้นทาง
- อย่าแก้ไฟล์ใน skill ที่ vendor มาโดยตรง ถ้าต้องปรับให้เขียน note ใน `skills/director/SKILL.md` แทน
