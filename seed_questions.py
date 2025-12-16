"""
Simple script to seed questions into the database.
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.question import Question, Subject, DifficultyLevel


def seed_questions():
    """Add sample Mathematics questions to the database."""
    db: Session = SessionLocal()
    
    try:
        print("📚 Seeding Mathematics questions...")
        
        questions = [
            # Algebra Questions (15 questions)
            Question(
                subject=Subject.MATHEMATICS,
                topic="Algebra",
                content="Solve for x: 2x + 5 = 15",
                options_json='["x = 5", "x = 10", "x = 7.5", "x = 20"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="2x = 15 - 5 = 10, so x = 5",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Algebra",
                content="Factor: x² - 9",
                options_json='["(x-3)(x+3)", "(x-9)(x+1)", "x(x-9)", "(x-3)²"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Difference of squares: a² - b² = (a-b)(a+b)",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Algebra",
                content="Simplify: 3(x + 4) - 2(x - 1)",
                options_json='["x + 14", "x + 10", "5x + 14", "x + 12"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="3x + 12 - 2x + 2 = x + 14",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Algebra",
                content="If 3x - 7 = 14, what is x?",
                options_json='["7", "5", "14", "21"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="3x = 14 + 7 = 21, so x = 7",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Algebra",
                content="Expand: (x + 3)(x - 2)",
                options_json='["x² + x - 6", "x² - x - 6", "x² + 5x - 6", "x² - 5x + 6"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="x² - 2x + 3x - 6 = x² + x - 6",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Algebra",
                content="Solve: x² - 5x + 6 = 0",
                options_json='["x = 2 or x = 3", "x = -2 or x = -3", "x = 1 or x = 6", "x = -1 or x = -6"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Factor: (x-2)(x-3) = 0, so x = 2 or x = 3",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Algebra",
                content="If y = 2x + 3, what is y when x = 4?",
                options_json='["11", "10", "8", "9"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="y = 2(4) + 3 = 8 + 3 = 11",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Algebra",
                content="Simplify: (2x³)(3x²)",
                options_json='["6x⁵", "6x⁶", "5x⁵", "6x"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Multiply coefficients and add exponents: 2×3 = 6, x³×x² = x⁵",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Algebra",
                content="What is the slope of the line y = 3x - 7?",
                options_json='["3", "-7", "7", "-3"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="In y = mx + b form, m is the slope. Here m = 3",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Algebra",
                content="Factor completely: 2x² + 8x",
                options_json='["2x(x + 4)", "2(x² + 4x)", "x(2x + 8)", "2x² + 8x"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Factor out the GCF: 2x(x + 4)",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Algebra",
                content="Solve for x: x/3 + 2 = 5",
                options_json='["9", "3", "21", "15"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="x/3 = 5 - 2 = 3, so x = 9",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Algebra",
                content="If f(x) = x² + 2x, what is f(3)?",
                options_json='["15", "11", "9", "12"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="f(3) = 3² + 2(3) = 9 + 6 = 15",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Algebra",
                content="Simplify: (x + 2)²",
                options_json='["x² + 4x + 4", "x² + 4", "x² + 2x + 4", "x² + 4x + 2"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="(x + 2)² = (x + 2)(x + 2) = x² + 2x + 2x + 4 = x² + 4x + 4",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Algebra",
                content="What is the y-intercept of y = 2x + 5?",
                options_json='["5", "2", "-5", "0"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="In y = mx + b form, b is the y-intercept. Here b = 5",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Algebra",
                content="Solve: 2(x - 3) = 10",
                options_json='["8", "5", "6.5", "11"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="2x - 6 = 10, so 2x = 16, x = 8",
                exam_year="WASSCE 2022"
            ),
            
            # Geometry Questions (15 questions)
            Question(
                subject=Subject.MATHEMATICS,
                topic="Geometry",
                content="What is the area of a circle with radius 7 cm?",
                options_json='["49π cm²", "14π cm²", "7π cm²", "98π cm²"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="A = πr² = π(7)² = 49π cm²",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Geometry",
                content="In a right triangle, if a² + b² = c², what is c called?",
                options_json='["Hypotenuse", "Adjacent", "Opposite", "Base"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="In the Pythagorean theorem, c is the hypotenuse",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Geometry",
                content="What is the sum of interior angles in a triangle?",
                options_json='["180°", "360°", "90°", "270°"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="The sum of all interior angles in any triangle is always 180°",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Geometry",
                content="What is the perimeter of a rectangle with length 8 cm and width 5 cm?",
                options_json='["26 cm", "40 cm", "13 cm", "18 cm"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="P = 2(l + w) = 2(8 + 5) = 2(13) = 26 cm",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Geometry",
                content="What is the volume of a cube with side length 4 cm?",
                options_json='["64 cm³", "16 cm³", "48 cm³", "12 cm³"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="V = s³ = 4³ = 64 cm³",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Geometry",
                content="What is the circumference of a circle with diameter 10 cm?",
                options_json='["10π cm", "20π cm", "5π cm", "100π cm"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="C = πd = π(10) = 10π cm",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Geometry",
                content="What is the area of a triangle with base 6 cm and height 8 cm?",
                options_json='["24 cm²", "48 cm²", "14 cm²", "12 cm²"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="A = (1/2)bh = (1/2)(6)(8) = 24 cm²",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Geometry",
                content="How many sides does a hexagon have?",
                options_json='["6", "5", "7", "8"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="A hexagon has 6 sides by definition",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Geometry",
                content="What is the sum of interior angles of a quadrilateral?",
                options_json='["360°", "180°", "540°", "270°"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Sum = (n-2) × 180° = (4-2) × 180° = 360°",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Geometry",
                content="What is the area of a square with side 9 cm?",
                options_json='["81 cm²", "36 cm²", "18 cm²", "9 cm²"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="A = s² = 9² = 81 cm²",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Geometry",
                content="If a triangle has sides 3, 4, and 5, what type of triangle is it?",
                options_json='["Right triangle", "Equilateral", "Isosceles", "Obtuse"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="3² + 4² = 9 + 16 = 25 = 5², so it's a right triangle",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Geometry",
                content="What is the volume of a rectangular prism with length 5, width 3, and height 2?",
                options_json='["30 cubic units", "10 cubic units", "15 cubic units", "16 cubic units"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="V = l × w × h = 5 × 3 × 2 = 30",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Geometry",
                content="What is the diagonal of a square with side 5 cm?",
                options_json='["5√2 cm", "10 cm", "5 cm", "25 cm"]',
                correct_index=0,
                difficulty=DifficultyLevel.HARD,
                explanation="Using Pythagorean theorem: d² = 5² + 5² = 50, so d = √50 = 5√2",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Geometry",
                content="How many degrees are in each interior angle of a regular pentagon?",
                options_json='["108°", "120°", "72°", "90°"]',
                correct_index=0,
                difficulty=DifficultyLevel.HARD,
                explanation="Each angle = [(n-2) × 180°]/n = [(5-2) × 180°]/5 = 540°/5 = 108°",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Geometry",
                content="What is the surface area of a cube with side 3 cm?",
                options_json='["54 cm²", "27 cm²", "18 cm²", "9 cm²"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="SA = 6s² = 6(3)² = 6(9) = 54 cm²",
                exam_year="WASSCE 2021"
            ),
            
            # Trigonometry Questions (10 questions)
            Question(
                subject=Subject.MATHEMATICS,
                topic="Trigonometry",
                content="What is the fundamental trigonometric identity?",
                options_json='["sin²θ + cos²θ = 1", "sin²θ - cos²θ = 1", "sinθ + cosθ = 1", "tanθ = 1"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="This is the most fundamental identity in trigonometry",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Trigonometry",
                content="If sin(30°) = 0.5, what is cos(60°)?",
                options_json='["0.5", "0.866", "1", "0"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="sin(30°) = cos(90° - 30°) = cos(60°) = 0.5",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Trigonometry",
                content="What is tan(θ) equal to?",
                options_json='["sin(θ)/cos(θ)", "cos(θ)/sin(θ)", "sin(θ) × cos(θ)", "sin(θ) + cos(θ)"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="By definition, tan(θ) = sin(θ)/cos(θ)",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Trigonometry",
                content="What is sin(90°)?",
                options_json='["1", "0", "0.5", "√2/2"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="sin(90°) = 1 by definition",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Trigonometry",
                content="What is cos(0°)?",
                options_json='["1", "0", "0.5", "-1"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="cos(0°) = 1 by definition",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Trigonometry",
                content="If tan(45°) = 1, what is sin(45°)?",
                options_json='["√2/2", "1", "1/2", "√3/2"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="sin(45°) = cos(45°) = √2/2 ≈ 0.707",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Trigonometry",
                content="What is the period of sin(x)?",
                options_json='["2π", "π", "π/2", "4π"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="The sine function repeats every 2π radians (360°)",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Trigonometry",
                content="What is sec(θ) equal to?",
                options_json='["1/cos(θ)", "1/sin(θ)", "cos(θ)", "sin(θ)/cos(θ)"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="sec(θ) is the reciprocal of cos(θ)",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Trigonometry",
                content="In a right triangle, if the opposite side is 3 and the hypotenuse is 5, what is sin(θ)?",
                options_json='["3/5", "4/5", "3/4", "5/3"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="sin(θ) = opposite/hypotenuse = 3/5",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Trigonometry",
                content="What is the range of the cosine function?",
                options_json='["[-1, 1]", "[0, 1]", "[-∞, ∞]", "[0, π]"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="The cosine function outputs values between -1 and 1 inclusive",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Trigonometry",
                content="Solve: sin(x) = 0.5 for x in [0, π]",
                options_json='["π/6", "π/3", "π/4", "π/2"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="sin(π/6) = 0.5",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Trigonometry",
                content="What is tan(θ) in terms of sin(θ) and cos(θ)?",
                options_json='["sin(θ)/cos(θ)", "sin(θ) × cos(θ)", "sin²(θ) + cos²(θ)", "1/sin(θ)"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="tan(θ) = sin(θ)/cos(θ)",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Trigonometry",
                content="What is the period of tan(x)?",
                options_json='["π", "2π", "π/2", "4π"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="The tangent function has a period of π",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Trigonometry",
                content="In a right triangle, if cos(θ) = 4/5, what is sin(θ)?",
                options_json='["3/5", "4/5", "5/4", "3/4"]',
                correct_index=0,
                difficulty=DifficultyLevel.HARD,
                explanation="Using Pythagoras: sin²(θ) + cos²(θ) = 1, so sin(θ) = √(1 - (4/5)²) = 3/5",
                exam_year="WASSCE 2022"
            ),
            
            # Number Theory (10 questions)
            Question(
                subject=Subject.MATHEMATICS,
                topic="Number Theory",
                content="What is the least common multiple (LCM) of 12 and 18?",
                options_json='["36", "6", "72", "24"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Prime factorization: 12 = 2² × 3, 18 = 2 × 3². LCM = 2² × 3² = 36",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Number Theory",
                content="What is the greatest common divisor (GCD) of 48 and 60?",
                options_json='["12", "6", "24", "4"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Prime factorization: 48 = 2⁴ × 3, 60 = 2² × 3 × 5. GCD = 2² × 3 = 12",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Number Theory",
                content="Which of the following is a prime number?",
                options_json='["17", "15", "21", "27"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="17 has only two divisors: 1 and 17, making it prime",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Number Theory",
                content="What is the sum of the first 10 positive integers?",
                options_json='["55", "45", "50", "60"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="1+2+3+...+10 = n(n+1)/2 = 10(11)/2 = 55",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Number Theory",
                content="How many prime numbers are there between 1 and 10?",
                options_json='["4", "3", "5", "6"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="The primes between 1 and 10 are: 2, 3, 5, 7",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Number Theory",
                content="What is the LCM of 4, 6, and 8?",
                options_json='["24", "12", "48", "16"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="4 = 2², 6 = 2×3, 8 = 2³. LCM = 2³×3 = 24",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Number Theory",
                content="Which number is divisible by both 3 and 4?",
                options_json='["24", "18", "20", "15"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="24 ÷ 3 = 8 and 24 ÷ 4 = 6, both with no remainder",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Number Theory",
                content="What is 7! (7 factorial)?",
                options_json='["5040", "720", "5000", "840"]',
                correct_index=0,
                difficulty=DifficultyLevel.HARD,
                explanation="7! = 7×6×5×4×3×2×1 = 5040",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Number Theory",
                content="What is the next prime number after 11?",
                options_json='["13", "12", "15", "14"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="13 is the next number after 11 that is only divisible by 1 and itself",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Number Theory",
                content="How many factors does 36 have?",
                options_json='["9", "6", "8", "12"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="The factors of 36 are: 1, 2, 3, 4, 6, 9, 12, 18, 36",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Number Theory",
                content="What is the greatest common divisor (GCD) of 24 and 36?",
                options_json='["12", "6", "24", "36"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="GCD(24, 36) = 12",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Number Theory",
                content="Is 29 a prime number?",
                options_json='["Yes", "No", "Composite", "Even"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="29 is a prime number (only divisible by 1 and itself)",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Number Theory",
                content="What is 2³ × 3² in expanded form?",
                options_json='["8 × 9", "6 × 8", "9 × 6", "8 × 6"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="2³ = 8, 3² = 9, so 8 × 9 = 72",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Number Theory",
                content="What is the prime factorization of 60?",
                options_json='["2² × 3 × 5", "2 × 3² × 5", "2³ × 5", "2² × 5²"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="60 = 2² × 3 × 5",
                exam_year="WASSCE 2022"
            ),
            
            # Statistics (10 questions)
            Question(
                subject=Subject.MATHEMATICS,
                topic="Statistics",
                content="What is the mean of the numbers: 2, 4, 6, 8, 10?",
                options_json='["6", "5", "7", "8"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="Mean = (2 + 4 + 6 + 8 + 10) / 5 = 30 / 5 = 6",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Statistics",
                content="What is the median of: 3, 7, 9, 15, 21?",
                options_json='["9", "11", "7", "15"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="The median is the middle value when numbers are arranged in order: 9",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Statistics",
                content="What is the mode of: 2, 3, 3, 4, 5, 5, 5, 6?",
                options_json='["5", "3", "4", "6"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="The mode is the most frequently occurring value: 5 appears 3 times",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Statistics",
                content="What is the range of: 12, 5, 8, 19, 3?",
                options_json='["16", "12", "19", "8"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="Range = Maximum - Minimum = 19 - 3 = 16",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Statistics",
                content="If the mean of 5, 7, 9, and x is 8, what is x?",
                options_json='["11", "8", "10", "12"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="(5 + 7 + 9 + x)/4 = 8, so 21 + x = 32, x = 11",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Statistics",
                content="What is the median of: 4, 8, 12, 16?",
                options_json='["10", "8", "12", "9"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="For even number of values, median = (8 + 12)/2 = 10",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Statistics",
                content="The mean of 6 numbers is 15. What is their sum?",
                options_json='["90", "21", "15", "75"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Mean = Sum/n, so Sum = Mean × n = 15 × 6 = 90",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Statistics",
                content="What type of average is affected most by extreme values?",
                options_json='["Mean", "Median", "Mode", "Range"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="The mean is most affected by outliers/extreme values",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Statistics",
                content="In the data set: 1, 2, 2, 3, 4, what is the mean?",
                options_json='["2.4", "2", "3", "2.5"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="Mean = (1 + 2 + 2 + 3 + 4)/5 = 12/5 = 2.4",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Statistics",
                content="If all values in a data set are the same, what are the mean, median, and mode?",
                options_json='["All equal to that value", "Mean only", "Cannot be determined", "Mode only"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="If all values are identical, mean = median = mode = that value",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Statistics",
                content="What is the range of the data: 5, 8, 12, 15, 20?",
                options_json='["15", "10", "20", "8"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="Range = maximum - minimum = 20 - 5 = 15",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Statistics",
                content="In a normal distribution, what percentage of data falls within 1 standard deviation?",
                options_json='["68%", "95%", "99.7%", "50%"]',
                correct_index=0,
                difficulty=DifficultyLevel.HARD,
                explanation="In a normal distribution, approximately 68% of data falls within 1 standard deviation of the mean",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Statistics",
                content="What is the median of: 3, 7, 9, 12, 15?",
                options_json='["9", "7", "12", "15"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="For odd number of values, median is the middle value: 9",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Statistics",
                content="What does the standard deviation measure?",
                options_json='["Spread of data", "Average value", "Middle value", "Most frequent value"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Standard deviation measures the spread or dispersion of data points around the mean",
                exam_year="WASSCE 2022"
            ),
            
            # Calculus Basics (10 questions)
            Question(
                subject=Subject.MATHEMATICS,
                topic="Calculus",
                content="What is the derivative of x²?",
                options_json='["2x", "x²", "x", "2"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Using the power rule: d/dx(x²) = 2x",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Calculus",
                content="What is the integral of 2x?",
                options_json='["x² + C", "2x² + C", "x + C", "2 + C"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="∫2x dx = x² + C (constant of integration)",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Calculus",
                content="What is the derivative of a constant?",
                options_json='["0", "1", "The constant itself", "Cannot be determined"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="The derivative of any constant is always 0",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Calculus",
                content="What is the derivative of 3x³?",
                options_json='["9x²", "3x²", "6x³", "x³"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Using power rule: d/dx(3x³) = 3 × 3x² = 9x²",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Calculus",
                content="What is the integral of 1 dx?",
                options_json='["x + C", "1 + C", "0", "x"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="∫1 dx = x + C",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Calculus",
                content="What is d/dx(x)?",
                options_json='["1", "0", "x", "x²"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="The derivative of x with respect to x is 1",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Calculus",
                content="What is the derivative of x⁴ - 3x²?",
                options_json='["4x³ - 6x", "4x³ - 3x", "x³ - 6x", "4x⁴ - 6x²"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="d/dx(x⁴) - d/dx(3x²) = 4x³ - 6x",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Calculus",
                content="What does the derivative represent?",
                options_json='["Rate of change", "Area under curve", "Maximum value", "Average value"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="The derivative represents the instantaneous rate of change",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Calculus",
                content="What is ∫3x² dx?",
                options_json='["x³ + C", "3x³ + C", "6x + C", "x² + C"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="∫3x² dx = 3(x³/3) + C = x³ + C",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Calculus",
                content="If f(x) = 5x, what is f'(x)?",
                options_json='["5", "5x", "x", "0"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="The derivative of 5x is 5",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Calculus",
                content="What is the derivative of sin(x)?",
                options_json='["cos(x)", "-sin(x)", "tan(x)", "sec(x)"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="d/dx[sin(x)] = cos(x)",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Calculus",
                content="What is the derivative of cos(x)?",
                options_json='["-sin(x)", "sin(x)", "-cos(x)", "tan(x)"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="d/dx[cos(x)] = -sin(x)",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Calculus",
                content="Evaluate ∫(2x + 3) dx",
                options_json='["x² + 3x + C", "x² + C", "2x² + 3x + C", "x² + 3"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="∫(2x + 3) dx = 2(x²/2) + 3x + C = x² + 3x + C",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Calculus",
                content="What is the integral of e^x?",
                options_json='["e^x + C", "e^x", "x e^x + C", "ln(x) + C"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="∫e^x dx = e^x + C",
                exam_year="WASSCE 2022"
            ),
            
            # Probability (10 questions)
            Question(
                subject=Subject.MATHEMATICS,
                topic="Probability",
                content="What is the probability of getting heads when flipping a fair coin?",
                options_json='["1/2", "1/4", "1", "0"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="A fair coin has 2 equally likely outcomes: heads or tails. P(heads) = 1/2",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Probability",
                content="What is the probability of rolling a 6 on a fair die?",
                options_json='["1/6", "1/2", "1/3", "6"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="A die has 6 equally likely outcomes, so P(6) = 1/6",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Probability",
                content="If you draw a card from a standard deck, what is the probability it's a heart?",
                options_json='["1/4", "1/13", "1/2", "4/52"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="There are 13 hearts in a 52-card deck: 13/52 = 1/4",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Probability",
                content="What is the probability of an impossible event?",
                options_json='["0", "1", "1/2", "Cannot be determined"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="An impossible event has probability 0",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Probability",
                content="What is the probability of a certain event?",
                options_json='["1", "0", "1/2", "100"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="A certain event has probability 1",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Probability",
                content="If P(A) = 0.3, what is P(not A)?",
                options_json='["0.7", "0.3", "1", "0"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="P(not A) = 1 - P(A) = 1 - 0.3 = 0.7",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Probability",
                content="What is the probability of rolling an even number on a fair die?",
                options_json='["1/2", "1/3", "2/3", "1/6"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="Even numbers are 2, 4, 6. That's 3 out of 6 outcomes: 3/6 = 1/2",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Probability",
                content="If you flip two coins, what is the probability of getting two heads?",
                options_json='["1/4", "1/2", "1/3", "2/4"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Outcomes: HH, HT, TH, TT. P(HH) = 1/4",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Probability",
                content="What is the sum of all probabilities in a probability distribution?",
                options_json='["1", "0", "100", "Depends on events"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="The sum of all probabilities must equal 1",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Probability",
                content="In a bag with 3 red and 2 blue marbles, what is P(red)?",
                options_json='["3/5", "2/5", "1/2", "3/2"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Total marbles = 5, red marbles = 3, so P(red) = 3/5",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Probability",
                content="What is the probability of rolling a 6 on a fair die?",
                options_json='["1/6", "1/2", "1/3", "1/4"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="A die has 6 faces, so P(6) = 1/6",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Probability",
                content="If P(A) = 0.3 and P(B) = 0.4, what is the maximum P(A and B)?",
                options_json='["0.3", "0.4", "0.7", "0.12"]',
                correct_index=0,
                difficulty=DifficultyLevel.HARD,
                explanation="P(A and B) ≤ min(P(A), P(B)) = 0.3",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Probability",
                content="What is the probability of drawing an ace from a deck of 52 cards?",
                options_json='["1/13", "1/4", "1/52", "4/52"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="There are 4 aces in a deck of 52 cards, so P(ace) = 4/52 = 1/13",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Probability",
                content="If two events are mutually exclusive, P(A or B) = ?",
                options_json='["P(A) + P(B)", "P(A) × P(B)", "P(A) - P(B)", "P(A) ÷ P(B)"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="For mutually exclusive events, P(A or B) = P(A) + P(B)",
                exam_year="WASSCE 2023"
            ),
            
            # Fractions and Decimals (10 questions)
            Question(
                subject=Subject.MATHEMATICS,
                topic="Fractions",
                content="What is 1/2 + 1/4?",
                options_json='["3/4", "2/6", "1/3", "2/4"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="1/2 = 2/4, so 2/4 + 1/4 = 3/4",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Fractions",
                content="What is 3/5 × 2/3?",
                options_json='["2/5", "5/8", "6/15", "1"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="(3×2)/(5×3) = 6/15 = 2/5",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Fractions",
                content="What is 0.75 as a fraction?",
                options_json='["3/4", "7/5", "75/100", "15/20"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="0.75 = 75/100 = 3/4 in simplest form",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Fractions",
                content="What is 1/2 ÷ 1/4?",
                options_json='["2", "1/8", "1/6", "4"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="1/2 ÷ 1/4 = 1/2 × 4/1 = 4/2 = 2",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Fractions",
                content="Simplify: 8/12",
                options_json='["2/3", "4/6", "8/12", "1/2"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="Divide both by GCD(8,12) = 4: 8÷4 / 12÷4 = 2/3",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Fractions",
                content="What is 2/3 - 1/6?",
                options_json='["1/2", "1/3", "2/6", "1/6"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="2/3 = 4/6, so 4/6 - 1/6 = 3/6 = 1/2",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Fractions",
                content="What is 1.5 as a fraction?",
                options_json='["3/2", "15/10", "5/3", "1/5"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="1.5 = 15/10 = 3/2 in simplest form",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Fractions",
                content="What is 5/8 as a decimal?",
                options_json='["0.625", "0.58", "0.5", "0.8"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="5 ÷ 8 = 0.625",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Fractions",
                content="What is 2 1/2 + 1 1/4?",
                options_json='["3 3/4", "3 1/2", "4", "3 1/4"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="2 1/2 = 2 2/4, so 2 2/4 + 1 1/4 = 3 3/4",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Fractions",
                content="What is the reciprocal of 3/5?",
                options_json='["5/3", "3/5", "15", "1/15"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="The reciprocal of a/b is b/a, so reciprocal of 3/5 is 5/3",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Fractions",
                content="Simplify 12/18 to lowest terms",
                options_json='["2/3", "1/2", "3/4", "4/6"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="Divide numerator and denominator by 6: 12÷6=2, 18÷6=3, so 2/3",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Fractions",
                content="What is 3/4 ÷ 2/5?",
                options_json='["15/8", "8/15", "6/20", "5/6"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Division of fractions: (3/4) ÷ (2/5) = (3/4) × (5/2) = 15/8",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Fractions",
                content="Convert 0.75 to a fraction",
                options_json='["3/4", "1/4", "1/2", "2/3"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="0.75 = 75/100 = 3/4",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.MATHEMATICS,
                topic="Fractions",
                content="What is 5/8 as a decimal?",
                options_json='["0.625", "0.5", "0.875", "0.125"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="5 ÷ 8 = 0.625",
                exam_year="WASSCE 2022"
            ),
            
            # English Questions (15 questions)
            Question(
                subject=Subject.ENGLISH,
                topic="Grammar",
                content="Which of the following is a noun?",
                options_json='["Run", "Beautiful", "Table", "Quickly"]',
                correct_index=2,
                difficulty=DifficultyLevel.EASY,
                explanation="A noun is a person, place, thing, or idea. 'Table' is a thing.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Grammar",
                content="What is the past tense of 'go'?",
                options_json='["Went", "Gone", "Going", "Goes"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="'Went' is the past tense of 'go'.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Grammar",
                content="Which sentence is grammatically correct?",
                options_json="['She don\\'t like apples', 'She doesn\\'t likes apples', 'She doesn\\'t like apples', 'She don\\'t likes apples']",
                correct_index=2,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="'She doesn't like apples' is correct - subject-verb agreement with 'doesn't'.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Grammar",
                content="What is an adjective?",
                options_json='["A describing word", "An action word", "A naming word", "A connecting word"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="An adjective describes or modifies a noun or pronoun.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Grammar",
                content="Which word is a synonym for 'happy'?",
                options_json='["Sad", "Joyful", "Angry", "Tired"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="'Joyful' means the same as 'happy'.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Literature",
                content="Who wrote 'Romeo and Juliet'?",
                options_json='["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="William Shakespeare wrote the tragedy 'Romeo and Juliet'.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Literature",
                content="What is a metaphor?",
                options_json="['A comparison using \\'like\\' or \\'as\\'', 'A direct comparison without \\'like\\' or \\'as\\'', 'A story about animals', 'A poem with rhyme']",
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="A metaphor is a figure of speech that describes an object or action in a way that isn't literally true.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Comprehension",
                content="What does 'infer' mean in reading comprehension?",
                options_json='["To read quickly", "To guess or conclude from evidence", "To memorize facts", "To write notes"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="To infer means to draw conclusions based on evidence and reasoning.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Vocabulary",
                content="What does 'ubiquitous' mean?",
                options_json='["Rare", "Present everywhere", "Very small", "Extremely large"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="'Ubiquitous' means existing or being everywhere at the same time.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Writing",
                content="What is the main purpose of a thesis statement?",
                options_json='["To introduce the topic", "To state the main argument", "To provide examples", "To conclude the essay"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="A thesis statement states the main argument or claim of an essay.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Grammar",
                content="Which is the correct plural form of 'child'?",
                options_json='["Childs", "Children", "Childes", "Childrens"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="'Children' is the correct plural of 'child'.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Grammar",
                content="What is the past tense of 'run'?",
                options_json='["Runned", "Ran", "Running", "Runs"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="'Ran' is the past tense of 'run'.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Grammar",
                content="Which word is a synonym for 'happy'?",
                options_json='["Sad", "Joyful", "Angry", "Tired"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="'Joyful' means the same as 'happy'.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Grammar",
                content="What is an adjective?",
                options_json='["A naming word", "A describing word", "An action word", "A joining word"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="Adjectives describe or modify nouns.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Grammar",
                content="Which sentence uses correct subject-verb agreement?",
                options_json='["He go to school", "He goes to school", "He going to school", "He gone to school"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="'He goes' shows correct agreement between singular subject and verb.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Grammar",
                content="What is the comparative form of 'good'?",
                options_json='["Gooder", "Better", "Best", "Goodest"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="'Better' is the comparative form of 'good'.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Grammar",
                content="Which is a preposition?",
                options_json='["Run", "Quickly", "In", "Beautiful"]',
                correct_index=2,
                difficulty=DifficultyLevel.EASY,
                explanation="'In' shows relationship between words.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Grammar",
                content="What is the superlative form of 'big'?",
                options_json='["Bigger", "Biggest", "Most big", "Bigly"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="'Biggest' is the superlative form of 'big'.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Grammar",
                content="Which word is an adverb?",
                options_json='["Quick", "Quickly", "Quickness", "Quickly"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="'Quickly' modifies verbs, adjectives, or other adverbs.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Literature",
                content="What is the climax of a story?",
                options_json='["The beginning", "The most exciting part", "The ending", "The introduction"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="The climax is the most intense, exciting, or important point of the story.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Literature",
                content="What is a metaphor?",
                options_json="['A comparison using \\'like\\' or \\'as\\'', 'A direct comparison without \\'like\\' or \\'as\\'', 'A story about animals', 'A poem with rhyme']",
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="A metaphor is a direct comparison between two unlike things.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Literature",
                content="What is the protagonist in a story?",
                options_json='["The main character", "The villain", "The narrator", "The setting"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="The protagonist is the main character or hero of the story.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Literature",
                content="What is foreshadowing?",
                options_json='["\\A hint about future events\\", "\\A description of the past\\", "\\A character\'s thoughts\\", "\\A dialogue between characters\\"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Foreshadowing gives hints about what will happen later in the story.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Literature",
                content="What is the resolution of a story?",
                options_json='["The beginning", "The conflict", "The ending where problems are solved", "The climax"]',
                correct_index=2,
                difficulty=DifficultyLevel.EASY,
                explanation="The resolution is the part where the story's conflicts are resolved.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Literature",
                content="What is personification?",
                options_json='["Giving human qualities to animals", "Giving human qualities to objects", "Describing nature", "Using dialogue"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Personification gives human characteristics to non-human things.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Literature",
                content="What is a simile?",
                options_json='["A direct comparison", "A comparison using like or as", "A type of poem", "A story ending"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="A simile compares two things using 'like' or 'as'.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Literature",
                content="What is the antagonist?",
                options_json='["The hero", "The villain or opposing force", "The narrator", "A minor character"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="The antagonist is the character or force opposing the protagonist.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Literature",
                content="What is irony?",
                options_json='["When something means the opposite of what it says", "A type of rhyme", "A story summary", "Character description"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Irony occurs when the intended meaning is opposite to the literal meaning.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Literature",
                content="What is a soliloquy?",
                options_json='["A conversation between characters", "A speech to oneself", "A description of setting", "A poem"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="A soliloquy is a speech where a character speaks their thoughts aloud.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Literature",
                content="What is the setting of a story?",
                options_json='["The main character", "The time and place", "The plot", "The theme"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="The setting is where and when the story takes place.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Literature",
                content="What is symbolism?",
                options_json='["Using words to create pictures", "Using objects to represent ideas", "Writing in code", "Using metaphors"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Symbolism uses objects or images to represent abstract ideas.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Vocabulary",
                content="What does 'ephemeral' mean?",
                options_json='["Permanent", "Lasting a very short time", "Very heavy", "Extremely bright"]',
                correct_index=1,
                difficulty=DifficultyLevel.HARD,
                explanation="'Ephemeral' means lasting for a very short time.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Comprehension",
                content="What is the author's purpose in writing?",
                options_json='["To entertain only", "To inform, persuade, or entertain", "To confuse readers", "To use big words"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Authors write to inform, persuade, entertain, or express themselves.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.ENGLISH,
                topic="Writing",
                content="What should be included in a conclusion?",
                options_json='["New information", "A restatement of the thesis", "Unrelated facts", "Personal opinions"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="A conclusion should restate the thesis and summarize main points.",
                exam_year="WASSCE 2021"
            ),
            
            # Physics Questions (15 questions)
            Question(
                subject=Subject.PHYSICS,
                topic="Mechanics",
                content="What is the SI unit of force?",
                options_json='["Newton", "Joule", "Watt", "Pascal"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="The Newton (N) is the SI unit of force.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.PHYSICS,
                topic="Mechanics",
                content="According to Newton's first law, an object at rest stays at rest unless...",
                options_json='["It is pushed", "A net force acts on it", "It is heavy", "It is light"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Newton's first law states that an object remains at rest or in uniform motion unless acted upon by a net force.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.PHYSICS,
                topic="Electricity",
                content="What is the unit of electric current?",
                options_json='["Volt", "Ampere", "Ohm", "Watt"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="The Ampere (A) is the SI unit of electric current.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.PHYSICS,
                topic="Electricity",
                content="In a series circuit, if one bulb blows, what happens to the others?",
                options_json='["They get brighter", "They go out", "They stay the same", "They get dimmer"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="In a series circuit, if one component fails, the circuit is broken and all components stop working.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.PHYSICS,
                topic="Optics",
                content="What type of mirror is used in car headlights?",
                options_json='["Plane mirror", "Concave mirror", "Convex mirror", "Spherical mirror"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Concave mirrors are used in car headlights because they converge light rays to produce a strong beam.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.PHYSICS,
                topic="Optics",
                content="What is the speed of light in vacuum?",
                options_json='["3 × 10⁸ m/s", "3 × 10⁶ m/s", "3 × 10¹⁰ m/s", "3 × 10⁴ m/s"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="The speed of light in vacuum is approximately 3 × 10⁸ meters per second.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.PHYSICS,
                topic="Thermodynamics",
                content="What is the boiling point of water at standard atmospheric pressure?",
                options_json='["0°C", "100°C", "50°C", "200°C"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="Water boils at 100°C at standard atmospheric pressure (1 atm).",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.PHYSICS,
                topic="Thermodynamics",
                content="What is the first law of thermodynamics also known as?",
                options_json='["Law of conservation of energy", "Law of entropy", "Law of heat transfer", "Law of temperature"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="The first law of thermodynamics states that energy cannot be created or destroyed, only converted.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.PHYSICS,
                topic="Waves",
                content="What type of wave is sound?",
                options_json='["Transverse", "Longitudinal", "Electromagnetic", "Mechanical"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Sound waves are longitudinal waves that travel through compression and rarefaction of particles.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.PHYSICS,
                topic="Waves",
                content="What is the frequency of a wave?",
                options_json='["Number of waves per second", "Height of the wave", "Distance between crests", "Speed of the wave"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="Frequency is the number of complete waves that pass a point per second, measured in Hertz (Hz).",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.PHYSICS,
                topic="Mechanics",
                content="What is the acceleration due to gravity on Earth?",
                options_json='["9.8 m/s²", "10 m/s²", "8.9 m/s²", "9.0 m/s²"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="The acceleration due to gravity on Earth is approximately 9.8 m/s².",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.PHYSICS,
                topic="Electricity",
                content="What does Ohm's law state?",
                options_json='["V = IR", "P = VI", "F = ma", "E = mc²"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Ohm's law states that voltage (V) equals current (I) multiplied by resistance (R).",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.PHYSICS,
                topic="Optics",
                content="What happens to light when it passes from air to glass?",
                options_json='["Speeds up", "Slows down", "Stops", "Changes color"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Light slows down when passing from air to glass because glass has a higher refractive index.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.PHYSICS,
                topic="Thermodynamics",
                content="What is absolute zero?",
                options_json='["0°C", "-273°C", "100°C", "-100°C"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Absolute zero is -273°C or 0 Kelvin, the lowest possible temperature.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.PHYSICS,
                topic="Waves",
                content="What is the wavelength of a wave?",
                options_json='["Time between waves", "Distance between crests", "Height of the wave", "Speed of the wave"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="Wavelength is the distance between two consecutive crests or troughs of a wave.",
                exam_year="WASSCE 2021"
            ),
            
            # Chemistry Questions (15 questions)
            Question(
                subject=Subject.CHEMISTRY,
                topic="Atomic Structure",
                content="What is the atomic number of an element?",
                options_json='["Number of protons", "Number of neutrons", "Mass number", "Number of electrons"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="The atomic number equals the number of protons in an atom's nucleus.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Atomic Structure",
                content="What is the mass number of an atom?",
                options_json='["Protons + neutrons", "Protons only", "Electrons only", "Neutrons only"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="Mass number = number of protons + number of neutrons in the nucleus.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Chemical Bonding",
                content="What type of bond involves sharing electrons?",
                options_json='["Ionic bond", "Covalent bond", "Metallic bond", "Hydrogen bond"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="Covalent bonds form when atoms share electrons to achieve stable electron configurations.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Chemical Bonding",
                content="What is formed when electrons are transferred between atoms?",
                options_json='["Covalent compound", "Ionic compound", "Metallic compound", "Molecular compound"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Ionic compounds form when electrons are transferred from metal to non-metal atoms.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Acids and Bases",
                content="What is the pH of pure water?",
                options_json='["0", "7", "14", "1"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="Pure water has a pH of 7, which is neutral.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Acids and Bases",
                content="What does a pH less than 7 indicate?",
                options_json='["Basic solution", "Acidic solution", "Neutral solution", "Salty solution"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="pH less than 7 indicates an acidic solution.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Organic Chemistry",
                content="What is the general formula for alkanes?",
                options_json='["CnH2n", "CnH2n+2", "CnH2n-2", "CnHn"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Alkanes have the general formula CnH2n+2, where n is the number of carbon atoms.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Organic Chemistry",
                content="What functional group is present in alcohols?",
                options_json='["-OH", "-COOH", "-NH2", "-CHO"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Alcohols contain the hydroxyl (-OH) functional group.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Electrochemistry",
                content="What is the process of depositing metal on a surface called?",
                options_json='["Electrolysis", "Electroplating", "Electrification", "Electron transfer"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Electroplating is the process of depositing a metal coating on a conducting surface.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Electrochemistry",
                content="In electrolysis, what happens at the cathode?",
                options_json='["Oxidation occurs", "Reduction occurs", "Nothing happens", "Electrons are produced"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Reduction (gain of electrons) occurs at the cathode during electrolysis.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Atomic Structure",
                content="Who proposed the planetary model of the atom?",
                options_json='["Bohr", "Rutherford", "Thomson", "Dalton"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Ernest Rutherford proposed the planetary model with a central nucleus and orbiting electrons.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Chemical Bonding",
                content="What is the bond angle in a water molecule?",
                options_json='["90°", "104.5°", "120°", "180°"]',
                correct_index=1,
                difficulty=DifficultyLevel.HARD,
                explanation="Water has a bond angle of 104.5° due to the bent shape caused by lone pairs on oxygen.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Acids and Bases",
                content="What is the conjugate base of HCl?",
                options_json='["H2O", "Cl-", "H3O+", "OH-"]',
                correct_index=1,
                difficulty=DifficultyLevel.HARD,
                explanation="The conjugate base of HCl is Cl- (chloride ion).",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Organic Chemistry",
                content="What is the IUPAC name for CH3-CH2-CH2-CH3?",
                options_json='["Methane", "Ethane", "Propane", "Butane"]',
                correct_index=3,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="CH3-CH2-CH2-CH3 is butane (4 carbon atoms).",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Electrochemistry",
                content="What is the standard reduction potential of hydrogen?",
                options_json='["0 V", "+1 V", "-1 V", "+2 V"]',
                correct_index=0,
                difficulty=DifficultyLevel.HARD,
                explanation="The standard hydrogen electrode has a reduction potential of 0 V by definition.",
                exam_year="WASSCE 2021"
            ),
            
            # Biology Questions (15 questions)
            Question(
                subject=Subject.BIOLOGY,
                topic="Cell Biology",
                content="What is the control center of a cell?",
                options_json='["Nucleus", "Mitochondria", "Ribosome", "Cell membrane"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="The nucleus contains the cell's DNA and controls cellular activities.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Cell Biology",
                content="What is the powerhouse of the cell?",
                options_json='["Nucleus", "Mitochondria", "Ribosome", "Golgi apparatus"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="Mitochondria generate ATP, the cell's energy currency.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Genetics",
                content="What is the basic unit of heredity?",
                options_json='["Chromosome", "Gene", "DNA", "RNA"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="A gene is a segment of DNA that codes for a specific trait.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Genetics",
                content="What is the shape of DNA molecule?",
                options_json='["Linear", "Double helix", "Single strand", "Circular"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="DNA has a double helix structure discovered by Watson and Crick.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Ecology",
                content="What is the study of relationships between organisms and their environment?",
                options_json='["Anatomy", "Ecology", "Physiology", "Taxonomy"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="Ecology studies how organisms interact with each other and their environment.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Ecology",
                content="What is the term for a group of organisms of the same species living in an area?",
                options_json='["Community", "Population", "Ecosystem", "Habitat"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="A population consists of individuals of the same species in a specific area.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Human Physiology",
                content="What is the main function of the heart?",
                options_json='["Pumping blood", "Producing hormones", "Filtering waste", "Storing nutrients"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="The heart pumps oxygenated blood to the body and deoxygenated blood to the lungs.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Human Physiology",
                content="What is the largest organ in the human body?",
                options_json='["Heart", "Liver", "Skin", "Brain"]',
                correct_index=2,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="The skin is the largest organ by surface area and weight.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Evolution",
                content="Who proposed the theory of evolution by natural selection?",
                options_json='["Darwin", "Lamarck", "Mendel", "Linnaeus"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Charles Darwin proposed the theory of evolution by natural selection in 1859.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Evolution",
                content="What is the term for change in species over time?",
                options_json='["Adaptation", "Evolution", "Mutation", "Selection"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="Evolution is the gradual change in species over generations.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Cell Biology",
                content="What process produces energy in cells without oxygen?",
                options_json='["Photosynthesis", "Respiration", "Fermentation", "Transpiration"]',
                correct_index=2,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Fermentation produces energy from glucose without using oxygen.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Genetics",
                content="What is the probability of getting a dominant trait from heterozygous parents?",
                options_json='["25%", "50%", "75%", "100%"]',
                correct_index=2,
                difficulty=DifficultyLevel.HARD,
                explanation="In a heterozygous cross (Aa x Aa), 75% of offspring show the dominant trait.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Ecology",
                content="What is the term for organisms that make their own food?",
                options_json='["Consumers", "Producers", "Decomposers", "Parasites"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="Producers (plants) use photosynthesis to make their own food.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Human Physiology",
                content="What is the function of red blood cells?",
                options_json='["Fight infection", "Carry oxygen", "Clot blood", "Produce antibodies"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Red blood cells contain hemoglobin which carries oxygen to body tissues.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Evolution",
                content="What is an example of homologous structures?",
                options_json='["Bird wing and bat wing", "Human arm and octopus tentacle", "Fish fin and dolphin fin", "All of the above"]',
                correct_index=3,
                difficulty=DifficultyLevel.HARD,
                explanation="Homologous structures have similar structure but different functions, indicating common ancestry.",
                exam_year="WASSCE 2021"
            ),
        ]
        
        # Add all questions to database
        db.add_all(questions)
        db.commit()
        
        print(f"✅ Successfully added {len(questions)} questions!")
        print(f"\nTopics covered:")
        topics = {}
        for q in questions:
            topics[q.topic] = topics.get(q.topic, 0) + 1
        
        for topic, count in sorted(topics.items()):
            print(f"  - {topic}: {count} questions")
        
        return len(questions)
        
    except Exception as e:
        print(f"❌ Error seeding questions: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    count = seed_questions()
    print(f"\n✨ Database now has {count} questions ready for practice!")
