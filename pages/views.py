from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.views.generic import TemplateView, ListView, View

from .models import Header, Web, Contacto, Suscriptor
from payment.models import Pricing
from .forms import ContactoForm


class HomeView(ListView):
    def get(self, request, *args, **kwargs):
        headers = list(Header.objects.filter(status=True).order_by("position")[:3])
        pricings = Pricing.objects.all()

        ctx = {
            "carousel_image1": headers[0],
            "carousel_image2": None,
            "carousel_image3": None,
            "pricings": pricings,
        }
        return render(request, "pages/index.html", ctx)


class PricingListView(TemplateView):
    template_name = "pages/pricing.html"


class AboutPageView(TemplateView):
    template_name = "pages/about.html"


class ContactView(View):
    def get(self, request, *args, **kwargs):
        contact = Web.objects.filter(estado=True).latest("fecha_creacion")
        form = ContactoForm()
        context = {"contact": contact, "form": form}
        return render(request, "pages/contact.html", context)

    def post(self, request, *args, **kwargs):
        form = ContactoForm(self.request.POST or None)

        try:
            if form.is_valid():
                nombre = form.cleaned_data.get("nombre")
                correo = form.cleaned_data.get("correo")
                asunto = form.cleaned_data.get("asunto")
                mensaje = form.cleaned_data.get("mensaje")

                contact = Contacto(
                    nombre=nombre,
                    correo=correo,
                    asunto=asunto,
                    mensaje=mensaje,
                )
                contact.save()
            messages.success(self.request, "Your message was send it successful!")
            return redirect("/")
        except ObjectDoesNotExist:
            messages.error(self.request, "Something wrong accourred. try again")
            return redirect("pages:contact")


class Suscribir(View):
    def post(self, request, *args, **kwargs):
        correo = request.POST.get("correo")
        Suscriptor.objects.create(correo=correo)
        asunto = "GRACIAS POR SUSCRIBIRTE A EnterpriseX!"
        mensaje = (
            "Te haz suscrito exitosamente a EnterpriseX, Gracias por tu preferencia!!!"
        )
        try:
            send_mail(asunto, mensaje, "apikey", [correo])
        except:
            pass

        return redirect("pages:index")
