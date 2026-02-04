from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Curriculum Vitae', 0, 1, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 10, body)
        self.ln()

pdf = PDF()
pdf.add_page()

# Datos Dummy
pdf.set_font('Arial', 'B', 16)
pdf.cell(0, 10, 'Juan Pérez - Desarrollador Senior Python', 0, 1)
pdf.ln(10)

pdf.chapter_title('Resumen Profesional')
pdf.chapter_body(
    'Desarrollador de software con más de 8 años de experiencia en Python y desarrollo web. '
    'Experto en liderazgo de equipos ágiles y gestión de proyectos.'
)

pdf.chapter_title('Experiencia')
pdf.chapter_body(
    '- Senior Python Developer en TechCorp (2020-Presente): Liderazgo de equipo de 5 personas. '
    'Migración de legacy code a microservicios.\n'
    '- Backend Developer en StartUpX (2017-2020): Desarrollo de APIs RESTful usando Django y Flask.'
)

pdf.chapter_title('Habilidades')
pdf.chapter_body(
    '- Lenguajes: Python, JavaScript, SQL.\n'
    '- Frameworks: Django, Flask, Streamlit.\n'
    '- Otros: Git, Docker, AWS, Liderazgo, Gestión de equipos.'
)

pdf.output('cv_ejemplo.pdf', 'F')
print("CV generado: cv_ejemplo.pdf")
