import logging
import random
from langchain_core.tools import tool

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger("a2a").setLevel(logging.ERROR)

@tool
def restock_func(products: list) -> list:
    """This function is called when the wholesaler agent receives a restock request."""
    logging.info(f"Received restock request: {products}")
    response = []
    for product in products:
        restocked_quantity = int(product['quantity'] * random.uniform(0.5, 1.0))
        response.append({
            "product_id": product['product_id'],
            "quantity": restocked_quantity
        })
    logging.info(f"Restock response: {response}")
    return response

def get_tools():
    return [restock_func]
