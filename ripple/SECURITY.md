# RIPPLE Security Best Practices

## 🔒 Token and Credential Management

### ✅ DO's

1. **Use Environment Variables**
   ```bash
   export GITHUB_TOKEN="your_token_here"
   export NAI_API_KEY="your_api_key_here"
   ```

2. **Never Commit Tokens**
   - All sensitive credentials are read from environment variables
   - `.env` files are automatically ignored by git
   - Never add tokens to version control

3. **Use Token Expiration**
   - Set expiration dates on GitHub tokens
   - Rotate tokens regularly (every 90 days recommended)

4. **Limit Token Scopes**
   - GitHub token only needs: `repo` scope
   - Don't use tokens with admin or delete permissions

5. **Store Securely**
   - Use environment variables for short-term use
   - Use secret managers for production (e.g., AWS Secrets Manager, HashiCorp Vault)
   - Add to shell profile for persistent use:
     ```bash
     # Add to ~/.bashrc or ~/.zshrc
     export GITHUB_TOKEN="your_token_here"
     ```

### ❌ DON'Ts

1. **Never Hardcode Tokens**
   ```python
   # ❌ BAD - Never do this
   GITHUB_TOKEN = "ghp_abc123..."
   
   # ✅ GOOD - Always do this
   GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
   ```

2. **Never Log Tokens**
   - Don't print tokens in logs
   - Don't include tokens in error messages
   - Don't echo tokens in scripts

3. **Never Share Tokens**
   - Don't email or message tokens
   - Don't share in Slack/Teams/etc.
   - Each user should generate their own tokens

4. **Never Check into Git**
   - Don't commit `.env` files
   - Don't commit `config.py` with hardcoded values
   - Review commits before pushing

## 🔐 Current Security Implementation

### Configuration (`config.py`)

```python
# All tokens read from environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Required
NAI_ENDPOINT_API_KEY = os.getenv("NAI_API_KEY")  # Optional

# Validation
if not GITHUB_TOKEN:
    raise EnvironmentError("GITHUB_TOKEN required!")
```

### What's Protected

- ✅ GitHub Personal Access Token
- ✅ Nutanix AI API Key
- ✅ All authentication credentials
- ✅ No secrets in source code
- ✅ No secrets in logs

## 🛡️ Setup Instructions

### Quick Setup

```bash
# 1. Set GitHub token (REQUIRED)
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 2. Set NAI API key (optional, for full features)
export NAI_API_KEY="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# 3. Run RIPPLE
python3 ripple.py --repos lcm-framework --days 2
```

### Persistent Setup

Add to your shell profile:

```bash
# Edit your profile
nano ~/.zshrc  # or ~/.bashrc

# Add these lines
export GITHUB_TOKEN="your_token_here"
export NAI_API_KEY="your_api_key_here"

# Reload profile
source ~/.zshrc  # or source ~/.bashrc
```

### Using setup_env.sh

```bash
# Run the setup helper
./setup_env.sh

# Follow the instructions to set your tokens
```

## 🔍 Token Generation

### GitHub Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Set a descriptive name: "RIPPLE Analysis Tool"
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
5. Set expiration (90 days recommended)
6. Click "Generate token"
7. **Copy immediately** (you won't see it again!)

### NAI API Key

Contact your Nutanix AI platform administrator for an API key.

## 🚨 Token Compromised?

If your token is accidentally exposed:

### GitHub Token

1. **Immediately revoke** at: https://github.com/settings/tokens
2. Generate a new token
3. Update your environment variable
4. Review recent API activity

### NAI API Key

1. Contact Nutanix AI administrator
2. Request key rotation
3. Update environment variable

## 📋 Security Checklist

Before running RIPPLE:

- [ ] Tokens stored in environment variables only
- [ ] No tokens in source code
- [ ] `.env` files in `.gitignore`
- [ ] GitHub token has minimal scopes
- [ ] Tokens have expiration dates set
- [ ] Shell history doesn't contain tokens
- [ ] No tokens in screenshots or documentation

## 🔐 Production Deployment

For production use:

1. **Use Secret Manager**
   ```bash
   # AWS Secrets Manager
   aws secretsmanager get-secret-value --secret-id ripple/github-token
   
   # HashiCorp Vault
   vault kv get secret/ripple/tokens
   ```

2. **Use Service Accounts**
   - Create dedicated GitHub app/account
   - Use machine accounts, not personal tokens

3. **Implement Token Rotation**
   - Automate token rotation every 90 days
   - Monitor for expiring tokens

4. **Enable Audit Logging**
   - Log all API access (without tokens)
   - Monitor for unusual patterns
   - Alert on failed authentication

## 📚 Additional Resources

- [GitHub Token Best Practices](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [12 Factor App - Config](https://12factor.net/config)

---

**Remember: Never commit secrets. Always use environment variables. 🔒**

