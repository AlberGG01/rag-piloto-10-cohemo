# -*- coding: utf-8 -*-
"""
Context Rewriter Agent
Responsabilidad: Reescribir la consulta del usuario para hacerla independiente del contexto (Standalone Query).
Usa el historial de chat para resolver correferencias (ej: "su importe" -> "importe del contrato X").
"""

import logging
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from src.graph.state import WorkflowState

# Cargar variables de entorno
load_dotenv()
logger = logging.getLogger(__name__)

# Configuración del Modelo Ligero (Requisito: gpt-4o-mini)
MODEL_REWRITER = "gpt-4o-mini"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class ContextRewriter:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=MODEL_REWRITER,
            temperature=0,
            api_key=OPENAI_API_KEY
        )
        
        # System Prompt con ejemplos Few-Shot de dominio de contratos
        self.system_prompt = """Eres un experto en lingüística y contratos de defensa. Tu única tarea es reescribir preguntas de seguimiento para que sean TOTALMENTE INDEPENDIENTES (Standalone), basándote en el historial de chat.

REGLAS CRÍTICAS:
1. Si la pregunta ya es independiente o no requiere contexto, DEVUÉLVELA INTACTA. No la modifiques.
2. Si la pregunta usa pronombres ("su", "el contrato", "este", "la adjudicataria") o es implícita ("¿y la fecha?"), reemplázalos con la entidad específica mencionada en la conversación previa.
3. NO respondas a la pregunta. Solo reescríbela.

EJEMPLOS (Dominio Defensa):

Historial:
User: ¿Quién ganó el contrato SER_2024_015?
AI: Fue adjudicado a Airbus.
Input: ¿Y cuál es su importe total?
Output: ¿Cuál es el importe total del contrato SER_2024_015?

Historial:
User: Háblame del contrato de Ciberseguridad.
AI: El contrato CON_2024_004 tiene por objeto...
Input: ¿Qué penalizaciones tiene?
Output: ¿Qué penalizaciones tiene el contrato CON_2024_004 de Ciberseguridad?

Historial:
User: Lista los contratos de munición.
AI: Aquí tienes la lista...
Input: Gracias, eso es todo.
Output: Gracias, eso es todo. (Intacta)
"""

    def rewrite(self, state: WorkflowState) -> dict:
        """
        Nodo del grafo que reescribe la query si es necesario.
        """
        current_query = state.get("query", "")
        chat_history = state.get("chat_history", [])
        
        # Si no hay historial, no hay nada que reescribir
        if not chat_history:
            logger.info("❌ No context history. Keeping original query.")
            return {"query": current_query}
            
        logger.info(f"📝 Rewriting query with context. History length: {len(chat_history)}")
        
        # Construir mensajes para el LLM
        messages = [
            SystemMessage(content=self.system_prompt),
        ]
        
        # Añadir historial reciente (últimos 5 mensajes para contexto inmediato)
        # Asumimos que chat_history es una lista de dicts o BaseMessages
        # Formato esperado en state: [{'role': 'user', 'content': '...'}, {'role': 'assistant', 'content': '...'}]
        for msg in chat_history[-5:]:
            if isinstance(msg, dict):
                role = msg.get("role")
                content = msg.get("content")
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))
            else:
                # Soporte para BaseMessage objects
                messages.append(msg)
                
        # Añadir la query actual
        messages.append(HumanMessage(content=f"Input: {current_query}"))
        
        try:
            # Invocar modelo
            response = self.llm.invoke(messages)
            rewritten_query = response.content.strip()
            
            # Log si hubo cambios significativos
            if rewritten_query != current_query:
                logger.info(f"🔄 Query Rewritten: '{current_query}' -> '{rewritten_query}'")
            else:
                logger.info("✅ Query kept intact.")
                
            return {"query": rewritten_query}
            
        except Exception as e:
            logger.error(f"⚠️ Error in ContextRewriter: {e}")
            # Fallback: devolver query original
            return {"query": current_query}
