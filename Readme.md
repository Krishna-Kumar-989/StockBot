


## 📈 StockBot

****StockBot**** is a Streamlit-based financial advisor tailored for the Indian stock market. It focuses on analyzing individual Nifty 50 stocks by retrieving historical price and volume data, scraping recent news, and using LLM-powered analytics to generate actionable buy/hold/sell recommendations.

---

## 🚀 Features

- Single-stock analysis (Nifty 50 only)
- Fetches historical price and volume data via IndianAPI
- Scrapes recent news headlines using Google News RSS
- Analyzes news and data with Groq LLM (LLaMA 3.1 8B Instant) to provide:
  - Statistical summaries and trend detection
  - Sentiment and event impact analysis
  - Final buy/hold/sell recommendation with confidence score
- Simple, user-friendly Streamlit web interface

---

## 📦 Dependencies

All required packages are listed in the `requirements.txt` file.

---

## 🔧 Installation

1. ****Clone the repo****
   ```bash
   git clone https://github.com/Krishna-Kumar-989/StockBot.git
   cd StockBot

2. **Create & activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

3. ****Install Python dependencies****
   ```bash
   pip install -r requirements.txt
   ```

4. ****Set up environment variables****
   Create a `.env` file in the project root with:
   ```dotenv
   API_KEY=your_indianapi_key
   GROQKEY=your_groq_api_key
   ```

---

## ⚙️ Configuration

- ****`API_KEY`****: Your IndianAPI key for `https://stock.indianapi.in/indian-stock-market`
- ****`GROQKEY`****: Your API key for the Groq LLM service

---

## 🧩 Project Structure

```
.
├── main.py            # Streamlit app & state graph orchestration
├── utils.py           # fetch stock data & news scraper
├── consts.py          # constants (tickers list, filters)
├── classes.py         # AppState & custom classes
├── requirements.txt
└── .env               # (not committed) API keys
```

---

## 🚀 Usage

Run the Streamlit app:

```bash
streamlit run main.py
```

1. Open the URL shown in your browser.
2. Enter your query, e.g.:
   - “Should I buy TCS today?”
   - “What’s the outlook for Reliance?”
3. View:
   - 📊 Final report (price & news analysis)
   - 💬 Final answer with actionable advice

---

## 💡 Examples

```
Enter your financial query: Should I buy TCS today?
```

- ****Output****:
  - Final Report with trend summary, sentiment score, correlations
  - Final Answer: “Buy with confidence 7/10 because….”

---

## ⚠️ Limitations

- ****Single-ticker only**** (cannot handle multi-stock queries)
- ****Nifty 50 universe**** hard-coded in `consts.py`
- Relies on free RSS & IndianAPI — may be rate-limited
- Forecasts are LLM-based and not a substitute for professional advice

---




```
