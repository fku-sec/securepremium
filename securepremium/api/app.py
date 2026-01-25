"""FastAPI application and route setup."""

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

from securepremium.storage import (
    init_db,
    SchemaManager,
    DeviceRepository,
    RiskAssessmentRepository,
    PremiumRepository,
    ThreatReportRepository,
    NetworkParticipantRepository,
)
from securepremium.core.risk_calculator import RiskCalculator
from securepremium.core.premium_engine import PremiumEngine

from .schemas import (
    DeviceRegisterRequest,
    DeviceResponse,
    DeviceListResponse,
    RiskAssessmentRequest,
    RiskAssessmentResponse,
    RiskHistoryResponse,
    PremiumQuoteRequest,
    PremiumResponse,
    PremiumHistoryResponse,
    ThreatReportRequest,
    ThreatReportResponse,
    ThreatListResponse,
    ParticipantRegisterRequest,
    ParticipantResponse,
    ParticipantListResponse,
    ParticipantStatsRequest,
    HealthResponse,
    ErrorResponse,
    StatsResponse,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize FastAPI app
app = FastAPI(
    title="Securepremium API",
    description="Device Behavior Insurance Protocol - REST API",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = init_db()
db.initialize()

# Initialize schema
SchemaManager.create_all_tables()

# Core engines
risk_calculator = RiskCalculator()
premium_engine = PremiumEngine()


# ========================
# Dependency Functions
# ========================

def get_device_repo():
    """Get device repository."""
    session = db.get_session()
    return DeviceRepository(session)


def get_assessment_repo():
    """Get assessment repository."""
    session = db.get_session()
    return RiskAssessmentRepository(session)


def get_premium_repo():
    """Get premium repository."""
    session = db.get_session()
    return PremiumRepository(session)


def get_threat_repo():
    """Get threat repository."""
    session = db.get_session()
    return ThreatReportRepository(session)


def get_participant_repo():
    """Get participant repository."""
    session = db.get_session()
    return NetworkParticipantRepository(session)


# ========================
# Health & Status
# ========================

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="0.1.0",
        database="connected"
    )


@app.get("/api/stats", response_model=StatsResponse)
async def get_stats(
    device_repo: DeviceRepository = Depends(get_device_repo),
    assessment_repo: RiskAssessmentRepository = Depends(get_assessment_repo),
    threat_repo: ThreatReportRepository = Depends(get_threat_repo),
    participant_repo: NetworkParticipantRepository = Depends(get_participant_repo),
):
    """Get system statistics."""
    try:
        devices = device_repo.get_all_active(limit=1)
        assessments = assessment_repo.get_recent(days=30, limit=1)
        threats = threat_repo.get_unverified(limit=1)
        participants = participant_repo.get_all_active(limit=1)
        
        return StatsResponse(
            total_devices=len(devices) if devices else 0,
            total_assessments=len(assessments) if assessments else 0,
            total_threats=len(threats) if threats else 0,
            total_participants=len(participants) if participants else 0,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# Device Endpoints
# ========================

@app.post("/api/devices", response_model=DeviceResponse, status_code=201)
async def register_device(
    request: DeviceRegisterRequest,
    device_repo: DeviceRepository = Depends(get_device_repo),
):
    """Register a new device."""
    try:
        existing = device_repo.get_by_id(request.device_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Device {request.device_id} already exists"
            )
        
        device = device_repo.create(
            device_id=request.device_id,
            fingerprint_hash=request.fingerprint_hash,
            cpu=request.cpu,
            ram=request.ram,
            os=request.os,
            os_version=request.os_version,
            hostname=request.hostname,
        )
        
        logger.info(f"Device registered: {request.device_id}")
        return DeviceResponse.model_validate(device)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering device: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/devices/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str,
    device_repo: DeviceRepository = Depends(get_device_repo),
):
    """Get device information."""
    try:
        device = device_repo.get_by_id(device_id)
        if not device:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
        return DeviceResponse.model_validate(device)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/devices", response_model=DeviceListResponse)
async def list_devices(
    risk_level: str = None,
    device_repo: DeviceRepository = Depends(get_device_repo),
):
    """List devices."""
    try:
        if risk_level:
            devices = device_repo.get_by_risk_level(risk_level)
        else:
            devices = device_repo.get_all_active()
        
        return DeviceListResponse(
            total=len(devices),
            devices=[DeviceResponse.model_validate(d) for d in devices]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/devices/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: str,
    updates: dict,
    device_repo: DeviceRepository = Depends(get_device_repo),
):
    """Update device."""
    try:
        device = device_repo.get_by_id(device_id)
        if not device:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
        
        updated = device_repo.update(device_id, **updates)
        logger.info(f"Device updated: {device_id}")
        return DeviceResponse.model_validate(updated)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# Risk Assessment Endpoints
# ========================

@app.post("/api/assessments", response_model=RiskAssessmentResponse, status_code=201)
async def create_assessment(
    request: RiskAssessmentRequest,
    device_repo: DeviceRepository = Depends(get_device_repo),
    assessment_repo: RiskAssessmentRepository = Depends(get_assessment_repo),
):
    """Create risk assessment."""
    try:
        device = device_repo.get_by_id(request.device_id)
        if not device:
            raise HTTPException(status_code=404, detail=f"Device {request.device_id} not found")
        
        # Calculate overall risk score
        risk_score = (
            request.behavioral_risk * 0.3 +
            request.hardware_risk * 0.2 +
            request.network_risk * 0.25 +
            request.anomaly_risk * 0.25
        )
        
        risk_level = "low" if risk_score < 0.33 else "medium" if risk_score < 0.66 else "high"
        
        assessment = assessment_repo.create(
            device_id=request.device_id,
            risk_score=risk_score,
            risk_level=risk_level,
            behavioral_risk=request.behavioral_risk,
            hardware_risk=request.hardware_risk,
            network_risk=request.network_risk,
            anomaly_risk=request.anomaly_risk,
            confidence_score=request.confidence_score,
            assessment_reason=request.assessment_reason,
        )
        
        # Update device risk
        device_repo.update_risk_score(request.device_id, risk_score, risk_level)
        
        logger.info(f"Assessment created for {request.device_id}: {risk_score:.2f}")
        return RiskAssessmentResponse.model_validate(assessment)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating assessment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/assessments/{device_id}", response_model=RiskHistoryResponse)
async def get_assessments(
    device_id: str,
    limit: int = 30,
    device_repo: DeviceRepository = Depends(get_device_repo),
    assessment_repo: RiskAssessmentRepository = Depends(get_assessment_repo),
):
    """Get risk assessment history."""
    try:
        device = device_repo.get_by_id(device_id)
        if not device:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
        
        latest = assessment_repo.get_latest_for_device(device_id)
        history = assessment_repo.get_history(device_id, limit=limit)
        
        return RiskHistoryResponse(
            device_id=device_id,
            total_assessments=len(history),
            latest_risk_score=latest.risk_score if latest else 0.0,
            latest_risk_level=latest.risk_level if latest else "unknown",
            assessments=[RiskAssessmentResponse.model_validate(a) for a in history]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# Premium Endpoints
# ========================

@app.post("/api/premiums", response_model=PremiumResponse, status_code=201)
async def create_premium(
    request: PremiumQuoteRequest,
    device_repo: DeviceRepository = Depends(get_device_repo),
    assessment_repo: RiskAssessmentRepository = Depends(get_assessment_repo),
    premium_repo: PremiumRepository = Depends(get_premium_repo),
):
    """Create insurance premium."""
    try:
        device = device_repo.get_by_id(request.device_id)
        if not device:
            raise HTTPException(status_code=404, detail=f"Device {request.device_id} not found")
        
        # Calculate premium
        base = 120.0
        risk_multiplier = 0.5 + (request.risk_score * 3.0)
        final = base * risk_multiplier
        
        from datetime import timedelta
        now = datetime.utcnow()
        
        premium = premium_repo.create(
            device_id=request.device_id,
            base_premium=base,
            final_premium=final,
            coverage_tier=request.coverage_tier,
            annual_deductible=500.0,
            coverage_limit=50000.0,
            policy_start_date=now,
            policy_end_date=now + timedelta(days=365*request.years),
            policy_term_years=request.years,
        )
        
        logger.info(f"Premium created for {request.device_id}: ${final:.2f}")
        return PremiumResponse.model_validate(premium)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating premium: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/premiums/{device_id}", response_model=PremiumHistoryResponse)
async def get_premiums(
    device_id: str,
    device_repo: DeviceRepository = Depends(get_device_repo),
    premium_repo: PremiumRepository = Depends(get_premium_repo),
):
    """Get premium information."""
    try:
        device = device_repo.get_by_id(device_id)
        if not device:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
        
        active = premium_repo.get_active_for_device(device_id)
        history = premium_repo.get_history(device_id)
        
        return PremiumHistoryResponse(
            device_id=device_id,
            total_policies=len(history),
            active_premium=PremiumResponse.model_validate(active) if active else None,
            history=[PremiumResponse.model_validate(p) for p in history]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# Threat Intelligence Endpoints
# ========================

@app.post("/api/threats", response_model=ThreatReportResponse, status_code=201)
async def report_threat(
    request: ThreatReportRequest,
    threat_repo: ThreatReportRepository = Depends(get_threat_repo),
):
    """Report a threat."""
    try:
        threat = threat_repo.create(
            report_id=request.report_id,
            reporting_participant=request.reporting_participant,
            threat_type=request.threat_type,
            threat_level=request.threat_level,
            target_device_id=request.target_device_id,
            threat_description=request.threat_description,
            confidence_score=request.confidence_score,
        )
        
        logger.info(f"Threat reported: {request.report_id}")
        return ThreatReportResponse.model_validate(threat)
    except Exception as e:
        logger.error(f"Error reporting threat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/threats/device/{device_id}", response_model=ThreatListResponse)
async def get_device_threats(
    device_id: str,
    threat_repo: ThreatReportRepository = Depends(get_threat_repo),
):
    """Get threats for device."""
    try:
        threats = threat_repo.get_for_device(device_id)
        return ThreatListResponse(
            total=len(threats),
            threat_level=None,
            threats=[ThreatReportResponse.model_validate(t) for t in threats]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/threats", response_model=ThreatListResponse)
async def list_threats(
    threat_level: str = None,
    threat_repo: ThreatReportRepository = Depends(get_threat_repo),
):
    """List threats."""
    try:
        if threat_level:
            threats = threat_repo.get_by_threat_level(threat_level)
        else:
            threats = threat_repo.get_unverified()
        
        return ThreatListResponse(
            total=len(threats),
            threat_level=threat_level,
            threats=[ThreatReportResponse.model_validate(t) for t in threats]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# Network Participant Endpoints
# ========================

@app.post("/api/participants", response_model=ParticipantResponse, status_code=201)
async def register_participant(
    request: ParticipantRegisterRequest,
    participant_repo: NetworkParticipantRepository = Depends(get_participant_repo),
):
    """Register network participant."""
    try:
        participant = participant_repo.create(
            participant_id=request.participant_id,
            participant_name=request.participant_name,
            api_key=request.api_key,
        )
        
        logger.info(f"Participant registered: {request.participant_id}")
        return ParticipantResponse.model_validate(participant)
    except Exception as e:
        logger.error(f"Error registering participant: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/participants/{participant_id}", response_model=ParticipantResponse)
async def get_participant(
    participant_id: str,
    participant_repo: NetworkParticipantRepository = Depends(get_participant_repo),
):
    """Get participant information."""
    try:
        participant = participant_repo.get_by_id(participant_id)
        if not participant:
            raise HTTPException(status_code=404, detail=f"Participant {participant_id} not found")
        return ParticipantResponse.model_validate(participant)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/participants", response_model=ParticipantListResponse)
async def list_participants(
    participant_repo: NetworkParticipantRepository = Depends(get_participant_repo),
):
    """List network participants."""
    try:
        participants = participant_repo.get_all_active()
        return ParticipantListResponse(
            total=len(participants),
            participants=[ParticipantResponse.model_validate(p) for p in participants]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# Error Handlers
# ========================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    error_response = ErrorResponse(
        error=f"HTTP {exc.status_code}",
        detail=exc.detail,
        timestamp=datetime.utcnow(),
        request_id=None,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(error_response.model_dump())
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    error_response = ErrorResponse(
        error="Internal Server Error",
        detail="An unexpected error occurred",
        timestamp=datetime.utcnow(),
        request_id=None,
    )
    return JSONResponse(
        status_code=500,
        content=jsonable_encoder(error_response.model_dump())
    )
