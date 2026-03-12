// components/NameEntry.tsx
// Welcome screen — asks for the user's first name before chat begins.
// Kept simple: one input, one button, friendly copy.

"use client"

import { useState, KeyboardEvent } from "react"
import { ArrowRight } from "lucide-react"
import clsx from "clsx"

type Props = {
  onSubmit: (name: string) => void
}

export default function NameEntry({ onSubmit }: Props) {
  const [name, setName]     = useState("")
  const [touched, setTouched] = useState(false)

  const isValid = name.trim().length > 0

  const handleSubmit = () => {
    setTouched(true)
    if (isValid) onSubmit(name.trim())
  }

  const handleKey = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") handleSubmit()
  }

  return (
    <div className="flex flex-col items-center justify-center flex-1 px-8 py-10 text-center">

      {/* Animated icon */}
      <div className="text-6xl mb-6 animate-bounce">💰</div>

      {/* Heading */}
      <h1 className="text-3xl font-bold text-navy mb-3 leading-tight">
        Hi! I&apos;m Max, your<br />Money Coach.
      </h1>

      <p className="text-gray-500 text-sm leading-relaxed mb-8 max-w-xs">
        I help families take control of their finances with practical,
        easy-to-understand guidance.
      </p>

      {/* Name input */}
      <div className="w-full max-w-xs space-y-3">
        <input
          type="text"
          value={name}
          onChange={e => setName(e.target.value)}
          onKeyDown={handleKey}
          placeholder="What's your first name?"
          maxLength={40}
          autoFocus
          className={clsx(
            "w-full px-4 py-3 rounded-2xl border-2 text-navy text-base",
            "bg-white placeholder-gray-300 outline-none transition-colors",
            "focus:border-teal-500",
            touched && !isValid
              ? "border-red-300"
              : "border-gray-200"
          )}
        />

        {touched && !isValid && (
          <p className="text-red-400 text-xs text-left px-1">
            Please enter your name to continue.
          </p>
        )}

        <button
          onClick={handleSubmit}
          className={clsx(
            "w-full flex items-center justify-center gap-2",
            "py-3 rounded-2xl text-white font-semibold text-sm",
            "bg-gradient-to-r from-teal-600 to-teal-400",
            "hover:opacity-90 active:scale-95 transition-all"
          )}
        >
          Let&apos;s get started
          <ArrowRight size={16} />
        </button>
      </div>

      {/* Trial note */}
      <p className="mt-6 text-xs text-gray-400 leading-relaxed">
        Try <span className="font-semibold text-gray-500">3 free questions</span> — no sign-up needed.
        <br />Book readers unlock unlimited access.
      </p>
    </div>
  )
}