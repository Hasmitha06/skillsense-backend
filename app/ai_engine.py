"""
Rule-based evaluation engine for SkillSense AI.

This is deliberately deterministic (no external LLM call) so the whole
pipeline works fully offline and is easy to test. The public function
`evaluate()` is the single seam where a real LLM/ML model could later be
swapped in — it takes the same role/questions/answers and must return the
same shape described in schemas.AssessmentResult.
"""

from collections import defaultdict
from app import models

ACTION_TEMPLATES = {
    "DSA": "Practice 3 array, hashing or tree problems a day for the next week.",
    "Spring Boot": "Rebuild a small REST API from scratch, focusing on controllers and dependency injection.",
    "Multithreading": "Review 2-3 classic race-condition examples and rewrite them using `synchronized` or locks.",
    "SQL": "Redo the join and aggregation exercises, focusing on WHERE vs HAVING.",
    "Java": "Revisit OOP fundamentals: inheritance, polymorphism and autoboxing edge cases.",
    "Python": "Work through generator and concurrency (GIL) exercises.",
    "ML Basics": "Review regularization and evaluation metrics on an imbalanced dataset example.",
    "Statistics": "Redo a set of hypothesis-testing problems with a focus on interpreting p-values.",
    "React": "Rebuild a small component using state, props and `useEffect` dependencies deliberately.",
    "JavaScript": "Review equality/coercion rules and rewrite a snippet using strict equality throughout.",
    "CSS": "Rebuild a layout using flexbox/grid `gap` instead of margin-based spacing.",
}

DEFAULT_ACTION = "Revisit the core concepts for this topic and retest in a few days."


def _topic_scores(role: models.Role, questions: list[models.Question], answers: dict[int, int]):
    by_topic = defaultdict(list)  # topic -> list[(question, correct: bool)]
    for q in questions:
        if q.topic not in role.topics:
            continue
        selected = answers.get(q.id)
        correct = selected is not None and selected == q.correct_index
        by_topic[q.topic].append((q, correct))

    scores = {}
    wrong_by_topic = defaultdict(list)
    for topic, items in by_topic.items():
        total = len(items)
        right = sum(1 for _, correct in items if correct)
        scores[topic] = round((right / total) * 100) if total else 0
        wrong_by_topic[topic] = [q for q, correct in items if not correct]

    # Ensure every role topic appears, even with 0 questions answered for it
    for topic in role.topics:
        scores.setdefault(topic, 0)

    return scores, wrong_by_topic


def evaluate(role: models.Role, questions: list[models.Question], answers: dict[int, int]) -> dict:
    scores, wrong_by_topic = _topic_scores(role, questions, answers)

    skills = [{"name": topic, "score": scores[topic]} for topic in role.topics]
    overall_score = round(sum(s["score"] for s in skills) / len(skills)) if skills else 0

    ranked = sorted(role.topics, key=lambda t: scores[t], reverse=True)

    strengths = []
    for topic in ranked:
        if scores[topic] >= 75 and len(strengths) < 3:
            strengths.append({
                "topic": topic,
                "detail": f"Consistently correct across {topic} questions.",
            })

    gaps = []
    for topic in sorted(role.topics, key=lambda t: scores[t]):
        if scores[topic] < 60 and len(gaps) < 3:
            wrong_qs = wrong_by_topic.get(topic, [])
            if wrong_qs:
                patterns = list(dict.fromkeys(q.mistake_pattern for q in wrong_qs))[:2]
                pattern = " ".join(patterns)
            else:
                pattern = "No questions attempted for this topic yet."
            gaps.append({
                "topic": topic,
                "pattern": pattern,
                "severity": "high" if scores[topic] < 50 else "medium",
            })

    # Readiness
    threshold = role.threshold
    if overall_score >= threshold:
        label = "Ready"
    elif overall_score >= threshold - 15:
        label = "Approaching ready"
    else:
        label = "Needs more preparation"

    if strengths and gaps:
        note = (
            f"Ahead of the bar on {strengths[0]['topic']}. "
            f"{gaps[0]['topic']} is currently below the threshold expected for {role.name} roles."
        )
    elif gaps:
        note = f"{gaps[0]['topic']} is currently below the threshold expected for {role.name} roles."
    else:
        note = f"Solid, even performance across the topics measured for {role.name} roles."

    readiness = {"score": overall_score, "threshold": threshold, "label": label, "note": note}

    # Recommendation
    top_gap_topics = [g["topic"] for g in gaps[:2]]
    if top_gap_topics:
        headline = f"Focus on {' and '.join(top_gap_topics)} for the next 14 days"
        detail = (
            "These areas carry the largest gap between your current score and the bar for "
            f"{role.name} roles. Closing them first will move your overall readiness the most."
        )
    else:
        headline = "Keep reinforcing your current strengths"
        detail = "No major gaps detected this round — focus on maintaining consistency and speed."

    actions = [ACTION_TEMPLATES.get(g["topic"], DEFAULT_ACTION) for g in gaps] or [
        "Take on a small project that stretches your strongest topics further."
    ]
    recommendation = {"headline": headline, "detail": detail, "actions": actions}

    # Roadmap
    gap_topics = [g["topic"] for g in gaps]
    phase_30 = gap_topics[:1] or ["your weakest topic"]
    phase_60 = gap_topics[1:] or ["a project applying your strongest skills"]
    roadmap = [
        {"window": "30 days", "goals": [f"Close the {t} gap" for t in phase_30] + ["Retest the weakest topic(s)"]},
        {"window": "60 days", "goals": [f"Build a project exercising {t}" for t in phase_60] + ["Practice medium-difficulty problems daily"]},
        {"window": "90 days", "goals": ["Mock interview simulation", "Portfolio project review", "Final readiness assessment"]},
    ]

    return {
        "skills": skills,
        "strengths": strengths,
        "gaps": gaps,
        "overall_score": overall_score,
        "readiness": readiness,
        "recommendation": recommendation,
        "roadmap": roadmap,
    }
