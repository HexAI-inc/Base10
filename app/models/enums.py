"""Centralized Enums for the Base10 platform to ensure strict data integrity."""
import enum

class Subject(str, enum.Enum):
    """WAEC subjects."""
    MATHEMATICS = "Mathematics"
    ENGLISH = "English Language"
    PHYSICS = "Physics"
    CHEMISTRY = "Chemistry"
    BIOLOGY = "Biology"
    ECONOMICS = "Economics"
    GEOGRAPHY = "Geography"
    GOVERNMENT = "Government"
    CIVIC_EDUCATION = "Civic Education"
    FINANCIAL_ACCOUNTING = "Financial Accounting"
    AGRICULTURAL_SCIENCE = "Agricultural Science"
    COMMERCE = "Commerce"
    LITERATURE_IN_ENGLISH = "Literature in English"

class DifficultyLevel(str, enum.Enum):
    """Question difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class GradeLevel(str, enum.Enum):
    """Educational grade levels."""
    JSS1 = "JSS1"
    JSS2 = "JSS2"
    JSS3 = "JSS3"
    SS1 = "SS1"
    SS2 = "SS2"
    SS3 = "SS3"
    UNIVERSITY = "University"
    OTHER = "Other"

class AssignmentType(str, enum.Enum):
    """Types of assignments."""
    QUIZ = "quiz"
    MANUAL = "manual"
    ESSAY = "essay"
    PRACTICE = "practice"

class AssignmentStatus(str, enum.Enum):
    """Status of an assignment."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    COMPLETED = "completed"

class PostType(str, enum.Enum):
    """Types of classroom stream posts."""
    ANNOUNCEMENT = "announcement"
    DISCUSSION = "discussion"
    ASSIGNMENT_ALERT = "assignment_alert"
    COMMENT = "comment"
    RESOURCE = "resource"

class ReportStatus(str, enum.Enum):
    """Status of a content report."""
    PENDING = "pending"
    REVIEWED = "reviewed"
    FIXED = "fixed"
    DISMISSED = "dismissed"

class ReportReason(str, enum.Enum):
    """Predefined report reasons for consistency."""
    WRONG_ANSWER = "Wrong Answer"
    TYPO = "Typo"
    UNCLEAR_QUESTION = "Unclear Question"
    MISSING_DIAGRAM = "Missing Diagram"
    OUTDATED_CONTENT = "Outdated Content"
    OTHER = "Other"

class Topic(str, enum.Enum):
    """
    Comprehensive list of WAEC topics.
    This ensures strict input and accurate dropdowns in the UI.
    """
    # Mathematics
    ALGEBRA = "Algebra"
    GEOMETRY = "Geometry"
    TRIGONOMETRY = "Trigonometry"
    STATISTICS = "Statistics"
    PROBABILITY = "Probability"
    CALCULUS = "Calculus"
    NUMBER_BASES = "Number Bases"
    SETS = "Sets"
    LOGARITHMS = "Logarithms"
    
    # English
    GRAMMAR = "Grammar"
    COMPREHENSION = "Comprehension"
    VOCABULARY = "Vocabulary"
    ORAL_ENGLISH = "Oral English"
    WRITING = "Writing"
    
    # Physics
    MECHANICS = "Mechanics"
    THERMAL_PHYSICS = "Thermal Physics"
    WAVES = "Waves"
    ELECTRICITY = "Electricity"
    MAGNETISM = "Magnetism"
    ATOMIC_PHYSICS = "Atomic Physics"
    OPTICS = "Optics"
    
    # Chemistry
    ATOMIC_STRUCTURE = "Atomic Structure"
    CHEMICAL_BONDING = "Chemical Bonding"
    STOICHIOMETRY = "Stoichiometry"
    STATES_OF_MATTER = "States of Matter"
    PERIODIC_TABLE = "Periodic Table"
    ORGANIC_CHEMISTRY = "Organic Chemistry"
    ELECTROCHEMISTRY = "Electrochemistry"
    
    # Biology
    CELL_BIOLOGY = "Cell Biology"
    GENETICS = "Genetics"
    ECOLOGY = "Ecology"
    PHYSIOLOGY = "Physiology"
    EVOLUTION = "Evolution"
    CLASSIFICATION = "Classification"
    
    # General/Other
    GENERAL = "General"
    OTHER = "Other"
