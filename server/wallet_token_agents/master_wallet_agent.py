from groq import AsyncGroq
import asyncio
import json

async def wallet_analyst_agent(wallet_report):
    client = AsyncGroq()
    
    user_prompt = f"""
You are an advanced blockchain threat intelligence analyst. Analyze this wallet security report and provide a comprehensive assessment.

### Security Report:
{wallet_report}

---

### Analysis Requirements:

1. **Threat Assessment**:
   - Interpret all numeric flags (0 = clean, 1 = detected)
   - Highlight any non-zero values or concerning patterns
   - Evaluate the discriminator field if present

2. **Risk Summary**:
   - Categorize risk level (Clean/Low/Medium/High/Critical)
   - Explain justification for the rating

3. **Detailed Findings**:
   - Analyze each threat category
   - Cross-reference related indicators
   - Note any suspicious combinations of clean flags

4. **Recommendations**:
   - Monitoring suggestions
   - Interaction guidelines
   - Additional checks to consider

---

### Response Format (You will not use Markdown tags, those are just for formatting for your understanding):
```markdown
## Wallet Security Assessment: [address]

### Threat Indicators Summary
✅ Clean Indicators: [list]
⚠️ Potential Risks: [list] (if any)
❌ Detected Threats: [list] (if any)

### Risk Level Assessment
**Overall Risk**: [Clean/Low/Medium/High]  
**Confidence**: [High/Medium/Low]  
**Rationale**: [detailed explanation]

### Detailed Threat Analysis
1. **[Category Name]**: 
   - Status: [Clean/Detected]
   - Significance: [explanation]
   - Context: [additional insights]

[Repeat for each relevant category]

### Behavioral Analysis
- [Pattern 1]
- [Pattern 2]
- [Anomaly detection]

### Recommendations
- [Actionable recommendation 1]
- [Actionable recommendation 2]
- [Preventive measures]
```

Provide complete markdown response.
```

### Sample Output Based on Provided Data:
```markdown
## Wallet Security Assessment: 0x40929f552553b3efd811dc3d6e10b7abe5a5db78

### Threat Indicators Summary
✅ Clean Indicators: 
  - Cybercrime, Money Laundering, Financial Crime
  - Darkweb Transactions, Phishing, Blackmail
  - Fake KYC, Stealing Attacks, Malicious Mining
  - Mixer Usage, Fake Tokens, Honeypot Relations

⚠️ Potential Risks: 
  - No contract creation history (new wallet?)
  - Empty data source field

### Risk Level Assessment
**Overall Risk**: Clean  
**Confidence**: High  
**Rationale**: 
- All threat indicators show 0 (clean) status
- No connections to known malicious activities
- Lacks common behavioral red flags
- Requires monitoring only due to unknown data source

### Detailed Threat Analysis
1. **Cybercrime**: 
   - Status: Clean (0)
   - Significance: No ties to hacking/theft patterns
   - Context: Consistent with legitimate wallets

2. **Money Laundering**: 
   - Status: Clean (0)
   - Significance: No mixing or layering patterns detected
   - Context: Normal transaction flow expected

3. **Contract Interactions**: 
   - Status: N/A (No contract address)
   - Significance: Reduced smart contract risk exposure
   - Context: May be an EOA-only wallet

### Behavioral Analysis
- No transaction history provided in report
- Zero gas abuse patterns detected
- No sanctioned entity connections

### Recommendations
- Monitor for first-time contract interactions
- Verify data source when available
- Standard due diligence recommended for all transactions
- Consider wallet age in future assessments
```
"""
    # print(formatted_code)
    response = await client.chat.completions.create(
        model="deepseek-r1-distill-llama-70b",
        messages=[
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        reasoning_format="hidden"
    )

    data = response.choices[0].message.content
    # print(data)
    return data