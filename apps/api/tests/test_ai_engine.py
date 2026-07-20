from app.ai.requirement_classifier import RequirementClassifier
from app.ai.requirement_extractor import RequirementExtractor
from app.ai.question_generator import QuestionGenerator


def test_requirement_extraction_returns_structured_output():
    transcript = (
        "We need an ecommerce website for selling electronics. "
        "Customers should be able to create accounts, browse products, add to cart, "
        "and pay securely with Stripe. The system should support mobile users and "
        "load quickly. We also need an admin dashboard for inventory and orders."
    )

    result = RequirementExtractor().extract_requirements(transcript)

    assert result["functional_requirements"]
    assert result["non_functional_requirements"]
    assert result["business_requirements"]
    assert result["technical_requirements"]
    assert result["missing_information"]
    assert result["questions"]


def test_requirement_classifier_assigns_expected_categories():
    classifier = RequirementClassifier()

    functional = classifier.classify_requirement(
        "Users should be able to create accounts and check out securely"
    )
    non_functional = classifier.classify_requirement(
        "The platform must respond within two seconds for mobile users"
    )

    assert functional["category"] == "functional"
    assert non_functional["category"] == "non_functional"


def test_question_generator_suggests_follow_up_questions():
    generator = QuestionGenerator()
    missing_information = [
        "target_users",
        "user_roles",
        "integrations",
        "timeline",
    ]

    questions = generator.generate_questions(missing_information, "We need an ecommerce site")

    assert any("payment gateway" in question["question"].lower() for question in questions)
    assert any("roles" in question["question"].lower() for question in questions)
    assert any("timeline" in question["question"].lower() for question in questions)
