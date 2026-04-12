from langchain_groq import ChatGroq
from dotenv import load_dotenv
import json
import os
import logging
import re

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-70b-versatile",
    temperature=0.3,
    api_key=os.getenv("GROQ_API_KEY")
)

logger = logging.getLogger(__name__)



def extract_json(content: str):
    """
    Extract JSON even if LLM wraps it in markdown/text.
    """
    try:
        content = re.sub(r"```json|```", "", content).strip()

        # extract first JSON object
        start = content.find("{")
        end = content.rfind("}") + 1

        if start == -1 or end == 0:
            return None

        json_str = content[start:end]
        return json.loads(json_str)

    except Exception:
        return None



def validate_output(data):
    if not isinstance(data, dict):
        return False

    required_keys = ["explanation", "key_risk_factors", "verdict"]

    if not all(k in data for k in required_keys):
        return False

    if not isinstance(data["key_risk_factors"], list):
        return False

    return True




def format_features(features):
    if not features:
        return "NO_FEATURES_AVAILABLE"

    return (
        f"tx_frequency={features.get('tx_frequency', 0)}, "
        f"avg_tx_value={features.get('avg_tx_value', 0)}, "
        f"unique_interactions={features.get('unique_interactions', 0)}, "
        f"contract_calls={features.get('contract_calls', 0)}, "
        f"high_risk_interactions={features.get('high_risk_interactions', 0)}"
    )




def format_patterns(patterns):
    if not patterns:
        return "none"

    clean = []

    for p in patterns[:5]:
        if isinstance(p, dict):
            name = p.get("name") or p.get("pattern") or str(p)
            desc = p.get("description", "")

            
            if desc:
                desc = desc[:120] + "..." if len(desc) > 120 else desc
                clean.append(f"{name} ({desc})")
            else:
                clean.append(name)
        else:
            clean.append(str(p))

    return ", ".join(clean)




def normalize_verdict(v):
    v = str(v).upper()

    if "HIGH" in v:
        return "HIGH"
    if "MED" in v:
        return "MEDIUM"
    if "LOW" in v:
        return "LOW"

    return "MEDIUM"  # safe default


def generate_explanation(risk_score, risk_level, features, patterns):

    if not features:
        return {
            "explanation": "No feature data available for risk analysis.",
            "key_risk_factors": ["missing features"],
            "verdict": "UNKNOWN"
        }

    clean_features = format_features(features)
    clean_patterns = format_patterns(patterns)

    prompt = f"""
You are a crypto risk analyst.

Risk Level: {risk_level}
Risk Score: {risk_score}

Features Summary:
{clean_features}

Matched Scam Patterns:
{clean_patterns}

Return STRICT JSON:
{{
  "explanation": "...",
  "key_risk_factors": ["...", "..."],
  "verdict": "LOW|MEDIUM|HIGH"
}}
"""

    logger.info("LLM_CALL_START | risk=%s | patterns=%s", risk_level, clean_patterns)

    try:
        response = llm.invoke(prompt, timeout=8)
        content = response.content

        logger.info("LLM_RAW_RESPONSE_RECEIVED")

        parsed = extract_json(content)

        
        if parsed and validate_output(parsed):

            parsed["verdict"] = normalize_verdict(parsed["verdict"])

            logger.info("LLM_JSON_VALID_SUCCESS")
            return parsed

        logger.warning("LLM_INVALID_OUTPUT | fallback triggered")

        return {
            "explanation": (
                f"Wallet shows {risk_level} risk level. "
                f"Behavioral anomalies detected via transaction patterns "
                f"and interaction signals."
            ),
            "key_risk_factors": [
                "transaction anomalies",
                f"patterns: {clean_patterns}"
            ],
            "verdict": normalize_verdict(risk_level)
        }

    except Exception as e:
        logger.error("LLM_CALL_FAILED | error=%s", str(e))

        return {
            "explanation": (
                f"System-based analysis indicates {risk_level} risk level "
                f"with detected irregular blockchain activity patterns."
            ),
            "key_risk_factors": ["system-level detection"],
            "verdict": "UNKNOWN"
        }