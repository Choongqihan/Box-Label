# Box Label PDF Generator

## Overview
This project is a web-based application that allows vendors to generate PDFs for box labels, ensuring proper tracking and organization. The application uses **Python, ReportLab, FastAPI, React.js, pdf.js, and PostgreSQL** for backend and frontend functionality.

## Features

### 1. Generate Box Label with CID
- Each box label includes a **CID (Customer Identification)** for tracking.

### 2. Generate Multiple PDFs Based on a Series
- One box = One PDF.
- If a user specifies **10 boxes**, the system generates **10 PDFs** labeled as:
  - `1 OF 10`
  - `2 OF 10`
  - `...`
  - `10 OF 10`
- The **Box Count field** automatically includes the `OF` format (e.g., `1 OF 10`).
- The total number of boxes is **user-defined** and dynamically reflected.

### 3. Enable Multiple SKUs and Quantities
- Users can **add, remove, or modify** multiple **SKUs and their respective quantities**.
- Changes apply to:
  - **Frontend (React.js UI)**
  - **Backend (FastAPI endpoints)**
  - **Database (PostgreSQL storage for multiple entries)**

### 4. Unique QR Codes per User
- Each generated PDF contains a **unique QR code**.
- Ensures that QR codes remain distinct for different users generating box labels simultaneously.
- Example:
  - **User 1 generates 5 boxes:**
    - `1 OF 5, 2 OF 5, 3 OF 5, 4 OF 5, 5 OF 5`
  - **User 2 generates 3 boxes simultaneously:**
    - `1 OF 3, 2 OF 3, 3 OF 3`
- The system maintains separate numbering for different users.

### 5. Dropdown Menus for Required Fields
- Minimizes input errors by **using dropdown lists** for:
  - **Vendor**
  - **Store Code**
  - **Store Name**
  - **SKU**
  - **Area Code**
- These dropdowns **fetch data from a MySQL database** storing pre-defined values.

## Tech Stack
- **Backend:** FastAPI, Python, ReportLab
- **Frontend:** React.js, pdf.js
- **Database:** PostgreSQL, MySQL (for dropdown lists)

## Setup Instructions
### 1. Clone the Repository
```bash
git clone https://github.com/your-repo/box-label-generator.git
cd box-label-generator
```

### 2. Start FastAPI Server
```bash
uvicorn main:app --reload --port 5000
or
Python main.py
```

### 3. Database Setup (Not yet Implemented)
- Ensure PostgreSQL and MySQL are installed.
- Configure **PostgreSQL** for storing box label data.
- Configure **MySQL** for dropdown menus.
- Run database migration scripts.
