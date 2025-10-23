"""
Realistic Medical Document Templates

These templates create documents that closely approximate real medical records
for benchmarking PHI classification systems. PHI is embedded naturally in
clinical narrative rather than structured lists.

Key characteristics:
- 20-50 PHI identifiers per document (realistic density)
- Narrative clinical notes style with natural variation
- Multiple template variations for each document type
- Extensive clinical vocabulary and scenarios
- Mimics actual EHR/medical record output with provider variability
"""

import random

# Extensive clinical vocabulary for realistic variation
CLINICAL_VOCABULARY = {
    'hpi_templates': [
        "{first_name} {last_name} is a {age}-year-old {gender} with history of {primary_diagnosis} presenting for follow-up. Patient reports {symptom_quality} symptoms {symptom_frequency}. {symptom_context}",
        "Patient presents as scheduled for routine management of {primary_diagnosis}. Since last visit {time_reference}, symptoms have been {symptom_status}. {adherence_statement}",
        "Seen today for ongoing care of {primary_diagnosis}. Patient describes {symptom_description} that {temporal_pattern}. Currently {functional_status}.",
        "{age} y.o. {gender} returning for {visit_type} of {primary_diagnosis}. {symptom_course} Reports {specific_complaint}. {impact_statement}",
    ],

    'symptom_qualities': [
        'mild to moderate', 'intermittent', 'well-controlled', 'stable', 'improving',
        'unchanged', 'occasional', 'manageable', 'minimal', 'tolerable',
        'gradually improving', 'slowly resolving', 'fluctuating', 'episodic'
    ],

    'symptom_frequencies': [
        'occurring 2-3 times per week', 'primarily in the mornings', 'especially with activity',
        'mostly at night', 'throughout the day', 'after meals', 'intermittently',
        'less often than before', '1-2x weekly', 'sporadically'
    ],

    'symptom_contexts': [
        'No associated chest pain, dyspnea, or syncope.',
        'Denies fever, chills, night sweats, or weight changes.',
        'No exacerbating factors identified.',
        'Symptoms do not interfere with daily activities.',
        'Able to maintain regular work schedule.',
        'No emergency department visits since last appointment.',
        'Has not required urgent care or hospitalization.'
    ],

    'time_references': [
        '3 months ago', '6 weeks ago', 'in January', 'earlier this year',
        '90 days ago', 'in the spring', 'last quarter', 'previous visit'
    ],

    'symptom_statuses': [
        'relatively stable', 'well-managed', 'controlled on current regimen',
        'improved compared to prior', 'without significant changes',
        'adequately controlled', 'responding well to treatment'
    ],

    'adherence_statements': [
        'Patient reports good medication compliance.',
        'Taking all medications as prescribed.',
        'Adherent to treatment plan.',
        'No missed doses reported.',
        'Following recommended lifestyle modifications.'
    ],

    'physical_exam_variants': {
        'general': [
            'Well-appearing, NAD, comfortable',
            'Alert and oriented x3, no acute distress',
            'Pleasant, cooperative, appropriate affect',
            'Well-nourished, well-developed',
            'Appears stated age, in NAD'
        ],
        'cv': [
            'RRR, no m/r/g, S1 S2 normal',
            'Regular rate and rhythm, normal S1/S2',
            'Heart sounds normal, no murmurs appreciated',
            'PMI non-displaced, no heaves or thrills',
            'No JVD, peripheral pulses 2+ bilaterally'
        ],
        'resp': [
            'CTAB, no w/r/r',
            'Clear to auscultation bilaterally',
            'Lungs clear, good air movement',
            'No wheezes, rales, or rhonchi',
            'Respirations unlabored, symmetric chest expansion'
        ],
        'abd': [
            'Soft, NT/ND, +BS',
            'Non-tender, non-distended, normoactive bowel sounds',
            'Abdomen soft and flat, no masses',
            'No hepatosplenomegaly, no rebound or guarding',
            'BS present in all quadrants, no tenderness to palpation'
        ]
    },

    'assessment_plans': [
        '{diagnosis} - Continue current management. Patient doing well on {med1} and {med2}. Will maintain current doses. F/u in {interval}.',
        '{diagnosis} - Stable on current regimen. Labs within acceptable range. Continue {med1} {dose1}. Recheck labs in {interval}.',
        '{diagnosis} - Adequately controlled. Patient tolerating medications well. Reinforce adherence. Next visit {interval}.',
        '{diagnosis} - Good response to therapy. Discussed side effect profile. Will continue {med1}. PRN adjustment if symptoms change.',
        '{diagnosis} - Chronic, stable. Ongoing pharmacologic management with {med1}. Lifestyle modifications discussed. RTC {interval}.'
    ],

    'clinical_reasoning': [
        'Given the patient\'s clinical stability and good medication tolerance, will continue current approach.',
        'Patient meeting treatment goals with current regimen.',
        'Risk-benefit analysis favors continuation of current therapy.',
        'No indication for medication adjustment at this time.',
        'Patient understanding and compliance are excellent.'
    ]
}

PROGRESS_NOTE_VARIANTS = [
    # Variant 1: Standard format
    """{facility_name}
{city}, {state} {zip_code}

PROGRESS NOTE

Patient: {last_name}, {first_name}
MRN: {mrn}
DOB: {date_of_birth}
Visit Date: {visit_date}
Provider: {attending_physician}

CHIEF COMPLAINT: {chief_complaint}

HPI:
{hpi_narrative}

CURRENT MEDICATIONS:
{medication_list_narrative}

ALLERGIES: {allergy_list_simple}

PHYSICAL EXAM:
Vitals: BP {bp_systolic}/{bp_diastolic} | HR {heart_rate} | T {temperature}F | Wt {weight} lbs | RR {resp_rate}
General: {general_exam}
CV: {cv_exam}
Lungs: {resp_exam}
Abd: {abd_exam}

ASSESSMENT/PLAN:
{assessment_plan}

{clinical_reasoning}

Patient counseled and questions answered. Verbalized understanding.

Next appointment: {next_visit_date}
Patient contact: {phone_mobile}

{attending_physician}, MD
NPI: {physician_npi}
Note signed: {note_date}
""",

    # Variant 2: Condensed style
    """{facility_name} | {city}, {state}

OFFICE VISIT NOTE
{visit_date}

Pt: {last_name}, {first_name} | MRN {mrn} | DOB {date_of_birth}

CC: Follow-up {primary_diagnosis}

HPI: {hpi_narrative}

Meds: {medication_list_narrative}
Allergies: {allergy_list_simple}

VS: {bp_systolic}/{bp_diastolic}, P{heart_rate}, T{temperature}, Wt {weight}#
Exam: {general_exam}. {cv_exam}. {resp_exam}. {abd_exam}.

A/P:
{assessment_plan}
{clinical_reasoning}

Discussed plan with patient who agrees and understands.
F/u {next_visit_date} or prn. Can reach at {phone_mobile}.

{attending_physician}, MD (NPI {physician_npi})
Signed {note_date}
""",

    # Variant 3: Narrative-heavy style
    """{facility_name}
Department of Internal Medicine
{facility_address}, {city}, {state} {zip_code}

OUTPATIENT PROGRESS NOTE

PATIENT INFORMATION:
Name: {last_name}, {first_name}
Medical Record Number: {mrn}
Date of Birth: {date_of_birth} (Age: {age} years)
Date of Service: {visit_date}
Attending Physician: Dr. {attending_physician}

HISTORY OF PRESENT ILLNESS:
{hpi_narrative}

Patient is currently taking the following medications: {medication_list_narrative}. Reports good adherence with no missed doses. Known drug allergies: {allergy_list_simple}.

VITAL SIGNS:
Blood Pressure: {bp_systolic}/{bp_diastolic} mmHg
Heart Rate: {heart_rate} bpm
Temperature: {temperature}°F
Weight: {weight} lbs
Respiratory Rate: {resp_rate} /min

PHYSICAL EXAMINATION:
General Appearance: {general_exam}
Cardiovascular: {cv_exam}
Respiratory: {resp_exam}
Abdominal: {abd_exam}

CLINICAL IMPRESSION AND PLAN:
{assessment_plan}

{clinical_reasoning}

The patient demonstrates good understanding of the treatment plan and has been counseled regarding warning signs requiring immediate medical attention. Contact information on file: {phone_mobile}.

Follow-up scheduled for {next_visit_date}.

Electronically signed by Dr. {attending_physician}
Provider NPI: {physician_npi}
Document date/time: {note_date}
"""
]

DISCHARGE_SUMMARY_VARIANTS = [
    # Variant 1: Comprehensive format
    """{facility_name}
{facility_address}
{city}, {state} {zip_code}

DISCHARGE SUMMARY

PATIENT: {last_name}, {first_name}
MRN: {mrn}
DOB: {date_of_birth}
AGE: {age} years
ADMISSION: {admission_date}
DISCHARGE: {discharge_date}
ATTENDING: Dr. {attending_physician}

ADMITTING DIAGNOSIS: {admission_diagnosis}
DISCHARGE DIAGNOSIS: {discharge_diagnosis_list}

HOSPITAL COURSE:
{first_name} {last_name} is a {age}-year-old {gender} admitted on {admission_date} with {admission_diagnosis}. {hospital_course_narrative}

Initial labs showed {initial_labs}. Imaging studies {imaging_findings}. Patient was started on {treatment_regimen}.

Consultations obtained:
- Cardiology (Dr. {consultant1}): {consult_recommendation1}
- {specialty2} (Dr. {consultant2}): {consult_recommendation2}

{clinical_progress}

By discharge on {discharge_date}, patient was {discharge_status}.

DISCHARGE MEDICATIONS:
{discharge_med_list}

DISCHARGE INSTRUCTIONS:
{discharge_instructions}

FOLLOW-UP CARE:
- PCP Dr. {pcp_name} in 1-2 weeks (call {pcp_phone} to schedule)
- {specialty1} follow-up as arranged
- Return to ED for {warning_signs}

CONDITION AT DISCHARGE: {discharge_condition}

Patient and family educated regarding discharge plan and expressed understanding. All questions answered.

Attending Physician: Dr. {attending_physician}
License: {physician_license}
Dictated: {discharge_date}
Authenticated: {note_date}
""",

    # Variant 2: Brief discharge summary
    """{facility_name} - DISCHARGE SUMMARY

Patient: {last_name}, {first_name} | MRN {mrn} | DOB {date_of_birth}
Admitted: {admission_date} | Discharged: {discharge_date}

DIAGNOSES:
1. {admission_diagnosis}
2. {secondary_diagnosis}

BRIEF HOSPITAL COURSE:
{age} y.o. {gender} admitted with {admission_diagnosis}. {hospital_course_brief} Consulted {specialty1} and {specialty2}. {treatment_summary} Patient improved and ready for discharge.

DISCHARGE MEDS: {discharge_med_list}

FOLLOW-UP:
Dr. {pcp_name} ({pcp_phone}) in 1-2 weeks
{specialty1} clinic prn

INSTRUCTIONS: {discharge_instructions_brief}

Dr. {attending_physician} (Lic# {physician_license})
Completed {note_date}
"""
]

CONSULTATION_NOTE_VARIANTS = [
    """{facility_name}
CARDIOLOGY CONSULTATION

PATIENT: {last_name}, {first_name}
MRN: {mrn} | DOB: {date_of_birth} | Age: {age}
Consultation Date: {consult_date}
Requesting Physician: Dr. {referring_physician}
Location: {visit_location}

REASON FOR CONSULTATION:
Cardiology evaluation for {consult_reason} in patient with known {primary_diagnosis}.

HISTORY OF PRESENT ILLNESS:
{first_name} {last_name} is a {age}-year-old {gender} referred for cardiology assessment. {consult_hpi} Past medical history significant for {comorbidity1}, {comorbidity2}, and {comorbidity3}.

Current cardiac medications: {cardiac_meds}

REVIEW OF SYSTEMS:
Cardiovascular: {cv_review}
Respiratory: {resp_review}
Constitutional: {constitutional_review}

PHYSICAL EXAMINATION:
Vital Signs: BP {bp_systolic}/{bp_diastolic}, HR {heart_rate}, RR {resp_rate}, T {temperature}F
General: {general_exam}
Cardiovascular: {cv_exam_detailed}
Pulmonary: {lung_findings}
Extremities: {extremity_exam}

DIAGNOSTIC DATA REVIEWED:
ECG ({ecg_date}): {ecg_findings}
Echocardiogram ({echo_date}): {echo_findings}
Labs ({lab_date}): {lab_findings}

ASSESSMENT:
{assessment_detailed}

RECOMMENDATIONS:
1. {recommendation1}
2. {recommendation2}
3. {recommendation3}
4. {recommendation4}
5. Follow-up in {followup_interval}

Thank you for this interesting consultation. I will continue to follow. Please contact me at {consult_phone} with questions or concerns.

{consultant_name}, MD, FACC
Board Certified - Cardiovascular Disease
NPI: {consultant_npi}
""",

    """{facility_name} - CONSULTATION REPORT

Pt: {last_name}, {first_name} ({age}y.o. {gender})
MRN {mrn} | DOB {date_of_birth}
Date: {consult_date}
Consulting Service: CARDIOLOGY
Requesting MD: {referring_physician}

REASON: {consult_reason}

HPI: {consult_hpi_brief} PMH: {primary_diagnosis}, {comorbidity1}, {comorbidity2}.

Meds: {cardiac_meds}

ROS: {ros_brief}

PE: VS: {bp_systolic}/{bp_diastolic}, HR {heart_rate}. {general_exam}. CV: {cv_exam_detailed}. Lungs: {lung_findings}.

DATA: ECG {ecg_findings}. Echo {echo_findings}. Labs {lab_findings}.

IMPRESSION: {assessment_brief}

PLAN:
{recommendation1}
{recommendation2}
{recommendation3}
F/u cardiology clinic {followup_interval}

{consultant_name}, MD | NPI {consultant_npi}
{note_date}
"""
]

LAB_REPORT_VARIANTS = [
    """{facility_name} - Laboratory Services
{facility_address}, {city}, {state} {zip_code}
Phone: {lab_phone} | Fax: {lab_fax}

LABORATORY REPORT

PATIENT: {last_name}, {first_name}
MRN: {mrn}
DOB: {date_of_birth}
AGE/SEX: {age} / {gender}

COLLECTION DATE/TIME: {collection_date} {collection_time}
RECEIVED: {received_datetime}
REPORTED: {report_date}

ORDERING PROVIDER: Dr. {ordering_physician}
Phone: {provider_phone}

TEST ORDERED: {test_panel_name}

RESULTS:
{detailed_lab_results}

{abnormal_flags}

REFERENCE RANGES PROVIDED

INTERPRETATION:
{test_interpretation}

{critical_value_note}

Performed by: {lab_name}
CLIA #: {clia_number}
Medical Director: {medical_director}, MD

Report electronically signed {note_date}
""",

    """{lab_name} | CLIA# {clia_number}
{city}, {state} | Ph: {lab_phone}

LAB REPORT

Pt: {last_name}, {first_name} | MRN {mrn} | DOB {date_of_birth}
Collected: {collection_date} | Resulted: {report_date}
Ordering MD: {ordering_physician} ({provider_phone})

{test_panel_name}:
{concise_lab_results}

{abnormal_note}

{critical_call_note}

Dir: {medical_director}, MD | {note_date}
"""
]

OPERATIVE_NOTE_VARIANTS = [
    """{facility_name}
OPERATIVE REPORT

PATIENT: {last_name}, {first_name}
MRN: {mrn} | DOB: {date_of_birth}
DATE OF SURGERY: {surgery_date}
LOCATION: {or_location}

PREOPERATIVE DIAGNOSIS: {preop_diagnosis}
POSTOPERATIVE DIAGNOSIS: {postop_diagnosis}
PROCEDURE: {procedure_name}

SURGEON: Dr. {surgeon_name}
ASSISTANT: Dr. {assistant_name}
ANESTHESIA: {anesthesia_type} - Dr. {anesthesiologist}

INDICATIONS:
{first_name} {last_name} is a {age}-year-old {gender} with {indication_detail}. {indication_narrative} After thorough discussion of risks, benefits, and alternatives including {alternatives}, patient provided informed consent.

DESCRIPTION OF PROCEDURE:
{procedure_description_detailed}

The procedure was completed successfully without intraoperative complications.

FINDINGS: {operative_findings}
EBL: {ebl} mL
FLUIDS: {fluids_given}
SPECIMENS: {specimen_description}
DRAINS: {drain_description}
DISPOSITION: {disposition}

Patient tolerated procedure well and transferred to {post_location} in stable condition.

SURGEON: Dr. {surgeon_name}
License: {surgeon_license}

Dictated: {surgery_date}
Transcribed: {note_date}
""",

    """{facility_name} - OR NOTE

Pt: {last_name}, {first_name} | MRN {mrn} | DOB {date_of_birth}
Date: {surgery_date}

Preop Dx: {preop_diagnosis}
Postop Dx: {postop_diagnosis}
Procedure: {procedure_name}

Surgeon: {surgeon_name} | Assist: {assistant_name} | Anes: {anesthesiologist}

Indications: {age} y.o. {gender} with {indication_detail}. {indication_narrative}

Procedure: {procedure_description_brief}

Findings: {operative_findings}
EBL: {ebl}mL | Complications: {complications}
Specimens: {specimen_description}

Patient to {post_location} stable.

Dr. {surgeon_name} (Lic {surgeon_license})
Signed {note_date}
"""
]

def get_realistic_template(doc_type: str) -> str:
    """Get a random realistic template for the specified document type."""
    template_map = {
        'progress_note': PROGRESS_NOTE_VARIANTS,
        'discharge_summary': DISCHARGE_SUMMARY_VARIANTS,
        'consultation_note': CONSULTATION_NOTE_VARIANTS,
        'lab_report_focused': LAB_REPORT_VARIANTS,
        'operative_note': OPERATIVE_NOTE_VARIANTS
    }

    variants = template_map.get(doc_type, PROGRESS_NOTE_VARIANTS)
    return random.choice(variants)

def get_clinical_phrase(category: str, subcategory: str = None) -> str:
    """Get a random clinical phrase from the vocabulary."""
    if subcategory:
        options = CLINICAL_VOCABULARY.get(category, {}).get(subcategory, ['Normal'])
    else:
        options = CLINICAL_VOCABULARY.get(category, ['Normal finding'])
    return random.choice(options)
