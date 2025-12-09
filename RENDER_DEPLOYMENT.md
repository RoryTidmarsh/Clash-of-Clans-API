# Deploying to Render

This guide provides step-by-step instructions for deploying the Clash of Clans API web application to Render.

## Prerequisites

Before you begin, ensure you have:
- ✅ A [Render](https://render.com) account (free tier available)
- ✅ A [Supabase](https://supabase.com) project with your war data
- ✅ Your Supabase URL and anon key (found in Supabase project settings)
- ✅ This repository pushed to GitHub

---

## Deployment Steps

### 1. Create a New Web Service on Render

1. **Log in to Render** at [https://dashboard.render.com](https://dashboard.render.com)

2. **Click "New +"** in the top right corner

3. **Select "Web Service"**

4. **Connect your GitHub repository**:
   - If this is your first time, authorize Render to access your GitHub account
   - Select your repository (e.g., `RoryTidmarsh/Clash-of-Clans-API` or your fork)
   - Click "Connect"

### 2. Configure the Web Service

Fill in the following settings:

#### Basic Settings
- **Name**: `clash-of-clans-api` (or your preferred name)
- **Region**: Choose the region closest to your users (e.g., `Oregon (US West)`)
- **Branch**: `main` (or your production branch)
- **Root Directory**: Leave empty (will use repository root)

#### Build & Deploy Settings
- **Runtime**: `Python 3`
- **Build Command**: 
  ```bash
  pip install -r webapp/requirements.txt
  ```
- **Start Command**: 
  ```bash
  gunicorn --bind 0.0.0.0:$PORT run:app
  ```

#### Instance Type
- **Free** (or select paid tier for better performance)

### 3. Configure Environment Variables

⚠️ **CRITICAL STEP**: This is where you add your Supabase credentials **without committing them to GitHub**.

1. **Scroll down to "Environment Variables"** section

2. **Click "Add Environment Variable"**

3. **Add the following environment variables**:

   | Key | Value | Description |
   |-----|-------|-------------|
   | `SUPABASE_URL` | `https://your-project-id.supabase.co` | Your Supabase project URL |
   | `SUPABASE_KEY` | `your-anon-key-here` | Your Supabase anon key (for read-only access) |
   | `FLASK_ENV` | `production` | Set Flask to production mode |
   | `PORT` | `10000` | Render's default port (auto-set) |

#### How to Find Your Supabase Credentials

1. Go to your [Supabase dashboard](https://app.supabase.com)
2. Select your project
3. Click on the **Settings** icon (gear icon) in the left sidebar
4. Navigate to **API** section
5. You'll find:
   - **Project URL** → Use this for `SUPABASE_URL`
   - **Project API keys** → Use the `anon` `public` key for `SUPABASE_KEY`

**Note**: For the web application, use the **anon key**, NOT the service role key. The anon key provides read-only access, which is all the webapp needs.

### 4. Deploy

1. **Review your settings** to ensure everything is correct

2. **Click "Create Web Service"**

3. Render will:
   - Clone your repository
   - Install dependencies from `webapp/requirements.txt`
   - Start your application using gunicorn
   - Assign a public URL (e.g., `https://clash-of-clans-api.onrender.com`)

4. **Monitor the deployment**:
   - Watch the logs in real-time to ensure the build succeeds
   - Look for "Build successful" and "Starting service..." messages

### 5. Verify Deployment

1. **Wait for deployment to complete** (usually 2-5 minutes)

2. **Click the URL** at the top of the page (e.g., `https://your-app-name.onrender.com`)

3. **Test the application**:
   - Homepage should load with player statistics
   - Navigate to "War Table" to see war data
   - Check "Progress Graphs" for visualizations
   - Ensure filters work properly

---

## Post-Deployment Configuration

### Custom Domain (Optional)

If you want to use a custom domain:

1. Go to your web service settings in Render
2. Navigate to the **Custom Domains** section
3. Click **Add Custom Domain**
4. Follow Render's instructions to configure DNS

### Automatic Deploys

By default, Render will automatically deploy when you push to your connected branch:
- ✅ Enabled by default
- ✅ Deploys on every push to `main` branch
- ⚙️ Can be disabled in service settings if needed

### Scaling (Paid Plans)

If you experience high traffic:
1. Upgrade to a paid instance type
2. Enable auto-scaling in service settings
3. Configure scaling rules based on CPU/memory usage

---

## Troubleshooting

### Build Fails

**Problem**: Build command fails with dependency errors

**Solution**: 
```bash
# Make sure you're using the correct requirements file
pip install -r webapp/requirements.txt
```

### Application Crashes on Start

**Problem**: "Application failed to start"

**Solution**: Check that:
1. Environment variables `SUPABASE_URL` and `SUPABASE_KEY` are set correctly
2. Start command is: `gunicorn --bind 0.0.0.0:$PORT run:app`
3. Gunicorn is listed in `webapp/requirements.txt`

### Database Connection Errors

**Problem**: "Failed to connect to Supabase"

**Solution**:
1. Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct
2. Ensure your Supabase project is active (not paused)
3. Check Supabase service status at [status.supabase.com](https://status.supabase.com)

### 502 Bad Gateway

**Problem**: Render shows 502 error

**Solution**:
1. Check application logs for errors
2. Ensure the app is listening on `0.0.0.0:$PORT`
3. Verify `run.py` is configured correctly

### Empty Data / No Statistics

**Problem**: Website loads but shows no data

**Solution**:
1. Verify data exists in your Supabase tables (`war_data`, `battle_tags`)
2. Check that the webapp has read permissions
3. Review application logs for Supabase query errors

---

## Security Best Practices

✅ **DO**:
- Use environment variables for all secrets
- Use the Supabase **anon key** for the webapp (read-only)
- Keep the service key on your Raspberry Pi only
- Enable HTTPS (provided by Render automatically)
- Regularly update dependencies

❌ **DON'T**:
- Commit `.env` files to GitHub
- Use the service key in the webapp
- Expose Clash of Clans API keys in the webapp
- Share your Render environment variables publicly

---

## Environment Variable Summary

Create a `.env.webapp` file locally for development (not committed):

```bash
# For local development only - DO NOT COMMIT
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
```

On Render, add these same variables through the dashboard (Environment Variables section).

---

## Maintenance

### Updating the Application

1. **Push changes to GitHub**:
   ```bash
   git add .
   git commit -m "Your update message"
   git push origin main
   ```

2. **Automatic deployment**: Render will automatically detect and deploy changes

3. **Manual deployment**: 
   - Go to your Render dashboard
   - Click "Manual Deploy" → "Deploy latest commit"

### Monitoring

- **Logs**: View real-time logs in Render dashboard
- **Metrics**: Check CPU, memory, and bandwidth usage
- **Health Checks**: Render automatically monitors application health

### Backup Strategy

- Your data is stored in Supabase (automatically backed up)
- Application code is in GitHub (version controlled)
- Environment variables are stored in Render (export if needed)

---

## Cost Estimates

### Free Tier Limitations
- ✅ 750 hours/month (enough for one service)
- ⚠️ Service may spin down after 15 minutes of inactivity
- ⚠️ Cold start time: 30-60 seconds
- ✅ Unlimited bandwidth

### Paid Tier Benefits
- ✅ No spin down / Always running
- ✅ Faster response times
- ✅ More memory and CPU
- ✅ Priority support

For a personal project like this, the **free tier is usually sufficient**.

**Note**: Pricing is subject to change. Check [Render's pricing page](https://render.com/pricing) for current rates.

---

## Support

If you encounter issues:
1. Check Render's [documentation](https://render.com/docs)
2. Review application logs in Render dashboard
3. Check Supabase [status page](https://status.supabase.com)
4. Post in Render's [community forum](https://community.render.com)

---

## Summary Checklist

Before going live, ensure:
- [ ] Repository is pushed to GitHub
- [ ] Render web service is created
- [ ] Build command: `pip install -r webapp/requirements.txt`
- [ ] Start command: `gunicorn --bind 0.0.0.0:$PORT run:app`
- [ ] Environment variables are set (SUPABASE_URL, SUPABASE_KEY)
- [ ] Application deployed successfully
- [ ] Website is accessible via Render URL
- [ ] Homepage loads with data
- [ ] War table displays correctly
- [ ] Graphs render properly
- [ ] Filters work as expected
- [ ] No errors in application logs

---

🎉 **Congratulations!** Your Clash of Clans API web application is now live on Render!