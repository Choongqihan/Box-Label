from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging
import uvicorn
from pydantic import BaseModel
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from io import BytesIO
from database import get_db_connection  # Import database connection function

# ✅ Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Initialize FastAPI app
app = FastAPI()

# ✅ Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# ✅ Serve frontend static files
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Frontend"))

if os.path.isdir(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
    logger.info(f"✅ Static files served from: {frontend_path}")
else:
    logger.error(f"⚠️ Frontend directory not found at {frontend_path}")

# ✅ Ensure PDFs directory exists
pdfs_dir = "pdfs"
os.makedirs(pdfs_dir, exist_ok=True)

# ✅ Root endpoint
@app.get("/")
def home():
    return {"message": "Box Label Generator API is running!"}

# ✅ Data model for PDF request
class BoxLabelRequest(BaseModel):
    vendor_name: str
    po_number: str
    store_code: str
    delivery_date: str
    sku_barcode: str
    quantity: int
    case_id: str
    box_count: int  # ✅ Integer to specify number of boxes
    area_code: str

# ✅ Function to create a multi-page PDF for all boxes
def create_multi_page_pdf(data: BoxLabelRequest, file_path: str):
    try:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        for i in range(1, data.box_count + 1):  # ✅ Create a new page for each box
            # Header
            c.setFont("Helvetica-Bold", 18)
            x_offset = (width - 400) / 2  # Centering a 400px wide block
            y_offset = height - 80
            line_height = 20

            c.line(x_offset, y_offset + 40, x_offset + 400, y_offset + 40)
            c.drawCentredString(width / 2, height - 65, "OUTRIGHT - HANDYMAN")
            c.line(x_offset, y_offset + 5, x_offset + 400, y_offset + 5)

            # Table Data
            c.setFont("Helvetica", 12)
            y_offset = height - 100

            labels = [
                ("Vendor Name:", data.vendor_name),
                ("PO#:", data.po_number),
                ("Store Code and Name:", data.store_code),
                ("Delivery Date:", data.delivery_date),
            ]

            for label, value in labels:
                c.drawString(x_offset, y_offset, label)
                c.drawString(x_offset + 150, y_offset, value)
                y_offset -= line_height

            # SKU Table
            y_offset -= 10
            c.line(x_offset, y_offset + 10, x_offset + 400, y_offset + 10)
            c.drawString(x_offset, y_offset - 5, "SKU / BARCODE")
            c.drawString(x_offset + 200, y_offset - 5, "QTY")
            c.line(x_offset, y_offset - 10, x_offset + 400, y_offset - 10)
            y_offset -= 20
            c.drawString(x_offset, y_offset - 5, data.sku_barcode)
            c.drawString(x_offset + 200, y_offset - 5, str(data.quantity))

            # Box Details
            y_offset -= 20
            c.line(x_offset, y_offset - 5, x_offset + 400, y_offset - 5)
            c.drawString(x_offset, y_offset - 20, "CASE ID")
            c.drawString(x_offset + 160, y_offset - 20, "BOX COUNT")
            c.drawString(x_offset + 280, y_offset - 20, "AREA CODE")
            c.line(x_offset, y_offset - 25, x_offset + 400, y_offset - 25)
            y_offset -= 40
            c.drawString(x_offset, y_offset, data.case_id)
            c.drawString(x_offset + 160, y_offset, f"{i} OF {data.box_count}")  # ✅ "Box X OF Y"
            c.drawString(x_offset + 280, y_offset, data.area_code)

            # QR Code ✅ FIXED
            qr_code = QrCodeWidget(data.case_id)
            qr_drawing = Drawing(80, 80)
            qr_drawing.add(qr_code)
            qr_x_offset = (width - 400) / 2  # Centering QR Code
            renderPDF.draw(qr_drawing, c, qr_x_offset, y_offset - 100)

            # ✅ Add new page if more boxes remain
            if i < data.box_count:
                c.showPage()

        # Save PDF
        c.save()
        buffer.seek(0)

        with open(file_path, "wb") as f:
            f.write(buffer.getvalue())

        logger.info(f"✅ Multi-page PDF successfully created: {file_path}")

    except Exception as e:
        logger.error(f"⚠️ PDF Generation Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF Generation Error: {str(e)}")

# ✅ PDF generation endpoint (now generates a multi-page PDF)
@app.post("/generate_box_label/")
def generate_pdf(request: BoxLabelRequest):
    sanitized_vendor_name = request.vendor_name.replace(" ", "_").replace("/", "_")
    file_name = f"Box_Label_{sanitized_vendor_name}.pdf"
    file_path = os.path.join(pdfs_dir, file_name)

    # Generate multi-page PDF
    create_multi_page_pdf(request, file_path)

    # Insert into database
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO generated_pdfs 
                    (file_name, file_path, vendor_name, po_number, store_code, delivery_date, sku_barcode, quantity, case_id, box_count, area_code) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        file_name, file_path, request.vendor_name, request.po_number, 
                        request.store_code, request.delivery_date, request.sku_barcode, 
                        request.quantity, request.case_id, request.box_count, request.area_code
                    )
                )
                conn.commit()
        logger.info(f"✅ Multi-page PDF saved to database: {file_path}")
    except Exception as e:
        logger.error(f"⚠️ Database error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # ✅ Return single PDF file with multiple pages
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=file_name,
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'}
    )

# ✅ Automatically run FastAPI on port 5000
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)
