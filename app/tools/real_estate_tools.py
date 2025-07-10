from pydantic_ai import RunContext
from app.models.user_models import UserInput

async def search_properties(
    ctx: RunContext[UserInput],
    preco_min: float = None,
    preco_max: float = None,
    tamanho_min: float = None,
    tamanho_max: float = None,
    n_quartos: int = None,
    n_banheiros: int = None,
    n_garagem: int = None,
    rua: str = None,
    bairro: str = None,
    cidade: str = None,
) -> str:
    """
    Searches for properties in the database based on the provided filters.

    Args:
        preco_min: Minimum price of the property.
        preco_max: Maximum price of the property.
        tamanho_min: Minimum size of the property.
        tamanho_max: Maximum size of the property.
        n_quartos: Number of bedrooms.
        n_banheiros: Number of bathrooms.
        n_garagem: Number of garage spaces.
        rua: Street name (partial match).
        bairro: Neighborhood name (partial match).
        cidade: City name (partial match).

    Returns:
        A markdown table with the properties found, or an empty table if no properties match.
    """
    base_query = "SELECT id, preco, tamanho, cidade, bairro, rua, n_quartos, n_banheiros, n_garagem FROM propriedades"
    filters = []
    params = {}

    if preco_min is not None:
        filters.append(f"preco >= {preco_min}")
        params["preco_min"] = preco_min
    if preco_max is not None:
        filters.append(f"preco <= {preco_max}")
        params["preco_max"] = preco_max
    if tamanho_min is not None:
        filters.append(f"tamanho >= {tamanho_min}")
        params["tamanho_min"] = tamanho_min
    if tamanho_max is not None:
        filters.append(f"tamanho <= {tamanho_max}")
        params["tamanho_max"] = tamanho_max
    if n_quartos is not None:
        filters.append(f"n_quartos = {n_quartos}")
        params["n_quartos"] = n_quartos
    if n_banheiros is not None:
        filters.append(f"n_banheiros = {n_banheiros}")
        params["n_banheiros"] = n_banheiros
    if n_garagem is not None:
        filters.append(f"n_garagem = {n_garagem}")
        params["n_garagem"] = n_garagem
    if rua is not None:
        filters.append(f"rua ILIKE '%{rua}%'")
        params["rua"] = f"%{rua}%"
    if bairro is not None:
        filters.append(f"bairro ILIKE '%{bairro}%'")
        params["bairro"] = f"%{bairro}%"
    if cidade is not None:
        filters.append(f"cidade ILIKE '%{cidade}%'")
        params["cidade"] = f"%{cidade}%"

    if filters:
        base_query += " WHERE " + " AND ".join(filters)

    df = ctx.deps.connection.execute(base_query).fetch_df()
    return df.to_markdown(index=False)
