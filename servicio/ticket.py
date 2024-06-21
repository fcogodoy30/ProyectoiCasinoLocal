from datetime import timezone
import io
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from django.shortcuts import redirect, render
from .models import Programacion
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import mm
import os
import platform
import tempfile
from django.utils import timezone
from django.contrib import messages

# Importar bibliotecas específicas según el sistema operativo
if platform.system() == "Windows":
    import win32print
    import win32api
else:
    import cups

# Función de impresión para Windows
def print_pdf_windows(pdf_content):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(pdf_content)
        temp_file.close()
        printer_name = win32print.GetDefaultPrinter()
        win32api.ShellExecute(0, "print", temp_file.name, f'/d:"{printer_name}"', ".", 0)

# Función de impresión para Linux
def print_pdf_linux(pdf_content):
    conn = cups.Connection()
    printers = conn.getPrinters()
    printer_name = list(printers.keys())[0]
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(pdf_content)
        temp_file.close()
        conn.printFile(printer_name, temp_file.name, "Job Title", {})

def generar_ticket(request, usuario_id, fecha):
    if not fecha:
        fecha = timezone.now().strftime('%Y-%m-%d')  # Set current date as default

    try:
        datos = Programacion.objects.get(usuario=usuario_id, fecha_servicio=fecha)

        if datos.impreso == 1:
            messages.success(request, "El ticket ya ha sido impreso.")
            return redirect('principal')
            #return render(request, 'error.html', {'message': 'El ticket ya ha sido impreso.'})

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="ticket.pdf"'

        buffer = io.BytesIO()
        # Configurar tamaño de papel para ticket térmico
        doc = SimpleDocTemplate(buffer, pagesize=(80*mm, 297*mm), rightMargin=5*mm, leftMargin=5*mm, topMargin=5*mm, bottomMargin=5*mm)
        styles = getSampleStyleSheet()
        
        # Crear un nuevo estilo de párrafo con tamaño de fuente ajustado
        centered_style = ParagraphStyle(name="Centered", alignment=TA_CENTER, fontSize=14)
        #title_style = ParagraphStyle(name="Title", alignment=TA_CENTER, fontSize=12, spaceAfter=10)

        content = []
        content.append(Paragraph("Ticket Menu", styles['Title']))
        content.append(Paragraph(f"Perfil: {datos.usuario.tipo_usuario}", centered_style))
        content.append(Paragraph(f"Nombre: {datos.usuario.nombre} {datos.usuario.apellido}", centered_style))
        content.append(Spacer(0.5, 0.5 * cm))
        content.append(Paragraph(f"Fecha: {datos.fecha_servicio.strftime('%Y-%m-%d')}", centered_style))
        content.append(Spacer(0.2, 0.2 * cm))
        content.append(Paragraph("", centered_style))
        content.append(Spacer(0.2, 0.2 * cm))
        content.append(Paragraph(f"Menu: {datos.nom_menu}", centered_style))
        content.append(Paragraph("", centered_style))
        content.append(Spacer(0.2, 0.2 * cm))
        content.append(Paragraph(f"Cantidad : {datos.cantidad_almuerzo}", centered_style))

        doc.build(content)

        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)

        # Imprimir el PDF dependiendo del sistema operativo
        if platform.system() == "Windows":
            print_pdf_windows(pdf)
        else:
            print_pdf_linux(pdf)

        datos.impreso = 1
        datos.fecha_impreso = timezone.now()
        datos.save()

        messages.success(request, "Imprimiendo Ticket.")
        return redirect('principal')

    except Programacion.DoesNotExist:
        messages.success(request, "Sin Ticket Disponible.")
        return redirect('principal')
        #return render(request, 'error.html', {'message': 'Sin Ticket Disponible'})

    except Exception as e:
        messages.success(request,{'message': str(e)})
        return redirect('principal')
        #return render(request, 'error.html', {'message': str(e)})
