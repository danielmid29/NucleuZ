from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa
from xhtml2pdf.files import pisaFileObject

def render_to_pdf(template_src, context_dict={}):
    
    print(template_src)
    print(context_dict)
    try:
        template = get_template(template_src)
        
        html  = template.render(context_dict)
        result = BytesIO()
        pisaFileObject.getNamedFile = lambda self: self.uri
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        
    except Exception as e:
        print(e, 'Download')
    print(pdf.err)
    if pdf.err:
        return HttpResponse("Invalid PDF", status_code=400, content_type='text/plain')
    return HttpResponse(result.getvalue(), content_type='application/pdf')
