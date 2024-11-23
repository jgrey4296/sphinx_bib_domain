
from sphinx_bib_domain import DOMAIN_NAME

def anchor(sig) -> str:
    return f"{DOMAIN_NAME}-{sig}"

def fsig(sig) -> str:
    return f"{DOMAIN_NAME}.{sig}"
