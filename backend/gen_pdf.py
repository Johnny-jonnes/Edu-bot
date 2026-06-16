from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font('Arial', 'B', 16)
pdf.cell(200, 10, txt='RELEVE DE NOTES OFFICIEL - BACCALAUREAT', ln=1, align='C')

pdf.set_font('Arial', '', 12)
pdf.ln(10)
pdf.cell(200, 10, txt='Session: 2023', ln=1)
pdf.cell(200, 10, txt='Serie: Sciences Experimentales (SE)', ln=1)
pdf.cell(200, 10, txt='Mention: Bien', ln=1)
pdf.ln(10)

pdf.set_font('Arial', 'B', 14)
pdf.cell(200, 10, txt='NOTES PAR MATIERE:', ln=1)

pdf.set_font('Arial', '', 12)
pdf.cell(200, 10, txt='Biologie: 16/20', ln=1)
pdf.cell(200, 10, txt='Chimie: 15/20', ln=1)
pdf.cell(200, 10, txt='Physique: 14/20', ln=1)
pdf.cell(200, 10, txt='Mathematiques: 13/20', ln=1)
pdf.cell(200, 10, txt='Francais: 12/20', ln=1)
pdf.cell(200, 10, txt='Philosophie: 11/20', ln=1)
pdf.cell(200, 10, txt='Anglais: 14/20', ln=1)

pdf.output(r'C:\Users\LUXE\Desktop\releve_notes_test.pdf')
print("PDF généré avec succès")
