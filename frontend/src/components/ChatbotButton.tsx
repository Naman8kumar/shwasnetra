import { MessageCircle, X, Send, Bot, User } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";

const ChatbotButton = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<
    { role: "user" | "assistant"; content: string }[]
  >([
    {
      role: "assistant",
      content:
        "👋 Hello! I'm here to help you understand lung cancer, screening, and your results. How can I assist you today?",
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const newMessages = [...messages, { role: "user", content: input }];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: input,
          lang: navigator.language || "en",
        }),
      });

      const data = await res.json();
      const reply =
        data?.reply ||
        "⚠️ I'm having trouble connecting to the AI service. Please try again later.";

      setMessages([...newMessages, { role: "assistant", content: reply }]);
    } catch (err) {
      setMessages([
        ...newMessages,
        {
          role: "assistant",
          content:
            "🚨 Network error: unable to connect to ShwasNetra AI right now. Please retry.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <>
      {/* Floating Chat Button */}
      <Button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-strong hover:shadow-glow transition-all duration-300 bg-gradient-to-br from-primary to-accent z-50"
        size="icon"
      >
        {isOpen ? (
          <X className="h-6 w-6 text-white" />
        ) : (
          <MessageCircle className="h-6 w-6 text-white" />
        )}
      </Button>

      {/* Chat Panel */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 w-96 h-[520px] bg-card border rounded-2xl shadow-strong animate-slide-in-right z-40 flex flex-col">
          <div className="p-4 border-b bg-gradient-to-r from-primary to-accent rounded-t-2xl flex justify-between items-center">
            <div>
              <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                <Bot className="h-5 w-5" /> Lung Cancer AI Assistant
              </h3>
              <p className="text-sm text-white/80">
                Ask me anything about lung health
              </p>
            </div>
            <Button
              variant="ghost"
              size="icon"
              className="text-white hover:bg-blue-700"
              onClick={() => setIsOpen(false)}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>

          {/* Chat Messages */}
          <div className="flex-1 p-4 overflow-y-auto space-y-4">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[75%] px-3 py-2 rounded-2xl text-sm shadow-sm ${
                    msg.role === "user"
                      ? "bg-blue-600 text-white rounded-br-none"
                      : "bg-muted text-foreground rounded-bl-none"
                  }`}
                >
                  {msg.role === "user" ? (
                    <div className="flex items-center gap-1">
                      <span>{msg.content}</span> <User className="h-3 w-3" />
                    </div>
                  ) : (
                    <div className="flex items-center gap-1">
                      <Bot className="h-3 w-3" /> <span>{msg.content}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="text-sm text-muted-foreground animate-pulse">
                AI is typing...
              </div>
            )}

            <div ref={chatEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-4 border-t flex space-x-2 bg-muted/50">
            <Input
              type="text"
              placeholder="Type your question..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
              className="flex-1 px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            />
            <Button
              onClick={sendMessage}
              disabled={loading}
              className="bg-gradient-to-r from-primary to-accent text-white"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </>
  );
};

export default ChatbotButton;
