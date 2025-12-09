# Quick Reference: Render Deployment Setup

This is a condensed reference for deploying the Clash of Clans API webapp to Render. For complete instructions, see [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md).

## Pre-Deployment Checklist

Before deploying to Render, ensure you have:
- [ ] A [Render](https://render.com) account
- [ ] A [Supabase](https://supabase.com) project with war data
- [ ] Your Supabase URL and **anon key** (NOT service key)
- [ ] This repository pushed to GitHub

## Render Configuration (Copy-Paste Ready)

### Service Settings
- **Name**: `clash-of-clans-api` (or your choice)
- **Runtime**: Python 3
- **Branch**: `main`
- **Root Directory**: (leave empty)

### Build & Deploy
- **Build Command**: 
  ```bash
  pip install -r webapp/requirements.txt
  ```
- **Start Command**: 
  ```bash
  gunicorn --bind 0.0.0.0:$PORT run:app
  ```

## Environment Variables (.env.webapp)

⚠️ **CRITICAL**: Add these in Render's dashboard, NOT in GitHub

| Variable | Value | Where to Find |
|----------|-------|---------------|
| `SUPABASE_URL` | `https://xxxxx.supabase.co` | Supabase → Settings → API → Project URL |
| `SUPABASE_KEY` | `eyJhbGc...` | Supabase → Settings → API → Project API keys → `anon` `public` |
| `FLASK_ENV` | `production` | Set manually |

### Finding Your Supabase Credentials

1. Go to [https://app.supabase.com](https://app.supabase.com)
2. Select your project
3. Click **Settings** (gear icon) → **API**
4. Copy:
   - **Project URL** → Use for `SUPABASE_URL`
   - **anon public** key → Use for `SUPABASE_KEY`

⚠️ **Important**: Use the **anon (public)** key, NOT the service_role key!

## Post-Deployment

After deployment:
1. Wait 2-5 minutes for build to complete
2. Visit your Render URL (e.g., `https://your-app.onrender.com`)
3. Test homepage, war table, and graphs
4. Verify data loads correctly

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| Build fails | Check build command uses `webapp/requirements.txt` |
| App won't start | Verify environment variables are set correctly |
| No data showing | Confirm Supabase credentials and data exists in tables |
| 502 error | Check logs for errors, verify start command is correct |

## Key Security Points

✅ **DO**:
- Use environment variables in Render (never commit to GitHub)
- Use the Supabase **anon key** for the webapp
- Keep the **service key** only on your Raspberry Pi

❌ **DON'T**:
- Commit any `.env` files
- Use the service key in the webapp
- Include CoC API keys in the webapp

## Quick Deploy Steps

1. **Render**: New → Web Service → Connect GitHub repo
2. **Configure**: Set build/start commands (see above)
3. **Environment**: Add `SUPABASE_URL` and `SUPABASE_KEY`
4. **Deploy**: Click "Create Web Service"
5. **Verify**: Test your deployment URL

## Need More Details?

See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for:
- Step-by-step screenshots guidance
- Detailed troubleshooting
- Scaling and monitoring tips
- Security best practices
- Cost information

## Support

- Render Docs: [render.com/docs](https://render.com/docs)
- Supabase Docs: [supabase.com/docs](https://supabase.com/docs)
- Issues: Check GitHub repository issues
