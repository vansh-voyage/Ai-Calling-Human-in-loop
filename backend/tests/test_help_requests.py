import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.database import Base, get_session
from backend.main import create_app


@pytest_asyncio.fixture
async def client():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    app = create_app()

    async def override_session():
        async with factory() as s:
            yield s

    app.dependency_overrides[get_session] = override_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    await engine.dispose()


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_create_help_request(client: AsyncClient):
    resp = await client.post(
        "/api/v1/help-requests",
        json={"caller_id": "+15550100", "question": "Do you offer hot stone massage?"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "pending"
    assert data["caller_id"] == "+15550100"
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_resolve_request(client: AsyncClient):
    create_resp = await client.post(
        "/api/v1/help-requests",
        json={"caller_id": "+15550101", "question": "Do you do eyelash extensions?"},
    )
    request_id = create_resp.json()["id"]

    resolve_resp = await client.patch(
        f"/api/v1/help-requests/{request_id}/resolve",
        json={"answer": "Yes, lash extensions from $85.", "answered_by": "supervisor@luxe"},
    )
    assert resolve_resp.status_code == 200
    data = resolve_resp.json()
    assert data["status"] == "resolved"
    assert "85" in data["answer"]
    assert data["sms_sent"] is True


@pytest.mark.asyncio
async def test_resolve_saves_to_knowledge_base(client: AsyncClient):
    await client.post(
        "/api/v1/help-requests",
        json={"caller_id": "+15550102", "question": "Do you sell shampoo?"},
    )
    requests_resp = await client.get("/api/v1/help-requests?status=pending")
    request_id = requests_resp.json()["items"][0]["id"]

    await client.patch(
        f"/api/v1/help-requests/{request_id}/resolve",
        json={"answer": "Yes, we sell professional shampoos by Oribe and Kerastase."},
    )

    lookup_resp = await client.get("/api/v1/knowledge/lookup?q=do+you+sell+shampoo")
    assert lookup_resp.status_code == 200
    assert lookup_resp.json()["found"] is True


@pytest.mark.asyncio
async def test_resolve_already_resolved_returns_409(client: AsyncClient):
    create_resp = await client.post(
        "/api/v1/help-requests",
        json={"caller_id": "+15550103", "question": "Do you do manicures?"},
    )
    request_id = create_resp.json()["id"]

    await client.patch(
        f"/api/v1/help-requests/{request_id}/resolve",
        json={"answer": "Yes, manicures start at $35."},
    )
    second_resolve = await client.patch(
        f"/api/v1/help-requests/{request_id}/resolve",
        json={"answer": "Trying to resolve again."},
    )
    assert second_resolve.status_code == 409


@pytest.mark.asyncio
async def test_list_filter_by_status(client: AsyncClient):
    await client.post(
        "/api/v1/help-requests",
        json={"caller_id": "+15550104", "question": "Do you offer facials?"},
    )
    resp = await client.get("/api/v1/help-requests?status=pending")
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert all(i["status"] == "pending" for i in items)


@pytest.mark.asyncio
async def test_stats_endpoint(client: AsyncClient):
    resp = await client.get("/api/v1/help-requests/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "pending" in data
    assert "resolved" in data
    assert "unresolved" in data
