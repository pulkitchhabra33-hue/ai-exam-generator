import json
import os
import uuid

from typing import List, Optional

from fastapi import (
    APIRouter,
    HTTPException,
    Header,
    UploadFile,
    File,
    Form
)

from collections import Counter

from fastapi.responses import FileResponse
from jose import jwt

from backend.services.generation_pipeline import (
    generate_exam_paper
)

from backend.services.pdf_service import (
    generate_pdf
)

from backend.schemas.request_models import (
    TeacherRequest
)

from backend.database import SessionLocal

from backend.models import (
    User,
    GuestSession
)

from backend.validators.question_type_validator import normalize_question_type


router = APIRouter()

def validate_generated_question_counts(
    paper,
    teacher_data
):
    """
Final safety check before PDF generation.

The PDF must only be created when the generated paper
contains exactly the number of questions requested by
the teacher, both per section and per question type.
    """

    generated_sections= paper.get(
        "sections",
        []
    )

    expected_sections= teacher_data.sections

    #SECTION COUNT

    if len(generated_sections) != len(expected_sections):
        raise HTTPException(
            status_code=500,
            detail= (
                "Generated section count mismatch: "
                f"expected {len(expected_sections)},"
                f"got {len(generated_sections)}."
            )
        )

    expected_total= 0
    generated_total= 0

    # CHECK EACH SECTION

    for section_index, expected_section in enumerate(
        expected_sections
    ):
        generated_section= generated_sections[
            section_index
        ]

        expected_count= int(
            expected_section.question_count
        )

        generated_questions= generated_section.get(
            "questions",
            []
        )

        generated_count= len(
            generated_questions
        )

        expected_total += expected_count
        generated_total += generated_count

        # SECTION QUESTION COUNT

        if generated_count != expected_count:
            raise HTTPException(
                status_code=500,
                detail=(
                    f"Question count mismatch in "
                    f"{expected_section.section_name}: "
                    f"expected {expected_count}, "
                    f"got {generated_count}."
                )
            )

        # EXPECTED QUESTION-TYPE COUNTS

        expected_types= Counter()

        for group in expected_section.question_groups:
            question_type= normalize_question_type(
                group.question_type
            )

            expected_types[question_type] += int(
                group.question_count
            )

        # GENERATED QUESTION-TYPE COUNTS

        generated_types= Counter()

        for question in generated_questions:
            question_type= normalize_question_type(
                question.get(
                    "question_type",
                    ""
                )
            )

            if not question_type:
                raise HTTPException(
                    status_code=500,
                    detail= (
                        f"A generated question in "
                        f"{expected_section.section_name} "
                        "is missing question_type."
                    )
                )

            generated_types[
                question_type
            ] += 1

        # QUESTION-TYPE COUNT CHECK

        if generated_types != expected_types:
            raise HTTPException(
                status_code=500,
                detail=(
                    f"Question type count mismatch in "
                    f"{expected_section.section_name}: "
                    f"expected {dict(expected_types)}, "
                    f"got {dict(generated_types)}."
                )
            )

    # TOTAL QUESTION COUNT

    if generated_total != expected_total:
        raise HTTPException(
            status_code=500,
            detail=(
                "Total question count mismatch: "
                f"expected {expected_total}, "
                f"got {generated_total}."
            )
        )

    return generated_total


# ============================================================
# OPTIONAL USER AUTHENTICATION
# ============================================================

def get_optional_user(
        authorization: Optional[str]
):
    if not authorization:
        return None

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code= 401,
            detail= "AUTHENTICATION_REQUIRED"
        )

    token= authorization.split(" ", 1)[1]

    try:
        secret_key= os.getenv("SECRET_KEY")
        payload= jwt.decode(
            token,
            secret_key,
            algorithms= ["HS256"]
        )

        email= payload.get("sub")

        if not email:
            raise HTTPException(
                status_code= 401,
                detail= "AUTHENTICATION_REQUIRED"
            )

        db= SessionLocal()

        try:
            user= (
                db.query(User)
                .filter(User.email == email)
                .first()
            )

        finally:
            db.close()

        if not user:
            raise HTTPException(
                status_code= 401,
                detail= "AUTHENTICATION_REQUIRED"
            )

        return user

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code= 401,
            detail= "AUTHENTICATION_REQUIRED"
        )

# ============================================================
# GUEST CREDITS
# ============================================================

@router.get(
    "/guest-credits"
)
def get_guest_credits(
    x_guest_id: Optional[str] = Header(
        default=None
    )
):

    if not x_guest_id:

        return {
            "credits": 0
        }

    db = SessionLocal()

    try:

        guest = (
            db.query(GuestSession)
            .filter(
                GuestSession.guest_id
                == x_guest_id
            )
            .first()
        )

        if not guest:

            return {
                "credits": 0
            }

        return {
            "credits":
                guest.credits_remaining
        }

    finally:

        db.close()


# ============================================================
# GENERATE PAPER
# ============================================================

@router.post(
    "/generate-paper",
    summary="Generate AI Exam Paper"
)
def generate(

    data: str = Form(...),

    files: List[UploadFile] = File(
        default=[]
    ),

    include_answers: bool = Form(
        default=True
    ),

    authorization: Optional[str] = Header(
        default=None
    ),

    x_guest_id: Optional[str] = Header(
        default=None
    )
):

    # ========================================================
    # PARSE TEACHER DATA
    # ========================================================

    try:

        data_dict = json.loads(
            data
        )

        teacher_data = TeacherRequest(
            **data_dict
        )

    except Exception as error:

        raise HTTPException(
            status_code=422,
            detail=(
                f"Invalid exam data: {error}"
            )
        )


    # ========================================================
    # DATABASE
    # ========================================================

    db = SessionLocal()


    try:

        # ====================================================
        # IDENTIFY USER
        # ====================================================

        user = get_optional_user(
            authorization
        )

        print(
            "[DEBUG] user:",
            user,
            "type:",
            type(user),
            flush=True
        )

        guest = None


        # ====================================================
        # CREDIT COST
        # ====================================================

        credit_cost= 2 if teacher_data.exam_type else 1

        # ====================================================
        # AUTHENTICATED USER
        # ====================================================

        if user:

            if (
                user.credits_remaining
                < credit_cost
            ):

                raise HTTPException(
                    status_code=403,
                    detail="NO_CREDITS"
                )


        # ====================================================
        # GUEST USER
        # ====================================================

        else:

            # ------------------------------------------------
            # Find existing guest
            # ------------------------------------------------

            if x_guest_id:

                guest = (
                    db.query(GuestSession)
                    .filter(
                        GuestSession.guest_id
                        == x_guest_id
                    )
                    .first()
                )


            # ------------------------------------------------
            # Create guest if necessary
            # ------------------------------------------------

            if not guest:

                guest_id = (
                    x_guest_id
                    if x_guest_id
                    else str(uuid.uuid4())
                )

                guest = GuestSession(
                    guest_id=guest_id,
                    credits_remaining=2
                )

                db.add(
                    guest
                )

                db.commit()

                db.refresh(
                    guest
                )


            # ------------------------------------------------
            # Check guest credits
            # ------------------------------------------------

            if (
                guest.credits_remaining
                < credit_cost
            ):

                raise HTTPException(
                    status_code=403,
                    detail="NO_CREDITS"
                )


        # ====================================================
        # GENERATE AI PAPER
        # ====================================================

        try:
            print("[GEN] Before OpenAI call", flush=True)

            result = generate_exam_paper(
                teacher_data.model_dump()
            )

            print("[GEN] After OpenAI call", flush=True)

        except Exception as error:

            raise HTTPException(
                status_code=500,
                detail=(
                    f"Paper generation failed: {error}"
                )
            )


        # ====================================================
        # CHECK GENERATION RESULT
        # ====================================================

        if not result.get(
            "success",
            False
        ):

            raise HTTPException(
                status_code=500,
                detail=result.get(
                    "error",
                    "Paper generation failed."
                )
            )


        # ====================================================
        # EXTRACT GENERATED PAPER
        # ====================================================

        try:

            final_result = result[
                "result"
            ]

            paper = final_result[
                "paper"
            ]

        except Exception as error:

            raise HTTPException(
                status_code=500,
                detail=(
                    "Generated paper format "
                    f"is invalid: {error}"
                )
            )


        # ====================================================
        # ADD TEACHER INFORMATION
        # ====================================================

        paper[
            "class_name"
        ] = (
            teacher_data.class_name
            or ""
        )

        paper[
            "subject"
        ] = (
            teacher_data.subject
            or ""
        )

        paper[
            "total_marks"
        ] = (
            teacher_data.total_marks
            or 0
        )

        paper[
            "exam_type"
        ] = (
            teacher_data.exam_type
            or ""
        )


        # ====================================================
        # FINAL QUESTION COUNT SAFETY CHECK
        # ====================================================

        validate_generated_question_counts(
            paper,
            teacher_data
        )

        # ====================================================
        # GENERATE PDF
        # ====================================================

        try:

            print(
                "[GEN] Before PDF generation",
                flush=True
            )

            filename = f"paper_{uuid.uuid4().hex}.pdf"

            file_path = generate_pdf(
                paper,
                filename=filename,
                include_answers=(
                    include_answers
                )
            )

            print("[GEN] After PDF generation", flush=True)

        except Exception as error:
            import traceback
            print(
                "[PDF ERROR]",
                repr(error),
                flush=True
            )
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=(
                    f"PDF generation failed: {error}"
                )
            )


        # ====================================================
        # VERIFY PDF
        # ====================================================

        if not file_path:

            raise HTTPException(
                status_code=500,
                detail="PDF generation failed."
            )

        if not os.path.exists(
            file_path
        ):

            raise HTTPException(
                status_code=500,
                detail="Generated PDF file not found."
            )


        # ====================================================
        # DEDUCT CREDITS
        #
        # IMPORTANT:
        # Credits are deducted ONLY after
        # successful AI + PDF generation.
        # ====================================================

        if user:

            user.credits_remaining -= (
                credit_cost
            )

            credits_remaining = (
                user.credits_remaining
            )

        else:

            guest.credits_remaining -= (
                credit_cost
            )

            credits_remaining = (
                guest.credits_remaining
            )


        db.commit()


        # ====================================================
        # RETURN RESPONSE
        # ====================================================

        filename = os.path.basename(
            file_path
        )

        return {

            "success": True,

            "message":
                "Paper generated successfully.",

            "download_url":
                f"/download/{filename}",

            "credits_used":
                credit_cost,

            "credits_remaining":
                credits_remaining

        }


    except HTTPException:

        db.rollback()

        raise


    except Exception as error:

        db.rollback()

        print(
            f"GENERATION ROUTE ERROR: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Paper generation failed: {error}"
            )
        )


    finally:

        db.close()


# ============================================================
# DOWNLOAD GENERATED PDF
# ============================================================

@router.get(
    "/download/{filename}"
)

def download_file(filename: str):
    pdf_folder= os.path.abspath(
        os.path.join(
            "backend",
            "pdfs"
        )
    )

    safe_filename= os.path.basename(filename)

    file_path= os.path.abspath(
        os.path.join(
            pdf_folder,
            safe_filename
        )
    )

    #Prevent Path Traversal
    if (
        os.path.commonpath(
            [
                pdf_folder,
                file_path
            ]
        )
        != pdf_folder
    ):
        raise HTTPException(
            status_code=404,
            detail= "PDF file not found."
        )

    if not os.path.isfile(
        file_path
    ):
        raise HTTPException(
            status_code=404,
            detail="PDF file not found."
        )

    return FileResponse(
        path= file_path,
        media_type= "application/pdf",
        filename= safe_filename
    )