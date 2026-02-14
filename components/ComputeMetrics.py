import requests
import hashlib
import math
import re

class BreachChecker(Exception):
    pass

class ComputeMetrics:

    def __init__(self,password):
        self.password = password

    def check_breach(self) -> int:

            api_url = "https://api.pwnedpasswords.com/range/"
            sha1 = hashlib.sha1(self.password.encode()).hexdigest().upper()
            prefix = sha1[:5]
            suffix = sha1[5:]

            try:
                response = requests.get(api_url + prefix,
                                        timeout=10,
                                        headers={'Add-Padding': 'True'}
                                        )
                response.raise_for_status()

            except requests.RequestException as e:
                raise BreachChecker(f"Breach API Error: {e}")

            for line in response.text.splitlines():
                hash_suffix, count = line.split(":")
                if hash_suffix == suffix:
                    return int(count)

            return 0

    def calculate_entropy(self) -> float:
        pool = 0
        p = self.password

        if any(c.islower() for c in p):
            pool += 26
        if any(c.isupper() for c in p):
            pool += 26
        if any(c.isdigit() for c in p):
            pool += 10
        if any(not c.isalnum() for c in p):
            pool += 32

        if pool == 0:
            return 0

        return round(min(float((len(p) * math.log2(pool))), float(128)), 2)

    def rule_score(self) -> int:

        common_patterns = [
            "123", "234", "345", "456", "567", "678", "789",
            "password", "admin", "letmein"
        ]

        keyboard_sequences = [
            "qwerty", "asdf", "zxcv",
            "poiuy", "lkjhg", "mnbvc",
            "1qaz", "2wsx", "3edc", "4rfv", "5tgb",
        ]

        score = 0
        length = len(self.password)
        p = self.password

        #Length (strongly weighted)
        if length >= 16:
            score += 3
        elif length >= 12:
            score += 2
        elif length >= 10:
            score += 1

        #Character variety
        has_lower = any(c.islower() for c in p)
        has_upper = any(c.isupper() for c in p)
        has_digit = any(c.isdigit() for c in p)
        has_symbol = any(not c.isalnum() for c in p)

        score += sum([has_lower, has_upper, has_digit, has_symbol])

        if any(run in p.lower() for run in keyboard_sequences):
            score -= 2

        #Penalize repeated characters (aaaa, 1111, !!!!)
        if re.search(r"(.)\1{2,}", p):
            score -= 1

        # 4️⃣ Penalize common patterns / dictionary fragments
        lower_pw = p.lower()
        if any(pat in lower_pw for pat in common_patterns):
            score -= 2

        # 5️⃣ Reward passphrase-like structure (spaces or separators)
        if length >= 14 and re.search(r"[ _\-]", p):
            score += 2

        # Clamp score between 0 and 8
        return max(0, min(score, 8))

def classify_risk(entropy, rule_score, breach_count):

    if breach_count > 1000:
        return "\nThis password is no longer secure.\nBecause it has appeared in innumerous data breaches, it could be exploited without warning.\nPlease change it now and do not reuse it elsewhere.","CRITICAL"
    if breach_count > 0:
        return "This password is vulnerable due to exposure in previous data breaches.\nEven if it appears complex, attackers may already recognize it.\nChanging it now and using a unique password for each service is strongly recommended.","HIGH"
    if entropy < 40 or rule_score < 7:
        return "\nGood news — this password hasn’t been found in any known breaches.\nHowever, it’s only moderately strong.\nWhile its complexity is decent, real-world security depends on length, uniqueness, and resistance to common patterns.\nA longer passphrase or a few extra characters would significantly improve its safety.","MEDIUM"
    else:
         return "\nGreat choice! This password is strong and hasn’t appeared in known breaches.\nKeep it unique to this service, and you’re in good shape.","LOW"



























