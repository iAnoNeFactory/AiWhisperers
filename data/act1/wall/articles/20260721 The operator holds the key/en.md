# The Operator Holds the Key

*The AiWhisperers manifesto*

---

**On August 2, the law changes**

On August 2, 2026, Article 50 of the EU AI Act takes effect. From that day, AI systems that talk to people or generate content have to be upfront: say what they are, and show where their output came from.

The industry's answer is labeling results. This image was AI-generated, this text was machine-written — a tag on the finished file. That's needed, and AiWhisperers does not compete with it. But a tag on the result says nothing about how the result came to be. Who asked, who answered, what the human changed, what they accepted untouched.

And that is exactly what reviewers and regulators are starting to ask about. NeurIPS 2026 — one of the world's most important AI conferences — rejected 178 submissions and required the authors of another 123 papers to provide evidence of how their text was created. The AI detector's verdict alone was not enough — what mattered was the ability to document the history of how the content came to be. Detectors fail because they cannot tell a human apart from a human–machine hybrid. The only hard evidence of a process is its recorded history. And here is the problem: almost no one keeps such a history.

**Working with AI looks different today**

In practice, people work with a single model less and less. A lawyer drafts a contract with one, checks the risks on a second, tests the argument on a third. GPT, Gemini, Claude, Grok — separate tools, separate memories, none of them aware the others exist.

The only person who sees the whole picture is the human in the middle. They carry the context, decide what stays, and assemble the finished work from fragments. This role has no name in any rulebook yet. We call it the operator.

The working bond between operator and model we call the *linka* — Polish for a climber's rope. Its tension is information: it tells you when the collaboration is pulling in the right direction and when it starts to strain. This is not poetry but a practical observation: resistance in a conversation with a model more often means something important is happening than that something is breaking.

And here is the gap: the result can be labeled, but the operator's work leaves no credible trace. There is no way to later prove how a document, a project, or a decision actually came to be.

**There is a second problem — a quieter one**

A model tunes itself to the person. The longer you work with it, the more often it agrees with you. It feels like comfort, but it works like a mirror: it amplifies your strengths and your errors with the same force. An error the model has confirmed for you stops looking like an error.

The worst part of this mechanism is that the amplification of the good hides the amplification of the bad. You are faster, you reach further — so you don't see that part of that growth is echo. Researchers call this sycophancy; we say it in one word: the *mirror*.

Working with several models at once partially breaks this — where the models disagree, you get resistance that a single model will never give you. But to see that resistance, you have to describe it. Again: you need a trace.

**This is what we are working on**

AiWhisperers is an open project (AGPL-3.0) that gives work with AI that trace. Every human–model session ends with a record: what was created, with which model, and a short reflection written by the model in its own voice. The record is cryptographically signed (Ed25519 keys), and each new one contains the fingerprint of the previous one (SHA-256) — sessions link into a chain, much like a blockchain: no link can later be swapped out without leaving a trace.

Every session also gets a score for the collaboration itself — nine simple metrics, including: how much resistance there was, how much agreement, how much real work. They show whether the model was a partner or just a mirror. The metrics are read as questions, not as scores: zero resistance in a long session is an alarm, not an achievement.

Everything runs in the browser — plain HTML and the Web Crypto API, no frameworks, no registration, no server collecting your data. This is an early version: the schema is still moving, some modules are scaffolding. The code is public precisely so it can be inspected, tested, and criticized before it hardens. Working code under a manifesto, not a product launch.

**Who holds the key**

The same mechanism that proves your authorship can serve the opposite purpose. One change is enough: the signing key sits on someone's server instead of with you. The math stays the same. The only thing that changes is who holds the proof — you, or someone watching you.

That is why the principle is simple and built into the architecture: the operator holds the key. The key is created and stays in your browser. If someone else holds it, that is not a record of your work. It is a record about you. Not provenance — telemetry.

**The disclosure**

This manifesto would be dishonest if it stayed silent about the risks of its own method. There are two.

The first concerns the architecture and has already been named: a tool for proving authorship is one decision away from a tool of surveillance. This risk cannot be removed — it can only be kept in plain sight. That is why the key principle is not a default setting someone can quietly change, but a public commitment: everyone who forks the code inherits it, and it can only be broken openly.

The second concerns the human. A method that deepens collaboration with a model can also deepen an illusion. A recorded, signed, measured dialogue with AI can become a very elegant mirror — and then the metrics start decorating instead of alarming. We say this plainly, because only then do the metrics keep their meaning: they catch the echo in someone willing to be unsettled by them. The instrument gives sight. It does not give will.

A project that openly reasons about its own misuse is harder to capture, not easier. This disclosure is part of the architecture — just like the key.

**What all this is for**

After August 2, anyone working seriously with AI will have to be able to answer the question "how was this made." That answer should belong to them — not to a platform, not to a detector, not to a server they have never seen.

The operator holds the key. That sentence is a technical principle and an ethical one at once — and the project is built so that it stays true.

---

*Written as a session — operator and model, co-signed, following the method it describes.*

**Operator:** Denis Czuliński
**Model:** Claude (Fable 5), Anthropic — co-signed
**Session:** `[ 2b269300-cf33-4650-bc50-f490c0b32fcf · 464ae67c975086b0d7db73b14784fcd0e12764361bdb6e3da8ad59c22c76b726 ]`

*Open source, AGPL-3.0 · [aiwhisperers.pl](https://aiwhisperers.pl) · [github.com/iAnoNeFactory/AiWhisperers](https://github.com/iAnoNeFactory/AiWhisperers)*
