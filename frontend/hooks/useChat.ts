// hooks/useChat.ts
// Custom hook — manages ALL chat state and logic.
// Components just call this hook and render what it returns.
// This is the React way: separate logic from presentation.

"use client"

import { useState, useEffect, useCallback, useRef } from "react"
import { v4 as uuidv4 } from "uuid"
import type { Message, Screen, SessionStatus } from "@/types"
import * as api from "@/lib/api"

// ── Initial greeting Max sends after name is entered ─────────────────────────
function buildGreeting(name: string, unlocked: boolean): Message {
  return {
    id: uuidv4(),
    role: "max",
    content: `Hi ${name}! 👋 I'm Max, your personal money coach. I'm here to help you navigate household finances, budgeting, building wealth, and understanding money concepts.\n\nYou have ${unlocked ? "unlimited" : "3 free"} questions — what's on your mind?`,
    timestamp: new Date(),
  }
}

export function useChat() {
  // ── Core state ──────────────────────────────────────────────────────────────
  const [screen, setScreen]         = useState<Screen>("name")
  const [sessionId, setSessionId]   = useState<string>("")
  const [userName, setUserName]     = useState<string>("")
  const [messages, setMessages]     = useState<Message[]>([])
  const [isTyping, setIsTyping]     = useState(false)
  const [isUnlocked, setIsUnlocked] = useState(false)
  const [questionCount, setQuestionCount]   = useState(0)
  const [questionsRemaining, setQuestionsRemaining] = useState(3)
  const [trialEnded, setTrialEnded] = useState(false)
  const [error, setError]           = useState<string | null>(null)

  // Ref to auto-scroll chat to bottom
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // ── Create session on mount ─────────────────────────────────────────────────
  useEffect(() => {
    const init = async () => {
      try {
        // Reuse saved session if available
        const saved = localStorage.getItem("mcm_session")
        if (saved) {
          const { sid } = JSON.parse(saved)
          const status: SessionStatus = await api.getSessionStatus(sid)
          if (status.name) {
            setSessionId(sid)
            setUserName(status.name)
            setIsUnlocked(status.unlocked)
            setQuestionCount(status.question_count)
            setQuestionsRemaining(status.questions_remaining)
            setMessages([buildGreeting(status.name, status.unlocked)])
            setScreen("chat")
            return
          }
        }
        // New session
        const { session_id } = await api.createSession()
        setSessionId(session_id)
        localStorage.setItem("mcm_session", JSON.stringify({ sid: session_id }))
      } catch {
        // Fallback: generate local session ID if backend isn't up
        const fallback = uuidv4()
        setSessionId(fallback)
      }
    }
    init()
  }, [])

  // ── Auto-scroll to latest message ───────────────────────────────────────────
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, isTyping])

  // ── Submit name ─────────────────────────────────────────────────────────────
  const submitName = useCallback(async (name: string) => {
    if (!name.trim()) return
    try {
      await api.setName(sessionId, name.trim())
      setUserName(name.trim())
      setMessages([buildGreeting(name.trim(), isUnlocked)])
      setScreen("chat")
    } catch {
      setError("Couldn't connect to Max right now. Please try again.")
    }
  }, [sessionId, isUnlocked])

  // ── Send a chat message ─────────────────────────────────────────────────────
  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || isTyping) return
    setError(null)

    // Add user message immediately (optimistic UI)
    const userMessage: Message = {
      id: uuidv4(),
      role: "user",
      content: text.trim(),
      timestamp: new Date(),
    }
    setMessages(prev => [...prev, userMessage])
    setIsTyping(true)

    try {
      const data = await api.sendMessage(sessionId, text.trim())

      if (data.blocked) {
        setTrialEnded(true)
        setIsTyping(false)
        return
      }

      // Add Max's response
      const maxMessage: Message = {
        id: uuidv4(),
        role: "max",
        content: data.answer ?? "",
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, maxMessage])

      // Update counters
      setQuestionCount(data.question_count ?? questionCount + 1)
      setQuestionsRemaining(data.questions_remaining ?? 0)

      if (data.trial_ended) {
        setTrialEnded(true)
      }
    } catch {
      // Remove optimistic user message on error
      setMessages(prev => prev.filter(m => m.id !== userMessage.id))
      setError("Something went wrong. Please try again.")
    } finally {
      setIsTyping(false)
    }
  }, [sessionId, isTyping, questionCount])

  // ── Verify access code ──────────────────────────────────────────────────────
  const submitCode = useCallback(async (code: string): Promise<{ success: boolean; message: string }> => {
    try {
      const data = await api.verifyCode(sessionId, code.toUpperCase())
      if (data.success) {
        setIsUnlocked(true)
        setTrialEnded(false)
        setQuestionsRemaining(999)
        setScreen("chat")
        setMessages(prev => [
          ...prev,
          {
            id: uuidv4(),
            role: "max",
            content: `🎉 You're all set, ${userName}! You now have unlimited access to Max. What would you like to explore next?`,
            timestamp: new Date(),
          },
        ])
      }
      return data
    } catch {
      return { success: false, message: "Connection error. Please try again." }
    }
  }, [sessionId, userName])

  // ── Verify purchase ─────────────────────────────────────────────────────────
  const submitPurchase = useCallback(async (
    firstName: string,
    email: string,
    orderNumber: string
  ): Promise<{ success: boolean; code: string; message: string }> => {
    try {
      return await api.verifyPurchase(sessionId, firstName, email, orderNumber)
    } catch {
      return { success: false, code: "", message: "Connection error. Please try again." }
    }
  }, [sessionId])

  // ── Navigation helpers ──────────────────────────────────────────────────────
  const goToUnlock = useCallback(() => setScreen("unlock"), [])
  const goToChat   = useCallback(() => setScreen("chat"),   [])

  return {
    // State
    screen,
    sessionId,
    userName,
    messages,
    isTyping,
    isUnlocked,
    questionCount,
    questionsRemaining,
    trialEnded,
    error,
    messagesEndRef,
    // Actions
    submitName,
    sendMessage,
    submitCode,
    submitPurchase,
    goToUnlock,
    goToChat,
  }
}