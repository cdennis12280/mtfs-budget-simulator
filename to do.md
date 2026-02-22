# To Do

- **Started Streamlit server (background):** terminal ID `b0d9df74-5d37-4844-868c-f60167de7b9e` — http://localhost:8501

- **Next (test commercial page flows):**
  - Upload a commercial projects CSV via the `Commercial` page uploader.
  - Verify the **Auto PWLB rate** displays and that the **Refresh PWLB Rate** button updates it.
  - Confirm per-project PWLB inputs default to the auto PWLB value.
  - Export the **portfolio RAG CSV** and open it to check `name`, `capital_cost`, `net_return_80pct`, `RAG`, and `RAG_reason` columns.

- **Commands:**

```bash
streamlit run app/main.py
```

- **Notes:**
  - Ensure `pip install -r requirements.txt` has been run (includes `requests` for PWLB helper).
  - PWLB fetch is best-effort; for production use, verify data source reliability.
