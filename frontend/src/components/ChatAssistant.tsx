import { useState, useRef, useEffect } from "react";
import { Send, Mic, X, Bot, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const ChatAssistant = ({ onClose }: { onClose?: () => void }) => {
  const [messages, setMessages] = useState<
    { role: "user" | "assistant"; content: string }[]
  >([
    {
      role: "assistant",
      content:
        "👋 Hello! I'm here to help you understand lung scans and health insights. How can I assist you today?",
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
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
          // send the full chat history for context!
          messages: newMessages,
          lang: navigator.language || "en",
        }),
      });

      const data = await res.json();
      const reply =
        data?.reply ||
        "⚠️ I'm having trouble reaching the AI service right now. Please try again.";

      setMessages([...newMessages, { role: "assistant", content: reply }]);
    } catch (error) {
      setMessages([
        ...messages,
        { role: "user", content: input }, // add the user's message, even if error
        {
          role: "assistant",
          content:
            "🚨 Network error while connecting to AI. Please try again later.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <Card className="fixed bottom-4 right-4 w-[380px] max-h-[75vh] flex flex-col shadow-2xl border-primary/30 z-50 animate-in slide-in-from-bottom">
      <CardHeader className="flex justify-between items-center bg-gradient-to-r from-blue-600 to-blue-400 text-white rounded-t-xl">
        <CardTitle className="text-lg flex items-center gap-2">
          <Bot className="h-5 w-5" /> Lung Cancer AI Assistant
        </CardTitle>
        <Button
          variant="ghost"
          size="icon"
          className="text-white hover:bg-blue-700"
          onClick={onClose}
        >
          <X className="h-4 w-4" />
        </Button>
      </CardHeader>

      <CardContent className="flex flex-col flex-1 overflow-y-auto p-3 bg-background">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex mb-3 ${
              msg.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`px-3 py-2 rounded-2xl max-w-[75%] text-sm shadow-sm ${
                msg.role === "user"
                  ? "bg-blue-600 text-white rounded-br-none"
                  : "bg-muted text-foreground rounded-bl-none"
              }`}
            >
              {msg.role === "user" ? (
                <div className="flex items-center gap-2">
                  <span>{msg.content}</span> <User className="h-3 w-3" />
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <Bot className="h-3 w-3" /> <span>{msg.content}</span>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center text-muted-foreground text-sm gap-2">
            <span className="animate-pulse">AI is typing...</span>
          </div>
        )}

        <div ref={chatEndRef} />
      </CardContent>

      <div className="flex p-3 border-t bg-muted/50 items-center gap-2">
        <Input
          placeholder="Ask me about lung health..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
          className="flex-1"
        />
        <Button
          onClick={sendMessage}
          disabled={loading}
          className="bg-blue-600 text-white"
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </Card>
  );
};

export default ChatAssistant;
