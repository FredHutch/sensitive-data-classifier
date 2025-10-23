"""
Realistic Medical Document Templates

These templates create documents that closely approximate real medical records
for benchmarking PHI classification systems. PHI is embedded naturally in
clinical narrative rather than structured lists.

Key characteristics:
- 20-50 PHI identifiers per document (realistic density)
- Narrative clinical notes style
- Natural embedding of identifiers in context
- Varied document types with appropriate content
- Mimics actual EHR/medical record output
"""

REALISTIC_TEMPLATES = {
    'progress_note': """
{facility_name}
{city}, {state} {zip_code}

PROGRESS NOTE

Patient: {last_name}, {first_name}
MRN: {mrn}
DOB: {date_of_birth}
Date of Service: {visit_date}

CHIEF COMPLAINT:
Patient presents for follow-up of {primary_diagnosis}.

HISTORY OF PRESENT ILLNESS:
{first_name} {last_name} is a {age}-year-old {gender} with a history of {primary_diagnosis} who presents today for routine follow-up. Patient reports {complaint_detail}. Medications have been taken as prescribed. No new concerns since last visit on {last_visit_date}. Patient can be reached at {phone_mobile} if needed for follow-up.

CURRENT MEDICATIONS:
{medication_list_narrative}

ALLERGIES:
{allergy_list_simple}

VITAL SIGNS:
BP: {bp_systolic}/{bp_diastolic}, HR: {heart_rate}, Temp: {temperature}°F, Wt: {weight} lbs

PHYSICAL EXAMINATION:
General: Well-appearing, in no acute distress
Cardiovascular: Regular rate and rhythm, no murmurs
Respiratory: Clear to auscultation bilaterally
Abdomen: Soft, non-tender, non-distended

ASSESSMENT AND PLAN:
1. {primary_diagnosis} - Continue current management. Patient doing well on current regimen. Will continue {med1} and {med2}. Follow-up in 3 months.

2. Health maintenance - Patient due for preventive care screening. Discussed importance of routine monitoring.

Patient verbalized understanding of treatment plan and agrees to continue current medications.

FOLLOW-UP:
Scheduled for {next_visit_date}
Patient may contact office at {facility_phone}

Electronically signed by:
Dr. {attending_physician}
NPI: {physician_npi}

Note completed: {note_date}
""",

    'discharge_summary': """
{facility_name}
{facility_address}
{city}, {state} {zip_code}

DISCHARGE SUMMARY

Patient Name: {last_name}, {first_name}
Medical Record #: {mrn}
Date of Birth: {date_of_birth}
Admission Date: {admission_date}
Discharge Date: {discharge_date}

ADMITTING DIAGNOSIS:
{admission_diagnosis}

DISCHARGE DIAGNOSIS:
{primary_diagnosis}

HOSPITAL COURSE:
{first_name} {last_name}, a {age}-year-old {gender}, was admitted on {admission_date} with {admission_diagnosis}. The patient's clinical course during this hospitalization was notable for {clinical_course_detail}.

Initial laboratory studies revealed {lab_finding1}. Serial monitoring showed {lab_finding2}. The patient was managed with {treatment1} and {treatment2}.

Throughout the hospital stay, the patient was followed by cardiology (Dr. {consultant1}) and pulmonology (Dr. {consultant2}). Consultants recommended {consultation_recommendation}.

The patient's condition improved steadily, and by {improvement_date}, vital signs were stable and laboratory values were trending toward normal ranges.

DISCHARGE MEDICATIONS:
{discharge_med_list}

DISCHARGE INSTRUCTIONS:
1. Follow up with Dr. {pcp_name} in 1-2 weeks
2. Call {pcp_phone} to schedule appointment
3. Continue all medications as prescribed
4. Return to emergency department if symptoms worsen

FOLLOW-UP CARE:
Primary care with Dr. {pcp_name} at {pcp_phone}
Cardiology follow-up as needed

The patient and family verbalized understanding of discharge instructions and medication regimen.

ATTENDING PHYSICIAN:
Dr. {attending_physician}
License: {physician_license}

Report electronically authenticated on {discharge_date}
""",

    'consultation_note': """
{facility_name}
CARDIOLOGY CONSULTATION

Patient: {last_name}, {first_name}
MRN: {mrn} | DOB: {date_of_birth} | Age: {age}
Date: {consult_date}
Requesting Physician: Dr. {referring_physician}

REASON FOR CONSULTATION:
Evaluation of {consult_reason} in patient with known history of {primary_diagnosis}.

HISTORY:
Patient {first_name} {last_name} is a {age}-year-old {gender} referred for cardiology evaluation. The patient reports {symptom_description}. Symptoms began approximately {symptom_duration}. Past medical history is significant for {comorbidity1} and {comorbidity2}.

Current medications include {med1}, {med2}, and {med3}.

REVIEW OF SYSTEMS:
Cardiovascular: {cv_review}
Respiratory: Denies shortness of breath at rest
Other systems: As documented in chart

PHYSICAL EXAMINATION:
Vital Signs: BP {bp_systolic}/{bp_diastolic}, HR {heart_rate}, RR {resp_rate}
Cardiovascular: {cv_exam_findings}
Lungs: {lung_findings}

DIAGNOSTIC DATA REVIEWED:
ECG ({ecg_date}): {ecg_findings}
Recent labs ({lab_date}): {relevant_labs}

ASSESSMENT:
{assessment_paragraph}

RECOMMENDATIONS:
1. {recommendation1}
2. {recommendation2}
3. {recommendation3}
4. Follow-up in clinic in {followup_interval}

Thank you for this consultation. Please contact me at {consult_phone} with any questions.

{consultant_name}, MD
Board Certified, Cardiovascular Disease
NPI: {consultant_npi}
""",

    'operative_note': """
{facility_name}
OPERATIVE REPORT

Patient: {last_name}, {first_name}
MRN: {mrn}
DOB: {date_of_birth}
Date of Surgery: {surgery_date}

PREOPERATIVE DIAGNOSIS:
{preop_diagnosis}

POSTOPERATIVE DIAGNOSIS:
{postop_diagnosis}

PROCEDURE PERFORMED:
{procedure_name}

SURGEON: Dr. {surgeon_name}
ASSISTANT: Dr. {assistant_name}
ANESTHESIA: General endotracheal, provided by Dr. {anesthesiologist}

INDICATIONS:
{first_name} {last_name} is a {age}-year-old {gender} with {indication_detail}. After discussion of risks, benefits, and alternatives, the patient provided informed consent for the procedure.

PROCEDURE IN DETAIL:
The patient was brought to the operating room and placed in supine position. After induction of general anesthesia, the surgical site was prepped and draped in sterile fashion.

{procedure_description}

The procedure was completed without complications. Estimated blood loss was {ebl}mL. The patient tolerated the procedure well and was transferred to the post-anesthesia care unit in stable condition.

SPECIMENS: {specimen_description} sent to pathology
DRAINS: {drain_description}
COMPLICATIONS: None

Dr. {surgeon_name}
License #: {surgeon_license}
Procedure completed: {surgery_date}
""",

    'lab_report_focused': """
{facility_name} - Laboratory Services
Phone: {lab_phone}

LABORATORY REPORT

Patient: {last_name}, {first_name}
MRN: {mrn}
DOB: {date_of_birth}
Collection Date: {collection_date}

Ordering Provider: Dr. {ordering_physician}
Phone: {provider_phone}

TEST: {test_panel_name}

RESULTS:
{test_results_narrative}

INTERPRETATION:
{test_interpretation}

Critical values called to Dr. {ordering_physician} on {call_date} at {call_time} by {tech_name}.

Report Date: {report_date}
Performed by: {lab_name}, CLIA# {clia_number}

Medical Director: Dr. {medical_director}
"""
}

def get_realistic_template(doc_type: str) -> str:
    """Get a realistic template for the specified document type."""
    return REALISTIC_TEMPLATES.get(doc_type, REALISTIC_TEMPLATES['progress_note'])
