# Order Entry App

A Streamlit app that lets a user pick a customer and product, review and confirm an
order, save it to Supabase, and verify it by reading it back from the database.

**Live app:** https://assignment-app-6mpbjmb2nghreqwjs2sxmp.streamlit.app/

## Files
| File | Purpose |
|---|---|
| app.py | Streamlit interface |
| database.py | Supabase connection and database functions |
| requirements.txt | Packages needed to run the app |
| .gitignore | Keeps secrets and local files out of GitHub |
| .streamlit/secrets.toml.example | Placeholder settings (no real keys) |

## Run locally
1. `python -m venv .venv` then activate it
2. `pip install -r requirements.txt`
3. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and add your real values
4. `streamlit run app.py`

## Deploy
1. Push this repo to GitHub (without secrets).
2. On Streamlit Community Cloud choose **Create app**, pick the repo, branch, and `app.py`.
3. Under **Advanced settings > Secrets**, paste `SUPABASE_URL`, `SUPABASE_KEY`, and `APP_PASSWORD`.
4. Deploy. The password is shared with the instructor privately.

## Testing results (deployed app)
| Test | Result | Notes |
|---|---|---|
| Open the deployed app | Interface loads after authorized access | |
| View customers and products | Records are retrieved from Supabase | |
| Try an invalid quantity (0) | <img width="990" height="295" alt="image" src="https://github.com/user-attachments/assets/5ac88ef5-4c9e-4705-9735-6981c2841271" />
| |
| Submit without confirmation | <img width="1088" height="209" alt="image" src="https://github.com/user-attachments/assets/f528f253-df40-431b-b503-0c77612a7e04" />
| |
| Confirm and submit a valid order | <img width="1093" height="181" alt="image" src="https://github.com/user-attachments/assets/630561bc-3ef2-4e73-8652-38ddb63ba25c" />
| |
| View the verification table | Newly saved order is retrieved from Supabase | |
| Refresh / use another widget | Previously submitted order is not inserted again | |
| Refresh order history | Saved order remains visible | |

