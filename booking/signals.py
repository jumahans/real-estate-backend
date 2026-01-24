from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Booking, Agent

@receiver(post_save, sender=Booking)
def handle_booking_events(sender, instance, created, **kwargs):
    if created:
        print(f"SIGNAL: New booking #{instance.id} by {instance.user.username}")
        
        # AUTO-ASSIGN AGENT (Works perfectly!)
        if instance.property.agent:
            instance.agents.add(instance.property.agent)
            print(f"Auto-assigned agent: {instance.property.agent.name}")
        elif Agent.objects.exists():
            first_agent = Agent.objects.first()
            instance.agents.add(first_agent)
            print(f"Assigned default agent: {first_agent.name}")

        # Email User
        subject = f"Booking Received: {instance.property.title}"
        message = f"Hello {instance.user.username}, your booking for {instance.start_datetime} is pending."
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [instance.user.email])
            print(f"User email sent to {instance.user.email}")
        except Exception as e:
            print(f"User email failed: {e}")

        # Notify Agent
        if instance.property.agent and instance.property.agent.user.email:
            agent_msg = f"New booking from {instance.user.username} for {instance.property.title}."
            try:
                send_mail("New Booking Alert", agent_msg, settings.DEFAULT_FROM_EMAIL, [instance.property.agent.user.email])
                print(f"Agent notified: {instance.property.agent.user.email}")
            except Exception as e:
                print(f"Agent email failed: {e}")

    elif instance.status == 'confirmed' and kwargs.get('update_fields', {}).get('status'):
        print(f"SIGNAL: Booking #{instance.id} confirmed")
        agent_name = instance.agents.first().name if instance.agents.exists() else "TBD"
        subject = f"Booking Confirmed: {instance.property.title}"
        message = f"Your viewing is confirmed for {instance.start_datetime}. Agent: {agent_name}"
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [instance.user.email])
            print(f"Confirmation sent to {instance.user.email}")
        except Exception as e:
            print(f"Confirmation failed: {e}")
