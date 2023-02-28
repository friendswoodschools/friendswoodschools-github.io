from fpdf import FPDF

class PDF(FPDF):
    def __init__(self, **kwargs):
        super(PDF, self).__init__(**kwargs)
        self.set_margins(left=10,top=6)

    def head(self, title, email, date, address):
        self.set_font("helvetica", 'B', 8)

        # Set colors
        self.set_fill_color(1,17,91)
        self.set_text_color(0,0,0)

        self.cell(76, 2, date)
        self.cell(6, 2, title, ln=True)
        self.ln()
        self.set_font("helvetica", 'B', 12)
        self.cell(0, 5, "FRIENDSWOOD PRIVATE SCHOOL", ln=True, align="C")

        self.set_font("helvetica", 'B', 9)
        self.cell(0, 3, address, ln=True, align="C")
        self.cell(0, 3, email, ln=True, align="C")
        self.image('static/art/Unknown.png', 15, 8, 20,)
        self.image('static/art/Unknown.png', 184, 8, 20,)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'BI', 8)
        self.set_text_color(169, 169, 169)
        self.cell(0, 10, f"Page {self.page_no()} This result is rendered void if any modifications is made on it", ln=True, align='C')
    
        
    def create_table(self, table_data, title='', data_size = 10, title_size=12, align_data='L', align_header='L'):
        self.set_font("helvetica",'',title_size)
        self.cell(0,5,title, align=align_header)

        self.set_font_size(data_size)
        for d1 in table_data:
            for d2 in table_data:
                self.cell(0,5,d2, align=align_data)
