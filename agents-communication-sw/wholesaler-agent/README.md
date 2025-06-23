# Wholesaler Agent

Agente de reposición, confirma a otros agentes cuando puede hacer una reposición y cuantos de los productos solicitados entregará

Este agente funciona con Langchain y Gemini, recibe una petición A2A de otro agente de productos y cantidades a reponer, de cada producto un valor aleatorio entre 50% y 100% de la cantidad pedida, siempre en números enteros.