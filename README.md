# 🏠 Real Estate Income Dashboard

Dashboard วิเคราะห์ **รายได้จากการซื้อขายอสังหาริมทรัพย์ (กรมที่ดิน)** แยกตามภาคและประเภทรายได้ ปีงบประมาณ พ.ศ. 2566–2568
พัฒนาด้วย **Python + Pandas + Streamlit + Plotly**

- ที่มาข้อมูล: <https://data.go.th/dataset/income-2> (Open Data Common License)
- Live demo: <https://real-estate-income-dashboard-abqfb7appyeuvsrk5g8dxdr.streamlit.app/>

## ฟีเจอร์

| ส่วน | รายละเอียด |
|---|---|
| Interactive widgets | Multiselect ปี / ภาค / ประเภทรายได้, Radio เลือกหน่วย (บาท / ล้านบาท), Slider Top N |
| KPI | รายได้รวม, รายได้ปีล่าสุดพร้อม % เปลี่ยนแปลง, ภาคและประเภทรายได้สูงสุด |
| กราฟ | Line (แนวโน้มรายปี), Grouped bar (เทียบภาค), Donut (สัดส่วนประเภทรายได้), Horizontal bar (Top N), Heatmap (ภาค × ประเภท) |
| ข้อมูล | ตารางข้อมูลที่กรองแล้ว + ปุ่มดาวน์โหลด CSV |

## โครงสร้างโปรเจกต์

```
app.py                       # Streamlit app
fetch_data.py                # ดึงข้อมูลล่าสุดจาก data.go.th API -> data/income_real_estate.csv
data/income_real_estate.csv  # ข้อมูล 180 แถว (ปี, ภาค, ประเภทรายได้, บาท)
requirements.txt
.streamlit/config.toml       # ธีม dark
```

## รันบนเครื่อง

```bash
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

อัปเดตข้อมูลจาก data.go.th: `python fetch_data.py`

## Deploy บน Streamlit Community Cloud

1. Push โปรเจกต์ขึ้น GitHub (public repo)
2. ไปที่ <https://share.streamlit.io> → **Create app** → เลือก repo, branch `main`, main file `app.py`
3. Advanced settings → Python 3.12 → **Deploy**
