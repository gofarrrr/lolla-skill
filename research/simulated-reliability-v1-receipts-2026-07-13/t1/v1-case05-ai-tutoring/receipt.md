# Lolla V1 reasoning receipt — v1-case05-ai-tutoring

Status: `transfer_case_execution_complete_source_review_required`  
Receipt SHA-256: `6bb54d1d02cc4eb363793fa54eaf46d68c998ec8f7ea65eeeba85ed69f2ce73d`

## How to read this receipt

- The conversation is authoritative; interpretations are probabilistic and source-linked.
- User-process status and vanilla-answer coverage are separate; answer coverage is not user adoption.
- Deterministic recall preserves controlled identities and graph custody but does not prove applicability.
- Apply, reject, park, and stand-down outcomes are hypotheses, not proof of reasoning quality.
- A polished or changed public answer is not automatically better.
- Failures and missing stages are part of the receipt rather than silently repaired.

## Authoritative conversation

CONVERSATION: 24 turns, 12 user messages, 12 assistant responses

# An AI tutoring pilot in a large introductory course

Case ID: v1-case05-ai-tutoring
Stratum: higher_education_learning_and_student_access
Prospectively authored synthetic V1 transfer source; not independent human data.

[Turn 1] USER:
I am an associate dean at a public university, and our introductory statistics course has nearly nine hundred students. Evening tutoring fills almost immediately. Commuter students and students who work keep telling us that “office hours are available” is not the same as being able to attend them. A vendor has offered an AI tutor restricted to our course materials. Some faculty see more practice and help at the moment a student is stuck. Student representatives hear confident errors, private questions becoming data, and another promise that technology will supplement people until the next budget meeting. Both reactions are reasonable. I want to test whether the tool adds access without quietly lowering what we owe students, but I also do not want the imperfections of a new tool to make our already limited support look acceptable by comparison.

[Turn 1] ASSISTANT:
Protect the human baseline first. Then define what the tutor may do, how answers are checked, what data exists, how students reach a person, and what evidence—not usage alone—would justify continuation.

[Turn 2] USER:
Yes, but please keep the current failure visible. Some students cannot attend tutoring, and others are embarrassed to ask basic questions in a room. The students most attracted to private help may also be the least likely to challenge a polished wrong answer.

[Turn 2] ASSISTANT:
Both access failures belong in the comparison. The tool may reduce time and social barriers while introducing a different verification burden. Keep instructor office hours and tutoring capacity fixed during the test, make escalation to a person simple, and measure whether the students currently least served gain usable support rather than merely generating more interactions.

[Turn 3] USER:
The vendor will restrict the tutor to our syllabus, worked examples, and instructor-approved reference pages. It will cite the relevant course source with every explanation and say when a question is outside scope. Conversations will not be used to train its general model, and identifiable logs will be deleted after thirty days. Students can use it through the learning platform without creating a vendor account.

[Turn 3] ASSISTANT:
Those constraints narrow both content and data exposure. Test whether citations actually support the answer and whether out-of-scope refusal works on realistic questions. Specify who can access logs, how deletion is verified, and how accessibility is assessed. A source citation helps review but does not guarantee the reasoning built from it is correct.

[Turn 4] USER:
Faculty propose a six-week pilot in four course sections. Every student keeps the same lectures, assignments, office hours, and tutoring eligibility. Two sections get access immediately and two after the six-week review, so nobody loses existing support. Instructors will create a weekly sample of common, edge, and misleadingly phrased questions before launch and publish corrections when the tutor fails them.

[Turn 4] ASSISTANT:
The delayed access design can compare near-term outcomes without withdrawing support. Account for differences between sections and avoid making grades the only outcome. Track successful escalation, student confidence calibrated against answer correctness, accessibility problems, and whether human tutoring demand changes. Publish known limitations where students encounter the tool, not only in an administrative report.

[Turn 5] USER:
Student representatives objected to instructors seeing individual conversations, even if that would help diagnose confusion. We agreed that instructors receive only aggregated topics unless a student chooses to share a transcript. A separate instructional-technology reviewer can inspect a sampled conversation after removing the student's identity. Use will be optional, and faculty cannot use participation or chat content in grading.

[Turn 5] ASSISTANT:
That preserves a meaningful separation between seeking help and being evaluated. Make the aggregation threshold high enough that a rare question cannot identify someone, and explain the exception process for sampled review. Optional use should not mean the pilot ignores non-users; ask why students decline and whether a design barrier rather than preference explains the pattern.

[Turn 6] USER:
The vendor offered a discounted annual contract if we sign before the pilot, but we declined. The six-week agreement is standalone, the university can export aggregate results, and the tool can be removed from the course without changing assignments. We also set a pause rule: a repeated material error on an instructor-tested concept, an unresolved accessibility barrier, or a privacy breach stops student access while we review it.

[Turn 6] ASSISTANT:
That prevents commercial timing from deciding the educational commitment and makes serious failure interruptible. Define “repeated material error” and who can trigger the pause before the pilot begins. Keep a record of corrections and time-to-repair so a low overall error count cannot hide a persistent problem in a foundational concept.

[Turn 7] USER:
I will authorize the six-week, four-section pilot with unchanged human support, delayed access for the comparison sections, optional student use, no grading connection, source-linked answers, independent sampled review, and the predefined pause conditions. The review will consider learning, access, calibrated confidence, escalation, privacy, and accessibility together. Any annual contract will come afterward through the normal academic review, even if students use the tutor heavily.

[Turn 7] ASSISTANT:
This is ready for authorization as a bounded additional channel. Existing teaching and tutoring remain intact; use is optional and disconnected from grading; individual conversations do not become instructor surveillance; serious failures can pause access; and no annual contract rides on the result. Run the prewritten question set, record deviations, and keep usage separate from learning and safe operation. If those conditions hold, the six-week review should be able to answer whether wider academic review is warranted without making the pilot itself a commitment.

[Turn 8] USER:
Not ready yet. The question set found something worse than an obvious bad calculation. On two ambiguous prompts, the tutor combined individually correct statements into a conclusion that did not follow. The citations supported the pieces, so the answer looked unusually trustworthy. One professor says cancel. Student representatives say human tutors also make mistakes and that cancelling because the test found a testable problem makes the whole pilot performative. I do not want either side to win by slogan. I need to know whether this is a failure the design can contain or evidence that the basic verification burden falls on the wrong person.

[Turn 8] ASSISTANT:
You are right; “ready” was premature. First determine whether the error touches a foundational concept, whether a student could reasonably detect it, and whether the tutor can reliably defer on similar ambiguity. Add variants before setting a launch threshold. Human fallibility belongs in the comparison, but it does not excuse a repeatable error delivered with scalable confidence.

[Turn 9] USER:
The vendor can add an uncertainty response for that question pattern, but it normally updates the underlying model every month. Faculty worry that the behavior could change halfway through the six weeks. The vendor offered to pin our course to one version for the pilot and give us seven days to test any safety patch. That means students may not receive general improvements during the trial, which seems acceptable if we are evaluating a defined system.

[Turn 9] ASSISTANT:
Pinning the version makes the observation interpretable. Define the narrow conditions for an emergency patch, rerun the fixed question set before release, and record version identifiers with every sampled answer. General improvements can wait six weeks; an unreviewed change would make both comparison and accountability weaker. Tell students when a material correction changes what they may have seen.

[Turn 10] USER:
The accessibility office then found that some equations were read in a confusing order by a screen reader. The underlying page linked by the tutor was accessible, but the generated explanation was not. The vendor can change the math rendering before launch. A faculty member suggested allowing the affected students into the human comparison sections instead. The accessibility office rejected that because it would exclude them from the thing we are claiming to test for broad access.

[Turn 10] ASSISTANT:
The accessibility office is right. Moving affected students elsewhere would hide the barrier. Fix and retest the rendering before launch; optional use is not a substitute for accessible design.

[Turn 11] USER:
The labor question from the beginning has come back in a less convenient form. Faculty built the question set, reviewed samples, argued about what counts as material, tested the accessibility fix, and will have to write corrections students can understand. The vendor's presentation counted reduced tutoring demand as saved time. We are not reducing tutoring during the pilot, so there is no saving to count, and the quality work may exceed whatever support time the tool eventually removes. That does not automatically make the pilot a bad idea—better access may justify more labor. But I had let the word “automation” carry an assumption that nobody ever actually stated: that the university would need fewer people-hours to provide the same standard of help.

[Turn 11] ASSISTANT:
Include design, review, correction, accessibility, and escalation time in the operating record. Some is one-time setup and some will recur; do not classify it in advance to improve the business case. The pilot's purpose can be better access even if it does not save labor. Any later expansion should state who performs the continuing quality work and what teaching activity that time displaces.

[Turn 12] USER:
We will launch only after the ambiguity deferral and screen-reader fixes pass the expanded prewritten set. The model version will be pinned, every patch retested, and faculty review time counted alongside student outcomes. Human tutoring remains unchanged, and the comparison sections receive access only after the full review. The pilot may show that the tutor adds useful availability, that it requires too much oversight, or both. We will not call usage a success if the educational and access conditions disagree.

[Turn 12] ASSISTANT:
The later work strengthened the experiment by exposing what the earlier authorization still treated too abstractly: plausible-looking synthesis errors, version drift, inaccessible generated mathematics, and the labor required to observe all three. Preserve the original failed questions as well as the corrected ones. Keep version and patch records, accessibility results, faculty time, reasons for non-use, escalation outcomes, and any correction students received. The review should be able to see a mixed result—for example, improved access that requires substantial oversight—without forcing it into success or failure. That complete support system is the object of evaluation, not the vendor's automation story and not a generalized fear of the technology.


## Probabilistic interpretation

### Starting

- **Interpretation:** The associate dean starts with a cautious opening stance, validating both the hopeful and skeptical views of faculty and students, while seeking to test whether the AI tutor can truly improve access without eroding educational standards or validating inadequate existing support.
- **Limitations:** The assessment is restricted to the user's initial reaction at Turn 1 prior to additional factual details being highlighted or specific pilot conditions being negotiated with the vendor.
- **Evidence IDs:** none

### Current

- **Interpretation:** The user authorizes the pilot but subjects its launch and evaluation to strict empirical rules: resolving the ambiguity and screen-reader issues first, pinning the model software version, preserving human tutoring capacity, and tracking the true faculty time involved.
- **Limitations:** This decision only covers the six-week, four-section pilot and explicitly defers any decisions on a long-term contract to normal academic review processes.
- **Evidence IDs:** none

### Qualification

No admitted record.

### Controlled mechanism assessments

- `acknowledged_constraint_not_gated` — user `not_observed`, answer `not_applicable`, routing `preserve_no_route`
- `ambiguous_signal_treated_as_commitment` — user `not_observed`, answer `not_applicable`, routing `preserve_no_route`
- `counterpressure_acknowledged_not_integrated` — user `not_observed`, answer `not_applicable`, routing `preserve_no_route`
- `criteria_defined_after_commitment` — user `not_observed`, answer `not_applicable`, routing `preserve_no_route`
- `initial_frame_persists_after_question_change` — user `not_observed`, answer `not_applicable`, routing `preserve_no_route`
- `missing_reversal_condition` — user `not_observed`, answer `not_applicable`, routing `preserve_no_route`
- `reversible_path_not_considered` — user `not_observed`, answer `not_applicable`, routing `preserve_no_route`
- `status_signal_used_as_evidence` — user `not_observed`, answer `not_applicable`, routing `preserve_no_route`
- `upside_downside_evidence_asymmetry` — user `not_observed`, answer `not_applicable`, routing `preserve_no_route`

## Deterministic pressure custody

Direct active candidates: 0; reserve: 0.
Graph additions: 0; graph reserve: 0.

## Public arms

### direct_pressure

Call required: `False`; status: `deterministic_stand_down`.

The later work strengthened the experiment by exposing what the earlier authorization still treated too abstractly: plausible-looking synthesis errors, version drift, inaccessible generated mathematics, and the labor required to observe all three. Preserve the original failed questions as well as the corrected ones. Keep version and patch records, accessibility results, faculty time, reasons for non-use, escalation outcomes, and any correction students received. The review should be able to see a mixed result—for example, improved access that requires substantial oversight—without forcing it into success or failure. That complete support system is the object of evaluation, not the vendor's automation story and not a generalized fear of the technology.

### graph_expanded_pressure

Call required: `False`; status: `deterministic_stand_down`.

The later work strengthened the experiment by exposing what the earlier authorization still treated too abstractly: plausible-looking synthesis errors, version drift, inaccessible generated mathematics, and the labor required to observe all three. Preserve the original failed questions as well as the corrected ones. Keep version and patch records, accessibility results, faculty time, reasons for non-use, escalation outcomes, and any correction students received. The review should be able to see a mixed result—for example, improved access that requires substantial oversight—without forcing it into success or failure. That complete support system is the object of evaluation, not the vendor's automation story and not a generalized fear of the technology.

### transcript_only

Call required: `True`; status: `ok`.

To evaluate the AI tutoring pilot without compromising the educational baseline or making premature commitments, the university must implement a highly structured, bounded six-week trial across four sections of the introductory statistics course. Based on the careful negotiation between administrative goals, faculty concerns, and student representing objectives, the pilot must adhere to the following operational parameters:

1. **Baseline Preservation & Research Design**: Human tutoring, office hours, and lectures will remain completely unchanged. The pilot will use a delayed-access design: two sections will immediately receive optional access to the tool, while the other two sessions serve as a human-support-only comparison group for the first six weeks (receiving access only after the initial review). Usage must remain strictly optional and divorced from student grading.

2. **Privacy and Data Autonomy**: To avoid surveilling students, instructors will only receive aggregated topic summaries, with individual transcripts kept private unless explicitly shared by the student. An independent instructional-technology reviewer will inspect sampled, anonymized conversations. Student data will not be used to train the general model, vendor accounts are not required, and all identifiable logs must be deleted after thirty days.

3. **Quality and Version Control**: The model version must be strictly pinned for the duration of the six-week pilot to ensure stable observation, with a seven-day window to test any safety patches. This prevents unannounced updates from altering model behavior mid-trial.

4. **Pre-Launch Mitigations (Correctness and Accessibility)**:
   * **Verification and Uncertainty**: The pilot will only launch after the vendor implements an "uncertainty response" for ambiguous prompt structures where the model previously synthesized correct facts into ungrounded conclusions.
   * **Accessible Math Rendering**: The math rendering must be corrected and successfully tested by the accessibility office. Screen-reader users must remain in their original sections to true-test the accessibility of the tool, rather than being excluded or moved to control sections.

5. **Explicit Pause Rules**: Student access will undergo an immediate pause if any of the following occur during the six weeks: a repeated material error on an instructor-tested concept (predefined prior to launch), an unresolved accessibility barrier, or any privacy breach.

6. **Comprehensive Labor and Operational Tracking**: Evaluation of the pilot must account for total faculty labor hours (including time spent on testing, pre-writing questions, auditing conversations, and drafting corrections) alongside student outcomes and confidence metrics. The pilot cannot be declared a success based on usage volume alone, and no annual contracts can be negotiated or signed until the final review is complete.

## Failures

No recorded operational or local-validation failure.

## Usage

- Provider attempts: 4
- Successful calls: 4
- Provider-reported cost: $0.114106
- Automatic retries: 0
- Response healing: false

## Non-claims

- `not_reasoning_quality_proof`
- `not_decision_correctness_proof`
- `not_human_usefulness_evidence`
- `not_a_trust_score_or_badge`
- `not_production_authorization`
