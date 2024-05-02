import json
import urllib.parse
import requests
from pydantic import BaseModel, Field
from phi.assistant import Assistant
from phi.llm.groq import Groq

def get_products(product:str ) -> str:
    """Call this tool to search for products based on the user's query. 
        The tool searches the product catalog and returns relevant products along with their URLs.
        It can handle queries specifying product attributes like name, color, condition, storage type, and price range.
    Args:
        product (str): User's query describing the desired product and its attributes.
    Returns:
        str: A formatted string listing the matching products and their URLs.
    """ 


    class ProductSpecs(BaseModel):
        product_name: str = Field(None, description="Name of the product.")
        product_color: str = Field(None, description="Color of the product the user asked for(null if unspecified).")
        product_condition: str = Field(None, description="Condition of the product the user asked for(null if unspecified).")
        product_storage: str = Field(None, description="Storage type of the product the user asked for(null if unspecified) .")
        price_minimum: float = Field(None, description="Minimum user budget for the product the user asked for(null if unspecified).")
        price_maximum: float = Field(None, description="Maximum user budget for the productthe user asked for(null if unspecified).")



    jsagent = Assistant(
        llm=Groq(model="llama3-8b-8192"),
        description="You task is to extract product specifications from user queries.",
        output_model=ProductSpecs
    )


    data_str = jsagent.run(product)
    print(data_str)

    ##data_json = data_str.strip('`')
    data = json.loads(data_str)




    filter_url_fragments = []

    # Check for 'product_name' and append if not None
    if 'product_name' in data and data['product_name'] is not None:
        filter_url_fragments.append(('query', data['product_name']))
    # Check for 'product_condition' and append if not None
    if 'product_condition' in data and data['product_condition'] is not None:
        filter_url_fragments.append(('filter_attr_221_condition', data['product_condition']))
    # Check for 'product_color' and append if not None
    if 'product_color' in data and data['product_color'] is not None:
        filter_url_fragments.append(('filter_attr_108_colour', data['product_color']))
    # Check for 'product_storage' and append if not None
    if 'product_storage' in data and data['product_storage'] is not None:
        filter_url_fragments.append(('filter_attr_1010_internal_storage', str(data['product_storage'])))
    # Check for 'price_minimum' and 'price_maximum' and append if not None
    if 'price_minimum' in data and 'price_maximum' in data and data['price_minimum'] is not None and data['price_maximum'] is not None:
        min_price = data['price_minimum'] - 500 if data['price_minimum'] > 500 else 0
        max_price = data['price_maximum'] + 500
        filter_url_fragments.append(('price_min', str(min_price)))
        filter_url_fragments.append(('price_max', str(max_price)))


    
    # Encode the filter URL fragments into a query string
    query_params = urllib.parse.urlencode(filter_url_fragments)
    print(query_params)
    url = "https://pupps.onrender.com/scrape"
    payload = {
        "url": "https://jiji.com.et/mobile-phones",
        "query": query_params
    }


    response = requests.post(url, json=payload)
    print(response.json())
    return json.dumps(response.json())