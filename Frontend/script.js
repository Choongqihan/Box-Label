document.getElementById("boxLabelForm").addEventListener("submit", async function (event) {
    event.preventDefault();

    const apiBaseURL = "http://127.0.0.1:5000";

    const vendorName = document.getElementById("vendorName").value.trim();
    const sanitizedVendorName = vendorName.replace(/[^a-zA-Z0-9]/g, "_");

    const data = {
        vendor_name: vendorName,
        po_number: document.getElementById("poNumber").value.trim(),
        store_code: document.getElementById("storeCode").value.trim(),
        delivery_date: document.getElementById("deliveryDate").value.trim(),
        sku_barcode: document.getElementById("skuBarcode").value.trim(),
        quantity: parseInt(document.getElementById("quantity").value, 10) || 0,
        case_id: document.getElementById("caseId").value.trim(),
        box_count: parseInt(document.getElementById("boxCount").value.trim(), 10) || 1, // ✅ FIXED HERE
        area_code: document.getElementById("areaCode").value.trim()
    };

    try {
        const response = await fetch(`${apiBaseURL}/generate_box_label/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        if (!response.ok) throw new Error("Server error: " + response.status);

        // Convert response to Blob
        const blob = await response.blob();
        const downloadUrl = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = downloadUrl;
        a.download = `${sanitizedVendorName}.pdf`; 
        document.body.appendChild(a);
        a.click();
        a.remove();
        
        alert(`✅ PDF Downloading as '${sanitizedVendorName}.pdf'...`);
    } catch (error) {
        alert("❌ Error: " + error.message);
    }
});
