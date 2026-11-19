# Cuppa Brew Cafe

Website for **Cuppa Brew Cafe**, "your neighborhood cafe" in Rosewood Plains, Villa Kananga, Butuan City.
Built with Python and [Flask](https://flask.palletsprojects.com/).

## Pages

- **Home**: hero banner, customer favorites with photo cards, hours and socials
- **Menu**: blurred-cafe banner, swipeable photo carousel of the 14 categories, and the full price list
- **Visit**: address, Google Map, hours and a contact form

## Run it locally

```bash
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000.

## Editing content

- **Menu items and prices**: the `MENU` list in `app.py`
- **Customer favorites**: the `FAVORITES` list in `app.py`
- **Shop info** (address, hours, socials): the `SHOP` dict in `app.py`
- **Photos**: drop an image into `static/images/favorites/` or `static/images/categories/`,
  named after the item or category (for example `frappes.webp`). The card picks it up
  automatically; cards without a photo show an emoji icon instead.
- **Styles**: `static/style.css`

## Deploying

Set a `SECRET_KEY` environment variable to a long random string, and run without debug mode.
