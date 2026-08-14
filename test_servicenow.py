from app.integrations.servicenow.client import create_incident, ServiceNowError

try:
    result = create_incident(
        short_description="Laptop screen cracked",
        description="Employee reports a cracked laptop screen and needs a replacement.",
        urgency="2",
    )
    print("Ticket created:", result["number"])
except ServiceNowError as e:
    print("Error:", e)