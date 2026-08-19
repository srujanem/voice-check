const fs = require('fs');
let content = fs.readFileSync('D:/voice-check/voice-check/theme.js', 'utf8');

const pdfCode = `
// ===== PDF EVIDENCE GENERATOR =====
document.addEventListener('DOMContentLoaded', () => {
    const pdfBtn = document.getElementById('download-pdf-btn');
    if (pdfBtn) {
        pdfBtn.addEventListener('click', async () => {
            const resultCard = document.getElementById('result-card');
            if (!resultCard || resultCard.classList.contains('hidden')) {
                alert("Please analyze a file first before downloading the report.");
                return;
            }
            
            // Show loading state on button
            const originalText = pdfBtn.innerHTML;
            pdfBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Generating...';
            pdfBtn.style.pointerEvents = 'none';

            try {
                // Dynamically load libraries
                if (!window.html2canvas) {
                    await new Promise(r => { const s = document.createElement('script'); s.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js'; s.onload = r; document.head.appendChild(s); });
                    await new Promise(r => { const s = document.createElement('script'); s.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js'; s.onload = r; document.head.appendChild(s); });
                }

                const canvas = await html2canvas(resultCard, {
                    scale: 2,
                    backgroundColor: '#0f172a',
                    logging: false
                });

                const imgData = canvas.toDataURL('image/png');
                const { jsPDF } = window.jspdf;
                
                // Create PDF (A4 size)
                const pdf = new jsPDF('p', 'mm', 'a4');
                const pdfWidth = pdf.internal.pageSize.getWidth();
                const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
                
                // Add header
                pdf.setFillColor(6, 182, 212);
                pdf.rect(0, 0, pdfWidth, 20, 'F');
                pdf.setTextColor(255, 255, 255);
                pdf.setFontSize(16);
                pdf.setFont("helvetica", "bold");
                pdf.text("AuthGuard AI - Official Evidence Report", 15, 13);
                
                pdf.setTextColor(150, 150, 150);
                pdf.setFontSize(10);
                pdf.setFont("helvetica", "normal");
                pdf.text("Generated: " + new Date().toLocaleString(), 15, 30);
                pdf.text("Authorized by: Srujan EM (Founder)", 15, 36);
                
                // Add the result card image
                pdf.addImage(imgData, 'PNG', 15, 45, pdfWidth - 30, pdfHeight - ((30/pdfWidth) * pdfHeight));
                
                // Save
                pdf.save(\`AuthGuard_Report_\${Date.now()}.pdf\`);
            } catch (err) {
                console.error("PDF Error:", err);
                alert("Failed to generate PDF. Please try again.");
            } finally {
                pdfBtn.innerHTML = originalText;
                pdfBtn.style.pointerEvents = 'auto';
            }
        });
    }
});
`;

// Append PDF feature
if (!content.includes("PDF EVIDENCE GENERATOR")) {
    content += '\n' + pdfCode;
}

fs.writeFileSync('D:/voice-check/voice-check/theme.js', content, 'utf8');
