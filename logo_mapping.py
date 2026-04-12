"""
Logo Mapping für Portfolio-Ticker
Ordnet jeden Ticker einer Firmen-Domain zu für Clearbit Logo API.
Mit Fallback auf ein generisches Platzhalter-Icon, falls kein
spezifisches Logo verfügbar ist.
"""

# Ticker → Domain Mapping für Logo-URLs
TICKER_DOMAINS = {
    # Deutsche Aktien
    'ALV.DE': 'allianz.com',
    'SAP.DE': 'sap.com',
    'BAS.DE': 'basf.com',
    'BAYN.DE': 'bayer.com',
    '14D.DE': 'datron.de',

    # US Aktien
    'NVDA': 'nvidia.com',
    'RKLB': 'rocketlabusa.com',
    'POET': 'poet-technologies.com',
    'ROOT': 'joinroot.com',
    'AAPL': 'apple.com',
    'MSFT': 'microsoft.com',
    'INTC': 'intel.com',
    'PYPL': 'paypal.com',
    'NKE': 'nike.com',

    # UK Aktien
    'BATS.L': 'bat.com',

    # Skandinavien
    'NOVO-B.CO': 'novonordisk.com',
    'PCELL.ST': 'powercell.se',

    # Frankreich
    'VIE.PA': 'veolia.com',

    # Griechenland
    'THEON.AS': 'theon.com',

    # ETFs
    'XAMB.DE': 'xtrackers.com',
    'DGIT.L': 'ishares.com',
    'IWDA.AS': 'ishares.com',
    'DBX0.DE': 'xtrackers.com',
    'VGEJ.DE': 'vanguard.com',
    'VWCE.DE': 'vanguard.com',

    # Crypto
    'XRP-USD': 'ripple.com',
    'ETH-USD': 'ethereum.org',
    'BTC-USD': 'bitcoin.org',

    # Gold und Edelmetalle (oft keine Clearbit-Logos verfügbar)
    'GOLD-750': 'gold.org',
    'VRENELI-20FR': 'swissmint.ch',
    'NL-10G-WILLEM3': 'knm.nl',
    'SOVEREIGN-VICTORIA': 'royalmint.com',
}

# Generisches Platzhalter-Icon, falls kein spezifisches Logo verfügbar ist.
# Nutzt ein neutrales SVG-Icon von einem öffentlichen CDN.
FALLBACK_LOGO_URL = (
    "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f4ca.png"
)

# Tickers, für die direkt der Fallback genutzt werden soll, weil Clearbit
# bekanntermaßen kein Logo liefert (z.B. physisches Gold, Sammlermünzen).
USE_FALLBACK_DIRECTLY = {
    'GOLD-750',
    'VRENELI-20FR',
    'NL-10G-WILLEM3',
    'SOVEREIGN-VICTORIA',
}


def get_logo_url(ticker: str) -> str:
    """
    Generiere Logo-URL für einen Ticker.

    Strategie:
    1. Wenn der Ticker in USE_FALLBACK_DIRECTLY steht, gib direkt das
       Fallback-Icon zurück (spart unnötige Clearbit-Aufrufe).
    2. Wenn der Ticker im Mapping ist, baue die Clearbit-URL.
    3. Wenn der Ticker unbekannt ist, gib das Fallback-Icon zurück.

    Args:
        ticker: Portfolio-Ticker (z.B. 'NVDA', 'ALV.DE')

    Returns:
        URL zu einem Logo-Bild (Clearbit oder Fallback)
    """
    if ticker in USE_FALLBACK_DIRECTLY:
        return FALLBACK_LOGO_URL

    domain = TICKER_DOMAINS.get(ticker)
    if domain is None:
        return FALLBACK_LOGO_URL

    return f"https://www.google.com/s2/favicons?domain={domain}&sz=64"


def get_region(ticker: str) -> str:
    """
    Automatische geografische Zuordnung aus Ticker.

    Args:
        ticker: Portfolio-Ticker

    Returns:
        Region-Name (Europa, Nordamerika, International)
    """
    # Spezielle ETFs → International
    if ticker in ['XAMB.DE', 'DBX0.DE', 'VGEJ.DE', 'DGIT.L', 'IWDA.AS', 'VWCE.DE']:
        return 'International'

    # Crypto & Gold → International
    if ticker.endswith('-USD') or ticker.startswith('GOLD') or \
       ticker.startswith('VRENELI') or ticker.startswith('NL-10G') or \
       ticker.startswith('SOVEREIGN'):
        return 'International'

    # Europa (alle europäischen Börsen)
    if ticker.endswith('.DE') or ticker.endswith('.L') or \
       ticker.endswith('.AS') or ticker.endswith('.PA') or \
       ticker.endswith('.CO') or ticker.endswith('.ST'):
        return 'Europa'

    # Nordamerika (USA/Kanada - kein Suffix)
    return 'Nordamerika'