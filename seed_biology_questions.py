"""
Biology seeding script to add questions for all Biology topics.
Each topic needs 12 more questions to reach 15 total.
"""
import os
import sys
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.question import Question, Subject, DifficultyLevel


def seed_biology_questions():
    """Add 60 questions across 5 Biology topics."""
    db = SessionLocal()
    try:
        questions = []

        # Biology - Cell Biology - needs 12 more
        cell_questions = [
            Question(
                subject=Subject.BIOLOGY,
                topic="Cell Biology",
                content="What is the control center of the cell?",
                options_json='["Cell membrane", "Cytoplasm", "Nucleus", "Mitochondria"]',
                correct_index=2,
                difficulty=DifficultyLevel.EASY,
                explanation="The nucleus contains the cell's DNA and controls cellular activities.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Cell Biology",
                content="Which organelle is responsible for protein synthesis?",
                options_json='["Ribosomes", "Lysosomes", "Vacuoles", "Golgi apparatus"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="Ribosomes are the sites of protein synthesis in cells.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Cell Biology",
                content="What is the function of mitochondria?",
                options_json='["Protein synthesis", "Energy production", "Waste removal", "Cell division"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="Mitochondria are the powerhouse of the cell, producing ATP energy.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Cell Biology",
                content="Which structure controls movement of substances into/out of the cell?",
                options_json='["Cell wall", "Cytoplasm", "Cell membrane", "Nucleus"]',
                correct_index=2,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="The cell membrane is selectively permeable and controls substance movement.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Cell Biology",
                content="What is the difference between prokaryotic and eukaryotic cells?",
                options_json='["Size only", "Presence of nucleus", "Cell wall", "Ribosomes"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Eukaryotic cells have a nucleus, prokaryotic cells do not.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Cell Biology",
                content="Which organelle contains digestive enzymes?",
                options_json='["Ribosomes", "Lysosomes", "Vacuoles", "Peroxisomes"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Lysosomes contain hydrolytic enzymes for digestion.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Cell Biology",
                content="What is the role of the endoplasmic reticulum?",
                options_json='["Energy production", "Protein synthesis and transport", "Waste storage", "Cell division"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="The ER is involved in protein synthesis, folding, and transport.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Cell Biology",
                content="Which cell structure is found only in plant cells?",
                options_json='["Mitochondria", "Ribosomes", "Cell wall", "Nucleus"]',
                correct_index=2,
                difficulty=DifficultyLevel.EASY,
                explanation="The cell wall is a rigid structure found only in plant cells.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Cell Biology",
                content="What is osmosis?",
                options_json='["Active transport", "Diffusion of water", "Bulk transport", "Facilitated diffusion"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Osmosis is the movement of water molecules across a semi-permeable membrane.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Cell Biology",
                content="Which organelle modifies and packages proteins?",
                options_json='["Rough ER", "Smooth ER", "Golgi apparatus", "Lysosomes"]',
                correct_index=2,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="The Golgi apparatus modifies, sorts, and packages proteins and lipids.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Cell Biology",
                content="What is the cell theory?",
                options_json='["All cells come from pre-existing cells", "Cells are the basic unit of life", "All living things are made of cells", "All of the above"]',
                correct_index=3,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="The cell theory states that all living things are made of cells, cells are the basic unit of life, and all cells come from pre-existing cells.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Cell Biology",
                content="Which process requires energy input?",
                options_json='["Diffusion", "Osmosis", "Active transport", "Facilitated diffusion"]',
                correct_index=2,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Active transport moves substances against their concentration gradient, requiring energy.",
                exam_year="WASSCE 2023"
            ),
        ]
        questions.extend(cell_questions)

        # Biology - Genetics - needs 12 more
        genetics_questions = [
            Question(
                subject=Subject.BIOLOGY,
                topic="Genetics",
                content="Who is known as the father of genetics?",
                options_json='["Charles Darwin", "Gregor Mendel", "Watson and Crick", "Louis Pasteur"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="Gregor Mendel is known as the father of genetics for his work with pea plants.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Genetics",
                content="What is a gene?",
                options_json='["Unit of inheritance", "Type of cell", "Protein molecule", "DNA sequence"]',
                correct_index=3,
                difficulty=DifficultyLevel.EASY,
                explanation="A gene is a segment of DNA that codes for a specific protein or trait.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Genetics",
                content="What is the shape of DNA molecule?",
                options_json='["Linear", "Circular", "Double helix", "Single strand"]',
                correct_index=2,
                difficulty=DifficultyLevel.EASY,
                explanation="DNA has a double helix structure discovered by Watson and Crick.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Genetics",
                content="Which nitrogenous base pairs with adenine?",
                options_json='["Cytosine", "Guanine", "Thymine", "Uracil"]',
                correct_index=2,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="In DNA, adenine (A) pairs with thymine (T).",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Genetics",
                content="What is mitosis?",
                options_json='["Cell division producing gametes", "Cell division for growth", "DNA replication", "Protein synthesis"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Mitosis is cell division that produces two identical daughter cells for growth and repair.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Genetics",
                content="What is meiosis?",
                options_json='["Cell division for growth", "Cell division producing gametes", "DNA replication", "Protein synthesis"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Meiosis produces gametes with half the chromosome number.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Genetics",
                content="What is a homozygous genotype?",
                options_json='["Different alleles", "Same alleles", "One dominant allele", "No alleles"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Homozygous means having two identical alleles for a trait.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Genetics",
                content="What is the probability of getting a dominant trait from heterozygous parents?",
                options_json='["25%", "50%", "75%", "100%"]',
                correct_index=2,
                difficulty=DifficultyLevel.HARD,
                explanation="For a heterozygous cross (Aa × Aa), 75% of offspring show the dominant trait.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Genetics",
                content="What is genetic engineering?",
                options_json='["Natural selection", "Artificial manipulation of genes", "Cell division", "Protein synthesis"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Genetic engineering involves artificially modifying an organism's genetic material.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Genetics",
                content="What is RNA?",
                options_json='["Double-stranded molecule", "Single-stranded molecule", "Protein", "Carbohydrate"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="RNA is a single-stranded nucleic acid involved in protein synthesis.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Genetics",
                content="What is transcription?",
                options_json='["DNA to DNA", "DNA to RNA", "RNA to protein", "Protein to DNA"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Transcription is the process of making RNA from DNA template.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Genetics",
                content="What is a mutation?",
                options_json='["Normal gene function", "Change in DNA sequence", "Cell division", "Protein synthesis"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="A mutation is a permanent change in the DNA sequence.",
                exam_year="WASSCE 2023"
            ),
        ]
        questions.extend(genetics_questions)

        # Biology - Ecology - needs 12 more
        ecology_questions = [
            Question(
                subject=Subject.BIOLOGY,
                topic="Ecology",
                content="What is an ecosystem?",
                options_json='["Group of same species", "Community and environment", "Single organism", "Food chain"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="An ecosystem includes all living organisms and their physical environment.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Ecology",
                content="What is the primary source of energy in most ecosystems?",
                options_json='["Water", "Soil", "Sunlight", "Air"]',
                correct_index=2,
                difficulty=DifficultyLevel.EASY,
                explanation="The sun is the primary source of energy for most ecosystems.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Ecology",
                content="What is a producer in a food chain?",
                options_json='["Herbivore", "Carnivore", "Plant", "Decomposer"]',
                correct_index=2,
                difficulty=DifficultyLevel.EASY,
                explanation="Producers are organisms that make their own food through photosynthesis.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Ecology",
                content="What is the term for animals that eat both plants and animals?",
                options_json='["Herbivore", "Carnivore", "Omnivore", "Decomposer"]',
                correct_index=2,
                difficulty=DifficultyLevel.EASY,
                explanation="Omnivores eat both plants and animals.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Ecology",
                content="What is biodiversity?",
                options_json='["Number of species", "Variety of life", "Population size", "Food availability"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Biodiversity refers to the variety of life forms in an ecosystem.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Ecology",
                content="What is eutrophication?",
                options_json='["Oxygen depletion", "Nutrient enrichment", "Soil erosion", "Deforestation"]',
                correct_index=1,
                difficulty=DifficultyLevel.HARD,
                explanation="Eutrophication is the enrichment of water bodies with nutrients leading to excessive plant growth.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Ecology",
                content="What is a keystone species?",
                options_json='["Largest species", "Species with high population", "Species crucial to ecosystem", "Invasive species"]',
                correct_index=2,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="A keystone species has a disproportionate effect on its ecosystem.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Ecology",
                content="What is the greenhouse effect?",
                options_json='["Global warming", "Ozone depletion", "Acid rain", "Deforestation"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="The greenhouse effect is the trapping of heat by greenhouse gases.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Ecology",
                content="What is symbiosis?",
                options_json='["Competition", "Predation", "Close relationship between species", "Migration"]',
                correct_index=2,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Symbiosis is a close, long-term relationship between different species.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Ecology",
                content="What is parasitism?",
                options_json='["Mutual benefit", "One benefits, one harmed", "Both benefit", "No interaction"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="In parasitism, one organism benefits while the other is harmed.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Ecology",
                content="What is the first trophic level?",
                options_json='["Primary consumer", "Secondary consumer", "Producer", "Decomposer"]',
                correct_index=2,
                difficulty=DifficultyLevel.EASY,
                explanation="Producers form the first trophic level in food chains.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Ecology",
                content="What is biomagnification?",
                options_json='["Population increase", "Toxin concentration up food chain", "Species diversity", "Energy transfer"]',
                correct_index=1,
                difficulty=DifficultyLevel.HARD,
                explanation="Biomagnification is the increasing concentration of toxins as they move up the food chain.",
                exam_year="WASSCE 2023"
            ),
        ]
        questions.extend(ecology_questions)

        # Biology - Human Physiology - needs 12 more
        physiology_questions = [
            Question(
                subject=Subject.BIOLOGY,
                topic="Human Physiology",
                content="What is the function of the heart?",
                options_json='["Gas exchange", "Pumping blood", "Food digestion", "Waste removal"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="The heart pumps blood throughout the body.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Human Physiology",
                content="Where does gas exchange occur in humans?",
                options_json='["Heart", "Kidneys", "Lungs", "Liver"]',
                correct_index=2,
                difficulty=DifficultyLevel.EASY,
                explanation="Gas exchange occurs in the alveoli of the lungs.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Human Physiology",
                content="What is the function of red blood cells?",
                options_json='["Fight infection", "Blood clotting", "Oxygen transport", "Nutrient absorption"]',
                correct_index=2,
                difficulty=DifficultyLevel.EASY,
                explanation="Red blood cells transport oxygen from lungs to body tissues.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Human Physiology",
                content="Which organ produces insulin?",
                options_json='["Liver", "Pancreas", "Kidney", "Stomach"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="The pancreas produces insulin to regulate blood sugar.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Human Physiology",
                content="What is homeostasis?",
                options_json='["Cell division", "Maintaining internal balance", "Energy production", "Waste removal"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Homeostasis is the maintenance of stable internal conditions.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Human Physiology",
                content="Which blood vessels carry blood away from the heart?",
                options_json='["Veins", "Arteries", "Capillaries", "Venules"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="Arteries carry oxygenated blood away from the heart.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Human Physiology",
                content="What is the function of the nephron?",
                options_json='["Blood pumping", "Gas exchange", "Urine formation", "Food digestion"]',
                correct_index=2,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Nephrons in the kidneys filter blood and form urine.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Human Physiology",
                content="Which hormone regulates calcium levels?",
                options_json='["Insulin", "Adrenaline", "Parathyroid hormone", "Thyroxine"]',
                correct_index=2,
                difficulty=DifficultyLevel.HARD,
                explanation="Parathyroid hormone regulates blood calcium levels.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Human Physiology",
                content="What is the role of the diaphragm in breathing?",
                options_json='["Gas exchange", "Air filtration", "Chest cavity expansion", "Oxygen transport"]',
                correct_index=2,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="The diaphragm contracts to expand the chest cavity during inhalation.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Human Physiology",
                content="Which enzyme breaks down starch?",
                options_json='["Pepsin", "Amylase", "Lipase", "Trypsin"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Amylase breaks down starch into sugars.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Human Physiology",
                content="What is the normal human body temperature?",
                options_json='["35°C", "37°C", "39°C", "41°C"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="Normal human body temperature is 37°C.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Human Physiology",
                content="Which blood type is the universal donor?",
                options_json='["A", "B", "AB", "O"]',
                correct_index=3,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Type O negative blood can be donated to all blood types.",
                exam_year="WASSCE 2023"
            ),
        ]
        questions.extend(physiology_questions)

        # Biology - Evolution - needs 12 more
        evolution_questions = [
            Question(
                subject=Subject.BIOLOGY,
                topic="Evolution",
                content="Who proposed the theory of evolution by natural selection?",
                options_json='["Charles Darwin", "Gregor Mendel", "Louis Pasteur", "Robert Hooke"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="Charles Darwin proposed the theory of evolution by natural selection.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Evolution",
                content="What is natural selection?",
                options_json='["Artificial breeding", "Survival of the fittest", "Random mutations", "Genetic engineering"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Natural selection is the process where organisms better adapted to their environment survive and reproduce.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Evolution",
                content="What is a fossil?",
                options_json='["Living organism", "Remains of ancient organisms", "Modern species", "DNA evidence"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="Fossils are preserved remains or traces of ancient organisms.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Evolution",
                content="What is speciation?",
                options_json='["Individual variation", "Formation of new species", "Population growth", "Extinction"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Speciation is the formation of new species from existing ones.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Evolution",
                content="What is homologous structures?",
                options_json='["Similar function, different origin", "Similar structure, different function", "Similar structure, common origin", "Different structure, common function"]',
                correct_index=2,
                difficulty=DifficultyLevel.HARD,
                explanation="Homologous structures have similar structure and common evolutionary origin.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Evolution",
                content="What is convergent evolution?",
                options_json='["Species becoming similar", "Species becoming different", "Same ancestor", "Different habitats"]',
                correct_index=0,
                difficulty=DifficultyLevel.HARD,
                explanation="Convergent evolution is when different species develop similar traits in similar environments.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Evolution",
                content="What is genetic drift?",
                options_json='["Natural selection", "Random change in gene frequencies", "Mutation", "Gene flow"]',
                correct_index=1,
                difficulty=DifficultyLevel.HARD,
                explanation="Genetic drift is random changes in allele frequencies in small populations.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Evolution",
                content="What is adaptive radiation?",
                options_json='["Species extinction", "One species giving rise to many", "Population decline", "Genetic variation"]',
                correct_index=1,
                difficulty=DifficultyLevel.HARD,
                explanation="Adaptive radiation is when one species rapidly diversifies into many species.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Evolution",
                content="What is the evidence for evolution from embryology?",
                options_json='["Fossils", "Similar embryo stages", "DNA sequences", "Geographic distribution"]',
                correct_index=1,
                difficulty=DifficultyLevel.HARD,
                explanation="Similar embryonic stages in different species suggest common ancestry.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Evolution",
                content="What is Lamarck's theory?",
                options_json='["Natural selection", "Inheritance of acquired traits", "Genetic mutation", "Genetic drift"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Lamarck proposed that acquired traits could be inherited.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Evolution",
                content="What is the unit of evolution?",
                options_json='["Individual", "Population", "Species", "Community"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Evolution occurs at the population level through changes in gene frequencies.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.BIOLOGY,
                topic="Evolution",
                content="What is punctuated equilibrium?",
                options_json='["Gradual change", "Rapid change followed by stability", "No change", "Continuous variation"]',
                correct_index=1,
                difficulty=DifficultyLevel.HARD,
                explanation="Punctuated equilibrium suggests evolution occurs in rapid bursts followed by long periods of stability.",
                exam_year="WASSCE 2023"
            ),
        ]
        questions.extend(evolution_questions)

        # Bulk insert all questions
        db.add_all(questions)
        db.commit()

        print(f"✅ Successfully added {len(questions)} Biology questions!")
        return len(questions)

    except Exception as e:
        print(f"❌ Error seeding Biology questions: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    count = seed_biology_questions()
    print(f"\n🚀 Added {count} Biology questions!")