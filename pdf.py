from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import csv
from openpyxl import load_workbook

def pdfWeightGen(weightList):
    cellSize_Y = 25
    cellSize_X = 3
    cellStep_Y = 19.9
    cellStep_X = 65
    cellStart_X = 225
    cellStart_Y = 81

    packet = io.BytesIO()
    # create a new PDF with Reportlab
    can = canvas.Canvas(packet, pagesize=letter)
    
    for i in range(cellSize_X):
        for j in range(cellSize_Y):
            can.drawString(cellStart_X+i*cellStep_X,cellStart_Y+j*cellStep_Y,weightList[24-j][i+1])
    can.save()
    #move to the beginning of the StringIO buffer
    packet.seek(0)
    new_pdf = PdfFileReader(packet)
    """
    # read your existing PDF
    existing_pdf = PdfFileReader(open("template.pdf", "rb"))
    output = PdfFileWriter()
    # add the "watermark" (which is the new pdf) on the existing page
    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)
    # finally, write "output" to a real file
    """
    output = PdfFileWriter()
    page = new_pdf.getPage(0)
    output.addPage(page)
    outputStream = open("destination.pdf", "wb")
    output.write(outputStream)
    outputStream.close()

if __name__ == "__main__":
    templist = [['2020000', '1', '2', '3'], ['2020001', '2', '3', '4'], ['2020002', '3', '4', '5'], ['2020003', '4', '5', '6'], ['2020004', 
'5', '6', '7'], ['2020005', '6', '7', '8'], ['2020006', '7', '8', '9'], ['2020007', '8', '9', '10'], ['2020008', '9', '10', '11'], ['2020009', '10', '11', '12'], ['2020010', '11', '12', '13'], ['2020011', '12', '13', '14'], ['2020012', '13', '14', '15'], ['2020013', '14', '15', '16'], ['2020014', '15', '16', '17'], ['2020015', '16', '17', '18'], ['2020016', '17', '18', '19'], ['2020017', '18', '19', '20'], ['2020018', '19', '20', '21'], ['2020019', '20', '21', '22'], ['2020020', '21', '22', '23'], ['2020021', '22', '23', '24'], ['2020022', '23', '24', '25'], ['2020023', '24', '25', '26'], ['2020024', '25', '26', '27']]
    pdfWeightGen(templist)