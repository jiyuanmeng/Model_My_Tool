import PyPDF2
import openpyxl

# 打开PDF文件
pdf_file = open('tools/4CF607D3BE52456BBBE3F1ABA610054A.pdf', 'rb')
pdf_reader = PyPDF2.PdfReader(pdf_file)

# 创建一个新的Excel文件
workbook = openpyxl.Workbook()
sheet = workbook.active

# 逐页读取PDF内容，并将其写入Excel表格
for page_num in range(len(pdf_reader.pages)):
    page = pdf_reader.pages[page_num]
    text = page.extract_text()
    lines = text.split('\n')
    for i, line in enumerate(lines):
        sheet.cell(row=i+1, column=page_num+1, value=line)

# 保存Excel文件
workbook.save('output.xlsx')