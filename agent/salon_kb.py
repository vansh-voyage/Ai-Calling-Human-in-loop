"""
Static fallback knowledge base used during development and agent self-check.
These same entries are seeded into the backend DB on startup via backend/seed.py.
"""

SALON_KNOWLEDGE: dict[str, str] = {
    "what are your hours": "We're open Monday through Saturday 9 AM to 7 PM, and Sunday 10 AM to 5 PM.",
    "where are you located": "We're at 142 Maple Street, downtown. There's free parking in the lot behind the building.",
    "how do i book an appointment": "You can book online at luxesalon.com/book, call us at 555-0100, or just walk in.",
    "do you accept walk ins": "Yes, we welcome walk-ins, though appointments are recommended on weekends.",
    "what services do you offer": "We offer haircuts, coloring, blowouts, manicures, pedicures, facials, and massages.",
    "how much does a haircut cost": "Haircuts start at $45 for a trim and $65 and up for a full cut and style.",
    "do you have gift cards": "Yes! Gift cards are available in any amount, in-salon or online at luxesalon.com.",
    "what is your cancellation policy": "We ask for 24 hours notice to cancel or reschedule. Late cancellations may incur a 50% fee.",
    "do you offer color services": "Yes, we offer full color, highlights, balayage, and toning. Prices vary by length and service.",
    "do you offer kids haircuts": "Yes, we offer kids' haircuts for children 12 and under starting at $25.",
    "is there parking": "Yes, free parking is available in the lot directly behind our building on Maple Street.",
    "do you sell hair products": "Yes, we carry professional hair care products including Oribe, Kerastase, and Redken.",
}
