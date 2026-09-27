import secrets
import string

AMBIGUOUS_CHARS = "Il1O0"
def generate_password(length: int = 16, use_symbols: bool = True, avoid_ambiguous: bool = True) -> str:
    if length < 8:
        length = 8

    symbols = "!@#$%^&*()-_=+[]{}"
    lower_pool = string.ascii_lowercase
    upper_pool = string.ascii_uppercase
    digit_pool = string.digits

    pool = lower_pool + upper_pool + digit_pool
    if use_symbols:
        pool += symbols

    if avoid_ambiguous:
        pool = "".join(c for c in pool if c not in AMBIGUOUS_CHARS)
        lower_pool = "".join(c for c in lower_pool if c not in AMBIGUOUS_CHARS)
        upper_pool = "".join(c for c in upper_pool if c not in AMBIGUOUS_CHARS)
        digit_pool = "".join(c for c in digit_pool if c not in AMBIGUOUS_CHARS)

    required = [
        secrets.choice(lower_pool),
        secrets.choice(upper_pool),
        secrets.choice(digit_pool),
    ]
    if use_symbols:
        required.append(secrets.choice(symbols))

    remaining_len = length - len(required)
    body = [secrets.choice(pool) for _ in range(remaining_len)]

    result = required + body

    for i in range(len(result) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        result[i], result[j] = result[j], result[i]

    return "".join(result)


def password_strength_label(password: str) -> str:
    length_ok = len(password) >= 12
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in string.punctuation for c in password)

    score = sum([length_ok, has_upper, has_lower, has_digit, has_symbol])

    if score >= 5:
        return "Strong"
    elif score >= 3:
        return "Moderate"
    else:
        return "Weak"
