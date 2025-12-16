"""
Chemistry seeding script to add questions for all Chemistry topics.
Each topic needs 12 more questions to reach 15 total.
"""
import os
import sys
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.question import Question, Subject, DifficultyLevel


def seed_chemistry_questions():
    """Add 60 questions across 5 Chemistry topics."""
    db = SessionLocal()
    try:
        questions = []

        # Chemistry - Atomic Structure - needs 12 more
        atomic_questions = [
            Question(
                subject=Subject.CHEMISTRY,
                topic="Atomic Structure",
                content="What is the atomic number of an element?",
                options_json='["Number of protons", "Number of neutrons", "Number of electrons", "Mass number"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="Atomic number equals the number of protons in an atom's nucleus.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Atomic Structure",
                content="What is the mass number of an atom?",
                options_json='["Number of protons", "Number of neutrons", "Protons + neutrons", "Number of electrons"]',
                correct_index=2,
                difficulty=DifficultyLevel.EASY,
                explanation="Mass number is the total number of protons and neutrons in an atom.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Atomic Structure",
                content="Which subatomic particle has a negative charge?",
                options_json='["Proton", "Neutron", "Electron", "Nucleus"]',
                correct_index=2,
                difficulty=DifficultyLevel.EASY,
                explanation="Electrons carry a negative charge and orbit the nucleus.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Atomic Structure",
                content="What is an isotope?",
                options_json='["Atoms with same atomic number", "Atoms with same mass number", "Atoms with different number of neutrons", "Atoms with different number of protons"]',
                correct_index=2,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Isotopes are atoms of the same element with different numbers of neutrons.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Atomic Structure",
                content="Who proposed the planetary model of the atom?",
                options_json='["Rutherford", "Bohr", "Thomson", "Dalton"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Ernest Rutherford proposed the planetary model with a central nucleus.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Atomic Structure",
                content="What is the maximum number of electrons in the first energy level?",
                options_json='["2", "8", "18", "32"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="The first energy level (K shell) can hold a maximum of 2 electrons.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Atomic Structure",
                content="What is the relative mass of a proton?",
                options_json='["1", "0", "1/1836", "1836"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="A proton has a relative mass of 1 atomic mass unit.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Atomic Structure",
                content="Which scientist discovered the electron?",
                options_json='["Rutherford", "Bohr", "Thomson", "Dalton"]',
                correct_index=2,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="J.J. Thomson discovered the electron through cathode ray experiments.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Atomic Structure",
                content="What is the charge of a neutron?",
                options_json='["+1", "0", "-1", "+2"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="Neutrons are neutral particles with no electric charge.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Atomic Structure",
                content="What determines the chemical properties of an element?",
                options_json='["Mass number", "Atomic number", "Number of neutrons", "Isotopes"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Chemical properties are determined by the atomic number (number of protons).",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Atomic Structure",
                content="What is the atomic number of carbon?",
                options_json='["6", "12", "14", "16"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="Carbon has 6 protons, so its atomic number is 6.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Atomic Structure",
                content="Which energy level can hold up to 18 electrons?",
                options_json='["K", "L", "M", "N"]',
                correct_index=2,
                difficulty=DifficultyLevel.HARD,
                explanation="The M shell (third energy level) can hold up to 18 electrons.",
                exam_year="WASSCE 2023"
            ),
        ]
        questions.extend(atomic_questions)

        # Chemistry - Chemical Bonding - needs 12 more
        bonding_questions = [
            Question(
                subject=Subject.CHEMISTRY,
                topic="Chemical Bonding",
                content="What type of bond forms between two non-metal atoms?",
                options_json='["Ionic", "Covalent", "Metallic", "Hydrogen"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="Non-metals form covalent bonds by sharing electrons.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Chemical Bonding",
                content="What is an ionic bond?",
                options_json='["Sharing of electrons", "Transfer of electrons", "Metallic bonding", "Hydrogen bonding"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="Ionic bonds form when electrons are transferred from metal to non-metal.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Chemical Bonding",
                content="Which compound has ionic bonding?",
                options_json='["H2O", "NaCl", "CH4", "CO2"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="NaCl (sodium chloride) is an ionic compound.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Chemical Bonding",
                content="What is the bond angle in water (H2O)?",
                options_json='["90°", "104.5°", "109.5°", "120°"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Water has a bond angle of 104.5° due to lone pairs on oxygen.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Chemical Bonding",
                content="What is electronegativity?",
                options_json='["Ability to form bonds", "Ability to attract electrons", "Atomic size", "Ionization energy"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Electronegativity is the ability of an atom to attract electrons in a bond.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Chemical Bonding",
                content="Which element has the highest electronegativity?",
                options_json='["Sodium", "Chlorine", "Fluorine", "Oxygen"]',
                correct_index=2,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Fluorine has the highest electronegativity of all elements.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Chemical Bonding",
                content="What is a dative covalent bond?",
                options_json='["Equal sharing", "Unequal sharing", "Both electrons from one atom", "Ionic bond"]',
                correct_index=2,
                difficulty=DifficultyLevel.HARD,
                explanation="A dative bond forms when both electrons come from one atom.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Chemical Bonding",
                content="Which molecule has a triple bond?",
                options_json='["H2O", "CO2", "N2", "CH4"]',
                correct_index=2,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Nitrogen (N2) has a triple covalent bond.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Chemical Bonding",
                content="What is metallic bonding?",
                options_json='["Electron transfer", "Electron sharing", "Sea of electrons", "Hydrogen bonding"]',
                correct_index=2,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Metallic bonding involves a 'sea of electrons' around positive ions.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Chemical Bonding",
                content="Which compound has polar covalent bonds?",
                options_json='["Cl2", "HCl", "NaCl", "MgO"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="HCl has polar covalent bonds due to electronegativity difference.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Chemical Bonding",
                content="What is the shape of methane (CH4)?",
                options_json='["Linear", "Trigonal planar", "Tetrahedral", "Pyramidal"]',
                correct_index=2,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Methane has a tetrahedral shape with 109.5° bond angles.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Chemical Bonding",
                content="Which bond is strongest?",
                options_json='["Single covalent", "Double covalent", "Triple covalent", "Ionic"]',
                correct_index=2,
                difficulty=DifficultyLevel.HARD,
                explanation="Triple covalent bonds are the strongest due to three shared pairs.",
                exam_year="WASSCE 2023"
            ),
        ]
        questions.extend(bonding_questions)

        # Chemistry - Acids and Bases - needs 12 more
        acid_base_questions = [
            Question(
                subject=Subject.CHEMISTRY,
                topic="Acids and Bases",
                content="What is the pH of a neutral solution?",
                options_json='["0", "7", "14", "1"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="A pH of 7 indicates a neutral solution.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Acids and Bases",
                content="Which ion do acids produce in water?",
                options_json='["OH-", "H+", "Na+", "Cl-"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="Acids produce hydrogen ions (H+) when dissolved in water.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Acids and Bases",
                content="What is a strong acid?",
                options_json='["Partially ionizes", "Completely ionizes", "No ionization", "Weak ionization"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Strong acids completely ionize in water solution.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Acids and Bases",
                content="What is the conjugate base of HCl?",
                options_json='["H2O", "Cl-", "H3O+", "OH-"]',
                correct_index=1,
                difficulty=DifficultyLevel.HARD,
                explanation="Cl- is the conjugate base formed when HCl donates a proton.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Acids and Bases",
                content="Which substance is amphoteric?",
                options_json='["HCl", "NaOH", "H2O", "CH3COOH"]',
                correct_index=2,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Water can act as both an acid and a base.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Acids and Bases",
                content="What is the pH of 0.1 M HCl?",
                options_json='["1", "7", "13", "0"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="0.1 M HCl has a pH of 1 (strong acid).",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Acids and Bases",
                content="Which acid is found in vinegar?",
                options_json='["HCl", "H2SO4", "CH3COOH", "HNO3"]',
                correct_index=2,
                difficulty=DifficultyLevel.EASY,
                explanation="Acetic acid (CH3COOH) is the acid in vinegar.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Acids and Bases",
                content="What is neutralization?",
                options_json='["Acid + base → salt", "Acid + acid → water", "Base + base → salt", "Salt + water → acid"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="Neutralization is the reaction between an acid and base producing salt and water.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Acids and Bases",
                content="Which indicator turns red in acid?",
                options_json='["Phenolphthalein", "Methyl orange", "Litmus", "Universal indicator"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Methyl orange turns red in acidic solutions.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Acids and Bases",
                content="What is the pKa of a weak acid?",
                options_json='["Always 7", "Less than 7", "Greater than 7", "Zero"]',
                correct_index=2,
                difficulty=DifficultyLevel.HARD,
                explanation="Weak acids have pKa values greater than 7.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Acids and Bases",
                content="Which base is used in antacids?",
                options_json='["NaOH", "KOH", "Mg(OH)2", "Ca(OH)2"]',
                correct_index=2,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Magnesium hydroxide is commonly used in antacid tablets.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Acids and Bases",
                content="What is the pOH of a 0.01 M NaOH solution?",
                options_json='["1", "2", "12", "13"]',
                correct_index=1,
                difficulty=DifficultyLevel.HARD,
                explanation="0.01 M NaOH has pOH = 2, so pH = 12.",
                exam_year="WASSCE 2023"
            ),
        ]
        questions.extend(acid_base_questions)

        # Chemistry - Electrochemistry - needs 12 more
        electrochemistry_questions = [
            Question(
                subject=Subject.CHEMISTRY,
                topic="Electrochemistry",
                content="What is electrolysis?",
                options_json='["Chemical decomposition", "Electrical decomposition", "Formation of compounds", "Neutralization"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="Electrolysis uses electricity to decompose compounds.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Electrochemistry",
                content="Which ion moves to the cathode during electrolysis?",
                options_json='["Anions", "Cations", "Electrons", "Molecules"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Positive ions (cations) move to the cathode.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Electrochemistry",
                content="What is the anode?",
                options_json='["Negative electrode", "Positive electrode", "Neutral electrode", "Salt bridge"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="The anode is the positive electrode where oxidation occurs.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Electrochemistry",
                content="Which product forms at the cathode during water electrolysis?",
                options_json='["Oxygen", "Hydrogen", "Chlorine", "Sodium"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Hydrogen gas is produced at the cathode during water electrolysis.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Electrochemistry",
                content="What is a voltaic cell?",
                options_json='["Electrolytic cell", "Galvanic cell", "Fuel cell", "Concentration cell"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="A voltaic cell converts chemical energy to electrical energy.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Electrochemistry",
                content="What is the standard hydrogen electrode potential?",
                options_json='["0 V", "1 V", "-1 V", "2 V"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="The standard hydrogen electrode has a potential of 0 V.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Electrochemistry",
                content="Which metal has the highest reduction potential?",
                options_json='["Copper", "Zinc", "Gold", "Lithium"]',
                correct_index=2,
                difficulty=DifficultyLevel.HARD,
                explanation="Gold has the highest reduction potential among these metals.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Electrochemistry",
                content="What is Faraday's first law?",
                options_json='["Mass ∝ charge", "Mass ∝ current", "Mass ∝ time", "Mass ∝ voltage"]',
                correct_index=0,
                difficulty=DifficultyLevel.HARD,
                explanation="Faraday's first law states mass deposited is proportional to charge passed.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Electrochemistry",
                content="Which electrolyte is used in dry cells?",
                options_json='["Copper sulfate", "Sodium chloride", "Ammonium chloride", "Potassium nitrate"]',
                correct_index=2,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Dry cells use ammonium chloride as the electrolyte.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Electrochemistry",
                content="What is corrosion?",
                options_json='["Deposition", "Oxidation", "Reduction", "Electrolysis"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Corrosion is the oxidation of metals in the presence of moisture.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Electrochemistry",
                content="Which method prevents corrosion?",
                options_json='["Painting", "Galvanizing", "Sacrificial protection", "All of the above"]',
                correct_index=3,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="All these methods (painting, galvanizing, sacrificial anodes) prevent corrosion.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Electrochemistry",
                content="What is the EMF of a cell?",
                options_json='["Current × resistance", "Potential difference", "Charge × voltage", "Power × time"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="EMF (electromotive force) is the potential difference of a cell.",
                exam_year="WASSCE 2023"
            ),
        ]
        questions.extend(electrochemistry_questions)

        # Chemistry - Organic Chemistry - needs 12 more
        organic_questions = [
            Question(
                subject=Subject.CHEMISTRY,
                topic="Organic Chemistry",
                content="What is the general formula for alkanes?",
                options_json='["CnH2n", "CnH2n+2", "CnH2n-2", "CnHn"]',
                correct_index=1,
                difficulty=DifficultyLevel.EASY,
                explanation="Alkanes have the general formula CnH2n+2.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Organic Chemistry",
                content="Which functional group is present in alcohols?",
                options_json='["-OH", "-COOH", "-CHO", "-NH2"]',
                correct_index=0,
                difficulty=DifficultyLevel.EASY,
                explanation="Alcohols contain the hydroxyl (-OH) functional group.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Organic Chemistry",
                content="What is isomerism?",
                options_json='["Same formula, different structure", "Different formula, same structure", "Same formula, same structure", "Different formula, different structure"]',
                correct_index=0,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Isomers have the same molecular formula but different structural arrangements.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Organic Chemistry",
                content="Which compound is unsaturated?",
                options_json='["Methane", "Ethene", "Ethanol", "Ethanoic acid"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Ethene (C2H4) has a double bond, making it unsaturated.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Organic Chemistry",
                content="What is fermentation?",
                options_json='["Cracking", "Polymerization", "Anaerobic respiration", "Combustion"]',
                correct_index=2,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Fermentation is anaerobic conversion of sugars to ethanol and CO2.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Organic Chemistry",
                content="Which reagent tests for unsaturation?",
                options_json='["Fehling\'s solution", "Tollen\'s reagent", "Bromine water", "Benedict\'s solution"]',
                correct_index=2,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Bromine water decolorizes in the presence of unsaturated compounds.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Organic Chemistry",
                content="What is the IUPAC name of CH3COOH?",
                options_json='["Methanol", "Ethanol", "Ethanoic acid", "Methanoic acid"]',
                correct_index=2,
                difficulty=DifficultyLevel.EASY,
                explanation="CH3COOH is ethanoic acid.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Organic Chemistry",
                content="Which reaction produces soap?",
                options_json='["Hydrogenation", "Saponification", "Esterification", "Hydrolysis"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Saponification of fats with alkali produces soap.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Organic Chemistry",
                content="What is polymerization?",
                options_json='["Breaking bonds", "Forming monomers", "Joining monomers", "Cracking hydrocarbons"]',
                correct_index=2,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Polymerization joins many monomers to form a polymer.",
                exam_year="WASSCE 2023"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Organic Chemistry",
                content="Which compound is aromatic?",
                options_json='["Cyclohexane", "Benzene", "Hexane", "Ethene"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Benzene is an aromatic hydrocarbon with a ring structure.",
                exam_year="WASSCE 2021"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Organic Chemistry",
                content="What is the test for proteins?",
                options_json='["Iodine", "Biuret", "Benedict\'s", "Fehling\'s"]',
                correct_index=1,
                difficulty=DifficultyLevel.MEDIUM,
                explanation="Biuret test detects peptide bonds in proteins.",
                exam_year="WASSCE 2022"
            ),
            Question(
                subject=Subject.CHEMISTRY,
                topic="Organic Chemistry",
                content="Which carbohydrate is a monosaccharide?",
                options_json='["Sucrose", "Lactose", "Glucose", "Starch"]',
                correct_index=2,
                difficulty=DifficultyLevel.EASY,
                explanation="Glucose is a simple sugar (monosaccharide).",
                exam_year="WASSCE 2023"
            ),
        ]
        questions.extend(organic_questions)

        # Bulk insert all questions
        db.add_all(questions)
        db.commit()

        print(f"✅ Successfully added {len(questions)} Chemistry questions!")
        return len(questions)

    except Exception as e:
        print(f"❌ Error seeding Chemistry questions: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    count = seed_chemistry_questions()
    print(f"\n🚀 Added {count} Chemistry questions!")