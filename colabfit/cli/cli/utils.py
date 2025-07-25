from pprint import pprint
import json
import os
import psycopg
from psycopg.rows import dict_row

def _query(dbname, user, password, host, port, text=None, elements=None, elements_exact=None, properties=None):

    query_conditions = []

    if text is not None:
        # Full-text search condition
        query_conditions.append(f"to_tsvector('english', name || ' ' || description || ' ' || array_to_string(authors, ' ')) @@ to_tsquery('english', '{text}')")

    if elements is not None:
        if elements_exact is not None:
            raise Exception('Only one of elements or elements-exact should be specified')
        else:
            # Check if elements array contains all specified elements
            formatted_elements = ", ".join([f"'{e.capitalize()}'" for e in elements.split(' ')])
            query_conditions.append(f"elements @> ARRAY[{formatted_elements}]::VARCHAR[]")

    if elements_exact is not None:
        # Check if elements array matches size and contains exactly the specified elements
        ee = [e.upper() for e in elements_exact.split(' ')]
        formatted_elements_exact = ", ".join([f"'{e}'" for e in ee])
        query_conditions.append(
            f"array_length(elements, 1) = {len(ee)} AND elements @> ARRAY[{formatted_elements_exact}]::VARCHAR[]"
        )

    if properties is not None:
        # Check if property_types array contains all specified properties
        formatted_properties = properties.split(' ')
        for p in formatted_properties:
            query_conditions.append("{p}_count > 0")

    # Combine conditions into a single SQL WHERE clause
    where_clause = " AND ".join(query_conditions)
    if where_clause:
        sql_query = f"SELECT * FROM datasets WHERE {where_clause} ORDER by last_modified;"
    else:    
        sql_query = f"SELECT * FROM datasets ORDER by last_modified;"


    with psycopg.connect(dbname=dbname, user=user, password=password , port=port, host=host, row_factory=dict_row) as conn:
            with conn.cursor() as curs:
                 curs.execute(sql_query)
                 return curs.fetchall()

    
def format_print(doc):
    new_doc={}
    new_doc['colabfit-id']=doc['id']
    new_doc['name']=doc['name']
    new_doc['authors']=doc['authors']
    new_doc['description']=doc['description']
    new_doc['elements']=doc['elements']  
    new_doc['nconfigurations']=doc['nconfigurations']
    new_doc['natoms']=doc['nsites']
    new_doc['uploader'] = doc['uploader']
    pprint (new_doc,sort_dicts=False)
