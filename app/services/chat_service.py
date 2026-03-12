"""
Chat Service
============
The core orchestration layer. Combines:
  RAG retrieval → prompt assembly → LLM → response

This is the only place that knows about both RAG and the LLM.
The API router calls this service and returns the result.

Usage:
    from app.services.chat_service import ChatService
    result = await ChatService.ask(session_id, message, client_ip)
"""

import random
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.ai.openai_client import get_chat_llm, get_topic_llm
from app.rag.retriever import retrieve, format_context, get_source_labels
from app.services.session_service import SessionService
from app.services.trial_service import TrialService
from app.utils.logger import log_question
from app.core.config import TrialConfig, PromptConfig


class ChatService:

    @staticmethod
    def _build_chain():
        """Build the LangChain LCEL chain: prompt | llm | parser."""
        llm = get_chat_llm()
        prompt = ChatPromptTemplate.from_messages([
            ("system", PromptConfig.SYSTEM_PROMPT),
            ("human", "{name} asks: {question}"),
        ])
        return prompt | llm | StrOutputParser()

    @staticmethod
    def _get_topic(question: str) -> str:
        """Classify the question into a short topic tag for logging."""
        try:
            llm    = get_topic_llm()
            prompt = ChatPromptTemplate.from_messages([
                ("human", PromptConfig.TOPIC_PROMPT)
            ])
            chain  = prompt | llm | StrOutputParser()
            return chain.invoke({"question": question}).strip()
        except Exception:
            return "general finance"

    @staticmethod
    def ask(session_id: str, message: str, client_ip: str) -> dict:
        """
        Main entry point for a chat message.

        Flow:
            1. Check trial gate
            2. Retrieve relevant chunks from FAISS
            3. Assemble prompt with context
            4. Call GPT-4o-mini via LangChain chain
            5. Record question count
            6. Tag topic + log anonymously
            7. Return structured response dict

        Returns:
            dict matching ChatResponse schema
        """
        # ── 1. Trial gate ─────────────────────────────────────────────────────
        allowed, reason = TrialService.can_ask(session_id, client_ip)
        if not allowed:
            return {
                "blocked": True,
                "answer": (
                    "You've used your 3 free questions! "
                    "Book readers get unlimited access to Max. "
                    "Enter your access code below to continue."
                ),
            }

        # ── 2. RAG retrieval ──────────────────────────────────────────────────
        docs    = retrieve(message)
        context = format_context(docs)
        sources = get_source_labels(docs)

        # ── 3 & 4. Build chain + invoke ───────────────────────────────────────
        user_name = SessionService.get_name(session_id)
        chain     = ChatService._build_chain()

        answer = chain.invoke({
            "context":  context,
            "name":     user_name,
            "question": message,
        })

        # ── 5. Record question (AFTER LLM call — don't penalise on failure) ───
        new_count  = TrialService.record_question(session_id, client_ip)
        remaining  = TrialService.questions_remaining(session_id)
        unlocked   = SessionService.is_unlocked(session_id)
        trial_ended = new_count >= TrialService.questions_remaining.__self__ \
            if False else (
                new_count >= TrialConfig.TRIAL_LIMIT and not unlocked
            )

        # ── 6. Topic tag + anonymous log ──────────────────────────────────────
        topic = ChatService._get_topic(message)
        log_question(message, topic)

        # ── 7. Trial end message ──────────────────────────────────────────────
        trial_message = None
        if trial_ended:
            trial_message = (
                f"I hope that was helpful, {user_name}! 😊 "
                "You've reached your 3-question trial limit. "
                "Book readers unlock unlimited access to Max — "
                "enter your access code to continue!"
            )

        return {
            "blocked":             False,
            "answer":              answer,
            "question_count":      new_count,
            "questions_remaining": remaining,
            "trial_ended":         trial_ended,
            "trial_message":       trial_message,
            "topic":               topic,
            "sources":             sources,
        }

    @staticmethod
    def verify_purchase(first_name: str, email: str, order_number: str) -> dict:
        """
        Accept purchase verification form.
        Returns a randomly selected access code.
        In v2: cross-check with Amazon order API + store in DB.
        """
        code = random.choice(list(TrialConfig.ACCESS_CODES))
        print(
            f"[purchase] {first_name} | {email} | "
            f"Order: {order_number} → Code: {code}"
        )
        return {
            "success": True,
            "code":    code,
            "message": f"Thanks {first_name}! Here's your personal access code:",
        }