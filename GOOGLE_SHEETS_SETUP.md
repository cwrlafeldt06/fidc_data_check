# Google Sheets Integration Setup

This guide explains how to set up Google Sheets integration for exporting fund differences.

## 🔐 Security Note
**IMPORTANT**: Never commit actual Google credentials to the repository. The `google_credentials.json` file is already excluded in `.gitignore`.

## 📋 Prerequisites

1. **Install required Python packages:**
   ```bash
   pip install gspread google-auth openpyxl
   ```

## 🚀 Setup Steps

### Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project ID

### Step 2: Enable Google Sheets API

1. In the Google Cloud Console, go to **APIs & Services** > **Library**
2. Search for "Google Sheets API"
3. Click on it and press **Enable**
4. Also enable "Google Drive API" (needed for creating spreadsheets)

### Step 3: Create Service Account

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **Service Account**
3. Enter a name (e.g., "fund-data-exporter")
4. Click **Create and Continue**
5. Skip role assignment for now (click **Continue**)
6. Click **Done**

### Step 4: Generate Service Account Key

1. Click on the service account you just created
2. Go to the **Keys** tab
3. Click **Add Key** > **Create New Key**
4. Select **JSON** format
5. Click **Create**
6. A JSON file will be downloaded to your computer

### Step 5: Set Up Credentials File

1. **Rename** the downloaded JSON file to `google_credentials.json`
2. **Move** it to your project root directory (same level as `analyze_differences.py`)
3. **Verify** the file structure matches the template in `google_credentials_template.json`

### Step 6: Configure Spreadsheet Permissions

Since the service account needs to create and access spreadsheets:

**Option A: Make spreadsheets publicly readable (simpler)**
- The script will automatically make created spreadsheets readable by anyone with the link

**Option B: Share with specific users (more secure)**
- After creating a spreadsheet, manually share it with the users who need access
- Or modify the script to share with specific email addresses

## 🧪 Testing the Setup

Test your setup by running:

```bash
# Test Google Sheets export
python analyze_differences.py --fund pi --format google_sheets

# If it fails, fall back to Excel
python analyze_differences.py --fund pi --format excel
```

## 🔧 Alternative Setup (Environment Variables)

For even better security, you can use environment variables instead of a JSON file:

1. **Create a `.env` file** (already excluded in .gitignore):
   ```
   GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_KEY_HERE\n-----END PRIVATE KEY-----\n"
   GOOGLE_CLIENT_EMAIL="your-service-account@project.iam.gserviceaccount.com"
   GOOGLE_PROJECT_ID="your-project-id"
   ```

2. **Install python-dotenv**:
   ```bash
   pip install python-dotenv
   ```

3. **Modify the script** to use environment variables (optional enhancement)

## ❌ Troubleshooting

### "Credentials file not found"
- Ensure `google_credentials.json` is in the project root
- Check the file name is exactly `google_credentials.json`

### "Permission denied" or "API not enabled"
- Verify Google Sheets API and Google Drive API are enabled
- Check service account permissions

### "Invalid credentials"
- Ensure the JSON file is valid and complete
- Try downloading a fresh service account key

### "Quota exceeded"
- Google Sheets API has usage limits
- Wait a few minutes and try again

## 🎯 Usage Examples

```bash
# Export to Google Sheets (creates new spreadsheet)
python analyze_differences.py --fund pi --format google_sheets

# Export to Excel (local file)
python analyze_differences.py --fund pi --format excel

# Export to CSV (fallback)
python analyze_differences.py --fund pi --format csv
```

## 📁 File Structure

```
project/
├── google_credentials.json          # Your actual credentials (NOT in git)
├── google_credentials_template.json # Template showing structure
├── GOOGLE_SHEETS_SETUP.md          # This setup guide
├── analyze_differences.py           # Main script
└── .gitignore                      # Excludes sensitive files
```

---

**Remember**: Keep your `google_credentials.json` file secure and never share it publicly! 