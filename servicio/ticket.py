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
    try:
        import cups
    except ImportError:
        cups = None  # CUPS no está disponible en este sistema

# Función de impresión para Windows
def print_pdf_windows(pdf_content):
    try:
        # Crear un archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(pdf_content)
            temp_file.close()
            
            # Obtener el nombre de la impresora predeterminada
            printer_name = win32print.GetDefaultPrinter()
            print(f"Using printer: {printer_name}")  # Depuración

            # Enviar el archivo PDF a la impresora
            win32api.ShellExecute(0, "print", temp_file.name, f'/d:"{printer_name}"', ".", 0)
    except Exception as e:
        print(f"Error printing on Windows: {e}")  # Depuración

# Función de impresión para Linux
def print_pdf_linux(pdf_content):
    if cups:
        try:
            conn = cups.Connection()
            printers = conn.getPrinters()
            printer_name = list(printers.keys())[0]
            print(f"Using printer: {printer_name}")  # Depuración
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(pdf_content)
                temp_file.close()
                conn.printFile(printer_name, temp_file.name, "Job Title", {})
        except Exception as e:
            print(f"Error printing on Linux: {e}")  # Depuración
    else:
        print("CUPS is not available on this system.")

def generar_ticket(request, usuario_id, fecha):
    if not fecha:
        fecha = timezone.now().strftime('%Y-%m-%d')  # Set current date as default

    try:
        datos = Programacion.objects.get(usuario=usuario_id, fecha_servicio=fecha)

        if datos.impreso == 1:
            messages.success(request, "El ticket ya ha sido impreso.")
            return redirect('principal')

        buffer = io.BytesIO()
        # Configurar tamaño de papel para ticket térmico
        doc = SimpleDocTemplate(buffer, pagesize=(80*mm, 297*mm), rightMargin=5*mm, leftMargin=5*mm, topMargin=5*mm, bottomMargin=5*mm)
        styles = getSampleStyleSheet()
        
        # Crear un nuevo estilo de párrafo con tamaño de fuente ajustado
        centered_style = ParagraphStyle(name="Centered", alignment=TA_CENTER, fontSize=14)

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

        # Imprimir el PDF dependiendo del sistema operativo
        if platform.system() == "Windows":
            print_pdf_windows(pdf)
        else:
            print_pdf_linux(pdf)

        # Marcar como impreso y guardar
        datos.impreso = 1
        datos.fecha_impreso = timezone.now()
        datos.save()

        # Preparar la respuesta para la descarga
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="ticket.pdf"'

        messages.success(request, "Imprimiendo Ticket.")
        return response

    except Programacion.DoesNotExist:
        messages.error(request, "Sin Ticket Disponible.")
        return redirect('principal')

    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('principal')
