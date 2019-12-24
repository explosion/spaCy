# spaCy-th

## โปรเจคนี้ถูกรวมเข้ากับ repository หลักแล้ว การพัฒนา ให้ fork จาก https://github.com/explosion/spaCy โดยตรง

เพิ่มภาษาไทยให้กับ  spaCy

> repository นี้เป็น repository ที่จะนำไปรวมกับ  https://github.com/explosion/spaCy ในอนาคต

## ทำไมถึงเกิด repository นี้

เนื่องจาก  spaCy นั้นเป็นไลบารี NLP ที่กำลังมาแรง และเหมาะสมกับงาน AI และงานอื่น ๆ ที่ใช้ Deep learning  มากกว่า NLTK

ด้วยจุดนี้เองที่ทางนักพัฒนา NLP ต้องการให้  spaCy รองรับภาษาไทย จึงเกิด repository นี้ขึ้นมา

โดยเราได้แยกไฟล์ที่จะนำไปรวมกับ spaCy/th ออกมาก่อน เพื่อให้สะดวกต่อการพัฒนา

## การทดสอบการใช้งาน

ให้ทำการ fork https://github.com/explosion/spaCy สร้างโฟลเดอร์ th ใน spaCy แล้วเอาไฟล์ทั้งหมดในนี้ไปไว้ใน  spaCy/th

nlp = spacy.load('th')

## ผู้ร่วมพัฒนา

- นาย วรรณพงษ์  ภัททิยไพบูลย์

สามารถร่วมพัฒนาได้โดยการ fork แล้วส่ง Pull requests กลับมา
