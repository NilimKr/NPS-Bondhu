def calculate_pension_corpus(current_age, retirement_age, monthly_contribution, expected_return_rate):
    """
    Calculates the expected pension corpus and other details.
    
    Args:
        current_age (int): Current age of the subscriber.
        retirement_age (int): Age at which the subscriber wishes to retire (default 60 usually).
        monthly_contribution (float): Monthly investment amount.
        expected_return_rate (float): Expected annual return rate in percentage.
        
    Returns:
        dict: A dictionary containing:
            - total_investment
            - interest_earned
            - total_corpus
            - lumpsum_withdrawal (60% typical)
            - annuity_corpus (40% typical)
    """
    if current_age >= retirement_age:
        return {
            "error": "Current age must be less than retirement age."
        }
    
    months = (retirement_age - current_age) * 12
    monthly_rate = expected_return_rate / 12 / 100
    
    # Future Value of SIP formula
    # FV = P * [ (1+r)^n - 1 ] * (1+r) / r
    
    if monthly_rate == 0:
        total_corpus = monthly_contribution * months
    else:
        total_corpus = monthly_contribution * ( ( (1 + monthly_rate) ** months - 1 ) / monthly_rate ) * (1 + monthly_rate)
    
    total_investment = monthly_contribution * months
    interest_earned = total_corpus - total_investment
    
    # Standard NPS Exit Rules at 60
    lumpsum_withdrawal = total_corpus * 0.60
    annuity_corpus = total_corpus * 0.40
    
    # Monthly Pension from Annuity (Assuming ~6% annuity rate typically, but simplest is just showing the corpus)
    # Let's estimate monthly pension at 6% p.a. on annuity corpus
    estimated_monthly_pension = (annuity_corpus * 0.06) / 12
    
    return {
        "total_investment": round(total_investment, 2),
        "interest_earned": round(interest_earned, 2),
        "total_corpus": round(total_corpus, 2),
        "lumpsum_withdrawal": round(lumpsum_withdrawal, 2),
        "annuity_corpus": round(annuity_corpus, 2),
        "estimated_monthly_pension": round(estimated_monthly_pension, 2)
    }
