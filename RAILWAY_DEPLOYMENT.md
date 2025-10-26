# Railway.app Deployment Guide

Complete guide to deploy both the Python scraper and WordPress site on Railway.

## 🚀 Overview

We'll create two separate Railway services:
1. **Python Scraper Service** - Runs the automated property scraper
2. **WordPress Site** - Hosts your website with the property plugin

## 📋 Prerequisites

- Railway.app account
- GitHub account (for continuous deployment)
- Domain name (optional, Railway provides subdomains)

## 🔧 Step 1: Deploy Python Scraper Service

### 1.1 Prepare Your Repository

```bash
# In your project directory
git init
git add .
git commit -m "Initial commit: AppFolio scraper and WordPress plugin"
git branch -M main
```

### 1.2 Push to GitHub

```bash
# Create a new repository on GitHub, then:
git remote add origin https://github.com/yourusername/appfolio-integration.git
git push -u origin main
```

### 1.3 Create Railway Service for Scraper

1. Go to [Railway.app](https://railway.app)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository
5. Railway will detect it's a Python project

### 1.4 Configure Scraper Service

1. **Configure Build and Deploy**:
   - Go to Settings → Build
   - **IMPORTANT**: Leave "Custom Build Command" EMPTY (or use default)
   - Railway will automatically use the Dockerfile for building
   
2. **Set the start command**:
   - Go to Settings → Deploy
   - Set Custom Start Command: `python scheduler.py`
   - Or leave it empty to use the Dockerfile CMD directive

3. **Add environment variables**:
   - Go to Variables tab
   - Add these variables:
     ```
     WP_URL=https://your-wordpress-site.up.railway.app
     WP_USERNAME=admin
     WP_PASSWORD=your-secure-password
     SCRAPE_INTERVAL_HOURS=4
     MAX_PROPERTIES=100
     ```

3. **Deploy**:
   - Click "Deploy"
   - Railway will install dependencies and start the scraper

### 1.5 Verify Scraper Service

- Check the Logs tab to see scraper activity
- Wait a few minutes for the first scrape to complete
- You should see "Successfully scraped X properties" in the logs

## 🌐 Step 2: Deploy WordPress Site

### 2.1 Optimize WordPress Plugin for Production

Update the plugin to read from JSON files created by the scraper:

```php
// Add this to wordpress-plugin.php before the ajax_get_properties function
public function get_properties_from_json() {
    $json_file = '/app/appfolio_properties.json'; // Adjust path as needed
    if (file_exists($json_file)) {
        $properties = json_decode(file_get_contents($json_file), true);
        return $properties ?: [];
    }
    return [];
}
```

### 2.2 Create WordPress Template for Railway

Create `wordpress-dockerfile`:

```dockerfile
FROM wordpress:latest

# Copy our custom plugin
COPY wordpress-plugin.php /var/www/html/wp-content/plugins/appfolio-properties/
COPY assets/ /var/www/html/wp-content/plugins/appfolio-properties/assets/

# Set permissions
RUN chown -R www-data:www-data /var/www/html/wp-content/plugins/appfolio-properties/

# Enable the plugin
RUN wp plugin activate appfolio-properties --allow-root || true
```

### 2.3 Deploy WordPress on Railway

**Option A: Use Railway's WordPress Template**

1. In Railway, click **"New Project"**
2. Select **"WordPress"** template
3. Follow the setup wizard
4. Get your WordPress URL

**Option B: Use Custom Dockerfile**

1. Create a new service in Railway
2. Select **"Private repo"** or upload files
3. Add Dockerfile and configure

### 2.4 Configure WordPress Database

Railway WordPress template automatically sets up MySQL database. Make note of:
- Database URL
- Database credentials
- WordPress admin credentials

### 2.5 Install Plugin

1. Access WordPress admin: `https://your-site.up.railway.app/wp-admin`
2. Go to **Plugins** → **Add New** → **Upload Plugin**
3. Upload `wordpress-plugin.php` and `assets/` folder
4. Activate the plugin

### 2.6 Add Property Shortcode

1. Go to **Pages** → **Add New**
2. Add the shortcode: `[appfolio_properties]`
3. Publish the page
4. View the page to see properties

## 🔗 Step 3: Connect Scraper to WordPress

### 3.1 Update Scraper to Write JSON

Update `import_to_wordpress.py` to save JSON that WordPress can read:

```python
def save_json_for_wordpress(properties, filename='appfolio_properties.json'):
    """Save properties in WordPress-compatible format"""
    wp_properties = []
    for prop in properties:
        wp_properties.append({
            'id': len(wp_properties) + 1,
            'title': prop.get('title', ''),
            'content': prop.get('description', ''),
            'price': prop.get('price', ''),
            'address': prop.get('address', ''),
            'bedrooms': prop.get('bedrooms', ''),
            'bathrooms': prop.get('bathrooms', ''),
            'square_feet': prop.get('square_feet', ''),
            'original_url': prop.get('url', ''),
            'images': prop.get('images', [])
        })
    
    import json
    with open(filename, 'w') as f:
        json.dump(wp_properties, f, indent=2)
```

### 3.2 Set Up Shared Storage (Optional)

For better integration, use Railway volumes:

1. Go to Scraper service → Settings → Volumes
2. Create a volume: `/app/data`
3. Mount it to WordPress service
4. Store JSON file in the shared volume

## 📊 Step 4: Monitor and Maintain

### 4.1 Check Scraper Logs

```bash
# In Railway, go to Scraper service → Logs
# You should see:
# - "Starting AppFolio property scraping..."
# - "Successfully scraped X properties"
# - Any errors or warnings
```

### 4.2 Monitor WordPress

- Check plugin activation status
- Test property display
- Monitor page load times
- Check for errors in WordPress logs

### 4.3 Set Up Continuous Deployment

Both services will auto-deploy when you push to GitHub:

```bash
# Make changes locally
git add .
git commit -m "Update scraper or plugin"
git push

# Railway will automatically redeploy
```

## 🎯 Quick Setup Checklist

### Scraper Service:
- [ ] Repository pushed to GitHub
- [ ] Railway service created
- [ ] Environment variables configured
- [ ] Start command set to `python scheduler.py`
- [ ] Service deployed and running
- [ ] Logs show successful scraping

### WordPress Service:
- [ ] WordPress template deployed
- [ ] Database configured
- [ ] Plugin installed and activated
- [ ] Shortcode added to page
- [ ] Properties displaying correctly
- [ ] Mobile responsive working

### Integration:
- [ ] Scraper saving JSON to accessible location
- [ ] WordPress reading JSON file
- [ ] Properties updating automatically
- [ ] No errors in logs

## 🐛 Troubleshooting

### Scraper Not Running
- Check Railway logs for errors
- Verify environment variables are set
- Ensure `requirements.txt` is complete
- Check Playwright browsers are installed

### WordPress Plugin Not Working
- Verify plugin is activated
- Check file permissions
- Test AJAX endpoints are accessible
- Clear WordPress cache

### Properties Not Displaying
- Check JSON file exists and is readable
- Verify JSON format is correct
- Test AJAX request in browser console
- Check WordPress error logs

### Performance Issues
- Optimize images (convert to WebP)
- Enable WordPress caching
- Use CDN for static assets
- Monitor Railway resource usage

## 📞 Need Help?

If you encounter issues:
1. Check Railway logs for error messages
2. Verify all environment variables are set
3. Test scraper locally first
4. Contact Railway support

## 🎉 Success Indicators

Your deployment is successful when:
- ✅ Scraper runs every 4 hours automatically
- ✅ Properties appear on WordPress site
- ✅ Filters and search work correctly
- ✅ Mobile display is responsive
- ✅ No errors in Railway logs
- ✅ Page loads in < 2 seconds

---

**Next Steps**: Once deployed, monitor for 24 hours to ensure everything runs smoothly, then share the live site with your client!
