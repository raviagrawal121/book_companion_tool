// components/ChatWidget.tsx
// The main chat interface — message list, input area, trial banner.
// Receives everything it needs as props from the parent.

"use client"

import { useState, KeyboardEvent, useRef, useEffect } from "react"
import { Send } from "lucide-react"
import clsx from "clsx"
import MessageBubble, { TypingIndicator } from "@/components/MessageBubble"
import TrialBanner from "@/components/TrialBanner"
import type { Message } from "@/types"

type Props = {
  messages:           Message[]
  isTyping:           boolean
  isUnlocked:         boolean
  questionsRemaining: number
  trialEnded:         boolean
  error:              string | null
  messagesEndRef:     React.RefObject<HTMLDivElement>
  onSend:             (text: string) => void
  onUnlock:           () => void
}

export default function ChatWidget({
  messages,
  isTyping,
  isUnlocked,
  questionsRemaining,
  trialEnded,
  error,
  messagesEndRef,
  onSend,
  onUnlock,
}: Props) {
  const [input, setInput] = useState("")
  const textareaRef       = useRef<HTMLTextAreaElement>(null)

  // Disable input when trial has ended
  const inputDisabled = isTyping || (trialEnded && !isUnlocked)

  const handleSend = () => {
    if (!input.trim() || inputDisabled) return
    onSend(input.trim())
    setInput("")
    // Reset textarea height
    if (textareaRef.current) textareaRef.current.style.height = "auto"
  }

  const handleKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // Auto-resize textarea as user types
  const handleInput = () => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = "auto"
    el.style.height = `${Math.min(el.scrollHeight, 80)}px`
  }

  return (
    <>
      {/* ── Message list ─────────────────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3 bg-cream">
        {messages.map(msg => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {isTyping && <TypingIndicator />}

        {/* Error inline */}
        {error && (
          <div className="text-center text-xs text-red-400 py-1 animate-fadeUp">
            {error}
          </div>
        )}

        {/* Scroll anchor */}
        <div ref={messagesEndRef} />
      </div>

      {/* ── Trial banner ─────────────────────────────────────────────────── */}
      {trialEnded && !isUnlocked && (
        <TrialBanner onUnlock={onUnlock} />
      )}

      {/* ── Input area ───────────────────────────────────────────────────── */}
      <div className="flex items-end gap-2 px-3 py-3 bg-white border-t border-gray-100">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={e => { setInput(e.target.value); handleInput() }}
          onKeyDown={handleKey}
          placeholder={
            inputDisabled && !isTyping
              ? "Enter a code to continue…"
              : "Ask Max anything about money…"
          }
          disabled={inputDisabled}
          rows={1}
          className={clsx(
            "flex-1 resize-none px-4 py-2.5 text-sm rounded-2xl border-2",
            "bg-cream text-navy placeholder-gray-300 outline-none",
            "transition-colors leading-relaxed max-h-20",
            "focus:border-teal-500",
            inputDisabled
              ? "border-gray-100 opacity-50 cursor-not-allowed"
              : "border-gray-200"
          )}
        />

        <button
          onClick={handleSend}
          disabled={inputDisabled || !input.trim()}
          className={clsx(
            "w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0",
            "bg-gradient-to-br from-teal-600 to-teal-400 text-white",
            "hover:opacity-90 active:scale-90 transition-all",
            "disabled:opacity-40 disabled:cursor-not-allowed"
          )}
        >
          <Send size={15} />
        </button>
      </div>
    </>
  )
}