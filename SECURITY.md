# 🔒 Security & Privacy

This document outlines the security measures implemented in the Mohan Voice Assistant project.

## 📋 Personal Information Privacy

### **Personal Context Protection**

The personal context containing professional background, achievements, and personal details is kept private through:

#### **1. Separated Context File**
- **Personal details** are stored in `mohan_context.py` (gitignored)
- **Template provided** as `mohan_context_template.py` (public)
- **Fallback context** used when personal file is not available

#### **2. Git Protection**
Personal context files are automatically excluded from version control:
```gitignore
# Personal Context (IMPORTANT: Keep private)
mohan_context.py
*_context.py
personal_info.py
```

#### **3. Setup Instructions**
```bash
# 1. Copy template
cp mohan_context_template.py mohan_context.py

# 2. Edit with your information
nano mohan_context.py

# 3. File is automatically ignored by git
git status  # mohan_context.py will not appear
```

## 🔐 API Key Security

### **Environment-Based Configuration**
- API keys stored as **Modal secrets** (encrypted)
- **No hardcoded keys** in source code
- **Environment variables** for local testing

```bash
# Modal secrets (production)
modal secret create groq-api-key GROQ_API_KEY=your_key

# Environment variables (development)
export GROQ_API_KEY="your_key"
```

### **API Key Best Practices**
- ✅ **Never commit** API keys to version control
- ✅ **Use secrets management** (Modal secrets)
- ✅ **Rotate keys regularly**
- ✅ **Monitor usage** through provider dashboards

## 🌐 Application Security

### **HTTPS Only**
- All communication over **encrypted connections**
- Modal.com provides **automatic HTTPS**
- **Secure WebSocket** connections (WSS)

### **No Data Persistence**
- **Conversations not stored** permanently
- **Audio data processed** in memory only
- **No logging** of personal conversations

### **Environment Isolation**
- **Serverless execution** in isolated containers
- **Automatic scaling** and resource management
- **No shared state** between instances

## 🛡️ Privacy Considerations

### **Data Processing**
- **Speech-to-text**: Processed via secure APIs or locally
- **LLM inference**: Groq's secure infrastructure
- **Web search**: Anonymous DuckDuckGo queries
- **No tracking** or analytics on user conversations

### **Third-Party Services**
| Service | Purpose | Data Sent | Privacy Policy |
|---------|---------|-----------|----------------|
| **Groq** | LLM Inference | User questions, context | [Groq Privacy](https://groq.com/privacy/) |
| **OpenAI** | STT/TTS Fallback | Audio data (optional) | [OpenAI Privacy](https://openai.com/privacy/) |
| **DuckDuckGo** | Web Search | Search queries only | [DDG Privacy](https://duckduckgo.com/privacy) |
| **Modal.com** | Hosting | Application code, logs | [Modal Privacy](https://modal.com/privacy) |

### **User Data**
- **No user accounts** or authentication required
- **No personal data collection** from users
- **No conversation history** stored
- **Anonymous usage** by design

## 🔍 Security Audit

### **Regular Security Checks**
- [ ] Review API key usage and rotation
- [ ] Monitor Modal dashboard for unusual activity
- [ ] Check for hardcoded secrets in code
- [ ] Validate .gitignore effectiveness
- [ ] Review third-party service updates

### **Recommended Security Practices**
1. **API Key Management**:
   - Use unique keys for development/production
   - Monitor usage through provider dashboards
   - Set up billing alerts for unusual usage

2. **Code Security**:
   - Never commit secrets to version control
   - Use environment variables for sensitive data
   - Regularly update dependencies

3. **Deployment Security**:
   - Use Modal secrets for production keys
   - Monitor application logs for errors
   - Keep personal context file local only

## 🚨 Security Incident Response

### **If API Keys are Compromised**
1. **Immediately revoke** compromised keys
2. **Generate new keys** from provider dashboard
3. **Update Modal secrets** with new keys
4. **Monitor usage** for unauthorized activity
5. **Review access logs** if available

### **If Personal Information is Exposed**
1. **Remove exposed content** immediately
2. **Update .gitignore** if needed
3. **Force push** to overwrite git history if necessary
4. **Regenerate context file** with updated information

### **Reporting Security Issues**
For security concerns or vulnerabilities:
- **Email**: [security contact if applicable]
- **Create private issue** in repository
- **Follow responsible disclosure**

## ✅ Security Checklist

Before deployment, ensure:
- [ ] Personal context file (`mohan_context.py`) is gitignored
- [ ] No hardcoded API keys in source code
- [ ] Modal secrets properly configured
- [ ] HTTPS enabled (automatic with Modal)
- [ ] Dependencies up to date
- [ ] No sensitive data in logs
- [ ] Error handling doesn't expose secrets

---

**Remember**: Security is an ongoing process. Regularly review and update these practices as the project evolves. 