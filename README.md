
# 12Bytes – A Django Platform for Drone & Financial Operations

**12Bytes** is a modular Django application built to manage drone pilot operations, financial tracking, and document management — all in one responsive web portal.

---

## 🚀 Features

### 🧑‍✈️ Pilot Management (`app`)
- Custom user registration and login
- Pilot profile with license uploads and annual training tracker
- Certificate and training management

### 🚁 Drone Operations (`drone`)
- Upload and manage SOP documents
- Log incident reports with attachments and PDF export
- Drone equipment tracking
- General document storage (with preview/download)

### 💰 Financial Management (`finance`)
- Track income and expense transactions
- Keyword-based summaries and filters
- Yearly breakdown by category and subcategory
- Mileage logging with CRUD views

---

## 📦 Tech Stack

- Django 4+
- PostgreSQL (Heroku Ready)
- Bootstrap 5 & Crispy Forms
- Font Awesome Icons
- WeasyPrint for PDF generation
- AWS S3 (optional for production media)
- Heroku-ready deployment


---

## 📁 Folder Structure

```
project/
│
├── app/         # Pilot profile and auth
├── drone/       # SOPs, incidents, equipment
├── finance/     # Income, expenses, mileage
├── templates/   # All HTML templates
├── static/      # CSS, JS, images
├── media/       # Uploaded files (local)
├── manage.py
├── requirements.txt
├── Procfile
```

---

## 📄 License

MIT License. © 2024 Tom Stout / 12Bytes
