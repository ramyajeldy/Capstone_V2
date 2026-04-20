def calculate_risk_score(
    bert_score: float,
    url_score: float,
    domain_score: float,
    html_score: float
) -> float:
    final_score = (
        0.35 * bert_score +
        0.40 * url_score +
        0.25 * html_score
    )

    return round(min(final_score, 1.0), 4)