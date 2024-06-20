import io
from django.http import HttpResponse
from reportlab.lib.pagesizes import landscape, A7
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from django.shortcuts import render, get_object_or_404
from .models import Programacion
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Spacer

def generar_ticket(request, usuario_id, fecha):
    try:
        # Obtener el objeto Programacion
        datos = Programacion.objects.get(usuario=usuario_id, fecha_servicio=fecha)

        # Validar si el ticket ya ha sido impreso
        if datos.impreso == 1:
            return render(request, 'error.html', {'message': 'El ticket ya ha sido impreso.'})

        # Crear un objeto HttpResponse con el tipo de contenido PDF
        response = HttpResponse(content_type='application/pdf')
        # Adjuntar el PDF al response con el nombre de archivo "ticket.pdf"
        response['Content-Disposition'] = 'attachment; filename="ticket.pdf"'

        # Crear un objeto PDF usando ReportLab
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A7), rightMargin=5, leftMargin=5, topMargin=5, bottomMargin=5)
        styles = getSampleStyleSheet()

        # Definir un estilo para los párrafos centrados
        centered_style = ParagraphStyle(name="Centered", alignment=TA_CENTER)

        # Agregar el contenido al PDF
        content = []
        content.append(Paragraph("Ticket Menu", styles['Title']))
        content.append(Paragraph(f"Perfil: {datos.usuario.tipo_usuario}", centered_style))
        content.append(Paragraph(f"Nombre: {datos.usuario.nombre} {datos.usuario.apellido}", centered_style))
        content.append(Spacer(0.5, 0.5 * cm))
        content.append(Paragraph(f"Fecha: {datos.fecha_servicio.strftime('%Y-%m-%d')}", centered_style))
        content.append(Paragraph("", centered_style))
        content.append(Paragraph(f"Menu: {datos.nom_menu}", centered_style))
        content.append(Paragraph("", centered_style))
        content.append(Paragraph(f"Cantidad : {datos.cantidad_almuerzo}", centered_style))
        # Agregar más detalles del ticket según tus necesidades

        doc.build(content)

        # Adjuntar el contenido del objeto PDF al response
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)

        # Marcar el ticket como impreso
        datos.impreso = 1
        datos.save()

        return response

    except Programacion.DoesNotExist:
        return render(request, 'error.html', {'message': 'Sin Ticket Disponible'})

    except Exception as e:
        return render(request, 'error.html', {'message': str(e)})
