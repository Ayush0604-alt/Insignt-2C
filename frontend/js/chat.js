document.addEventListener("DOMContentLoaded", () => {
    const chatWidget = document.getElementById("chatWidget");
    const openChatBtn = document.getElementById("openChatBtn");
    const closeChatBtn = document.getElementById("closeChatBtn");
    const chatMessages = document.getElementById("chatMessages");
    const chatInput = document.getElementById("chatInput");
    const sendChatBtn = document.getElementById("sendChatBtn");

    // Make toggle button visible if there is a dataset uploaded (state.filePath exists).
    // The state variable is from upload.js, but since it's in the global scope we can use a polling or event mechanism,
    // or simply hook into the uploadDataset completion. Let's just poll for state.filePath.
    setInterval(() => {
        // 'state' is defined in upload.js globally, not on window object since it uses const
        if (typeof state !== "undefined" && state.filePath && chatWidget.classList.contains("hidden") && openChatBtn.classList.contains("hidden")) {
            openChatBtn.classList.remove("hidden");
        }
    }, 1000);

    openChatBtn.addEventListener("click", () => {
        chatWidget.classList.remove("hidden");
        openChatBtn.classList.add("hidden");
        chatInput.focus();
    });

    closeChatBtn.addEventListener("click", () => {
        chatWidget.classList.add("hidden");
        openChatBtn.classList.remove("hidden");
    });

    const addMessage = (text, sender) => {
        const msgDiv = document.createElement("div");
        msgDiv.className = `chat-message ${sender}`;
        msgDiv.textContent = text;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    const sendMessage = async () => {
        const text = chatInput.value.trim();
        if (!text) return;

        if (typeof state === "undefined" || !state.filePath) {
            addMessage("Please upload a dataset first.", "bot");
            return;
        }

        addMessage(text, "user");
        chatInput.value = "";
        chatInput.disabled = true;
        sendChatBtn.disabled = true;

        const loadingMsg = document.createElement("div");
        loadingMsg.className = "chat-message bot";
        loadingMsg.textContent = "Thinking...";
        loadingMsg.id = "chatLoading";
        chatMessages.appendChild(loadingMsg);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const res = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    filePath: state.filePath,
                    query: text
                })
            });

            const data = await res.json();
            document.getElementById("chatLoading")?.remove();
            
            if (res.ok) {
                addMessage(data.reply || "No reply from agent.", "bot");
            } else {
                addMessage(`Error: ${data.message}`, "bot");
            }
        } catch (err) {
            document.getElementById("chatLoading")?.remove();
            addMessage(`Failed to connect to Chat API: ${err.message}`, "bot");
        } finally {
            chatInput.disabled = false;
            sendChatBtn.disabled = false;
            chatInput.focus();
        }
    };

    sendChatBtn.addEventListener("click", sendMessage);
    chatInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            sendMessage();
        }
    });
});
