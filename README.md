\# Three Vibe Gallery / そのイチギャラリー



「その一枚、私達にも見せてもらえませんか？」



`Three Vibe Gallery` は、評価アプリ `Three Vibe Impression` / `そのイチ印象値` で保存された作品のうち、Supabase の `image\_evaluations` テーブルで `is\_public = true` になっている作品だけを表示する Streamlit 製の画廊 MVP です。



評価アプリ本体には触れず、公開作品を誰でも無料で閲覧できる別アプリとして運用する前提です。



\## Files



\- `app.py`: Streamlit アプリ本体

\- `requirements.txt`: Python 依存関係

\- `.streamlit/secrets.toml.example`: Streamlit secrets の例



\## Setup



```powershell

pip install -r requirements.txt

Copy-Item .streamlit/secrets.toml.example .streamlit/secrets.toml

streamlit run app.py

```



`.streamlit/secrets.toml` に Supabase の URL と anon key を設定してください。



```toml

SUPABASE\_URL = "https://YOUR\_PROJECT\_ID.supabase.co"

SUPABASE\_ANON\_KEY = "YOUR\_SUPABASE\_ANON\_KEY"

```



\## Supabase Assumptions



\- Table: `image\_evaluations`

\- Storage bucket: `evaluation-images`

\- Public gallery condition: `is\_public = true`

\- The app only uses the anon key. Do not put a service role key in Streamlit secrets.



If the bucket is private, either make gallery images public through Storage policy or add a server-side signed URL flow with an appropriate policy.



