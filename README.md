# Order Entry App (DATA 4000)

A Streamlit app that lets a user pick a customer and product, review and confirm an
order, save it to Supabase, and verify it by reading it back from the database.

**Live app:** PASTE YOUR STREAMLIT COMMUNITY CLOUD LINK HERE
**GitHub repo:** PASTE YOUR REPO LINK HERE

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
| Open the deployed app | | |
| View customers and products | | |
| Try an invalid quantity (0) | | |
| Submit without confirmation | | |
| Confirm and submit a valid order | | |
| View the verification table | | |
| Refresh / use another widget | | |
| Refresh order history | | |

Screenshots (no credentials shown): add images to a `screenshots/` folder and link them here.
- Order entry interface: 
- Successfully verified order: 
