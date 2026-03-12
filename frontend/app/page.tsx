// app/page.tsx
// Root page — wires the hook to all components.
// This component owns NO state — it just connects useChat() to UI.

"use client"

import { useChat } from "@/hooks/useChat"
import Header       from "@/components/Header"
import NameEntry    from "@/components/NameEntry"
import ChatWidget   from "@/components/ChatWidget"
import UnlockScreen from "@/components/UnlockScreen"

export default function Home() {
  const chat = useChat()

  return (
    <main className="min-h-screen bg-cream flex items-center justify-center p-4">
      <div className="w-full max-w-sm bg-white rounded-3xl shadow-2xl overflow-hidden flex flex-col h-[680px]">

        {/* Header — always visible */}
        <Header
          screen={chat.screen}
          isUnlocked={chat.isUnlocked}
          questionsRemaining={chat.questionsRemaining}
          onBack={chat.goToChat}
        />

        {/* Screen 1 — Name entry */}
        {chat.screen === "name" && (
          <NameEntry onSubmit={chat.submitName} />
        )}

        {/* Screen 2 — Chat */}
        {chat.screen === "chat" && (
          <ChatWidget
            messages={chat.messages}
            isTyping={chat.isTyping}
            isUnlocked={chat.isUnlocked}
            questionsRemaining={chat.questionsRemaining}
            trialEnded={chat.trialEnded}
            error={chat.error}
            messagesEndRef={chat.messagesEndRef}
            onSend={chat.sendMessage}
            onUnlock={chat.goToUnlock}
          />
        )}

        {/* Screen 3 — Unlock */}
        {chat.screen === "unlock" && (
          <UnlockScreen
            onCodeSubmit={chat.submitCode}
            onPurchaseSubmit={chat.submitPurchase}
          />
        )}

      </div>
    </main>
  )
}