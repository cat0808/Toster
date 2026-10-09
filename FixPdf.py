import md2pdf


def start_convertation(response):
    answer = str(response)
    return md2pdf.make_pdf_io(answer, filename="Ответ.pdf")
