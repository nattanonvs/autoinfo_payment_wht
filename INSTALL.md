## Auto Payment WHT (Odoo 15) — คู่มือติดตั้ง

### 1) สิ่งที่ต้องมี
- Odoo 15
- โมดูลที่ต้องติดตั้งก่อน
  - account
  - dtr_taxation
  - dtr_payment_invoice

### 2) ติดตั้งโมดูล (กรณีใช้งานบน Server)
1. วางโฟลเดอร์โมดูล `auto_payment_wht` ไว้ใน addons path ของระบบ (เช่น `/var/odoo/custom15_autoinfo/`)
2. ตรวจสอบว่า `addons_path` ในไฟล์ config ของ Odoo ชี้มาที่โฟลเดอร์ดังกล่าวแล้ว
3. Restart service ของ Odoo
4. เปิด Odoo → Apps
5. เปิด Developer Mode (ถ้ายังไม่เปิด)
6. กด “Update Apps List”
7. ค้นหา `Auto Payment WHT` แล้วกด Install หรือ Upgrade (ถ้าติดตั้งไว้แล้ว)

### 3) ติดตั้งผ่านคำสั่ง (ทางเลือก)
- Upgrade เฉพาะโมดูล:
  - `-u auto_payment_wht`
- Upgrade พร้อม dependency (ถ้าต้องการ):
  - `-u dtr_taxation,dtr_payment_invoice,auto_payment_wht`

### 4) วิธีใช้งาน (สรุป)
1. ไปที่ Payments (Receive/Send Money)
2. เลือก Invoice/Bill ที่ต้องการจาก `processing_invoice_ids`
3. ไปแท็บ `WHT Invoices`
   - ติ๊ก `Apply WHT?` เฉพาะใบที่ต้องการนำมาคำนวณ
   - ปรับ `WHT Base Amount` ได้ (ฐานก่อน VAT ต่อใบ)
4. ไปแท็บ `Withholding Tax` (ของ dtr_taxation) แล้วเลือก `ภาษีหัก ณ ที่จ่าย` (tax_id1)
   - ระบบจะทำให้ `pay_amount1` = ผลรวมฐานก่อน VAT จากแท็บ `WHT Invoices`
   - และคำนวณ `wht_amount1` ให้ทันที
5. ไปแท็บ `WHT Summary` เพื่อดูผลรวม (ใช้ฟิลด์เดียวกับ Withholding Tax)

### 5) หมายเหตุสำคัญ
- ถ้าเลือกภาษีหัก ณ ที่จ่ายแล้วระบบฟ้อง `amount is not valid` ให้ตรวจว่า:
  - มีการติ๊ก `Apply WHT?` อย่างน้อย 1 ใบ
  - และ `WHT Base Amount` ของใบนั้นไม่เป็น 0

### 6) ไฟล์สำคัญในโมดูล
- Manifest: `__manifest__.py`
- Logic: `models/account_payment.py`
- View: `views/account_payment_view.xml`
- Security: `security/ir.model.access.csv`

