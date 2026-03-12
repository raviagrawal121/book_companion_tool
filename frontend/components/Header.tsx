// components/Header.tsx
// Top bar of the widget — shows Max's name, status, and trial badge.

import clsx from "clsx"
import { ArrowLeft } from "lucide-react"
import type { Screen } from "@/types"

type Props = {
  screen:             Screen
  isUnlocked:         boolean
  questionsRemaining: number
  onBack?:            () => void
}

export default function Header({ screen, isUnlocked, questionsRemaining, onBack }: Props) {
  return (
    <div className="flex items-center gap-3 px-4 py-3 bg-navy flex-shrink-0">

      {/* Back button (only on unlock screen) */}
      {screen === "unlock" && onBack && (
        <button
          onClick={onBack}
          className="text-white/60 hover:text-white transition-colors mr-1"
          aria-label="Back to chat"
        >
          <ArrowLeft size={18} />
        </button>
      )}

      {/* Avatar */}
      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-teal-600 to-teal-400 flex items-center justify-center text-xl flex-shrink-0 ring-2 ring-teal-400/30">
        🤖
      </div>

      {/* Name + subtitle */}
      <div className="flex-1">
        <div className="text-white font-bold text-base leading-tight">
          Money Coach Max
        </div>
        <div className="text-teal-400 text-xs font-medium mt-0.5">
          Your personal finance guide
        </div>
      </div>

      {/* Trial badge */}
      {screen === "chat" && (
        <div
          className={clsx(
            "text-[10px] font-bold px-2.5 py-1 rounded-full border",
            isUnlocked
              ? "bg-teal-500/20 border-teal-400/40 text-teal-300"
              : "bg-yellow-400/15 border-yellow-400/40 text-yellow-300"
          )}
        >
          {isUnlocked
            ? "✓ Unlimited"
            : `${questionsRemaining} Q${questionsRemaining !== 1 ? "'s" : ""} left`
          }
        </div>
      )}
    </div>
  )
}