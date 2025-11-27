"""Example demonstrating scrollable menus with many options.

This example shows how menus automatically scroll when there are more
options than can fit on the screen. Try resizing your terminal to see
the scrolling behavior adapt.
"""

from typing import List

from rich_toolkit import RichToolkit
from rich_toolkit.menu import Option
from rich_toolkit.styles.border import BorderedStyle
from rich_toolkit.styles.tagged import TaggedStyle


def get_country_options() -> List[Option[str]]:
    """Generate a large list of country options to demonstrate scrolling."""
    countries = [
        "Afghanistan",
        "Albania",
        "Algeria",
        "Andorra",
        "Angola",
        "Argentina",
        "Armenia",
        "Australia",
        "Austria",
        "Azerbaijan",
        "Bahamas",
        "Bahrain",
        "Bangladesh",
        "Barbados",
        "Belarus",
        "Belgium",
        "Belize",
        "Benin",
        "Bhutan",
        "Bolivia",
        "Bosnia and Herzegovina",
        "Botswana",
        "Brazil",
        "Brunei",
        "Bulgaria",
        "Burkina Faso",
        "Burundi",
        "Cambodia",
        "Cameroon",
        "Canada",
        "Cape Verde",
        "Central African Republic",
        "Chad",
        "Chile",
        "China",
        "Colombia",
        "Comoros",
        "Congo",
        "Costa Rica",
        "Croatia",
        "Cuba",
        "Cyprus",
        "Czech Republic",
        "Denmark",
        "Djibouti",
        "Dominica",
        "Dominican Republic",
        "Ecuador",
        "Egypt",
        "El Salvador",
        "Equatorial Guinea",
        "Eritrea",
        "Estonia",
        "Ethiopia",
        "Fiji",
        "Finland",
        "France",
        "Gabon",
        "Gambia",
        "Georgia",
        "Germany",
        "Ghana",
        "Greece",
        "Grenada",
        "Guatemala",
        "Guinea",
        "Guinea-Bissau",
        "Guyana",
        "Haiti",
        "Honduras",
        "Hungary",
        "Iceland",
        "India",
        "Indonesia",
        "Iran",
        "Iraq",
        "Ireland",
        "Israel",
        "Italy",
        "Jamaica",
        "Japan",
        "Jordan",
        "Kazakhstan",
        "Kenya",
        "Kiribati",
        "Kuwait",
        "Kyrgyzstan",
        "Laos",
        "Latvia",
        "Lebanon",
        "Lesotho",
        "Liberia",
        "Libya",
        "Liechtenstein",
        "Lithuania",
        "Luxembourg",
        "Madagascar",
        "Malawi",
        "Malaysia",
        "Maldives",
        "Mali",
        "Malta",
        "Marshall Islands",
        "Mauritania",
        "Mauritius",
        "Mexico",
        "Micronesia",
        "Moldova",
        "Monaco",
        "Mongolia",
        "Montenegro",
        "Morocco",
        "Mozambique",
        "Myanmar",
        "Namibia",
        "Nauru",
        "Nepal",
        "Netherlands",
        "New Zealand",
        "Nicaragua",
        "Niger",
        "Nigeria",
        "North Korea",
        "North Macedonia",
        "Norway",
        "Oman",
        "Pakistan",
        "Palau",
        "Palestine",
        "Panama",
        "Papua New Guinea",
        "Paraguay",
        "Peru",
        "Philippines",
        "Poland",
        "Portugal",
        "Qatar",
        "Romania",
        "Russia",
        "Rwanda",
        "Saint Kitts and Nevis",
        "Saint Lucia",
        "Saint Vincent and the Grenadines",
        "Samoa",
        "San Marino",
        "Sao Tome and Principe",
        "Saudi Arabia",
        "Senegal",
        "Serbia",
        "Seychelles",
        "Sierra Leone",
        "Singapore",
        "Slovakia",
        "Slovenia",
        "Solomon Islands",
        "Somalia",
        "South Africa",
        "South Korea",
        "South Sudan",
        "Spain",
        "Sri Lanka",
        "Sudan",
        "Suriname",
        "Sweden",
        "Switzerland",
        "Syria",
        "Taiwan",
        "Tajikistan",
        "Tanzania",
        "Thailand",
        "Timor-Leste",
        "Togo",
        "Tonga",
        "Trinidad and Tobago",
        "Tunisia",
        "Turkey",
        "Turkmenistan",
        "Tuvalu",
        "Uganda",
        "Ukraine",
        "United Arab Emirates",
        "United Kingdom",
        "United States",
        "Uruguay",
        "Uzbekistan",
        "Vanuatu",
        "Vatican City",
        "Venezuela",
        "Vietnam",
        "Yemen",
        "Zambia",
        "Zimbabwe",
    ]
    return [{"name": country, "value": country} for country in countries]


def get_numbered_options(count: int = 50) -> List[Option[int]]:
    """Generate numbered options for simple demonstration."""
    return [{"name": f"Option {i + 1}", "value": i + 1} for i in range(count)]


theme = {
    "tag.title": "black on #A7E3A2",
    "tag": "white on #893AE3",
    "placeholder": "grey85",
    "text": "white",
    "selected": "green",
    "result": "grey85",
    "progress": "on #893AE3",
}


def main():
    print("=" * 60)
    print("Scrollable Menu Example")
    print("=" * 60)
    print()
    print("This example demonstrates menus that automatically scroll")
    print("when there are more options than can fit on the screen.")
    print()
    print("Use arrow keys (or j/k) to navigate, Enter to select.")
    print("The menu will scroll as you move past visible options.")
    print()

    # Example 1: Simple scrollable menu with TaggedStyle
    print("-" * 60)
    print("Example 1: Numbered options with TaggedStyle")
    print("-" * 60)

    with RichToolkit(style=TaggedStyle(tag_width=12, theme=theme)) as app:
        result = app.ask(
            "Select a number (50 options):",
            tag="number",
            options=get_numbered_options(50),
        )
        app.print_line()
        app.print(f"You selected: {result}", tag="result")

    print()

    # Example 2: Country picker with filtering and BorderedStyle
    print("-" * 60)
    print("Example 2: Country picker with filtering (BorderedStyle)")
    print("-" * 60)
    print("Tip: Type to filter the list!")
    print()

    with RichToolkit(style=BorderedStyle(theme=theme)) as app:
        country = app.ask(
            "Select your country:",
            tag="country",
            options=get_country_options(),
            allow_filtering=True,
        )
        app.print_line()
        app.print(f"You selected: {country}", tag="result")

    print()

    # Example 3: Explicitly limited max_visible
    print("-" * 60)
    print("Example 3: Explicitly limited to 5 visible options")
    print("-" * 60)

    from rich_toolkit.menu import Menu

    with RichToolkit(style=TaggedStyle(tag_width=12, theme=theme)) as app:
        # Create menu with explicit max_visible limit
        menu = Menu(
            label="Pick a programming language:",
            options=[
                {"name": "Python", "value": "python"},
                {"name": "JavaScript", "value": "js"},
                {"name": "TypeScript", "value": "ts"},
                {"name": "Rust", "value": "rust"},
                {"name": "Go", "value": "go"},
                {"name": "Java", "value": "java"},
                {"name": "C++", "value": "cpp"},
                {"name": "C#", "value": "csharp"},
                {"name": "Ruby", "value": "ruby"},
                {"name": "PHP", "value": "php"},
                {"name": "Swift", "value": "swift"},
                {"name": "Kotlin", "value": "kotlin"},
            ],
            style=app.style,
            max_visible=5,  # Only show 5 options at a time
        )

        result = menu.ask()
        app.print_line()
        app.print(f"You selected: {result}", tag="result")

    print()
    print("=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
