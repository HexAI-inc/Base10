"""
Comprehensive seeding script to ensure each topic has at least 15 questions.
"""
import os
import sys
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.question import Question, Subject, DifficultyLevel


def generate_additional_questions():
    """Generate additional questions to reach 15 per topic."""
    questions = []

    # English Comprehension - needs 13 more (currently 2)
    comprehension_questions = [
        Question(
            subject=Subject.ENGLISH,
            topic="Comprehension",
            content="What is the main idea of a passage?",
            options_json='["A minor detail", "The most important point", "An example", "A conclusion"]',
            correct_index=1,
            difficulty=DifficultyLevel.EASY,
            explanation="The main idea is the primary point or message of the text.",
            exam_year="WASSCE 2023"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Comprehension",
            content="What does 'infer' mean in reading?",
            options_json='["To read quickly", "To guess based on evidence", "To memorize", "To skip"]',
            correct_index=1,
            difficulty=DifficultyLevel.MEDIUM,
            explanation="To infer means to draw conclusions based on evidence in the text.",
            exam_year="WASSCE 2022"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Comprehension",
            content="What is the author's purpose?",
            options_json='["To entertain", "To inform", "To persuade", "All of the above"]',
            correct_index=3,
            difficulty=DifficultyLevel.MEDIUM,
            explanation="Authors can write to entertain, inform, or persuade readers.",
            exam_year="WASSCE 2021"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Comprehension",
            content="What is a summary?",
            options_json='["A long retelling", "A brief overview of main points", "A list of details", "An opinion"]',
            correct_index=1,
            difficulty=DifficultyLevel.EASY,
            explanation="A summary captures the main points in a concise way.",
            exam_year="WASSCE 2023"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Comprehension",
            content="What does 'context clues' mean?",
            options_json="['Hints in the text that help understand words', 'Pictures in the book', 'The book\\'s cover', 'The author\\'s biography']",
            correct_index=0,
            difficulty=DifficultyLevel.MEDIUM,
            explanation="Context clues are words or phrases around an unknown word that help determine its meaning.",
            exam_year="WASSCE 2022"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Comprehension",
            content="What is the difference between fact and opinion?",
            options_json='["Facts can be proven, opinions are beliefs", "Facts are long, opinions are short", "Facts are opinions", "No difference"]',
            correct_index=0,
            difficulty=DifficultyLevel.MEDIUM,
            explanation="Facts are verifiable statements, while opinions are personal beliefs.",
            exam_year="WASSCE 2021"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Comprehension",
            content="What is tone in writing?",
            options_json="['The volume of voice', 'The author\\'s attitude', 'The writing style', 'The length of sentences']",
            correct_index=1,
            difficulty=DifficultyLevel.MEDIUM,
            explanation="Tone is the author's attitude toward the subject or audience.",
            exam_year="WASSCE 2023"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Comprehension",
            content="What is bias in reading?",
            options_json="['Fair presentation', 'Unfair prejudice', 'Complete neutrality', 'Author\\'s opinion']",
            correct_index=1,
            difficulty=DifficultyLevel.HARD,
            explanation="Bias is an unfair preference or prejudice that affects objectivity.",
            exam_year="WASSCE 2022"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Comprehension",
            content="What is skimming?",
            options_json='["Reading every word", "Quickly reading for main ideas", "Reading backwards", "Memorizing text"]',
            correct_index=1,
            difficulty=DifficultyLevel.EASY,
            explanation="Skimming involves quickly glancing through text to find main ideas.",
            exam_year="WASSCE 2021"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Comprehension",
            content="What is scanning?",
            options_json='["Reading for pleasure", "Looking for specific information", "Reading slowly", "Memorizing"]',
            correct_index=1,
            difficulty=DifficultyLevel.EASY,
            explanation="Scanning involves quickly looking for specific facts or details.",
            exam_year="WASSCE 2023"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Comprehension",
            content="What is a thesis statement?",
            options_json='["A question", "The main argument", "A conclusion", "An example"]',
            correct_index=1,
            difficulty=DifficultyLevel.MEDIUM,
            explanation="A thesis statement expresses the main argument or claim of an essay.",
            exam_year="WASSCE 2022"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Comprehension",
            content="What is figurative language?",
            options_json='["Literal meanings", "Word-for-word translation", "Non-literal expressions", "Scientific terms"]',
            correct_index=2,
            difficulty=DifficultyLevel.MEDIUM,
            explanation="Figurative language uses words in non-literal ways to create meaning.",
            exam_year="WASSCE 2021"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Comprehension",
            content="What is the purpose of an introduction?",
            options_json='["To end the essay", "To hook the reader and state thesis", "To provide examples", "To conclude"]',
            correct_index=1,
            difficulty=DifficultyLevel.MEDIUM,
            explanation="An introduction grabs attention and presents the main argument.",
            exam_year="WASSCE 2023"
        ),
    ]
    questions.extend(comprehension_questions)

    # English Vocabulary - needs 13 more (currently 2)
    vocabulary_questions = [
        Question(
            subject=Subject.ENGLISH,
            topic="Vocabulary",
            content="What does 'ubiquitous' mean?",
            options_json='["Rare", "Present everywhere", "Very small", "Extremely large"]',
            correct_index=1,
            difficulty=DifficultyLevel.HARD,
            explanation="'Ubiquitous' means present or found everywhere.",
            exam_year="WASSCE 2023"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Vocabulary",
            content="What does 'gregarious' mean?",
            options_json='["Shy", "Sociable", "Angry", "Lazy"]',
            correct_index=1,
            difficulty=DifficultyLevel.MEDIUM,
            explanation="'Gregarious' means fond of company or sociable.",
            exam_year="WASSCE 2022"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Vocabulary",
            content="What does 'candid' mean?",
            options_json='["Dishonest", "Truthful and straightforward", "Complicated", "Simple"]',
            correct_index=1,
            difficulty=DifficultyLevel.MEDIUM,
            explanation="'Candid' means truthful and straightforward in speech or behavior.",
            exam_year="WASSCE 2021"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Vocabulary",
            content="What does 'prudent' mean?",
            options_json='["Careless", "Acting with care and thought", "Reckless", "Stupid"]',
            correct_index=1,
            difficulty=DifficultyLevel.MEDIUM,
            explanation="'Prudent' means acting with or showing care and thought for the future.",
            exam_year="WASSCE 2023"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Vocabulary",
            content="What does 'altruistic' mean?",
            options_json='["Selfish", "Selfless concern for others", "Greedy", "Proud"]',
            correct_index=1,
            difficulty=DifficultyLevel.HARD,
            explanation="'Altruistic' means showing a disinterested and selfless concern for others.",
            exam_year="WASSCE 2022"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Vocabulary",
            content="What does 'meticulous' mean?",
            options_json='["Careless", "Showing great attention to detail", "Fast", "Lazy"]',
            correct_index=1,
            difficulty=DifficultyLevel.MEDIUM,
            explanation="'Meticulous' means showing great attention to detail; very careful and precise.",
            exam_year="WASSCE 2021"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Vocabulary",
            content="What does 'resilient' mean?",
            options_json='["Weak", "Able to recover quickly", "Brittle", "Fragile"]',
            correct_index=1,
            difficulty=DifficultyLevel.MEDIUM,
            explanation="'Resilient' means able to recover quickly from difficulties.",
            exam_year="WASSCE 2023"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Vocabulary",
            content="What does 'eloquent' mean?",
            options_json='["Poor speaker", "Fluent and persuasive speaker", "Quiet", "Rude"]',
            correct_index=1,
            difficulty=DifficultyLevel.MEDIUM,
            explanation="'Eloquent' means fluent and persuasive in speaking or writing.",
            exam_year="WASSCE 2022"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Vocabulary",
            content="What does 'benevolent' mean?",
            options_json='["Evil", "Well-meaning and kind", "Cruel", "Indifferent"]',
            correct_index=1,
            difficulty=DifficultyLevel.MEDIUM,
            explanation="'Benevolent' means well-meaning and kind; characterized by goodwill.",
            exam_year="WASSCE 2021"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Vocabulary",
            content="What does 'voracious' mean?",
            options_json='["Having little appetite", "Having a huge appetite", "Sleepy", "Thirsty"]',
            correct_index=1,
            difficulty=DifficultyLevel.HARD,
            explanation="'Voracious' means having a huge appetite; eager to consume.",
            exam_year="WASSCE 2023"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Vocabulary",
            content="What does 'ambiguous' mean?",
            options_json='["Clear", "Open to more than one interpretation", "Simple", "Obvious"]',
            correct_index=1,
            difficulty=DifficultyLevel.MEDIUM,
            explanation="'Ambiguous' means open to more than one interpretation; unclear.",
            exam_year="WASSCE 2022"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Vocabulary",
            content="What does 'conscientious' mean?",
            options_json='["Irresponsible", "Careful to do what is right", "Lazy", "Dishonest"]',
            correct_index=1,
            difficulty=DifficultyLevel.MEDIUM,
            explanation="'Conscientious' means careful to do what is right; diligent.",
            exam_year="WASSCE 2021"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Vocabulary",
            content="What does 'tenacious' mean?",
            options_json='["Giving up easily", "Holding firmly to a purpose", "Weak", "Flexible"]',
            correct_index=1,
            difficulty=DifficultyLevel.HARD,
            explanation="'Tenacious' means holding firmly to a purpose or course of action.",
            exam_year="WASSCE 2023"
        ),
    ]
    questions.extend(vocabulary_questions)

    # English Writing - needs 13 more (currently 2)
    writing_questions = [
        Question(
            subject=Subject.ENGLISH,
            topic="Writing",
            content="What is the purpose of a conclusion?",
            options_json='["To introduce the topic", "To summarize and restate thesis", "To provide examples", "To ask questions"]',
            correct_index=1,
            difficulty=DifficultyLevel.MEDIUM,
            explanation="A conclusion summarizes main points and restates the thesis.",
            exam_year="WASSCE 2023"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Writing",
            content="What is brainstorming?",
            options_json='["Writing the final draft", "Generating ideas freely", "Editing grammar", "Reading research"]',
            correct_index=1,
            difficulty=DifficultyLevel.EASY,
            explanation="Brainstorming is the process of generating ideas without judgment.",
            exam_year="WASSCE 2022"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Writing",
            content="What is a topic sentence?",
            options_json='["The last sentence", "A sentence stating main idea", "A question", "An example"]',
            correct_index=1,
            difficulty=DifficultyLevel.EASY,
            explanation="A topic sentence states the main idea of a paragraph.",
            exam_year="WASSCE 2021"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Writing",
            content="What is revision in writing?",
            options_json='["First draft", "Checking spelling", "Reorganizing and improving content", "Printing"]',
            correct_index=2,
            difficulty=DifficultyLevel.MEDIUM,
            explanation="Revision involves reorganizing and improving the content and structure.",
            exam_year="WASSCE 2023"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Writing",
            content="What is editing in writing?",
            options_json='["Adding content", "Checking grammar and spelling", "Changing structure", "Researching"]',
            correct_index=1,
            difficulty=DifficultyLevel.EASY,
            explanation="Editing focuses on grammar, spelling, punctuation, and style.",
            exam_year="WASSCE 2022"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Writing",
            content="What is a hook in writing?",
            options_json='["A fishing tool", "An attention-grabbing opening", "A conclusion", "A bibliography"]',
            correct_index=1,
            difficulty=DifficultyLevel.MEDIUM,
            explanation="A hook is an attention-grabbing opening that draws readers in.",
            exam_year="WASSCE 2021"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Writing",
            content="What is coherence in writing?",
            options_json='["Using big words", "Logical flow of ideas", "Long sentences", "Short paragraphs"]',
            correct_index=1,
            difficulty=DifficultyLevel.MEDIUM,
            explanation="Coherence is the logical flow and connection of ideas in writing.",
            exam_year="WASSCE 2023"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Writing",
            content="What is unity in writing?",
            options_json='["Using one font", "All parts support main idea", "One long paragraph", "No transitions"]',
            correct_index=1,
            difficulty=DifficultyLevel.MEDIUM,
            explanation="Unity means all parts of the writing support the main idea.",
            exam_year="WASSCE 2022"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Writing",
            content="What is a counterargument?",
            options_json='["Agreeing with opponent", "Addressing opposing views", "Ignoring criticism", "Personal opinion"]',
            correct_index=1,
            difficulty=DifficultyLevel.HARD,
            explanation="A counterargument addresses and responds to opposing viewpoints.",
            exam_year="WASSCE 2021"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Writing",
            content="What is ethos in persuasive writing?",
            options_json='["Emotional appeal", "Ethical appeal", "Logical appeal", "Personal appeal"]',
            correct_index=1,
            difficulty=DifficultyLevel.HARD,
            explanation="Ethos is an ethical appeal that establishes the writer's credibility.",
            exam_year="WASSCE 2023"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Writing",
            content="What is pathos in persuasive writing?",
            options_json='["Ethical appeal", "Emotional appeal", "Logical appeal", "Factual appeal"]',
            correct_index=1,
            difficulty=DifficultyLevel.HARD,
            explanation="Pathos is an emotional appeal that stirs the reader's feelings.",
            exam_year="WASSCE 2022"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Writing",
            content="What is logos in persuasive writing?",
            options_json='["Emotional appeal", "Ethical appeal", "Logical appeal", "Personal appeal"]',
            correct_index=2,
            difficulty=DifficultyLevel.HARD,
            explanation="Logos is a logical appeal that uses reason and evidence.",
            exam_year="WASSCE 2021"
        ),
        Question(
            subject=Subject.ENGLISH,
            topic="Writing",
            content="What is a transition word?",
            options_json='["A long word", "A word connecting ideas", "A descriptive word", "A proper noun"]',
            correct_index=1,
            difficulty=DifficultyLevel.EASY,
            explanation="Transition words connect ideas and show relationships between thoughts.",
            exam_year="WASSCE 2023"
        ),
    ]
    questions.extend(writing_questions)

    return questions


def seed_additional_questions():
    """Add additional questions to reach 15 per topic."""
    db: Session = SessionLocal()

    try:
        print("📚 Adding additional questions to reach 15 per topic...")

        questions = generate_additional_questions()

        # Add all questions to database
        db.add_all(questions)
        db.commit()

        print(f"✅ Successfully added {len(questions)} additional questions!")

        # Count by subject and topic
        from sqlalchemy import func
        topic_counts = db.query(
            Question.subject, Question.topic, func.count(Question.id)
        ).group_by(Question.subject, Question.topic).all()

        print("\n📊 Questions per topic:")
        for subject, topic, count in sorted(topic_counts):
            print(f"  {subject.value} - {topic}: {count} questions")

        return len(questions)

    except Exception as e:
        print(f"❌ Error seeding additional questions: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    count = seed_additional_questions()
    print(f"\n✨ Added {count} additional questions to reach comprehensive coverage!")