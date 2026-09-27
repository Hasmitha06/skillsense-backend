from sqlalchemy.orm import Session
from app import models

ROLES = [
    dict(key="java", name="Java Developer", blurb="Core Java, OOP, Spring Boot, SQL",
         color="primary", threshold=80.0,
         topics=["Java", "DSA", "Spring Boot", "SQL", "Multithreading"]),
    dict(key="python", name="Python Developer", blurb="Python, APIs, data handling, SQL",
         color="sky", threshold=75.0,
         topics=["Python", "DSA", "SQL", "Multithreading"]),
    dict(key="ai", name="AI Developer", blurb="ML fundamentals, Python, data structures",
         color="violet", threshold=75.0,
         topics=["Python", "ML Basics", "Statistics", "DSA"]),
    dict(key="frontend", name="Frontend Developer", blurb="JavaScript, React, CSS, accessibility",
         color="accent", threshold=75.0,
         topics=["JavaScript", "React", "CSS", "DSA"]),
]

QUESTIONS = [
    dict(topic="Java", prompt="Which keyword prevents a class from being inherited?",
         options=["static", "final", "private", "abstract"], correct_index=1,
         mistake_pattern="Confuses access modifiers with inheritance-control keywords."),
    dict(topic="Java", prompt="What does `Integer.valueOf(5) == Integer.valueOf(5)` evaluate to?",
         options=["true", "false", "Compile error", "Depends on the JVM"], correct_index=0,
         mistake_pattern="Unclear on Java's Integer caching for small autoboxed values."),

    dict(topic="DSA", prompt="What is the time complexity of binary search on a sorted array?",
         options=["O(n)", "O(n log n)", "O(log n)", "O(1)"], correct_index=2,
         mistake_pattern="Overestimates the cost of divide-and-conquer search on sorted data."),
    dict(topic="DSA", prompt="Which data structure combination is best for an LRU cache?",
         options=["Array only", "HashMap + doubly linked list", "Stack only", "Binary search tree"], correct_index=1,
         mistake_pattern="Doesn't connect O(1) access/eviction needs to a combined hashmap + linked list design."),

    dict(topic="Spring Boot", prompt="Which annotation marks a class as a REST controller in Spring Boot?",
         options=["@Service", "@RestController", "@Repository", "@Configuration"], correct_index=1,
         mistake_pattern="Confuses @Controller (view-based) with @RestController (JSON responses)."),
    dict(topic="Spring Boot", prompt="Which annotation injects a bean by type in Spring?",
         options=["@Value", "@Autowired", "@Bean", "@Component"], correct_index=1,
         mistake_pattern="Unclear on how dependency injection annotations are applied."),

    dict(topic="SQL", prompt="Which JOIN returns only matching rows from both tables?",
         options=["LEFT JOIN", "RIGHT JOIN", "INNER JOIN", "FULL OUTER JOIN"], correct_index=2,
         mistake_pattern="Mixes up JOIN types and which rows each one includes."),
    dict(topic="SQL", prompt="Which SQL clause filters groups after aggregation?",
         options=["WHERE", "HAVING", "GROUP BY", "ORDER BY"], correct_index=1,
         mistake_pattern="Confuses WHERE (row-level filter) with HAVING (group-level filter)."),

    dict(topic="Multithreading", prompt="What does Java's `synchronized` keyword primarily prevent?",
         options=["Memory leaks", "Race conditions", "Null pointer errors", "Slow compilation"], correct_index=1,
         mistake_pattern="Understands the syntax but not when race conditions actually occur."),

    dict(topic="Python", prompt="What does the GIL primarily restrict in CPython?",
         options=["Disk I/O", "True parallel execution of threads", "Memory allocation", "Import speed"], correct_index=1,
         mistake_pattern="Unclear on how the Global Interpreter Lock affects multithreaded CPU-bound code."),
    dict(topic="Python", prompt="Which of these creates a generator in Python?",
         options=["def f(): return 1", "def f(): yield 1", "lambda: 1", "class F: pass"], correct_index=1,
         mistake_pattern="Confuses generator functions (yield) with regular functions."),

    dict(topic="ML Basics", prompt="What problem does L2 regularization primarily address?",
         options=["Underfitting", "Overfitting", "Slow training", "Data leakage"], correct_index=1,
         mistake_pattern="Doesn't connect regularization techniques to controlling model variance/overfitting."),
    dict(topic="ML Basics", prompt="Which metric is most appropriate for a highly imbalanced classification problem?",
         options=["Accuracy", "F1-score", "Mean Squared Error", "R-squared"], correct_index=1,
         mistake_pattern="Relies on plain accuracy even when class imbalance makes it misleading."),

    dict(topic="Statistics", prompt="A p-value of 0.03 at alpha = 0.05 typically leads you to:",
         options=["Accept the null hypothesis", "Reject the null hypothesis", "Increase sample size", "Ignore the result"],
         correct_index=1, mistake_pattern="Misinterprets p-value thresholds relative to the chosen significance level."),

    dict(topic="JavaScript", prompt="What does `===` check in JavaScript that `==` does not?",
         options=["Nothing, they're identical", "Type, in addition to value",
                  "Only reference equality for objects", "Whether a variable is declared"], correct_index=1,
         mistake_pattern="Relies on loose equality (==) and misses type coercion pitfalls."),

    dict(topic="React", prompt="What triggers a React functional component to re-render?",
         options=["Changing a local variable", "A state or props update", "Calling console.log", "Refreshing the CSS"],
         correct_index=1, mistake_pattern="Doesn't distinguish between plain variables and reactive state/props."),
    dict(topic="React", prompt="What is the purpose of the dependency array in `useEffect`?",
         options=["It has no effect", "Controls when the effect re-runs", "Only for TypeScript typing",
                  "Sets the component's initial state"], correct_index=1,
         mistake_pattern="Misunderstands when effects re-run relative to dependency changes."),

    dict(topic="CSS", prompt="Which CSS property creates space between flex items directly?",
         options=["margin only", "gap", "padding only", "flex-space"], correct_index=1,
         mistake_pattern="Reaches for margin hacks instead of the modern flex/grid `gap` property."),
]


def seed(db: Session) -> None:
    if db.query(models.Role).count() == 0:
        for r in ROLES:
            db.add(models.Role(**r))

    if db.query(models.Question).count() == 0:
        for q in QUESTIONS:
            db.add(models.Question(**q))

    db.commit()
