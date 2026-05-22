# 🛡️ Sentinel AI — AI Prompt Security Gateway

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
  <img src="https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB" />
  <img src="https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white" alt="Vite" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS" />
</p>

### Scan, detect, and neutralize prompt threats in real-time before they reach your LLMs (ChatGPT, Claude, Gemini).

Sentinel AI is a high-performance, enterprise-grade **Prompt Firewall & Threat Detection Gateway**. It acts as a security middleware sitting between your users and your Large Language Models (LLMs), identifying prompt injection, jailbreaks, data leakage, and system manipulation within milliseconds.


## 🌟 Key Features

* **8-Layer Hybrid Threat Detection Engine**: Scans prompts using high-speed deterministic heuristics and pattern matching.
* **AI-Augmented Cloud Moderation**: Optionally connects with OpenAI Moderation API or Google Gemini Safety Filters with automatic local fallback.
* **Multi-Signal Consensus & Boosting**: Smart confidence-level adjustment if both heuristic filters and AI analysis flag the same threat.
* **Intelligent Risk Scoring**: Computes a dynamic risk score from 0-100 to classify prompt safety (LOW, MEDIUM, HIGH, CRITICAL).
* **Automatic Prompt Sanitizer**: Automatically strips matching threat segments and replaces them with clean `[SUSPICIOUS CONTENT REMOVED]` markers.
* **Interactive Analytics Dashboard**: Beautiful real-time telemetry charts tracking scan history, threat distributions, and attack rates.


## 🏗️ System Architecture & Request Flow

The diagram below details the end-to-end telemetry pathway when a client application submits a prompt for scanning:

```mermaid
sequenceDiagram
    participant User as 👤 Client / Browser
    participant Gateway as 🛡️ Sentinel API (FastAPI)
    participant Engine as ⚙️ Detection Engine
    participant DB as 🍃 MongoDB (Database)
    participant LLM as 🤖 Target LLM (ChatGPT/Gemini)

    User->>Gateway: Submit Prompt (POST /api/v1/scan)
    Gateway->>Gateway: Verify JWT Session & Rate Limits
    Gateway->>Engine: Run engine.analyze(prompt)
    
    par Run Heuristics in Parallel
        Engine->>Engine: Heuristics 1-8 (Injection, Leakage, SQL, Toxicity, etc.)
    and Run AI Verification
        Engine->>Engine: Fetch AI Moderation (Local / OpenAI / Gemini)
    end

    Engine->>Engine: Apply Consensus Confidence Boosting
    Engine->>Engine: Calculate Risk Score (0-100) & Severity
    Engine->>Engine: Sanitize threat segments
    Engine->>Gateway: Return Structured Threat Result

    Gateway->>DB: Save Scan Record & Daily Analytics Increments
    Gateway->>DB: Increment User Stats (Total Scans / Blocked Alerts)
    
    alt Prompt is SAFE
        Gateway-->>User: Return clean prompt + metadata
        User->>LLM: Forward clean prompt with confidence
    else Prompt is DANGEROUS
        Gateway-->>User: Return Blocked warning + Sanitized prompt + Explanations
    end
```
