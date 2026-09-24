# 🤖 Multi-Agent Customer Support System (AutoGen v0.4)

An enterprise-ready, multi-agent customer support system built with **Streamlit** and **AutoGen v0.4 (`autogen-agentchat`)**. The application dynamically routes user queries to specialized support agents using a deterministic routing engine.

---

## 🌟 Key Features

* **Multi-Agent Specialist Architecture**:
  * 💳 **Billing_Agent**: Handles payments, refunds, subscription double charges, and invoices.
  * 🛠️ **TechSupport_Agent**: Handles platform crashes, 500 server errors, API debugging, and code issues.
  * 🔐 **Account_Agent**: Handles MFA/2FA resets, login issues, password recovery, and account security.
  * 📦 **Shipping_Agent**: Handles physical delivery costs, package tracking, and courier logistics.
  * ℹ️ **GeneralInfo_Agent**: Fallback specialist for AI news, company FAQs, and general queries.
* **Deterministic Selector Routing**: Uses custom AutoGen `selector_func` logic to eliminate LLM speaker selection retries ("Model failed to select a speaker after 3") and guarantee low-latency routing.
* **Modern Dark UI**: Features high-contrast dark themes with explicit specialist scope descriptions and a high-visibility white chat input box.
* **Isolated Turn Execution**: Guarantees independent evaluation per user request to prevent conversation context leakage across turns.

---

## 📁 Project Structure

```text
├── Customer_Support_System_Autogen.py   # Main Streamlit & AutoGen application
├── .env                                 # Environment file containing OPENAI_API_KEY
├── requirements.txt                     # Project dependencies
└── README.md                            # Documentation