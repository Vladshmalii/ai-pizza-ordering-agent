import json
from typing import Annotated

from livekit.agents import llm
from src.api import fake_api

@llm.function_tool(description="Повертає меню піцерії. Може фільтрувати за категорією: 'pizza', 'drinks', 'desserts'.")
async def get_menu(
    category: Annotated[str | None, "Категорія меню ('pizza', 'drinks', 'desserts') або None для всього меню"] = None,
) -> str:
    res = fake_api.get_menu(category)
    return json.dumps(res, ensure_ascii=False)

@llm.function_tool(description="Отримує повну інформацію про страву (склад, ціну, розмір, наявність) за її ID.")
async def get_item_details(
    item_id: Annotated[str, "ID позиції меню (наприклад 'pz1', 'dr1')"],
) -> str:
    res = fake_api.get_item_details(item_id)
    return json.dumps(res, ensure_ascii=False)

@llm.function_tool(description="Оформлює замовлення.")
async def create_order(
    items: Annotated[list[dict], "Список позицій для замовлення. Приклад: [{'id': 'pz1', 'quantity': 2}]"],
    customer_name: Annotated[str, "Ім'я клієнта"],
    phone: Annotated[str, "Номер телефону клієнта"],
    address: Annotated[str, "Адреса доставки"],
) -> str:
    normalized_items = []
    for item in items:
        if "item_id" in item and "id" not in item:
            item["id"] = item["item_id"]
        normalized_items.append(item)
    res = fake_api.create_order(normalized_items, customer_name, phone, address)
    return json.dumps(res, ensure_ascii=False)

@llm.function_tool(description="Перевіряє статус замовлення за його номером (ID) або ім'ям клієнта.")
async def get_order_status(
    order_id_or_name: Annotated[str, "Номер замовлення (наприклад 'ORD-101', '101') або ім'я клієнта (наприклад 'Дмитро')"],
) -> str:
    normalized_id = order_id_or_name.upper().strip()
    if normalized_id.startswith("ORD") and not normalized_id.startswith("ORD-"):
        normalized_id = "ORD-" + normalized_id[3:]
    elif normalized_id.isdigit():
        normalized_id = "ORD-" + normalized_id

    res = fake_api.get_order_status(normalized_id)
    if res.get("success", True) is not False:
        return json.dumps(res, ensure_ascii=False)

    for oid, order in fake_api.ORDERS.items():
        if order_id_or_name.lower() in order.get("customer_name", "").lower():
            return json.dumps(order, ensure_ascii=False)

    return json.dumps({"success": False, "error": f"Замовлення '{order_id_or_name}' не знайдено ані за номером, ані за ім'ям клієнта"}, ensure_ascii=False)
