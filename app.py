"""Cuppa Brew Cafe website, built with Flask.

Run it:
    pip install -r requirements.txt
    python app.py
Then open http://127.0.0.1:5000 in your browser.

To update the site, edit SHOP and MENU below.
"""

import os
import re
from urllib.parse import quote_plus

from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
# Needed for flash messages. Set a real SECRET_KEY environment variable when deploying.
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")

SHOP = {
    "name": "Cuppa Brew Cafe",
    "slogan": "Your neighborhood cafe",
    "tagline": "Coffee, matcha, croffles and comfort food in Villa Kananga, Butuan City.",
    "address": "Rosewood Plains Subd., Brgy. Villa Kananga, Butuan City, 8600 Agusan del Norte",
    "rating": 4.8,
    "review_count": 5,
    "facebook": "https://www.facebook.com/p/Cuppa-Brew-Cafe-61565144407194/",
    "instagram": "https://www.instagram.com/cuppabrewcafe",
    "instagram_handle": "@cuppabrewcafe",
    # Only "opens 12 PM" is confirmed (from Google Maps).
    # Replace with the full schedule, e.g. ("Mon - Sun", "12:00 PM - 10:00 PM").
    "hours": [
        ("Opens", "12:00 PM"),
    ],
    "hours_note": "Hours may change. Check our Facebook page for today's schedule.",
}
SHOP["map_url"] = "https://www.google.com/maps/search/?api=1&query=" + quote_plus(
    "Cuppa Brew Cafe Villa Kananga Butuan City"
)
SHOP["map_embed"] = "https://maps.google.com/maps?output=embed&q=" + quote_plus(
    "Cuppa Brew Cafe, Villa Kananga, Butuan City"
)


def item(name, *prices, desc="", tag=None):
    """One menu line. `prices` lines up with the category's `sizes`.
    Use None for a size that isn't offered. tag: "new", "best" or "rec"."""
    return {"name": name, "prices": list(prices), "desc": desc, "tag": tag}


# Transcribed from the cafe's printed menu.
# NOTE: the Pica-Pica, Pasta/Bread, Rice Meals, Salad, Non-Coffee and Matcha
# prices were read from small, blurry photos. Double-check them with the cafe.
MENU = [
    {
        "group": "Drinks",
        "title": "Coffee Based",
        "sizes": ["Hot 12oz", "Iced 16oz", "Iced 22oz"],
        "items": [
            item("Americano", 85, 95, 105),
            item("Cafe Latte", 125, 135, 145),
            item("Salted Caramel", 145, 150, 160),
            item("Caramel Macchiato", 145, 150, 160, tag="best"),
            item("Spanish Latte", 140, 145, 155, tag="best"),
            item("Spanish w/ Banana Pudds", None, 215, 235, tag="rec"),
            item("Banana Hazelnut Latte", None, 170, 180, tag="new"),
            item("White Mocha", 145, 155, 165),
            item("Dark Mocha", 140, 150, 160),
            item("Hazelnut Mocha", 145, 155, 165),
            item("Dirty Matcha", 160, 175, 185),
            item("Brown Cinnamon", 140, 145, 155),
        ],
        "note": "Add-ons: sub oat milk, extra shot, syrup, cold foam. Ask us for add-on prices.",
    },
    {
        "group": "Drinks",
        "title": "Cloud Series",
        "sizes": ["Medium", "Large"],
        "items": [
            item("Spanish Oat Cloud", 180, 190, desc="Oat milk & espresso + cold foam + cinnamon", tag="rec"),
            item("Cloudtella", 185, 195, desc="Milk & espresso + Nutella + cold foam + cocoa", tag="rec"),
            item("Seasalt Cloud", 170, 180, desc="Milk & espresso + seasalt cold foam"),
            item("Biscoff Cloud", 185, 195, desc="Milk & espresso + cold foam + Biscoff biscuit", tag="best"),
            item("Butterscotch Cloud", 170, 180, desc="Milk & espresso + cold foam + butterscotch bites"),
            item("Tiramisu Cloud", 175, 185, desc="Milk & espresso + cold foam w/ cocoa powder + lady finger biscuit", tag="best"),
        ],
    },
    {
        "group": "Drinks",
        "title": "Matcha Picks",
        "sizes": [""],
        "items": [
            item("Matcha Oat Milk", 185, desc="Oat milk + premium matcha", tag="best"),
            item("Whisked Kyoto", 215, desc="Oat milk + ceremonial matcha (great for beginners)", tag="rec"),
            item("Matcha Latte w/ Banana Pudds", 210, desc="Matcha latte + banana pudding ice cream"),
            item("Mango Matcha", 170, desc="Mango fruity + milk + matcha"),
            item("Sea Salt Matcha", 210, desc="Oat milk + matcha + sea salt cream", tag="best"),
            item("Mushroom Matcha", 145, desc="Oat milk + mushroom matcha", tag="new"),
            item("Strawberry Matcha", 185, desc="Strawberry purée + strawberry milk + matcha"),
            item("Matcha Einspanner", 195, desc="Milk + sweetened matcha + cold foam"),
            item("Cookie Butter Matcha", 220, desc="Milk + matcha + cold foam + Biscoff spread & cream"),
        ],
    },
    {
        "group": "Drinks",
        "title": "Frappes",
        "sizes": ["Medium", "Large"],
        "items": [
            item("Biscoff Frappe", 185, 195, tag="best"),
            item("Cookies and Cream", 180, 190, tag="best"),
            item("Butterscotch Frappe", 170, 180),
            item("Pistachio Frappe", 185, 195, tag="new"),
            item("Double Dutch", 180, 190),
            item("Salted Caramel", 175, 185),
            item("Matcha Frappe", 185, 195),
        ],
    },
    {
        "group": "Drinks",
        "title": "Non-Coffee",
        "sizes": ["Medium", "Large"],
        "items": [
            item("Choco Rush", 135, 150, desc="Choco milk + choco sauce"),
            item("Choco Milk w/ Banana Pudds", 190, 210, desc="Choco milk + choco sauce + banana pudding ice cream", tag="best"),
            item("Oreo Berry Blush", 140, 155, desc="Oreo milk + strawberry purée", tag="best"),
            item("Pink Berry Bliss", 140, 155, desc="Strawberry milk + strawberry purée"),
            item("Mango Berry Fusion", 135, 150, desc="Strawberry milk + mango purée"),
            item("Milky Mixed Berries", 140, 155, desc="Milk + mixed berries purée + cold foam"),
            item("Merry Mango", 140, 155, desc="Milk + mango jam + cold foam"),
            item("Choccy Campfire", 150, 165, desc="Chocolate milk + burnt mallows"),
        ],
    },
    {
        "group": "Drinks",
        "title": "Soda Series",
        "subtitle": "with sinkers",
        "sizes": ["Medium", "Large"],
        "items": [
            item("Strawberry Soda", 100, 110),
            item("Strawberry Lychee Spritz", 105, 115, tag="best"),
            item("Strawberry Peach Soda", 105, 115),
            item("Peach Mango Spark", 105, 115),
            item("Green Apple Fiz", 100, 110, tag="best"),
            item("Lemon Sunrise", 100, 110, tag="best"),
            item("Blueberry Soda", 100, 110),
            item("Lemon Peach", 105, 115),
            item("Strawberry Love Float", 140, 155),
        ],
    },
    {
        "group": "Drinks",
        "title": "Brewed Tea",
        "sizes": ["Hot 12oz", "Iced 16oz"],
        "items": [
            item("Oolong Tea w/ Peach Mango", 70, 135),
            item("Jasmine Green Tea w/ Lemon", 70, 130),
            item("Earl Grey Tea w/ Blueberry", 70, 130, tag="best"),
            item("Cupid's Berry Pop", 80, 140),
            item("Summer Peach Passion", 80, 135, tag="new"),
            item("Chamomile Flower Tea", 70, None),
        ],
    },
    {
        "group": "Drinks",
        "title": "Sugarcane Juice",
        "subtitle": "freshly squeezed, 100% natural",
        "sizes": [""],
        "items": [
            item("Tubo + Yakult", 80),
            item("Tubo + Lemon", 80),
            item("Tubo + Lemon + Yakult", 90, tag="best"),
            item("Tubo + Lemon + Passion Fruit", 100, tag="new"),
            item("Tubo + Lemon + Ginger", 100, tag="new"),
        ],
    },
    {
        "group": "Drinks",
        "title": "Fruit Shakes",
        "sizes": [""],
        "items": [
            item("Strawberry Slush", 150),
            item("Ube Macapuno Blend", 150),
            item("Mango Graham Shake", 160, tag="best"),
        ],
    },
    {
        "group": "Food",
        "title": "Croffles",
        "sizes": [""],
        "items": [
            item("Just Croffles", 100, desc="Croffles + powdered sugar"),
            item("Banana Pudding Delight", 145, desc="Banana pudding + caramel drizzle + Biscoff crumbs"),
            item("Bananatella", 150, desc="Whip cream + banana + Nutella drizzle & cocoa powder", tag="best"),
            item("Loaded Biscoff", 150, desc="Whip cream + Biscoff biscuit & Biscoff drizzle", tag="best"),
            item("Honey Cinnabite", 130, desc="Honey drizzle & cinnamon", tag="rec"),
            item("Strawberry Cloud", 135, desc="Whip cream & strawberry purée"),
            item("S'mores", 135, desc="Burnt mallows + choco drizzle & biscuit"),
            item("Matcha Dream", 145, desc="Whip cream + matcha drizzle + matcha biscuit & powder"),
            item("Oreo Crumble", 140, desc="Whip cream + Oreo crumbs & biscuit + choco drizzle", tag="best"),
            item("Ham & Cheese", 145, desc="Ham & cheese + mayo", tag="rec"),
            item("Savory Cheese", 125, desc="Cheese & mayo"),
        ],
    },
    {
        "group": "Food",
        "title": "Pica-Pica Corner",
        "sizes": [""],
        "items": [
            item("Fry Board", 350, desc="Good for 3-4 persons", tag="new"),
            item("French Fries", 85),
            item("Cheezy Beef Dynamite (5 pcs)", 99),
            item("Spinach Dip w/ Garlic Bread", 150),
            item("Empanada (3 pcs)", 90),
            item("Loaded Cheezy Bacon Fries", 180, tag="best"),
            item("Nachos", 250, desc="For sharing (2-3 persons)", tag="best"),
        ],
    },
    {
        "group": "Food",
        "title": "Rice Meals",
        "subtitle": "with rice & side dish",
        "sizes": [""],
        "items": [
            item("Chicken in White Sauce", 219, tag="best"),
            item("Hungarian Sausage", 175),
            item("Caramelized Spam", 170),
            item("Beef Tapa", 220, tag="best"),
            item("Mushroom Beef Patty", 190),
            item("Baby Back Ribs", 289, tag="rec"),
            item("Korean Pork Bulgogi", 245, tag="rec"),
        ],
    },
    {
        "group": "Food",
        "title": "Pasta & Bread",
        "sizes": [""],
        "items": [
            item("Classic Carbonara", 199),
            item("Lasagna Supreme", None, tag="best"),  # price not readable on the menu photo
            item("Cuppa Brew Sandwich", 170),
            item("Chicken Sandwich", 180),
        ],
    },
    {
        "group": "Food",
        "title": "Salad",
        "subtitle": "100% organic",
        "sizes": [""],
        "items": [
            item("Mango Garden Salad", 255, desc="For sharing (2-3 persons)", tag="best"),
            item("Mango Garden Salad (Solo)", 185),
        ],
    },
]

CATEGORY_ICONS = {
    "Coffee Based": "☕", "Cloud Series": "☁️", "Matcha Picks": "🍵", "Frappes": "🥤",
    "Non-Coffee": "🍓", "Soda Series": "🍹", "Brewed Tea": "🌿", "Sugarcane Juice": "🎋",
    "Fruit Shakes": "🥭", "Croffles": "🧇", "Pica-Pica Corner": "🍟", "Rice Meals": "🍛",
    "Pasta & Bread": "🍝", "Salad": "🥗",
}

for cat in MENU:
    cat["id"] = cat["title"].lower().replace(" & ", "-").replace(" ", "-")
    cat["icon"] = CATEGORY_ICONS.get(cat["title"], "🍽️")

FAVORITES = [
    ("Spanish w/ Banana Pudds", "Our Spanish latte topped with banana pudding ice cream.", "☕", "from ₱215"),
    ("Whisked Kyoto", "Ceremonial matcha with oat milk. Great for matcha beginners.", "🍵", "₱215"),
    ("Loaded Biscoff Croffle", "Crispy croffle with whip cream and Biscoff everything.", "🧇", "₱150"),
    ("Biscoff Cloud", "Espresso and milk under a fluffy cold foam cloud.", "☁️", "from ₱185"),
]

TAGS = {"new": "New", "best": "Best seller", "rec": "Recommended"}


@app.template_filter("peso")
def peso(value):
    return f"₱{value:,.0f}"


@app.context_processor
def inject_shop():
    return {"shop": SHOP, "tags": TAGS}


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def find_photo(folder, slug):
    """Return 'images/<folder>/<slug>.<ext>' if that photo exists in static/, else None."""
    for ext in ("jpg", "jpeg", "png", "webp"):
        rel = f"images/{folder}/{slug}.{ext}"
        if os.path.exists(os.path.join(app.static_folder, rel)):
            return rel
    return None


# Until a category has its own photo in static/images/categories/<id>.jpg,
# borrow the photo of a favorite from that category.
CATEGORY_PHOTO_FALLBACK = {
    "coffee-based": "spanish-w-banana-pudds",
    "cloud-series": "biscoff-cloud",
    "matcha-picks": "whisked-kyoto",
    "croffles": "loaded-biscoff-croffle",
}
# Where to crop a category photo when the food isn't near the top (CSS background-position).
CATEGORY_PHOTO_POSITION = {
    "croffles": "center 60%",
    "non-coffee": "center 35%",
    "frappes": "center 30%",
    "pica-pica-corner": "center 85%",
    "pasta-bread": "center 80%",
    "salad": "center 75%",
    "rice-meals": "center 75%",
}


@app.route("/")
def home():
    # A favorite gets a photo background when static/images/favorites/<slug>.jpg exists;
    # otherwise its card falls back to the emoji icon.
    favorites = [
        {"name": name, "desc": desc, "icon": icon, "price": price,
         "photo": find_photo("favorites", slugify(name))}
        for name, desc, icon, price in FAVORITES
    ]
    return render_template("index.html", favorites=favorites)


@app.route("/menu")
def menu():
    for cat in MENU:
        fallback = CATEGORY_PHOTO_FALLBACK.get(cat["id"])
        cat["photo"] = find_photo("categories", cat["id"]) or (
            find_photo("favorites", fallback) if fallback else None)
        cat["photo_pos"] = CATEGORY_PHOTO_POSITION.get(cat["id"])
    return render_template("menu.html", menu=MENU)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        message = request.form.get("message", "").strip()
        if not name or not message:
            flash("Please fill in your name and a message.", "error")
        else:
            # A real site would save this or email it to the cafe.
            print(f"New message from {name}: {message}")
            flash(f"Thanks, {name}! We'll get back to you soon.", "success")
            return redirect(url_for("contact"))
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True)
