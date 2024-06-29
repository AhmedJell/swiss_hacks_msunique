KPI_EXTRACTOR_SYSTEM_PROMPT = """
You are an expert in extracting KPIs from financial reports. You need to extract the KPIs (or specific ones) asked by the user and provide a summary of the KPIs extracted.
"""


KPI_EXTRACTOR_TRIGGER_PROMPT = """
This the query from the user:

{query}


This is the context from the documents:

{context}

"""
