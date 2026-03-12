// components/MessageBubble.tsx
// Renders a single chat message — either from the user or from Max.
// Role determines alignment, color, and avatar.

import clsx from "clsx"
import type { Message } from "@/types"

type Props = {
  message: Message
}

export default function MessageBubble({ message }: Props) {
  const isMax  = message.role === "max"
  const isUser = message.role === "user"

  return (
    <div
      className={clsx(
        "flex items-end gap-2 animate-fadeUp",
        isUser && "flex-row-reverse"
      )}
    >
      {/* Avatar */}
      <div
        className={clsx(
          "w-8 h-8 rounded-full flex items-center justify-center",
          "text-base flex-shrink-0",
          isMax  && "bg-gradient-to-br from-teal-600 to-teal-400",
          isUser && "bg-navy"
        )}
      >
        {isMax ? "🤖" : "👤"}
      </div>

      {/* Bubble */}
      <div
        className={clsx(
          "max-w-[78%] px-4 py-3 text-sm leading-relaxed rounded-2xl",
          isMax  && "bg-white text-navy rounded-bl-sm shadow-sm",
          isUser && "bg-navy text-white rounded-br-sm"
        )}
      >
        {/* Render newlines as line breaks */}
        {message.content.split("\n").map((line, i) => (
          <span key={i}>
            {line}
            {i < message.content.split("\n").length - 1 && <br />}
          </span>
        ))}
      </div>
    </div>
  )
}

// ── Typing indicator (shown while Max is thinking) ───────────────────────────

export function TypingIndicator() {
  return (
    <div className="flex items-end gap-2 animate-fadeUp">
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-teal-600 to-teal-400 flex items-center justify-center text-base flex-shrink-0">
        🤖
      </div>
      <div className="bg-white rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
        <div className="flex gap-1 items-center h-4">
          {[0, 1, 2].map(i => (
            <div
              key={i}
              className="w-2 h-2 rounded-full bg-teal-500 animate-bounce"
              style={{ animationDelay: `${i * 0.15}s` }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}