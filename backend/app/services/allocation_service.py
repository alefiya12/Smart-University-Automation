"""
services/allocation_service.py — Core allocation algorithm logic.
"""
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from math import floor

from app.models.course import Course
from app.models.admission_staging import (
    AdmissionStaging, 
    AdmissionStatus, 
    AllocatedSeatType, 
    CandidateCategory
)

def run_allocation_for_all_courses(db: Session):
    """Runs the full algorithm for all courses that have pending staging records."""
    courses = db.query(Course).all()
    results = {}
    for course in courses:
        res = allocate_seats_for_course(db, course.id)
        results[course.id] = res
    db.commit()
    return results

def allocate_seats_for_course(db: Session, course_id: int):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        return {"error": "Course not found"}

    # STAGE 1: Calculate Category Quotas
    total = course.total_seats
    obc_seats = floor(total * (course.quota_obc / 100.0))
    sc_seats = floor(total * (course.quota_sc / 100.0))
    st_seats = floor(total * (course.quota_st / 100.0))
    ews_seats = floor(total * (course.quota_ews / 100.0))
    
    reserved_total = obc_seats + sc_seats + st_seats + ews_seats
    open_seats = total - reserved_total
    
    # Get all pending records for this course
    candidates: List[AdmissionStaging] = db.query(AdmissionStaging).filter(
        AdmissionStaging.applied_course_id == course_id,
        AdmissionStaging.final_admission_status == AdmissionStatus.PENDING
    ).all()
    
    if not candidates:
        return {"processed": 0, "course": course.name}
        
    stats = {
        "processed": len(candidates),
        "rejected": 0,
        "admitted_open": 0,
        "admitted_reserved": 0,
        "waitlisted": 0
    }

    # STAGE 2: Two-Pass Eligibility Selection Filter
    eligible_candidates = []
    
    for c in candidates:
        # Determine specific thresholds based on category
        relax_pct = 0.0
        if c.candidate_category in [CandidateCategory.SC, CandidateCategory.ST]:
            relax_pct = course.relaxation_sc_st_pct
        elif c.candidate_category in [CandidateCategory.OBC, CandidateCategory.EWS]:
            relax_pct = course.relaxation_obc_ews_pct
            
        required_12_pct = course.min_class_12_pct - relax_pct
        required_core = course.min_core_subject_score - relax_pct
        
        # Check eligibility
        if c.class_12_pct < required_12_pct:
            c.final_admission_status = AdmissionStatus.REJECTED_INELIGIBLE
            c.reason_code_logs = f"Rejected: Class 12 Pct ({c.class_12_pct}) below threshold ({required_12_pct})"
            stats["rejected"] += 1
        elif c.core_subject_score < required_core:
            c.final_admission_status = AdmissionStatus.REJECTED_INELIGIBLE
            c.reason_code_logs = f"Rejected: Core Score ({c.core_subject_score}) below threshold ({required_core})"
            stats["rejected"] += 1
        else:
            eligible_candidates.append(c)

    if not eligible_candidates:
        return stats

    # STAGE 3: Merit Sorting & Compliance Seat Allocation
    # Helper to sort candidates according to Tie-Breaking rules
    # 1. Entrance_Exam_Score DESC
    # 2. Core_Subject_Score DESC
    # 3. Class_12_Pct DESC
    # 4. Date_Of_Birth ASC (older preferred, meaning smaller date value)
    
    def sort_key(c: AdmissionStaging):
        return (
            -c.entrance_exam_score,
            -c.core_subject_score,
            -c.class_12_pct,
            c.date_of_birth.toordinal() if c.date_of_birth else 0
        )
    
    eligible_candidates.sort(key=sort_key)
    
    unallocated = []
    
    # 3.1: Open Merit Phase (All Categories)
    for c in eligible_candidates:
        if stats["admitted_open"] < open_seats:
            c.final_admission_status = AdmissionStatus.ELIGIBLE_FOR_ADMISSION
            c.allocated_seat_type = AllocatedSeatType.OPEN_MERIT
            c.reason_code_logs = f"Eligible via Open Merit Rank #{stats['admitted_open'] + 1}"
            stats["admitted_open"] += 1
        else:
            unallocated.append(c)
            
    # 3.2: Reserved Quota Phase
    quotas = {
        CandidateCategory.OBC: {"limit": obc_seats, "filled": 0},
        CandidateCategory.SC: {"limit": sc_seats, "filled": 0},
        CandidateCategory.ST: {"limit": st_seats, "filled": 0},
        CandidateCategory.EWS: {"limit": ews_seats, "filled": 0},
    }
    
    waitlist_pool = []
    
    for c in unallocated:
        cat = c.candidate_category
        if cat in quotas:
            q = quotas[cat]
            if q["filled"] < q["limit"]:
                c.final_admission_status = AdmissionStatus.ELIGIBLE_FOR_ADMISSION
                c.allocated_seat_type = AllocatedSeatType.RESERVED_QUOTA
                c.reason_code_logs = f"Eligible via {cat.value} Quota Rank #{q['filled'] + 1}"
                q["filled"] += 1
                stats["admitted_reserved"] += 1
            else:
                waitlist_pool.append(c)
        else:
            waitlist_pool.append(c)
            
    # STAGE 4: State Transition & Data Commitment for Waitlist
    # Note: waitlist_pool is already sorted by merit
    waitlist_rank = 1
    for c in waitlist_pool:
        c.final_admission_status = AdmissionStatus.WAITLISTED
        c.waitlist_rank = waitlist_rank
        c.reason_code_logs = f"Waitlisted: Overall Rank #{waitlist_rank}"
        stats["waitlisted"] += 1
        waitlist_rank += 1

    return stats
