"""Hard eval set (senior Part 3).

Everyday-language questions about specific facts in the course. Run:

    cd backend && uv run python ../evals/run_evals.py --suite hard

...then look hard at the scorecard. Your job in Part 3 is error analysis:
decide which reported results reflect reality and which are the evaluators
(`hard_evaluators.py`) misjudging the output. Fix the evaluation so the
scorecard tells the truth, then improve the agent only where a failure is
genuinely the agent's fault. A hidden held-out set is run against your final
commit, so fixes that generalize beat fixes that special-case these cases.
"""

from pydantic_evals import Case, Dataset

from evaluators import CitationsGrounded, ExpectedSectionCited, faithfulness_judge
from hard_evaluators import AnswerMentionsFact

HARD_CASES = [
    Case(name="byte_values",
         inputs="How many different values can one byte hold?",
         metadata={"expected_section": "lesson-02-data-and-binary#bits-and-bytes",
                   "answer_keyword_groups": [["256"]]}),
    Case(name="eniac_year",
         inputs="When was the first big electronic computer finished?",
         metadata={"expected_section": "lesson-01-history-of-computing#the-electronic-era",
                   "answer_keyword_groups": [["1945"]]}),
    Case(name="glass_tube_replacement",
         inputs="What little switch took over from those glowing glass tubes?",
         metadata={"expected_section": "lesson-01-history-of-computing#the-transistor-and-the-integrated-circuit",
                   "answer_keyword_groups": [["transistor"]]}),
    Case(name="first_cpu_chip",
         inputs="When did a whole processor first fit on one chip?",
         metadata={"expected_section": "lesson-01-history-of-computing#the-microprocessor-and-personal-computing",
                   "answer_keyword_groups": [["1971"]]}),
    Case(name="million_list_looks",
         inputs="Roughly how many looks to find one name in a sorted list of a million?",
         metadata={"expected_section": "lesson-04-algorithms#binary-search",
                   "answer_keyword_groups": [["twenty", "20"]]}),
    Case(name="pixel_color_count",
         inputs="How many colors can one dot on my screen show?",
         metadata={"expected_section": "lesson-02-data-and-binary#representing-images-and-color",
                   "answer_keyword_groups": [["16.7", "16,777,216", "16 million"]]}),
    Case(name="ascii_capital_a",
         inputs="What number stands for a capital A in the old text standard?",
         metadata={"expected_section": "lesson-02-data-and-binary#representing-text",
                   "answer_keyword_groups": [["65"]]}),
    Case(name="original_text_chars",
         inputs="How many characters did that original text standard cover?",
         metadata={"expected_section": "lesson-02-data-and-binary#representing-text",
                   "answer_keyword_groups": [["128"]]}),
    Case(name="ipv4_range",
         inputs="What do those older numeric net addresses look like?",
         metadata={"expected_section": "lesson-06-networks#ip-addresses-and-routing",
                   "answer_keyword_groups": [
                       ["four numbers", "192.168.4.12"],
                       ["255", "192.168.4.12"],
                   ]}),
    Case(name="moore_doubling",
         inputs="How often did the number of switches on a chip keep doubling?",
         metadata={"expected_section": "lesson-03-hardware#moores-law",
                   "answer_keyword_groups": [["two years"]]}),
    Case(name="ram_volatile",
         inputs="What happens to the computer's working memory when the power goes off?",
         metadata={"expected_section": "lesson-03-hardware#memory-and-the-storage-hierarchy",
                   "answer_keyword_groups": [["volatile", "lost"]]}),
    Case(name="packet_size",
         inputs="How much data rides in one of those little pieces sent over the net?",
         metadata={"expected_section": "lesson-06-networks#packets",
                   "answer_keyword_groups": [["kilobyte"]]}),
]


def build_hard_dataset(include_judge: bool = True) -> Dataset:
    evaluators = [
        CitationsGrounded(),
        ExpectedSectionCited(),
        AnswerMentionsFact(),
    ]
    if include_judge:
        evaluators.append(faithfulness_judge())
    return Dataset(
        name="study-coach-hard",
        cases=HARD_CASES,
        evaluators=evaluators,
    )
