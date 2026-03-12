// components/TrialBanner.tsx
// Shown after the user exhausts their 3 free questions.
// Two CTA buttons: buy the book or enter an access code.

import { BookOpen, KeyRound } from "lucide-react"

type Props = {
  onUnlock: () => void
}

export default function TrialBanner({ onUnlock }: Props) {
  return (
    <div className="mx-3 mb-3 rounded-2xl border border-yellow-200 bg-gradient-to-br from-yellow-50 to-white p-4 animate-fadeUp">

      {/* Title */}
      <p className="font-bold text-navy text-sm mb-1">
        🎉 You&apos;ve used your 3 free questions!
      </p>
      <p className="text-gray-500 text-xs mb-4 leading-relaxed">
        Unlock unlimited access to Max by getting the book.
      </p>

      {/* CTA buttons */}
      <div className="flex gap-2">
        <a
          href="https://amazon.com"
          target="_blank"
          rel="noopener noreferrer"
          className="flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-xl bg-yellow-400 text-navy text-xs font-bold hover:bg-yellow-300 transition-colors"
        >
          <BookOpen size={13} />
          Buy the Book
        </a>

        <button
          onClick={onUnlock}
          className="flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-xl bg-navy text-white text-xs font-semibold hover:opacity-85 transition-opacity"
        >
          <KeyRound size={13} />
          I Have a Code
        </button>
      </div>
    </div>
  )
}