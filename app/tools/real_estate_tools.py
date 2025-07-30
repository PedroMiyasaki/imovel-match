from pydantic_ai import RunContext, ModelRetry
from app.models.user_models import UserInput
from app.agents.real_estate_agent import real_state_agent
from app.utils.general import check_if_property_exists, check_if_slot_exists
from unidecode import unidecode

@real_state_agent.tool(retries=3)
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
    Use this tool to search for real estate properties based on user-provided criteria.
    All parameters are optional. The more criteria provided, the more specific the search.

    Args:
        preco_min (float): Minimum price of the property.
        preco_max (float): Maximum price of the property.
        tamanho_min (float): Minimum size of the property.
        tamanho_max (float): Maximum size of the property.
        n_quartos (int): Number of bedrooms.
        n_banheiros (int): Number of bathrooms.
        n_garagem (int): Number of garage spaces.
        rua (str): Street name (partial match).
        bairro (str): Neighborhood name (partial match).
        cidade (str): City name (partial match).

    Returns:
        A markdown table with the properties found, or an empty table if no properties match.
    """
    base_query = "SELECT property_id, preco, tamanho, cidade, bairro, rua, n_quartos, n_banheiros, n_garagem FROM properties"
    filters = []
    params = {}

    if rua is not None:
        rua = unidecode(rua)
    if bairro is not None:
        bairro = unidecode(bairro)
    if cidade is not None:
        cidade = unidecode(cidade)

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
        filters.append(f"bairro ILIKE '%{bairro.lower()}%'")
        params["bairro"] = f"%{bairro.lower()}%"
    if cidade is not None:
        filters.append(f"cidade ILIKE '%{cidade.lower()}%'")
        params["cidade"] = f"%{cidade.lower()}%"

    if filters:
        base_query += " WHERE " + " AND ".join(filters)

    df = ctx.deps.connection.execute(base_query).fetch_df()

    if df.empty:
        raise ModelRetry(
"""No properties found for the given filters.
Please try again with less specific filters.
But if you are looking for a specific property using almost all parameters, review parameters values.
IMPORTANT: If you are ussing the `rua` parameter to find a specific property, review the value used.
Rua names tend to have lexical variations, so try ussing a different value for this parameter.""")
    
    return df.to_markdown(index=False)

@real_state_agent.tool(retries=3)
async def get_property_slots(ctx: RunContext[UserInput], property_id: str) -> str:
    """
    Use this tool to get the available time slots for visiting a specific property.

    Args:
        property_id (str): The unique identifier of the property.
    
    Returns:
        A markdown table with the available slots for the given property.
    """
    if not await check_if_property_exists(ctx.deps.connection, property_id):
        raise ModelRetry(
            f"""Property id not found in the database. ID: {property_id}
Check the `property_id` and try again."""
        )

    df = ctx.deps.connection.execute(f"SELECT * FROM property_slots WHERE property_id = '{property_id}' AND status = 'free'").fetch_df()
    df = df.sort_values(by="slot_start").head(10)
    return df.to_markdown(index=False)

@real_state_agent.tool(retries=3)
async def book_property_slot(ctx: RunContext[UserInput], property_id: str, slot_start: str) -> str:
    """
    Use this tool to book a visit to a specific property at a given time.

    Args:
        property_id (str): The unique identifier of the property to book.
        slot_start (str): The desired start time for the visit, in 'YYYY-MM-DD HH:MM:SS' format.

    Returns:
        A confirmation message if the booking is successful.
    """
    if not await check_if_property_exists(ctx.deps.connection, property_id):
        raise ModelRetry(
            f"""Property id not found in the database. ID: {property_id}
Check the `property_id` and try again."""
        )
    if not await check_if_slot_exists(ctx.deps.connection, property_id, slot_start):
        raise ModelRetry(
            f"""Slot {slot_start} is not available for property {property_id}
Check the `slot_start` and try again."""
        )

    ctx.deps.connection.execute(f"UPDATE property_slots SET status = 'booked' WHERE property_id = '{property_id}' AND slot_start = '{slot_start}'")
    return f"Slot {slot_start} booked for property {property_id}."

@real_state_agent.tool(retries=3)
async def cancel_property_slot(ctx: RunContext[UserInput], property_id: str, slot_start: str) -> str:
    """
    Use this tool to cancel a previously booked visit to a property.

    Args:
        property_id (str): The unique identifier of the property for the visit to be canceled.
        slot_start (str): The start time of the visit to be canceled, in 'YYYY-MM-DD HH:MM:SS' format.

    Returns:
        A confirmation message if the cancellation is successful.
    """
    if not await check_if_property_exists(ctx.deps.connection, property_id):
        raise ModelRetry(
            f"""Property id not found in the database. ID: {property_id}
Check the `property_id` and try again."""
        )
    if not await check_if_slot_exists(ctx.deps.connection, property_id, slot_start):
        raise ModelRetry(
            f"""Slot {slot_start} is not available for property {property_id}
Check the `slot_start` and try again."""
        )
        
    ctx.deps.connection.execute(f"UPDATE property_slots SET status = 'free' WHERE property_id = '{property_id}' AND slot_start = '{slot_start}'")
    return f"Slot {slot_start} cancelled for property {property_id}."
